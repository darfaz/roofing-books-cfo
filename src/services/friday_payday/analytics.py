"""
Friday Payday - Analytics Service

Provides AR aging, DSO calculations, and collection metrics.
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from uuid import UUID
import logging

from supabase import Client

from .schemas import (
    ARAgingBucket,
    ARAgingSummary,
    CollectionMetrics,
    DSOTrend,
    FridayPaydaySummary,
)

logger = logging.getLogger(__name__)

# Roofing industry DSO benchmark
INDUSTRY_DSO_BENCHMARK = Decimal("83")


class FridayPaydayAnalytics:
    """Analytics service for Friday Payday metrics."""

    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def get_ar_aging(self, tenant_id: str) -> ARAgingSummary:
        """
        Calculate AR aging summary for a tenant.

        Returns aging buckets: Current, 1-30, 31-60, 61-90, 90+
        """
        today = date.today()

        # Get all unpaid invoices
        result = self.supabase.table("fp_invoices").select(
            "id, balance, due_date"
        ).eq("tenant_id", tenant_id).gt("balance", 0).not_.in_(
            "status", ["paid", "written_off"]
        ).execute()

        invoices = result.data or []

        # Initialize buckets
        buckets = {
            "current": {"amount": Decimal("0"), "count": 0},
            "1-30": {"amount": Decimal("0"), "count": 0},
            "31-60": {"amount": Decimal("0"), "count": 0},
            "61-90": {"amount": Decimal("0"), "count": 0},
            "90+": {"amount": Decimal("0"), "count": 0},
        }

        for inv in invoices:
            balance = Decimal(str(inv.get("balance", 0)))
            due_date = datetime.strptime(inv["due_date"], "%Y-%m-%d").date()
            days_overdue = (today - due_date).days

            if days_overdue <= 0:
                bucket = "current"
            elif days_overdue <= 30:
                bucket = "1-30"
            elif days_overdue <= 60:
                bucket = "31-60"
            elif days_overdue <= 90:
                bucket = "61-90"
            else:
                bucket = "90+"

            buckets[bucket]["amount"] += balance
            buckets[bucket]["count"] += 1

        # Calculate total
        total_ar = sum(b["amount"] for b in buckets.values())
        total_invoices = sum(b["count"] for b in buckets.values())

        # Build response
        bucket_list = []
        for bucket_name, data in buckets.items():
            pct = (data["amount"] / total_ar * 100) if total_ar > 0 else Decimal("0")
            bucket_list.append(ARAgingBucket(
                bucket=bucket_name,
                amount=data["amount"],
                count=data["count"],
                percentage=round(pct, 2),
            ))

        # Calculate DSO
        dso = await self.calculate_dso(tenant_id)

        return ARAgingSummary(
            tenant_id=UUID(tenant_id),
            as_of_date=today,
            buckets=bucket_list,
            total_ar=total_ar,
            total_invoices=total_invoices,
            dso=dso,
        )

    async def calculate_dso(
        self, tenant_id: str, days_back: int = 90
    ) -> Optional[Decimal]:
        """
        Calculate Days Sales Outstanding (DSO).

        Formula: (Average AR / Total Credit Sales) * Days in Period

        For simplicity, we'll use:
        Average days between invoice date and payment date for paid invoices
        """
        cutoff = (date.today() - timedelta(days=days_back)).isoformat()

        # Get paid invoices with payment dates
        result = self.supabase.table("fp_invoices").select(
            "invoice_date, updated_at"
        ).eq("tenant_id", tenant_id).eq("status", "paid").gte(
            "invoice_date", cutoff
        ).execute()

        paid_invoices = result.data or []

        if not paid_invoices:
            # Fallback: calculate from current AR and average sales
            return await self._calculate_dso_from_ar(tenant_id)

        # Calculate average days to payment
        total_days = 0
        count = 0

        for inv in paid_invoices:
            invoice_date = datetime.strptime(inv["invoice_date"], "%Y-%m-%d").date()
            # Use updated_at as proxy for payment date
            payment_date = datetime.fromisoformat(
                inv["updated_at"].replace("Z", "+00:00")
            ).date()
            days = (payment_date - invoice_date).days
            if days >= 0:
                total_days += days
                count += 1

        if count == 0:
            return None

        return Decimal(str(round(total_days / count, 1)))

    async def _calculate_dso_from_ar(self, tenant_id: str) -> Optional[Decimal]:
        """
        Calculate DSO using AR balance and average daily sales.
        DSO = (AR Balance / Average Daily Sales)
        """
        # Get total AR
        ar_result = self.supabase.table("fp_invoices").select("balance").eq(
            "tenant_id", tenant_id
        ).gt("balance", 0).not_.in_("status", ["paid", "written_off"]).execute()

        total_ar = sum(Decimal(str(inv.get("balance", 0))) for inv in (ar_result.data or []))

        # Get total sales from last 90 days
        cutoff = (date.today() - timedelta(days=90)).isoformat()
        sales_result = self.supabase.table("fp_invoices").select("amount").eq(
            "tenant_id", tenant_id
        ).gte("invoice_date", cutoff).execute()

        total_sales = sum(Decimal(str(inv.get("amount", 0))) for inv in (sales_result.data or []))

        if total_sales <= 0:
            return None

        avg_daily_sales = total_sales / 90
        dso = total_ar / avg_daily_sales

        return Decimal(str(round(float(dso), 1)))

    async def get_collection_metrics(
        self, tenant_id: str, period_days: int = 7
    ) -> CollectionMetrics:
        """Get collection performance metrics for a period."""
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)

        # Get payments in period
        payments_result = self.supabase.table("fp_payments").select(
            "amount, invoice_id"
        ).eq("tenant_id", tenant_id).gte(
            "payment_date", start_date.isoformat()
        ).lte("payment_date", end_date.isoformat()).execute()

        payments = payments_result.data or []
        amount_collected = sum(Decimal(str(p.get("amount", 0))) for p in payments)
        invoices_paid = len(set(p.get("invoice_id") for p in payments))

        # Get reminder stats
        reminders_result = self.supabase.table("fp_reminders").select(
            "status, opened_at, clicked_at"
        ).eq("tenant_id", tenant_id).gte(
            "sent_at", start_date.isoformat()
        ).execute()

        reminders = reminders_result.data or []
        reminders_sent = len(reminders)
        reminders_opened = sum(1 for r in reminders if r.get("opened_at"))
        reminders_clicked = sum(1 for r in reminders if r.get("clicked_at"))

        return CollectionMetrics(
            period_start=start_date,
            period_end=end_date,
            amount_collected=amount_collected,
            invoices_paid=invoices_paid,
            reminders_sent=reminders_sent,
            reminders_opened=reminders_opened,
            reminders_clicked=reminders_clicked,
            average_days_to_collect=None,  # TODO: Calculate
        )

    async def get_dso_trend(
        self, tenant_id: str, days: int = 90
    ) -> List[DSOTrend]:
        """Get DSO trend over time from daily metrics."""
        cutoff = (date.today() - timedelta(days=days)).isoformat()

        result = self.supabase.table("fp_daily_metrics").select(
            "metric_date, dso"
        ).eq("tenant_id", tenant_id).gte(
            "metric_date", cutoff
        ).order("metric_date").execute()

        trends = []
        for row in result.data or []:
            if row.get("dso") is not None:
                trends.append(DSOTrend(
                    date=datetime.strptime(row["metric_date"], "%Y-%m-%d").date(),
                    dso=Decimal(str(row["dso"])),
                    industry_benchmark=INDUSTRY_DSO_BENCHMARK,
                ))

        return trends

    async def get_friday_summary(self, tenant_id: str) -> FridayPaydaySummary:
        """
        Generate the Friday Payday weekly summary.
        This is sent out every Friday with collection metrics.
        """
        today = date.today()
        week_end = today
        week_start = today - timedelta(days=7)
        prev_week_end = week_start
        prev_week_start = prev_week_end - timedelta(days=7)

        # This week's metrics
        this_week = await self.get_collection_metrics(tenant_id, period_days=7)

        # Last week's metrics for comparison
        prev_payments = self.supabase.table("fp_payments").select(
            "amount"
        ).eq("tenant_id", tenant_id).gte(
            "payment_date", prev_week_start.isoformat()
        ).lt("payment_date", prev_week_end.isoformat()).execute()

        prev_amount = sum(
            Decimal(str(p.get("amount", 0))) for p in (prev_payments.data or [])
        )

        # Calculate week-over-week change
        vs_last_week_amount = this_week.amount_collected - prev_amount
        if prev_amount > 0:
            vs_last_week_pct = (vs_last_week_amount / prev_amount) * 100
        else:
            vs_last_week_pct = Decimal("100") if this_week.amount_collected > 0 else Decimal("0")

        # Get top payments this week
        top_payments_result = self.supabase.table("fp_payments").select(
            "amount, fp_invoices(invoice_number, job_name, job_address), fp_customers(display_name)"
        ).eq("tenant_id", tenant_id).gte(
            "payment_date", week_start.isoformat()
        ).order("amount", desc=True).limit(5).execute()

        top_payments = []
        for p in top_payments_result.data or []:
            inv = p.get("fp_invoices", {})
            cust = p.get("fp_customers", {})
            top_payments.append({
                "amount": float(p.get("amount", 0)),
                "customer_name": cust.get("display_name", "Unknown"),
                "job_name": inv.get("job_name") or inv.get("job_address") or inv.get("invoice_number"),
            })

        # Get outstanding balance
        ar_summary = await self.get_ar_aging(tenant_id)

        # Get current DSO
        dso = await self.calculate_dso(tenant_id) or INDUSTRY_DSO_BENCHMARK

        return FridayPaydaySummary(
            tenant_id=UUID(tenant_id),
            week_start=week_start,
            week_end=week_end,
            amount_collected=this_week.amount_collected,
            invoices_paid=this_week.invoices_paid,
            vs_last_week_amount=vs_last_week_amount,
            vs_last_week_pct=round(vs_last_week_pct, 1),
            top_payments=top_payments,
            outstanding_balance=ar_summary.total_ar,
            outstanding_invoices=ar_summary.total_invoices,
            current_dso=dso,
        )

    async def record_daily_metrics(self, tenant_id: str) -> Dict[str, Any]:
        """
        Record daily metrics snapshot for a tenant.
        Should be called by a daily cron job.
        """
        today = date.today()

        # Get AR aging
        aging = await self.get_ar_aging(tenant_id)

        # Get today's collections
        payments_result = self.supabase.table("fp_payments").select(
            "amount, invoice_id"
        ).eq("tenant_id", tenant_id).eq(
            "payment_date", today.isoformat()
        ).execute()

        amount_collected = sum(
            Decimal(str(p.get("amount", 0))) for p in (payments_result.data or [])
        )
        invoices_paid = len(set(p.get("invoice_id") for p in (payments_result.data or [])))

        # Get today's reminders
        reminders_result = self.supabase.table("fp_reminders").select(
            "status, opened_at, clicked_at"
        ).eq("tenant_id", tenant_id).gte(
            "sent_at", today.isoformat()
        ).execute()

        reminders = reminders_result.data or []

        # Build metrics record
        metrics = {
            "tenant_id": tenant_id,
            "metric_date": today.isoformat(),
            "bucket_current": float(aging.buckets[0].amount) if aging.buckets else 0,
            "bucket_1_30": float(aging.buckets[1].amount) if len(aging.buckets) > 1 else 0,
            "bucket_31_60": float(aging.buckets[2].amount) if len(aging.buckets) > 2 else 0,
            "bucket_61_90": float(aging.buckets[3].amount) if len(aging.buckets) > 3 else 0,
            "bucket_90_plus": float(aging.buckets[4].amount) if len(aging.buckets) > 4 else 0,
            "total_ar": float(aging.total_ar),
            "invoices_current": aging.buckets[0].count if aging.buckets else 0,
            "invoices_1_30": aging.buckets[1].count if len(aging.buckets) > 1 else 0,
            "invoices_31_60": aging.buckets[2].count if len(aging.buckets) > 2 else 0,
            "invoices_61_90": aging.buckets[3].count if len(aging.buckets) > 3 else 0,
            "invoices_90_plus": aging.buckets[4].count if len(aging.buckets) > 4 else 0,
            "total_invoices": aging.total_invoices,
            "amount_collected": float(amount_collected),
            "invoices_paid": invoices_paid,
            "reminders_sent": len(reminders),
            "reminders_opened": sum(1 for r in reminders if r.get("opened_at")),
            "reminders_clicked": sum(1 for r in reminders if r.get("clicked_at")),
            "dso": float(aging.dso) if aging.dso else None,
        }

        # Upsert metrics
        self.supabase.table("fp_daily_metrics").upsert(
            metrics, on_conflict="tenant_id,metric_date"
        ).execute()

        return metrics

    async def get_invoices_due_for_action(
        self, tenant_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get invoices that need a reminder action today.
        Used by the daily dunning workflow.
        """
        now = datetime.utcnow()

        # Get active sequences with next action due
        result = self.supabase.table("fp_invoices").select(
            "*, fp_customers(display_name, email, phone, is_suppressed, communication_preferences), "
            "fp_sequences(name, fp_sequence_steps(*))"
        ).eq("tenant_id", tenant_id).eq(
            "sequence_status", "active"
        ).lte("sequence_next_action_at", now.isoformat()).gt("balance", 0).execute()

        invoices = []
        for inv in result.data or []:
            customer = inv.get("fp_customers", {})

            # Skip suppressed customers
            if customer.get("is_suppressed"):
                continue

            # Add computed fields
            due_date = datetime.strptime(inv["due_date"], "%Y-%m-%d").date()
            inv["days_overdue"] = max(0, (date.today() - due_date).days)
            inv["customer_name"] = customer.get("display_name", "Unknown")
            inv["customer_email"] = customer.get("email")
            inv["customer_phone"] = customer.get("phone")

            invoices.append(inv)

        return invoices
