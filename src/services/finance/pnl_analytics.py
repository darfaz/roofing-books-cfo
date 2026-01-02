"""
P&L Analytics Service

Transforms raw QuickBooks P&L report data into actionable analytics:
- Break-even revenue calculation
- EBITDA/SDE calculation for valuation
- Profit leak detection
- Cash flow forecasting
- Industry benchmarking (roofing)
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass


# Roofing industry benchmarks (based on industry data)
ROOFING_BENCHMARKS = {
    "gross_margin": {"healthy": 0.35, "warning": 0.28, "critical": 0.20},
    "net_margin": {"healthy": 0.10, "warning": 0.05, "critical": 0.02},
    "overhead_ratio": {"healthy": 0.20, "warning": 0.28, "critical": 0.35},
    "labor_ratio": {"healthy": 0.30, "warning": 0.40, "critical": 0.50},
    "marketing_ratio": {"healthy": 0.05, "warning": 0.08, "critical": 0.12},
}

# Categories for expense classification
OVERHEAD_KEYWORDS = [
    "office", "admin", "rent", "lease", "utility", "utilities", "electric",
    "phone", "telephone", "internet", "insurance", "professional", "legal",
    "accounting", "marketing", "advertising", "dues", "subscription",
    "depreciation", "amortization", "interest", "bank", "merchant",
    "security", "janitorial", "meals", "entertainment", "education",
    "license", "postage", "computer", "software", "paypal"
]

COGS_KEYWORDS = [
    "material", "supplies", "labor", "subcontract", "equipment",
    "disposal", "dump", "roofing", "shingle", "flashing",
    "cogs", "cost of", "direct"
]


@dataclass
class PLAnalytics:
    """Holds computed P&L analytics"""
    period_start: str
    period_end: str

    # Core P&L figures
    total_revenue: float
    total_cogs: float
    gross_profit: float
    gross_margin_pct: float
    total_expenses: float
    net_income: float
    net_margin_pct: float

    # Computed metrics
    monthly_revenue: float
    monthly_overhead: float
    break_even_monthly: float
    break_even_annual: float

    # EBITDA calculation
    ebitda: float
    ebitda_margin_pct: float
    sde: float  # Seller's Discretionary Earnings

    # Health indicators
    gross_margin_status: str
    net_margin_status: str
    overhead_status: str

    # Detailed breakdowns
    overhead_by_category: Dict[str, float]
    cogs_by_category: Dict[str, float]
    profit_leaks: List[Dict]

    # Valuation metrics
    valuation_multiple_range: Tuple[float, float]
    estimated_value_range: Tuple[float, float]


class PnLAnalyticsService:
    """
    Analyzes P&L data to produce actionable insights
    """

    def __init__(self):
        self.benchmarks = ROOFING_BENCHMARKS

    def parse_pnl_report(self, report_data: Dict) -> Dict:
        """
        Parse raw QuickBooks P&L report into structured data

        Args:
            report_data: Raw P&L report from QuickBooks MCP tool

        Returns:
            Structured P&L data with categorized expenses
        """
        summary = report_data.get("summary", {})
        metrics = report_data.get("metrics", {})

        # Core figures
        total_income = float(summary.get("total_income", 0))
        total_cogs = float(summary.get("total_cogs", 0))
        gross_profit = float(summary.get("gross_profit", 0))
        total_expenses = float(summary.get("total_expenses", 0))
        net_income = float(summary.get("net_income", 0))

        # Parse expense categories from metrics
        overhead_items = {}
        cogs_items = {}

        for key, value in metrics.items():
            if not isinstance(value, (int, float)):
                continue

            value = float(value)
            key_lower = key.lower()

            # Categorize expenses
            if "expenses." in key_lower:
                # Extract account name
                account_name = key.split(".")[-1]
                category = self._categorize_expense(account_name)

                if category == "overhead":
                    overhead_items[account_name] = value
                elif category == "cogs":
                    cogs_items[account_name] = value

            elif "cost of goods sold." in key_lower:
                account_name = key.split(".")[-1]
                cogs_items[account_name] = value

        return {
            "period": {
                "start": report_data.get("start_date"),
                "end": report_data.get("end_date")
            },
            "summary": {
                "total_income": total_income,
                "total_cogs": abs(total_cogs),  # COGS often comes as negative
                "gross_profit": gross_profit,
                "total_expenses": total_expenses,
                "net_income": net_income
            },
            "overhead_items": overhead_items,
            "cogs_items": cogs_items,
            "raw_metrics": metrics
        }

    def _categorize_expense(self, account_name: str) -> str:
        """Categorize an expense account as overhead or COGS"""
        name_lower = account_name.lower()

        for keyword in COGS_KEYWORDS:
            if keyword in name_lower:
                return "cogs"

        for keyword in OVERHEAD_KEYWORDS:
            if keyword in name_lower:
                return "overhead"

        # Default to overhead for unclassified operating expenses
        return "overhead"

    def calculate_break_even(
        self,
        total_overhead: float,
        gross_margin_pct: float
    ) -> Dict:
        """
        Calculate break-even revenue at various margin levels

        Break-even = Fixed Overhead / Gross Margin %
        """
        if gross_margin_pct <= 0:
            return {
                "current_margin": {
                    "monthly": 0,
                    "annual": 0,
                    "gross_margin": gross_margin_pct
                },
                "scenarios": {},
                "error": "Gross margin must be positive"
            }

        # Calculate months in period (assume 12 for TTM)
        monthly_overhead = total_overhead / 12
        monthly_break_even = monthly_overhead / gross_margin_pct

        # Calculate scenarios at different margins
        scenarios = {}
        for margin in [0.20, 0.25, 0.28, 0.30, 0.35, 0.40]:
            monthly_be = monthly_overhead / margin
            scenarios[f"{int(margin * 100)}%"] = {
                "gross_margin": margin,
                "monthly_break_even": round(monthly_be, 2),
                "annual_break_even": round(monthly_be * 12, 2),
                "is_current": abs(margin - gross_margin_pct) < 0.025
            }

        return {
            "current_margin": {
                "gross_margin": round(gross_margin_pct, 4),
                "monthly_break_even": round(monthly_break_even, 2),
                "annual_break_even": round(monthly_break_even * 12, 2)
            },
            "monthly_overhead": round(monthly_overhead, 2),
            "scenarios": scenarios
        }

    def calculate_ebitda_sde(
        self,
        net_income: float,
        interest: float = 0,
        taxes: float = 0,
        depreciation: float = 0,
        amortization: float = 0,
        owner_compensation: float = 0,
        owner_benefits: float = 0,
        non_recurring: float = 0
    ) -> Dict:
        """
        Calculate EBITDA and SDE for valuation purposes

        EBITDA = Net Income + Interest + Taxes + Depreciation + Amortization
        SDE = EBITDA + Owner Compensation + Owner Benefits + Non-recurring Expenses

        For roofing contractors:
        - Typical multiples: 2.5-4.5x SDE for small ($1-3M), 3.5-5.5x for mid-market
        - Key value drivers: recurring revenue, management depth, growth rate
        """
        # Calculate EBITDA
        ebitda = net_income + interest + taxes + depreciation + amortization

        # Calculate SDE (adds back owner's salary/benefits)
        sde = ebitda + owner_compensation + owner_benefits + non_recurring

        # Determine multiple range based on SDE level
        if sde < 100_000:
            multiple_range = (1.5, 2.5)
        elif sde < 250_000:
            multiple_range = (2.0, 3.5)
        elif sde < 500_000:
            multiple_range = (2.5, 4.0)
        elif sde < 1_000_000:
            multiple_range = (3.0, 4.5)
        else:
            multiple_range = (3.5, 5.5)

        # Calculate value range
        value_low = sde * multiple_range[0]
        value_high = sde * multiple_range[1]

        return {
            "ebitda": round(ebitda, 2),
            "sde": round(sde, 2),
            "add_backs": {
                "interest": interest,
                "taxes": taxes,
                "depreciation": depreciation,
                "amortization": amortization,
                "owner_compensation": owner_compensation,
                "owner_benefits": owner_benefits,
                "non_recurring": non_recurring
            },
            "valuation": {
                "multiple_range": multiple_range,
                "value_range": {
                    "low": round(value_low, 0),
                    "high": round(value_high, 0),
                    "midpoint": round((value_low + value_high) / 2, 0)
                }
            }
        }

    def detect_profit_leaks(
        self,
        pnl_data: Dict,
        revenue: float
    ) -> List[Dict]:
        """
        Identify profit leaks by comparing expense ratios to benchmarks

        Returns list of issues with severity and recommendations
        """
        profit_leaks = []
        overhead_items = pnl_data.get("overhead_items", {})

        # Check overall overhead ratio
        total_overhead = sum(overhead_items.values())
        overhead_ratio = total_overhead / revenue if revenue > 0 else 0

        benchmark = self.benchmarks["overhead_ratio"]
        if overhead_ratio > benchmark["critical"]:
            profit_leaks.append({
                "category": "overhead",
                "severity": "critical",
                "issue": f"Total overhead is {overhead_ratio:.1%} of revenue (target: <{benchmark['healthy']:.0%})",
                "current_value": round(total_overhead, 2),
                "current_ratio": round(overhead_ratio, 4),
                "target_ratio": benchmark["healthy"],
                "potential_savings": round(total_overhead - (revenue * benchmark["healthy"]), 2),
                "recommendation": "Review all overhead expenses for cost reduction opportunities"
            })
        elif overhead_ratio > benchmark["warning"]:
            profit_leaks.append({
                "category": "overhead",
                "severity": "warning",
                "issue": f"Overhead ratio at {overhead_ratio:.1%} approaching critical threshold",
                "current_value": round(total_overhead, 2),
                "current_ratio": round(overhead_ratio, 4),
                "target_ratio": benchmark["healthy"],
                "potential_savings": round(total_overhead - (revenue * benchmark["healthy"]), 2),
                "recommendation": "Monitor overhead costs and look for efficiency gains"
            })

        # Check specific expense categories
        for account, amount in overhead_items.items():
            ratio = amount / revenue if revenue > 0 else 0
            account_lower = account.lower()

            # Marketing spend check
            if any(kw in account_lower for kw in ["marketing", "advertising"]):
                benchmark = self.benchmarks["marketing_ratio"]
                if ratio > benchmark["critical"]:
                    profit_leaks.append({
                        "category": "marketing",
                        "account": account,
                        "severity": "critical",
                        "issue": f"Marketing spend is {ratio:.1%} of revenue (target: <{benchmark['healthy']:.0%})",
                        "current_value": round(amount, 2),
                        "current_ratio": round(ratio, 4),
                        "potential_savings": round(amount - (revenue * benchmark["healthy"]), 2),
                        "recommendation": "Analyze marketing ROI and cut underperforming channels"
                    })
                elif ratio > benchmark["warning"]:
                    profit_leaks.append({
                        "category": "marketing",
                        "account": account,
                        "severity": "warning",
                        "issue": f"Marketing spend at {ratio:.1%} is above industry average",
                        "current_value": round(amount, 2),
                        "current_ratio": round(ratio, 4),
                        "recommendation": "Track marketing ROI by channel"
                    })

            # Phone/communication check (common issue)
            if any(kw in account_lower for kw in ["phone", "telephone", "communication"]):
                if ratio > 0.02:  # More than 2% on phone is unusual
                    profit_leaks.append({
                        "category": "communications",
                        "account": account,
                        "severity": "warning",
                        "issue": f"Communication costs at {ratio:.1%} seem high",
                        "current_value": round(amount, 2),
                        "current_ratio": round(ratio, 4),
                        "recommendation": "Review phone plans and consolidate services"
                    })

            # Contract labor check
            if any(kw in account_lower for kw in ["contract labor", "contractor"]):
                if ratio > 0.15:  # High contractor spend may indicate staffing issues
                    profit_leaks.append({
                        "category": "labor",
                        "account": account,
                        "severity": "info",
                        "issue": f"Contract labor at {ratio:.1%} - evaluate hiring vs contracting",
                        "current_value": round(amount, 2),
                        "current_ratio": round(ratio, 4),
                        "recommendation": "Consider converting frequent contractors to employees for cost savings"
                    })

        # Sort by severity
        severity_order = {"critical": 0, "warning": 1, "info": 2}
        profit_leaks.sort(key=lambda x: severity_order.get(x["severity"], 3))

        return profit_leaks

    def get_health_status(self, ratio: float, benchmark_key: str) -> str:
        """Get health status based on benchmark comparison"""
        benchmark = self.benchmarks.get(benchmark_key, {})

        if ratio >= benchmark.get("healthy", 0):
            return "healthy"
        elif ratio >= benchmark.get("warning", 0):
            return "warning"
        else:
            return "critical"

    def analyze_pnl(self, report_data: Dict) -> Dict:
        """
        Main analysis function - takes raw P&L report and returns full analytics

        Args:
            report_data: Raw P&L report from QuickBooks MCP tool

        Returns:
            Complete P&L analytics with all metrics
        """
        # Parse the report
        parsed = self.parse_pnl_report(report_data)
        summary = parsed["summary"]

        # Core figures
        revenue = summary["total_income"]
        cogs = summary["total_cogs"]
        gross_profit = summary["gross_profit"]
        expenses = summary["total_expenses"]
        net_income = summary["net_income"]

        # Calculate margins
        gross_margin = gross_profit / revenue if revenue > 0 else 0
        net_margin = net_income / revenue if revenue > 0 else 0

        # Calculate overhead
        total_overhead = sum(parsed["overhead_items"].values())
        overhead_ratio = total_overhead / revenue if revenue > 0 else 0

        # Monthly figures (assume TTM = 12 months)
        monthly_revenue = revenue / 12
        monthly_overhead = total_overhead / 12

        # Break-even analysis
        break_even = self.calculate_break_even(total_overhead, gross_margin)

        # EBITDA/SDE calculation
        # Extract add-backs from expense items
        interest = 0
        depreciation = 0
        for key, value in parsed["raw_metrics"].items():
            if not isinstance(value, (int, float)):
                continue
            key_lower = key.lower()
            if "interest" in key_lower:
                interest += abs(float(value))
            if "depreciation" in key_lower or "amortization" in key_lower:
                depreciation += abs(float(value))

        ebitda_sde = self.calculate_ebitda_sde(
            net_income=net_income,
            interest=interest,
            depreciation=depreciation,
            # Owner comp would need to be provided separately
            owner_compensation=0
        )

        # Profit leak detection
        profit_leaks = self.detect_profit_leaks(parsed, revenue)

        # Health statuses
        gross_margin_status = self.get_health_status(gross_margin, "gross_margin")
        net_margin_status = self.get_health_status(net_margin, "net_margin")
        # For overhead, lower is better so invert logic
        if overhead_ratio <= self.benchmarks["overhead_ratio"]["healthy"]:
            overhead_status = "healthy"
        elif overhead_ratio <= self.benchmarks["overhead_ratio"]["warning"]:
            overhead_status = "warning"
        else:
            overhead_status = "critical"

        return {
            "period": parsed["period"],

            "summary": {
                "total_revenue": round(revenue, 2),
                "total_cogs": round(cogs, 2),
                "gross_profit": round(gross_profit, 2),
                "gross_margin_pct": round(gross_margin * 100, 1),
                "total_expenses": round(expenses, 2),
                "net_income": round(net_income, 2),
                "net_margin_pct": round(net_margin * 100, 1)
            },

            "monthly": {
                "revenue": round(monthly_revenue, 2),
                "overhead": round(monthly_overhead, 2),
                "net_income": round(net_income / 12, 2)
            },

            "break_even": break_even,

            "ebitda_sde": ebitda_sde,

            "health": {
                "gross_margin": {
                    "status": gross_margin_status,
                    "value": round(gross_margin * 100, 1),
                    "benchmark": self.benchmarks["gross_margin"]["healthy"] * 100
                },
                "net_margin": {
                    "status": net_margin_status,
                    "value": round(net_margin * 100, 1),
                    "benchmark": self.benchmarks["net_margin"]["healthy"] * 100
                },
                "overhead": {
                    "status": overhead_status,
                    "value": round(overhead_ratio * 100, 1),
                    "benchmark": self.benchmarks["overhead_ratio"]["healthy"] * 100
                }
            },

            "expense_breakdown": {
                "overhead": {
                    "total": round(total_overhead, 2),
                    "items": {k: round(v, 2) for k, v in sorted(
                        parsed["overhead_items"].items(),
                        key=lambda x: -x[1]
                    )}
                },
                "cogs": {
                    "total": round(cogs, 2),
                    "items": {k: round(v, 2) for k, v in sorted(
                        parsed["cogs_items"].items(),
                        key=lambda x: -x[1]
                    )}
                }
            },

            "profit_leaks": profit_leaks,

            "recommendations": self._generate_recommendations(
                gross_margin_status,
                net_margin_status,
                overhead_status,
                profit_leaks
            )
        }

    def _generate_recommendations(
        self,
        gross_margin_status: str,
        net_margin_status: str,
        overhead_status: str,
        profit_leaks: List[Dict]
    ) -> List[Dict]:
        """Generate prioritized recommendations based on analysis"""
        recommendations = []
        priority = 1

        if gross_margin_status == "critical":
            recommendations.append({
                "priority": priority,
                "category": "pricing",
                "title": "Review Pricing Strategy",
                "description": "Gross margin is below industry standard. Consider raising prices or reducing direct costs.",
                "impact": "high"
            })
            priority += 1

        if overhead_status == "critical":
            recommendations.append({
                "priority": priority,
                "category": "overhead",
                "title": "Reduce Overhead Expenses",
                "description": "Overhead is too high relative to revenue. Review all fixed costs for savings opportunities.",
                "impact": "high"
            })
            priority += 1

        if net_margin_status == "critical":
            recommendations.append({
                "priority": priority,
                "category": "profitability",
                "title": "Improve Overall Profitability",
                "description": "Net margin is critically low. Focus on both revenue growth and cost reduction.",
                "impact": "high"
            })
            priority += 1

        # Add recommendations from profit leaks
        for leak in profit_leaks[:3]:  # Top 3 issues
            if leak["severity"] == "critical":
                recommendations.append({
                    "priority": priority,
                    "category": leak["category"],
                    "title": f"Address {leak['category'].title()} Costs",
                    "description": leak.get("recommendation", leak["issue"]),
                    "potential_savings": leak.get("potential_savings"),
                    "impact": "high" if leak["severity"] == "critical" else "medium"
                })
                priority += 1

        return recommendations[:5]  # Top 5 recommendations


# Convenience function for use in API endpoints
def analyze_quickbooks_pnl(pnl_report: Dict) -> Dict:
    """
    Analyze a QuickBooks P&L report and return full analytics

    Args:
        pnl_report: Raw report from mcp__quickbooks__report_profit_and_loss

    Returns:
        Complete analytics dictionary
    """
    service = PnLAnalyticsService()
    return service.analyze_pnl(pnl_report)
