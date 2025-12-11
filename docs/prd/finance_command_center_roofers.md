# PRD: Finance Command Center for Roofers

> **Version**: 1.0.0  
> **Last Updated**: 2025-12-11  
> **Status**: Draft  
> **Owner**: Product Team  

---

## Problem Statement

Roofing contractors operate in a **uniquely challenging cash flow environment**:

- **Seasonality**: Revenue swings 50-70% between peak and slow seasons
- **Large payables**: Material bills can hit $20-50K per job
- **Delayed receivables**: Insurance jobs take 45-90 days to collect
- **Weather dependency**: A bad weather week can crater monthly revenue
- **Growth blind spots**: Owners add crews or trucks without understanding overhead impact

**The result**: Owners experience recurring "cash surprise" moments—discovering on payroll day that they can't cover checks, or missing growth opportunities because they're afraid of running out of money.

**The gap**: Generic financial dashboards show historical data but don't answer "Will I be okay?" Construction-specific tools (Briq, Adaptive) focus on project tracking, not owner-level cash intelligence. Fractional CFO services cost $2-5K/month and don't provide real-time visibility.

**Our solution**: An AI-powered Finance Command Center that gives roofing owners the confidence of having a CFO without the cost—automated forecasting, scenario modeling, and plain-English insights delivered weekly.

---

## User Personas & Agents

### Primary: Roofing Business Owner

| Attribute | Description |
|-----------|-------------|
| **Mental model** | "I need to know if I can make payroll and pay my suppliers" |
| **Decision frequency** | Daily check-ins during busy season, weekly during slow |
| **Questions asked** | "Can I hire another crew?" "Should I take this big job?" "How bad will winter be?" |
| **Time available** | 5-10 minutes daily, 30 minutes weekly |
| **Preferred format** | Mobile-first, narrative summaries over tables |

### Secondary: Spec-OS Fractional CFO

| Attribute | Description |
|-----------|-------------|
| **Role** | Human advisor who reviews system outputs and provides strategic guidance |
| **Interaction** | Monthly call, ad-hoc Slack/email |
| **Questions asked** | "What's driving margin compression?" "Where should they focus?" |
| **System use** | Deeper dashboard access, scenario modeling, report generation |

### System Actors: AI Agents

| Agent | Role |
|-------|------|
| **Forecast Engine** | Builds and maintains 13-week cash flow projection |
| **Scenario Planner** | Models "what-if" scenarios (price changes, volume shifts, overhead adds) |
| **Alert Monitor** | Detects danger zones and triggers notifications |
| **Narrative Generator** | Produces plain-English weekly CFO brief |
| **Margin Analyzer** | Tracks job type and channel profitability trends |

---

## Jobs-to-Be-Done (JTBD)

### Owner JTBD - Survival Mode

| When I... | I want to... | So I can... |
|-----------|--------------|-------------|
| Wake up Monday | Know my cash position and runway | Start the week with confidence |
| See a big material bill | Understand impact on next 4 weeks | Decide if I need to accelerate collections |
| Approach slow season | See forecasted cash valley | Plan for reduced crew or line of credit |
| Have a surprise expense | See updated forecast immediately | Adjust spending or collections |

### Owner JTBD - Growth Mode

| When I... | I want to... | So I can... |
|-----------|--------------|-------------|
| Consider hiring | See overhead impact on breakeven | Make informed hiring decision |
| Get offered a big job | Model cash flow impact | Decide if I can fund the job |
| Think about raising prices | See margin improvement potential | Set pricing strategy |
| Review quarterly results | Understand which channels/job types perform | Focus marketing and sales |

### CFO JTBD

| When I... | I want to... | So I can... |
|-----------|--------------|-------------|
| Prepare for monthly call | See key metrics and trends | Focus conversation on what matters |
| Identify at-risk clients | See cash alerts across portfolio | Proactively reach out |
| Explain a variance | Drill into underlying drivers | Provide useful analysis |

---

