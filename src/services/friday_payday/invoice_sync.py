"""
Friday Payday - Invoice Sync Service

Syncs invoices directly from QuickBooks Online API
to the fp_invoices table with classification and sequence assignment.
"""
import os
import secrets
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID
import logging

from supabase import Client

from .classification import classify_invoice, get_default_sequence_for_payer_type
from .schemas import PayerType, InvoiceStatus, SequenceStatus
from src.services.qbo.client import QBOClient

logger = logging.getLogger(__name__)


class FridayPaydaySync:
    """
    Service to sync invoices from QBO transactions to Friday Payday tables.
    """

    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def sync_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """
        Sync all invoices for a tenant directly from QuickBooks Online.

        Args:
            tenant_id: Tenant UUID

        Returns:
            Dict with sync statistics
        """
        stats = {
            "customers_synced": 0,
            "customers_created": 0,
            "invoices_synced": 0,
            "invoices_created": 0,
            "invoices_updated": 0,
            "errors": [],
        }

        try:
            # 1. Fetch invoices directly from QuickBooks Online
            # Use a 5-year lookback to capture historical invoices
            qbo_client = QBOClient(tenant_id)
            qbo_invoices = qbo_client.get_invoices(start_date="2018-01-01")

            logger.info(f"Fetched {len(qbo_invoices)} invoices from QuickBooks for tenant {tenant_id}")

            # 2. Group by customer and sync customers first
            customers_by_qbo_id = {}
            for inv in qbo_invoices:
                qbo_customer_id = inv.get("customer_ref")
                if qbo_customer_id and qbo_customer_id not in customers_by_qbo_id:
                    customers_by_qbo_id[qbo_customer_id] = {
                        "qbo_id": qbo_customer_id,
                        "display_name": inv.get("customer_name", "Unknown Customer"),
                        "email": None,  # QBO invoice doesn't include email
                    }

            # Sync customers
            customer_id_map = {}  # QBO ID -> FP customer UUID
            for qbo_id, customer_data in customers_by_qbo_id.items():
                fp_customer_id = await self._sync_customer(tenant_id, customer_data)
                if fp_customer_id:
                    customer_id_map[qbo_id] = fp_customer_id
                    stats["customers_synced"] += 1

            stats["customers_created"] = stats["customers_synced"]  # Simplified for now

            # 3. Sync invoices from QBO
            for inv in qbo_invoices:
                try:
                    qbo_customer_id = inv.get("customer_ref")
                    fp_customer_id = customer_id_map.get(qbo_customer_id)

                    if not fp_customer_id:
                        logger.warning(f"No FP customer found for QBO customer {qbo_customer_id}")
                        continue

                    created = await self._sync_invoice_from_qbo(tenant_id, inv, fp_customer_id)
                    stats["invoices_synced"] += 1
                    if created:
                        stats["invoices_created"] += 1
                    else:
                        stats["invoices_updated"] += 1

                except Exception as e:
                    logger.error(f"Error syncing invoice {inv.get('id')}: {e}")
                    stats["errors"].append(str(e))

            # 4. Update tenant fp_settings with last sync time
            try:
                tenant_result = self.supabase.table("tenants").select("fp_settings").eq(
                    "id", tenant_id
                ).single().execute()

                current_settings = tenant_result.data.get("fp_settings", {}) if tenant_result.data else {}
                current_settings["last_sync_at"] = datetime.utcnow().isoformat()

                self.supabase.table("tenants").update({
                    "fp_settings": current_settings
                }).eq("id", tenant_id).execute()
            except Exception as e:
                logger.warning(f"Could not update fp_settings: {e}")

        except Exception as e:
            logger.error(f"Error syncing tenant {tenant_id}: {e}")
            stats["errors"].append(str(e))

        return stats

    async def _sync_customer(
        self, tenant_id: str, customer_data: Dict
    ) -> Optional[str]:
        """
        Sync or create a customer in fp_customers.
        Returns the fp_customers UUID.
        """
        try:
            # Check if customer exists
            result = self.supabase.table("fp_customers").select("id").eq(
                "tenant_id", tenant_id
            ).eq("qbo_id", customer_data["qbo_id"]).execute()

            if result.data:
                # Update existing
                self.supabase.table("fp_customers").update({
                    "display_name": customer_data["display_name"],
                    "email": customer_data.get("email"),
                    "updated_at": datetime.utcnow().isoformat(),
                }).eq("id", result.data[0]["id"]).execute()
                return result.data[0]["id"]
            else:
                # Create new
                insert_result = self.supabase.table("fp_customers").insert({
                    "tenant_id": tenant_id,
                    "qbo_id": customer_data["qbo_id"],
                    "display_name": customer_data["display_name"],
                    "email": customer_data.get("email"),
                    "phone": customer_data.get("phone"),
                    "customer_type": "homeowner",
                }).execute()

                if insert_result.data:
                    return insert_result.data[0]["id"]

        except Exception as e:
            logger.error(f"Error syncing customer {customer_data.get('qbo_id')}: {e}")

        return None

    async def _sync_invoice(
        self, tenant_id: str, transaction: Dict, customer_id: str
    ) -> bool:
        """
        Sync or create an invoice in fp_invoices.
        Returns True if created, False if updated.
        """
        # raw_data is nested inside metadata
        raw_data = transaction.get("metadata", {}).get("raw_data", {})
        qbo_id = raw_data.get("Id")

        # Parse dates
        invoice_date = self._parse_date(raw_data.get("TxnDate"))
        due_date = self._parse_date(raw_data.get("DueDate")) or invoice_date

        # Calculate balance
        total_amount = Decimal(str(raw_data.get("TotalAmt", 0)))
        balance = Decimal(str(raw_data.get("Balance", total_amount)))

        # Get line items
        line_items = []
        for line in raw_data.get("Line", []):
            if line.get("DetailType") == "SalesItemLineDetail":
                detail = line.get("SalesItemLineDetail", {})
                line_items.append({
                    "description": line.get("Description", ""),
                    "amount": float(line.get("Amount", 0)),
                    "quantity": float(detail.get("Qty", 1)),
                    "item_ref": detail.get("ItemRef", {}).get("name"),
                })

        # Classify the invoice
        memo = raw_data.get("CustomerMemo", {}).get("value", "")
        description = raw_data.get("PrivateNote", "")
        payer_type, confidence = classify_invoice(
            memo=memo,
            description=description,
            line_items=line_items,
            amount=total_amount,
        )

        # Determine status
        status = self._determine_status(balance, total_amount, due_date)

        # Check if invoice exists
        result = self.supabase.table("fp_invoices").select("id, payer_type_override").eq(
            "tenant_id", tenant_id
        ).eq("qbo_id", qbo_id).execute()

        invoice_data = {
            "tenant_id": tenant_id,
            "customer_id": customer_id,
            "transaction_id": transaction.get("id"),
            "qbo_id": qbo_id,
            "invoice_number": raw_data.get("DocNumber"),
            "amount": float(total_amount),
            "balance": float(balance),
            "invoice_date": invoice_date.isoformat() if invoice_date else None,
            "due_date": due_date.isoformat() if due_date else None,
            "status": status.value,
            "description": description or memo,
            "line_items": line_items,
            "qbo_synced_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        if result.data:
            # Update existing, but preserve manual overrides
            existing = result.data[0]
            if not existing.get("payer_type_override"):
                invoice_data["payer_type"] = payer_type.value
                invoice_data["classification_confidence"] = float(confidence)

            self.supabase.table("fp_invoices").update(invoice_data).eq(
                "id", existing["id"]
            ).execute()
            return False
        else:
            # Create new invoice
            invoice_data["payer_type"] = payer_type.value
            invoice_data["classification_confidence"] = float(confidence)
            invoice_data["payment_token"] = self._generate_payment_token()
            invoice_data["payment_token_expires_at"] = (
                datetime.utcnow() + timedelta(days=90)
            ).isoformat()

            # Get default sequence for this payer type
            sequence_id = await self._get_default_sequence(tenant_id, payer_type)
            if sequence_id:
                invoice_data["sequence_id"] = sequence_id
                invoice_data["sequence_status"] = SequenceStatus.ACTIVE.value

            self.supabase.table("fp_invoices").insert(invoice_data).execute()
            return True

    async def _sync_invoice_from_qbo(
        self, tenant_id: str, qbo_invoice: Dict, customer_id: str
    ) -> bool:
        """
        Sync or create an invoice in fp_invoices from QBO invoice data.
        Returns True if created, False if updated.

        QBO invoice format from QBOClient.get_invoices():
        {
            "id": "123",
            "doc_number": "INV-001",
            "txn_date": "2024-01-15",
            "due_date": "2024-02-15",
            "customer_ref": "456",
            "customer_name": "John Smith",
            "total_amt": 1000.00,
            "balance": 500.00,
            "status": "EmailSent"
        }
        """
        qbo_id = qbo_invoice.get("id")

        # Parse dates
        invoice_date = self._parse_date(qbo_invoice.get("txn_date"))
        due_date = self._parse_date(qbo_invoice.get("due_date")) or invoice_date

        # Get amounts directly from QBO
        total_amount = Decimal(str(qbo_invoice.get("total_amt", 0)))
        balance = Decimal(str(qbo_invoice.get("balance", 0)))

        # Classify based on customer name (simplified - no line items from this endpoint)
        customer_name = qbo_invoice.get("customer_name", "")
        payer_type, confidence = classify_invoice(
            memo="",
            description=customer_name,
            line_items=[],
            amount=total_amount,
        )

        # Determine status based on balance
        status = self._determine_status(balance, total_amount, due_date)

        # Check if invoice exists
        result = self.supabase.table("fp_invoices").select("id, payer_type_override").eq(
            "tenant_id", tenant_id
        ).eq("qbo_id", qbo_id).execute()

        invoice_data = {
            "tenant_id": tenant_id,
            "customer_id": customer_id,
            "qbo_id": qbo_id,
            "invoice_number": qbo_invoice.get("doc_number"),
            "amount": float(total_amount),
            "balance": float(balance),
            "invoice_date": invoice_date.isoformat() if invoice_date else None,
            "due_date": due_date.isoformat() if due_date else None,
            "status": status.value,
            "description": customer_name,
            "qbo_synced_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        if result.data:
            # Update existing, but preserve manual overrides
            existing = result.data[0]
            if not existing.get("payer_type_override"):
                invoice_data["payer_type"] = payer_type.value
                invoice_data["classification_confidence"] = float(confidence)

            self.supabase.table("fp_invoices").update(invoice_data).eq(
                "id", existing["id"]
            ).execute()
            return False
        else:
            # Create new invoice
            invoice_data["payer_type"] = payer_type.value
            invoice_data["classification_confidence"] = float(confidence)
            invoice_data["payment_token"] = self._generate_payment_token()
            invoice_data["payment_token_expires_at"] = (
                datetime.utcnow() + timedelta(days=90)
            ).isoformat()

            # Get default sequence for this payer type
            sequence_id = await self._get_default_sequence(tenant_id, payer_type)
            if sequence_id:
                invoice_data["sequence_id"] = sequence_id
                invoice_data["sequence_status"] = SequenceStatus.ACTIVE.value

            self.supabase.table("fp_invoices").insert(invoice_data).execute()
            return True

    async def _get_default_sequence(
        self, tenant_id: str, payer_type: PayerType
    ) -> Optional[str]:
        """Get the default sequence ID for a payer type."""
        result = self.supabase.table("fp_sequences").select("id").eq(
            "tenant_id", tenant_id
        ).eq("payer_type", payer_type.value).eq("is_default", True).limit(1).execute()

        if result.data:
            return result.data[0]["id"]
        return None

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse a date string from QBO format."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None

    def _determine_status(
        self, balance: Decimal, total: Decimal, due_date: Optional[date]
    ) -> InvoiceStatus:
        """Determine invoice status based on balance and due date."""
        if balance <= 0:
            return InvoiceStatus.PAID
        if balance < total:
            return InvoiceStatus.PARTIAL
        if due_date and due_date < date.today():
            return InvoiceStatus.OVERDUE
        return InvoiceStatus.SENT

    def _generate_payment_token(self) -> str:
        """Generate a secure payment token for the payment portal."""
        return secrets.token_urlsafe(24)

    async def get_invoices(
        self,
        tenant_id: str,
        status: Optional[InvoiceStatus] = None,
        payer_type: Optional[PayerType] = None,
        min_days_overdue: Optional[int] = None,
        max_days_overdue: Optional[int] = None,
        page: int = 1,
        per_page: int = 50,
    ) -> Tuple[List[Dict], int]:
        """
        Get invoices with filtering and pagination.
        Returns (invoices, total_count).
        """
        query = self.supabase.table("fp_invoices").select(
            "*, fp_customers(display_name, email)"
        ).eq("tenant_id", tenant_id)

        # Apply filters
        if status:
            query = query.eq("status", status.value)
        if payer_type:
            query = query.eq("payer_type", payer_type.value)

        # Exclude paid/written-off by default when filtering by overdue
        if min_days_overdue is not None or max_days_overdue is not None:
            query = query.gt("balance", 0)

        # Get count first
        count_result = self.supabase.table("fp_invoices").select(
            "id", count="exact"
        ).eq("tenant_id", tenant_id).execute()
        total = count_result.count or 0

        # Apply pagination
        offset = (page - 1) * per_page
        query = query.order("due_date", desc=False).range(offset, offset + per_page - 1)

        result = query.execute()

        # Add computed fields
        invoices = []
        today = date.today()
        for inv in result.data or []:
            due = datetime.strptime(inv["due_date"], "%Y-%m-%d").date() if inv.get("due_date") else today
            inv["days_overdue"] = max(0, (today - due).days)
            inv["customer_name"] = inv.get("fp_customers", {}).get("display_name", "Unknown")
            invoices.append(inv)

        return invoices, total

    async def get_invoice_by_id(self, tenant_id: str, invoice_id: str) -> Optional[Dict]:
        """Get a single invoice by ID."""
        result = self.supabase.table("fp_invoices").select(
            "*, fp_customers(*), fp_reminders(*), fp_payments(*)"
        ).eq("tenant_id", tenant_id).eq("id", invoice_id).single().execute()

        if result.data:
            inv = result.data
            due = datetime.strptime(inv["due_date"], "%Y-%m-%d").date() if inv.get("due_date") else date.today()
            inv["days_overdue"] = max(0, (date.today() - due).days)
            return inv
        return None

    async def update_invoice(
        self, tenant_id: str, invoice_id: str, updates: Dict
    ) -> Optional[Dict]:
        """Update an invoice."""
        # If payer_type is being updated, mark as override
        if "payer_type" in updates:
            updates["payer_type_override"] = True

        updates["updated_at"] = datetime.utcnow().isoformat()

        result = self.supabase.table("fp_invoices").update(updates).eq(
            "tenant_id", tenant_id
        ).eq("id", invoice_id).execute()

        if result.data:
            return result.data[0]
        return None

    async def pause_sequence(
        self, tenant_id: str, invoice_id: str, reason: Optional[str] = None
    ) -> bool:
        """Pause the dunning sequence for an invoice."""
        result = self.supabase.table("fp_invoices").update({
            "sequence_status": SequenceStatus.PAUSED.value,
            "sequence_paused_reason": reason,
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("tenant_id", tenant_id).eq("id", invoice_id).execute()

        return bool(result.data)

    async def resume_sequence(self, tenant_id: str, invoice_id: str) -> bool:
        """Resume the dunning sequence for an invoice."""
        result = self.supabase.table("fp_invoices").update({
            "sequence_status": SequenceStatus.ACTIVE.value,
            "sequence_paused_reason": None,
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("tenant_id", tenant_id).eq("id", invoice_id).execute()

        return bool(result.data)

    async def get_invoice_by_payment_token(self, token: str) -> Optional[Dict]:
        """Get invoice by payment portal token (for public payment page)."""
        result = self.supabase.table("fp_invoices").select(
            "*, fp_customers(display_name, email, phone), tenants(name, fp_settings)"
        ).eq("payment_token", token).single().execute()

        if result.data:
            inv = result.data
            # Check token expiration
            expires = inv.get("payment_token_expires_at")
            if expires:
                exp_date = datetime.fromisoformat(expires.replace("Z", "+00:00"))
                if exp_date < datetime.now(exp_date.tzinfo):
                    return None  # Token expired
            return inv
        return None
