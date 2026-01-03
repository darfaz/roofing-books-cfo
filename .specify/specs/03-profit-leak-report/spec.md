# Profit Leak Report Specification

> **Feature**: 03-profit-leak-report
> **Status**: Implemented
> **Priority**: P0 (Core)
> **Last Updated**: 2026-01-02

---

## Overview

The Profit Leak Report analyzes expense patterns to identify where margin is being lost, provides break-even analysis, and benchmarks against roofing industry standards.

**Target User**: Owner, bookkeeper, fractional CFO
**Access Frequency**: Monthly
**Key Question Answered**: "Where is my profit leaking and what should I fix?"

---

## User Stories

### US-01: See Break-Even Point
**As a** roofing contractor owner
**I want to** know my monthly break-even revenue
**So that** I understand the minimum I need to survive

**Acceptance Criteria**:
- [ ] Display monthly break-even revenue prominently
- [ ] Show calculation: Fixed Overhead / Gross Margin %
- [ ] Display scenario table at different margin levels (15%, 20%, 25%, 30%, 35%)
- [ ] Highlight current margin scenario
- [ ] Show annual break-even extrapolation

### US-02: View Overhead Breakdown
**As a** roofing contractor owner
**I want to** see my overhead costs by category
**So that** I can identify opportunities to reduce fixed costs

**Acceptance Criteria**:
- [ ] Display total overhead with monthly average
- [ ] Break down by category: Payroll, Insurance, Office, Professional Fees, Marketing, Utilities, Depreciation, Other
- [ ] Show percentage of total for each category
- [ ] Display transaction count for data quality
- [ ] Enable drill-down to see transactions

### US-03: View Job Cost Breakdown
**As a** roofing contractor owner
**I want to** see my job costs (COGS) by category
**So that** I can identify opportunities to improve job margins

**Acceptance Criteria**:
- [ ] Display total job costs with monthly average
- [ ] Break down by category: Materials, Direct Labor, Equipment, Subcontractors, Disposal, Permits, Other
- [ ] Show percentage of total for each category
- [ ] Compare to revenue for gross margin

### US-04: Identify Profit Leaks
**As a** roofing contractor owner
**I want to** see specific profit leaks identified by the system
**So that** I can prioritize improvements

**Acceptance Criteria**:
- [ ] List profit leaks with severity (high/medium/low)
- [ ] For each leak show:
  - Category (e.g., "Gross Margin", "Labor Ratio")
  - Issue description
  - Current ratio vs benchmark
  - Impact description
  - Recommendation
- [ ] Sort by severity
- [ ] Color-code by severity

### US-05: See Health Status
**As a** roofing contractor owner
**I want to** see an overall health assessment
**So that** I know if I'm in good shape or need urgent attention

**Acceptance Criteria**:
- [ ] Status: Healthy (green), Needs Attention (yellow), Critical (red)
- [ ] Based on gross margin:
  - Healthy: >25%
  - Needs Attention: 15-25%
  - Critical: <15%
- [ ] Show status icon and description

---

## Roofing Industry Benchmarks

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Gross Margin | ≥35% | 28-35% | <28% |
| Net Margin | ≥10% | 5-10% | <5% |
| Overhead Ratio | ≤20% | 20-28% | >28% |
| Labor Ratio | ≤30% | 30-40% | >40% |
| Marketing Ratio | ≤5% | 5-8% | >8% |

---

## Data Model

### Overhead Analysis
```typescript
interface OverheadAnalysis {
  period: {
    start: string
    end: string
    months: number
  }
  overhead: {
    total: number
    monthly_average: number
    by_category: Record<string, number>
    monthly_trend: Record<string, Record<string, number>>
    transaction_count: number
  }
  job_costs: {
    total: number
    monthly_average: number
    by_category: Record<string, number>
    transaction_count: number
  }
  revenue: {
    total: number
    monthly_average: number
  }
  profitability: {
    gross_margin: number
    gross_margin_pct: string
    gross_profit_monthly: number
  }
  break_even: {
    current_margin: {
      margin: number
      monthly: number
      annual: number
    }
    scenarios: Record<string, {
      margin: number
      monthly_break_even: number
      annual_break_even: number
    }>
  }
  mixed_expenses: {
    total: number
    count: number
    note: string
  }
  confidence: {
    overhead_avg: number
    job_cost_avg: number
  }
}
```

### Profit Leak
```typescript
interface ProfitLeak {
  category: string
  issue: string
  current_ratio: number
  benchmark: number
  impact: string
  severity: 'high' | 'medium' | 'low'
  recommendation: string
}
```

---

## Expense Categories

