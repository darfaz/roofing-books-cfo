# <!-- filename: /dashboards/cfo/cfo_dashboard.md -->
# CFO Analytics Dashboard

## Overview

The CFO Dashboard is designed to answer the strategic question: **"Where is the leverage?"**

This dashboard provides a fractional CFO or financially-sophisticated owner with deep analytical capabilities to identify opportunities, risks, and strategic levers in the business.

---

## Design Philosophy

### Narrative Goals

| Question | Answer Location | Analysis Depth |
|----------|-----------------|----------------|
| "Where is the leverage?" | Executive summary | High-level |
| "What's driving profitability?" | Margin analysis | Deep dive |
| "Where is cash tied up?" | Working capital analysis | Detailed |
| "What are the trends?" | Time series charts | Historical |
| "What scenarios should I plan for?" | Scenario modeler | Interactive |
| "How accurate are our forecasts?" | Accuracy tracking | Meta-analysis |

### Design Principles

1. **Analytical Depth** - Support drill-down to transaction level
2. **Comparative** - Show trends, benchmarks, and variances
3. **Scenario-Driven** - What-if modeling built in
4. **Exportable** - All data and charts exportable for board/lender reports
5. **Customizable** - Save views and create custom metrics

---

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXECUTIVE KPI BAR                                   │
│  [Cash: $127K] [Revenue: $892K] [GM: 34%] [EBITDA: 12%] [AR Days: 28]      │
├─────────────────────────────────┬───────────────────────────────────────────┤
│                                 │                                           │
│   FINANCIAL PERFORMANCE         │        WORKING CAPITAL ANALYSIS           │
│   (P&L Trend Chart)             │        (Cash Conversion Cycle)            │
│                                 │                                           │
├─────────────────────────────────┼───────────────────────────────────────────┤
│                                 │                                           │
│   MARGIN ANALYSIS               │        REVENUE COMPOSITION                │
│   (By Job Type, Channel)        │        (By Customer Type, Source)         │
│                                 │                                           │
├─────────────────────────────────┴───────────────────────────────────────────┤
│                                                                             │
│                    SCENARIO COMPARISON TABLE                                │
│   (Pessimistic | Baseline | Optimistic - Key Metrics Side by Side)         │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                    FORECAST ACCURACY TRACKING                               │
│   (Historical Forecast vs Actual - Confidence Calibration)                  │
│                                                                             │
├─────────────────────────────────┬───────────────────────────────────────────┤
│                                 │                                           │
│   COST STRUCTURE ANALYSIS       │        CREW/DIVISION PERFORMANCE          │
│   (Fixed vs Variable)           │        (Contribution Margin by Crew)      │
│                                 │                                           │
└─────────────────────────────────┴───────────────────────────────────────────┘
```

---

## Widget Specifications

### 1. Executive KPI Bar

**Purpose:** At-a-glance key metrics with sparklines

**Metrics:**

| KPI | Calculation | Benchmark | Alert Threshold |
|-----|-------------|-----------|-----------------|
| Cash Balance | Current bank balance | $50K+ target | < $25K |
| LTM Revenue | Last 12 months | YoY growth | < -10% YoY |
| Gross Margin | Revenue - COGS / Revenue | 35% roofing avg | < 25% |
| EBITDA Margin | EBITDA / Revenue | 10-15% target | < 5% |
| AR Days | Avg AR / (Revenue / 365) | < 30 days | > 45 days |
| Quick Ratio | (Cash + AR) / Current Liabilities | > 1.0 | < 0.8 |

**Display:**
```
┌──────────────────────────────────────────────────────────────────────────────┐
│  💰 $127,450      📈 $892K LTM      📊 34.2%      💵 11.8%      📅 28 days  │
│     Cash             Revenue           GM          EBITDA         AR Days   │
│     ↑ 12%           ↑ 8% YoY         ↓ 1.2pt      ↑ 0.5pt        ↓ 3 days  │
│     ▁▂▃▄▅▆▇█▇▆      ▁▂▂▃▄▅▅▆▇█      ▆▅▅▄▄▃▃▄▅▆    ▂▃▃▄▄▅▅▆▇█     ▇▆▅▅▄▄▃▃▂▁ │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Financial Performance Chart

**Purpose:** Multi-metric trend visualization over time

**Chart Type:** Combination chart (bars + lines)

**Metrics:**
- Bar: Monthly Revenue
- Bar (stacked): COGS breakdown
- Line: Gross Margin %
- Line: EBITDA Margin %

**Time Periods:**
- Default: Last 12 months
- Options: Last 6 months, Last 24 months, YTD, Custom range

