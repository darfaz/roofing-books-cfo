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
                    except Exception:
                        pass  # Continue with existing token
        
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
        return query_response.get("entities", [])
    
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

