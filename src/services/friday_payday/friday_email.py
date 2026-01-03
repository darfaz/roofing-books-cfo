"""
Friday Payday - Weekly Summary Email

Generates and sends the Friday Payday summary email to business owners.
Includes collection highlights, AR status, and week-over-week comparison.
"""
import os
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from supabase import create_client, Client as SupabaseClient
from .schemas import FridayPaydaySummary
from ..email_service import email_service

logger = logging.getLogger(__name__)


class FridayEmailService:
    """Generates and sends Friday summary emails."""

    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY are required")
        self.supabase: SupabaseClient = create_client(supabase_url, supabase_key)

    async def generate_summary(self, tenant_id: str) -> FridayPaydaySummary:
        """Generate the Friday Payday summary for a tenant."""
        today = date.today()

        # Calculate this week's date range (Mon-Sun, ending today or last Sunday)
        days_since_sunday = (today.weekday() + 1) % 7
        week_end = today - timedelta(days=days_since_sunday) if days_since_sunday > 0 else today
        week_start = week_end - timedelta(days=6)

        # Calculate last week's date range
        last_week_end = week_start - timedelta(days=1)
        last_week_start = last_week_end - timedelta(days=6)

        # Get this week's collections
        this_week = await self._get_week_collections(
            tenant_id, week_start, week_end
        )

        # Get last week's collections for comparison
        last_week = await self._get_week_collections(
            tenant_id, last_week_start, last_week_end
        )

        # Get current outstanding balance
        outstanding = await self._get_outstanding(tenant_id)

        # Get current DSO
        dso = await self._calculate_dso(tenant_id)

        # Calculate week-over-week comparison
        this_amount = this_week.get("amount", Decimal("0"))
        last_amount = last_week.get("amount", Decimal("0"))

        if last_amount > 0:
            vs_last_week_pct = ((this_amount - last_amount) / last_amount) * 100
        else:
            vs_last_week_pct = Decimal("100") if this_amount > 0 else Decimal("0")

        return FridayPaydaySummary(
            tenant_id=tenant_id,
            week_start=week_start,
            week_end=week_end,
            amount_collected=this_amount,
            invoices_paid=this_week.get("count", 0),
            vs_last_week_amount=this_amount - last_amount,
            vs_last_week_pct=vs_last_week_pct,
            top_payments=this_week.get("top_payments", []),
            outstanding_balance=outstanding.get("balance", Decimal("0")),
            outstanding_invoices=outstanding.get("count", 0),
            current_dso=dso or Decimal("0")
        )

    async def _get_week_collections(
        self, tenant_id: str, start: date, end: date
    ) -> Dict[str, Any]:
        """Get collection stats for a week."""
        result = self.supabase.table("fp_payments").select(
            "amount, fp_invoices(invoice_number, fp_customers(display_name))"
        ).eq(
            "tenant_id", tenant_id
        ).gte(
            "payment_date", start.isoformat()
        ).lte(
            "payment_date", end.isoformat()
        ).order("amount", desc=True).execute()

        payments = result.data or []

        total_amount = sum(Decimal(str(p.get("amount", 0))) for p in payments)
        count = len(payments)

        # Get top 5 payments
        top_payments = []
        for p in payments[:5]:
            invoice = p.get("fp_invoices", {}) or {}
            customer = invoice.get("fp_customers", {}) or {}
            top_payments.append({
                "amount": float(p.get("amount", 0)),
                "invoice_number": invoice.get("invoice_number", "N/A"),
                "customer_name": customer.get("display_name", "Unknown")
            })

        return {
            "amount": total_amount,
            "count": count,
            "top_payments": top_payments
        }

    async def _get_outstanding(self, tenant_id: str) -> Dict[str, Any]:
        """Get current outstanding AR."""
        result = self.supabase.table("fp_invoices").select(
            "balance"
        ).eq(
            "tenant_id", tenant_id
        ).gt(
            "balance", 0
        ).execute()

        invoices = result.data or []
        total_balance = sum(Decimal(str(i.get("balance", 0))) for i in invoices)

        return {
            "balance": total_balance,
            "count": len(invoices)
        }

    async def _calculate_dso(self, tenant_id: str) -> Optional[Decimal]:
        """Calculate Days Sales Outstanding."""
        # Get last 90 days of data
        end_date = date.today()
        start_date = end_date - timedelta(days=90)

        # Get total revenue in period
        revenue_result = self.supabase.table("fp_invoices").select(
            "amount"
        ).eq(
            "tenant_id", tenant_id
        ).gte(
            "invoice_date", start_date.isoformat()
        ).lte(
            "invoice_date", end_date.isoformat()
        ).execute()

        revenues = revenue_result.data or []
        total_revenue = sum(Decimal(str(r.get("amount", 0))) for r in revenues)

        if total_revenue <= 0:
            return None

        # Get current AR
        ar_result = await self._get_outstanding(tenant_id)
        current_ar = ar_result.get("balance", Decimal("0"))

        # DSO = (AR / Revenue) * Days in period
        dso = (current_ar / total_revenue) * 90
        return dso.quantize(Decimal("1"))

    def generate_email_html(self, summary: FridayPaydaySummary, company: Dict) -> str:
        """Generate the HTML email content."""
        company_name = company.get("name", "Your Company")
        brand_color = company.get("brand_color", "#1E40AF")

        # Format currency
        def fmt_currency(amount):
            return f"${float(amount):,.2f}"

        # Determine emoji based on performance
        if summary.vs_last_week_pct > 0:
            emoji = "🎉"
            trend_color = "#10B981"
            trend_text = f"+{summary.vs_last_week_pct:.1f}% vs last week"
        elif summary.vs_last_week_pct < 0:
            emoji = "📉"
            trend_color = "#EF4444"
            trend_text = f"{summary.vs_last_week_pct:.1f}% vs last week"
        else:
            emoji = "📊"
            trend_color = "#6B7280"
            trend_text = "Same as last week"

        # Build top payments section
        top_payments_html = ""
        for p in summary.top_payments[:3]:
            top_payments_html += f"""
            <tr>
                <td style="padding: 8px 0; border-bottom: 1px solid #E5E7EB;">
                    {p['customer_name']}<br>
                    <span style="color: #6B7280; font-size: 12px;">Invoice #{p['invoice_number']}</span>
                </td>
                <td style="padding: 8px 0; text-align: right; border-bottom: 1px solid #E5E7EB; font-weight: 600;">
                    {fmt_currency(p['amount'])}
                </td>
            </tr>
            """

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Friday Payday Summary</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #F3F4F6;">
    <table width="100%" cellpadding="0" cellspacing="0" style="padding: 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #FFFFFF; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background-color: {brand_color}; padding: 30px; text-align: center;">
                            <h1 style="color: #FFFFFF; margin: 0; font-size: 28px;">{emoji} Friday Payday!</h1>
                            <p style="color: rgba(255,255,255,0.8); margin: 10px 0 0 0; font-size: 14px;">
                                {company_name} • Week of {summary.week_start.strftime('%b %d')} - {summary.week_end.strftime('%b %d, %Y')}
                            </p>
                        </td>
                    </tr>

                    <!-- Main Stats -->
                    <tr>
                        <td style="padding: 30px;">
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="text-align: center; padding: 20px;">
                                        <div style="font-size: 42px; font-weight: 700; color: #111827;">
                                            {fmt_currency(summary.amount_collected)}
                                        </div>
                                        <div style="font-size: 14px; color: #6B7280; margin-top: 5px;">
                                            Collected This Week
                                        </div>
                                        <div style="font-size: 14px; color: {trend_color}; margin-top: 8px; font-weight: 600;">
                                            {trend_text}
                                        </div>
                                    </td>
                                </tr>
                            </table>

                            <!-- Stats Grid -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 20px; background-color: #F9FAFB; border-radius: 8px;">
                                <tr>
                                    <td style="padding: 20px; text-align: center; border-right: 1px solid #E5E7EB;">
                                        <div style="font-size: 24px; font-weight: 700; color: #111827;">
                                            {summary.invoices_paid}
                                        </div>
                                        <div style="font-size: 12px; color: #6B7280; margin-top: 3px;">
                                            Invoices Paid
                                        </div>
                                    </td>
                                    <td style="padding: 20px; text-align: center; border-right: 1px solid #E5E7EB;">
                                        <div style="font-size: 24px; font-weight: 700; color: #111827;">
                                            {fmt_currency(summary.outstanding_balance)}
                                        </div>
                                        <div style="font-size: 12px; color: #6B7280; margin-top: 3px;">
                                            Outstanding
                                        </div>
                                    </td>
                                    <td style="padding: 20px; text-align: center;">
                                        <div style="font-size: 24px; font-weight: 700; color: #111827;">
                                            {int(summary.current_dso)}
                                        </div>
                                        <div style="font-size: 12px; color: #6B7280; margin-top: 3px;">
                                            DSO (Days)
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Top Payments -->
                    {'<tr><td style="padding: 0 30px 30px 30px;"><h3 style="margin: 0 0 15px 0; font-size: 16px; color: #111827;">Top Payments This Week</h3><table width="100%" cellpadding="0" cellspacing="0">' + top_payments_html + '</table></td></tr>' if summary.top_payments else ''}

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 20px 30px; background-color: #F9FAFB; text-align: center; border-top: 1px solid #E5E7EB;">
                            <p style="margin: 0; font-size: 12px; color: #6B7280;">
                                Powered by <a href="https://crewcfo.com" style="color: {brand_color}; text-decoration: none;">Friday Payday</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """

        return html

    async def send_summary(self, tenant_id: str) -> bool:
        """Generate and send the Friday summary email to the business owner."""
        # Get tenant info
        tenant_result = self.supabase.table("tenants").select(
            "name, fp_settings"
        ).eq("id", tenant_id).single().execute()

        if not tenant_result.data:
            return False

        tenant = tenant_result.data
        fp_settings = tenant.get("fp_settings", {}) or {}

        # Generate summary
        summary = await self.generate_summary(tenant_id)

        # Generate email HTML
        html = self.generate_email_html(summary, {
            "name": tenant.get("name", "Your Company"),
            "brand_color": fp_settings.get("brand_color", "#1E40AF")
        })

        # Get the owner's email (from tenant users)
        users_result = self.supabase.table("tenant_users").select(
            "email"
        ).eq("tenant_id", tenant_id).eq("role", "owner").execute()

        if not users_result.data:
            return False

        owner_email = users_result.data[0].get("email")
        if not owner_email:
            return False

        # Send via Resend
        company_name = tenant.get("name", "Your Company")
        result = await email_service.send_friday_summary(
            to=owner_email,
            html=html,
            tenant_id=tenant_id,
            company_name=company_name,
        )

        if not result.get("success"):
            logger.error(f"Failed to send Friday summary to {owner_email}: {result.get('error')}")
            if not result.get("simulated"):
                return False
        else:
            logger.info(f"Friday summary sent to {owner_email}")

        # Store the summary for analytics
        self.supabase.table("fp_weekly_summaries").insert({
            "tenant_id": tenant_id,
            "week_start": summary.week_start.isoformat(),
            "week_end": summary.week_end.isoformat(),
            "amount_collected": float(summary.amount_collected),
            "invoices_paid": summary.invoices_paid,
            "vs_last_week_pct": float(summary.vs_last_week_pct),
            "outstanding_balance": float(summary.outstanding_balance),
            "current_dso": float(summary.current_dso),
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        return True

    async def send_all_summaries(self) -> Dict[str, Any]:
        """Send Friday summaries to all enabled tenants."""
        # Get all tenants with Friday Payday enabled
        result = self.supabase.table("tenants").select(
            "id, name"
        ).execute()

        tenants = result.data or []
        results = {
            "sent": 0,
            "failed": 0,
            "skipped": 0
        }

        for tenant in tenants:
            try:
                # Check if tenant has Friday Payday enabled
                fp_settings_result = self.supabase.table("tenants").select(
                    "fp_settings"
                ).eq("id", tenant["id"]).single().execute()

                fp_settings = fp_settings_result.data.get("fp_settings", {}) or {}
                if not fp_settings.get("enabled", False):
                    results["skipped"] += 1
                    continue

                success = await self.send_summary(tenant["id"])
                if success:
                    results["sent"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                print(f"Error sending summary to {tenant['id']}: {e}")
                results["failed"] += 1

        return results


# Global instance
friday_email = FridayEmailService()