### Overhead Categories
| Key | Label | Icon | Examples |
|-----|-------|------|----------|
| payroll | Payroll & Taxes | 💵 | Office staff wages, employer taxes |
| insurance | Insurance | 🛡️ | GL, WC, auto, umbrella |
| office | Office & Admin | 🏢 | Rent, supplies, software |
| professional_fees | Professional Fees | 👔 | Legal, accounting, consulting |
| marketing | Marketing & Advertising | 📢 | Ads, website, signage |
| utilities | Utilities | ⚡ | Electric, gas, phone, internet |
| depreciation | Depreciation | 📉 | Equipment, vehicle depreciation |
| other_overhead | Other Overhead | 📋 | Miscellaneous |

### Job Cost Categories
| Key | Label | Icon | Examples |
|-----|-------|------|----------|
| materials | Materials & Supplies | 🧱 | Shingles, underlayment, flashing |
| direct_labor | Direct Labor | 👷 | Crew wages for jobs |
| equipment | Equipment Rental | 🚜 | Lifts, tools |
| subcontractors | Subcontractors | 🤝 | Specialty subs |
| disposal | Disposal & Hauling | 🚛 | Dumpsters, debris removal |
| permits | Permits & Inspections | 📜 | Building permits, inspections |
| other_job_cost | Other Job Costs | 🔧 | Miscellaneous |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analytics/pnl` | GET | Full P&L analysis with all metrics |
| `/api/analytics/break-even` | GET | Break-even analysis |
| `/api/analytics/profit-leaks` | GET | Detected profit leaks |
| `/api/qbo/overhead/summary` | GET | Overhead breakdown |
| `/api/qbo/expenses/classified` | GET | Expenses by classification |

---

## UI Components

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│  STOP THE PROFIT LEAKS                         [HEALTHY ✅] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  MONTHLY BREAK-EVEN POINT                                   │
│                                                             │
│              $206,818                                       │
│   in revenue to cover overhead at 22% margin                │
│                                                             │
│  ┌─────────┬─────────┬─────────┬─────────┐                │
│  │ Overhead│ Job Cost│ Margin  │ Revenue │                │
│  │ $45,500 │ $227,500│  22%    │ $291,667│                │
│  └─────────┴─────────┴─────────┴─────────┘                │
├─────────────────────────────────────────────────────────────┤
│  🎯 BREAK-EVEN SCENARIOS                        [Expand ▼] │
│  15%: $303K | 20%: $228K | [25%: $182K] | 30%: $152K      │
├─────────────────────────────────────────────────────────────┤
│  🏢 OVERHEAD BREAKDOWN ($546K)                  [Expand ▼] │
│  └─ Payroll $216K (40%) | Insurance $84K (15%) | ...       │
├─────────────────────────────────────────────────────────────┤
│  🔧 JOB COST BREAKDOWN ($2.73M)                [Expand ▼] │
│  └─ Materials $1.23M (45%) | Labor $630K (23%) | ...       │
├─────────────────────────────────────────────────────────────┤
│  🚨 PROFIT LEAKS DETECTED (2 issues)           [Expand ▼] │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 🔴 HIGH: Gross Margin                                 │ │
│  │ Current: 22% | Benchmark: 35% | Impact: 13% below    │ │
│  │ 💡 Review pricing strategy and job costing           │ │
│  ├───────────────────────────────────────────────────────┤ │
│  │ 🟢 LOW: Marketing Spend                              │ │
│  │ Current: 1.7% | Benchmark: 5% | Within range         │ │
│  │ 💡 Monitor ROI on marketing channels                 │ │
│  └───────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  CONFIDENCE: Overhead 85% | Job Cost 92%                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Break-Even Calculation

```
Break-Even Revenue = Monthly Overhead / Gross Margin %

Example:
- Monthly Overhead: $45,500
- Gross Margin: 22%
- Break-Even: $45,500 / 0.22 = $206,818/month
```

---

## Profit Leak Detection Logic

For each benchmark metric:
1. Calculate current ratio from P&L data
2. Compare to healthy benchmark
3. If exceeds warning threshold, flag as medium severity
4. If exceeds critical threshold, flag as high severity
5. Generate recommendation based on category

```python
def detect_profit_leaks(pnl_data, revenue):
    leaks = []

    # Gross Margin Check
    gross_margin = pnl_data.gross_margin
    if gross_margin < BENCHMARKS['gross_margin']['critical']:
        leaks.append({
            'category': 'Gross Margin',
            'severity': 'high',
            'current_ratio': gross_margin,
            'benchmark': BENCHMARKS['gross_margin']['healthy'],
            'recommendation': 'Review pricing and job costing'
        })

    # Labor Ratio Check
    labor_ratio = pnl_data.labor_costs / revenue
    if labor_ratio > BENCHMARKS['labor_ratio']['critical']:
        leaks.append({
            'category': 'Labor Costs',
            'severity': 'high',
            # ...
        })

    return leaks
```

---

## Review Checklist

- [ ] Break-even calculation matches manual Excel verification
- [ ] All overhead categories are mapped correctly from QBO
- [ ] Job costs exclude overhead expenses
- [ ] Benchmarks are appropriate for roofing industry
- [ ] Profit leak recommendations are actionable
- [ ] Demo mode shows realistic $3.5M contractor data