**Data Source:**
```sql
SELECT 
  DATE_TRUNC('month', t.transaction_date) as month,
  SUM(CASE WHEN a.account_type = 'Revenue' THEN t.amount ELSE 0 END) as revenue,
  SUM(CASE WHEN a.account_type = 'COGS' THEN t.amount ELSE 0 END) as cogs,
  SUM(CASE WHEN a.category = 'labor' THEN t.amount ELSE 0 END) as labor_cost,
  SUM(CASE WHEN a.category = 'materials' THEN t.amount ELSE 0 END) as material_cost,
  SUM(CASE WHEN a.category = 'subcontractor' THEN t.amount ELSE 0 END) as sub_cost,
  SUM(CASE WHEN a.account_type = 'Expense' THEN t.amount ELSE 0 END) as opex
FROM transactions_categorized t
JOIN accounts a ON t.account_id = a.id
WHERE t.tenant_id = $1
  AND t.transaction_date >= NOW() - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', t.transaction_date)
ORDER BY month;
```

**Visualization Config:**
```javascript
const chartConfig = {
  type: 'bar',
  data: {
    datasets: [
      {
        type: 'bar',
        label: 'Revenue',
        backgroundColor: '#3182ce',
        data: monthlyData.map(m => m.revenue)
      },
      {
        type: 'bar',
        label: 'COGS',
        backgroundColor: '#e53e3e',
        data: monthlyData.map(m => m.cogs),
        stack: 'costs'
      },
      {
        type: 'line',
        label: 'Gross Margin %',
        borderColor: '#38a169',
        data: monthlyData.map(m => ((m.revenue - m.cogs) / m.revenue) * 100),
        yAxisID: 'percentage'
      }
    ]
  },
  options: {
    scales: {
      y: { position: 'left', title: { text: 'Dollars' } },
      percentage: { position: 'right', min: 0, max: 50, title: { text: '%' } }
    }
  }
};
```

---

### 3. Working Capital Analysis

**Purpose:** Understand cash tied up in operations

**Metrics:**

| Component | Calculation | Target |
|-----------|-------------|--------|
| Days Sales Outstanding (DSO) | (Avg AR / Revenue) × 365 | < 30 |
| Days Payable Outstanding (DPO) | (Avg AP / COGS) × 365 | 30-45 |
| Days Inventory Outstanding (DIO) | (Avg Inventory / COGS) × 365 | < 15 |
| Cash Conversion Cycle | DSO - DPO + DIO | < 15 days |

**Visualization:** Waterfall chart showing cash conversion cycle

```
┌───────────────────────────────────────────────────────────────┐
│  CASH CONVERSION CYCLE                                        │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  DSO: 28 days     ████████████████████████████                │
│                   Collect receivables                         │
│                                                               │
│  DPO: 32 days               ████████████████████████████████  │
│                             Pay suppliers                     │
│                                                               │
│  DIO: 8 days      ████████                                    │
│                   Material in yard                            │
│                                                               │
│  ═══════════════════════════════════════════════════════════  │
│  CYCLE: 4 days    ████                                        │
│                   Cash tied up in working capital             │
│                                                               │
│  💡 Insight: Extending DPO to 35 days would free up $12K     │
└───────────────────────────────────────────────────────────────┘
```

**Trend Analysis:**
- Show CCC trend over last 12 months
- Highlight improvements/deteriorations
- Compare to industry benchmark (roofing: 10-20 days typical)

---

### 4. Margin Analysis Widget

**Purpose:** Understand profitability drivers by segment

**Dimensions:**
- By Job Type (residential repair, residential replacement, commercial, storm/insurance)
- By Customer Channel (referral, web lead, repeat customer)
- By Crew
- By Material Type (shingle, metal, flat)

**Data Structure:**
```sql
SELECT 
  j.job_type,
  j.customer_channel,
  j.crew_id,
  COUNT(*) as job_count,
  SUM(j.contract_amount) as total_revenue,
  SUM(j.total_cost) as total_cost,
  AVG(j.gross_margin_pct) as avg_margin,
  STDDEV(j.gross_margin_pct) as margin_stddev,
  MIN(j.gross_margin_pct) as min_margin,
  MAX(j.gross_margin_pct) as max_margin
FROM jobs j
WHERE j.tenant_id = $1
  AND j.status = 'completed'
  AND j.completed_date >= NOW() - INTERVAL '12 months'
GROUP BY j.job_type, j.customer_channel, j.crew_id;
```

**Visualization:** Pivot table with conditional formatting

