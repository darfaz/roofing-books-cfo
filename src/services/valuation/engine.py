"""
Valuation Engine Service
Calculates business valuations using TTM financials and Matador tier multiples
"""
import os
from datetime import datetime, date, timedelta
from typing import Dict, Optional, Any, List
from decimal import Decimal
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


class ValuationEngine:
    """Calculate business valuations using TTM financials and Matador multiples"""
    
    # Matador tier multiples (applied to SDE/EBITDA)
    MULTIPLES = {
        "below_avg": {"low": 2.8, "high": 3.2},  # ~3x
        "avg": {"low": 4.5, "high": 5.0},         # ~4.5-5x
        "above_avg": {"low": 7.0, "high": 8.0}    # ~7x+
    }
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.supabase = create_client(
            os.getenv("SUPABASE_URL", ""),
            os.getenv("SUPABASE_SERVICE_KEY", "")
        )
    
    def calculate_ttm_financials(self, as_of_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Calculate TTM (Trailing Twelve Months) financials from Books OS data
        
        Args:
            as_of_date: Date to calculate TTM as of (defaults to today)
            
        Returns:
            Dict with ttm_revenue, ttm_expenses, ttm_net_income, and breakdowns
        """
        if not as_of_date:
            as_of_date = date.today()
        
        # Calculate TTM date range (12 months ending on as_of_date)
        ttm_start = date(as_of_date.year - 1, as_of_date.month, as_of_date.day) + timedelta(days=1)
        ttm_end = as_of_date
        
        # Get revenue and expenses using direct queries
        revenue_query = self._query_ttm_revenue_direct(ttm_start, ttm_end)
        expenses_query = self._query_ttm_expenses_direct(ttm_start, ttm_end)
        
        ttm_revenue = float(revenue_query.get("total_revenue", 0))
        ttm_expenses = float(expenses_query.get("total_expenses", 0))
        ttm_net_income = ttm_revenue - ttm_expenses
        
        # Get owner compensation (from expense accounts, typically salary/benefits)
        owner_comp = self._get_owner_compensation(ttm_start, ttm_end)
        
        # Get addbacks (depreciation, interest, taxes)
        addbacks = self._get_addbacks(ttm_start, ttm_end)
        
        return {
            "ttm_revenue": ttm_revenue,
            "ttm_expenses": ttm_expenses,
            "ttm_net_income": ttm_net_income,
            "ttm_start_date": ttm_start.isoformat(),
            "ttm_end_date": ttm_end.isoformat(),
            "owner_compensation": owner_comp,
            "addbacks": addbacks,
            "revenue_breakdown": revenue_query.get("breakdown", {}),
            "expense_breakdown": expenses_query.get("breakdown", {})
        }
    
    def _query_ttm_revenue_direct(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Query TTM revenue directly from transactions table (invoices)"""
        # Get revenue from invoices in date range
        invoices = self.supabase.table("transactions")\
            .select("total_amount")\
            .eq("tenant_id", self.tenant_id)\
            .eq("transaction_type", "invoice")\
            .gte("transaction_date", start_date.isoformat())\
            .lte("transaction_date", end_date.isoformat())\
            .neq("status", "voided")\
            .execute()

        total_revenue = sum(float(t.get("total_amount", 0)) for t in invoices.data) if invoices.data else 0

        return {
            "total_revenue": total_revenue,
            "breakdown": {}
        }
    
    def _query_ttm_expenses_direct(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Query TTM expenses directly from transactions table (bills/expenses)"""
        # Get expenses from bills and expense transactions
        expenses = self.supabase.table("transactions")\
            .select("total_amount, description, category")\
            .eq("tenant_id", self.tenant_id)\
            .in_("transaction_type", ["bill", "expense"])\
            .gte("transaction_date", start_date.isoformat())\
            .lte("transaction_date", end_date.isoformat())\
            .neq("status", "voided")\
            .execute()

        total_expenses = 0
        breakdown = {
            "total": 0,
            "cogs": 0,
            "operating": 0,
            "depreciation": 0,
            "interest": 0,
            "taxes": 0,
            "owner_comp": 0
        }

        for txn in (expenses.data or []):
            # Expenses are stored as negative, convert to positive
            amount = abs(float(txn.get("total_amount", 0)))
            total_expenses += amount

            desc = (txn.get("description") or "").lower()
            category = (txn.get("category") or "").lower()

            # Categorize based on description/category
            if "depreciation" in desc or "amortization" in desc:
                breakdown["depreciation"] += amount
            elif "interest" in desc or "loan interest" in category:
                breakdown["interest"] += amount
            elif "tax" in desc or "taxes" in category:
                breakdown["taxes"] += amount
            elif "materials" in category or "cogs" in category or "cost of goods" in desc:
                breakdown["cogs"] += amount
            else:
                breakdown["operating"] += amount

        breakdown["total"] = total_expenses

        return {
            "total_expenses": total_expenses,
            "breakdown": breakdown
        }
    
    def _get_owner_compensation(self, start_date: date, end_date: date) -> float:
        """Get owner compensation from transactions (salary, benefits, draws)"""
        # Get expense transactions in date range
        expenses = self.supabase.table("transactions")\
            .select("total_amount, description")\
            .eq("tenant_id", self.tenant_id)\
            .in_("transaction_type", ["bill", "expense"])\
            .gte("transaction_date", start_date.isoformat())\
            .lte("transaction_date", end_date.isoformat())\
            .neq("status", "voided")\
            .execute()

        # Filter for owner compensation (case-insensitive)
        owner_keywords = ["owner", "officer", "shareholder", "member", "partner",
                          "draw", "distribution", "dividend", "bonus", "w-2", "w2"]

        owner_comp = 0.0
        for txn in (expenses.data or []):
            desc = (txn.get("description") or "").lower()
            if any(kw in desc for kw in owner_keywords):
                owner_comp += abs(float(txn.get("total_amount", 0)))

        return owner_comp
    
    def _get_addbacks(self, start_date: date, end_date: date) -> Dict[str, float]:
        """Get addbacks for SDE calculation (depreciation, interest, taxes, etc.)"""
        expense_breakdown = self._query_ttm_expenses_direct(start_date, end_date).get("breakdown", {})
        
        return {
            "depreciation": expense_breakdown.get("depreciation", 0),
            "interest": expense_breakdown.get("interest", 0),
            "taxes": expense_breakdown.get("taxes", 0),
            "total": expense_breakdown.get("depreciation", 0) + 
                    expense_breakdown.get("interest", 0) + 
                    expense_breakdown.get("taxes", 0)
        }
    
    def calculate_sde(self, ttm_financials: Dict[str, Any]) -> float:
        """
        Calculate Seller's Discretionary Earnings (SDE)
        
        SDE = Net Income + Owner Compensation + Addbacks (depreciation, interest, taxes, etc.)
        """
        net_income = ttm_financials["ttm_net_income"]
        owner_comp = ttm_financials.get("owner_compensation", 0)
        addbacks = ttm_financials.get("addbacks", {}).get("total", 0)
        
        sde = net_income + owner_comp + addbacks
        return round(sde, 2)
    
    def calculate_ebitda(self, ttm_financials: Dict[str, Any]) -> float:
        """
        Calculate EBITDA (Earnings Before Interest, Taxes, Depreciation, Amortization)
        
        EBITDA = Net Income + Interest + Taxes + Depreciation + Amortization
        """
        net_income = ttm_financials["ttm_net_income"]
        addbacks = ttm_financials.get("addbacks", {})
        
        interest = addbacks.get("interest", 0)
        taxes = addbacks.get("taxes", 0)
        depreciation = addbacks.get("depreciation", 0)
        
        ebitda = net_income + interest + taxes + depreciation
        return round(ebitda, 2)
    
    def get_driver_scores(self, as_of_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get latest driver scores for the tenant
        
        Returns:
            Dict with driver scores and overall assessment
        """
        query = self.supabase.table("driver_scores")\
            .select("*")\
            .eq("tenant_id", self.tenant_id)
        
        if as_of_date:
            query = query.eq("as_of_date", as_of_date.isoformat())
        else:
            # Get latest date
            latest_query = self.supabase.table("driver_scores")\
                .select("as_of_date")\
                .eq("tenant_id", self.tenant_id)\
                .order("as_of_date", desc=True)\
                .limit(1)\
                .execute()
            
            if latest_query.data:
                query = query.eq("as_of_date", latest_query.data[0]["as_of_date"])
            else:
                return {
                    "scores": {},
                    "overall_average": 0,
                    "tier": "below_avg"
                }
        
        result = query.execute()
        
        scores = {}
        total_score = 0
        count = 0
        
        for driver in result.data:
            key = driver["driver_key"]
            # Convert from 0-100 scale to 0-5 scale for tier calculation
            score_value = driver["score"] / 20.0 if driver["score"] <= 100 else 5.0
            scores[key] = score_value
            total_score += score_value
            count += 1
        
        overall_avg = round(total_score / count, 2) if count > 0 else 0
        
        # Determine tier based on overall average score (0-5 scale)
        if overall_avg < 3.0:
            tier = "below_avg"
        elif overall_avg < 4.0:
            tier = "avg"
        else:
            tier = "above_avg"
        
        return {
            "scores": scores,
            "overall_average": overall_avg,
            "tier": tier,
            "as_of_date": result.data[0]["as_of_date"] if result.data else None
        }
    
    def determine_tier(self, driver_scores: Optional[Dict[str, Any]] = None) -> str:
        """
        Determine Matador tier based on driver scores
        
        Returns:
            "below_avg", "avg", or "above_avg"
        """
        if not driver_scores:
            driver_scores = self.get_driver_scores()
        
        return driver_scores.get("tier", "below_avg")
    
    def apply_multiples(
        self, 
        sde: float, 
        ebitda: float, 
        tier: str
    ) -> Dict[str, float]:
        """
        Apply Matador multiples to SDE/EBITDA based on tier
        
        Args:
            sde: Seller's Discretionary Earnings
            ebitda: EBITDA
            tier: "below_avg", "avg", or "above_avg"
            
        Returns:
            Dict with multiple_low, multiple_high, ev_low, ev_high
        """
        multiples = self.MULTIPLES.get(tier, self.MULTIPLES["below_avg"])
        multiple_low = multiples["low"]
        multiple_high = multiples["high"]
        
        # Use EBITDA if available and positive, otherwise use SDE
        earnings_metric = ebitda if ebitda > 0 else sde
        
        ev_low = round(earnings_metric * multiple_low, 2)
        ev_high = round(earnings_metric * multiple_high, 2)
        
        return {
            "multiple_low": multiple_low,
            "multiple_high": multiple_high,
            "ev_low": ev_low,
            "ev_high": ev_high,
            "earnings_metric": earnings_metric,
            "earnings_type": "ebitda" if ebitda > 0 else "sde"
        }
    
    def calculate_confidence_score(
        self,
        ttm_financials: Dict[str, Any],
        driver_scores: Dict[str, Any]
    ) -> int:
        """
        Calculate confidence score (0-100) for the valuation
        
        Factors:
        - Data completeness
        - Driver scores availability
        - Account classification quality
        """
        confidence = 100
        
        # Reduce confidence if revenue is missing/zero
        if ttm_financials.get("ttm_revenue", 0) <= 0:
            confidence -= 30
        
        # Reduce confidence if expenses are missing/zero
        if ttm_financials.get("ttm_expenses", 0) <= 0:
            confidence -= 20
        
        # Reduce confidence if driver scores are missing
        if not driver_scores.get("scores"):
            confidence -= 25
        elif len(driver_scores.get("scores", {})) < 6:
            # Missing some driver scores
            confidence -= (6 - len(driver_scores.get("scores", {}))) * 5
        
        # Ensure confidence is between 0 and 100
        return max(0, min(100, confidence))
    
    def create_valuation_snapshot(
        self,
        as_of_date: Optional[date] = None,
        force_recalculation: bool = False
    ) -> Dict[str, Any]:
        """
        Create a complete valuation snapshot
        
        Args:
            as_of_date: Date for snapshot (defaults to today)
            force_recalculation: Force recalculation if snapshot exists
            
        Returns:
            Dict with snapshot data ready to insert into valuation_snapshots table
        """
        if not as_of_date:
            as_of_date = date.today()
        
        # Check if snapshot already exists
        if not force_recalculation:
            existing = self.supabase.table("valuation_snapshots")\
                .select("id")\
                .eq("tenant_id", self.tenant_id)\
                .eq("as_of_date", as_of_date.isoformat())\
                .limit(1)\
                .execute()
            
            if existing.data:
                raise ValueError(
                    f"Valuation snapshot already exists for {as_of_date.isoformat()}. "
                    "Use force_recalculation=True to override."
                )
        
        # Calculate TTM financials
        ttm_financials = self.calculate_ttm_financials(as_of_date)
        
        # Calculate SDE and EBITDA
        sde = self.calculate_sde(ttm_financials)
        ebitda = self.calculate_ebitda(ttm_financials)
        
        # Get driver scores and determine tier
        driver_scores = self.get_driver_scores(as_of_date)
        tier = driver_scores.get("tier", "below_avg")
        
        # Apply multiples
        valuation_range = self.apply_multiples(sde, ebitda, tier)
        
        # Calculate confidence score
        confidence_score = self.calculate_confidence_score(ttm_financials, driver_scores)
        
        # Build drivers_json from driver scores
        drivers_json = driver_scores.get("scores", {})
        
        # Determine if review is required
        review_required = confidence_score < 80
        
        # Build snapshot data
        snapshot_data = {
            "tenant_id": self.tenant_id,
            "as_of_date": as_of_date.isoformat(),
            "ttm_revenue": ttm_financials["ttm_revenue"],
            "ttm_sde": sde,
            "ttm_ebitda": ebitda,
            "tier": tier,
            "multiple_low": valuation_range["multiple_low"],
            "multiple_high": valuation_range["multiple_high"],
            "ev_low": valuation_range["ev_low"],
            "ev_high": valuation_range["ev_high"],
            "confidence_score": confidence_score,
            "drivers_json": drivers_json,
            "computed_by": "valuation_engine",
            "automation_tier": "hybrid",
            "human_reviewed": False,
            "review_required": review_required
        }
        
        return snapshot_data





