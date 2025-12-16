# Valuation Intelligence — Integration Seams

## Bounded Context
valuation_intelligence

## Reads From
- Books OS financial snapshots
- Job costing summaries (if available)
- Questionnaire inputs

## Writes To
- valuation_snapshots
- driver_scores
- roadmap_items
- deal_room_artifacts
- audit_logs

## Automation & Governance
- Rules-first, deterministic
- LLMs only for narrative/explanation
- Human approval required for high-impact adjustments
- No auto-posting of accounting entries
