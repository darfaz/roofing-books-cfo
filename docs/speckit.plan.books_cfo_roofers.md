# Spec-Kit Plan: Books OS + CFO for Roofers

> **Version**: 1.0.0  
> **Last Updated**: 2025-12-11  
> **Target ICP**: Roofing contractors, $1-10M revenue, 3+ crews  

---

## Executive Summary

This plan outlines the phased build from discovery through productization of an AI-powered bookkeeping and fractional CFO platform for roofing contractors. Total timeline: 20 weeks to beta launch.

---

## Phase 0: Discovery & Standardization (Weeks 1-2)

**Objective**: Lock in standards and validate assumptions before writing code.

### Epic 0.1: Chart of Accounts Standardization

| Deliverable | Description |
|-------------|-------------|
| Roofing-optimized CoA template | Trade-specific account structure with cost codes |
| Job type taxonomy | Residential repair, residential replacement, commercial, storm/insurance |
| Cost code hierarchy | Labor, materials, equipment, subcontractors, overhead |

**Acceptance Criteria**:
- [ ] CoA maps to QBO standard accounts
- [ ] Supports 60/40 labor/materials rule tracking
- [ ] Enables P&L by division and job type

### Epic 0.2: Month-End Close Playbook

| Deliverable | Description |
|-------------|-------------|
| Standard close checklist | 25-item checklist with owner/agent assignments |
| Timeline template | Day-by-day close schedule |
| Exception catalog | Known exception types with resolution paths |

### Epic 0.3: Persona & Scenario Documentation

| Deliverable | Description |
|-------------|-------------|
| "Month in the life" scenarios | 5 documented scenarios: busy month, slow month, high AR, large material bills, insurance claims |
| User journey maps | Owner, bookkeeper, and CFO touchpoints |

### Milestone: Discovery Complete
- [ ] CoA template approved
- [ ] Close checklist validated with 3 pilot prospects
- [ ] Scenarios documented and reviewed

---

## Phase 1: Data Plumbing (Weeks 3-6)

**Objective**: Establish reliable data pipelines from source systems.

### Epic 1.1: QuickBooks Online Integration

| Task | Priority | Est. Hours |
|------|----------|------------|
| OAuth 2.0 flow implementation | P0 | 8 |
| Customer/Vendor sync adapter | P0 | 12 |
| Invoice/Bill sync adapter | P0 | 16 |
| Payment sync adapter | P0 | 8 |
| Journal entry read/write | P1 | 12 |
| Webhook receiver setup | P1 | 8 |

**Tech Stack**: `python-quickbooks` (MIT), FastAPI, PostgreSQL

### Epic 1.2: Field Service Integration

| Task | Priority | Est. Hours |
|------|----------|------------|
| Jobber OAuth + job sync | P0 | 16 |
| ServiceTitan OAuth + job sync | P1 | 20 |
| Job-to-transaction mapping logic | P0 | 12 |
| Invoice-to-job reconciliation | P0 | 8 |

### Epic 1.3: Supabase Schema & ETL

| Task | Priority | Est. Hours |
|------|----------|------------|
| Multi-tenant schema design | P0 | 16 |
| Row-level security policies | P0 | 8 |
| ETL pipeline (incremental sync) | P0 | 20 |
| Sync status monitoring | P1 | 8 |

**Output Tables**:
```
tenants, accounts, transactions_raw, transactions_categorized,
jobs, job_costs, invoices, payments, vendors, customers,
sync_history, integration_credentials
```

### Milestone: Data Pipeline Live
- [ ] QBO sync running hourly
- [ ] Jobber jobs syncing to `jobs` table
- [ ] < 5 minute sync latency achieved
- [ ] Zero data leakage between tenants verified

---

## Phase 2: Books OS Automation (Weeks 7-12)

**Objective**: Automate core bookkeeping workflows with AI agents.

### Epic 2.1: Classification & CoA Mapping Agent

