# <!-- filename: /dashboards/owner/owner_dashboard.md -->
# Owner Command Center Dashboard

## Overview

The Owner Command Center is designed to answer one primary question: **"Am I okay?"**

This dashboard provides a roofing contractor owner with a 5-second health check and drill-down capabilities for when they need to understand what's happening in their business.

---

## Design Philosophy

### Narrative Goals

| Question | Answer Location | Time to Answer |
|----------|-----------------|----------------|
| "Am I okay?" | Top status banner | 2 seconds |
| "Do I have enough cash?" | Cash widget | 3 seconds |
| "How's this month going?" | Revenue widget | 5 seconds |
| "What needs my attention?" | Action items panel | 10 seconds |
| "Are my jobs profitable?" | Margin heatmap | 15 seconds |

### Design Principles

1. **Glanceable** - Most important info visible without scrolling
2. **Narrative-first** - Numbers tell a story, not just data
3. **Actionable** - Every metric leads to an action
4. **Calm Technology** - Alerts only when attention is truly needed
5. **Mobile-first** - Works on phone while on job sites

---

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                    OVERALL HEALTH BANNER                        │
│  [🟢 Looking Good] [🟡 Needs Attention] [🔴 Action Required]    │
├────────────────────────┬────────────────────────────────────────┤
│                        │                                        │
│    CASH POSITION       │         ACTION ITEMS                   │
│    (Primary Widget)    │         (Top 5 Priority)               │
│                        │                                        │
├────────────────────────┼────────────────────────────────────────┤
│                        │                                        │
│    REVENUE MTD         │         AR/AP SUMMARY                  │
│    (vs Target/LY)      │         (Quick Health)                 │
│                        │                                        │
├────────────────────────┴────────────────────────────────────────┤
│                                                                 │
│              13-WEEK CASH FORECAST CHART                        │
│              (with confidence bands)                            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│              JOB PROFITABILITY HEATMAP                          │
│              (Recent 20 jobs, margin by size)                   │
│                                                                 │
├────────────────────────┬────────────────────────────────────────┤
│                        │                                        │
│    PIPELINE SUMMARY    │         CREW UTILIZATION               │
│    (Backlog Value)     │         (if available)                 │
│                        │                                        │
└────────────────────────┴────────────────────────────────────────┘
```

---

## Widget Specifications

### 1. Overall Health Banner

**Purpose:** Instant business health assessment

**Logic:**
```javascript
function calculateHealthStatus(metrics) {
  // Critical conditions (RED)
  if (metrics.cash_runway_weeks < 2) return 'critical';
  if (metrics.overdue_ar_pct > 40) return 'critical';
  if (metrics.negative_margin_jobs > 3) return 'critical';
  
  // Warning conditions (YELLOW)
  if (metrics.cash_runway_weeks < 4) return 'warning';
  if (metrics.overdue_ar_pct > 25) return 'warning';
  if (metrics.mtd_revenue < metrics.target * 0.7) return 'warning';
  if (metrics.avg_margin < 25) return 'warning';
  
  // All good (GREEN)
  return 'healthy';
}
```

**Display:**
- **Green Banner:** "Looking Good - Keep it up! 👍"
- **Yellow Banner:** "Needs Attention - 3 items to review"
- **Red Banner:** "Action Required - Click to see priorities"

**Data Sources:**
- `cash_positions` (cash_balance, forecast)
- `jobs` (margin calculations)
- AR aging from QBO

---

### 2. Cash Position Widget

**Purpose:** Answer "Do I have enough cash to make payroll?"

**Metrics:**

| Metric | Source | Update Frequency |
|--------|--------|------------------|
| Current Cash Balance | `cash_positions.cash_balance` | Daily |
| Cash Change (WoW) | Calculated | Daily |
| Cash Runway | `cash_forecasts.summary` | Daily |
| Next Payroll | `recurring_expenses` | Static |

**Visualization:**
```
┌─────────────────────────────┐
│  💰 CASH POSITION           │
├─────────────────────────────┤
│                             │
│   $127,450                  │
│   ↑ $12,300 (+10.7%)        │
│   from last week            │
│                             │
│   ────────────────────      │
│   📊 8 weeks runway         │
│   💸 Next payroll: $28K     │
│      in 5 days              │
│                             │
└─────────────────────────────┘
```

**Conditional Formatting:**
- Balance > Target: Green text
- Balance < Minimum: Red text, pulse animation
- Runway < 4 weeks: Yellow warning icon

---

### 3. Revenue MTD Widget

**Purpose:** Track monthly progress against targets

**Metrics:**

| Metric | Calculation |
|--------|-------------|
| MTD Revenue | SUM(job_revenue) WHERE date >= month_start |
| Target | Manual or auto-calculated from history |
| vs Last Year | Same period comparison |
| Projected Month | MTD × (days_in_month / current_day) |

**Visualization:**
```
┌─────────────────────────────┐
│  📈 REVENUE - NOVEMBER      │
├─────────────────────────────┤
│                             │
│   $189,500 MTD              │
│   ▓▓▓▓▓▓▓▓░░ 78% to goal    │
│                             │
│   Target: $245,000          │
│   vs LY:  $172,000 (+10%)   │
│                             │
│   Projected: $237,000       │
│   12 jobs completed         │
│                             │
└─────────────────────────────┘
```

**Progress Bar Logic:**
- Green if on track (>80% of prorated target)
- Yellow if behind (60-80%)
- Red if significantly behind (<60%)

---

### 4. Action Items Panel

**Purpose:** Surface items requiring owner attention

**Categories:**
1. **Cash Actions** (High Priority)
   - Invoices ready to send
   - Large AR overdue
   - AP due that affects cash runway

2. **Job Actions** (Medium Priority)
   - Jobs missing cost entries
   - Jobs with negative/low margin
   - Change orders pending approval

3. **Admin Actions** (Lower Priority)
   - Transactions needing categorization
   - Missing vendor W-9s
   - Upcoming compliance deadlines

**Data Source Query:**
```sql
SELECT 
  action_type,
  priority,
  title,
  description,
  due_date,
  potential_impact
