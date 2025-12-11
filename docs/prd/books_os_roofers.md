# PRD: Books OS for Roofers

> **Version**: 1.0.0  
> **Last Updated**: 2025-12-11  
> **Status**: Draft  
> **Owner**: Product Team  

---

## Problem Statement

Roofing contractors in the $1-10M revenue range face a consistent set of bookkeeping challenges:

1. **Messy books**: Transactions pile up uncategorized; reconciliations are months behind
2. **No job-level visibility**: Owners don't know which jobs are profitable until year-end (if ever)
3. **Slow closes**: Month-end takes 20+ days, delaying financial insight
4. **Single point of failure**: One bookkeeper holds all institutional knowledge
5. **Audit anxiety**: Books aren't clean enough to support lending, bonding, or exit

**The result**: Owners fly blind, making gut decisions on pricing, hiring, and growth that leave money on the table or create cash crunches.

**Market gap**: Current solutions either lack AI sophistication (legacy ERPs, manual bookkeepers) or lack construction-specific features (Digits, Zeni, Pilot). Briq and Adaptive.build target larger contractors ($10M+) at premium pricing ($499+/month).

---

## User Personas & Roles

### Primary: Roofing Business Owner / GM

| Attribute | Description |
|-----------|-------------|
| **Demographics** | 35-55 years old, runs 3-10 person crew |
| **Tech comfort** | Uses smartphone daily, comfortable with basic software |
| **Pain points** | Doesn't trust the numbers, dreads month-end, can't get job margins |
| **Goals** | Know if they're making money, make informed decisions, sleep better |
| **Time available** | 30 min/week for financials |

### Secondary: In-House Bookkeeper (Optional)

| Attribute | Description |
|-----------|-------------|
| **Demographics** | Part-time (10-20 hrs/week), often owner's spouse or admin |
| **Tech comfort** | Proficient in QBO, learns new tools slowly |
| **Pain points** | Overwhelmed during busy season, unclear on construction accounting |
| **Goals** | Clear instructions, fewer surprises, defined responsibilities |

### System Actors: Spec-OS Agents

| Agent | Role |
|-------|------|
| **Classification Agent** | Auto-categorizes transactions with confidence scoring |
| **Close Orchestrator** | Manages month-end checklist, assigns tasks, tracks completion |
| **Anomaly Detector** | Flags unusual transactions or patterns for human review |
| **Report Generator** | Produces financial statements and job reports on demand |

---

## Jobs-to-Be-Done (JTBD)

### Owner JTBD

| When I... | I want to... | So I can... |
|-----------|--------------|-------------|
| Look at my phone on Monday | See a simple cash/AR/AP summary | Know if the week will be okay |
| Finish a job | Know my actual margin vs estimate | Price future jobs better |
| Approach month-end | Have confidence close will happen | Focus on running the business |
| Need a loan or bond | Provide clean financials quickly | Access capital without stress |
| Consider hiring/equipment | Understand true overhead capacity | Make informed growth decisions |

### Bookkeeper JTBD

| When I... | I want to... | So I can... |
|-----------|--------------|-------------|
| Start the month-end close | Have a clear checklist of tasks | Know exactly what needs doing |
| See an unknown vendor | Get a suggested category with context | Make decisions faster |
| Process a stack of invoices | Have them pre-categorized | Focus on exceptions only |
| Get asked about a job | Pull up job-level P&L quickly | Answer the owner's question |

---

## Functional Requirements

### FR-1: Data Integration

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Sync transactions from QuickBooks Online via OAuth | P0 |
| FR-1.2 | Sync jobs from Jobber or ServiceTitan | P0 |
| FR-1.3 | Incremental sync with < 4 hour latency | P0 |
| FR-1.4 | Handle sync failures with retry and alerting | P0 |
| FR-1.5 | Support bank feed data from QBO | P1 |

