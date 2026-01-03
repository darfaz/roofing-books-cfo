# Owner Dashboard Specification

> **Feature**: 01-owner-dashboard
> **Status**: Implemented
> **Priority**: P0 (Core)
> **Last Updated**: 2026-01-02

---

## Overview

The Owner Dashboard is the primary operations view for roofing contractors, providing at-a-glance visibility into cash position, revenue progress, receivables aging, active jobs, and a 13-week cash forecast.

**Target User**: Roofing business owner/operator
**Access Frequency**: Daily to weekly
**Key Question Answered**: "How is my business doing right now?"

---

## User Stories

### US-01: View Cash Position
**As a** roofing contractor owner
**I want to** see my current cash position and runway
**So that** I know how long I can operate before needing to collect receivables or slow spending

**Acceptance Criteria**:
- [ ] Display total cash balance
- [ ] Show runway in weeks (cash / weekly burn)
- [ ] Show week-over-week change percentage
- [ ] Color-code based on health (green >8 weeks, yellow 4-8, red <4)

### US-02: Track Revenue Progress
**As a** roofing contractor owner
**I want to** see my month-to-date revenue vs target
**So that** I know if I'm on track to hit my monthly goals

**Acceptance Criteria**:
- [ ] Display MTD revenue amount
- [ ] Show monthly target
- [ ] Display progress percentage with visual bar
- [ ] Indicate days remaining in month

### US-03: Monitor AR Aging
**As a** roofing contractor owner
**I want to** see my accounts receivable by aging bucket
**So that** I can prioritize collections and identify problem customers

**Acceptance Criteria**:
- [ ] Display AR in buckets: Current, 1-30, 31-60, 61-90, 90+
- [ ] Show total AR amount
- [ ] Highlight overdue amounts (31+ days)
- [ ] Calculate overdue percentage

### US-04: View Active Jobs
**As a** roofing contractor owner
**I want to** see my active jobs with revenue and margins
**So that** I can monitor job performance and identify issues early

**Acceptance Criteria**:
- [ ] List active jobs with name, revenue, margin %, status
- [ ] Sort by revenue descending
- [ ] Color-code margins (green >30%, yellow 20-30%, red <20%)
- [ ] Show job status (scheduled, in_progress, completed)

### US-05: See Cash Forecast
**As a** roofing contractor owner
**I want to** see a 13-week cash forecast with scenarios
**So that** I can anticipate cash crunches and plan accordingly

**Acceptance Criteria**:
- [ ] Display 13-week rolling forecast
- [ ] Show base, optimistic, and pessimistic scenarios
- [ ] Visualize with area chart
- [ ] Highlight minimum cash point
- [ ] Show runway weeks

### US-06: View Backlog
**As a** roofing contractor owner
**I want to** see my job backlog
**So that** I understand my pipeline and crew capacity needs

**Acceptance Criteria**:
- [ ] Show total backlog amount
- [ ] Display count of pending jobs
- [ ] Calculate backlog runway (backlog / avg monthly revenue)

---

## Data Model

### Inputs
```typescript
interface CashPosition {
  total_cash: number
  runway_weeks: number
  change_wow: number  // Week-over-week percentage change
}

interface Revenue {
  mtd: number
  target: number
  progress: number  // 0-1
}

interface ARBucket {
  current: number
  '1-30': number
  '31-60': number
  '61-90': number
  '90+': number
}

interface Job {
  name: string
  revenue: number
  margin: number  // 0-1
  status: 'scheduled' | 'in_progress' | 'completed'
}

interface ForecastWeek {
  week_start_date: string
  ending_cash: number
  optimistic_cash: number
  pessimistic_cash: number
}

interface Backlog {
  amount: number
  jobs: number
}
```

### Data Sources
- **Cash Position**: Calculated from `transactions` table (deposits - withdrawals)
- **Revenue**: Aggregated from `transactions` where `qbo_type = 'Invoice'` for current month
- **AR Aging**: Unpaid invoices grouped by days since invoice date
- **Jobs**: From field service integration (Jobber/ServiceTitan) or manual entry
- **Forecast**: Calculated by `CashFlowForecastService`

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/cash/position` | GET | Returns cash position and runway |
| `/api/cash/forecast` | GET | Returns 13-week forecast array |
| `/api/ar/aging` | GET | Returns AR aging buckets |
| `/api/jobs/active` | GET | Returns active jobs list |
| `/api/jobs/backlog` | GET | Returns backlog summary |

---

## UI Components

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│  OWNER DASHBOARD                              [Demo Mode]   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ Cash        │ │ Revenue MTD │ │ Backlog     │           │
│  │ $187,500    │ │ $292K/$320K │ │ $485K       │           │
│  │ 14 wk runway│ │ 91% to goal │ │ 12 jobs     │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│  AR AGING                                                   │
│  ┌─────┬─────┬─────┬─────┬─────┐                          │
│  │Curr │1-30 │31-60│61-90│ 90+ │                          │
│  │$125K│$68K │$32K │$18K │$8.5K│                          │
│  └─────┴─────┴─────┴─────┴─────┘                          │
├─────────────────────────────────────────────────────────────┤
│  13-WEEK CASH FORECAST                                      │
│  [Area Chart: Base / Optimistic / Pessimistic]             │
├─────────────────────────────────────────────────────────────┤
│  ACTIVE JOBS                                                │
│  ┌────────────────────────┬─────────┬────────┬────────┐    │
│  │ Job Name               │ Revenue │ Margin │ Status │    │
│  ├────────────────────────┼─────────┼────────┼────────┤    │
│  │ Henderson Commercial   │ $85,000 │  34%   │ Active │    │
│  │ Oakwood HOA Phase 2    │ $125,000│  31%   │ Active │    │
│  │ Martinez Insurance     │ $28,500 │  42%   │ Done   │    │
│  └────────────────────────┴─────────┴────────┴────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Component Tree
```
OwnerDashboard
├── MetricCard (Cash Position)
├── MetricCard (Revenue Progress)
├── MetricCard (Backlog)
├── ARAgingChart
├── CashForecastChart
└── JobsTable
```

---

## Demo Mode

When `isDemoMode = true`, display hardcoded data for **Apex Roofing Solutions**:

```typescript
const DEMO_DATA = {
  cash: { total_cash: 187500, runway_weeks: 14, change_wow: 0.12 },
  revenue: { mtd: 292000, target: 320000, progress: 0.9125 },
  arAging: { current: 125000, '1-30': 68000, '31-60': 32000, '61-90': 18000, '90+': 8500 },
  backlog: { amount: 485000, jobs: 12 },
  jobs: [
    { name: 'Henderson Commercial Plaza', revenue: 85000, margin: 0.34, status: 'in_progress' },
    { name: 'Oakwood HOA - Phase 2', revenue: 125000, margin: 0.31, status: 'in_progress' },
    // ...more jobs
  ]
}
```

---

## Error Handling

| Error | User Message | Recovery Action |
|-------|--------------|-----------------|
| No QBO connected | "Connect QuickBooks to see your real data" | Show connect button |
| No transactions | "No data yet. Sync will start after QuickBooks connects" | Show loading state |
| API timeout | "Having trouble loading data. Trying again..." | Auto-retry 3x |
| Auth expired | "Session expired. Please log in again" | Redirect to login |

---

## Review Checklist

- [ ] Cash position updates within 4 hours of QBO sync
- [ ] AR aging buckets calculate correctly from invoice dates
- [ ] Forecast scenarios show meaningful variance
- [ ] Demo mode data is realistic for $3.5M contractor
- [ ] Mobile responsive layout works on tablet
- [ ] Performance: <3s initial load
