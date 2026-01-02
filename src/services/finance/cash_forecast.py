"""
Cash Flow Forecast Service
13-week rolling cash forecast using AR, AP, and historical patterns
"""
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from collections import defaultdict
from dotenv import load_dotenv
from supabase import create_client, Client

from .ap import APService

load_dotenv()


class CashFlowForecastService:
    """13-week rolling cash flow forecast"""

    # Collection assumptions by aging bucket
    AR_COLLECTION_RATES = {
        "current": {"week_1": 0.15, "week_2": 0.30, "week_3": 0.25, "week_4": 0.20, "later": 0.10},
        "1-30": {"week_1": 0.25, "week_2": 0.35, "week_3": 0.25, "later": 0.15},
        "31-60": {"week_1": 0.30, "week_2": 0.30, "week_3": 0.20, "later": 0.20},
        "61-90": {"week_1": 0.20, "week_2": 0.20, "later": 0.60},  # Higher bad debt risk
        "90+": {"week_1": 0.10, "later": 0.90}  # Very high bad debt risk
    }

    # Default recurring expenses (weekly estimates as % of monthly)
    RECURRING_EXPENSE_DEFAULTS = {
        "payroll": 0.25,        # 25% of monthly each week
        "rent": 0.0,            # Monthly, not weekly
        "utilities": 0.0,       # Monthly
        "insurance": 0.0,       # Monthly
        "materials": 0.20,      # Tied to jobs
        "other": 0.10
    }

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.supabase = create_client(
            os.getenv("SUPABASE_URL", ""),
            os.getenv("SUPABASE_SERVICE_KEY", "")
        )
        self.ap_service = APService(tenant_id)

    def get_current_cash_balance(self) -> float:
        """
        Get current cash balance from bank accounts

        Returns:
            Total cash balance across all bank accounts (actual value, may be $0 or negative)
        """
        # Calculate from deposits minus withdrawals in last 30 days
        # This is a simplified approach - ideally would integrate with bank feeds
        today = date.today()
        start_date = (today - timedelta(days=30)).isoformat()

        # Use qbo_type column (not transaction_type) to match synced QB data
        deposits = self.supabase.table("transactions")\
            .select("total_amount")\
            .eq("tenant_id", self.tenant_id)\
            .eq("qbo_type", "Deposit")\
            .gte("transaction_date", start_date)\
            .neq("status", "voided")\
            .execute()

        deposit_total = sum(float(t.get("total_amount", 0)) for t in (deposits.data or []))

        # Get payments made - use qbo_type column
        payments = self.supabase.table("transactions")\
            .select("total_amount")\
            .eq("tenant_id", self.tenant_id)\
            .eq("qbo_type", "BillPayment")\
            .gte("transaction_date", start_date)\
            .neq("status", "voided")\
            .execute()

        payment_total = sum(abs(float(t.get("total_amount", 0))) for t in (payments.data or []))

        # Return actual calculated value - NO fabricated defaults
        # If no transactions, return 0 (not a fake $50K)
        return deposit_total - payment_total

    def get_ar_aging(self, as_of_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get AR aging buckets from unpaid invoices

        Args:
            as_of_date: Date to calculate aging from

        Returns:
            Dict with AR aging buckets and totals
        """
        if not as_of_date:
            as_of_date = date.today()

        # Get unpaid invoices - use qbo_type column to match synced QB data
        result = self.supabase.table("transactions")\
            .select("id, transaction_date, total_amount, customer_id, memo, metadata")\
            .eq("tenant_id", self.tenant_id)\
            .eq("qbo_type", "Invoice")\
            .eq("status", "pending")\
            .neq("status", "voided")\
            .execute()

        aging = {
            "current": 0.0,
            "1-30": 0.0,
            "31-60": 0.0,
            "61-90": 0.0,
            "90+": 0.0
        }

        invoices_by_bucket = defaultdict(list)

        for inv in (result.data or []):
            metadata = inv.get("metadata", {}) or {}
            due_date_str = metadata.get("due_date")

            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    txn_date = datetime.strptime(inv["transaction_date"], "%Y-%m-%d").date()
                    due_date = txn_date + timedelta(days=30)
            else:
                txn_date = datetime.strptime(inv["transaction_date"], "%Y-%m-%d").date()
                due_date = txn_date + timedelta(days=30)

            days_past_due = (as_of_date - due_date).days
            amount = float(inv["total_amount"])

            invoice_data = {
                "id": inv["id"],
                "amount": amount,
                "due_date": due_date.isoformat(),
                "days_past_due": days_past_due
            }

            if days_past_due <= 0:
                aging["current"] += amount
                invoices_by_bucket["current"].append(invoice_data)
            elif days_past_due <= 30:
                aging["1-30"] += amount
                invoices_by_bucket["1-30"].append(invoice_data)
            elif days_past_due <= 60:
                aging["31-60"] += amount
                invoices_by_bucket["31-60"].append(invoice_data)
            elif days_past_due <= 90:
                aging["61-90"] += amount
                invoices_by_bucket["61-90"].append(invoice_data)
            else:
                aging["90+"] += amount
                invoices_by_bucket["90+"].append(invoice_data)

        total = sum(aging.values())
        overdue = aging["1-30"] + aging["31-60"] + aging["61-90"] + aging["90+"]

        return {
            "aging": aging,
            "total": total,
            "overdue": overdue,
            "overdue_pct": (overdue / total * 100) if total > 0 else 0,
            "as_of_date": as_of_date.isoformat(),
            "invoices_by_bucket": dict(invoices_by_bucket)
        }

    def project_collections(
        self,
        ar_aging: Dict[str, Any],
        weeks: int = 13
    ) -> List[Dict[str, Any]]:
        """
        Project expected cash collections from AR aging

        Args:
            ar_aging: AR aging data from get_ar_aging()
            weeks: Number of weeks to project

        Returns:
            List of weekly projected collections
        """
        collections = []
        aging_buckets = ar_aging.get("aging", {})

        for week_num in range(weeks):
            week_total = 0.0
            breakdown = {}

            for bucket, amount in aging_buckets.items():
                rates = self.AR_COLLECTION_RATES.get(bucket, {"week_1": 0.1, "later": 0.9})

                if week_num == 0:
                    rate = rates.get("week_1", 0)
                elif week_num == 1:
                    rate = rates.get("week_2", 0)
                elif week_num == 2:
                    rate = rates.get("week_3", 0)
                elif week_num == 3:
                    rate = rates.get("week_4", 0)
                else:
                    # Distribute remaining over later weeks
                    later_rate = rates.get("later", 0)
                    remaining_weeks = weeks - 4
                    rate = later_rate / max(remaining_weeks, 1) if week_num >= 4 else 0

                bucket_collection = amount * rate
                week_total += bucket_collection
                breakdown[bucket] = bucket_collection

            collections.append({
                "week_number": week_num + 1,
                "projected_collections": round(week_total, 2),
                "breakdown": breakdown
            })

        return collections

    def get_recurring_expenses(self) -> Dict[str, float]:
        """
        Analyze historical expenses to identify recurring patterns

        Returns:
            Dict of estimated weekly recurring expenses by category
        """
        # Get last 90 days of expenses
        end_date = date.today()
        start_date = end_date - timedelta(days=90)

        # Use qbo_type column to match synced QB data
        expenses = self.supabase.table("transactions")\
            .select("total_amount, memo, category, metadata")\
            .eq("tenant_id", self.tenant_id)\
            .in_("qbo_type", ["Bill", "Expense", "BillPayment", "Purchase"])\
            .gte("transaction_date", start_date.isoformat())\
            .neq("status", "voided")\
            .execute()

        # Categorize and average
        category_totals = defaultdict(float)
        for exp in (expenses.data or []):
            amount = abs(float(exp.get("total_amount", 0)))
            memo = (exp.get("memo") or "").lower()
            category = (exp.get("category") or "").lower()

            # Classify by keywords
            if "payroll" in memo or "salary" in memo or "wages" in memo:
                category_totals["payroll"] += amount
            elif "rent" in memo or "lease" in memo:
                category_totals["rent"] += amount
            elif "utility" in memo or "electric" in memo or "gas" in memo or "water" in memo:
                category_totals["utilities"] += amount
            elif "insurance" in memo:
                category_totals["insurance"] += amount
            elif "material" in memo or "supply" in memo or "supplies" in memo:
                category_totals["materials"] += amount
            else:
                category_totals["other"] += amount

        # Convert to weekly averages (90 days = ~13 weeks)
        weekly_expenses = {}
        for cat, total in category_totals.items():
            weekly_expenses[cat] = round(total / 13, 2)

        return weekly_expenses

    def generate_13_week_forecast(
        self,
        as_of_date: Optional[date] = None,
        scenario: str = "base"
    ) -> Dict[str, Any]:
        """
        Generate a complete 13-week cash flow forecast

        Args:
            as_of_date: Start date for forecast
            scenario: "optimistic", "base", or "pessimistic"

        Returns:
            Complete forecast with weekly projections and summary
        """
        if not as_of_date:
            as_of_date = date.today()

        # Scenario adjustments
        if scenario == "optimistic":
            collection_adj = 1.15  # 15% better collections
            expense_adj = 0.90    # 10% lower expenses
        elif scenario == "pessimistic":
            collection_adj = 0.80  # 20% worse collections
            expense_adj = 1.10    # 10% higher expenses
        else:
            collection_adj = 1.0
            expense_adj = 1.0

        # Get current state
        starting_cash = self.get_current_cash_balance()
        ar_aging = self.get_ar_aging(as_of_date)
        ap_schedule = self.ap_service.get_payment_schedule_by_week(weeks=13, as_of_date=as_of_date)
        projected_collections = self.project_collections(ar_aging, weeks=13)
        recurring_expenses = self.get_recurring_expenses()

        # Build weekly forecast
        weekly_forecast = []
        running_cash = starting_cash
        min_cash = starting_cash
        min_cash_week = 0

        for week_num in range(13):
            week_start = as_of_date + timedelta(weeks=week_num)
            week_end = week_start + timedelta(days=6)

            # Inflows
            collections = projected_collections[week_num]["projected_collections"] * collection_adj

            # Outflows
            ap_payments = ap_schedule[week_num]["total_due"]
            recurring = sum(recurring_expenses.values()) * expense_adj

            total_inflows = collections
            total_outflows = ap_payments + recurring

            net_cash_flow = total_inflows - total_outflows
            ending_cash = running_cash + net_cash_flow

            # Track minimum cash point
            if ending_cash < min_cash:
                min_cash = ending_cash
                min_cash_week = week_num + 1

            weekly_forecast.append({
                "week_number": week_num + 1,
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "starting_cash": round(running_cash, 2),
                "inflows": {
                    "collections": round(collections, 2),
                    "total": round(total_inflows, 2)
                },
                "outflows": {
                    "ap_payments": round(ap_payments, 2),
                    "recurring_expenses": round(recurring, 2),
                    "total": round(total_outflows, 2)
                },
                "net_cash_flow": round(net_cash_flow, 2),
                "ending_cash": round(ending_cash, 2)
            })

            running_cash = ending_cash

        # Calculate runway (weeks until cash goes negative)
        runway_weeks = 13
        for week in weekly_forecast:
            if week["ending_cash"] < 0:
                runway_weeks = week["week_number"] - 1
                break

        # Summary metrics
        total_inflows = sum(w["inflows"]["total"] for w in weekly_forecast)
        total_outflows = sum(w["outflows"]["total"] for w in weekly_forecast)
        total_net = total_inflows - total_outflows

        return {
            "forecast_date": as_of_date.isoformat(),
            "scenario": scenario,
            "starting_cash": round(starting_cash, 2),
            "ending_cash": round(running_cash, 2),
            "min_cash": round(min_cash, 2),
            "min_cash_week": min_cash_week,
            "runway_weeks": runway_weeks,
            "summary": {
                "total_inflows": round(total_inflows, 2),
                "total_outflows": round(total_outflows, 2),
                "net_change": round(total_net, 2)
            },
            "ar_total": ar_aging["total"],
            "ap_total": sum(w["total_due"] for w in ap_schedule),
            "weekly_forecast": weekly_forecast
        }

    def get_all_scenarios(self, as_of_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Generate forecasts for all three scenarios

        Returns:
            Dict with base, optimistic, and pessimistic forecasts
        """
        if not as_of_date:
            as_of_date = date.today()

        return {
            "as_of_date": as_of_date.isoformat(),
            "base": self.generate_13_week_forecast(as_of_date, "base"),
            "optimistic": self.generate_13_week_forecast(as_of_date, "optimistic"),
            "pessimistic": self.generate_13_week_forecast(as_of_date, "pessimistic")
        }

    def get_cash_alert_status(self, as_of_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get cash position health status for dashboard

        Returns:
            Status with health indicator and recommendations
        """
        if not as_of_date:
            as_of_date = date.today()

        forecast = self.generate_13_week_forecast(as_of_date, "base")
        runway = forecast["runway_weeks"]
        min_cash = forecast["min_cash"]
        current_cash = forecast["starting_cash"]

        # Determine status
        if runway >= 13 and min_cash > 50000:
            status = "healthy"
            color = "green"
            message = "Cash position is strong with 13+ weeks runway"
        elif runway >= 8 and min_cash > 25000:
            status = "good"
            color = "green"
            message = f"Cash position is good with {runway} weeks runway"
        elif runway >= 4 and min_cash > 10000:
            status = "caution"
            color = "yellow"
            message = f"Monitor closely - {runway} weeks runway"
        else:
            status = "critical"
            color = "red"
            message = f"Action needed - only {runway} weeks runway"

        # Recommendations based on status
        recommendations = []
        if runway < 8:
            recommendations.append("Accelerate AR collections")
        if forecast["ar_total"] > current_cash * 0.5:
            recommendations.append("Follow up on outstanding invoices")
        if min_cash < 25000:
            recommendations.append("Negotiate extended payment terms with vendors")
        if status == "critical":
            recommendations.append("Consider credit line or bridge financing")

        return {
            "status": status,
            "color": color,
            "message": message,
            "runway_weeks": runway,
            "current_cash": current_cash,
            "min_projected_cash": min_cash,
            "min_cash_week": forecast["min_cash_week"],
            "recommendations": recommendations,
            "as_of_date": as_of_date.isoformat()
        }