### FR-2: Chart of Accounts Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Provide roofing-optimized CoA template | P0 |
| FR-2.2 | Map incoming transactions to CoA accounts | P0 |
| FR-2.3 | Support custom account additions | P1 |
| FR-2.4 | Maintain cost code hierarchy (labor, materials, equipment, subs, overhead) | P0 |

### FR-3: Transaction Categorization

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Auto-categorize transactions using tiered classification | P0 |
| FR-3.2 | Assign confidence scores to each categorization | P0 |
| FR-3.3 | Route low-confidence transactions to review queue | P0 |
| FR-3.4 | Support human override with feedback capture | P0 |
| FR-3.5 | Learn from corrections to improve future accuracy | P1 |
| FR-3.6 | Explain categorization reasoning on demand | P2 |

### FR-4: Job Costing

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Link transactions to jobs from field service system | P0 |
| FR-4.2 | Calculate job-level revenue, COGS, and margin | P0 |
| FR-4.3 | Alert on transactions missing job assignment | P0 |
| FR-4.4 | Support job budget vs actual comparison | P1 |
| FR-4.5 | Track labor hours by job (if time data available) | P2 |

### FR-5: Month-End Close

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Generate month-end close checklist from template | P0 |
| FR-5.2 | Auto-assign tasks to agents vs humans | P0 |
| FR-5.3 | Track task completion status with due dates | P0 |
| FR-5.4 | Send notifications for overdue tasks | P0 |
| FR-5.5 | Block close until all P0 tasks complete | P0 |
| FR-5.6 | Log close certification with signoff | P1 |

### FR-6: Financial Reporting

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-6.1 | Generate P&L (total and by division/job type) | P0 |
| FR-6.2 | Generate Balance Sheet | P0 |
| FR-6.3 | Generate AR Aging Report | P0 |
| FR-6.4 | Generate AP Aging Report | P0 |
| FR-6.5 | Generate Job Profitability Report | P0 |
| FR-6.6 | Export reports to PDF | P1 |

### FR-7: Exception Handling

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-7.1 | Maintain exception queue with context | P0 |
| FR-7.2 | Categorize exceptions by type (unknown vendor, duplicate, etc.) | P0 |
| FR-7.3 | Support batch resolution actions | P1 |
| FR-7.4 | Track exception resolution time | P1 |

---

## Non-Functional Requirements

### NFR-1: Security & Compliance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1.1 | Multi-tenant data isolation | Zero cross-tenant data access |
| NFR-1.2 | Encryption at rest and in transit | AES-256, TLS 1.3 |
| NFR-1.3 | SOC 2 Type 1 readiness | By beta launch |
| NFR-1.4 | Audit logging for all financial operations | 100% coverage |
| NFR-1.5 | No auto-posting of adjusting entries without human approval | v1 requirement |

### NFR-2: Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-2.1 | Transaction categorization latency | < 2 seconds |
| NFR-2.2 | Report generation time | < 10 seconds |
| NFR-2.3 | Dashboard load time | < 3 seconds |
| NFR-2.4 | Sync latency from source systems | < 4 hours |

### NFR-3: Reliability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-3.1 | System uptime | 99.5% |
| NFR-3.2 | Data durability | 99.999999999% (11 nines) |
| NFR-3.3 | Recovery Point Objective (RPO) | < 1 hour |
| NFR-3.4 | Recovery Time Objective (RTO) | < 4 hours |

### NFR-4: Auditability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-4.1 | Every transaction change logs actor + timestamp | 100% |
| NFR-4.2 | Every categorization decision logs confidence + source | 100% |
| NFR-4.3 | Audit trail exportable to CSV | On demand |

### NFR-5: Extensibility

| ID | Requirement | Notes |
|----|-------------|-------|
| NFR-5.1 | Support additional field service integrations | Housecall Pro, Roofr |
| NFR-5.2 | Support Xero as alternative to QBO | v2 consideration |
| NFR-5.3 | Support additional trades | HVAC, plumbing, electrical |

---

## Success Metrics

