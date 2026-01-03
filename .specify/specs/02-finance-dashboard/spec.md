# Finance Dashboard Specification

> **Feature**: 02-finance-dashboard
> **Status**: Implemented
> **Priority**: P0 (Core)
> **Last Updated**: 2026-01-02

---

## Overview

The Finance Dashboard provides CFO-level financial analytics including 13-week cash forecasting with multiple scenarios, AP aging, budget variance analysis, and cash health alerts.

**Target User**: Owner (CFO hat), bookkeeper, fractional CFO
**Access Frequency**: Weekly
**Key Question Answered**: "What's my cash position going to look like, and am I on budget?"

---

## User Stories

### US-01: View Cash Forecast with Scenarios
**As a** roofing contractor owner
**I want to** see 13-week cash projections with base, optimistic, and pessimistic scenarios
**So that** I can plan for different business conditions

**Acceptance Criteria**:
- [ ] Display 13-week rolling forecast starting from current week
- [ ] Show three scenarios: Base (expected), Optimistic (+20%), Pessimistic (-25%)
- [ ] Visualize with stacked area chart
- [ ] Show weekly inflows (collections) and outflows (AP, payroll, recurring)
- [ ] Highlight minimum cash point and which week it occurs
- [ ] Calculate runway in weeks for each scenario

### US-02: Receive Cash Alerts
**As a** roofing contractor owner
**I want to** receive alerts when cash position is concerning
**So that** I can take action before a cash crunch

**Acceptance Criteria**:
- [ ] Alert status: Healthy (>12 weeks), Good (8-12 weeks), Caution (4-8 weeks), Critical (<4 weeks)
- [ ] Display contextual message explaining the situation
- [ ] Provide specific recommendations (e.g., "Accelerate collections on $32K 60+ day AR")
- [ ] Color-code alert banner (green/yellow/orange/red)

### US-03: View AP Aging
**As a** roofing contractor owner
**I want to** see my accounts payable by aging and due date
**So that** I can prioritize payments and manage vendor relationships

**Acceptance Criteria**:
- [ ] Display AP in buckets: Current, 1-30 overdue, 31-60 overdue, 61-90 overdue, 90+ overdue
- [ ] Show total AP amount
- [ ] List upcoming payments for next 30 days
- [ ] Group by vendor with top vendors highlighted

### US-04: Track Budget Variance
**As a** roofing contractor owner
**I want to** see my actual spending vs budget by category
**So that** I can control costs and stay on track

**Acceptance Criteria**:
- [ ] Display budget vs actual by expense category
- [ ] Calculate variance in $ and %
- [ ] Color-code: Under budget (green), On track ±5% (gray), Over budget (red)
- [ ] Show YTD totals
- [ ] Highlight categories significantly over budget

### US-05: View Weekly Cash Detail
**As a** roofing contractor owner
**I want to** drill into each forecast week
**So that** I can understand the drivers of cash flow

**Acceptance Criteria**:
- [ ] Expandable week detail showing:
  - Starting cash
  - Inflows breakdown (collections by AR bucket)
  - Outflows breakdown (AP payments, payroll, recurring)
  - Ending cash
- [ ] Net cash flow for the week
- [ ] Comparison to previous week

---

## Data Model

### Cash Forecast
```typescript
interface CashForecast {
  forecast_date: string
  scenario: 'base' | 'optimistic' | 'pessimistic'
  starting_cash: number
  ending_cash: number
  min_cash: number
  min_cash_week: number
  runway_weeks: number
  ar_total: number
  ap_total: number
  summary: {
    total_inflows: number
    total_outflows: number
    net_change: number
  }
  weekly_forecast: WeeklyForecast[]
}

interface WeeklyForecast {
  week_number: number
  week_start: string
  week_end: string
  starting_cash: number
  ending_cash: number
  net_cash_flow: number
  inflows: {
    collections: number
    total: number
  }
  outflows: {
    ap_payments: number
    recurring_expenses: number
    total: number
  }
}
```