FROM action_items
WHERE tenant_id = $1
  AND status = 'pending'
ORDER BY 
  CASE priority 
    WHEN 'critical' THEN 1 
    WHEN 'high' THEN 2 
    WHEN 'medium' THEN 3 
    ELSE 4 
  END,
  due_date ASC
LIMIT 5;
```

**Display:**
```
┌─────────────────────────────────────────┐
│  ⚡ ACTION ITEMS (5)                    │
├─────────────────────────────────────────┤
│ 🔴 Invoice #1042 ready - $18,500        │
│    Click to review & send               │
│                                         │
│ 🟡 $12,400 AR overdue 45+ days          │
│    Johnson residence - follow up        │
│                                         │
│ 🟡 Job #2089 missing material costs     │
│    Elm St. project - verify receipts    │
│                                         │
│ 🟢 3 transactions need categorization   │
│    Quick review (est. 2 min)            │
│                                         │
│ 🟢 W-9 needed: ABC Supplies             │
│    Before next payment                  │
└─────────────────────────────────────────┘
```

---

### 5. AR/AP Summary Widget

**Purpose:** Quick receivables/payables health check

**Metrics:**

| Metric | Source |
|--------|--------|
| Total AR | QBO Aged Receivables |
| AR Aging Buckets | QBO Report |
| Total AP | QBO Aged Payables |
| AP Due This Week | Calculated |

**Visualization:**
```
┌─────────────────────────────┐
│  💳 AR/AP HEALTH            │
├─────────────────────────────┤
│                             │
│  RECEIVABLES    $89,200     │
│  ▓▓▓▓▓▓▓▓▓░ Current: $71K   │
│  ░░░░░░▓▓░░ 31-60: $12K     │
│  ░░░░░░░░▓░ 61-90: $4K      │
│  ░░░░░░░░░▓ 90+: $2K ⚠️     │
│                             │
│  ─────────────────────────  │
│                             │
│  PAYABLES       $34,800     │
│  Due this week: $12,400     │
│  Overdue: $0 ✓              │
│                             │
└─────────────────────────────┘
```

---

### 6. 13-Week Cash Forecast Chart

**Purpose:** Visual cash trajectory with scenarios

**Chart Type:** Line chart with confidence bands

**Elements:**
- **Primary Line:** Baseline (expected) forecast
- **Upper Band:** Optimistic scenario (light green fill)
- **Lower Band:** Pessimistic scenario (light red fill)
- **Horizontal Lines:** Minimum balance threshold, target balance
- **Markers:** Payroll dates, large AP due dates

**Chart Configuration:**
```javascript
const chartConfig = {
  type: 'line',
  data: {
    labels: weeks.map(w => w.week_start),
    datasets: [
      {
        label: 'Expected',
        data: baseline.map(w => w.ending_cash),
        borderColor: '#3182ce',
        fill: false
      },
      {
        label: 'Optimistic',
        data: optimistic.map(w => w.ending_cash),
        borderColor: '#38a169',
        backgroundColor: 'rgba(56, 161, 105, 0.1)',
        fill: '+1'
      },
      {
        label: 'Pessimistic', 
        data: pessimistic.map(w => w.ending_cash),
        borderColor: '#e53e3e',
        backgroundColor: 'rgba(229, 62, 62, 0.1)',
        fill: false
      }
    ]
  },
  options: {
    plugins: {
      annotation: {
        annotations: {
          minBalanceLine: {
            type: 'line',
            yMin: 25000,
            yMax: 25000,
            borderColor: 'red',
            borderDash: [5, 5],
            label: {
              content: 'Minimum Balance',
              enabled: true
            }
          }
        }
      }
    }
  }
};
```

**Interactions:**
- Hover for weekly detail
- Click week to see drivers (AR coming in, AP going out)
- Toggle scenarios on/off

---

### 7. Job Profitability Heatmap

**Purpose:** Visual margin analysis across recent jobs

**Data:**
```sql
SELECT 
  job_number,
  customer_name,
  contract_amount,
  total_cost,
  gross_margin_pct,
  job_type,
  completed_date