| Task | Priority | Est. Hours |
|------|----------|------------|
| Rules engine for known patterns | P0 | 16 |
| ML classifier (XGBoost) training | P0 | 24 |
| LLM fallback with LangChain | P1 | 16 |
| Confidence scoring + routing | P0 | 12 |
| Feedback loop infrastructure | P1 | 16 |

**Target Accuracy**: 85% auto-categorization after 3-month learning period

### Epic 2.2: Invoice Processing Pipeline

| Task | Priority | Est. Hours |
|------|----------|------------|
| PaddleOCR integration | P0 | 12 |
| docTR field extraction | P0 | 16 |
| LangChain structured output parsing | P0 | 12 |
| Three-way matching logic | P1 | 16 |
| Exception queue UI | P1 | 20 |

### Epic 2.3: Month-End Close Orchestrator

| Task | Priority | Est. Hours |
|------|----------|------------|
| Close checklist generator | P0 | 12 |
| Task assignment engine (agent vs human) | P0 | 16 |
| Status tracking + notifications | P0 | 12 |
| Reconciliation automation | P1 | 20 |
| Close certification workflow | P1 | 12 |

### Epic 2.4: Job Costing Enforcement

| Task | Priority | Est. Hours |
|------|----------|------------|
| Job-transaction linking rules | P0 | 12 |
| Untagged transaction alerts | P0 | 8 |
| Job margin calculation engine | P0 | 16 |
| WIP schedule automation | P2 | 24 |

### Epic 2.5: Standard Financial Reports

| Task | Priority | Est. Hours |
|------|----------|------------|
| P&L by division/job type | P0 | 16 |
| Balance sheet generation | P0 | 12 |
| AR/AP aging reports | P0 | 12 |
| Job profitability report | P0 | 16 |

### Milestone: Books OS MVP Complete
- [ ] 70%+ transactions auto-categorized
- [ ] Month-end close checklist functional
- [ ] All standard reports generating
- [ ] Job costing operational

---

## Phase 3: Finance Command Center (Weeks 13-16)

**Objective**: Deliver CFO-grade insights and forecasting to owners.

### Epic 3.1: 13-Week Cashflow Engine

| Task | Priority | Est. Hours |
|------|----------|------------|
| AR projection from open invoices | P0 | 12 |
| AP projection from open bills | P0 | 12 |
| Recurring expense pattern detection | P0 | 16 |
| Payroll pattern integration | P0 | 12 |
| Weekly forecast recalculation | P0 | 8 |
| Scenario modeling (±10%, ±20%) | P1 | 16 |

### Epic 3.2: Pricing & Margin Insights

| Task | Priority | Est. Hours |
|------|----------|------------|
| Job type margin analysis | P0 | 16 |
| Breakeven price calculator | P1 | 12 |
| Material cost trend tracking | P1 | 12 |
| Crew productivity metrics | P2 | 16 |

### Epic 3.3: Owner Command Center Dashboard

| Task | Priority | Est. Hours |
|------|----------|------------|
| Cash runway visualization | P0 | 12 |
| AR/AP heatmap | P0 | 12 |
| Job margin sparklines | P0 | 8 |
| Alert banner system | P0 | 8 |
| Mobile-responsive design | P1 | 16 |

### Epic 3.4: CFO Weekly Brief Agent

| Task | Priority | Est. Hours |
|------|----------|------------|
| Dify/LangChain prompt engineering | P0 | 16 |
| KPI aggregation pipeline | P0 | 12 |
| Narrative generation | P0 | 16 |
| Email/Slack delivery | P1 | 8 |

### Milestone: Finance Command Center MVP Complete
- [ ] 13-week forecast generating weekly
- [ ] Owner dashboard live
- [ ] CFO brief delivering weekly
- [ ] < 15% forecast variance achieved

---

## Phase 4: Construction-Specific Features (Weeks 17-18)

**Objective**: Address roofing-specific compliance and billing needs.

