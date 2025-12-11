# Spec-Kit Constitution: Books OS + CFO for Roofers

> **Version**: 1.0.0  
> **Last Updated**: 2025-12-11  
> **Status**: Active  

---

## Objective Statement

**Every roofing contractor on Spec-OS has clean, job-costed books and a rolling 13-week cash forecast without needing a full-time bookkeeper or CFO.**

This system transforms back-office operations from a liability into a strategic advantage, enabling roofing business owners to:
- Close books within 5 business days of month-end
- Understand true job-level profitability in real-time
- Forecast cash with confidence through seasonal cycles
- Make data-driven decisions on pricing, hiring, and growth

---

## Non-Negotiables

### Financial Integrity

| Principle | Enforcement |
|-----------|-------------|
| **Books close by the 7th business day** | Automated close orchestrator with escalation workflows |
| **All revenue and COGS are job-tagged** | Validation rules block uncategorized transactions from posting |
| **Double-entry compliance** | All transactions use python-accounting with GAAP/IFRS ledger enforcement |
| **No manual Excel models** | Every recurring workflow lives in Spec-OS + accounting system |
| **Audit trail required** | Every transaction, categorization, and adjustment logs actor + timestamp |

### System Boundaries

| Boundary | Rule |
|----------|------|
| **No auto-posting adjusting entries** | All adjusting entries require human sign-off in v1 |
| **Human approval for amounts > $5,000** | Large transactions route to human review queue |
| **No credential storage in plaintext** | All API keys and secrets use encrypted vault (AWS Secrets Manager / Supabase Vault) |
| **Multi-tenant isolation** | Row-level security enforced; tenant_id filters on every query |

### Operational Standards

| Standard | Requirement |
|----------|-------------|
| **Single source of truth** | QuickBooks Online is system of record; Spec-OS syncs and enriches |
| **Field service integration mandatory** | Job data must flow from Jobber/ServiceTitan for job-costing |
| **Exception handling** | Every automated process has defined exception paths with human escalation |

---

## Automation Principles

### The 80/20 Rule
**Target 80%+ touchless processing** while maintaining quality through strategic human intervention.

```
┌─────────────────────────────────────────────────────────────────┐
│  AUTOMATION TIERS                                               │
├─────────────────────────────────────────────────────────────────┤
│  Tier 1: Full Auto (90%+ touchless)                            │
│  • Invoice data extraction (OCR → structured data)              │
│  • Transaction categorization (known patterns)                  │
│  • Bank reconciliation matching                                 │
│  • Three-way matching within tolerance                          │
│  • Recurring journal entries                                    │
│  • Standard financial report generation                         │
├─────────────────────────────────────────────────────────────────┤
│  Tier 2: Assisted (50-70% touchless)                           │
│  • Complex invoice matching (multi-PO)                          │
│  • New vendor setup and verification                            │
│  • Unusual transaction categorization                           │
│  • Progress billing calculations                                │
│  • Lien waiver collection from subs                            │
├─────────────────────────────────────────────────────────────────┤
│  Tier 3: Human Required                                         │
│  • Approval decisions above thresholds                          │
│  • Change order evaluation                                      │
│  • Client communication                                         │
│  • Tax strategy decisions                                       │
│  • Financial statement certification                            │
│  • Complex reconciliation exceptions                            │
└─────────────────────────────────────────────────────────────────┘
```

### Classification Strategy

Use tiered classification for optimal accuracy/cost:

1. **Rules-based** (first pass): 98%+ accuracy on matched patterns, zero marginal cost
2. **ML fallback** (Random Forest/XGBoost): 90-94% accuracy for unmatched
3. **LLM routing** (last resort): Only for complex/ambiguous requiring reasoning

### Human-in-the-Loop Design

| Confidence Level | Action |
|------------------|--------|
| ≥ 95% | Auto-commit with logging |
| 80-94% | Auto-commit with flagged review queue |
| 60-79% | Draft state, human confirmation required |
| < 60% | Reject to exception queue with context |

---

## Key Performance Indicators (KPIs)

### Books OS Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Month-end close time** | ≤ 5 business days | Days from period end to books closed |
| **Auto-categorization rate** | ≥ 85% after 3 months | % transactions requiring no human intervention |
| **Exception rate** | < 10% | % transactions routed to exception queue |
| **Processing time per invoice** | < 30 seconds | Average OCR → categorized → staged |
| **Classification accuracy** | ≥ 95% | Verified correct categorizations / total |
| **Job-tagging compliance** | 100% revenue/COGS | % revenue and COGS with valid job assignment |

### Finance Command Center Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Forecast accuracy** | ≤ 15% variance | Actual vs forecast cash position at week 4 |
| **Owner engagement** | Weekly login | % of owners accessing command center ≥ 1x/week |
| **Alert response time** | < 24 hours | Time from cash alert to owner acknowledgment |
| **Cash crunch prevention** | Zero surprises | Count of unforecasted cash shortfalls |

### System Health Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Sync freshness** | < 4 hours | Max age of QBO/field-service data |
| **API uptime** | 99.5% | QBO/Jobber/ServiceTitan integration availability |
| **Processing backlog** | 0 at EOD | Unprocessed transactions at end of business day |

---

## Governance

### Change Control

- **Schema changes**: Require PRD update + migration plan
- **Agent behavior changes**: Require A/B testing plan + rollback procedure
- **Threshold changes**: Require finance team sign-off

### Compliance Requirements

- **SOC 2 Type 1** readiness by beta launch
- **SOC 2 Type 2** within 12 months of GA
- **GAAP/IFRS** compliant reporting at all times
- **State-specific lien waiver** compliance for statutory states

### Exception Escalation Path

```
┌─────────────────────────────────────────────────────────────────┐
│  ESCALATION MATRIX                                              │
├──────────────────┬──────────────────────────────────────────────┤
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
