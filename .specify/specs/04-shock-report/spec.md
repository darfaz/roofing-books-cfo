# Shock Report (Valuation Gap Analysis) Specification

> **Feature**: 04-shock-report
> **Status**: Implemented
> **Priority**: P0 (Core)
> **Last Updated**: 2026-01-02

---

## Overview

The Shock Report is the "WOW moment" feature that reveals the gap between what an owner thinks their business is worth vs. what a buyer would actually pay. It analyzes EBITDA adjustments, multiple penalties, and provides prioritized value unlocks.

**Target User**: Owner considering exit (1-5 year horizon)
**Access Frequency**: Quarterly
**Key Question Answered**: "What is my business really worth to a buyer, and why?"

---

## Core Concept: Owner View vs. Buyer View

| Perspective | What They See | Typical Gap |
|-------------|---------------|-------------|
| **Owner View** | Reported EBITDA + all add-backs | Optimistic (10x multiple) |
| **Buyer View** | Defensible EBITDA after haircuts | Conservative (3-5x multiple) |
| **The Shock** | Value gap in $ and % | Often 40-60% lower |

---

## User Stories

### US-01: See the Valuation Gap
**As a** roofing contractor owner
**I want to** see the difference between my expected valuation and what a buyer would pay
**So that** I understand the real market value of my business

**Acceptance Criteria**:
- [ ] Display owner's expected valuation (reported EBITDA × expected multiple)
- [ ] Display buyer's defensible valuation (adjusted EBITDA × buyer multiple range)
- [ ] Show the gap in $ and % prominently
- [ ] Visualize with side-by-side comparison

### US-02: Understand EBITDA Adjustments
**As a** roofing contractor owner
**I want to** see which of my add-backs a buyer would accept or reject
**So that** I understand what drives the EBITDA haircut

**Acceptance Criteria**:
- [ ] Categorize adjustments: Accepted, Rejected, Partial, Needs Review
- [ ] For each adjustment show:
  - Type (owner comp, personal expense, one-time, etc.)
  - Amount and accepted amount
  - Buyer's concern
  - Remediation action
- [ ] Calculate total EBITDA haircut
- [ ] Show confidence percentage

### US-03: See Multiple Penalties
**As a** roofing contractor owner
**I want to** see why a buyer would pay a lower multiple
**So that** I can improve the factors that drive multiple expansion

**Acceptance Criteria**:
- [ ] List penalties by Matador driver (6 drivers)
- [ ] For each penalty show:
  - Driver name and score (0-100)
  - Penalty amount (e.g., -1.5x)
  - Buyer's concern
  - Remediation action and timeline
  - Effort level
- [ ] Show resulting multiple vs. baseline

### US-04: View Prioritized Value Unlocks
**As a** roofing contractor owner
**I want to** see prioritized actions to recover lost value
**So that** I know what to work on first

**Acceptance Criteria**:
- [ ] List value unlocks sorted by EV impact
- [ ] For each unlock show:
  - Title and description
  - EBITDA impact
  - Multiple impact
  - Total EV impact
  - Timeline and effort level
- [ ] Mark locked vs. preview items (paywall)
- [ ] Enable "Start Working On This" action

### US-05: Download PDF Report
**As a** roofing contractor owner
**I want to** download a PDF of the shock report
**So that** I can share with partners, advisors, or family

**Acceptance Criteria**:
- [ ] Generate professional PDF with all sections
- [ ] Include company name and date
- [ ] Track download event in analytics

---

## Matador Driver Model

| Driver | Weight | What Buyers Investigate |
|--------|--------|------------------------|
| **Management Independence** | High | Can business run without owner? Hours, key decisions |
| **Financial Records Quality** | High | Clean books, accurate job costing, audit-ready |
| **Recurring Revenue** | Medium | Maintenance contracts, repeat customer rate |
| **Operational Systems** | Medium | SOPs, CRM, scheduling software, documented processes |
| **Customer Base Diversity** | Medium | No customer >15% of revenue, geographic spread |
| **Market Outlook** | Low | Local construction activity, competition, economic trends |

