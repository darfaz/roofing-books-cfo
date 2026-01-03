"""
Friday Payday - Template Service

Manages email and SMS templates for collection reminders.
Provides default templates and allows customization.
"""
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4
from supabase import create_client, Client as SupabaseClient
from .schemas import ReminderChannel


# Default templates for each payer type and step
DEFAULT_TEMPLATES = {
    "homeowner_direct": [
        {
            "step": 1,
            "days_from_due": 0,
            "channel": "email",
            "tone": "friendly",
            "subject": "Payment Reminder: Invoice #{{invoice_number}}",
            "body": """Hi {{customer_name}},

Just a friendly reminder that your invoice #{{invoice_number}} for {{balance}} is now due.

You can pay online using the secure link below:
{{payment_link}}

If you've already sent payment, please disregard this notice.

Questions? Just reply to this email.

Thank you for your business!
{{company_name}}"""
        },
        {
            "step": 2,
            "days_from_due": 7,
            "channel": "email",
            "tone": "professional",
            "subject": "Second Notice: Invoice #{{invoice_number}} Past Due",
            "body": """Dear {{customer_name}},

This is a reminder that invoice #{{invoice_number}} for {{balance}} was due on {{due_date}}.

To avoid any late fees or service holds, please remit payment at your earliest convenience.

Pay now: {{payment_link}}

If you're experiencing difficulties or have questions about this invoice, please reach out so we can work together on a solution.

Best regards,
{{company_name}}"""
        },
        {
            "step": 3,
            "days_from_due": 14,
            "channel": "sms",
            "tone": "professional",
            "body": "Hi {{customer_name}}, this is {{company_name}}. Invoice #{{invoice_number}} for {{balance}} is 14 days past due. Please pay at {{payment_link}} or call us to discuss. Thanks!"
        },
        {
            "step": 4,
            "days_from_due": 21,
            "channel": "email",
            "tone": "firm",
            "subject": "Urgent: Invoice #{{invoice_number}} - Action Required",
            "body": """{{customer_name}},

Invoice #{{invoice_number}} for {{balance}} is now 21 days past due.

This is our final notice before we may need to escalate this matter.

Please pay immediately: {{payment_link}}

If there's an issue with this invoice, we need to hear from you within 3 business days.

{{company_name}}"""
        },
    ],
    "insurance_pending": [
        {
            "step": 1,
            "days_from_due": 7,
            "channel": "email",
            "tone": "professional",
            "subject": "Insurance Claim Status Check - Invoice #{{invoice_number}}",
            "body": """Hi {{customer_name}},

We wanted to check in on the status of your insurance claim for the work completed at {{job_address}}.

Invoice #{{invoice_number}}: {{balance}}
Claim Number: {{claim_number}}

Have you received your check from the insurance company? If so, we'd appreciate prompt payment so we can close out this project.

If you're still waiting on the insurance company, please let us know and we can follow up with the adjuster if needed.

{{company_name}}"""
        },
        {
            "step": 2,
            "days_from_due": 21,
            "channel": "sms",
            "tone": "friendly",
            "body": "Hi {{customer_name}}, checking on your insurance claim status for invoice #{{invoice_number}}. Has the check arrived? Let us know if you need help with the adjuster. - {{company_name}}"
        },
        {
            "step": 3,
            "days_from_due": 45,
            "channel": "email",
            "tone": "professional",
            "subject": "Insurance Payment Follow-Up - Invoice #{{invoice_number}}",
            "body": """{{customer_name}},

It's been several weeks since we completed your roofing project. We understand insurance claims can take time, but we need to follow up on invoice #{{invoice_number}} for {{balance}}.

If you've received your insurance check, please remit payment as soon as possible.

If you're having issues with your claim, we're here to help. We can:
- Provide additional documentation
- Call the adjuster on your behalf
- Discuss payment arrangements

Please contact us to discuss. We want to help resolve this.

{{company_name}}"""
        },
    ],
    "supplement_pending": [
        {
            "step": 1,
            "days_from_due": 14,
            "channel": "email",
            "tone": "professional",
            "subject": "Supplement Status Update - Invoice #{{invoice_number}}",
            "body": """Hi {{customer_name}},

We're following up on the supplement we submitted for your project at {{job_address}}.

Original invoice: #{{invoice_number}}
Supplement amount: {{balance}}

We've submitted the additional documentation to your insurance company and are awaiting their response.

Is there anything you need from us in the meantime?

{{company_name}}"""
        },
    ],
    "gc_commercial": [
        {
            "step": 1,
            "days_from_due": 3,
            "channel": "email",
            "tone": "professional",
            "subject": "Invoice #{{invoice_number}} - Payment Due",
            "body": """Hello,

This is a reminder that invoice #{{invoice_number}} for {{balance}} is now due per our contract terms.

Project: {{job_address}}
Amount Due: {{balance}}
Due Date: {{due_date}}

Please process payment at your earliest convenience to maintain your preferred vendor status.

Remit to: {{payment_link}}

If there are any discrepancies or questions, please contact us immediately.

Best regards,
{{company_name}}"""
        },
        {
            "step": 2,
            "days_from_due": 10,
            "channel": "email",
            "tone": "professional",
            "subject": "Second Notice: Invoice #{{invoice_number}}",
            "body": """Hello,

Invoice #{{invoice_number}} for {{balance}} remains outstanding and is now past due.

Per our agreement, we may need to hold future work orders until this account is current.

Please expedite payment or contact us to discuss.

{{company_name}}"""
        },
    ],
}


