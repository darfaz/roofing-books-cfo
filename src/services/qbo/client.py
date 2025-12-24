"""
QuickBooks Online API Client
Fetches data from QBO using OAuth2 REST API
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import httpx
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# QBO API endpoints
QBO_SANDBOX_URL = "https://sandbox-quickbooks.api.intuit.com"  # For sandbox
QBO_PROD_URL = "https://quickbooks.api.intuit.com"  # For production


class QBOClient:
    """QuickBooks Online API client using OAuth2"""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.base_url = QBO_PROD_URL if os.getenv("QBO_ENVIRONMENT") != "sandbox" else QBO_SANDBOX_URL
        self.supabase = create_client(
            os.getenv("SUPABASE_URL", ""),
            os.getenv("SUPABASE_SERVICE_KEY", "")
        )
        self._access_token = None
        self._realm_id = None
        
    def _get_credentials(self) -> tuple[str, str]:
        """Get access token and realm_id from Supabase, refreshing if expired"""
        # Always fetch from database to check expiration (don't rely on cached token)
        result = self.supabase.table("tenant_integrations")\
            .select("access_token, realm_id, token_expires_at, refresh_token, metadata")\
            .eq("tenant_id", self.tenant_id)\
            .eq("provider", "quickbooks")\
            .eq("is_active", True)\
            .execute()
        
        if not result.data:
            raise ValueError(f"No active QBO integration found for tenant {self.tenant_id}")
        
        integration = result.data[0]
        self._realm_id = integration["realm_id"]
        token_expires_at = integration.get("token_expires_at")
        
        # Check if token is expired or will expire in the next 5 minutes
        if token_expires_at:
            try:
                if isinstance(token_expires_at, str):
                    # Handle ISO format strings
                    if token_expires_at.endswith('Z'):
                        expires_at = datetime.fromisoformat(token_expires_at.replace('Z', '+00:00'))
                    else:
                        expires_at = datetime.fromisoformat(token_expires_at)
                else:
                    expires_at = token_expires_at
                
                # Convert to UTC naive datetime for comparison
                if expires_at.tzinfo:
                    expires_at_naive = expires_at.replace(tzinfo=None) - expires_at.utcoffset()
                else:
                    expires_at_naive = expires_at
                
                now_naive = datetime.utcnow()
                
                # Refresh if expired or expiring within 5 minutes
                if expires_at_naive <= now_naive + timedelta(minutes=5):
                    self._refresh_token(integration.get("refresh_token"))
                    # Re-fetch after refresh
                    result = self.supabase.table("tenant_integrations")\
                        .select("access_token, realm_id")\
                        .eq("tenant_id", self.tenant_id)\
                        .eq("provider", "quickbooks")\
                        .eq("is_active", True)\
                        .execute()
                    integration = result.data[0]
            except (ValueError, AttributeError) as e:
                # If date parsing fails, try refresh anyway
                print(f"Warning: Could not parse token expiration: {e}")
                if integration.get("refresh_token"):
                    try:
                        self._refresh_token(integration.get("refresh_token"))
                        result = self.supabase.table("tenant_integrations")\
                            .select("access_token, realm_id")\
                            .eq("tenant_id", self.tenant_id)\
                            .eq("provider", "quickbooks")\
                            .eq("is_active", True)\
                            .execute()
                        integration = result.data[0]
                    except Exception as refresh_err:
                        # Don't silently ignore - re-raise so user knows to reconnect
                        raise refresh_err
        
        self._access_token = integration["access_token"]
        
        return self._access_token, self._realm_id
    
    def _refresh_token(self, refresh_token: str):
        """Refresh the access token using refresh token"""
        if not refresh_token:
            raise ValueError("No refresh token available")
        
        client_id = os.getenv("QBO_CLIENT_ID")
        client_secret = os.getenv("QBO_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            raise ValueError("QBO credentials not configured")
        
        # QBO token refresh endpoint
        token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
        
        with httpx.Client() as client:
            response = client.post(
                token_url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token
                },
                auth=(client_id, client_secret),
                headers={"Accept": "application/json"}
            )
        
        if response.status_code != 200:
            error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            error_type = error_data.get("error", "unknown")

            # If refresh token is invalid, mark integration as inactive so UI shows "Connect" button
            if error_type == "invalid_grant":
                print(f"QBO refresh token invalid for tenant {self.tenant_id}, marking integration as inactive")
                self.supabase.table("tenant_integrations")\
                    .update({"is_active": False})\
                    .eq("tenant_id", self.tenant_id)\
                    .eq("provider", "quickbooks")\
                    .execute()
                raise ValueError("QBO connection expired. Please reconnect QuickBooks.")

            raise ValueError(f"Token refresh failed: {response.text}")
        
        tokens = response.json()
        
        # Calculate new expiration
        expires_in = tokens.get("expires_in", 3600)
        token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Update tokens in Supabase
        self.supabase.table("tenant_integrations")\
            .update({
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token", refresh_token),  # Keep old if not provided
                "token_expires_at": token_expires_at.isoformat(),
                "metadata": {
                    "token_type": tokens.get("token_type"),
                    "expires_in": expires_in,
                    "last_refreshed_at": datetime.utcnow().isoformat()
                }
            })\
            .eq("tenant_id", self.tenant_id)\
            .eq("provider", "quickbooks")\
            .execute()
        
        # Update cached token
        self._access_token = tokens.get("access_token")
    
    def _make_request(self, endpoint: str, method: str = "GET", params: Optional[Dict] = None) -> Dict:
        """Make authenticated request to QBO API"""
        access_token, realm_id = self._get_credentials()
        
        url = f"{self.base_url}/v3/company/{realm_id}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        with httpx.Client() as client:
            if method == "GET":
                response = client.get(url, headers=headers, params=params, timeout=30.0)
            elif method == "POST":
                response = client.post(url, headers=headers, json=params, timeout=30.0)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == 401:
                raise ValueError("QBO token expired or invalid. Please reconnect.")
            response.raise_for_status()
            return response.json()
    
    def query(self, query_string: str) -> List[Dict]:
        """Execute QBO query string"""
        # QBO query endpoint expects 'query' as a URL parameter, not in body
        response = self._make_request("query", params={"query": query_string})
        query_response = response.get("QueryResponse", {})
        # Check for errors
        if "Fault" in query_response:
            error = query_response["Fault"]
            raise ValueError(f"QBO Query Error: {error}")

        # QBO returns data keyed by entity type name (e.g., "Purchase", "Invoice", "Account")
        # Extract the entity type from the query string to find the right key
        # Query format: "SELECT * FROM EntityName WHERE..."
        entity_type = None
        query_upper = query_string.upper()
        if " FROM " in query_upper:
            # Extract entity name after FROM
            from_idx = query_upper.index(" FROM ") + 6
            rest = query_string[from_idx:].strip()
            # Entity name ends at space or end of string
            entity_type = rest.split()[0] if rest else None

        # Try to get data using the entity type key
        if entity_type and entity_type in query_response:
            return query_response[entity_type]

        # Fallback: try common entity names or return first list found
        for key in ["Purchase", "Invoice", "Deposit", "Bill", "Account", "CompanyInfo", "Vendor", "Customer"]:
            if key in query_response:
                result = query_response[key]
                return result if isinstance(result, list) else [result]

        # Last resort: find any list in the response
        for key, value in query_response.items():
            if isinstance(value, list):
                return value

        return []
    
    def get_accounts(self) -> List[Dict]:
        """Get chart of accounts"""
        query_str = "SELECT * FROM Account WHERE Active = true"
        accounts = self.query(query_str)
        
        result = []
        for acc in accounts:
            result.append({
                "id": acc.get("Id"),
                "name": acc.get("Name"),
                "account_type": acc.get("AccountType"),
                "account_sub_type": acc.get("AccountSubType"),
                "code": acc.get("AcctNum", ""),
                "balance": float(acc.get("CurrentBalance", {}).get("value", 0)) if acc.get("CurrentBalance") else 0,
                "active": acc.get("Active", True)
            })
        return result
    
    def get_company_info(self) -> Dict:
        """Get company information"""
        # Use query endpoint instead of companyinfo endpoint
        query_str = "SELECT * FROM CompanyInfo"
        result = self.query(query_str)
        
        if not result:
            return {}
        
        company = result[0]
        return {
            "company_name": company.get("CompanyName"),
            "legal_name": company.get("LegalName"),
            "company_addr": company.get("CompanyAddr", {}),
            "fiscal_year_start_month": company.get("FiscalYearStartMonth"),
            "email": company.get("Email", {}).get("Address") if company.get("Email") else None
        }
    
    def get_invoices(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Get invoices (for AR)"""
        today = datetime.now().date()
        if not start_date:
            # Go back 1 year from today
            start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = today.strftime("%Y-%m-%d")
        
        # QBO query syntax - get all invoices
        # Note: QBO dates must be in YYYY-MM-DD format
        query_str = (
            f"SELECT * FROM Invoice "
            f"WHERE TxnDate >= '{start_date}' AND TxnDate <= '{end_date}'"
        )
        invoices = self.query(query_str)
        
        result = []
        for inv in invoices:
            balance_obj = inv.get("Balance")
            total_obj = inv.get("TotalAmt")
            
            # Handle QBO amount objects
            balance = float(balance_obj.get("value", 0)) if isinstance(balance_obj, dict) else float(balance_obj or 0)
            total = float(total_obj.get("value", 0)) if isinstance(total_obj, dict) else float(total_obj or 0)
            
            txn_date = inv.get("TxnDate")
            due_date = inv.get("DueDate")
            
            customer_ref = inv.get("CustomerRef", {})
            customer_id = customer_ref.get("value") if isinstance(customer_ref, dict) else None
            customer_name = customer_ref.get("name") if isinstance(customer_ref, dict) else None
            
            result.append({
                "id": inv.get("Id"),
                "doc_number": inv.get("DocNumber"),
                "txn_date": txn_date,
                "due_date": due_date,
                "customer_ref": customer_id,
                "customer_name": customer_name,
                "total_amt": total,
                "balance": balance,
                "status": inv.get("EmailStatus")
            })
        return result
    
    def get_bills(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Get bills (for AP)"""
        today = datetime.now().date()
        if not start_date:
            start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = today.strftime("%Y-%m-%d")
        
        # Note: QBO doesn't support filtering on Balance in query, so we get all bills and filter in code
        query_str = (
            f"SELECT * FROM Bill "
            f"WHERE TxnDate >= '{start_date}' AND TxnDate <= '{end_date}'"
        )
        bills = self.query(query_str)
        
        result = []
        for bill in bills:
            balance_obj = bill.get("Balance")
            total_obj = bill.get("TotalAmt")
            
            # Handle QBO amount objects
            balance = float(balance_obj.get("value", 0)) if isinstance(balance_obj, dict) else float(balance_obj or 0)
            total = float(total_obj.get("value", 0)) if isinstance(total_obj, dict) else float(total_obj or 0)
            
            vendor_ref = bill.get("VendorRef", {})
            vendor_id = vendor_ref.get("value") if isinstance(vendor_ref, dict) else None
            vendor_name = vendor_ref.get("name") if isinstance(vendor_ref, dict) else None
            
            result.append({
                "id": bill.get("Id"),
                "doc_number": bill.get("DocNumber"),
                "txn_date": bill.get("TxnDate"),
                "due_date": bill.get("DueDate"),
                "vendor_ref": vendor_id,
                "vendor_name": vendor_name,
                "total_amt": total,
                "balance": balance
            })
        # Filter to only bills with outstanding balance (optional - remove if you want all bills)
        # return [b for b in result if b["balance"] > 0]
        return result
    
    def get_account_balance(self, account_name: str = "Checking") -> float:
        """Get balance for a specific account (e.g., checking account)"""
        query_str = f"SELECT * FROM Account WHERE Name = '{account_name}' AND Active = true"
        accounts = self.query(query_str)
        
        if not accounts:
            # Try to find any bank account
            query_str = "SELECT * FROM Account WHERE AccountType = 'Bank' AND Active = true"
            accounts = self.query(query_str)
        
        if accounts:
            balance = accounts[0].get("CurrentBalance")
            if balance:
                return float(balance.get("value", 0))
        
        return 0.0
    
    def get_cash_accounts_balance(self) -> float:
        """Get total balance across all cash/bank accounts"""
        query_str = "SELECT * FROM Account WHERE AccountType = 'Bank' AND Active = true"
        accounts = self.query(query_str)
        
        total = 0.0
        for acc in accounts:
            balance = acc.get("CurrentBalance")
            if balance:
                total += float(balance.get("value", 0))
        
        return total
    
    def get_revenue_mtd(self, start_date: Optional[str] = None) -> Dict:
        """Get month-to-date revenue from invoices"""
        today = datetime.now()
        if not start_date:
            start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

        # Get all invoices for current month (including paid ones)
        # Query for invoices with TxnDate in the month
        query_str = (
            f"SELECT * FROM Invoice "
            f"WHERE TxnDate >= '{start_date}' AND TxnDate <= '{end_date}'"
        )
        invoices = self.query(query_str)

        # Calculate total revenue (use TotalAmt for invoices)
        total = 0.0
        for inv in invoices:
            total_amt = float(inv.get("TotalAmt", {}).get("value", 0)) if inv.get("TotalAmt") else 0
            total += total_amt

        return {
            "mtd": total,
            "target": 100000,  # Default target, should come from settings
            "invoice_count": len(invoices)
        }

    # ============================================================
    # EXPENSE CLASSIFICATION FOR ROOFING CONTRACTORS
    # ============================================================

    # QBO AccountSubTypes that are typically OVERHEAD (fixed costs)
    OVERHEAD_SUBTYPES = {
        # Administrative & Office
        "OfficeGeneralAdministrativeExpenses",
        "LegalProfessionalFees",
        "AdvertisingPromotional",
        "DuesSubscriptions",
        "BankCharges",
        "Insurance",
        "TaxesPaid",
        # Facilities
        "RentOrLeaseOfBuildings",
        "Utilities",
        "RepairMaintenance",  # Building/office repairs
        # Travel & Entertainment (admin)
        "EntertainmentMeals",
        "Travel",
        "TravelMeals",
        # Other overhead
        "Depreciation",
        "Amortization",
        "OtherMiscellaneousExpense",
        "PenaltiesSettlements",
        # Payroll (admin staff)
        "PayrollExpenses",
        "PayrollTaxExpenses",
    }

    # QBO AccountSubTypes that are typically JOB COSTS (variable/direct)
    JOB_COST_SUBTYPES = {
        # Materials
        "SuppliesMaterials",
        "SuppliesMaterialsCogs",
        "CostOfLaborCos",
        # Equipment for jobs
        "EquipmentRental",
        # Other job-related
        "OtherMiscellaneousServiceCost",  # Often job expenses
    }

    # Keywords in account NAMES that indicate OVERHEAD
    OVERHEAD_KEYWORDS = [
        "office", "admin", "accounting", "bookkeep", "lawyer", "legal",
        "professional fee", "advertising", "marketing", "promotion",
        "dues", "subscription", "membership", "license fee",
        "bank charge", "bank fee", "merchant fee", "processing fee",
        "rent", "lease", "mortgage",
        "utility", "utilities", "electric", "gas", "water", "internet", "phone", "telephone",
        "insurance", "liability", "general insurance",
        "depreciation", "amortization",
        "meal", "entertainment", "travel",
        "office supplies", "stationery", "printing",
        "computer", "software", "it support",
        "salary", "salaries",  # Usually admin/office
        "training", "education", "conference",
        "miscellaneous", "other expense",
    ]

    # Keywords in account NAMES that indicate JOB COSTS
    JOB_COST_KEYWORDS = [
        "material", "supplies", "inventory",
        "job", "project", "contract",
        "labor", "wages", "crew", "field",
        "subcontract", "sub ", "subs ",
        "equipment rental", "tool rental",
        "disposal", "dump", "haul",
        "permit", "inspection",
        "roofing", "shingle", "flashing", "underlayment", "decking",
        "gutter", "siding", "fascia", "soffit",
        "lumber", "plywood", "osb",
        "nail", "fastener", "adhesive", "sealant", "caulk",
        "safety", "harness", "scaffold",
        "installation", "repair", "replace",
        "cogs", "cost of goods", "cost of sales",
        "direct cost", "variable cost",
    ]

    # Keywords that indicate WORKERS COMP (job cost - scales with labor)
    WORKERS_COMP_KEYWORDS = ["workers comp", "workman", "work comp", "wc insurance"]

    def _classify_expense_account(self, account: Dict) -> Dict:
        """
        Classify an expense account as overhead, job_cost, or mixed.

        Returns classification with confidence and reasoning.
        """
        account_type = account.get("AccountType", "")
        account_subtype = account.get("AccountSubType", "")
        name = account.get("Name", "").lower()

        classification = "unknown"
        category = "other"
        confidence = 0.5
        reason = ""

        # COGS is always job cost
        if account_type == "Cost of Goods Sold":
            return {
                "classification": "job_cost",
                "category": "materials",
                "confidence": 1.0,
                "reason": "Cost of Goods Sold account type"
            }

        # Check for workers comp (job cost - scales with field labor)
        for kw in self.WORKERS_COMP_KEYWORDS:
            if kw in name:
                return {
                    "classification": "job_cost",
                    "category": "workers_comp",
                    "confidence": 0.95,
                    "reason": f"Workers comp scales with job labor"
                }

        # Check subtype first (most reliable)
        if account_subtype in self.OVERHEAD_SUBTYPES:
            classification = "overhead"
            confidence = 0.85
            reason = f"AccountSubType {account_subtype} is typically overhead"

            # Determine category
            if account_subtype in ["LegalProfessionalFees"]:
                category = "professional_fees"
            elif account_subtype in ["AdvertisingPromotional"]:
                category = "marketing"
            elif account_subtype in ["RentOrLeaseOfBuildings"]:
                category = "rent"
            elif account_subtype in ["Utilities"]:
                category = "utilities"
            elif account_subtype in ["Insurance"]:
                category = "insurance"
            elif account_subtype in ["PayrollExpenses", "PayrollTaxExpenses"]:
                category = "admin_payroll"
            elif account_subtype in ["OfficeGeneralAdministrativeExpenses"]:
                category = "office"
            elif account_subtype in ["Depreciation", "Amortization"]:
                category = "depreciation"
            else:
                category = "other_overhead"

        elif account_subtype in self.JOB_COST_SUBTYPES:
            classification = "job_cost"
            confidence = 0.75  # Lower because some could be overhead supplies
            reason = f"AccountSubType {account_subtype} is typically job-related"

            if account_subtype in ["SuppliesMaterials", "SuppliesMaterialsCogs"]:
                category = "materials"
            elif account_subtype == "EquipmentRental":
                category = "equipment"
            elif account_subtype == "CostOfLaborCos":
                category = "direct_labor"
            else:
                category = "other_job_cost"

        # Refine with name keywords (can override subtype)
        for kw in self.OVERHEAD_KEYWORDS:
            if kw in name:
                if classification != "overhead":
                    classification = "overhead"
                    confidence = 0.8
                    reason = f"Name contains overhead keyword: '{kw}'"
                else:
                    confidence = min(0.95, confidence + 0.1)
                break

        for kw in self.JOB_COST_KEYWORDS:
            if kw in name:
                if classification != "job_cost":
                    classification = "job_cost"
                    confidence = 0.8
                    reason = f"Name contains job cost keyword: '{kw}'"
                else:
                    confidence = min(0.95, confidence + 0.1)

                # Refine category based on name
                if any(m in name for m in ["material", "supplies", "inventory", "shingle", "lumber"]):
                    category = "materials"
                elif any(m in name for m in ["labor", "wages", "crew"]):
                    category = "direct_labor"
                elif any(m in name for m in ["subcontract", "sub "]):
                    category = "subcontractors"
                elif any(m in name for m in ["equipment", "tool", "rental"]):
                    category = "equipment"
                elif any(m in name for m in ["disposal", "dump", "haul"]):
                    category = "disposal"
                elif any(m in name for m in ["permit", "inspection"]):
                    category = "permits"
                break

        # Handle ambiguous cases
        if classification == "unknown":
            # Default Other Expense to overhead
            if account_type == "Other Expense":
                classification = "overhead"
                category = "other_overhead"
                confidence = 0.6
                reason = "Other Expense type defaults to overhead"
            else:
                classification = "mixed"
                category = "needs_review"
                confidence = 0.5
                reason = "Could not determine - needs manual review"

        return {
            "classification": classification,
            "category": category,
            "confidence": round(confidence, 2),
            "reason": reason
        }

    def get_expense_accounts_classified(self) -> List[Dict]:
        """
        Get all expense accounts with overhead/job cost classification.

        Returns accounts classified as:
        - overhead: Fixed costs (rent, utilities, admin salaries, etc.)
        - job_cost: Variable costs that scale with jobs (materials, labor, subs)
        - mixed: Needs manual review or context-dependent
        """
        query_str = "SELECT * FROM Account WHERE Active = true"
        accounts = self.query(query_str)

        expense_types = ["Expense", "Cost of Goods Sold", "Other Expense"]
        expense_accounts = [a for a in accounts if a.get("AccountType") in expense_types]

        classified = []
        for acc in expense_accounts:
            classification = self._classify_expense_account(acc)
            classified.append({
                "id": acc.get("Id"),
                "name": acc.get("Name"),
                "account_type": acc.get("AccountType"),
                "account_sub_type": acc.get("AccountSubType", ""),
                "balance": float(acc.get("CurrentBalance", 0) or 0),
                **classification
            })

        return classified

    def get_expense_transactions_by_classification(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Get all expense transactions grouped by overhead vs job cost.
        """
        today = datetime.now().date()
        if not start_date:
            start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = (today + timedelta(days=365)).strftime("%Y-%m-%d")

        # Get classified accounts
        accounts = self.get_expense_accounts_classified()
        account_map = {acc["id"]: acc for acc in accounts}

        # Query purchases
        purchase_query = (
            f"SELECT * FROM Purchase "
            f"WHERE TxnDate >= '{start_date}' AND TxnDate <= '{end_date}'"
        )
        purchases = self.query(purchase_query)

        overhead_txns = []
        job_cost_txns = []
        mixed_txns = []

        for purchase in purchases:
            lines = purchase.get("Line", [])
            if not isinstance(lines, list):
                lines = [lines]

            for line in lines:
                if not isinstance(line, dict):
                    continue

                detail = line.get("AccountBasedExpenseLineDetail", {})
                account_ref = detail.get("AccountRef", {})
                account_id = account_ref.get("value") if isinstance(account_ref, dict) else None

                if not account_id or account_id not in account_map:
                    continue

                acc_info = account_map[account_id]
                amount = float(line.get("Amount", 0) or 0)

                txn_data = {
                    "source_id": purchase.get("Id"),
                    "txn_date": purchase.get("TxnDate"),
                    "account_id": account_id,
                    "account_name": acc_info["name"],
                    "category": acc_info["category"],
                    "amount": amount,
                    "description": line.get("Description", ""),
                    "vendor": purchase.get("EntityRef", {}).get("name") if purchase.get("EntityRef") else None,
                    "confidence": acc_info["confidence"]
                }

                if acc_info["classification"] == "overhead":
                    overhead_txns.append(txn_data)
                elif acc_info["classification"] == "job_cost":
                    job_cost_txns.append(txn_data)
                else:
                    mixed_txns.append(txn_data)

        return {
            "overhead": overhead_txns,
            "job_cost": job_cost_txns,
            "mixed": mixed_txns
        }

    def get_overhead_analysis(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        Comprehensive overhead analysis for break-even calculation.

        Returns:
        - Total overhead by category
        - Monthly overhead trend
        - Average monthly overhead
        - Break-even scenarios at various margins
        - Job cost summary for gross margin calculation
        """
        today = datetime.now().date()
        if not start_date:
            start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = (today + timedelta(days=365)).strftime("%Y-%m-%d")

        # Get transactions by classification
        txns = self.get_expense_transactions_by_classification(start_date, end_date)

        # Aggregate overhead by category
        overhead_by_category = {}
        overhead_monthly = {}

        for txn in txns["overhead"]:
            category = txn["category"]
            amount = txn["amount"]
            month = txn["txn_date"][:7] if txn["txn_date"] else "unknown"

            overhead_by_category[category] = overhead_by_category.get(category, 0) + amount

            if month not in overhead_monthly:
                overhead_monthly[month] = {}
            overhead_monthly[month][category] = overhead_monthly[month].get(category, 0) + amount

        total_overhead = sum(overhead_by_category.values())

        # Aggregate job costs by category
        job_cost_by_category = {}
        for txn in txns["job_cost"]:
            category = txn["category"]
            amount = txn["amount"]
            job_cost_by_category[category] = job_cost_by_category.get(category, 0) + amount

        total_job_costs = sum(job_cost_by_category.values())

        # Calculate averages
        num_months = len(overhead_monthly) if overhead_monthly else 1
        avg_monthly_overhead = total_overhead / num_months
        avg_monthly_job_costs = total_job_costs / num_months

        # Get revenue for gross margin calculation
        revenue_data = self.get_revenue_mtd()  # This is MTD, we need TTM
        # For now, estimate from invoices
        invoice_query = (
            f"SELECT * FROM Invoice "
            f"WHERE TxnDate >= '{start_date}' AND TxnDate <= '{end_date}'"
        )
        invoices = self.query(invoice_query)
        total_revenue = sum(
            float(inv.get("TotalAmt", 0) or 0) for inv in invoices
        )
        avg_monthly_revenue = total_revenue / num_months if num_months > 0 else 0

        # Calculate gross margin
        if avg_monthly_revenue > 0:
            gross_profit = avg_monthly_revenue - avg_monthly_job_costs
            gross_margin = gross_profit / avg_monthly_revenue
        else:
            gross_margin = 0.30  # Default assumption for roofing

        # Break-even calculations
        break_even_scenarios = {}
        for margin in [0.20, 0.25, 0.30, 0.35, 0.40]:
            if margin > 0:
                monthly_break_even = avg_monthly_overhead / margin
                break_even_scenarios[f"{int(margin*100)}%"] = {
                    "margin": margin,
                    "monthly_break_even": round(monthly_break_even, 2),
                    "annual_break_even": round(monthly_break_even * 12, 2),
                    "is_current": abs(margin - gross_margin) < 0.025
                }

        # Actual break-even at current margin
        actual_break_even = avg_monthly_overhead / gross_margin if gross_margin > 0 else 0

        return {
            "period": {"start": start_date, "end": end_date, "months": num_months},

            "overhead": {
                "total": round(total_overhead, 2),
                "monthly_average": round(avg_monthly_overhead, 2),
                "by_category": {k: round(v, 2) for k, v in sorted(
                    overhead_by_category.items(), key=lambda x: -x[1]
                )},
                "monthly_trend": {
                    k: {c: round(a, 2) for c, a in v.items()}
                    for k, v in sorted(overhead_monthly.items())
                },
                "transaction_count": len(txns["overhead"])
            },

            "job_costs": {
                "total": round(total_job_costs, 2),
                "monthly_average": round(avg_monthly_job_costs, 2),
                "by_category": {k: round(v, 2) for k, v in sorted(
                    job_cost_by_category.items(), key=lambda x: -x[1]
                )},
                "transaction_count": len(txns["job_cost"])
            },

            "revenue": {
                "total": round(total_revenue, 2),
                "monthly_average": round(avg_monthly_revenue, 2)
            },

            "profitability": {
                "gross_margin": round(gross_margin, 4),
                "gross_margin_pct": f"{gross_margin*100:.1f}%",
                "gross_profit_monthly": round(avg_monthly_revenue - avg_monthly_job_costs, 2)
            },

            "break_even": {
                "current_margin": {
                    "margin": round(gross_margin, 4),
                    "monthly": round(actual_break_even, 2),
                    "annual": round(actual_break_even * 12, 2)
                },
                "scenarios": break_even_scenarios
            },

            "mixed_expenses": {
                "total": round(sum(t["amount"] for t in txns["mixed"]), 2),
                "count": len(txns["mixed"]),
                "note": "These expenses need manual review to classify as overhead or job cost"
            },

            "confidence": {
                "overhead_avg": round(
                    sum(t["confidence"] for t in txns["overhead"]) / len(txns["overhead"]), 2
                ) if txns["overhead"] else 0,
                "job_cost_avg": round(
                    sum(t["confidence"] for t in txns["job_cost"]) / len(txns["job_cost"]), 2
                ) if txns["job_cost"] else 0
            }
        }

    def get_payroll_accounts(self) -> List[Dict]:
        """
        Get all payroll-related accounts from Chart of Accounts.

        Identifies accounts by:
        - AccountSubType containing 'Payroll' (PayrollExpenses, PayrollTaxExpenses, etc.)
        - Account names containing payroll-related keywords
        """
        query_str = "SELECT * FROM Account WHERE Active = true"
        accounts = self.query(query_str)

        # Payroll-related AccountSubTypes in QBO
        payroll_subtypes = {
            "PayrollExpenses", "PayrollTaxExpenses", "PayrollWageExpenses",
            "PayrollTaxPayable", "PayrollClearing"
        }

        # Keywords to identify payroll accounts by name
        payroll_keywords = [
            "payroll", "wages", "salary", "salaries", "labor", "labour",
            "fica", "futa", "suta", "medicare", "social security",
            "workers comp", "workman", "health insurance", "401k", "retirement",
            "employee benefit", "pto", "vacation pay", "sick pay"
        ]

        payroll_accounts = []
        for acc in accounts:
            account_subtype = acc.get("AccountSubType", "")
            account_name = acc.get("Name", "").lower()

            is_payroll = False
            match_reason = None

            # Check by subtype
            if account_subtype in payroll_subtypes:
                is_payroll = True
                match_reason = f"AccountSubType: {account_subtype}"

            # Check by name keywords
            if not is_payroll:
                for keyword in payroll_keywords:
                    if keyword in account_name:
                        is_payroll = True
                        match_reason = f"Name contains: {keyword}"
                        break

            if is_payroll:
                payroll_accounts.append({
                    "id": acc.get("Id"),
                    "name": acc.get("Name"),
                    "account_type": acc.get("AccountType"),
                    "account_sub_type": account_subtype,
                    "code": acc.get("AcctNum", ""),
                    "balance": float(acc.get("CurrentBalance", 0) or 0),
                    "match_reason": match_reason,
                    "classification": self._classify_payroll_account(acc)
                })

        return payroll_accounts

    def _classify_payroll_account(self, account: Dict) -> str:
        """Classify a payroll account into a category for reporting"""
        account_type = account.get("AccountType", "")
        account_subtype = account.get("AccountSubType", "")
        name = account.get("Name", "").lower()

        # Expense classifications
        if account_type == "Expense":
            if "tax" in name or account_subtype == "PayrollTaxExpenses":
                return "payroll_tax_expense"
            elif any(kw in name for kw in ["health", "insurance", "benefit", "401k", "retirement"]):
                return "employee_benefits"
            elif any(kw in name for kw in ["workers comp", "workman"]):
                return "workers_comp"
            else:
                return "wages_salaries"

        # Liability classifications
        elif account_type in ["Other Current Liability", "Liability"]:
            if "tax" in name:
                return "payroll_tax_liability"
            else:
                return "payroll_liability"

        return "other_payroll"

    def get_payroll_transactions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Get all transactions posted to payroll-related accounts.

        This captures payroll expenses regardless of how they were entered:
        - Direct payroll entries from QBO Payroll
        - Journal entries from external payroll (Gusto, ADP)
        - Manual payroll entries
        """
        today = datetime.now().date()
        if not start_date:
            start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = (today + timedelta(days=365)).strftime("%Y-%m-%d")

        # First get all payroll account IDs
        payroll_accounts = self.get_payroll_accounts()
        if not payroll_accounts:
            return []

        payroll_account_ids = {acc["id"]: acc for acc in payroll_accounts}

        # Query purchases that might have payroll line items
        purchase_query = (
            f"SELECT * FROM Purchase "
            f"WHERE TxnDate >= '{start_date}' AND TxnDate <= '{end_date}'"
        )
        purchases = self.query(purchase_query)

        # Query journal entries (common for external payroll imports)
        je_query = (
            f"SELECT * FROM JournalEntry "
            f"WHERE TxnDate >= '{start_date}' AND TxnDate <= '{end_date}'"
        )
        try:
            journal_entries = self.query(je_query)
        except Exception:
            journal_entries = []

        payroll_transactions = []

        # Process purchases for payroll line items
        for purchase in purchases:
            lines = purchase.get("Line", [])
            if not isinstance(lines, list):
                lines = [lines]

            for line in lines:
                if not isinstance(line, dict):
                    continue

                # Check AccountBasedExpenseLineDetail for account reference
                detail = line.get("AccountBasedExpenseLineDetail", {})
                account_ref = detail.get("AccountRef", {})
                account_id = account_ref.get("value") if isinstance(account_ref, dict) else None

                if account_id and account_id in payroll_account_ids:
                    amount = float(line.get("Amount", 0) or 0)
                    payroll_transactions.append({
                        "source": "Purchase",
                        "source_id": purchase.get("Id"),
                        "txn_date": purchase.get("TxnDate"),
                        "account_id": account_id,
                        "account_name": payroll_account_ids[account_id]["name"],
                        "classification": payroll_account_ids[account_id]["classification"],
                        "amount": amount,
                        "description": line.get("Description", ""),
                        "vendor": purchase.get("EntityRef", {}).get("name") if purchase.get("EntityRef") else None,
                        "doc_number": purchase.get("DocNumber")
                    })

        # Process journal entries for payroll
        for je in journal_entries:
            lines = je.get("Line", [])
            if not isinstance(lines, list):
                lines = [lines]

            for line in lines:
                if not isinstance(line, dict):
                    continue

                detail = line.get("JournalEntryLineDetail", {})
                account_ref = detail.get("AccountRef", {})
                account_id = account_ref.get("value") if isinstance(account_ref, dict) else None
                posting_type = detail.get("PostingType", "")

                if account_id and account_id in payroll_account_ids:
                    amount = float(line.get("Amount", 0) or 0)
                    # Debit to expense = positive, Credit = negative
                    if posting_type == "Credit":
                        amount = -amount

                    payroll_transactions.append({
                        "source": "JournalEntry",
                        "source_id": je.get("Id"),
                        "txn_date": je.get("TxnDate"),
                        "account_id": account_id,
                        "account_name": payroll_account_ids[account_id]["name"],
                        "classification": payroll_account_ids[account_id]["classification"],
                        "amount": amount,
                        "description": line.get("Description", "") or je.get("PrivateNote", ""),
                        "vendor": None,
                        "doc_number": je.get("DocNumber")
                    })

        return payroll_transactions

    def get_payroll_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        Get summarized payroll data for analysis.

        Returns:
            - Total payroll expense
            - Breakdown by classification (wages, taxes, benefits, etc.)
            - Monthly trend
            - Average monthly payroll (for overhead calculation)
        """
        transactions = self.get_payroll_transactions(start_date, end_date)

        if not transactions:
            return {
                "total_payroll": 0,
                "by_classification": {},
                "monthly_breakdown": {},
                "avg_monthly_payroll": 0,
                "transaction_count": 0
            }

        # Aggregate by classification
        by_classification = {}
        monthly_breakdown = {}

        for txn in transactions:
            classification = txn["classification"]
            amount = txn["amount"]
            txn_date = txn["txn_date"]

            # Only count positive amounts (expenses)
            if amount > 0:
                by_classification[classification] = by_classification.get(classification, 0) + amount

                # Monthly breakdown
                if txn_date:
                    month_key = txn_date[:7]  # YYYY-MM
                    if month_key not in monthly_breakdown:
                        monthly_breakdown[month_key] = {}
                    monthly_breakdown[month_key][classification] = \
                        monthly_breakdown[month_key].get(classification, 0) + amount

        total_payroll = sum(by_classification.values())

        # Calculate average monthly
        num_months = len(monthly_breakdown) if monthly_breakdown else 1
        avg_monthly = total_payroll / num_months

        return {
            "total_payroll": round(total_payroll, 2),
            "by_classification": {k: round(v, 2) for k, v in by_classification.items()},
            "monthly_breakdown": {
                k: {c: round(a, 2) for c, a in v.items()}
                for k, v in sorted(monthly_breakdown.items())
            },
            "avg_monthly_payroll": round(avg_monthly, 2),
            "transaction_count": len([t for t in transactions if t["amount"] > 0]),
            "period": {
                "start": start_date,
                "end": end_date
            }
        }