### Scoring Impact

| Score Range | Tier | Multiple Impact |
|-------------|------|-----------------|
| 0-40 | Below Average | -1.0 to -2.0x |
| 41-70 | Average | -0.3 to -0.7x |
| 71-100 | Above Average | +0.0 to +0.5x |

---

## EBITDA Adjustment Types

| Type | Description | Typical Treatment |
|------|-------------|-------------------|
| `owner_compensation` | Owner salary above market rate | Partial (normalize to market) |
| `personal_expense` | Personal expenses run through business | Rejected (haircut) |
| `one_time_revenue` | Non-recurring revenue (insurance claim) | Rejected |
| `one_time_expense` | Non-recurring expense (legal settlement) | Accepted (add back) |
| `non_recurring` | Items unlikely to repeat | Case-by-case |
| `related_party` | Transactions with owner-related entities | Scrutinized |
| `discretionary` | Owner perks (auto, travel, club) | Usually rejected |
| `non_operating` | Income/expense unrelated to operations | Excluded |

### Personal Expense Detection Patterns

| Pattern | Rejection Probability |
|---------|----------------------|
| Auto/Vehicle (not commercial) | 50% |
| Travel/Entertainment | 60% |
| Health Insurance (owner only) | 30% |
| Phone/Tech (personal devices) | 40% |
| Memberships/Clubs | 90% |

---

## Data Model

### Shock Report
```typescript
interface ShockReportData {
  // Owner's view
  owner_view: {
    reported_revenue: number
    reported_ebitda: number
    reported_owner_comp: number
    reported_addbacks: number
    expected_multiple: number  // Usually 10x
    expected_valuation: number
  }

  // Buyer's view
  buyer_view: {
    defensible_ebitda: number
    defensible_sde: number
    buyer_multiple_low: number
    buyer_multiple_high: number
    buyer_valuation_low: number
    buyer_valuation_high: number
  }

  // The gap
  gap_analysis: {
    ebitda_haircut: number
    ebitda_haircut_pct: number
    multiple_penalty: number
    value_gap: number
    value_gap_pct: number
    total_recoverable: number
  }

  // Breakdowns
  adjustments: EbitdaAdjustment[]
  penalties: MultiplePenalty[]
  unlocks: ValueUnlock[]

  // Data quality
  data_quality: {
    qbo_range_start: string
    qbo_range_end: string
    transaction_count: number
    invoice_count: number
    expense_count: number
    confidence_score: number
  }

  tier: 'below_avg' | 'avg' | 'above_avg'
  generated_at: string
}
```

### EBITDA Adjustment
```typescript
interface EbitdaAdjustment {
  id: string
  type: AdjustmentType
  category: 'accepted' | 'rejected' | 'partial' | 'needs_review'
  description: string
  amount: number
  accepted_amount: number
  transaction_ids: string[]
  vendor_names: string[]
  buyer_concern: string
  rejection_reason?: string
  is_recoverable: boolean
  remediation_action?: string
  remediation_effort?: 'low' | 'medium' | 'high'
  remediation_impact?: number
}
```

### Multiple Penalty
```typescript
interface MultiplePenalty {
  driver_key: string
  penalty_amount: number  // e.g., -1.5
  baseline_multiple: number
  resulting_multiple: number
  driver_score: number  // 0-100
  reason: string
  buyer_concern: string
  due_diligence_flag: string
  remediation_action: string
  remediation_timeline: string
  remediation_effort: 'low' | 'medium' | 'high'
  multiple_recovery: number
}
```

