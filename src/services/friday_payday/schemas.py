"""
Friday Payday - Pydantic Schemas
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


# ============================================================================
# ENUMS
# ============================================================================

class PayerType(str, Enum):
    """Invoice payer classification"""
    HOMEOWNER_DIRECT = "homeowner_direct"
    INSURANCE_PENDING = "insurance_pending"
    SUPPLEMENT_PENDING = "supplement_pending"
    DEPRECIATION_RECOVERY = "depreciation_recovery"
    GC_COMMERCIAL = "gc_commercial"
    RETAINAGE = "retainage"


class InvoiceStatus(str, Enum):
    """Invoice payment status"""
    DRAFT = "draft"
    SENT = "sent"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    DISPUTED = "disputed"
    WRITTEN_OFF = "written_off"


class SequenceStatus(str, Enum):
    """Dunning sequence status for an invoice"""
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    MANUAL = "manual"


class ReminderChannel(str, Enum):
    """Communication channel"""
    EMAIL = "email"
    SMS = "sms"
    CALL = "call"


class ReminderStatus(str, Enum):
    """Reminder send status"""
    SCHEDULED = "scheduled"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    SKIPPED = "skipped"


class PaymentMethod(str, Enum):
    """Payment method type"""
    CARD = "card"
    ACH = "ach"
    CHECK = "check"
    CASH = "cash"
    OTHER = "other"


class PaymentSource(str, Enum):
    """Payment source"""
    QUICKBOOKS = "quickbooks"
    PAYMENT_PORTAL = "payment_portal"
    MANUAL = "manual"


# ============================================================================
# CUSTOMER MODELS
# ============================================================================

class FPCustomerBase(BaseModel):
    """Base customer fields"""
    display_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    customer_type: str = "homeowner"
    billing_address: Optional[Dict[str, Any]] = None
    tags: List[str] = []
    notes: Optional[str] = None


class FPCustomerCreate(FPCustomerBase):
    """Create customer request"""
    qbo_id: Optional[str] = None


class FPCustomer(FPCustomerBase):
    """Full customer model"""
    id: UUID
    tenant_id: UUID
    qbo_id: Optional[str] = None
    total_outstanding: Decimal = Decimal("0")
    lifetime_value: Decimal = Decimal("0")
    avg_payment_days: Optional[int] = None
    communication_preferences: Dict[str, bool] = {"email": True, "sms": True}
    is_suppressed: bool = False
    suppressed_reason: Optional[str] = None
    suppressed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FPCustomerSummary(BaseModel):
    """Customer summary for lists"""
    id: UUID
    display_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    customer_type: str
    total_outstanding: Decimal
    is_suppressed: bool


# ============================================================================
# INVOICE MODELS
# ============================================================================

class FPInvoiceBase(BaseModel):
    """Base invoice fields"""
    invoice_number: Optional[str] = None
    amount: Decimal
    balance: Decimal
    invoice_date: date
    due_date: date
    description: Optional[str] = None
    job_name: Optional[str] = None
    job_address: Optional[str] = None


class FPInvoiceCreate(FPInvoiceBase):
    """Create invoice request"""
    customer_id: UUID
    qbo_id: Optional[str] = None
    payer_type: PayerType = PayerType.HOMEOWNER_DIRECT


class FPInvoiceUpdate(BaseModel):
    """Update invoice request"""
    payer_type: Optional[PayerType] = None
    status: Optional[InvoiceStatus] = None
    sequence_status: Optional[SequenceStatus] = None
    sequence_paused_reason: Optional[str] = None
    insurance_claim_number: Optional[str] = None
    insurance_adjuster_name: Optional[str] = None
    insurance_adjuster_email: Optional[str] = None
    insurance_adjuster_phone: Optional[str] = None


class FPInvoice(FPInvoiceBase):
    """Full invoice model"""
    id: UUID
    tenant_id: UUID
    customer_id: UUID
    transaction_id: Optional[UUID] = None
    qbo_id: Optional[str] = None
    currency: str = "USD"
    status: InvoiceStatus = InvoiceStatus.SENT

    # Classification
    payer_type: PayerType = PayerType.HOMEOWNER_DIRECT
    payer_type_override: bool = False
    classification_confidence: Optional[Decimal] = None

    # Sequence tracking
    sequence_id: Optional[UUID] = None
    sequence_status: SequenceStatus = SequenceStatus.NOT_STARTED
    sequence_current_step: int = 0
    sequence_next_action_at: Optional[datetime] = None
    sequence_paused_reason: Optional[str] = None

    # Insurance info
    insurance_claim_number: Optional[str] = None
    insurance_adjuster_name: Optional[str] = None
    insurance_adjuster_email: Optional[str] = None
    insurance_adjuster_phone: Optional[str] = None

    # Job info
    job_id_external: Optional[str] = None

    # Payment portal
    payment_link: Optional[str] = None
    payment_token: Optional[str] = None
    payment_token_expires_at: Optional[datetime] = None

    # Metadata
    line_items: Optional[List[Dict[str, Any]]] = None
    qbo_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Computed
    days_overdue: int = 0

    class Config:
        from_attributes = True


class FPInvoiceSummary(BaseModel):
    """Invoice summary for lists"""
    id: UUID
    customer_id: UUID
    customer_name: str
    invoice_number: Optional[str]
    amount: Decimal
    balance: Decimal
    due_date: date
    days_overdue: int
    status: InvoiceStatus
    payer_type: PayerType
    sequence_status: SequenceStatus
    job_address: Optional[str] = None


# ============================================================================
# SEQUENCE MODELS
# ============================================================================

class FPSequenceStepBase(BaseModel):
    """Base sequence step fields"""
    step_order: int
    days_from_due: int
    channel: ReminderChannel
    template_id: Optional[UUID] = None
    is_active: bool = True


class FPSequenceStep(FPSequenceStepBase):
    """Full sequence step model"""
    id: UUID
    sequence_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class FPSequenceBase(BaseModel):
    """Base sequence fields"""
    name: str
    description: Optional[str] = None
    payer_type: PayerType
    is_default: bool = False
    is_active: bool = True


class FPSequenceCreate(FPSequenceBase):
    """Create sequence request"""
    steps: List[FPSequenceStepBase] = []


class FPSequence(FPSequenceBase):
    """Full sequence model"""
    id: UUID
    tenant_id: UUID
    steps: List[FPSequenceStep] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# TEMPLATE MODELS
# ============================================================================

class FPTemplateBase(BaseModel):
    """Base template fields"""
    name: str
    channel: ReminderChannel
    tone: str = "friendly"
    subject: Optional[str] = None
    body: str
    is_active: bool = True


class FPTemplateCreate(FPTemplateBase):
    """Create template request"""
    pass


class FPTemplate(FPTemplateBase):
    """Full template model"""
    id: UUID
    tenant_id: UUID
    is_system: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# REMINDER MODELS
# ============================================================================

class FPReminderCreate(BaseModel):
    """Create reminder request"""
    invoice_id: UUID
    channel: ReminderChannel
    scheduled_for: datetime
    template_id: Optional[UUID] = None


class FPReminder(BaseModel):
    """Full reminder model"""
    id: UUID
    tenant_id: UUID
    invoice_id: UUID
    customer_id: UUID
    sequence_step_id: Optional[UUID] = None
    channel: ReminderChannel
    status: ReminderStatus = ReminderStatus.SCHEDULED
    scheduled_for: datetime
    sent_at: Optional[datetime] = None
    template_id: Optional[UUID] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    personalized_body: Optional[str] = None
    external_id: Optional[str] = None
    delivery_status: Optional[str] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# PAYMENT MODELS
# ============================================================================

class FPPaymentCreate(BaseModel):
    """Create payment request"""
    invoice_id: UUID
    amount: Decimal
    payment_date: date
    payment_method: PaymentMethod = PaymentMethod.OTHER
    source: PaymentSource = PaymentSource.MANUAL
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class FPPayment(BaseModel):
    """Full payment model"""
    id: UUID
    tenant_id: UUID
    invoice_id: UUID
    customer_id: UUID
    qbo_id: Optional[str] = None
    amount: Decimal
    payment_date: date
    payment_method: PaymentMethod
    source: PaymentSource
    stripe_payment_id: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# ANALYTICS MODELS
# ============================================================================

class ARAgingBucket(BaseModel):
    """Single AR aging bucket"""
    bucket: str  # 'current', '1-30', '31-60', '61-90', '90+'
    amount: Decimal
    count: int
    percentage: Decimal = Decimal("0")


class ARAgingSummary(BaseModel):
    """Full AR aging summary"""
    tenant_id: UUID
    as_of_date: date
    buckets: List[ARAgingBucket]
    total_ar: Decimal
    total_invoices: int
    dso: Optional[Decimal] = None


class CollectionMetrics(BaseModel):
    """Collection performance metrics"""
    period_start: date
    period_end: date
    amount_collected: Decimal
    invoices_paid: int
    reminders_sent: int
    reminders_opened: int
    reminders_clicked: int
    average_days_to_collect: Optional[Decimal] = None


class DSOTrend(BaseModel):
    """DSO over time"""
    date: date
    dso: Decimal
    industry_benchmark: Decimal = Decimal("83")  # Roofing industry average


class FridayPaydaySummary(BaseModel):
    """Weekly summary for Friday Payday email"""
    tenant_id: UUID
    week_start: date
    week_end: date
    amount_collected: Decimal
    invoices_paid: int
    vs_last_week_amount: Decimal
    vs_last_week_pct: Decimal
    top_payments: List[Dict[str, Any]]
    outstanding_balance: Decimal
    outstanding_invoices: int
    current_dso: Decimal


# ============================================================================
# API RESPONSE MODELS
# ============================================================================

class PaginatedResponse(BaseModel):
    """Paginated list response"""
    items: List[Any]
    total: int
    page: int
    per_page: int
    has_more: bool


class InvoiceListResponse(BaseModel):
    """Invoice list with pagination"""
    invoices: List[FPInvoiceSummary]
    total: int
    page: int
    per_page: int
    has_more: bool
    summary: ARAgingSummary


class FPSettings(BaseModel):
    """Friday Payday tenant settings"""
    enabled: bool = False
    quiet_hours_start: str = "19:00"
    quiet_hours_end: str = "08:00"
    weekly_contact_limit: int = 2
    default_payment_methods: List[str] = ["card", "ach"]
    auto_sync_enabled: bool = True
    ai_personalization_enabled: bool = True
    sending_email: Optional[str] = None
    sending_phone: Optional[str] = None
    brand_color: str = "#1E40AF"
    logo_url: Optional[str] = None
    last_sync_at: Optional[datetime] = None
