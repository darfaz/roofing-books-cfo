"""
Friday Payday - Dunning Engine

Handles automated reminder scheduling and sending based on dunning sequences.
Processes invoices that are overdue and need collection action.
"""
import os
import logging
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
from supabase import create_client, Client as SupabaseClient
from .schemas import (
    PayerType, InvoiceStatus, SequenceStatus,
    ReminderChannel, ReminderStatus
)
from ..email_service import email_service

logger = logging.getLogger(__name__)


class DunningEngine:
    """Processes invoices and sends reminders according to dunning sequences."""

    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY are required")
        self.supabase: SupabaseClient = create_client(supabase_url, supabase_key)

    async def process_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """
        Process all overdue invoices for a tenant.
        Returns summary of actions taken.
        """
        summary = {
            "tenant_id": tenant_id,
            "processed_at": datetime.utcnow().isoformat(),
            "invoices_processed": 0,
            "reminders_scheduled": 0,
            "reminders_sent": 0,
            "sequences_started": 0,
            "sequences_advanced": 0,
            "errors": []
        }

        try:
            # Get all invoices that need attention
            invoices = await self._get_actionable_invoices(tenant_id)
            summary["invoices_processed"] = len(invoices)

            # Get sequences for this tenant
            sequences = await self._get_sequences(tenant_id)
            sequence_map = {s["payer_type"]: s for s in sequences}

            for invoice in invoices:
                try:
                    result = await self._process_invoice(invoice, sequence_map)
                    summary["reminders_scheduled"] += result.get("scheduled", 0)
                    summary["reminders_sent"] += result.get("sent", 0)
                    if result.get("sequence_started"):
                        summary["sequences_started"] += 1
                    if result.get("sequence_advanced"):
                        summary["sequences_advanced"] += 1
                except Exception as e:
                    summary["errors"].append({
                        "invoice_id": invoice["id"],
                        "error": str(e)
                    })

            # Send scheduled reminders that are due
            sent_count = await self._send_pending_reminders(tenant_id)
            summary["reminders_sent"] += sent_count

        except Exception as e:
            summary["errors"].append({"error": str(e)})

        return summary

    async def _get_actionable_invoices(self, tenant_id: str) -> List[Dict]:
        """Get invoices that need dunning attention."""
        result = self.supabase.table("fp_invoices").select(
            "*, fp_customers(id, display_name, email, phone, mobile, is_suppressed)"
        ).eq(
            "tenant_id", tenant_id
        ).gt(
            "balance", 0
        ).in_(
            "sequence_status", [
                SequenceStatus.NOT_STARTED.value,
                SequenceStatus.ACTIVE.value
            ]
        ).neq(
            "status", InvoiceStatus.PAID.value
        ).order("due_date").execute()

        return result.data or []

    async def _get_sequences(self, tenant_id: str) -> List[Dict]:
        """Get all dunning sequences for a tenant with their steps."""
        result = self.supabase.table("fp_sequences").select(
            "*, fp_sequence_steps(*)"
        ).eq(
            "tenant_id", tenant_id
        ).eq(
            "is_active", True
        ).execute()

        return result.data or []

    async def _process_invoice(
        self, invoice: Dict, sequence_map: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """Process a single invoice for dunning actions."""
        result = {"scheduled": 0, "sent": 0, "sequence_started": False, "sequence_advanced": False}

        # Check if customer is suppressed
        customer = invoice.get("fp_customers", {})
        if customer and customer.get("is_suppressed"):
            return result  # Skip suppressed customers

        # Check if customer has contact info
        email = customer.get("email") if customer else None
        phone = customer.get("phone") or customer.get("mobile") if customer else None
        if not email and not phone:
            return result  # No way to contact

        payer_type = invoice.get("payer_type", PayerType.HOMEOWNER_DIRECT.value)
        sequence = sequence_map.get(payer_type)

        if not sequence:
            # Try to get default sequence
            sequence = next(
                (s for s in sequence_map.values() if s.get("is_default")),
                None
            )

        if not sequence:
            return result  # No applicable sequence

        # Calculate days overdue
        due_date = datetime.strptime(invoice["due_date"], "%Y-%m-%d").date()
        today = date.today()
        days_overdue = (today - due_date).days

        # Get sequence steps
        steps = sorted(
            sequence.get("fp_sequence_steps", []),
            key=lambda x: x.get("step_order", 0)
        )

        current_step = invoice.get("sequence_current_step", 0)

        # Start sequence if not started
        if invoice.get("sequence_status") == SequenceStatus.NOT_STARTED.value:
            if days_overdue >= 0:  # Invoice is due or overdue
                await self._start_sequence(invoice, sequence, steps)
                result["sequence_started"] = True
                current_step = 0

        # Check if we need to advance to next step
        if invoice.get("sequence_status") == SequenceStatus.ACTIVE.value:
            for i, step in enumerate(steps):
                if i < current_step:
                    continue  # Already past this step

                step_due_days = step.get("days_from_due", 0)
                if days_overdue >= step_due_days:
                    # Check if we've already sent this step
                    existing = await self._get_reminder_for_step(
                        invoice["id"], step["id"]
                    )
                    if not existing:
                        # Schedule this reminder
                        await self._schedule_reminder(invoice, step, customer)
                        result["scheduled"] += 1
                        result["sequence_advanced"] = True

                        # Update current step
                        await self._update_invoice_step(
                            invoice["id"], invoice["tenant_id"], i + 1
                        )

        return result

    async def _start_sequence(
        self, invoice: Dict, sequence: Dict, steps: List[Dict]
    ) -> None:
        """Start the dunning sequence for an invoice."""
        self.supabase.table("fp_invoices").update({
            "sequence_id": sequence["id"],
            "sequence_status": SequenceStatus.ACTIVE.value,
            "sequence_current_step": 0,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", invoice["id"]).execute()

    async def _get_reminder_for_step(
        self, invoice_id: str, step_id: str
    ) -> Optional[Dict]:
        """Check if a reminder already exists for this step."""
        result = self.supabase.table("fp_reminders").select("id").eq(
            "invoice_id", invoice_id
        ).eq(
            "sequence_step_id", step_id
        ).limit(1).execute()

        return result.data[0] if result.data else None

    async def _schedule_reminder(
        self, invoice: Dict, step: Dict, customer: Dict
    ) -> str:
        """Create a scheduled reminder."""
        channel = step.get("channel", ReminderChannel.EMAIL.value)

        # Determine if we can send via this channel
        has_email = bool(customer.get("email"))
        has_phone = bool(customer.get("phone") or customer.get("mobile"))

        if channel == ReminderChannel.EMAIL.value and not has_email:
            if has_phone:
                channel = ReminderChannel.SMS.value
            else:
                return None  # Can't send

        if channel == ReminderChannel.SMS.value and not has_phone:
            if has_email:
                channel = ReminderChannel.EMAIL.value
            else:
                return None  # Can't send

        # Calculate send time (respect quiet hours would go here)
        send_at = datetime.utcnow() + timedelta(minutes=5)  # Small delay

        reminder = {
            "tenant_id": invoice["tenant_id"],
            "invoice_id": invoice["id"],
            "customer_id": invoice["customer_id"],
            "sequence_step_id": step.get("id"),
            "channel": channel,
            "status": ReminderStatus.SCHEDULED.value,
            "scheduled_for": send_at.isoformat(),
            "template_id": step.get("template_id"),
            "step_number": step.get("step_order", 0),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        result = self.supabase.table("fp_reminders").insert(reminder).execute()
        return result.data[0]["id"] if result.data else None

    async def _update_invoice_step(
        self, invoice_id: str, tenant_id: str, step: int
    ) -> None:
        """Update the current step for an invoice."""
        self.supabase.table("fp_invoices").update({
            "sequence_current_step": step,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", invoice_id).eq("tenant_id", tenant_id).execute()

    async def _send_pending_reminders(self, tenant_id: str) -> int:
        """Send all reminders that are due."""
        now = datetime.utcnow().isoformat()

        # Get pending reminders
        result = self.supabase.table("fp_reminders").select(
            "*, fp_invoices(*, fp_customers(display_name, email, phone, mobile))"
        ).eq(
            "tenant_id", tenant_id
        ).eq(
            "status", ReminderStatus.SCHEDULED.value
        ).lte(
            "scheduled_for", now
        ).execute()

        reminders = result.data or []
        sent_count = 0

        for reminder in reminders:
            try:
                success = await self._send_reminder(reminder)
                if success:
                    sent_count += 1
            except Exception as e:
                # Log error but continue with other reminders
                await self._mark_reminder_failed(reminder["id"], str(e))

        return sent_count

    async def _send_reminder(self, reminder: Dict) -> bool:
        """Send a single reminder via the appropriate channel."""
        channel = reminder.get("channel")
        invoice = reminder.get("fp_invoices", {})
        customer = invoice.get("fp_customers", {}) if invoice else {}

        # Get template content
        template_id = reminder.get("template_id")
        template = None
        if template_id:
            template_result = self.supabase.table("fp_templates").select(
                "*"
            ).eq("id", template_id).single().execute()
            template = template_result.data if template_result.data else None

        # Generate message content
        subject, body = self._generate_message(
            template, invoice, customer, reminder
        )

        # Actually send the message
        success = False
        external_id = None

        if channel == ReminderChannel.EMAIL.value:
            email = customer.get("email")
            if email:
                # Send via Resend
                tenant_id = invoice.get("tenant_id", "")
                invoice_id = invoice.get("id", "")
                reminder_id = reminder.get("id", "")

                # Wrap body in HTML if needed
                html_body = body
                if not body.strip().startswith("<"):
                    html_body = f"<div style='font-family: sans-serif; line-height: 1.6;'>{body.replace(chr(10), '<br>')}</div>"

                result = await email_service.send_dunning_reminder(
                    to=email,
                    subject=subject,
                    html=html_body,
                    invoice_id=invoice_id,
                    reminder_id=reminder_id,
                    tenant_id=tenant_id,
                )

                if result.get("success"):
                    success = True
                    external_id = result.get("message_id", f"email-{datetime.utcnow().timestamp()}")
                else:
                    logger.error(f"Email send failed: {result.get('error')}")
                    # If Resend not configured, simulate success for testing
                    if result.get("simulated"):
                        success = True
                        external_id = f"simulated-{datetime.utcnow().timestamp()}"

        elif channel == ReminderChannel.SMS.value:
            phone = customer.get("phone") or customer.get("mobile")
            if phone:
                # TODO: Integrate with Twilio or other SMS provider
                # For now, simulate success
                logger.info(f"SMS would be sent to {phone}: {body[:100]}...")
                success = True
                external_id = f"sms-simulated-{datetime.utcnow().timestamp()}"

        if success:
            await self._mark_reminder_sent(
                reminder["id"], subject, body, external_id
            )

        return success

    def _generate_message(
        self,
        template: Optional[Dict],
        invoice: Dict,
        customer: Dict,
        reminder: Dict
    ) -> tuple:
        """Generate personalized message content."""
        if template:
            subject = template.get("subject", "Payment Reminder")
            body = template.get("body", "")
        else:
            # Default message
            subject = f"Payment Reminder - Invoice #{invoice.get('invoice_number', 'N/A')}"
            body = self._get_default_message(reminder.get("channel"))

        # Personalize the message
        customer_name = customer.get("display_name", "Valued Customer")
        invoice_number = invoice.get("invoice_number", "N/A")
        balance = invoice.get("balance", 0)
        due_date = invoice.get("due_date", "N/A")

        # Simple template replacement
        replacements = {
            "{{customer_name}}": customer_name,
            "{{invoice_number}}": invoice_number,
            "{{balance}}": f"${balance:,.2f}" if isinstance(balance, (int, float)) else str(balance),
            "{{due_date}}": due_date,
        }

        for key, value in replacements.items():
            subject = subject.replace(key, value)
            body = body.replace(key, value)

        return subject, body

    def _get_default_message(self, channel: str) -> str:
        """Get default message template based on channel."""
        if channel == ReminderChannel.SMS.value:
            return (
                "Hi {{customer_name}}, this is a friendly reminder that "
                "invoice #{{invoice_number}} for {{balance}} was due {{due_date}}. "
                "Please let us know if you have any questions!"
            )
        else:
            return (
                "Dear {{customer_name}},\n\n"
                "This is a friendly reminder that invoice #{{invoice_number}} "
                "for {{balance}} was due on {{due_date}}.\n\n"
                "If you've already sent payment, please disregard this notice.\n\n"
                "If you have any questions about this invoice, please don't "
                "hesitate to reach out.\n\n"
                "Thank you for your business!"
            )

    async def _mark_reminder_sent(
        self, reminder_id: str, subject: str, body: str, external_id: Optional[str]
    ) -> None:
        """Mark a reminder as sent."""
        self.supabase.table("fp_reminders").update({
            "status": ReminderStatus.SENT.value,
            "sent_at": datetime.utcnow().isoformat(),
            "subject": subject,
            "personalized_body": body,
            "external_id": external_id,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", reminder_id).execute()

    async def _mark_reminder_failed(self, reminder_id: str, error: str) -> None:
        """Mark a reminder as failed."""
        # Get current retry count
        result = self.supabase.table("fp_reminders").select(
            "retry_count"
        ).eq("id", reminder_id).single().execute()
        retry_count = result.data.get("retry_count", 0) if result.data else 0

        self.supabase.table("fp_reminders").update({
            "status": ReminderStatus.FAILED.value,
            "error_message": error,
            "retry_count": retry_count + 1,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", reminder_id).execute()

    async def record_email_open(self, reminder_id: str) -> bool:
        """Record when an email is opened (from tracking pixel)."""
        result = self.supabase.table("fp_reminders").update({
            "opened_at": datetime.utcnow().isoformat(),
            "delivery_status": "opened",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", reminder_id).execute()
        return bool(result.data)

    async def record_link_click(self, reminder_id: str) -> bool:
        """Record when a link in reminder is clicked."""
        result = self.supabase.table("fp_reminders").update({
            "clicked_at": datetime.utcnow().isoformat(),
            "delivery_status": "clicked",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", reminder_id).execute()
        return bool(result.data)


# Global instance
dunning_engine = DunningEngine()