### Value Unlock
```typescript
interface ValueUnlock {
  id: string
  priority_rank: number
  title: string
  description: string
  action_type: 'ebitda_recovery' | 'multiple_expansion' | 'revenue_quality'
  ebitda_impact: number
  multiple_impact: number
  ev_impact: number
  effort_level: 'low' | 'medium' | 'high'
  timeline: string
  related_driver?: string
  is_locked: boolean  // Paywall
  is_preview: boolean
}
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/valuation/shock-report` | POST | Generate new shock report |
| `/api/valuation/shock-report/latest` | GET | Get most recent report |
| `/api/valuation/shock-report/pdf` | GET | Download PDF |
| `/api/valuation/shock-report/{id}/analytics` | POST | Log engagement event |

---

## UI Components

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│  THE VALUATION SHOCK REPORT              [Download PDF 📄]  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐    ┌─────────────────────┐        │
│  │   OWNER'S VIEW      │    │   BUYER'S VIEW      │        │
│  │   (What you think)  │    │   (What they'll pay)│        │
│  │                     │    │                     │        │
│  │   $3,500,000        │    │   $1,400,000 -      │        │
│  │                     │    │   $1,960,000        │        │
│  │   10x Multiple      │    │   4.0-5.5x Multiple │        │
│  │   $350K EBITDA      │    │   $280K Defensible  │        │
│  └─────────────────────┘    └─────────────────────┘        │
│                                                             │
│            THE GAP: -$1.5M to -$2.1M (-43% to -60%)       │
├─────────────────────────────────────────────────────────────┤
│  📊 EBITDA ADJUSTMENTS                         [Expand ▼]  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Haircut: $70,000 (20% of reported)                    │ │
│  │                                                        │ │
│  │ ✅ Accepted: Owner compensation $45K                  │ │
│  │ ❌ Rejected: Personal auto $12K                       │ │
│  │ ⚠️ Partial: Travel $8K → $3K accepted                │ │
│  │ 🔍 Review: Entertainment $5K                         │ │
│  └───────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  📉 MULTIPLE PENALTIES                         [Expand ▼]  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Baseline: 6.0x → Resulting: 4.5x                      │ │
│  │                                                        │ │
│  │ ❌ Management Independence: -1.0x                     │ │
│  │    Score: 35/100 | "Owner IS the business"            │ │
│  │    Fix: Hire operations manager (6-12 months)         │ │
│  │                                                        │ │
│  │ ⚠️ Financial Records: -0.3x                          │ │
│  │    Score: 65/100 | "Job costing inconsistent"         │ │
│  │    Fix: Implement job costing system (3 months)       │ │
│  └───────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  💰 VALUE UNLOCKS (Recover up to $850K)       [Expand ▼]  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ #1: Reduce owner hours from 50→20/week               │ │
│  │     EV Impact: +$400K | Effort: High | 6-12 months   │ │
│  │     [🔒 Unlock Details]                              │ │
│  │                                                        │ │
│  │ #2: Eliminate personal expenses                       │ │
│  │     EV Impact: +$250K | Effort: Low | 3 months       │ │
│  │     [Preview Available]                               │ │
│  └───────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  📊 DATA QUALITY                                           │
│  Period: Jan 2024 - Dec 2024 | 1,247 transactions         │
│  Confidence: 78% (⚠️ Some items need review)              │
└─────────────────────────────────────────────────────────────┘
```

---

## Analytics Events

Track engagement to understand user behavior:

| Event | When Fired |
|-------|------------|
| `report_generated` | New shock report created |
| `report_viewed` | Report page loaded |
| `section_expanded` | User expands a section |
| `pdf_downloaded` | PDF download initiated |
| `unlock_clicked` | User clicks on value unlock |
| `trial_cta_clicked` | User clicks trial/upgrade CTA |

---

## Review Checklist

- [ ] EBITDA haircut calculation is accurate
- [ ] Multiple penalties align with Matador driver scores
- [ ] Value unlocks are prioritized correctly by EV impact
- [ ] PDF generates correctly with all sections
- [ ] Data quality indicators are accurate
- [ ] Demo mode shows realistic gap scenario
- [ ] Analytics events fire correctly