```
┌───────────────────────────────────────────────────────────────────────┐
│  MARGIN BY JOB TYPE & CHANNEL                                         │
├───────────────────────────────────────────────────────────────────────┤
│                      │ Referral │ Web Lead │ Repeat │  ALL   │        │
│ ─────────────────────┼──────────┼──────────┼────────┼────────┤        │
│ Res. Repair          │   38%    │   31%    │  42%   │  36%   │ 45 jobs│
│ Res. Replacement     │   35%    │   28%    │  38%   │  33%   │ 82 jobs│
│ Commercial           │   29%    │   24%    │  32%   │  28%   │ 18 jobs│
│ Storm/Insurance      │   41%    │   36%    │  44%   │  40%   │ 31 jobs│
│ ─────────────────────┼──────────┼──────────┼────────┼────────┤        │
│ ALL                  │   36%    │   29%    │  39%   │  34%   │176 jobs│
└───────────────────────────────────────────────────────────────────────┘

💡 Insight: Web leads have 7pts lower margin than referrals - review 
            pricing or lead quality
```

**Color Coding:**
- Green: > 35% margin
- Yellow: 25-35% margin
- Red: < 25% margin

---

### 5. Revenue Composition Analysis

**Purpose:** Understand revenue mix and trends

**Visualizations:**

#### Pie/Donut Chart - Current Mix
```
┌─────────────────────────────────────┐
│  REVENUE MIX (LTM)                  │
├─────────────────────────────────────┤
│                                     │
│         ┌─────────┐                 │
│       ╱    42%     ╲                │
│      │   Res Repl   │               │
│      │             │                │
│      ╲    ╭───╮   ╱                 │
│       ╲  │28%│  ╱                   │
│        ╲ │Rep│ ╱                    │
│         ╲╰───╯╱                     │
│          ╲   ╱ 18% Commercial       │
│           ╲ ╱  12% Storm            │
│            V                        │
│                                     │
│  Total: $892,000                    │
└─────────────────────────────────────┘
```

#### Stacked Area Chart - Mix Over Time
Show how revenue composition has shifted over past 24 months

#### Customer Concentration
```
┌─────────────────────────────────────────────────────────────┐
│  CUSTOMER CONCENTRATION                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Top 10 Customers: 23% of revenue                          │
│  ▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│                                                             │
│  1. ABC Property Mgmt    $45,200    5.1%                   │
│  2. Johnson Construction $38,100    4.3%                   │
│  3. Oakwood HOA          $31,500    3.5%                   │
│  ...                                                        │
│                                                             │
│  ✓ Healthy diversification - no customer > 10%             │
└─────────────────────────────────────────────────────────────┘
```

---

### 6. Scenario Comparison Table

**Purpose:** Side-by-side scenario analysis for planning

**Table Structure:**

```
┌───────────────────────────────────────────────────────────────────────────┐
│  13-WEEK SCENARIO COMPARISON                                              │
├───────────────────────────────────────────────────────────────────────────┤
│                        │ Pessimistic │  Baseline  │ Optimistic │  Actual  │
│ ───────────────────────┼─────────────┼────────────┼────────────┼──────────│
│ Starting Cash          │   $127,450  │  $127,450  │  $127,450  │ $127,450 │
│ Ending Cash (Wk 13)    │    $82,100  │  $142,800  │  $198,500  │    -     │
│ Min Cash (Week #)      │ $68K (Wk 8) │ $98K (Wk 6)│$127K (Wk 1)│    -     │
│ ───────────────────────┼─────────────┼────────────┼────────────┼──────────│
│ Total Revenue          │   $289,000  │  $362,000  │  $415,000  │    -     │
│ Total COGS             │   $195,000  │  $235,000  │  $268,000  │    -     │
│ Gross Margin %         │      32.5%  │     35.1%  │     35.4%  │    -     │
│ ───────────────────────┼─────────────┼────────────┼────────────┼──────────│
│ AR Collected           │   $178,000  │  $212,000  │  $238,000  │    -     │
│ AP Paid                │   $156,000  │  $168,000  │  $178,000  │    -     │
│ ───────────────────────┼─────────────┼────────────┼────────────┼──────────│
│ Cash Runway            │    6 weeks  │  10 weeks  │  13+ weeks │    -     │
│ Prob. of Cash Crunch   │       35%   │       8%   │       2%   │    -     │
└───────────────────────────────────────────────────────────────────────────┘

[Adjust Assumptions]  [Export to PDF]  [Save Scenario]
```

**Interactive Features:**
- Adjust scenario assumptions (slider controls)
- Monte Carlo simulation toggle
- Export scenarios for board presentations

---

### 7. Forecast Accuracy Tracking

**Purpose:** Meta-analysis of forecast reliability

