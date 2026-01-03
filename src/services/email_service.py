"""
Email Service using Resend

Provides a unified interface for sending emails across the application.
Used by Friday Payday for dunning reminders and weekly summaries.
"""
import os
import httpx
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via Resend API."""

    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY")
        self.from_email = os.getenv("RESEND_FROM_EMAIL", "Friday Payday <noreply@crewcfo.com>")
        self.base_url = "https://api.resend.com"

    @property
    def is_configured(self) -> bool:
        """Check if Resend is properly configured."""
        return bool(self.api_key)

    async def send_email(
        self,
        to: str | List[str],
        subject: str,
        html: str,
        text: Optional[str] = None,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
        tags: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Send an email via Resend.

        Args:
            to: Recipient email(s)
            subject: Email subject
            html: HTML body content
            text: Optional plain text body
            from_email: Override sender (default: configured from_email)
            reply_to: Reply-to address
            tags: List of tags for tracking (e.g., [{"name": "category", "value": "dunning"}])

        Returns:
            Dict with send result including message ID
        """
        if not self.is_configured:
            logger.warning("Resend not configured - email not sent")
            return {
                "success": False,
                "error": "Email service not configured",
                "simulated": True,
            }

        # Normalize recipients
        recipients = [to] if isinstance(to, str) else to

        payload = {
            "from": from_email or self.from_email,
            "to": recipients,
            "subject": subject,
            "html": html,
        }

        if text:
            payload["text"] = text
        if reply_to:
            payload["reply_to"] = reply_to
        if tags:
            payload["tags"] = tags

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/emails",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Email sent successfully: {data.get('id')}")
                    return {
                        "success": True,
                        "message_id": data.get("id"),
                        "to": recipients,
                    }
                else:
                    error_data = response.json()
                    logger.error(f"Resend API error: {error_data}")
                    return {
                        "success": False,
                        "error": error_data.get("message", "Unknown error"),
                        "status_code": response.status_code,
                    }

        except httpx.TimeoutException:
            logger.error("Resend API timeout")
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            logger.error(f"Email send error: {e}")
            return {"success": False, "error": str(e)}

    async def send_dunning_reminder(
        self,
        to: str,
        subject: str,
        html: str,
        invoice_id: str,
        reminder_id: str,
        tenant_id: str,
    ) -> Dict[str, Any]:
        """
        Send a dunning reminder email with tracking tags.

        Args:
            to: Recipient email
            subject: Email subject
            html: HTML body
            invoice_id: Invoice ID for tracking
            reminder_id: Reminder ID for tracking
            tenant_id: Tenant ID for tracking

        Returns:
            Send result
        """
        return await self.send_email(
            to=to,
            subject=subject,
            html=html,
            tags=[
                {"name": "type", "value": "dunning"},
                {"name": "tenant_id", "value": tenant_id},
                {"name": "invoice_id", "value": invoice_id},
                {"name": "reminder_id", "value": reminder_id},
            ],
        )

    async def send_friday_summary(
        self,
        to: str,
        html: str,
        tenant_id: str,
        company_name: str,
    ) -> Dict[str, Any]:
        """
        Send the Friday Payday weekly summary email.

        Args:
            to: Recipient email
            html: HTML body
            tenant_id: Tenant ID
            company_name: Company name for subject

        Returns:
            Send result
        """
        week_date = datetime.now().strftime("%b %d")
        return await self.send_email(
            to=to,
            subject=f"🎉 Friday Payday Summary - {company_name} - Week of {week_date}",
            html=html,
            tags=[
                {"name": "type", "value": "friday_summary"},
                {"name": "tenant_id", "value": tenant_id},
            ],
        )

    async def send_batch(
        self,
        emails: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Send multiple emails (Resend batch endpoint).

        Args:
            emails: List of email payloads

        Returns:
            Batch send result
        """
        if not self.is_configured:
            return {
                "success": False,
                "error": "Email service not configured",
                "simulated": True,
            }

        # Add from address to each email if not present
        for email in emails:
            if "from" not in email:
                email["from"] = self.from_email

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/emails/batch",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=emails,
                    timeout=60.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Batch email sent: {len(data.get('data', []))} emails")
                    return {
                        "success": True,
                        "results": data.get("data", []),
                        "count": len(data.get("data", [])),
                    }
                else:
                    error_data = response.json()
                    logger.error(f"Resend batch error: {error_data}")
                    return {
                        "success": False,
                        "error": error_data.get("message", "Unknown error"),
                    }

        except Exception as e:
            logger.error(f"Batch email error: {e}")
            return {"success": False, "error": str(e)}


# Global instance
email_service = EmailService()
