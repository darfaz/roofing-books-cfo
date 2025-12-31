"""
Budget vs Actual Service
Track budget performance and variance analysis
"""
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
from collections import defaultdict
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


class BudgetService:
    """Budget tracking and variance analysis"""

    # Default budget categories for roofing contractors
    DEFAULT_BUDGET_CATEGORIES = {
        "revenue": {
            "residential": {"monthly": 50000, "description": "Residential roofing jobs"},
            "commercial": {"monthly": 30000, "description": "Commercial roofing jobs"},
            "repairs": {"monthly": 15000, "description": "Repair and maintenance"},
            "insurance_work": {"monthly": 20000, "description": "Insurance restoration"}
        },
        "cogs": {
            "materials": {"monthly": 35000, "description": "Roofing materials"},
            "labor_direct": {"monthly": 25000, "description": "Direct labor (crews)"},
            "subcontractors": {"monthly": 10000, "description": "Subcontractor costs"},
            "equipment": {"monthly": 5000, "description": "Equipment and tools"}
        },
        "operating": {
            "payroll_admin": {"monthly": 12000, "description": "Administrative payroll"},
            "rent": {"monthly": 3000, "description": "Facility rent"},
            "utilities": {"monthly": 800, "description": "Utilities"},
            "insurance": {"monthly": 2500, "description": "Business insurance"},
            "marketing": {"monthly": 2000, "description": "Marketing and advertising"},
            "vehicle": {"monthly": 3000, "description": "Vehicle expenses"},
            "office": {"monthly": 500, "description": "Office supplies"},
            "professional": {"monthly": 1000, "description": "Professional services"}
        }
    }

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.supabase = create_client(
            os.getenv("SUPABASE_URL", ""),
            os.getenv("SUPABASE_SERVICE_KEY", "")
        )

    def get_budget(self, year: int, month: int) -> Dict[str, Any]:
        """
        Get budget for a specific month

        Args:
            year: Budget year
            month: Budget month (1-12)

        Returns:
            Budget data with categories and amounts
        """
        # Try to get from database
        budget_key = f"{year}-{month:02d}"
        try:
            result = self.supabase.table("budgets")\
                .select("*")\
                .eq("tenant_id", self.tenant_id)\
                .eq("budget_period", budget_key)\
                .execute()

            if result.data:
                return result.data[0]
        except Exception:
            # Table may not exist yet - use defaults
            pass

        # Return default budget structure
        return {
            "tenant_id": self.tenant_id,
            "budget_period": budget_key,
            "year": year,
            "month": month,
            "categories": self.DEFAULT_BUDGET_CATEGORIES,
            "is_default": True
        }

    def save_budget(
        self,
        year: int,
        month: int,
        categories: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save or update budget for a month

        Args:
            year: Budget year
            month: Budget month
            categories: Budget categories with amounts

        Returns:
            Saved budget data
        """
        budget_key = f"{year}-{month:02d}"

        budget_data = {
            "tenant_id": self.tenant_id,
            "budget_period": budget_key,
            "year": year,
            "month": month,
            "categories": categories,
            "updated_at": datetime.utcnow().isoformat()
        }

        # Upsert budget
        result = self.supabase.table("budgets")\
            .upsert(budget_data, on_conflict="tenant_id,budget_period")\
            .execute()

        return result.data[0] if result.data else budget_data

    def get_actuals(
        self,
        year: int,
        month: int
    ) -> Dict[str, Any]:
        """
        Get actual revenue and expenses for a month

        Args:
            year: Year
            month: Month (1-12)

        Returns:
            Actual amounts by category
        """
        # Calculate date range
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        # Get revenue (invoices)
        invoices = self.supabase.table("transactions")\
            .select("total_amount, memo, category, metadata")\
            .eq("tenant_id", self.tenant_id)\
            .eq("transaction_type", "invoice")\
            .gte("transaction_date", start_date.isoformat())\
            .lte("transaction_date", end_date.isoformat())\
            .neq("status", "voided")\
            .execute()

        # Get expenses (bills, expenses)
        expenses = self.supabase.table("transactions")\
            .select("total_amount, memo, category, metadata")\
            .eq("tenant_id", self.tenant_id)\
            .in_("transaction_type", ["bill", "expense"])\
            .gte("transaction_date", start_date.isoformat())\
            .lte("transaction_date", end_date.isoformat())\
            .neq("status", "voided")\
            .execute()

        # Categorize revenue
        revenue_totals = defaultdict(float)
        for inv in (invoices.data or []):
            amount = float(inv.get("total_amount", 0))
            memo = (inv.get("memo") or "").lower()
            category = (inv.get("category") or "").lower()

            # Classify by keywords
            if "commercial" in memo or "commercial" in category:
                revenue_totals["commercial"] += amount
            elif "insurance" in memo or "storm" in memo or "insurance" in category:
                revenue_totals["insurance_work"] += amount
            elif "repair" in memo or "maintenance" in memo:
                revenue_totals["repairs"] += amount
            else:
                revenue_totals["residential"] += amount

        # Categorize expenses
        cogs_totals = defaultdict(float)
        operating_totals = defaultdict(float)

        for exp in (expenses.data or []):
            amount = abs(float(exp.get("total_amount", 0)))
            memo = (exp.get("memo") or "").lower()
            category = (exp.get("category") or "").lower()

            # COGS categories
            if "material" in memo or "shingles" in memo or "lumber" in memo:
                cogs_totals["materials"] += amount
            elif "payroll" in memo or "wages" in memo or "labor" in memo:
                if "admin" in memo or "office" in memo:
                    operating_totals["payroll_admin"] += amount
                else:
                    cogs_totals["labor_direct"] += amount
            elif "subcontract" in memo or "sub " in memo:
                cogs_totals["subcontractors"] += amount
            elif "equipment" in memo or "tool" in memo:
                cogs_totals["equipment"] += amount
            # Operating categories
            elif "rent" in memo or "lease" in memo:
                operating_totals["rent"] += amount
            elif "utility" in memo or "electric" in memo or "gas" in memo:
                operating_totals["utilities"] += amount
            elif "insurance" in memo:
                operating_totals["insurance"] += amount
            elif "marketing" in memo or "advertis" in memo:
                operating_totals["marketing"] += amount
            elif "vehicle" in memo or "fuel" in memo or "gas" in memo or "truck" in memo:
                operating_totals["vehicle"] += amount
            elif "office" in memo or "supply" in memo or "supplies" in memo:
                operating_totals["office"] += amount
            elif "legal" in memo or "accounting" in memo or "professional" in memo:
                operating_totals["professional"] += amount
            else:
                operating_totals["other"] += amount

        return {
            "year": year,
            "month": month,
            "period": f"{year}-{month:02d}",
            "revenue": dict(revenue_totals),
            "cogs": dict(cogs_totals),
            "operating": dict(operating_totals),
            "totals": {
                "revenue": sum(revenue_totals.values()),
                "cogs": sum(cogs_totals.values()),
                "operating": sum(operating_totals.values()),
                "gross_profit": sum(revenue_totals.values()) - sum(cogs_totals.values()),
                "net_income": sum(revenue_totals.values()) - sum(cogs_totals.values()) - sum(operating_totals.values())
            }
        }

    def calculate_variance(
        self,
        year: int,
        month: int
    ) -> Dict[str, Any]:
        """
        Calculate budget vs actual variance

        Args:
            year: Year
            month: Month

        Returns:
            Variance analysis by category
        """
        budget = self.get_budget(year, month)
        actuals = self.get_actuals(year, month)

        budget_cats = budget.get("categories", self.DEFAULT_BUDGET_CATEGORIES)

        variance = {
            "period": f"{year}-{month:02d}",
            "revenue": {},
            "cogs": {},
            "operating": {},
            "summary": {}
        }

        # Revenue variance
        budget_revenue_total = 0
        actual_revenue_total = 0
        for cat, data in budget_cats.get("revenue", {}).items():
            budget_amt = data.get("monthly", 0)
            actual_amt = actuals.get("revenue", {}).get(cat, 0)
            var_amt = actual_amt - budget_amt
            var_pct = (var_amt / budget_amt * 100) if budget_amt > 0 else 0

            variance["revenue"][cat] = {
                "budget": budget_amt,
                "actual": round(actual_amt, 2),
                "variance": round(var_amt, 2),
                "variance_pct": round(var_pct, 1),
                "status": "over" if var_amt > 0 else "under" if var_amt < 0 else "on_target"
            }
            budget_revenue_total += budget_amt
            actual_revenue_total += actual_amt

        # COGS variance
        budget_cogs_total = 0
        actual_cogs_total = 0
        for cat, data in budget_cats.get("cogs", {}).items():
            budget_amt = data.get("monthly", 0)
            actual_amt = actuals.get("cogs", {}).get(cat, 0)
            var_amt = actual_amt - budget_amt
            var_pct = (var_amt / budget_amt * 100) if budget_amt > 0 else 0

            # For expenses, under budget is good (positive variance)
            variance["cogs"][cat] = {
                "budget": budget_amt,
                "actual": round(actual_amt, 2),
                "variance": round(var_amt, 2),
                "variance_pct": round(var_pct, 1),
                "status": "over" if var_amt > 0 else "under" if var_amt < 0 else "on_target"
            }
            budget_cogs_total += budget_amt
            actual_cogs_total += actual_amt

        # Operating expense variance
        budget_op_total = 0
        actual_op_total = 0
        for cat, data in budget_cats.get("operating", {}).items():
            budget_amt = data.get("monthly", 0)
            actual_amt = actuals.get("operating", {}).get(cat, 0)
            var_amt = actual_amt - budget_amt
            var_pct = (var_amt / budget_amt * 100) if budget_amt > 0 else 0

            variance["operating"][cat] = {
                "budget": budget_amt,
                "actual": round(actual_amt, 2),
                "variance": round(var_amt, 2),
                "variance_pct": round(var_pct, 1),
                "status": "over" if var_amt > 0 else "under" if var_amt < 0 else "on_target"
            }
            budget_op_total += budget_amt
            actual_op_total += actual_amt

        # Summary
        budget_gp = budget_revenue_total - budget_cogs_total
        actual_gp = actual_revenue_total - actual_cogs_total
        budget_ni = budget_gp - budget_op_total
        actual_ni = actual_gp - actual_op_total

        variance["summary"] = {
            "revenue": {
                "budget": budget_revenue_total,
                "actual": round(actual_revenue_total, 2),
                "variance": round(actual_revenue_total - budget_revenue_total, 2),
                "variance_pct": round((actual_revenue_total - budget_revenue_total) / budget_revenue_total * 100, 1) if budget_revenue_total > 0 else 0
            },
            "cogs": {
                "budget": budget_cogs_total,
                "actual": round(actual_cogs_total, 2),
                "variance": round(actual_cogs_total - budget_cogs_total, 2),
                "variance_pct": round((actual_cogs_total - budget_cogs_total) / budget_cogs_total * 100, 1) if budget_cogs_total > 0 else 0
            },
            "gross_profit": {
                "budget": budget_gp,
                "actual": round(actual_gp, 2),
                "variance": round(actual_gp - budget_gp, 2),
                "variance_pct": round((actual_gp - budget_gp) / budget_gp * 100, 1) if budget_gp > 0 else 0
            },
            "operating": {
                "budget": budget_op_total,
                "actual": round(actual_op_total, 2),
                "variance": round(actual_op_total - budget_op_total, 2),
                "variance_pct": round((actual_op_total - budget_op_total) / budget_op_total * 100, 1) if budget_op_total > 0 else 0
            },
            "net_income": {
                "budget": budget_ni,
                "actual": round(actual_ni, 2),
                "variance": round(actual_ni - budget_ni, 2),
                "variance_pct": round((actual_ni - budget_ni) / budget_ni * 100, 1) if budget_ni > 0 else 0
            }
        }

        return variance

    def get_ytd_performance(self, year: int, through_month: int) -> Dict[str, Any]:
        """
        Get year-to-date budget performance

        Args:
            year: Year
            through_month: Last month to include (1-12)

        Returns:
            YTD variance analysis
        """
        ytd_budget = {
            "revenue": defaultdict(float),
            "cogs": defaultdict(float),
            "operating": defaultdict(float)
        }
        ytd_actual = {
            "revenue": defaultdict(float),
            "cogs": defaultdict(float),
            "operating": defaultdict(float)
        }

        for month in range(1, through_month + 1):
            budget = self.get_budget(year, month)
            actuals = self.get_actuals(year, month)

            budget_cats = budget.get("categories", self.DEFAULT_BUDGET_CATEGORIES)

            # Aggregate budget
            for cat_type in ["revenue", "cogs", "operating"]:
                for cat, data in budget_cats.get(cat_type, {}).items():
                    ytd_budget[cat_type][cat] += data.get("monthly", 0)

            # Aggregate actuals
            for cat, amt in actuals.get("revenue", {}).items():
                ytd_actual["revenue"][cat] += amt
            for cat, amt in actuals.get("cogs", {}).items():
                ytd_actual["cogs"][cat] += amt
            for cat, amt in actuals.get("operating", {}).items():
                ytd_actual["operating"][cat] += amt

        # Calculate totals
        budget_revenue = sum(ytd_budget["revenue"].values())
        budget_cogs = sum(ytd_budget["cogs"].values())
        budget_operating = sum(ytd_budget["operating"].values())
        actual_revenue = sum(ytd_actual["revenue"].values())
        actual_cogs = sum(ytd_actual["cogs"].values())
        actual_operating = sum(ytd_actual["operating"].values())

        budget_gp = budget_revenue - budget_cogs
        actual_gp = actual_revenue - actual_cogs
        budget_ni = budget_gp - budget_operating
        actual_ni = actual_gp - actual_operating

        return {
            "year": year,
            "through_month": through_month,
            "period": f"{year} YTD (Jan-{datetime(year, through_month, 1).strftime('%b')})",
            "budget": {
                "revenue": budget_revenue,
                "cogs": budget_cogs,
                "gross_profit": budget_gp,
                "operating": budget_operating,
                "net_income": budget_ni
            },
            "actual": {
                "revenue": round(actual_revenue, 2),
                "cogs": round(actual_cogs, 2),
                "gross_profit": round(actual_gp, 2),
                "operating": round(actual_operating, 2),
                "net_income": round(actual_ni, 2)
            },
            "variance": {
                "revenue": round(actual_revenue - budget_revenue, 2),
                "cogs": round(actual_cogs - budget_cogs, 2),
                "gross_profit": round(actual_gp - budget_gp, 2),
                "operating": round(actual_operating - budget_operating, 2),
                "net_income": round(actual_ni - budget_ni, 2)
            },
            "variance_pct": {
                "revenue": round((actual_revenue - budget_revenue) / budget_revenue * 100, 1) if budget_revenue > 0 else 0,
                "gross_profit": round((actual_gp - budget_gp) / budget_gp * 100, 1) if budget_gp > 0 else 0,
                "net_income": round((actual_ni - budget_ni) / budget_ni * 100, 1) if budget_ni != 0 else 0
            }
        }

    def get_dashboard_metrics(self, year: Optional[int] = None, month: Optional[int] = None) -> Dict[str, Any]:
        """
        Get key budget metrics for dashboard display

        Args:
            year: Year (defaults to current)
            month: Month (defaults to current)

        Returns:
            Key metrics for dashboard cards
        """
        if not year:
            year = date.today().year
        if not month:
            month = date.today().month

        variance = self.calculate_variance(year, month)
        ytd = self.get_ytd_performance(year, month)

        summary = variance.get("summary", {})

        # Determine overall status
        ni_var_pct = summary.get("net_income", {}).get("variance_pct", 0)
        if ni_var_pct >= 10:
            status = "excellent"
            status_color = "green"
        elif ni_var_pct >= 0:
            status = "on_track"
            status_color = "green"
        elif ni_var_pct >= -10:
            status = "caution"
            status_color = "yellow"
        else:
            status = "warning"
            status_color = "red"

        # Find biggest variance items
        over_budget_items = []
        for cat_type in ["cogs", "operating"]:
            for cat, data in variance.get(cat_type, {}).items():
                if data.get("variance", 0) > 1000:  # $1000 threshold
                    over_budget_items.append({
                        "category": cat,
                        "type": cat_type,
                        "variance": data["variance"],
                        "variance_pct": data["variance_pct"]
                    })

        over_budget_items.sort(key=lambda x: x["variance"], reverse=True)

        return {
            "period": f"{year}-{month:02d}",
            "status": status,
            "status_color": status_color,
            "monthly": {
                "revenue_actual": summary.get("revenue", {}).get("actual", 0),
                "revenue_budget": summary.get("revenue", {}).get("budget", 0),
                "revenue_var_pct": summary.get("revenue", {}).get("variance_pct", 0),
                "net_income_actual": summary.get("net_income", {}).get("actual", 0),
                "net_income_budget": summary.get("net_income", {}).get("budget", 0),
                "net_income_var_pct": summary.get("net_income", {}).get("variance_pct", 0),
                "gp_margin_actual": round(summary.get("gross_profit", {}).get("actual", 0) / max(summary.get("revenue", {}).get("actual", 1), 1) * 100, 1),
                "gp_margin_budget": round(summary.get("gross_profit", {}).get("budget", 0) / max(summary.get("revenue", {}).get("budget", 1), 1) * 100, 1)
            },
            "ytd": {
                "revenue_actual": ytd["actual"]["revenue"],
                "revenue_budget": ytd["budget"]["revenue"],
                "net_income_actual": ytd["actual"]["net_income"],
                "net_income_budget": ytd["budget"]["net_income"]
            },
            "top_overages": over_budget_items[:3]
        }