**Visualization:** 
- Historical forecast vs actual (multiple forecast vintages)
- Accuracy by weeks-out (accuracy degrades over time)
- Bias analysis (are we consistently over/under?)

**Chart:**
```
┌───────────────────────────────────────────────────────────────────────────┐
│  FORECAST ACCURACY BY HORIZON                                             │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Variance (%)                                                             │
│  │                                                                        │
│  │                                                     ●                  │
│  │                                           ●                            │
│  │                                 ●                   ▲                  │
│  │                       ●                   ▲                            │
│  │              ●                  ▲                                      │
│  │     ●                 ▲                                                │
│  │────────────────────────────────────────────────────────  Target ±15%  │
│  │     ▲        ▲                                                         │
│  └──────────────────────────────────────────────────────────────────────  │
│       1w    2w    4w    6w    8w   10w   12w                              │
│                                                                           │
│  ● Actual Variance   ▲ Target Variance                                    │
│                                                                           │
│  Summary: 4-week forecasts are within ±12% (good)                         │
│           8-week forecasts have ±22% variance (needs improvement)         │
└───────────────────────────────────────────────────────────────────────────┘
```

**Metrics:**
| Horizon | MAPE | Bias | Within ±15% |
|---------|------|------|-------------|
| 1 week | 5% | +1% | 95% |
| 4 weeks | 12% | +3% | 78% |
| 8 weeks | 22% | +8% | 52% |
| 13 weeks | 31% | +12% | 38% |

---

### 8. Cost Structure Analysis

**Purpose:** Understand fixed vs variable cost behavior

**Visualization:** Scatter plot with regression line

```
┌───────────────────────────────────────────────────────────────┐
│  COST BEHAVIOR ANALYSIS                                       │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  Cost ($K)                                                    │
│  │                                              ●             │
│  │                                    ●    ●                  │
│  │                              ●  ●                          │
│  │                        ●  ●                                │
│  │                  ●  ●                                      │
│  │            ●  ●                     Variable: 62%          │
│  │      ●  ●                                                  │
│  │  ●                                                         │
│  │────────────────────────────────────  Fixed: $18K/month     │
│  └──────────────────────────────────────────────────────────  │
│       $50K   $100K  $150K  $200K  $250K  $300K               │
│                         Revenue                               │
│                                                               │
│  Break-even: ~$47K/month revenue                              │
│  Operating leverage: 1.6x (sensitive to revenue changes)      │
└───────────────────────────────────────────────────────────────┘
```

**Breakdown Table:**
| Category | Monthly Avg | % of Revenue | Fixed/Variable |
|----------|-------------|--------------|----------------|
| Labor - Direct | $42,000 | 47% | Variable |
| Materials | $28,000 | 31% | Variable |
| Subcontractors | $8,000 | 9% | Variable |
| Payroll - Indirect | $12,000 | - | Fixed |
| Vehicles | $4,500 | - | Fixed |
| Insurance | $3,800 | - | Fixed |
| Rent/Facilities | $2,200 | - | Fixed |

---

### 9. Crew/Division Performance

**Purpose:** Compare performance across operating units

**Table:**
```
┌───────────────────────────────────────────────────────────────────────────┐
│  CREW PERFORMANCE (Last 90 Days)                                          │
├───────────────────────────────────────────────────────────────────────────┤
│                │ Jobs │ Revenue  │ Gross  │ Avg Job │ Callback │ Rating │
│                │ Comp │          │ Margin │ Size    │ Rate     │        │
│ ───────────────┼──────┼──────────┼────────┼─────────┼──────────┼────────│
│ Crew A (Mike)  │  28  │ $312,000 │  38%   │ $11,140 │   2.1%   │  4.8   │
│ Crew B (Jose)  │  32  │ $287,000 │  35%   │  $8,970 │   3.2%   │  4.6   │
│ Crew C (Dave)  │  24  │ $245,000 │  31%   │ $10,210 │   4.8%   │  4.2   │
│ Crew D (New)   │  12  │  $98,000 │  28%   │  $8,170 │   6.1%   │  4.0   │
│ ───────────────┼──────┼──────────┼────────┼─────────┼──────────┼────────│
│ ALL            │  96  │ $942,000 │  34%   │  $9,810 │   3.5%   │  4.4   │
└───────────────────────────────────────────────────────────────────────────┘

💡 Insight: Crew C and D have higher callback rates impacting profitability.
            Crew A generates 12% more revenue per job with best margins.
```

**Additional Metrics:**
- Utilization rate (billable days / available days)
- Jobs per crew-day
- Material waste %
- Safety incidents

---

## Advanced Features

### Custom KPI Builder

Allow CFO to define custom metrics:

```
┌─────────────────────────────────────────────────────────────┐
│  CREATE CUSTOM KPI                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Name: Revenue per Crew Day                                 │
│                                                             │
│  Formula:                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ SUM(job_revenue) / SUM(crew_days_worked)            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Time Period: ○ MTD  ● LTM  ○ Custom                       │
│                                                             │
│  Benchmark: $2,500 (target)                                │
│                                                             │
│  Alert when: Below $2,000                                  │
│                                                             │
│  [Test Formula]  [Save KPI]  [Add to Dashboard]            │
└─────────────────────────────────────────────────────────────┘
```

### Export & Reporting

**Export Options:**
- PDF report (formatted for board/lender)
- Excel workbook (with formulas)
- PowerPoint slides (key charts)
- CSV raw data

**Scheduled Reports:**
- Weekly CFO packet (auto-generated)
- Monthly board report template
- Quarterly business review deck

### Comparison Tools

**Period Comparison:**
- This month vs last month
- This quarter vs same quarter last year
- Rolling 12 months vs prior 12 months
- Custom date range comparison

**Benchmark Comparison:**
- Industry benchmarks (roofing industry)
- Internal targets
- Peer comparison (if multi-location)

---

## Technical Implementation

### Data Aggregation Layer

Pre-compute common aggregations for performance:

```sql
-- Materialized view for monthly summaries
CREATE MATERIALIZED VIEW monthly_financials AS
SELECT 
  tenant_id,
  DATE_TRUNC('month', transaction_date) as month,
  SUM(CASE WHEN account_type = 'Revenue' THEN amount END) as revenue,
  SUM(CASE WHEN account_type = 'COGS' THEN amount END) as cogs,
  SUM(CASE WHEN account_type = 'Expense' THEN amount END) as opex,
  COUNT(DISTINCT job_id) as jobs_count
FROM transactions_categorized
GROUP BY tenant_id, DATE_TRUNC('month', transaction_date);

-- Refresh nightly
CREATE OR REPLACE FUNCTION refresh_financial_views()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_financials;
  REFRESH MATERIALIZED VIEW CONCURRENTLY job_profitability_summary;
  REFRESH MATERIALIZED VIEW CONCURRENTLY working_capital_metrics;
END;
$$ LANGUAGE plpgsql;
```

### API Structure

```
GET /api/cfo/:tenantId/executive-kpis
  → Returns KPI bar metrics

GET /api/cfo/:tenantId/performance?period=12m
  → Returns P&L trend data

GET /api/cfo/:tenantId/margins?groupBy=job_type,channel
  → Returns margin pivot data

GET /api/cfo/:tenantId/scenarios
  → Returns scenario comparison data

GET /api/cfo/:tenantId/forecast-accuracy
  → Returns accuracy metrics

POST /api/cfo/:tenantId/custom-kpi
  → Create custom KPI definition

GET /api/cfo/:tenantId/export?format=pdf&report=monthly
  → Generate and download report
```

### React Component Structure

```
CFODashboard/
├── CFODashboard.tsx              # Main container
├── components/
│   ├── ExecutiveKPIBar.tsx       # Top KPI strip
│   ├── PerformanceChart.tsx      # P&L trends
│   ├── WorkingCapital.tsx        # CCC analysis
│   ├── MarginAnalysis.tsx        # Margin pivot
│   ├── RevenueComposition.tsx    # Revenue mix
│   ├── ScenarioComparison.tsx    # Scenario table
│   ├── ForecastAccuracy.tsx      # Accuracy tracking
│   ├── CostStructure.tsx         # Fixed/variable
│   ├── CrewPerformance.tsx       # Crew analysis
│   └── CustomKPIBuilder.tsx      # KPI creator
├── hooks/
│   ├── useCFOData.ts             # Data fetching
│   ├── useScenarios.ts           # Scenario logic
│   └── useExport.ts              # Export functionality
├── utils/
│   ├── calculations.ts           # Financial calculations
│   ├── formatters.ts             # Number formatting
│   └── chartConfigs.ts           # Chart.js configs
└── styles/
    └── cfo-dashboard.css
```

---

## Access Control

| Feature | Owner | CFO | Bookkeeper |
|---------|-------|-----|------------|
| View KPIs | ✓ | ✓ | Limited |
| Scenario Modeling | ✓ | ✓ | ✗ |
| Export Reports | ✓ | ✓ | ✗ |
| Custom KPIs | ✗ | ✓ | ✗ |
| Crew Performance | ✓ | ✓ | ✗ |
| Cost Structure | ✗ | ✓ | ✗ |
| Forecast Accuracy | ✗ | ✓ | ✗ |