## Functional Requirements

### FR-1: 13-Week Cash Flow Forecast

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Project cash inflows from open AR (by due date) | P0 |
| FR-1.2 | Project cash outflows from open AP (by due date) | P0 |
| FR-1.3 | Detect and project recurring expenses (rent, insurance, subscriptions) | P0 |
| FR-1.4 | Project payroll based on historical pattern + active crew count | P0 |
| FR-1.5 | Incorporate seasonal patterns from prior years | P1 |
| FR-1.6 | Update forecast daily with actuals | P0 |
| FR-1.7 | Show forecast confidence bands (optimistic/pessimistic) | P1 |

### FR-2: Scenario Modeling

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Model price change impact (+/- 5%, 10%, 15%) | P1 |
| FR-2.2 | Model volume change impact (+/- 10%, 20%) | P1 |
| FR-2.3 | Model overhead additions (new hire, truck, tool) | P1 |
| FR-2.4 | Model collection acceleration impact | P1 |
| FR-2.5 | Save and compare multiple scenarios | P2 |

### FR-3: Cash Alerts

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Alert when projected cash falls below threshold | P0 |
| FR-3.2 | Alert when AR aging exceeds threshold | P0 |
| FR-3.3 | Alert when AP concentration risk detected | P1 |
| FR-3.4 | Provide mitigation suggestions with each alert | P0 |
| FR-3.5 | Support customizable thresholds per client | P1 |

### FR-4: Owner Command Center Dashboard

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Cash position widget (current balance + trend) | P0 |
| FR-4.2 | 13-week forecast chart (with confidence band) | P0 |
| FR-4.3 | AR summary (total, current, 30+, 60+, 90+) | P0 |
| FR-4.4 | AP summary (total, current, upcoming) | P0 |
| FR-4.5 | Job margin sparklines (last 10 completed jobs) | P0 |
| FR-4.6 | Alert banner (active alerts with quick actions) | P0 |
| FR-4.7 | "Week at a glance" narrative summary | P1 |

### FR-5: Pricing & Margin Insights

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Calculate average margin by job type | P0 |
| FR-5.2 | Calculate average margin by lead source/channel | P1 |
| FR-5.3 | Track margin trend over time (trailing 6 months) | P0 |
| FR-5.4 | Identify top 3 margin improvers and detractors | P1 |
| FR-5.5 | Calculate breakeven price per square by job type | P1 |

### FR-6: CFO Weekly Brief

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-6.1 | Auto-generate weekly narrative summary | P0 |
| FR-6.2 | Include key metrics: cash, AR, AP, margin, runway | P0 |
| FR-6.3 | Highlight notable changes from prior week | P0 |
| FR-6.4 | Include 1-3 actionable recommendations | P0 |
| FR-6.5 | Deliver via email and/or Slack | P1 |
| FR-6.6 | Support owner preference for detail level | P2 |

---

## Non-Functional Requirements

### NFR-1: Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1.1 | Dashboard load time | < 3 seconds |
| NFR-1.2 | Forecast recalculation time | < 30 seconds |
| NFR-1.3 | Scenario model generation | < 5 seconds |

### NFR-2: Accuracy

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-2.1 | Week 4 forecast accuracy | ≤ 15% variance |
| NFR-2.2 | Week 13 forecast accuracy | ≤ 25% variance |
| NFR-2.3 | Margin calculation accuracy | 100% (ties to Books OS) |

### NFR-3: Usability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-3.1 | Mobile-responsive design | Full functionality on phone |
| NFR-3.2 | Time to insight | < 30 seconds from login |
| NFR-3.3 | Onboarding time | < 5 minutes to understand dashboard |

### NFR-4: Reliability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-4.1 | Alert delivery reliability | 99.9% |
| NFR-4.2 | Weekly brief delivery | Every Monday 7am local |
| NFR-4.3 | Data freshness | < 4 hours from source |

---

## UX & Narrative Guidance

### Design Principles

