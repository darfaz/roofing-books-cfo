"""
Payment Service using Stripe

Provides payment processing for Friday Payday invoice payments.
Customers can pay invoices directly via payment links in dunning reminders.
"""
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from supabase import create_client, Client as SupabaseClient

logger = logging.getLogger(__name__)

# Stripe is optional - only import if available
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    stripe = None


class PaymentService:
    """Service for processing payments via Stripe."""

    def __init__(self):
        self.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
        self.stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        self.app_url = os.getenv("APP_URL", "http://localhost:5173")

        # Initialize Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        if supabase_url and supabase_key:
            self.supabase: SupabaseClient = create_client(supabase_url, supabase_key)
        else:
            self.supabase = None

        # Configure Stripe if available
        if self.is_configured and STRIPE_AVAILABLE:
            stripe.api_key = self.stripe_secret_key

    @property
    def is_configured(self) -> bool:
        """Check if Stripe is properly configured."""
        return bool(self.stripe_secret_key and STRIPE_AVAILABLE)

    async def create_payment_session(
        self,
        invoice_id: str,
        tenant_id: str,
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout session for an invoice.

        Args:
            invoice_id: The fp_invoices ID
            tenant_id: The tenant ID

        Returns:
            Dict with session URL or error
        """
        if not self.is_configured:
            logger.warning("Stripe not configured - cannot create payment session")
            return {
                "success": False,
                "error": "Payment service not configured",
            }

        if not self.supabase:
            return {
                "success": False,
                "error": "Database connection not configured",
            }

        # Get invoice details
        try:
            invoice_result = self.supabase.table("fp_invoices").select(
                "*, fp_customers(display_name, email)"
            ).eq("id", invoice_id).eq("tenant_id", tenant_id).single().execute()

            if not invoice_result.data:
                return {"success": False, "error": "Invoice not found"}

            invoice = invoice_result.data
            customer = invoice.get("fp_customers", {}) or {}

            if invoice.get("balance", 0) <= 0:
                return {"success": False, "error": "Invoice already paid"}

            # Get tenant info for company name
            tenant_result = self.supabase.table("tenants").select(
                "name"
            ).eq("id", tenant_id).single().execute()

            company_name = tenant_result.data.get("name", "Invoice") if tenant_result.data else "Invoice"

            # Create Stripe Checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Invoice #{invoice.get('invoice_number', 'N/A')}",
                            "description": f"{company_name} - Balance Due",
                        },
                        "unit_amount": int(float(invoice.get("balance", 0)) * 100),  # Convert to cents
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=f"{self.app_url}/pay/success?invoice_id={invoice_id}",
                cancel_url=f"{self.app_url}/pay/cancel?invoice_id={invoice_id}",
                customer_email=customer.get("email"),
                metadata={
                    "invoice_id": invoice_id,
                    "tenant_id": tenant_id,
                    "invoice_number": invoice.get("invoice_number", ""),
                },
            )

            # Store payment session for tracking
            self.supabase.table("fp_payments").insert({
                "tenant_id": tenant_id,
                "invoice_id": invoice_id,
                "amount": float(invoice.get("balance", 0)),
                "payment_method": "stripe",
                "status": "pending",
                "external_id": session.id,
                "metadata": {
                    "stripe_session_id": session.id,
                    "checkout_url": session.url,
                },
                "created_at": datetime.utcnow().isoformat(),
            }).execute()

            logger.info(f"Created Stripe session {session.id} for invoice {invoice_id}")

            return {
                "success": True,
                "checkout_url": session.url,
                "session_id": session.id,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Payment session error: {e}")
            return {"success": False, "error": str(e)}

    async def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """
        Handle Stripe webhook events.

        Args:
            payload: Raw webhook payload
            signature: Stripe signature header

        Returns:
            Dict with handling result
        """
        if not self.is_configured:
            return {"success": False, "error": "Payment service not configured"}

        if not self.stripe_webhook_secret:
            return {"success": False, "error": "Webhook secret not configured"}

        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.stripe_webhook_secret
            )
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            return {"success": False, "error": "Invalid signature"}
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return {"success": False, "error": str(e)}

        # Handle checkout.session.completed
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            return await self._handle_payment_success(session)

        # Handle payment_intent.payment_failed
        elif event["type"] == "payment_intent.payment_failed":
            intent = event["data"]["object"]
            return await self._handle_payment_failed(intent)

        return {"success": True, "message": f"Event {event['type']} acknowledged"}

    async def _handle_payment_success(self, session: Dict) -> Dict[str, Any]:
        """Handle successful checkout session completion."""
        if not self.supabase:
            return {"success": False, "error": "Database not configured"}

        metadata = session.get("metadata", {})
        invoice_id = metadata.get("invoice_id")
        tenant_id = metadata.get("tenant_id")

        if not invoice_id or not tenant_id:
            logger.error(f"Missing metadata in session {session.get('id')}")
            return {"success": False, "error": "Missing invoice metadata"}

        try:
            # Get current invoice balance
            invoice_result = self.supabase.table("fp_invoices").select(
                "balance, amount"
            ).eq("id", invoice_id).single().execute()

            if not invoice_result.data:
                return {"success": False, "error": "Invoice not found"}

            amount_paid = session.get("amount_total", 0) / 100  # Convert from cents
            current_balance = float(invoice_result.data.get("balance", 0))
            new_balance = max(0, current_balance - amount_paid)

            # Update fp_payments record
            self.supabase.table("fp_payments").update({
                "status": "completed",
                "payment_date": datetime.utcnow().date().isoformat(),
                "external_id": session.get("payment_intent"),
                "metadata": {
                    "stripe_session_id": session.get("id"),
                    "stripe_payment_intent": session.get("payment_intent"),
                },
                "updated_at": datetime.utcnow().isoformat(),
            }).eq("external_id", session.get("id")).execute()

            # Update invoice balance
            update_data = {
                "balance": new_balance,
                "updated_at": datetime.utcnow().isoformat(),
            }

            if new_balance <= 0:
                update_data["status"] = "paid"
                update_data["sequence_status"] = "completed"

            self.supabase.table("fp_invoices").update(update_data).eq(
                "id", invoice_id
            ).execute()

            logger.info(
                f"Payment processed: invoice={invoice_id}, amount=${amount_paid:.2f}, "
                f"new_balance=${new_balance:.2f}"
            )

            return {
                "success": True,
                "invoice_id": invoice_id,
                "amount_paid": amount_paid,
                "new_balance": new_balance,
            }

        except Exception as e:
            logger.error(f"Error processing payment success: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_payment_failed(self, intent: Dict) -> Dict[str, Any]:
        """Handle failed payment intent."""
        if not self.supabase:
            return {"success": False, "error": "Database not configured"}

        # Find the payment record
        session_id = intent.get("metadata", {}).get("checkout_session_id")
        if session_id:
            self.supabase.table("fp_payments").update({
                "status": "failed",
                "metadata": {
                    "error": intent.get("last_payment_error", {}).get("message", "Payment failed"),
                },
                "updated_at": datetime.utcnow().isoformat(),
            }).eq("external_id", session_id).execute()

        logger.warning(f"Payment failed: {intent.get('id')}")
        return {"success": True, "message": "Payment failure recorded"}

    async def get_invoice_for_payment(
        self, invoice_id: str, token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get invoice details for the payment portal.

        Args:
            invoice_id: The invoice ID
            token: Optional security token (for future use)

        Returns:
            Dict with invoice details or error
        """
        if not self.supabase:
            return {"success": False, "error": "Database not configured"}

        try:
            result = self.supabase.table("fp_invoices").select(
                "id, invoice_number, amount, balance, due_date, status, "
                "fp_customers(display_name), tenant_id"
            ).eq("id", invoice_id).single().execute()

            if not result.data:
                return {"success": False, "error": "Invoice not found"}

            invoice = result.data

            # Get company name
            tenant_result = self.supabase.table("tenants").select(
                "name"
            ).eq("id", invoice.get("tenant_id")).single().execute()

            customer = invoice.get("fp_customers", {}) or {}

            return {
                "success": True,
                "invoice": {
                    "id": invoice.get("id"),
                    "invoice_number": invoice.get("invoice_number"),
                    "amount": float(invoice.get("amount", 0)),
                    "balance": float(invoice.get("balance", 0)),
                    "due_date": invoice.get("due_date"),
                    "status": invoice.get("status"),
                    "customer_name": customer.get("display_name", "Customer"),
                    "company_name": tenant_result.data.get("name", "Company") if tenant_result.data else "Company",
                    "tenant_id": invoice.get("tenant_id"),
                },
            }

        except Exception as e:
            logger.error(f"Error fetching invoice: {e}")
            return {"success": False, "error": str(e)}


# Global instance
payment_service = PaymentService()
