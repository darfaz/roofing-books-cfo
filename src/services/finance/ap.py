"""
Accounts Payable (AP) Service
Manages bills, AP aging, and vendor payment scheduling
"""
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


class APService:
    """Accounts Payable management service"""

    # AP Aging buckets (days)
    AGING_BUCKETS = {
        "current": (0, 0),      # Not yet due
        "1-30": (1, 30),        # 1-30 days past due
        "31-60": (31, 60),      # 31-60 days past due
        "61-90": (61, 90),      # 61-90 days past due
        "90+": (91, 9999)       # 90+ days past due
    }

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.supabase = create_client(
            os.getenv("SUPABASE_URL", ""),
            os.getenv("SUPABASE_SERVICE_KEY", "")
        )

    def get_unpaid_bills(self, as_of_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Get all unpaid bills for the tenant

        Args:
            as_of_date: Date to calculate aging from (defaults to today)

        Returns:
            List of unpaid bills with due dates and amounts
        """
        if not as_of_date:
            as_of_date = date.today()

        # Query transactions for bills that are pending (not paid/voided)
        result = self.supabase.table("transactions")\
            .select("id, transaction_date, total_amount, memo, reference_number, vendor_id, status, metadata, qbo_id")\
            .eq("tenant_id", self.tenant_id)\
            .in_("transaction_type", ["bill", "expense"])\
            .eq("status", "pending")\
            .neq("status", "voided")\
            .order("transaction_date")\
            .execute()

        bills = []
        for txn in (result.data or []):
            # Get due date from metadata or calculate from transaction date
            metadata = txn.get("metadata", {}) or {}

            # Try to get due_date from metadata (QBO stores it there)
            due_date_str = metadata.get("due_date")
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    # Default to 30 days from transaction date
                    txn_date = datetime.strptime(txn["transaction_date"], "%Y-%m-%d").date()
                    due_date = txn_date + timedelta(days=30)
            else:
                # Default to 30 days from transaction date
                txn_date = datetime.strptime(txn["transaction_date"], "%Y-%m-%d").date()
                due_date = txn_date + timedelta(days=30)

            # Calculate days past due (negative means not yet due)
            days_past_due = (as_of_date - due_date).days

            # Get vendor name if available
            vendor_name = None
            if txn.get("vendor_id"):
                vendor_result = self.supabase.table("vendors")\
                    .select("name")\
                    .eq("id", txn["vendor_id"])\
                    .limit(1)\
                    .execute()
                if vendor_result.data:
                    vendor_name = vendor_result.data[0]["name"]

            bills.append({
                "id": txn["id"],
                "qbo_id": txn.get("qbo_id"),
                "transaction_date": txn["transaction_date"],
                "due_date": due_date.isoformat(),
                "amount": abs(float(txn["total_amount"])),
                "vendor_id": txn.get("vendor_id"),
                "vendor_name": vendor_name,
                "memo": txn.get("memo"),
                "reference_number": txn.get("reference_number"),
                "days_past_due": days_past_due,
                "is_overdue": days_past_due > 0
            })

        return bills

    def calculate_ap_aging(self, as_of_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Calculate AP aging buckets

        Args:
            as_of_date: Date to calculate aging from (defaults to today)

        Returns:
            Dict with aging buckets and totals
        """
        if not as_of_date:
            as_of_date = date.today()

        bills = self.get_unpaid_bills(as_of_date)

        # Initialize buckets
        aging = {
            "current": 0.0,
            "1-30": 0.0,
            "31-60": 0.0,
            "61-90": 0.0,
            "90+": 0.0
        }

        bills_by_bucket = {
            "current": [],
            "1-30": [],
            "31-60": [],
            "61-90": [],
            "90+": []
        }

        for bill in bills:
            days = bill["days_past_due"]
            amount = bill["amount"]

            if days <= 0:
                aging["current"] += amount
                bills_by_bucket["current"].append(bill)
            elif days <= 30:
                aging["1-30"] += amount
                bills_by_bucket["1-30"].append(bill)
            elif days <= 60:
                aging["31-60"] += amount
                bills_by_bucket["31-60"].append(bill)
            elif days <= 90:
                aging["61-90"] += amount
                bills_by_bucket["61-90"].append(bill)
            else:
                aging["90+"] += amount
                bills_by_bucket["90+"].append(bill)

        total = sum(aging.values())
        overdue = aging["1-30"] + aging["31-60"] + aging["61-90"] + aging["90+"]

        return {
            "aging": aging,
            "total": total,
            "overdue": overdue,
            "overdue_pct": (overdue / total * 100) if total > 0 else 0,
            "as_of_date": as_of_date.isoformat(),
            "bill_count": len(bills),
            "bills_by_bucket": bills_by_bucket
        }

    def get_upcoming_payments(
        self,
        days_ahead: int = 30,
        as_of_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get bills due in the next N days for cash planning

        Args:
            days_ahead: Number of days to look ahead
            as_of_date: Start date (defaults to today)

        Returns:
            List of upcoming payments sorted by due date
        """
        if not as_of_date:
            as_of_date = date.today()

        end_date = as_of_date + timedelta(days=days_ahead)
        bills = self.get_unpaid_bills(as_of_date)

        upcoming = []
        for bill in bills:
            due_date = datetime.strptime(bill["due_date"], "%Y-%m-%d").date()
            if as_of_date <= due_date <= end_date:
                upcoming.append(bill)

        # Sort by due date
        upcoming.sort(key=lambda x: x["due_date"])

        return upcoming

    def get_payment_schedule_by_week(
        self,
        weeks: int = 13,
        as_of_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get weekly payment schedule for cash flow forecasting

        Args:
            weeks: Number of weeks to project
            as_of_date: Start date (defaults to today)

        Returns:
            List of weekly payment totals with due bills
        """
        if not as_of_date:
            as_of_date = date.today()

        bills = self.get_unpaid_bills(as_of_date)

        schedule = []
        for week_num in range(weeks):
            week_start = as_of_date + timedelta(weeks=week_num)
            week_end = week_start + timedelta(days=6)

            # Find bills due this week
            week_bills = []
            week_total = 0.0

            for bill in bills:
                due_date = datetime.strptime(bill["due_date"], "%Y-%m-%d").date()
                if week_start <= due_date <= week_end:
                    week_bills.append(bill)
                    week_total += bill["amount"]

            schedule.append({
                "week_number": week_num + 1,
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "total_due": week_total,
                "bill_count": len(week_bills),
                "bills": week_bills
            })

        return schedule

    def get_vendor_summary(self, as_of_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Get AP summary by vendor

        Args:
            as_of_date: Date to calculate aging from

        Returns:
            List of vendors with their AP totals and aging
        """
        if not as_of_date:
            as_of_date = date.today()

        bills = self.get_unpaid_bills(as_of_date)

        # Group by vendor
        vendor_totals = {}
        for bill in bills:
            vendor_id = bill.get("vendor_id") or "unknown"
            vendor_name = bill.get("vendor_name") or "Unknown Vendor"

            if vendor_id not in vendor_totals:
                vendor_totals[vendor_id] = {
                    "vendor_id": vendor_id,
                    "vendor_name": vendor_name,
                    "total": 0.0,
                    "current": 0.0,
                    "overdue": 0.0,
                    "bill_count": 0,
                    "oldest_due": None
                }

            vendor_totals[vendor_id]["total"] += bill["amount"]
            vendor_totals[vendor_id]["bill_count"] += 1

            if bill["days_past_due"] <= 0:
                vendor_totals[vendor_id]["current"] += bill["amount"]
            else:
                vendor_totals[vendor_id]["overdue"] += bill["amount"]

            # Track oldest due date
            if vendor_totals[vendor_id]["oldest_due"] is None:
                vendor_totals[vendor_id]["oldest_due"] = bill["due_date"]
            elif bill["due_date"] < vendor_totals[vendor_id]["oldest_due"]:
                vendor_totals[vendor_id]["oldest_due"] = bill["due_date"]

        # Convert to list and sort by total descending
        result = list(vendor_totals.values())
        result.sort(key=lambda x: x["total"], reverse=True)

        return result

    def get_ap_metrics(self, as_of_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get key AP metrics for dashboard

        Args:
            as_of_date: Date for calculations

        Returns:
            Dict with key AP metrics
        """
        if not as_of_date:
            as_of_date = date.today()

        aging = self.calculate_ap_aging(as_of_date)
        vendors = self.get_vendor_summary(as_of_date)

        # Get average days to pay (from paid bills in last 90 days)
        paid_start = (as_of_date - timedelta(days=90)).isoformat()
        paid_bills = self.supabase.table("transactions")\
            .select("transaction_date, metadata")\
            .eq("tenant_id", self.tenant_id)\
            .in_("transaction_type", ["bill", "expense"])\
            .eq("status", "posted")\
            .gte("transaction_date", paid_start)\
            .execute()

        # Calculate average days to pay (simplified - using transaction date as proxy)
        avg_days_to_pay = 30  # Default
        if paid_bills.data:
            # This is simplified - ideally we'd track when bills were actually paid
            avg_days_to_pay = 25  # Placeholder

        return {
            "total_ap": aging["total"],
            "current": aging["aging"]["current"],
            "overdue": aging["overdue"],
            "overdue_pct": aging["overdue_pct"],
            "bill_count": aging["bill_count"],
            "vendor_count": len(vendors),
            "avg_days_to_pay": avg_days_to_pay,
            "top_vendor": vendors[0] if vendors else None,
            "as_of_date": as_of_date.isoformat()
        }