class TemplateService:
    """Manages email and SMS templates."""

    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY are required")
        self.supabase: SupabaseClient = create_client(supabase_url, supabase_key)

    async def get_templates(
        self, tenant_id: str, channel: Optional[str] = None
    ) -> List[Dict]:
        """Get all templates for a tenant."""
        query = self.supabase.table("fp_templates").select("*").eq(
            "tenant_id", tenant_id
        ).eq("is_active", True)

        if channel:
            query = query.eq("channel", channel)

        result = query.order("name").execute()
        return result.data or []

    async def get_template(self, tenant_id: str, template_id: str) -> Optional[Dict]:
        """Get a specific template."""
        result = self.supabase.table("fp_templates").select("*").eq(
            "tenant_id", tenant_id
        ).eq("id", template_id).single().execute()
        return result.data if result.data else None

    async def create_template(self, tenant_id: str, template: Dict) -> Dict:
        """Create a new template."""
        template_data = {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "name": template.get("name"),
            "channel": template.get("channel", ReminderChannel.EMAIL.value),
            "tone": template.get("tone", "friendly"),
            "subject": template.get("subject"),
            "body": template.get("body"),
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        result = self.supabase.table("fp_templates").insert(template_data).execute()
        return result.data[0] if result.data else template_data

    async def update_template(
        self, tenant_id: str, template_id: str, updates: Dict
    ) -> Optional[Dict]:
        """Update a template."""
        # Don't allow updating system templates
        existing = await self.get_template(tenant_id, template_id)
        if existing and existing.get("is_system"):
            raise ValueError("System templates cannot be modified")

        updates["updated_at"] = datetime.utcnow().isoformat()

        result = self.supabase.table("fp_templates").update(updates).eq(
            "tenant_id", tenant_id
        ).eq("id", template_id).execute()

        return result.data[0] if result.data else None

    async def delete_template(self, tenant_id: str, template_id: str) -> bool:
        """Delete a template (soft delete)."""
        # Don't allow deleting system templates
        existing = await self.get_template(tenant_id, template_id)
        if existing and existing.get("is_system"):
            raise ValueError("System templates cannot be deleted")

        result = self.supabase.table("fp_templates").update({
            "is_active": False,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("tenant_id", tenant_id).eq("id", template_id).execute()

        return bool(result.data)

    async def seed_default_templates(self, tenant_id: str) -> int:
        """Seed default templates for a new tenant."""
        count = 0

        for payer_type, templates in DEFAULT_TEMPLATES.items():
            for template in templates:
                template_data = {
                    "id": str(uuid4()),
                    "tenant_id": tenant_id,
                    "name": f"{payer_type.replace('_', ' ').title()} - Step {template['step']}",
                    "channel": template.get("channel", "email"),
                    "tone": template.get("tone", "friendly"),
                    "subject": template.get("subject"),
                    "body": template.get("body"),
                    "payer_type": payer_type,
                    "step_number": template["step"],
                    "days_from_due": template["days_from_due"],
                    "is_active": True,
                    "is_system": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }

                try:
                    self.supabase.table("fp_templates").insert(template_data).execute()
                    count += 1
                except Exception:
                    pass  # Template might already exist

        return count

    def render_template(
        self, template: Dict, invoice: Dict, customer: Dict, company: Dict
    ) -> tuple:
        """Render a template with variable substitution."""
        subject = template.get("subject", "")
        body = template.get("body", "")

        # Build replacement map
        replacements = {
            # Invoice fields
            "{{invoice_number}}": str(invoice.get("invoice_number", "N/A")),
            "{{balance}}": self._format_currency(invoice.get("balance", 0)),
            "{{amount}}": self._format_currency(invoice.get("amount", 0)),
            "{{due_date}}": self._format_date(invoice.get("due_date")),
            "{{invoice_date}}": self._format_date(invoice.get("invoice_date")),
            "{{job_address}}": invoice.get("job_address") or "your property",
            "{{job_name}}": invoice.get("job_name") or "",
            "{{claim_number}}": invoice.get("insurance_claim_number") or "N/A",

            # Customer fields
            "{{customer_name}}": customer.get("display_name", "Valued Customer"),
            "{{customer_email}}": customer.get("email", ""),
            "{{customer_phone}}": customer.get("phone", ""),

            # Company fields
            "{{company_name}}": company.get("name", "Our Company"),
            "{{company_phone}}": company.get("phone", ""),
            "{{company_email}}": company.get("email", ""),

            # Payment link
            "{{payment_link}}": invoice.get("payment_link") or "",
        }

        for key, value in replacements.items():
            subject = subject.replace(key, str(value))
            body = body.replace(key, str(value))

        return subject, body

    def _format_currency(self, amount: Any) -> str:
        """Format amount as currency."""
        try:
            return f"${float(amount):,.2f}"
        except (ValueError, TypeError):
            return str(amount)

    def _format_date(self, date_str: Any) -> str:
        """Format date string."""
        if not date_str:
            return "N/A"
        try:
            if isinstance(date_str, str):
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                dt = date_str
            return dt.strftime("%B %d, %Y")
        except Exception:
            return str(date_str)


# Global instance
template_service = TemplateService()
