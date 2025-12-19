"""
Valuation Shock Report Engine
Calculates the gap between owner expectations and buyer reality

This is the core WOW moment - showing roofers exactly how much value
they're leaving on the table and why buyers will pay less than expected.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class AdjustmentType(str, Enum):
    OWNER_COMPENSATION = "owner_compensation"
    PERSONAL_EXPENSE = "personal_expense"
    ONE_TIME_REVENUE = "one_time_revenue"
    ONE_TIME_EXPENSE = "one_time_expense"
    NON_RECURRING = "non_recurring"
    RELATED_PARTY = "related_party"
    DISCRETIONARY = "discretionary"
    NON_OPERATING = "non_operating"


class AdjustmentCategory(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PARTIAL = "partial"
    NEEDS_REVIEW = "needs_review"


@dataclass
class EBITDAAdjustment:
    """Individual EBITDA adjustment identified"""
    adjustment_type: str
    category: str
    description: str
    amount: float
    accepted_amount: float
    buyer_concern: str
    rejection_reason: Optional[str]
    is_recoverable: bool
    remediation_action: str
    remediation_effort: str
    remediation_impact: float
    transaction_ids: List[str]
    vendor_names: List[str]


@dataclass
class MultiplePenalty:
    """Individual multiple penalty from a value driver"""
    driver_key: str
    penalty_amount: float
    driver_score: int
    reason: str
    buyer_concern: str
    due_diligence_flag: str
    metric_name: str
    metric_value: float
    threshold_value: float
    remediation_action: str
    remediation_timeline: str
    remediation_effort: str
    remediation_impact: float
    multiple_recovery: float


@dataclass
class ValueUnlock:
    """Action to recover lost value"""
    priority_rank: int
    title: str
    description: str
    action_type: str
    ebitda_impact: float
    multiple_impact: float
    ev_impact: float
    effort_level: str
    timeline: str
    related_driver: Optional[str]
    is_locked: bool
    is_preview: bool


class ShockReportEngine:
    """
    Generates the Valuation Shock Report by:
    1. Calculating "Reported EBITDA" (owner's view with all add-backs)
    2. Calculating "Defensible EBITDA" (buyer's view after rejections)
    3. Scoring value drivers automatically from QBO data
    4. Calculating multiple penalties based on driver scores
    5. Generating prioritized value unlocks
    """

    # Owner compensation thresholds
    OWNER_COMP_RULES = {
        'market_rate_manager': 120000,  # What a buyer would pay a manager
        'max_acceptable_addback': 80000,  # Max additional add-back accepted
        'keywords': [
            'owner', 'officer', 'shareholder', 'member', 'partner',
            'draw', 'distribution', 'dividend', 'bonus', 'w-2 owner'
        ]
    }

    # Personal expense patterns (buyers reject these)
    PERSONAL_EXPENSE_PATTERNS = {
        'auto_vehicle': {
            'keywords': ['auto', 'vehicle', 'car', 'truck', 'gas', 'fuel', 'mileage'],
            'rejection_rate': 0.5,
            'concern': 'Mixed personal/business vehicle usage'
        },
        'travel_entertainment': {
            'keywords': ['travel', 'entertainment', 'meals', 'dining', 'restaurant'],
            'rejection_rate': 0.6,
            'concern': 'Discretionary spending that may not continue'
        },
        'insurance_health': {
            'keywords': ['health insurance', 'medical', 'dental', 'vision', 'life insurance'],
            'rejection_rate': 0.3,
            'concern': 'Owner-specific benefits above market'
        },
        'phone_tech': {
            'keywords': ['cell phone', 'mobile', 'iphone', 'internet', 'cable'],
            'rejection_rate': 0.4,
            'concern': 'Personal technology mixed with business'
        },
        'memberships': {
            'keywords': ['membership', 'club', 'golf', 'gym', 'country club'],
            'rejection_rate': 0.9,
            'concern': 'Personal memberships not business-essential'
        }
    }

    # One-time items (removed entirely from EBITDA)
    ONE_TIME_PATTERNS = {
        'insurance_proceeds': {
            'keywords': ['insurance claim', 'insurance proceeds', 'settlement', 'claim payment'],
            'concern': 'Non-recurring insurance windfall'
        },
        'legal_settlement': {
            'keywords': ['legal settlement', 'lawsuit', 'litigation'],
            'concern': 'One-time legal resolution'
        },
        'asset_sale': {
            'keywords': ['asset sale', 'equipment sale', 'sold truck', 'sold equipment'],
            'concern': 'One-time asset disposition'
        },
        'grant_subsidy': {
            'keywords': ['grant', 'subsidy', 'ppp', 'eidl', 'government'],
            'concern': 'Non-recurring government assistance'
        }
    }

    # Multiple penalty matrix based on driver scores
    MULTIPLE_PENALTIES = {
        'management_independence': {
            'weight': 0.25,
            'thresholds': [
                {
                    'score_range': (0, 30),
                    'penalty': -2.5,
                    'reason': 'Owner IS the business',
                    'concern': 'Business value collapses if owner leaves',
                    'flag': 'Key-man risk assessment required',
                    'remediation': 'Document all processes, hire operations manager',
                    'timeline': '12-18 months',
                    'effort': 'high'
                },
                {
                    'score_range': (30, 50),
                    'penalty': -1.5,
                    'reason': 'High owner dependency',
                    'concern': 'Owner handles critical functions daily',
                    'flag': 'Management transition plan needed',
                    'remediation': 'Delegate key responsibilities, cross-train team',
                    'timeline': '6-12 months',
                    'effort': 'medium'
                },
                {
                    'score_range': (50, 70),
                    'penalty': -0.75,
                    'reason': 'Moderate owner involvement',
                    'concern': 'Owner still required for major decisions',
                    'flag': 'Review decision-making authority',
                    'remediation': 'Empower managers with decision authority',
                    'timeline': '3-6 months',
                    'effort': 'low'
                },
            ]
        },
        'recurring_revenue': {
            'weight': 0.20,
            'thresholds': [
                {
                    'score_range': (0, 20),
                    'penalty': -2.0,
                    'reason': 'No recurring revenue',
                    'concern': 'Revenue restarts from zero each year',
                    'flag': 'Revenue quality assessment needed',
                    'remediation': 'Launch maintenance contract program',
                    'timeline': '6-12 months',
                    'effort': 'high'
                },
                {
                    'score_range': (20, 40),
                    'penalty': -1.2,
                    'reason': 'Minimal recurring revenue (<20%)',
                    'concern': 'Heavy reliance on new project wins',
                    'flag': 'Pipeline sustainability review',
                    'remediation': 'Convert past customers to maintenance contracts',
                    'timeline': '3-6 months',
                    'effort': 'medium'
                },
                {
                    'score_range': (40, 60),
                    'penalty': -0.5,
                    'reason': 'Low recurring revenue (20-40%)',
                    'concern': 'Revenue predictability below industry average',
                    'flag': 'Revenue mix analysis',
                    'remediation': 'Expand maintenance program scope',
                    'timeline': '3-6 months',
                    'effort': 'low'
                },
            ]
        },
        'financial_records': {
            'weight': 0.20,
            'thresholds': [
                {
                    'score_range': (0, 40),
                    'penalty': -1.5,
                    'reason': 'Unreliable financial records',
                    'concern': 'Cannot verify reported earnings',
                    'flag': 'Quality of earnings study required',
                    'remediation': 'Implement monthly close process, clean up books',
                    'timeline': '3-6 months',
                    'effort': 'medium'
                },
                {
                    'score_range': (40, 60),
                    'penalty': -0.75,
                    'reason': 'Inconsistent record-keeping',
                    'concern': 'Historical reconciliation issues',
                    'flag': 'Accounting review needed',
                    'remediation': 'Standardize chart of accounts, regular reconciliation',
                    'timeline': '1-3 months',
                    'effort': 'low'
                },
            ]
        },
        'customer_diversity': {
            'weight': 0.15,
            'thresholds': [
                {
                    'score_range': (0, 30),
                    'penalty': -1.0,
                    'reason': 'High customer concentration',
                    'concern': 'Top 3 customers exceed 50% of revenue',
                    'flag': 'Customer concentration risk assessment',
                    'remediation': 'Diversify customer base, expand marketing',
                    'timeline': '6-12 months',
                    'effort': 'high'
                },
                {
                    'score_range': (30, 50),
                    'penalty': -0.5,
                    'reason': 'Moderate customer concentration',
                    'concern': 'Losing top customer would significantly impact revenue',
                    'flag': 'Customer relationship review',
                    'remediation': 'Strengthen relationships, add new customers',
                    'timeline': '3-6 months',
                    'effort': 'medium'
                },
            ]
        },
        'operational_systems': {
            'weight': 0.10,
            'thresholds': [
                {
                    'score_range': (0, 40),
                    'penalty': -0.75,
                    'reason': 'No documented systems',
                    'concern': 'Tribal knowledge, difficult to scale or transfer',
                    'flag': 'Operational due diligence required',
                    'remediation': 'Document SOPs, implement project management system',
                    'timeline': '3-6 months',
                    'effort': 'medium'
                },
                {
                    'score_range': (40, 60),
                    'penalty': -0.35,
                    'reason': 'Partial system documentation',
                    'concern': 'Inconsistent process execution',
                    'flag': 'Process standardization review',
                    'remediation': 'Complete documentation, train team',
                    'timeline': '1-3 months',
                    'effort': 'low'
                },
            ]
        },
        'market_outlook': {
            'weight': 0.10,
            'thresholds': [
                {
                    'score_range': (0, 40),
                    'penalty': -0.5,
                    'reason': 'Limited market position',
                    'concern': 'No competitive moat or differentiation',
                    'flag': 'Market position analysis',
                    'remediation': 'Define and communicate unique value proposition',
                    'timeline': '3-6 months',
                    'effort': 'medium'
                },
            ]
        }
    }

    # Base multiples by tier (Matador methodology)
    TIER_MULTIPLES = {
        'below_avg': {'low': 2.5, 'high': 3.5, 'typical_sde': 3.0},
        'avg': {'low': 4.0, 'high': 5.5, 'typical_sde': 4.5},
        'above_avg': {'low': 6.0, 'high': 8.0, 'typical_sde': 7.0}
    }

    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL", ""),
            os.getenv("SUPABASE_SERVICE_KEY", "")
        )

    def generate_shock_report(self, tenant_id: str) -> Dict[str, Any]:
        """
        Generate the complete Valuation Shock Report

        Returns the "shock" - the gap between what owner expects
        and what a buyer will actually pay.
        """
        # Get date range (TTM)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)

        # 1. Calculate reported financials (owner's view)
        reported = self._calculate_reported_financials(tenant_id, start_date, end_date)

        # 2. Analyze EBITDA adjustments (what buyer will reject)
        adjustments = self._analyze_ebitda_adjustments(tenant_id, start_date, end_date, reported)

        # 3. Calculate defensible EBITDA (buyer's view)
        defensible_ebitda = self._calculate_defensible_ebitda(reported, adjustments)

        # 4. Score value drivers automatically
        driver_scores = self._auto_score_drivers(tenant_id, start_date, end_date)

        # 5. Calculate multiple penalties
        penalties, buyer_multiple = self._calculate_multiple_penalties(driver_scores)

        # 6. Determine tier
        tier = self._determine_tier(driver_scores)

        # 7. Calculate valuations
        owner_expected_multiple = 10.0  # Owners typically expect 10x
        owner_expected_valuation = reported['ebitda'] * owner_expected_multiple

        buyer_valuation_low = defensible_ebitda * buyer_multiple['low']
        buyer_valuation_high = defensible_ebitda * buyer_multiple['high']

        # The gap (the shock)
        value_gap = owner_expected_valuation - buyer_valuation_high
        ebitda_haircut = reported['ebitda'] - defensible_ebitda
        multiple_penalty = owner_expected_multiple - buyer_multiple['high']

        # 8. Generate value unlocks
        value_unlocks = self._generate_value_unlocks(adjustments, penalties, defensible_ebitda)

        # 9. Get data quality metrics
        data_metrics = self._get_data_quality_metrics(tenant_id, start_date, end_date)

        # Build the report
        report = {
            'tenant_id': tenant_id,
            'generated_at': datetime.now().isoformat(),

            # Reported (what owner thinks)
            'reported': {
                'revenue': reported['revenue'],
                'ebitda': reported['ebitda'],
                'owner_comp': reported['owner_comp'],
                'addbacks': reported['total_addbacks'],
                'expected_multiple': owner_expected_multiple,
                'expected_valuation': owner_expected_valuation
            },

            # Defensible (what buyer will pay)
            'defensible': {
                'ebitda': defensible_ebitda,
                'multiple_low': buyer_multiple['low'],
                'multiple_high': buyer_multiple['high'],
                'valuation_low': buyer_valuation_low,
                'valuation_high': buyer_valuation_high
            },

            # The gap (the shock moment)
            'gap': {
                'ebitda_haircut': ebitda_haircut,
                'ebitda_haircut_pct': (ebitda_haircut / reported['ebitda'] * 100) if reported['ebitda'] > 0 else 0,
                'multiple_penalty': multiple_penalty,
                'value_gap': value_gap,
                'value_gap_pct': (value_gap / owner_expected_valuation * 100) if owner_expected_valuation > 0 else 0
            },

            # Detailed breakdowns
            'adjustments': [asdict(a) for a in adjustments],
            'penalties': [asdict(p) for p in penalties],
            'driver_scores': driver_scores,
            'tier': tier,

            # Value recovery
            'value_unlocks': [asdict(u) for u in value_unlocks],
            'total_recoverable': sum(u.ev_impact for u in value_unlocks),

            # Data quality
            'data_quality': data_metrics,

            # Confidence
            'confidence_score': self._calculate_confidence(data_metrics, driver_scores)
        }

        # Store the report
        self._store_report(report)

        return report

    def _calculate_reported_financials(
        self,
        tenant_id: str,
        start_date,
        end_date
    ) -> Dict[str, float]:
        """Calculate financials as the owner reports them (with all add-backs)"""

        # Get revenue from invoices
        revenue_result = self.supabase.table("transactions")\
            .select("total_amount")\
            .eq("tenant_id", tenant_id)\
            .eq("transaction_type", "invoice")\
            .gte("transaction_date", start_date.isoformat())\
            .lte("transaction_date", end_date.isoformat())\
            .execute()

        revenue = sum(float(t.get('total_amount', 0)) for t in revenue_result.data) if revenue_result.data else 0

        # Get expenses
        expense_result = self.supabase.table("transactions")\
            .select("total_amount, description, metadata")\
            .eq("tenant_id", tenant_id)\
            .in_("transaction_type", ["bill", "expense"])\
            .gte("transaction_date", start_date.isoformat())\
            .lte("transaction_date", end_date.isoformat())\
            .execute()

        total_expenses = sum(float(t.get('total_amount', 0)) for t in expense_result.data) if expense_result.data else 0

        # Identify owner compensation
        owner_comp = 0
        for txn in (expense_result.data or []):
            desc = (txn.get('description') or '').lower()
            if any(kw in desc for kw in self.OWNER_COMP_RULES['keywords']):
                owner_comp += float(txn.get('total_amount', 0))

        # Calculate basic EBITDA (before owner adds back everything)
        gross_ebitda = revenue - total_expenses

        # Owner's reported EBITDA (adds back owner comp + typical adjustments)
        # Owners typically add back 15-25% of expenses as "adjustments"
        estimated_addbacks = total_expenses * 0.18  # Conservative estimate
        reported_ebitda = gross_ebitda + owner_comp + estimated_addbacks

        return {
            'revenue': revenue,
            'expenses': total_expenses,
            'gross_ebitda': gross_ebitda,
            'owner_comp': owner_comp,
            'total_addbacks': owner_comp + estimated_addbacks,
            'ebitda': reported_ebitda
        }

    def _analyze_ebitda_adjustments(
        self,
        tenant_id: str,
        start_date,
        end_date,
        reported: Dict
    ) -> List[EBITDAAdjustment]:
        """
        Analyze transactions to identify questionable add-backs
        This is where we show what buyers will reject
        """
        adjustments = []

        # Get all expense transactions
        expenses = self.supabase.table("transactions")\
            .select("id, total_amount, description, vendor_id, metadata")\
            .eq("tenant_id", tenant_id)\
            .in_("transaction_type", ["bill", "expense"])\
            .gte("transaction_date", start_date.isoformat())\
            .lte("transaction_date", end_date.isoformat())\
            .execute()

        # 1. Owner Compensation Analysis
        owner_comp_total = reported['owner_comp']
        market_rate = self.OWNER_COMP_RULES['market_rate_manager']
        max_addback = self.OWNER_COMP_RULES['max_acceptable_addback']

        if owner_comp_total > market_rate + max_addback:
            rejected_amount = owner_comp_total - market_rate - max_addback
            adjustments.append(EBITDAAdjustment(
                adjustment_type=AdjustmentType.OWNER_COMPENSATION,
                category=AdjustmentCategory.REJECTED,
                description=f"Owner compensation exceeds market rate + acceptable add-back",
                amount=rejected_amount,
                accepted_amount=max_addback,
                buyer_concern="Buyer will normalize to market-rate manager salary",
                rejection_reason=f"Total ${owner_comp_total:,.0f} exceeds ${market_rate + max_addback:,.0f} threshold",
                is_recoverable=True,
                remediation_action="Document owner duties, justify compensation with market data",
                remediation_effort="medium",
                remediation_impact=rejected_amount * 4.5,  # Impact at mid multiple
                transaction_ids=[],
                vendor_names=[]
            ))

        # 2. Personal Expense Analysis
        for pattern_name, pattern_config in self.PERSONAL_EXPENSE_PATTERNS.items():
            matching_txns = []
            total_amount = 0

            for txn in (expenses.data or []):
                desc = (txn.get('description') or '').lower()
                if any(kw in desc for kw in pattern_config['keywords']):
                    matching_txns.append(txn.get('id'))
                    total_amount += float(txn.get('total_amount', 0))

            if total_amount > 0:
                rejected_amount = total_amount * pattern_config['rejection_rate']
                if rejected_amount > 1000:  # Only flag significant amounts
                    adjustments.append(EBITDAAdjustment(
                        adjustment_type=AdjustmentType.PERSONAL_EXPENSE,
                        category=AdjustmentCategory.PARTIAL,
                        description=f"{pattern_name.replace('_', ' ').title()} expenses flagged",
                        amount=total_amount,
                        accepted_amount=total_amount - rejected_amount,
                        buyer_concern=pattern_config['concern'],
                        rejection_reason=f"Buyers typically reject {pattern_config['rejection_rate']*100:.0f}% of these expenses",
                        is_recoverable=True,
                        remediation_action="Separate personal from business expenses, document business purpose",
                        remediation_effort="low",
                        remediation_impact=rejected_amount * 4.5,
                        transaction_ids=matching_txns[:10],  # First 10 for reference
                        vendor_names=[]
                    ))

        # 3. One-Time Items Analysis
        for pattern_name, pattern_config in self.ONE_TIME_PATTERNS.items():
            for txn in (expenses.data or []):
                desc = (txn.get('description') or '').lower()
                if any(kw in desc for kw in pattern_config['keywords']):
                    amount = float(txn.get('total_amount', 0))
                    if amount > 5000:  # Only flag significant amounts
                        adjustments.append(EBITDAAdjustment(
                            adjustment_type=AdjustmentType.ONE_TIME_EXPENSE,
                            category=AdjustmentCategory.REJECTED,
                            description=f"One-time item: {pattern_name.replace('_', ' ').title()}",
                            amount=amount,
                            accepted_amount=0,
                            buyer_concern=pattern_config['concern'],
                            rejection_reason="One-time items are excluded from normalized EBITDA",
                            is_recoverable=False,
                            remediation_action="No action needed - correctly excluded",
                            remediation_effort="low",
                            remediation_impact=0,
                            transaction_ids=[txn.get('id')],
                            vendor_names=[]
                        ))

        return adjustments

    def _calculate_defensible_ebitda(
        self,
        reported: Dict,
        adjustments: List[EBITDAAdjustment]
    ) -> float:
        """
        Calculate buyer-defensible EBITDA after all adjustments
        """
        defensible = reported['ebitda']

        for adj in adjustments:
            if adj.category == AdjustmentCategory.REJECTED:
                defensible -= adj.amount
            elif adj.category == AdjustmentCategory.PARTIAL:
                defensible -= (adj.amount - adj.accepted_amount)

        return max(defensible, 0)

    def _auto_score_drivers(
        self,
        tenant_id: str,
        start_date,
        end_date
    ) -> Dict[str, int]:
        """
        Automatically score value drivers from QBO data
        Returns scores 0-100 for each driver
        """
        scores = {}

        # Get existing driver scores if any
        existing = self.supabase.table("driver_scores")\
            .select("driver_key, score")\
            .eq("tenant_id", tenant_id)\
            .order("as_of_date", desc=True)\
            .limit(10)\
            .execute()

        existing_scores = {d['driver_key']: d['score'] for d in (existing.data or [])}

        # 1. Management Independence - estimate from owner comp ratio
        # Higher owner comp = lower independence
        # This is a rough estimate - questionnaire would be more accurate
        scores['management_independence'] = existing_scores.get('management_independence', 35)

        # 2. Financial Records - based on data quality
        # Count uncategorized transactions, reconciliation issues
        uncategorized = self.supabase.table("transactions")\
            .select("id", count="exact")\
            .eq("tenant_id", tenant_id)\
            .is_("category", "null")\
            .execute()

        total_txns = self.supabase.table("transactions")\
            .select("id", count="exact")\
            .eq("tenant_id", tenant_id)\
            .execute()

        if total_txns.count and total_txns.count > 0:
            uncategorized_pct = (uncategorized.count or 0) / total_txns.count
            scores['financial_records'] = max(0, min(100, int(100 - uncategorized_pct * 150)))
        else:
            scores['financial_records'] = existing_scores.get('financial_records', 50)

        # 3. Recurring Revenue - check for maintenance/service contracts
        # Look for recurring invoice patterns
        invoices = self.supabase.table("transactions")\
            .select("customer_id, total_amount")\
            .eq("tenant_id", tenant_id)\
            .eq("transaction_type", "invoice")\
            .gte("transaction_date", start_date.isoformat())\
            .execute()

        if invoices.data:
            # Count repeat customers as proxy for recurring revenue
            customer_counts = {}
            for inv in invoices.data:
                cust = inv.get('customer_id')
                if cust:
                    customer_counts[cust] = customer_counts.get(cust, 0) + 1

            repeat_customers = sum(1 for c in customer_counts.values() if c > 1)
            total_customers = len(customer_counts)
            repeat_pct = repeat_customers / total_customers if total_customers > 0 else 0

            # Roofing typically has low recurring, so scale appropriately
            scores['recurring_revenue'] = max(0, min(100, int(repeat_pct * 150)))
        else:
            scores['recurring_revenue'] = existing_scores.get('recurring_revenue', 20)

        # 4. Customer Diversity - concentration analysis
        if invoices.data:
            customer_revenue = {}
            total_revenue = 0
            for inv in invoices.data:
                cust = inv.get('customer_id', 'unknown')
                amount = float(inv.get('total_amount', 0))
                customer_revenue[cust] = customer_revenue.get(cust, 0) + amount
                total_revenue += amount

            if total_revenue > 0:
                # Top 3 customer concentration
                sorted_customers = sorted(customer_revenue.values(), reverse=True)
                top_3_revenue = sum(sorted_customers[:3])
                concentration_pct = top_3_revenue / total_revenue

                # Lower concentration = higher score
                scores['customer_diversity'] = max(0, min(100, int((1 - concentration_pct) * 120)))
            else:
                scores['customer_diversity'] = 50
        else:
            scores['customer_diversity'] = existing_scores.get('customer_diversity', 50)

        # 5. Operational Systems - use existing or default
        scores['operational_systems'] = existing_scores.get('operational_systems', 40)

        # 6. Market Outlook - use existing or default
        scores['market_outlook'] = existing_scores.get('market_outlook', 60)

        return scores

    def _calculate_multiple_penalties(
        self,
        driver_scores: Dict[str, int]
    ) -> Tuple[List[MultiplePenalty], Dict[str, float]]:
        """
        Calculate multiple penalties based on driver scores
        Returns list of penalties and final buyer multiple range
        """
        penalties = []
        total_penalty = 0

        # Start with a baseline multiple (assuming average tier initially)
        baseline_multiple = 6.0

        for driver_key, config in self.MULTIPLE_PENALTIES.items():
            score = driver_scores.get(driver_key, 50)

            for threshold in config['thresholds']:
                score_min, score_max = threshold['score_range']
                if score_min <= score < score_max:
                    penalty = MultiplePenalty(
                        driver_key=driver_key,
                        penalty_amount=threshold['penalty'],
                        driver_score=score,
                        reason=threshold['reason'],
                        buyer_concern=threshold['concern'],
                        due_diligence_flag=threshold['flag'],
                        metric_name=f"{driver_key}_score",
                        metric_value=score,
                        threshold_value=score_max,
                        remediation_action=threshold['remediation'],
                        remediation_timeline=threshold['timeline'],
                        remediation_effort=threshold['effort'],
                        remediation_impact=abs(threshold['penalty']) * 100000,  # Rough EV impact
                        multiple_recovery=abs(threshold['penalty'])
                    )
                    penalties.append(penalty)
                    total_penalty += threshold['penalty']
                    break

        # Calculate final multiple
        final_multiple_high = max(2.0, baseline_multiple + total_penalty)
        final_multiple_low = max(1.5, final_multiple_high - 1.0)

        return penalties, {'low': final_multiple_low, 'high': final_multiple_high}

    def _determine_tier(self, driver_scores: Dict[str, int]) -> str:
        """Determine valuation tier based on driver scores"""
        avg_score = sum(driver_scores.values()) / len(driver_scores) if driver_scores else 50

        if avg_score < 40:
            return 'below_avg'
        elif avg_score < 65:
            return 'avg'
        else:
            return 'above_avg'

    def _generate_value_unlocks(
        self,
        adjustments: List[EBITDAAdjustment],
        penalties: List[MultiplePenalty],
        defensible_ebitda: float
    ) -> List[ValueUnlock]:
        """
        Generate prioritized list of actions to recover lost value
        """
        unlocks = []
        priority = 1

        # From EBITDA adjustments (recover rejected add-backs)
        for adj in sorted(adjustments, key=lambda x: x.remediation_impact, reverse=True):
            if adj.is_recoverable and adj.remediation_impact > 10000:
                unlocks.append(ValueUnlock(
                    priority_rank=priority,
                    title=f"Fix: {adj.description}",
                    description=adj.remediation_action,
                    action_type='ebitda_recovery',
                    ebitda_impact=adj.amount - adj.accepted_amount,
                    multiple_impact=0,
                    ev_impact=adj.remediation_impact,
                    effort_level=adj.remediation_effort,
                    timeline="1-3 months",
                    related_driver=None,
                    is_locked=True,
                    is_preview=priority <= 3
                ))
                priority += 1

        # From multiple penalties (improve drivers)
        for penalty in sorted(penalties, key=lambda x: x.remediation_impact, reverse=True):
            unlocks.append(ValueUnlock(
                priority_rank=priority,
                title=f"Improve: {penalty.driver_key.replace('_', ' ').title()}",
                description=penalty.remediation_action,
                action_type='multiple_expansion',
                ebitda_impact=0,
                multiple_impact=penalty.multiple_recovery,
                ev_impact=penalty.remediation_impact,
                effort_level=penalty.remediation_effort,
                timeline=penalty.remediation_timeline,
                related_driver=penalty.driver_key,
                is_locked=True,
                is_preview=priority <= 3
            ))
            priority += 1

        # Sort by EV impact and return top 10
        unlocks.sort(key=lambda x: x.ev_impact, reverse=True)
        for i, unlock in enumerate(unlocks):
            unlock.priority_rank = i + 1

        return unlocks[:10]

    def _get_data_quality_metrics(
        self,
        tenant_id: str,
        start_date,
        end_date
    ) -> Dict:
        """Get data quality metrics for confidence calculation"""

        txn_count = self.supabase.table("transactions")\
            .select("id", count="exact")\
            .eq("tenant_id", tenant_id)\
            .gte("transaction_date", start_date.isoformat())\
            .execute()

        invoice_count = self.supabase.table("transactions")\
            .select("id", count="exact")\
            .eq("tenant_id", tenant_id)\
            .eq("transaction_type", "invoice")\
            .gte("transaction_date", start_date.isoformat())\
            .execute()

        expense_count = self.supabase.table("transactions")\
            .select("id", count="exact")\
            .eq("tenant_id", tenant_id)\
            .in_("transaction_type", ["bill", "expense"])\
            .gte("transaction_date", start_date.isoformat())\
            .execute()

        return {
            'transaction_count': txn_count.count or 0,
            'invoice_count': invoice_count.count or 0,
            'expense_count': expense_count.count or 0,
            'date_range_start': start_date.isoformat(),
            'date_range_end': end_date.isoformat(),
            'months_of_data': 12
        }

    def _calculate_confidence(
        self,
        data_metrics: Dict,
        driver_scores: Dict
    ) -> int:
        """Calculate confidence score for the report"""
        confidence = 50  # Base confidence

        # More transactions = higher confidence
        txn_count = data_metrics.get('transaction_count', 0)
        if txn_count > 500:
            confidence += 20
        elif txn_count > 200:
            confidence += 15
        elif txn_count > 50:
            confidence += 10

        # Having both invoices and expenses
        if data_metrics.get('invoice_count', 0) > 10:
            confidence += 10
        if data_metrics.get('expense_count', 0) > 20:
            confidence += 10

        # Driver scores that seem reasonable (not all defaults)
        score_variance = max(driver_scores.values()) - min(driver_scores.values())
        if score_variance > 20:
            confidence += 10

        return min(100, confidence)

    def _store_report(self, report: Dict) -> str:
        """Store the shock report in the database"""
        try:
            result = self.supabase.table("valuation_shock_reports").insert({
                'tenant_id': report['tenant_id'],
                'generated_at': report['generated_at'],

                'reported_revenue': report['reported']['revenue'],
                'reported_ebitda': report['reported']['ebitda'],
                'reported_owner_comp': report['reported']['owner_comp'],
                'reported_addbacks': report['reported']['addbacks'],
                'expected_multiple': report['reported']['expected_multiple'],
                'expected_valuation': report['reported']['expected_valuation'],

                'defensible_ebitda': report['defensible']['ebitda'],
                'buyer_multiple_low': report['defensible']['multiple_low'],
                'buyer_multiple_high': report['defensible']['multiple_high'],
                'buyer_valuation_low': report['defensible']['valuation_low'],
                'buyer_valuation_high': report['defensible']['valuation_high'],

                'ebitda_haircut': report['gap']['ebitda_haircut'],
                'multiple_penalty': report['gap']['multiple_penalty'],
                'value_gap': report['gap']['value_gap'],
                'value_gap_percentage': report['gap']['value_gap_pct'],

                'ebitda_adjustments': report['adjustments'],
                'multiple_penalties': report['penalties'],
                'driver_scores': report['driver_scores'],

                'value_unlocks': report['value_unlocks'],
                'total_recoverable_value': report['total_recoverable'],

                'tier': report['tier'],

                'qbo_data_range_start': report['data_quality']['date_range_start'],
                'qbo_data_range_end': report['data_quality']['date_range_end'],
                'transaction_count': report['data_quality']['transaction_count'],
                'invoice_count': report['data_quality']['invoice_count'],
                'expense_count': report['data_quality']['expense_count'],
                'confidence_score': report['confidence_score']
            }).execute()

            return result.data[0]['id'] if result.data else None
        except Exception as e:
            print(f"Warning: Could not store shock report: {e}")
            return None


# Convenience function
def generate_shock_report(tenant_id: str) -> Dict[str, Any]:
    """Generate a Valuation Shock Report for a tenant"""
    engine = ShockReportEngine()
    return engine.generate_shock_report(tenant_id)
