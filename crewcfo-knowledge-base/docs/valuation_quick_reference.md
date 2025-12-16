# CrewCFO Valuation Intelligence Module - Quick Reference

## 5 Core Features

### Feature A: Real-time Valuation Engine
- Computes TTM SDE and TTM EBITDA
- Renders valuation ranges using SDE/EBITDA multiples
- Applies Matador tier multipliers (Below Avg ~3×, Avg ~4.5-5×, Above Avg ~7×+)
- Provides "value delta" view

### Feature B: Value Driver Scoring Engine
Scores across 6 Matador-style drivers:
1. Management Independence
2. Financial Records Quality
3. Recurring Revenue
4. Operational Systems
5. Customer Base Diversity
6. Market Outlook

### Feature C: Scenario Simulator
- No-Excel "what-if" modeling
- Adjustable levers: recurring revenue, owner hours, crew productivity, gross margin
- Recalculates EBITDA/SDE uplift and multiple uplift

### Feature D: Exit Readiness & Deal Room Builder
- Builds due diligence checklist
- Auto-assembles artifacts (financials, tax returns, AR/AP aging, KPIs)
- Produces CIM-like packet outline

### Feature E: Valuation Roadmap Agent
- Weekly operational + finance tasks
- Monthly close discipline + KPI improvements
- Quarterly "Spec Jam" review cadence

## Database Schema (Minimal)

```sql
-- Core tables
valuation_snapshots(tenant_id, as_of_date, ttm_revenue, ttm_sde, 
  ttm_ebitda, tier, multiple_low, multiple_high, ev_low, ev_high, 
  confidence_score, drivers_json, audit_log_ref)

driver_scores(tenant_id, as_of_date, driver_key, score, 
  evidence_refs, computed_by, confidence)

roadmap_items(tenant_id, created_at, driver_key, expected_impact_ev, 
  effort_level, automation_tier, task_refs[])
```

## Automation Tiers (Books OS Constitution)
- ≥95% confidence: auto-commit
- 80-94%: commit + flagged review  
- 60-79%: draft, human confirmation
- <60%: exception queue
- Human approval required for amounts > $5,000
