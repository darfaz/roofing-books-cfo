"""
Friday Payday - Invoice Classification Engine

Automatically classifies invoices by payer type based on:
- Invoice memo/description content
- Line item descriptions
- Invoice amount
- Customer history
"""
import re
from typing import Dict, List, Tuple, Optional
from decimal import Decimal

from .schemas import PayerType


# Classification keywords by payer type
CLASSIFICATION_KEYWORDS: Dict[PayerType, List[str]] = {
    PayerType.DEPRECIATION_RECOVERY: [
        "acv", "rcv", "depreciation", "recoverable depreciation",
        "withheld", "holdback", "actual cash value", "replacement cost value"
    ],
    PayerType.SUPPLEMENT_PENDING: [
        "supplement", "supplemental", "code upgrade", "additional",
        "revision", "change order", "added scope"
    ],
    PayerType.INSURANCE_PENDING: [
        "insurance", "claim", "claim #", "claim number", "adjuster",
        "carrier", "allstate", "state farm", "liberty mutual", "nationwide",
        "farmers", "usaa", "geico", "progressive", "aob", "assignment of benefits"
    ],
    PayerType.GC_COMMERCIAL: [
        "general contractor", "commercial", "gc:", "builder",
        "property management", "multi-family", "apartment", "hoa",
        "condo association", "development"
    ],
    PayerType.RETAINAGE: [
        "retainage", "retention", "final payment", "holdback",
        "completion payment", "punch list"
    ]
}

# Amount threshold for GC/Commercial classification
GC_COMMERCIAL_AMOUNT_THRESHOLD = Decimal("25000")


def _normalize_text(text: Optional[str]) -> str:
    """Normalize text for keyword matching"""
    if not text:
        return ""
    return text.lower().strip()


def _check_keywords(text: str, keywords: List[str]) -> Tuple[bool, float]:
    """
    Check if any keywords are present in text.
    Returns (matched, confidence) tuple.
    """
    text_lower = _normalize_text(text)
    if not text_lower:
        return False, 0.0

    matches = 0
    for keyword in keywords:
        if keyword.lower() in text_lower:
            matches += 1

    if matches == 0:
        return False, 0.0

    # Confidence based on number of keyword matches
    confidence = min(0.95, 0.6 + (matches * 0.15))
    return True, confidence


def classify_invoice(
    memo: Optional[str] = None,
    description: Optional[str] = None,
    line_items: Optional[List[Dict]] = None,
    amount: Optional[Decimal] = None,
    customer_type: Optional[str] = None,
) -> Tuple[PayerType, float]:
    """
    Classify an invoice into a payer type.

    Args:
        memo: Invoice memo/notes field
        description: Invoice description
        line_items: List of line item dicts with 'description' key
        amount: Total invoice amount
        customer_type: Customer type from fp_customers

    Returns:
        Tuple of (PayerType, confidence_score)
    """
    # Combine all text for analysis
    text_parts = [memo or "", description or ""]

    if line_items:
        for item in line_items:
            if isinstance(item, dict):
                text_parts.append(item.get("description", ""))
                text_parts.append(item.get("name", ""))

    combined_text = " ".join(text_parts)

    # Check each payer type in priority order
    # Priority: Depreciation > Supplement > Insurance > GC > Retainage > Homeowner

    # 1. Check for depreciation recovery (highest priority)
    matched, confidence = _check_keywords(
        combined_text,
        CLASSIFICATION_KEYWORDS[PayerType.DEPRECIATION_RECOVERY]
    )
    if matched:
        return PayerType.DEPRECIATION_RECOVERY, confidence

    # 2. Check for supplement pending
    matched, confidence = _check_keywords(
        combined_text,
        CLASSIFICATION_KEYWORDS[PayerType.SUPPLEMENT_PENDING]
    )
    if matched:
        return PayerType.SUPPLEMENT_PENDING, confidence

    # 3. Check for insurance pending
    matched, confidence = _check_keywords(
        combined_text,
        CLASSIFICATION_KEYWORDS[PayerType.INSURANCE_PENDING]
    )
    if matched:
        return PayerType.INSURANCE_PENDING, confidence

    # 4. Check for GC/Commercial by keywords OR amount
    matched, confidence = _check_keywords(
        combined_text,
        CLASSIFICATION_KEYWORDS[PayerType.GC_COMMERCIAL]
    )
    if matched:
        return PayerType.GC_COMMERCIAL, confidence

    # Check by amount threshold
    if amount and amount >= GC_COMMERCIAL_AMOUNT_THRESHOLD:
        return PayerType.GC_COMMERCIAL, 0.7

    # Check by customer type
    if customer_type and customer_type in ["gc", "commercial", "builder"]:
        return PayerType.GC_COMMERCIAL, 0.85

    # 5. Check for retainage
    matched, confidence = _check_keywords(
        combined_text,
        CLASSIFICATION_KEYWORDS[PayerType.RETAINAGE]
    )
    if matched:
        return PayerType.RETAINAGE, confidence

    # Default: Homeowner direct
    return PayerType.HOMEOWNER_DIRECT, 0.8


def get_default_sequence_for_payer_type(payer_type: PayerType) -> str:
    """
    Get the default sequence name for a payer type.
    Used when assigning sequences after classification.
    """
    sequence_names = {
        PayerType.HOMEOWNER_DIRECT: "Homeowner Standard",
        PayerType.INSURANCE_PENDING: "Insurance Claim",
        PayerType.SUPPLEMENT_PENDING: "Supplement Follow-up",
        PayerType.DEPRECIATION_RECOVERY: "Depreciation Recovery",
        PayerType.GC_COMMERCIAL: "Commercial 30-45-60",
        PayerType.RETAINAGE: "Homeowner Standard",  # Use homeowner for retainage
    }
    return sequence_names.get(payer_type, "Homeowner Standard")


def extract_claim_number(text: str) -> Optional[str]:
    """
    Attempt to extract an insurance claim number from text.
    Common formats: CLM-123456, #123456, Claim 123456
    """
    if not text:
        return None

    patterns = [
        r'claim[:\s#]*(\d{5,12})',
        r'clm[-\s#]*(\d{5,12})',
        r'#(\d{6,12})',
        r'policy[:\s#]*(\w{5,15})',
    ]

    text_lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(1)

    return None


def suggest_classification_improvements(
    invoice_data: Dict,
    actual_outcome: PayerType
) -> Dict:
    """
    Analyze a misclassified invoice to suggest keyword improvements.
    Used for learning from manual overrides.
    """
    predicted, confidence = classify_invoice(
        memo=invoice_data.get("memo"),
        description=invoice_data.get("description"),
        line_items=invoice_data.get("line_items"),
        amount=invoice_data.get("amount"),
        customer_type=invoice_data.get("customer_type"),
    )

    if predicted == actual_outcome:
        return {"needs_improvement": False}

    # Find unique words in the text that might be new keywords
    text = f"{invoice_data.get('memo', '')} {invoice_data.get('description', '')}"
    words = set(text.lower().split())

    # Filter out common words
    common_words = {"the", "a", "an", "for", "and", "or", "to", "of", "in", "on"}
    unique_words = words - common_words

    return {
        "needs_improvement": True,
        "predicted": predicted.value,
        "actual": actual_outcome.value,
        "confidence": confidence,
        "candidate_keywords": list(unique_words)[:10],
    }
