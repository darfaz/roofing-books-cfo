"""
Friday Payday - Collections Automation for Roofing Contractors
"""

from .schemas import (
    PayerType,
    InvoiceStatus,
    SequenceStatus,
    ReminderChannel,
    ReminderStatus,
    FPCustomer,
    FPInvoice,
    FPSequence,
    FPReminder,
    ARAgingBucket,
    ARAgingSummary,
)
from .classification import classify_invoice, CLASSIFICATION_KEYWORDS
from .invoice_sync import FridayPaydaySync
from .analytics import FridayPaydayAnalytics
from .dunning_engine import DunningEngine
from .template_service import TemplateService
from .friday_email import FridayEmailService

__all__ = [
    # Enums
    "PayerType",
    "InvoiceStatus",
    "SequenceStatus",
    "ReminderChannel",
    "ReminderStatus",
    # Models
    "FPCustomer",
    "FPInvoice",
    "FPSequence",
    "FPReminder",
    "ARAgingBucket",
    "ARAgingSummary",
    # Services
    "classify_invoice",
    "CLASSIFICATION_KEYWORDS",
    "FridayPaydaySync",
    "FridayPaydayAnalytics",
    "DunningEngine",
    "TemplateService",
    "FridayEmailService",
]