1. **Narrative-first**: Numbers tell, stories sell. Every dashboard element should answer a question in plain English.

2. **Glanceable**: Owner should understand health status within 5 seconds.

3. **Actionable**: Every insight includes a suggested next step.

4. **Calm technology**: Alerts are meaningful, not noisy. Don't cry wolf.

5. **Progressive disclosure**: Simple by default, detail on demand.

### Dashboard Narrative Goals

| Widget | Narrative Question Answered |
|--------|----------------------------|
| Cash Position | "Do I have enough money right now?" |
| Forecast Chart | "Will I run out of money in the next 3 months?" |
| AR Summary | "Who owes me and when should I expect it?" |
| AP Summary | "What do I owe and when?" |
| Margin Sparklines | "Are my recent jobs profitable?" |
| Alert Banner | "Is there anything I need to do today?" |

### Weekly Brief Structure

```markdown
## [Company Name] - Week of [Date]

### The Bottom Line
[One sentence summary: "Strong week" / "Watch cash in weeks 6-8" / etc.]

### This Week's Numbers
- **Cash Position**: $XX,XXX (↑ $X,XXX from last week)
- **Cash Runway**: X weeks at current burn
- **Open AR**: $XX,XXX (X invoices, oldest: X days)
- **Open AP**: $XX,XXX (next big payment: $X,XXX on [date])
- **Jobs Completed**: X jobs, $XX,XXX revenue, XX% avg margin

### What Changed
- [Notable change 1]
- [Notable change 2]
- [Notable change 3]

### Recommended Actions
1. [Action 1 with specific suggestion]
2. [Action 2 with specific suggestion]
3. [Action 3 with specific suggestion]

### Looking Ahead
[One paragraph on next 4-week outlook]
```

### Tone Guidelines

| Do | Don't |
|----|-------|
| "Cash looks tight in week 6. Consider..." | "WARNING: Cash critically low" |
| "Your margins improved 3% this month" | "Margin analysis complete" |
| "Insurance job #1234 is 45 days overdue" | "45+ AR detected" |
| "Adding a crew would increase breakeven by 12%" | "Scenario model complete" |

---

## Forecasting Methodology

### Cash Inflow Projection

```
For each open invoice:
  expected_date = IF aging < 30 THEN due_date
                  ELSE due_date + (avg_collection_days - 30)
  expected_amount = invoice_amount * collection_probability

Collection probability by aging:
  Current (0-30): 95%
  31-60 days: 80%
  61-90 days: 60%
  90+ days: 30%
```

### Cash Outflow Projection

```
For each open bill:
  expected_date = due_date (or payment_terms from vendor history)
  expected_amount = bill_amount

For recurring expenses:
  Detect from historical pattern (3+ occurrences)
  Project forward with seasonal adjustment

For payroll:
  expected_amount = crew_count * avg_hourly_rate * avg_hours * burden_rate
  expected_date = payroll_schedule (weekly/biweekly)
```

### Seasonal Adjustment

```
IF historical_data >= 12_months:
  seasonal_factor = (same_period_last_year / annual_average)
  adjusted_forecast = base_forecast * seasonal_factor
ELSE:
  seasonal_factor = industry_benchmark_for_region
```

---

## Success Metrics

### Engagement Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Weekly active users | 80% of customers | Login ≥1x per week |
| Dashboard views per week | 3+ per user | Page views |
| Weekly brief open rate | 60%+ | Email/Slack analytics |
| Alert acknowledgment rate | 90% within 24 hours | System tracking |

### Outcome Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Cash surprise incidents | Zero per quarter | Customer-reported |
| Forecast accuracy (Week 4) | ≤ 15% variance | Actual vs forecast |
| Owner confidence score | ≥ 8/10 | Quarterly survey |
| Action implementation rate | 40% of recommendations | Follow-up tracking |

### Business Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Upsell to CFO tier | 30% of Books OS customers | Conversion rate |
| NPS for Command Center | ≥ 50 | Quarterly survey |
| Feature as sales differentiator | 60% of won deals cite | Win/loss interviews |

