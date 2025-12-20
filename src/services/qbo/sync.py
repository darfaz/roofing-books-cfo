"""
QBO Transaction Sync Service
Pulls transactions from QuickBooks and stores in Supabase
"""
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from supabase import create_client, Client
from .client import QBOClient

load_dotenv()


class QBOSyncService:
    """Syncs transactions from QBO to Supabase"""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.qbo_client = QBOClient(tenant_id)
        self.supabase = create_client(
            os.getenv("SUPABASE_URL", ""),
            os.getenv("SUPABASE_SERVICE_KEY", "")
        )
    
    def sync_transactions(
        self, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sync all transaction types from QBO to Supabase
        
        Args:
            start_date: Start date in YYYY-MM-DD format (defaults to 30 days ago)
            end_date: End date in YYYY-MM-DD format (defaults to today)
        
        Returns:
            Dict with sync results: count, transactions, errors
        """
        today = datetime.now().date()
        if not start_date:
            start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = today.strftime("%Y-%m-%d")
        
        all_transactions = []
        errors = []
        
        # Sync different transaction types
        try:
            purchases = self.sync_purchases(start_date, end_date)
            all_transactions.extend(purchases)
        except Exception as e:
            errors.append(f"Error syncing purchases: {str(e)}")
        
        try:
            invoices = self.sync_invoices(start_date, end_date)
            all_transactions.extend(invoices)
        except Exception as e:
            errors.append(f"Error syncing invoices: {str(e)}")
        
        try:
            deposits = self.sync_deposits(start_date, end_date)
            all_transactions.extend(deposits)
        except Exception as e:
            errors.append(f"Error syncing deposits: {str(e)}")
        
        # Store transactions in Supabase
        stored_count = 0
        if all_transactions:
            try:
                stored_count = self.store_transactions(all_transactions)
            except Exception as e:
                errors.append(f"Error storing transactions: {str(e)}")
        
        return {
            "status": "success" if not errors else "partial",
            "synced_count": stored_count,
            "total_fetched": len(all_transactions),
            "errors": errors,
            "start_date": start_date,
            "end_date": end_date
        }
    
    def sync_purchases(self, start_date: str, end_date: str) -> List[Dict]:
        """Fetch purchases (bills, expenses) from QBO and normalize"""
        query_str = (
            f"SELECT * FROM Purchase "
            f"WHERE TxnDate >= '{start_date}' AND TxnDate <= '{end_date}'"
        )
        purchases = self.qbo_client.query(query_str)
        
        transactions = []
        for purchase in purchases:
            txn_date = purchase.get("TxnDate")
            total_amt_obj = purchase.get("TotalAmt", {})
            total_amt = float(total_amt_obj.get("value", 0)) if isinstance(total_amt_obj, dict) else float(total_amt_obj or 0)
            
            vendor_ref = purchase.get("EntityRef", {})
            vendor_name = vendor_ref.get("name") if isinstance(vendor_ref, dict) else None
            
            # Get memo/description from first line item or PrivateNote
            memo = purchase.get("PrivateNote", "")
            if not memo and purchase.get("Line"):
                first_line = purchase["Line"][0] if isinstance(purchase["Line"], list) else purchase["Line"]
                memo = first_line.get("Description", "") if isinstance(first_line, dict) else ""
            
            # Determine transaction type based on PaymentType
            payment_type = purchase.get("PaymentType", "")
            if payment_type == "CreditCard":
                txn_type = "expense"
            else:
                txn_type = "bill"
            
            transactions.append({
                "qbo_id": purchase.get("Id"),
                "qbo_type": "Purchase",
                "transaction_date": txn_date,
                "transaction_type": txn_type,
                "total_amount": total_amt,
                "memo": memo,
                "vendor_name": vendor_name,
                "reference_number": purchase.get("DocNumber"),
                "status": "pending",
                "classification_status": "unclassified",
                "qbo_synced_at": datetime.utcnow().isoformat(),
                "metadata": {
                    "payment_type": payment_type,
                    "sync_token": purchase.get("SyncToken"),
                    "raw_data": purchase
                }
            })
        
        return transactions
    
    def sync_invoices(self, start_date: str, end_date: str) -> List[Dict]:
        """Fetch invoices from QBO and normalize"""
        query_str = (
            f"SELECT * FROM Invoice "
            f"WHERE TxnDate >= '{start_date}' AND TxnDate <= '{end_date}'"
        )
        invoices = self.qbo_client.query(query_str)
        
        transactions = []
        for invoice in invoices:
            txn_date = invoice.get("TxnDate")
            total_amt_obj = invoice.get("TotalAmt", {})
            total_amt = float(total_amt_obj.get("value", 0)) if isinstance(total_amt_obj, dict) else float(total_amt_obj or 0)
            
            customer_ref = invoice.get("CustomerRef", {})
            customer_name = customer_ref.get("name") if isinstance(customer_ref, dict) else None
            
            # Get memo/description
            memo = invoice.get("PrivateNote", "")
            if not memo and invoice.get("Line"):
                first_line = invoice["Line"][0] if isinstance(invoice["Line"], list) else invoice["Line"]
                memo = first_line.get("Description", "") if isinstance(first_line, dict) else ""
            
            balance_obj = invoice.get("Balance", {})
            balance = float(balance_obj.get("value", 0)) if isinstance(balance_obj, dict) else float(balance_obj or 0)
            
            # Status based on balance
            status = "posted" if balance <= 0 else "pending"
            
            transactions.append({
                "qbo_id": invoice.get("Id"),
                "qbo_type": "Invoice",
                "transaction_date": txn_date,
                "transaction_type": "invoice",
                "total_amount": total_amt,
                "memo": memo,
                "customer_name": customer_name,
                "reference_number": invoice.get("DocNumber"),
                "status": status,
                "classification_status": "unclassified",
                "qbo_synced_at": datetime.utcnow().isoformat(),
                "metadata": {
                    "balance": balance,
                    "due_date": invoice.get("DueDate"),
                    "sync_token": invoice.get("SyncToken"),
                    "raw_data": invoice
                }
            })
        
        return transactions
    
    def sync_deposits(self, start_date: str, end_date: str) -> List[Dict]:
        """Fetch deposits (payments received) from QBO and normalize"""
        query_str = (
            f"SELECT * FROM Deposit "
            f"WHERE TxnDate >= '{start_date}' AND TxnDate <= '{end_date}'"
        )
        deposits = self.qbo_client.query(query_str)
        
        transactions = []
        for deposit in deposits:
            txn_date = deposit.get("TxnDate")
            total_amt_obj = deposit.get("TotalAmt", {})
            total_amt = float(total_amt_obj.get("value", 0)) if isinstance(total_amt_obj, dict) else float(total_amt_obj or 0)
            
            # Try to extract customer from linked transactions
            customer_name = None
            if deposit.get("Line"):
                lines = deposit["Line"] if isinstance(deposit["Line"], list) else [deposit["Line"]]
                for line in lines:
                    if isinstance(line, dict) and line.get("LinkedTxn"):
                        linked_txns = line["LinkedTxn"] if isinstance(line["LinkedTxn"], list) else [line["LinkedTxn"]]
                        for linked in linked_txns:
                            if isinstance(linked, dict) and linked.get("TxnType") == "Invoice":
                                customer_ref = linked.get("CustomerRef", {})
                                customer_name = customer_ref.get("name") if isinstance(customer_ref, dict) else None
                                break
            
            memo = deposit.get("PrivateNote", "")
            
            transactions.append({
                "qbo_id": deposit.get("Id"),
                "qbo_type": "Deposit",
                "transaction_date": txn_date,
                "transaction_type": "deposit",
                "total_amount": total_amt,
                "memo": memo,
                "customer_name": customer_name,
                "reference_number": deposit.get("DocNumber"),
                "status": "posted",
                "classification_status": "unclassified",
                "qbo_synced_at": datetime.utcnow().isoformat(),
                "metadata": {
                    "sync_token": deposit.get("SyncToken"),
                    "raw_data": deposit
                }
            })
        
        return transactions
    
    def store_transactions(self, transactions: List[Dict]) -> int:
        """
        Store transactions in Supabase with deduplication
        
        Uses qbo_id to prevent duplicates. Updates existing records if they exist.
        """
        stored_count = 0
        
        for txn in transactions:
            try:
                # Prepare transaction data for Supabase
                transaction_data = {
                    "tenant_id": self.tenant_id,
                    "transaction_date": txn["transaction_date"],
                    "transaction_type": txn["transaction_type"],
                    "total_amount": txn["total_amount"],
                    "memo": txn.get("memo"),
                    "reference_number": txn.get("reference_number"),
                    "status": txn.get("status", "pending"),
                    "classification_status": txn.get("classification_status", "unclassified"),
                    "qbo_id": txn["qbo_id"],
                    "qbo_type": txn.get("qbo_type"),
                    "qbo_synced_at": txn.get("qbo_synced_at"),
                    "metadata": txn.get("metadata", {})
                }
                
                # Try to resolve vendor_id or customer_id from names
                # First, try to find existing vendor/customer by name
                if txn.get("vendor_name"):
                    vendor_result = self.supabase.table("vendors")\
                        .select("id")\
                        .eq("tenant_id", self.tenant_id)\
                        .eq("name", txn["vendor_name"])\
                        .limit(1)\
                        .execute()
                    if vendor_result.data:
                        transaction_data["vendor_id"] = vendor_result.data[0]["id"]
                
                if txn.get("customer_name"):
                    customer_result = self.supabase.table("customers")\
                        .select("id")\
                        .eq("tenant_id", self.tenant_id)\
                        .eq("name", txn["customer_name"])\
                        .limit(1)\
                        .execute()
                    if customer_result.data:
                        transaction_data["customer_id"] = customer_result.data[0]["id"]
                
                # Check if transaction already exists by qbo_id
                existing = self.supabase.table("transactions")\
                    .select("id")\
                    .eq("tenant_id", self.tenant_id)\
                    .eq("qbo_id", txn["qbo_id"])\
                    .limit(1)\
                    .execute()
                
                if existing.data:
                    # Update existing transaction
                    self.supabase.table("transactions")\
                        .update(transaction_data)\
                        .eq("id", existing.data[0]["id"])\
                        .execute()
                else:
                    # Insert new transaction
                    self.supabase.table("transactions")\
                        .insert(transaction_data)\
                        .execute()
                
                stored_count += 1
                
            except Exception as e:
                # Log error but continue with other transactions
                print(f"Error storing transaction {txn.get('qbo_id')}: {str(e)}")
                continue
        
        return stored_count
    
    def get_last_sync_date(self) -> Optional[str]:
        """Get the date of the last successful sync for this tenant"""
        result = self.supabase.table("transactions")\
            .select("qbo_synced_at")\
            .eq("tenant_id", self.tenant_id)\
            .not_.is_("qbo_synced_at", "null")\
            .order("qbo_synced_at", desc=True)\
            .limit(1)\
            .execute()
        
        if result.data and result.data[0].get("qbo_synced_at"):
            # Return the date (not timestamp) for incremental sync
            sync_time = result.data[0]["qbo_synced_at"]
            if isinstance(sync_time, str):
                return sync_time.split("T")[0]  # Extract date part
            return sync_time.strftime("%Y-%m-%d") if hasattr(sync_time, "strftime") else None
        
        return None
    
    def sync_incremental(self) -> Dict[str, Any]:
        """
        Sync only new transactions since last sync
        Useful for scheduled/automated syncs
        """
        last_sync = self.get_last_sync_date()
        if last_sync:
            # Sync from last sync date (might miss same-day updates, but good enough for incremental)
            start_date = last_sync
        else:
            # First sync - go back 30 days
            start_date = (datetime.now().date() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        return self.sync_transactions(start_date=start_date)






