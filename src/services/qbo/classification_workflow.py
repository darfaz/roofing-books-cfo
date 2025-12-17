"""
Classification Workflow - Connects sync to classification
Automatically classifies transactions after they're synced
"""
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
from services.classification.agent import ClassificationAgent, TransactionClassification

load_dotenv()


class ClassificationWorkflow:
    """Workflow to classify unclassified transactions"""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.supabase = create_client(
            os.getenv("SUPABASE_URL", ""),
            os.getenv("SUPABASE_SERVICE_KEY", "")
        )
        self.classification_agent = ClassificationAgent()
    
    def classify_unclassified_transactions(
        self, 
        limit: int = 50,
        transaction_types: Optional[List[str]] = None
    ) -> Dict:
        """
        Find unclassified transactions and classify them
        
        Args:
            limit: Maximum number of transactions to classify in one run
            transaction_types: Filter by transaction types (default: all)
        
        Returns:
            Dict with classification results
        """
        # Build query for unclassified transactions
        query = self.supabase.table("transactions")\
            .select("id, transaction_date, transaction_type, total_amount, memo, reference_number, vendor_id, customer_id, vendors(name), customers(name)")\
            .eq("tenant_id", self.tenant_id)\
            .eq("classification_status", "unclassified")\
            .order("transaction_date", desc=True)\
            .limit(limit)
        
        if transaction_types:
            query = query.in_("transaction_type", transaction_types)
        
        result = query.execute()
        transactions = result.data
        
        if not transactions:
            return {
                "status": "success",
                "classified_count": 0,
                "message": "No unclassified transactions found"
            }
        
        classified_count = 0
        errors = []
        
        for txn in transactions:
            try:
                # Extract vendor/customer name
                vendor_name = txn.get("vendors", {}).get("name") if txn.get("vendors") else None
                customer_name = txn.get("customers", {}).get("name") if txn.get("customers") else None
                
                # Get vendor name from metadata if not in vendors table
                if not vendor_name:
                    metadata = txn.get("metadata", {})
                    if isinstance(metadata, dict):
                        vendor_name = metadata.get("vendor_name")
                
                if not vendor_name and not customer_name:
                    vendor_name = "Unknown"
                
                # Prepare transaction data for classification
                vendor = vendor_name or customer_name or "Unknown"
                amount = float(txn["total_amount"])
                date = txn["transaction_date"]
                memo = txn.get("memo") or txn.get("reference_number") or ""
                
                # Classify the transaction
                classification = self.classification_agent.classify(
                    tenant_id=self.tenant_id,
                    vendor=vendor,
                    amount=amount,
                    date=date,
                    memo=memo,
                    transaction_type=txn["transaction_type"]
                )
                
                # Find account_id from account_code
                account_id = self._get_account_id_by_code(classification.account_code)
                if not account_id:
                    errors.append(f"Account code {classification.account_code} not found for transaction {txn['id']}")
                    continue
                
                # Update transaction with classification
                update_data = {
                    "classification_status": "auto_classified",
                    "classification_confidence": classification.confidence,
                    "classified_by": "llm",
                    "classified_at": "now()",
                    "metadata": {
                        **(txn.get("metadata") or {}),
                        "classification_reasoning": classification.reasoning
                    }
                }
                
                self.supabase.table("transactions")\
                    .update(update_data)\
                    .eq("id", txn["id"])\
                    .execute()
                
                # Create transaction line (double-entry)
                self._create_transaction_line(
                    transaction_id=txn["id"],
                    account_id=account_id,
                    job_id=classification.job_id,
                    amount=amount,
                    transaction_type=txn["transaction_type"]
                )
                
                classified_count += 1
                
            except Exception as e:
                errors.append(f"Error classifying transaction {txn['id']}: {str(e)}")
                # Mark as review_needed on error
                self.supabase.table("transactions")\
                    .update({
                        "classification_status": "review_needed",
                        "metadata": {
                            **(txn.get("metadata") or {}),
                            "classification_error": str(e)
                        }
                    })\
                    .eq("id", txn["id"])\
                    .execute()
                continue
        
        return {
            "status": "success" if not errors else "partial",
            "classified_count": classified_count,
            "total_processed": len(transactions),
            "errors": errors
        }
    
    def _get_account_id_by_code(self, account_code: str) -> Optional[str]:
        """Find account_id by account code"""
        result = self.supabase.table("accounts")\
            .select("id")\
            .eq("tenant_id", self.tenant_id)\
            .eq("code", account_code)\
            .eq("is_active", True)\
            .limit(1)\
            .execute()
        
        if result.data:
            return result.data[0]["id"]
        return None
    
    def _create_transaction_line(
        self,
        transaction_id: str,
        account_id: str,
        job_id: Optional[str],
        amount: float,
        transaction_type: str
    ):
        """
        Create transaction line for double-entry accounting
        
        For expenses/bills: debit the expense account
        For invoices/deposits: credit revenue/asset accounts
        """
        # Determine debit/credit based on transaction type
        if transaction_type in ["bill", "expense"]:
            debit_amount = amount
            credit_amount = 0
        elif transaction_type in ["invoice", "deposit"]:
            debit_amount = 0
            credit_amount = amount
        else:
            # Default: debit
            debit_amount = amount
            credit_amount = 0
        
        # Create transaction line
        self.supabase.table("transaction_lines")\
            .insert({
                "transaction_id": transaction_id,
                "account_id": account_id,
                "job_id": job_id,
                "debit_amount": debit_amount,
                "credit_amount": credit_amount,
                "line_number": 1
            })\
            .execute()
        
        # TODO: Create offsetting entry (e.g., accounts payable for bills, accounts receivable for invoices)
        # For now, just creating the main line
    
    def classify_transaction_by_id(self, transaction_id: str) -> Dict:
        """Classify a specific transaction by ID"""
        result = self.supabase.table("transactions")\
            .select("*")\
            .eq("id", transaction_id)\
            .eq("tenant_id", self.tenant_id)\
            .limit(1)\
            .execute()
        
        if not result.data:
            return {"status": "error", "message": "Transaction not found"}
        
        txn = result.data[0]
        
        # Use the same logic as batch classification
        workflow_result = self.classify_unclassified_transactions(limit=1)
        
        return {
            "status": "success",
            "transaction_id": transaction_id,
            "classification": workflow_result
        }





