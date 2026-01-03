# CrewCFO Constitution

> **Version**: 2.0.0
> **Last Updated**: 2026-01-02
> **Status**: Active

---

## Mission Statement

**Transform roofing contractors from financially blind to financially empowered—delivering clean books, real-time cash visibility, and valuation intelligence that forces owners to confront the gap between what they think their business is worth and what buyers will actually pay.**

CrewCFO combines automated bookkeeping ("Books OS") with fractional CFO services through an integrated dashboard, enabling roofing business owners ($1-10M revenue) to:

- Close books within 5 business days of month-end
- Understand true job-level profitability in real-time
- Forecast cash with confidence through seasonal cycles
- See their business through a buyer's eyes (the "Shock Report")
- Take prioritized action to improve enterprise value

---

## Core Principles

### 1. Financial Truth Over Comfort

| Principle | Implementation |
|-----------|----------------|
| **Show the real numbers** | Never hide bad news; surface profit leaks, EBITDA haircuts, and multiple penalties prominently |
| **Buyer's perspective first** | Valuation views default to "what a buyer sees" not "what owner hopes" |
| **No vanity metrics** | Every metric must tie to cash, profitability, or enterprise value |
| **Defensible calculations** | All valuations use documented methodology with audit trails |

### 2. Automation with Accountability

| Principle | Enforcement |
|-----------|-------------|
| **80% touchless target** | Automate routine tasks; humans handle exceptions and approvals |
| **Confidence-based routing** | <80% confidence flags for human review; ≥80% auto-commits |
| **Audit everything** | Every transaction, categorization, and adjustment logs actor + timestamp |
| **No black boxes** | Users can always see *why* a decision was made |

### 3. Roofing-Specific Intelligence

| Principle | Application |
|-----------|-------------|
| **Industry benchmarks** | Compare against roofing-specific ratios (35% gross margin healthy, 10% net margin target) |
| **Job costing native** | Every revenue and COGS transaction ties to a job |
| **Seasonal awareness** | Cash forecasts account for roofing seasonality patterns |
| **PE buyer lens** | Valuation uses actual roofing M&A multiple data (3-7x EBITDA) |

---

## Non-Negotiables

### Financial Integrity

| Requirement | Enforcement |
|-------------|-------------|
| **Books close by day 7** | Automated close orchestrator with escalation workflows |
| **All revenue/COGS job-tagged** | Validation rules block uncategorized transactions |
| **Double-entry compliance** | GAAP/IFRS ledger enforcement on all entries |
| **No manual Excel models** | Every recurring workflow lives in the platform |

### Security & Privacy

| Requirement | Implementation |
|-------------|----------------|
| **Multi-tenant isolation** | Row-level security (RLS) enforced on every query |
| **No plaintext secrets** | All tokens/credentials encrypted at rest |
| **Human approval >$5,000** | Large transactions route to review queue |
| **No credential storage in code** | Environment variables + secure vaults only |

### Data Quality

| Requirement | Standard |
|-------------|----------|
| **Single source of truth** | QuickBooks Online is system of record |
| **Sync freshness** | Data no older than 4 hours |
| **Classification accuracy** | ≥85% auto-categorization after 90 days |
| **Valuation confidence** | Score 0-100; <80 requires human review |

---

## Automation Tiers

```
┌─────────────────────────────────────────────────────────────────┐
│  CONFIDENCE-BASED ROUTING                                        │
├─────────────────────────────────────────────────────────────────┤
│  ≥ 95%  │  Auto-commit with logging                              │
│  80-94% │  Auto-commit with flagged review queue                 │
│  60-79% │  Draft state, human confirmation required              │
│  < 60%  │  Reject to exception queue with context                │
└─────────────────────────────────────────────────────────────────┘
```

### Classification Strategy

1. **Rules-based** (first pass): 98%+ accuracy on matched patterns, zero marginal cost
2. **ML fallback** (Random Forest/XGBoost): 90-94% accuracy for unmatched
3. **LLM routing** (last resort): Only for complex/ambiguous requiring reasoning

---

## Key Performance Indicators

### Books OS Metrics

| Metric | Target |
|--------|--------|
| Month-end close time | ≤ 5 business days |
| Auto-categorization rate | ≥ 85% after 90 days |
| Exception rate | < 10% of transactions |
| Classification accuracy | ≥ 95% verified correct |
| Job-tagging compliance | 100% revenue/COGS |

### Finance Dashboard Metrics

| Metric | Target |
|--------|--------|
| Forecast accuracy | ≤ 15% variance at week 4 |
| Owner engagement | Weekly login ≥ 70% of users |
| Alert response time | < 24 hours |
| Cash crunch prevention | Zero unforecasted shortfalls |

### Valuation Metrics

| Metric | Target |
|--------|--------|
| Shock report generation | < 30 seconds |
| Valuation confidence | > 80% for auto-approve |
| Value unlock completion | ≥ 3 items per quarter |
| Roadmap progress | 80% on-time completion |

### System Health

| Metric | Target |
|--------|--------|
| API uptime | 99.5% |
| Sync latency | < 5 minutes |
| Page load time | < 3 seconds |
| Error rate | < 0.1% of requests |

---

## Matador Driver Model

The 6 value drivers that determine valuation multiples:

| Driver | Weight | What Buyers Look For |
|--------|--------|---------------------|
| **Management Independence** | High | Can it run without the owner? |
| **Financial Records Quality** | High | Clean books, accurate job costing |
| **Recurring Revenue** | Medium | Maintenance contracts, repeat customers |
| **Operational Systems** | Medium | Documented SOPs, CRM, scheduling |
| **Customer Base Diversity** | Medium | No single customer >15% of revenue |
| **Market Outlook** | Low | Geographic demand, competition |

### Tier → Multiple Mapping

| Tier | EBITDA Multiple | SDE Multiple | Characteristics |
|------|-----------------|--------------|-----------------|
| Below Average | 2.5-3.5x | 2.0-3.0x | Owner-dependent, weak records |
| Average | 4.0-5.5x | 3.0-4.5x | Decent operations, some systems |
| Above Average | 6.0-8.0x | 4.5-6.0x | Management team, recurring revenue |

---

## Governance

### Change Control

- **Schema changes**: Require spec update + migration plan
- **Agent behavior changes**: Require A/B testing + rollback procedure
- **Threshold changes**: Require finance team sign-off
- **Feature launches**: Require spec approval + QA sign-off

### Compliance Requirements

- **SOC 2 Type 1** readiness by beta launch
- **SOC 2 Type 2** within 12 months of GA
- **GAAP/IFRS** compliant reporting
- **State-specific** lien waiver compliance

### Exception Escalation Path

```
┌──────────────────┬──────────────────────────────────────────────┐
│  Level 1         │  Auto-retry with alternative strategy        │
│  Level 2         │  Queue for batch human review (next day)     │
│  Level 3         │  Immediate human review (same day)           │
│  Level 4         │  Client contact required                     │
│  Level 5         │  Senior finance escalation                   │
└──────────────────┴──────────────────────────────────────────────┘
```

---

## Versioning

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-11 | Initial constitution |
| 2.0.0 | 2026-01-02 | Added valuation principles, Matador model, expanded metrics |