### Efficiency Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Manual bookkeeping hours/month | 20-40 hrs | < 10 hrs | Time tracking |
| Month-end close time | 20+ days | ≤ 5 days | Days from period end to certified close |
| Transaction processing time | 5 min/tx | < 30 sec/tx | System metrics |

### Quality Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Auto-categorization rate | 0% | ≥ 85% (after 3 mo) | % touchless transactions |
| Categorization accuracy | N/A | ≥ 95% | Sample audit |
| Exception rate | N/A | < 10% | % to exception queue |
| Job-tagging compliance | ~50% | 100% | % revenue/COGS with job |

### Business Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Customer retention | N/A | > 90% annual | Churn rate |
| NPS | N/A | > 40 | Quarterly survey |
| Time to value | N/A | < 30 days | First successful close |

---

## User Stories (Sample)

### Epic: Transaction Categorization

```
As a bookkeeper
I want transactions auto-categorized with confidence scores
So that I only review exceptions, saving hours per week

Acceptance Criteria:
- Transactions appear in categorization queue with suggested category
- Confidence score displayed (High/Medium/Low)
- High-confidence (>95%) auto-committed without review
- One-click approve/reject/recategorize for Medium/Low
- Corrections feed back to improve future categorization
```

### Epic: Month-End Close

```
As an owner
I want to see month-end close status at a glance
So that I know if we're on track without chasing the bookkeeper

Acceptance Criteria:
- Dashboard shows close checklist with % complete
- Each task shows assignee (agent vs human) and due date
- Overdue tasks highlighted with notification sent
- Close cannot be certified until all P0 tasks complete
```

### Epic: Job Profitability

```
As an owner
I want to see profit margin for each completed job
So that I can identify which job types are most profitable

Acceptance Criteria:
- Job Profitability Report shows revenue, COGS, margin per job
- Filterable by date range, job type, crew
- Margin calculation includes labor burden (20%)
- Comparison to estimated margin (if estimate available)
```

---

## Out of Scope for v1

- AIA progress billing (G702/G703) - move to v1.1
- Lien waiver automation - move to v1.1
- WIP schedule automation - move to v1.1
- Xero integration - v2
- Multi-entity support - v2
- In-depth tax advisory - v2
- Custom report builder - v2

---

## Dependencies

| Dependency | Owner | Risk |
|------------|-------|------|
| QBO API access | Intuit | API rate limits, webhook reliability |
| Jobber API access | Jobber | Limited field availability |
| ServiceTitan API access | ServiceTitan | Enterprise-tier required |
| OpenAI/Claude API | Anthropic/OpenAI | Cost, rate limits |
| PaddleOCR model accuracy | Open source | May need fine-tuning |

---

## Appendix: Data Flow Diagram

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  QuickBooks │    │   Jobber/   │    │    Bank     │
│   Online    │    │ ServiceTitan│    │    Feed     │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       │    OAuth/API     │                  │
       ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────┐
│                    ETL Pipeline                      │
│  (Incremental Sync, Normalization, Deduplication)   │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                   Spec-OS Database                   │
│  (Supabase PostgreSQL + Row-Level Security)          │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │
│  │accounts│ │  jobs  │ │invoices│ │vendors │        │
│  └────────┘ └────────┘ └────────┘ └────────┘        │
│  ┌──────────────┐ ┌────────────┐ ┌──────────────┐   │
│  │transactions  │ │ job_costs  │ │ close_tasks  │   │
│  │  _raw        │ │            │ │              │   │
│  └──────────────┘ └────────────┘ └──────────────┘   │
└─────────────────────────┬───────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ Classif. │   │  Close   │   │ Anomaly  │
    │  Agent   │   │Orchestr. │   │ Detector │
    └──────────┘   └──────────┘   └──────────┘
          │               │               │
          └───────────────┼───────────────┘
                          │
                          ▼
              ┌───────────────────┐
              │  Owner Dashboard  │
              │  Reports & Alerts │
              └───────────────────┘
```
