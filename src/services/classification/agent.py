"""
Transaction Classification Agent
Uses Claude to classify transactions to chart of accounts
"""
import os
from typing import Optional
from pydantic import BaseModel, Field
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Initialize clients
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_SERVICE_KEY", "")
)

class TransactionClassification(BaseModel):
    """Classification result for a transaction"""
    account_code: str = Field(description="Account code to classify to (e.g., '5100')")
    account_name: str = Field(description="Account name (e.g., 'Materials')")
    job_id: Optional[str] = Field(description="Job ID if this cost relates to a specific job", default=None)
    confidence: float = Field(description="Confidence score from 0.0 to 1.0")
    reasoning: str = Field(description="Brief explanation of why this classification was chosen")

class ClassificationAgent:
    """AI agent for classifying transactions"""
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.parser = PydanticOutputParser(pydantic_object=TransactionClassification)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert bookkeeper for roofing contractors.
Your job is to classify each transaction to the correct account in the chart of accounts.

CHART OF ACCOUNTS:
{chart_of_accounts}

ACTIVE JOBS (assign job_id if the transaction clearly relates to a specific job):
{active_jobs}

CLASSIFICATION RULES FOR ROOFING CONTRACTORS:
1. **Materials/Supplies** (code 5100):
   - Home Depot, Lowe's, ABC Supply, Beacon Roofing, SRS Distribution
   - Shingles, underlayment, flashing, nails, caulk, lumber
   
2. **Subcontractors** (code 5200):
   - Payments to other contractors, gutters, HVAC, electrical, dumpster rental
   - Look for "LLC", "Inc", "Services", or contractor names
   
3. **Labor - Direct** (code 5300):
   - Payroll for roofing crews, day laborers
   - Square, Gusto, ADP payroll
   
4. **Equipment Rental** (code 5400):
   - Scissor lifts, boom lifts, scaffolding rental
   - United Rentals, Sunbelt, Home Depot Rental
   
5. **Permits & Fees** (code 5500):
   - City/county permits, inspection fees
   
6. **Dump Fees** (code 5600):
   - Landfill fees, waste disposal, roll-off dumpsters
   
7. **Vehicle Expense** (code 6400):
   - Gas stations, auto parts, repairs, car wash
   - Shell, Chevron, AutoZone, O'Reilly
   
8. **Fuel** (code 6500):
   - Gas stations when clearly just fuel
   
9. **Office Expenses** (code 6200):
   - Office supplies, Amazon (if office items), Staples
   
10. **Software & Subscriptions** (code 6800):
    - Jobber, ServiceTitan, QuickBooks, Microsoft, Google, Dropbox
    
11. **Insurance** (code 6300/6310/6320):
    - Insurance payments, Hartford, State Farm, Progressive
    
12. **Advertising** (code 6100):
    - Google Ads, Facebook, Yelp, Angi, print advertising

JOB MATCHING:
- If the memo mentions a job number (e.g., "JOB-2024-001") or customer name that matches an active job, include the job_id
- Materials purchases often relate to active jobs
- If unsure, leave job_id as null

{format_instructions}"""),
            ("human", """Classify this transaction:

Vendor/Payee: {vendor}
Amount: ${amount}
Date: {date}
Memo/Description: {memo}
Transaction Type: {transaction_type}
""")
        ])
    
    def get_chart_of_accounts(self, tenant_id: str) -> str:
        """Fetch chart of accounts for tenant"""
        result = supabase.table("accounts")\
            .select("code, name, account_type, job_cost_category")\
            .eq("tenant_id", tenant_id)\
            .eq("is_active", True)\
            .order("code")\
            .execute()
        
        lines = []
        for acct in result.data:
            job_cost = f" [Job Cost: {acct['job_cost_category']}]" if acct.get('job_cost_category') else ""
            lines.append(f"{acct['code']} - {acct['name']} ({acct['account_type']}){job_cost}")
        
        return "\n".join(lines)
    
    def get_active_jobs(self, tenant_id: str) -> str:
        """Fetch active jobs for tenant"""
        result = supabase.table("jobs")\
            .select("id, job_number, name, customer_id, customers(name)")\
            .eq("tenant_id", tenant_id)\
            .in_("status", ["scheduled", "in_progress"])\
            .execute()
        
        lines = []
        for job in result.data:
            customer = job.get("customers", {}).get("name", "Unknown")
            lines.append(f"ID: {job['id']} | {job['job_number']}: {job['name']} (Customer: {customer})")
        
        return "\n".join(lines) if lines else "No active jobs"
    
    def classify(
        self,
        tenant_id: str,
        vendor: str,
        amount: float,
        date: str,
        memo: str = "",
        transaction_type: str = "expense"
    ) -> TransactionClassification:
        """
        Classify a single transaction
        
        Args:
            tenant_id: The tenant UUID
            vendor: Vendor/payee name
            amount: Transaction amount
            date: Transaction date (YYYY-MM-DD)
            memo: Transaction memo/description
            transaction_type: Type of transaction
            
        Returns:
            TransactionClassification with account code, job_id, confidence, reasoning
        """
        chart_of_accounts = self.get_chart_of_accounts(tenant_id)
        active_jobs = self.get_active_jobs(tenant_id)
        
        chain = self.prompt | self.llm | self.parser
        
        result = chain.invoke({
            "vendor": vendor,
            "amount": amount,
            "date": date,
            "memo": memo,
            "transaction_type": transaction_type,
            "chart_of_accounts": chart_of_accounts,
            "active_jobs": active_jobs,
            "format_instructions": self.parser.get_format_instructions()
        })
        
        return result
    
    def classify_batch(
        self,
        tenant_id: str,
        transactions: list[dict]
    ) -> list[TransactionClassification]:
        """
        Classify multiple transactions
        
        Args:
            tenant_id: The tenant UUID
            transactions: List of transaction dicts with vendor, amount, date, memo
            
        Returns:
            List of TransactionClassification results
        """
        results = []
        for txn in transactions:
            try:
                result = self.classify(
                    tenant_id=tenant_id,
                    vendor=txn.get("vendor", "Unknown"),
                    amount=txn.get("amount", 0),
                    date=txn.get("date", ""),
                    memo=txn.get("memo", ""),
                    transaction_type=txn.get("transaction_type", "expense")
                )
                results.append(result)
            except Exception as e:
                # Return a low-confidence result on error
                results.append(TransactionClassification(
                    account_code="7900",  # Miscellaneous
                    account_name="Miscellaneous",
                    job_id=None,
                    confidence=0.0,
                    reasoning=f"Classification failed: {str(e)}"
                ))
        
        return results


# ============================================================
# RULE-BASED CLASSIFICATION (faster, cheaper, use first)
# ============================================================

def apply_classification_rules(tenant_id: str, vendor: str, memo: str, amount: float) -> Optional[dict]:
    """
    Try to classify using tenant's rules before falling back to AI
    
    Returns dict with account_id, job_id if matched, None otherwise
    """
    result = supabase.table("classification_rules")\
        .select("*")\
        .eq("tenant_id", tenant_id)\
        .eq("is_active", True)\
        .order("priority")\
        .execute()
    
    vendor_lower = vendor.lower()
    memo_lower = memo.lower()
    
    for rule in result.data:
        # Check vendor pattern
        if rule.get("match_vendor_name"):
            pattern = rule["match_vendor_name"].lower()
            if pattern not in vendor_lower:
                continue
        
        # Check memo pattern
        if rule.get("match_memo"):
            pattern = rule["match_memo"].lower()
            if pattern not in memo_lower:
                continue
        
        # Check amount range
        if rule.get("match_amount_min") and amount < float(rule["match_amount_min"]):
            continue
        if rule.get("match_amount_max") and amount > float(rule["match_amount_max"]):
            continue
        
        # Rule matched!
        # Update rule stats
        supabase.table("classification_rules")\
            .update({
                "times_applied": rule["times_applied"] + 1,
                "last_applied_at": "now()"
            })\
            .eq("id", rule["id"])\
            .execute()
        
        return {
            "account_id": rule["target_account_id"],
            "job_id": rule.get("target_job_id"),
            "rule_id": rule["id"],
            "confidence": 0.95
        }
    
    return None


# ============================================================
# USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    # Test the classification agent
    agent = ClassificationAgent()
    
    # Example transaction
    result = agent.classify(
        tenant_id="YOUR_TENANT_UUID",  # Replace with real tenant ID
        vendor="Home Depot",
        amount=1234.56,
        date="2024-01-15",
        memo="Shingles and underlayment for Smith job",
        transaction_type="expense"
    )
    
    print(f"Account: {result.account_code} - {result.account_name}")
    print(f"Job ID: {result.job_id}")
    print(f"Confidence: {result.confidence:.0%}")
    print(f"Reasoning: {result.reasoning}")
