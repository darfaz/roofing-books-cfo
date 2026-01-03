"""
SMS Service using Twilio

Provides a unified interface for sending SMS across the application.
Used by Friday Payday for dunning reminders.
"""
import os
import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import base64

logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending SMS via Twilio API."""

    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_FROM_NUMBER")
        self.base_url = "https://api.twilio.com/2010-04-01"

    @property
    def is_configured(self) -> bool:
        """Check if Twilio is properly configured."""
        return bool(self.account_sid and self.auth_token and self.from_number)

    def _get_auth_header(self) -> str:
        """Generate Basic Auth header for Twilio."""
        credentials = f"{self.account_sid}:{self.auth_token}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    async def send_sms(
        self,
        to: str,
        body: str,
        from_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send an SMS via Twilio.

        Args:
            to: Recipient phone number (E.164 format preferred)
            body: Message content (max 1600 characters)
            from_number: Override sender number (default: configured from_number)

        Returns:
            Dict with send result including message SID
        """
        if not self.is_configured:
            logger.warning("Twilio not configured - SMS not sent")
            return {
                "success": False,
                "error": "SMS service not configured",
                "simulated": True,
            }

        # Normalize phone number (basic cleanup)
        normalized_to = self._normalize_phone(to)
        if not normalized_to:
            return {
                "success": False,
                "error": "Invalid phone number",
            }

        # Truncate body if needed (Twilio limit is 1600 chars)
        if len(body) > 1600:
            body = body[:1597] + "..."

        payload = {
            "To": normalized_to,
            "From": from_number or self.from_number,
            "Body": body,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/Accounts/{self.account_sid}/Messages.json",
                    headers={
                        "Authorization": self._get_auth_header(),
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    data=payload,
                    timeout=30.0,
                )

                data = response.json()

                if response.status_code in (200, 201):
                    logger.info(f"SMS sent successfully: {data.get('sid')}")
                    return {
                        "success": True,
                        "message_sid": data.get("sid"),
                        "to": normalized_to,
                        "status": data.get("status"),
                    }
                else:
                    error_msg = data.get("message", "Unknown error")
                    logger.error(f"Twilio API error: {data}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "code": data.get("code"),
                        "status_code": response.status_code,
                    }

        except httpx.TimeoutException:
            logger.error("Twilio API timeout")
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            logger.error(f"SMS send error: {e}")
            return {"success": False, "error": str(e)}

    def _normalize_phone(self, phone: str) -> Optional[str]:
        """
        Normalize phone number to E.164 format.
        Basic implementation - assumes US numbers if no country code.
        """
        if not phone:
            return None

        # Remove common formatting characters
        cleaned = "".join(c for c in phone if c.isdigit() or c == "+")

        if not cleaned:
            return None

        # If starts with +, assume it's already E.164
        if cleaned.startswith("+"):
            return cleaned

        # If 10 digits, assume US and add +1
        if len(cleaned) == 10:
            return f"+1{cleaned}"

        # If 11 digits starting with 1, assume US
        if len(cleaned) == 11 and cleaned.startswith("1"):
            return f"+{cleaned}"

        # Otherwise return as-is with + prefix
        return f"+{cleaned}" if not cleaned.startswith("+") else cleaned

    async def send_dunning_reminder(
        self,
        to: str,
        body: str,
        invoice_id: str,
        reminder_id: str,
        tenant_id: str,
    ) -> Dict[str, Any]:
        """
        Send a dunning reminder SMS.

        Args:
            to: Recipient phone number
            body: Message content
            invoice_id: Invoice ID for tracking
            reminder_id: Reminder ID for tracking
            tenant_id: Tenant ID for tracking

        Returns:
            Send result
        """
        # Add tracking info to logs
        logger.info(
            f"Sending dunning SMS: tenant={tenant_id}, invoice={invoice_id}, "
            f"reminder={reminder_id}, to={to[:4]}***"
        )

        result = await self.send_sms(to=to, body=body)

        if result.get("success"):
            logger.info(
                f"Dunning SMS sent: sid={result.get('message_sid')}, "
                f"invoice={invoice_id}"
            )
        else:
            logger.error(
                f"Dunning SMS failed: invoice={invoice_id}, "
                f"error={result.get('error')}"
            )

        return result

    async def get_message_status(self, message_sid: str) -> Dict[str, Any]:
        """
        Get the status of a sent message.

        Args:
            message_sid: Twilio message SID

        Returns:
            Message status info
        """
        if not self.is_configured:
            return {"success": False, "error": "SMS service not configured"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/Accounts/{self.account_sid}/Messages/{message_sid}.json",
                    headers={"Authorization": self._get_auth_header()},
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "status": data.get("status"),
                        "error_code": data.get("error_code"),
                        "error_message": data.get("error_message"),
                        "date_sent": data.get("date_sent"),
                        "date_updated": data.get("date_updated"),
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to fetch message status",
                        "status_code": response.status_code,
                    }

        except Exception as e:
            logger.error(f"Error fetching message status: {e}")
            return {"success": False, "error": str(e)}


# Global instance
sms_service = SMSService()
