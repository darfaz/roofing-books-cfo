"""
CrewCFO Multi-Agent System

Specialized agents for different knowledge domains:
- Librarian: Knowledge management, sorting, deduplication
- Software: Tech specs, architecture, API docs
- Marketing: Brand, copy, positioning
- Outreach: Email templates, sequences
- Valuation: M&A, exit strategy, multiples
- Accounting: QBO, bookkeeping, reconciliation
- Sales: Proposals, pricing, objections

Usage:
    from agents import Router, Librarian

    router = Router()
    result = router.query("What are the valuation multiples?")
"""

from .router import Router, route_query
from .librarian import Librarian
from .domain_agents import (
    SoftwareAgent,
    MarketingAgent,
    OutreachAgent,
    ValuationAgent,
    AccountingAgent,
    SalesAgent,
    RoofingIndustryAgent,
)

__all__ = [
    "Router",
    "route_query",
    "Librarian",
    "SoftwareAgent",
    "MarketingAgent",
    "OutreachAgent",
    "ValuationAgent",
    "AccountingAgent",
    "SalesAgent",
    "RoofingIndustryAgent",
]