FROM jobs
WHERE tenant_id = $1
  AND status = 'completed'
  AND completed_date >= NOW() - INTERVAL '90 days'
ORDER BY completed_date DESC
LIMIT 20;
```

**Visualization:** Treemap or bubble chart

**Color Coding:**
- Dark Green: >40% margin (excellent)
- Light Green: 30-40% margin (good)
- Yellow: 25-30% margin (acceptable)
- Orange: 15-25% margin (needs review)
- Red: <15% margin (problem)

**Size:** Proportional to contract amount

```
┌────────────────────────────────────────────────────────────────┐
│  JOB PROFITABILITY (Last 90 Days)                              │
├────────────────────────────────────────────────────────────────┤
│ ┌──────────────────┐┌─────────────┐┌────────────┐              │
│ │                  ││             ││  #2087     │              │
│ │    #2091         ││   #2089     ││  $8.2K     │              │
│ │    $45K          ││   $28K      ││  38%       │              │
│ │    35% ██████    ││   31%       ││            │              │
│ └──────────────────┘└─────────────┘└────────────┘              │
│ ┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌────────────┐ │
│ │ #2085    ││ #2084    ││ #2083    ││ #2082    ││  #2079     │ │
│ │ $12K    ││ $15K     ││ $9K      ││ $11K     ││  $22K      │ │
│ │ 42%     ││ 28%      ││ 18% ⚠️   ││ 33%      ││  12% 🔴    │ │
│ └──────────┘└──────────┘└──────────┘└──────────┘└────────────┘ │
│                                                                │
│ Avg Margin: 31.2%  |  Target: 35%  |  3 jobs below 25%        │
└────────────────────────────────────────────────────────────────┘
```

**Interactions:**
- Click job to see cost breakdown
- Filter by job type, date range, customer type
- Drill to job detail page

---

### 8. Pipeline Summary Widget

**Purpose:** Forward-looking work visibility

**Metrics:**

| Status | Count | Value | Win Rate |
|--------|-------|-------|----------|
| Estimates | # | $XXX | 35% |
| Scheduled | # | $XXX | 90% |
| In Progress | # | $XXX | 98% |
| **Weighted Total** | - | $XXX | - |

**Visualization:**
```
┌─────────────────────────────┐
│  📋 PIPELINE                │
├─────────────────────────────┤
│                             │
│  BACKLOG         $312,000   │
│  8 jobs scheduled/in prog   │
│  ~4 weeks of work           │
│                             │
│  ─────────────────────────  │
│                             │
│  ESTIMATES       $187,000   │
│  12 open estimates          │
│  Weighted value: $65,450    │
│                             │
│  Win rate (90d): 38%        │
│                             │
└─────────────────────────────┘
```

---

## Data Refresh Schedule

| Widget | Refresh Frequency | Data Source |
|--------|-------------------|-------------|
| Health Banner | Real-time (on load) | Calculated |
| Cash Position | Every 4 hours | Supabase + QBO |
| Revenue MTD | Every 4 hours | Supabase |
| Action Items | Real-time (on load) | Supabase |
| AR/AP Summary | Every 4 hours | QBO API |
| Cash Forecast | Daily (6 AM) | Supabase |
| Job Profitability | Every 4 hours | Supabase |
| Pipeline | Real-time (on load) | Jobber/ST + Supabase |

---

## Mobile Responsiveness

### Phone Layout (< 768px)

Stack widgets vertically in priority order:
1. Health Banner (always visible at top)
2. Cash Position (collapsible)
3. Action Items (expandable list)
4. Revenue MTD (collapsible)
5. AR/AP Summary (collapsible)
6. Cash Forecast (horizontal scroll)
7. Job Profitability (simplified list view)
8. Pipeline Summary (collapsible)

### Tablet Layout (768px - 1024px)

Two-column layout:
- Left: Cash, Revenue, Pipeline
- Right: Action Items, AR/AP, Forecast

---

## Technical Implementation

### React Component Structure

```
OwnerDashboard/
├── OwnerDashboard.tsx          # Main container
├── components/
│   ├── HealthBanner.tsx        # Overall status
│   ├── CashWidget.tsx          # Cash position
│   ├── RevenueWidget.tsx       # MTD revenue
│   ├── ActionItems.tsx         # Priority actions
│   ├── ARAPWidget.tsx          # AR/AP health
│   ├── CashForecastChart.tsx   # 13-week chart
│   ├── JobProfitability.tsx    # Margin heatmap
│   └── PipelineWidget.tsx      # Backlog summary
├── hooks/
│   ├── useDashboardData.ts     # Data fetching
│   ├── useRefreshInterval.ts   # Auto-refresh
│   └── useHealthCalculation.ts # Status logic
├── utils/
│   ├── formatters.ts           # Number/date formatting
│   └── calculations.ts         # Metric calculations
└── styles/
    └── dashboard.css           # Styling