### Cash Alert
```typescript
interface CashAlertStatus {
  status: 'healthy' | 'good' | 'caution' | 'critical'
  color: 'green' | 'yellow' | 'red'
  message: string
  runway_weeks: number
  current_cash: number
  min_projected_cash: number
  min_cash_week: number
  recommendations: string[]
}
```

### Budget Variance
```typescript
interface BudgetVariance {
  period: string  // 'YYYY-MM'
  categories: {
    category: string
    budget: number
    actual: number
    variance: number
    variance_pct: number
    status: 'under' | 'over' | 'on_track'
  }[]
  totals: {
    budget: number
    actual: number
    variance: number
    variance_pct: number
  }
}
```

---

## Collection Rate Assumptions

The forecast uses these collection rate assumptions by AR aging bucket:

| Bucket | Week 1 | Week 2 | Week 3 | Week 4 | Later |
|--------|--------|--------|--------|--------|-------|
| Current | 15% | 30% | 25% | 20% | 10% |
| 1-30 days | 25% | 35% | 25% | - | 15% |
| 31-60 days | 30% | 30% | 20% | - | 20% |
| 61-90 days | 20% | 20% | - | - | 60% |
| 90+ days | 10% | - | - | - | 90% |

---

## Scenario Multipliers

| Scenario | Collections | Expenses | Description |
|----------|-------------|----------|-------------|
| Base | 1.0x | 1.0x | Expected case |
| Optimistic | 1.2x | 0.9x | Strong collections, controlled spending |
| Pessimistic | 0.75x | 1.1x | Slow collections, higher costs |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/finance/cash-forecast` | GET | Returns forecast for specified scenario |
| `/api/finance/cash-forecast/all-scenarios` | GET | Returns all three scenarios |
| `/api/finance/cash-forecast/alert` | GET | Returns cash alert status |
| `/api/finance/ap/aging` | GET | Returns AP aging buckets |
| `/api/finance/ap/upcoming` | GET | Returns upcoming AP payments |
| `/api/finance/ap/by-vendor` | GET | Returns AP grouped by vendor |
| `/api/finance/budget/variance` | GET | Returns budget vs actual |
| `/api/finance/budget/ytd` | GET | Returns YTD budget variance |

---

## UI Components

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│  FINANCE DASHBOARD                                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │ CASH ALERT: HEALTHY                                  │   │
│  │ 14-week runway | $187,500 cash | Min $142K week 6   │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  13-WEEK CASH FORECAST                                      │
│  [Scenario Toggle: Base | Optimistic | Pessimistic]        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                       │   │
│  │     [Stacked Area Chart]                             │   │
│  │     - Collections (blue)                             │   │
│  │     - AP Payments (red)                              │   │
│  │     - Net Position (line)                            │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  AP AGING                    │  BUDGET VARIANCE            │
│  ┌──────────────────────┐    │  ┌──────────────────────┐  │
│  │ Current    $45,000   │    │  │ Revenue   +$15K (5%)│  │
│  │ 1-30       $22,000   │    │  │ Materials -$8K (3%)│  │
│  │ 31-60      $8,500    │    │  │ Labor     -$12K (8%)│  │
│  │ 61-90      $3,200    │    │  │ Overhead  +$2K (2%) │  │
│  │ 90+        $1,500    │    │  └──────────────────────┘  │
│  └──────────────────────┘    │                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Error Handling

| Error | User Message | Recovery |
|-------|--------------|----------|
| Insufficient data | "Need at least 30 days of history for accurate forecasting" | Show partial forecast with disclaimer |
| No budget set | "No budget configured. Set a budget to see variance" | Link to budget setup |
| Stale data | "Data last synced 6 hours ago" | Show sync button |

---

## Review Checklist

- [ ] Forecast updates automatically on QBO sync
- [ ] All three scenarios calculate correctly
- [ ] Alert thresholds are appropriate for roofing seasonality
- [ ] Budget variance categories match Chart of Accounts
- [ ] AP aging matches QBO AP aging report
- [ ] Performance: <3s load with 1000+ transactions