---

## Integration Points

### From Books OS

- Account balances (current cash)
- Open AR with aging
- Open AP with due dates
- Completed jobs with margins
- Transaction patterns for recurring detection

### From Field Service (Jobber/ServiceTitan)

- Active job pipeline with estimated values
- Scheduled job dates
- Job completion status

### To External Systems

- Email (weekly brief delivery)
- Slack (alerts and weekly brief)
- SMS (critical alerts, optional)

---

## Scenario Planning Examples

### Scenario 1: Crew Addition

**Input**:
- New hire cost: $55,000/year fully loaded
- Expected revenue per crew: $180,000/year

**Output**:
- Monthly overhead increase: $4,583
- Breakeven revenue increase needed: $5,500/month (at 83% margin)
- Payback period: 4 months at full utilization
- Cash impact: -$15,000 first quarter (training ramp)

### Scenario 2: Price Increase

**Input**:
- Current average price per square: $350
- Proposed increase: 10%

**Output**:
- New average price: $385
- Margin improvement: 8 percentage points
- Breakeven volume reduction tolerance: 18%
- Annual profit impact at same volume: +$42,000

### Scenario 3: Collection Acceleration

**Input**:
- Current average collection: 38 days
- Target: 25 days (through deposit requirements)

**Output**:
- One-time cash benefit: $32,000
- Ongoing working capital improvement: $18,000
- Suggested tactics: 25% deposit on jobs >$5,000

---

## Out of Scope for v1

- Lending/LOC integration and recommendations
- Tax planning and projection
- Multi-year budget planning
- Benchmark comparison to industry
- What-if scenarios beyond core 4 (price, volume, overhead, collections)
- Real-time bank feed (relies on QBO sync)

---

## Appendix: Dashboard Wireframe Concept

```
┌─────────────────────────────────────────────────────────────────┐
│  [ALERT BANNER]  ⚠️ Cash projected below $10K in Week 6        │
│                     → View details  |  Dismiss                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐  ┌──────────────────────┐            │
│  │    CASH POSITION     │  │   13-WEEK FORECAST    │            │
│  │                      │  │                      │            │
│  │     $47,230         │  │   ~~~~/\~~~          │            │
│  │     ↑ $8,200        │  │  /    \/  \~~~       │            │
│  │    vs last week     │  │ /          \  \      │            │
│  │                      │  │/            \__\    │            │
│  │  Runway: 8 weeks    │  │ W1  W4  W7  W10 W13 │            │
│  └──────────────────────┘  └──────────────────────┘            │
│                                                                 │
│  ┌──────────────────────┐  ┌──────────────────────┐            │
│  │   AR SUMMARY         │  │   AP SUMMARY         │            │
│  │                      │  │                      │            │
│  │  Total: $68,400     │  │  Total: $31,200      │            │
│  │  ▓▓▓▓▓▓░░░░ 62%     │  │  Due this week: $12K │            │
│  │  Current             │  │  Due next week: $8K  │            │
│  │  ▓▓░░░░░░░░ 24%     │  │                      │            │
│  │  31-60 days          │  │  Largest: ABC Supply │            │
│  │  ░░░░░░░░░░ 14%     │  │           $8,400     │            │
│  │  60+ days            │  │                      │            │
│  └──────────────────────┘  └──────────────────────┘            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  RECENT JOB MARGINS                                      │   │
│  │                                                          │   │
│  │  Job #1234  ████████████████░░░░  42%  $4,200           │   │
│  │  Job #1233  ████████████░░░░░░░░  31%  $2,100           │   │
│  │  Job #1232  ████████████████████  52%  $6,800           │   │
│  │  Job #1231  ██████████░░░░░░░░░░  28%  $1,900           │   │
│  │  Job #1230  ████████████████░░░░  41%  $3,400           │   │
│  │                                     Avg: 39%             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