### Epic 4.1: AIA Progress Billing

| Task | Priority | Est. Hours |
|------|----------|------------|
| G702/G703 form generation | P2 | 24 |
| Retainage calculation | P2 | 12 |
| Progress percentage tracking | P2 | 16 |

### Epic 4.2: Lien Waiver Tracking

| Task | Priority | Est. Hours |
|------|----------|------------|
| State template library (12 states) | P2 | 20 |
| Waiver status tracking | P2 | 12 |
| Payment-to-waiver workflow | P2 | 16 |

### Epic 4.3: AR/AP Follow-up Automation

| Task | Priority | Est. Hours |
|------|----------|------------|
| Aging-based reminder rules | P1 | 12 |
| Email template system | P1 | 8 |
| Escalation workflow | P1 | 12 |

### Milestone: Construction Features Complete
- [ ] AIA billing operational (if prioritized)
- [ ] Lien waiver tracking for priority states
- [ ] AR follow-up automation active

---

## Phase 5: Production Hardening (Weeks 19-20)

**Objective**: Prepare for beta launch with 5-10 pilot customers.

### Epic 5.1: Security & Compliance

| Task | Priority | Est. Hours |
|------|----------|------------|
| SOC 2 Type 1 documentation | P0 | 40 |
| Security audit remediation | P0 | 24 |
| Penetration testing | P1 | 16 |
| Secret rotation automation | P1 | 8 |

### Epic 5.2: Monitoring & Operations

| Task | Priority | Est. Hours |
|------|----------|------------|
| CloudWatch alerting setup | P0 | 12 |
| Error tracking (Sentry) | P0 | 8 |
| Performance dashboards | P1 | 12 |
| On-call runbooks | P0 | 16 |

### Epic 5.3: Onboarding & Migration

| Task | Priority | Est. Hours |
|------|----------|------------|
| Intake application | P0 | 20 |
| Credential collection workflow | P0 | 12 |
| Historical data migration scripts | P0 | 24 |
| Onboarding checklist automation | P1 | 12 |

### Milestone: Beta Launch Ready
- [ ] 5-10 pilot customers onboarded
- [ ] SOC 2 Type 1 documentation complete
- [ ] Monitoring and alerting operational
- [ ] < 1 hour onboarding time achieved

---

## Resource Requirements

### Team Structure

| Role | Allocation | Responsibilities |
|------|------------|------------------|
| Full-stack Engineer | 2 FTE | Backend, integrations, DB |
| ML/AI Engineer | 1 FTE | Classification agents, LLM integration |
| Frontend Engineer | 0.5 FTE | Dashboard, owner UX |
| Product Manager | 0.5 FTE | Requirements, testing, pilots |
| Finance SME | 0.25 FTE | CoA, close checklist, validation |

### Infrastructure Budget

| Component | Monthly Cost |
|-----------|--------------|
| Supabase Pro | $25 |
| AWS ECS/RDS | $100-150 |
| n8n Cloud (or self-hosted) | $0-50 |
| OpenAI API | $50-100 |
| Monitoring (Sentry, CloudWatch) | $25 |
| **Total** | **$200-350/month** |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| QBO API rate limits | Medium | High | Implement caching, batch operations |
| Field service API limitations | Medium | Medium | Prioritize Jobber (better API) |
| Low classification accuracy | Medium | High | Human-in-loop fallback, continuous training |
| Pilot customer churn | Low | High | Weekly check-ins, rapid issue resolution |
| SOC 2 timeline slip | Medium | Medium | Start documentation in Phase 1 |

---

## Success Criteria for Beta

| Metric | Target |
|--------|--------|
| Pilot customers | 5-10 active |
| Month-end close time | ≤ 7 days |
| Auto-categorization rate | ≥ 70% |
| Forecast accuracy | ≤ 20% variance |
| NPS | ≥ 40 |
| Churn | 0 during beta |