```

### API Endpoints

```
GET /api/dashboard/owner/:tenantId
  → Returns aggregated dashboard data

GET /api/dashboard/owner/:tenantId/cash
  → Returns cash position details

GET /api/dashboard/owner/:tenantId/actions
  → Returns action items list

GET /api/dashboard/owner/:tenantId/forecast
  → Returns forecast data for chart
```

### Supabase Real-time Subscriptions

```javascript
// Subscribe to changes that affect dashboard
const subscription = supabase
  .channel('dashboard-updates')
  .on('postgres_changes', 
    { event: '*', schema: 'public', table: 'cash_positions' },
    (payload) => refreshCashWidget()
  )
  .on('postgres_changes',
    { event: '*', schema: 'public', table: 'action_items' },
    (payload) => refreshActionItems()
  )
  .subscribe();
```

---

## Alerts & Notifications

### In-Dashboard Alerts

Displayed as toast notifications or inline banners:

| Trigger | Message | Action |
|---------|---------|--------|
| Cash < minimum | "Cash below $25K threshold" | Link to forecast |
| AR > 60 days | "Invoice #X is 67 days overdue" | Link to AR detail |
| Job margin < 15% | "Job #X has 12% margin" | Link to job detail |
| Forecast negative | "Cash projected negative in Week X" | Link to scenarios |

### Push Notifications (Mobile)

Configure in user preferences:
- [ ] Daily cash summary (default: on)
- [ ] Critical alerts only
- [ ] Weekly brief ready
- [ ] Large AR/AP activity
