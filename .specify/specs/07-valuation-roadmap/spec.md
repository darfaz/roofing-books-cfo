# Valuation Roadmap Specification

> **Feature**: 07-valuation-roadmap
> **Status**: Implemented
> **Priority**: P1 (High)
> **Last Updated**: 2026-01-02

---

## Overview

The Valuation Roadmap provides a prioritized action plan to improve value drivers. Items are linked to the 6 Matador drivers and categorized by operational cadence.

**Target User**: Owner, fractional CFO
**Access Frequency**: Weekly
**Key Question Answered**: "What should I work on this week/month/quarter to improve my valuation?"

---

## User Stories

### US-01: View Prioritized Roadmap
**As a** roofing contractor owner
**I want to** see a prioritized list of improvement actions
**So that** I know what to focus on to increase business value

**Acceptance Criteria**:
- [ ] Display roadmap items sorted by expected EV impact
- [ ] Show priority level (critical, high, medium, low)
- [ ] Show effort level (low, medium, high)
- [ ] Filter by driver, category, priority, or status

### US-02: Track Item Status
**As a** roofing contractor owner
**I want to** update the status of roadmap items
**So that** I can track my progress

**Acceptance Criteria**:
- [ ] Status options: pending, in_progress, completed, cancelled, blocked
- [ ] Update status with one click
- [ ] Show timestamp of last update
- [ ] Track completion date

### US-03: View by Driver
**As a** roofing contractor owner
**I want to** see roadmap items grouped by value driver
**So that** I can focus on improving specific drivers

**Acceptance Criteria**:
- [ ] Group items by the 6 Matador drivers
- [ ] Show driver score next to each group
- [ ] Calculate potential impact if all items completed

### US-04: View by Cadence
**As a** roofing contractor owner
**I want to** see roadmap items by operational cadence
**So that** I can integrate them into my workflow

**Acceptance Criteria**:
- [ ] Categories: Weekly Ops, Monthly Close, Quarterly Review, Strategic, Compliance
- [ ] Filter by category
- [ ] Show due dates where applicable

### US-05: See EV Impact
**As a** roofing contractor owner
**I want to** see the expected value impact of each item
**So that** I can prioritize high-impact activities

**Acceptance Criteria**:
- [ ] Display expected EV impact in dollars
- [ ] Show total potential EV if all items completed
- [ ] Indicate confidence level of estimates

---

## Roadmap Categories

| Category | Cadence | Examples |
|----------|---------|----------|
| `weekly_ops` | Weekly | Review AR aging, follow up on collections |
| `monthly_close` | Monthly | Close books, reconcile accounts, review P&L |
| `quarterly_review` | Quarterly | Driver score review, strategic planning |
| `strategic` | As needed | Hire manager, implement CRM, create SOPs |
| `compliance` | As needed | Update insurance, safety training, permits |

---

## Matador Drivers

| Driver Key | Driver Name | Example Items |
|------------|-------------|---------------|
| `management_independence` | Management Independence | Hire ops manager, document SOPs, reduce owner hours |
| `financial_records` | Financial Records | Clean up CoA, implement job costing, monthly close process |
| `recurring_revenue` | Recurring Revenue | Launch maintenance program, create service contracts |
| `operational_systems` | Operational Systems | Implement CRM, scheduling software, project management |
| `customer_diversity` | Customer Base Diversity | Diversify customer base, expand geographic coverage |
| `market_outlook` | Market Outlook | Geographic expansion, new service lines |

---

## Data Model

### Roadmap Item
```typescript
interface RoadmapItem {
  id: string
  tenant_id: string
  driver_key: string
  title: string
  description: string
  category: 'weekly_ops' | 'monthly_close' | 'quarterly_review' | 'strategic' | 'compliance'
  priority: 'low' | 'medium' | 'high' | 'critical'
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled' | 'blocked'
  expected_impact_ev: number
  effort_level: 'low' | 'medium' | 'high'
  estimated_hours: number
  automation_tier: 'rules' | 'ml' | 'llm' | 'hybrid' | 'human'
  assigned_to?: string
  due_date?: string
  completed_at?: string
  evidence_required: boolean
  human_approval_required: boolean
  created_at: string
  updated_at: string
}
```

### Roadmap Summary
```typescript
interface RoadmapSummary {
  total_items: number
  by_status: Record<string, number>
  by_priority: Record<string, number>
  by_driver: Record<string, number>
  total_potential_ev: number
  completed_ev: number
  in_progress_ev: number
}
```

---

## Demo Roadmap Items

```typescript
const DEMO_ROADMAP: RoadmapItem[] = [
  {
    id: '1',
    driver_key: 'management_independence',
    title: 'Document Standard Operating Procedures',
    description: 'Create comprehensive SOPs for all key business processes',
    category: 'strategic',
    priority: 'high',
    status: 'in_progress',
    expected_impact_ev: 150000,
    effort_level: 'medium',
    estimated_hours: 40,
    due_date: '2025-02-15'
  },
  {
    id: '2',
    driver_key: 'management_independence',
    title: 'Hire Operations Manager',
    description: 'Recruit and train an operations manager to handle day-to-day decisions',
    category: 'strategic',
    priority: 'critical',
    status: 'pending',
    expected_impact_ev: 250000,
    effort_level: 'high',
    estimated_hours: 100,
    due_date: '2025-04-01'
  },
  {
    id: '3',
    driver_key: 'financial_records',
    title: 'Clean Up Chart of Accounts',
    description: 'Standardize QBO chart of accounts to align with industry standards',
    category: 'monthly_close',
    priority: 'high',
    status: 'completed',
    expected_impact_ev: 75000,
    effort_level: 'low',
    estimated_hours: 8
  },
  {
    id: '4',
    driver_key: 'financial_records',
    title: 'Implement Monthly Close Process',
    description: 'Establish consistent monthly close procedure with reconciliation checklist',
    category: 'monthly_close',
    priority: 'high',
    status: 'in_progress',
    expected_impact_ev: 100000,
    effort_level: 'medium',
    estimated_hours: 20,
    due_date: '2025-01-31'
  },
  {
    id: '5',
    driver_key: 'recurring_revenue',
    title: 'Launch Maintenance Agreement Program',
    description: 'Create recurring revenue through annual roof maintenance contracts',
    category: 'strategic',
    priority: 'critical',
    status: 'pending',
    expected_impact_ev: 300000,
    effort_level: 'high',
    estimated_hours: 60,
    due_date: '2025-03-15'
  },
  {
    id: '6',
    driver_key: 'operational_systems',
    title: 'Implement CRM System',
    description: 'Deploy CRM to track customer relationships and enable follow-ups',
    category: 'strategic',
    priority: 'medium',
    status: 'pending',
    expected_impact_ev: 125000,
    effort_level: 'medium',
    estimated_hours: 40,
    due_date: '2025-02-28'
  },
  {
    id: '7',
    driver_key: 'customer_diversity',
    title: 'Diversify Customer Base',
    description: 'Reduce dependency on top 3 customers to below 30% of revenue',
    category: 'quarterly_review',
    priority: 'high',
    status: 'in_progress',
    expected_impact_ev: 200000,
    effort_level: 'high',
    estimated_hours: 80,
    due_date: '2025-06-01'
  },
  {
    id: '8',
    driver_key: 'market_outlook',
    title: 'Expand Commercial Contracts',
    description: 'Target commercial property managers for stable larger contracts',
    category: 'strategic',
    priority: 'medium',
    status: 'pending',
    expected_impact_ev: 175000,
    effort_level: 'medium',
    estimated_hours: 50,
    due_date: '2025-05-01'
  }
]
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/valuation/roadmap` | GET | Get all roadmap items |
| `/api/valuation/roadmap` | POST | Create new roadmap item |
| `/api/valuation/roadmap/{id}` | PATCH | Update roadmap item |
| `/api/valuation/roadmap/{id}` | DELETE | Delete roadmap item |
| `/api/valuation/roadmap/summary` | GET | Get roadmap summary stats |

### Query Parameters
```
GET /api/valuation/roadmap?driver=management_independence&status=pending&priority=high
```

### Update Request
```json
PATCH /api/valuation/roadmap/123
{
  "status": "completed",
  "completed_at": "2025-01-15T10:30:00Z"
}
```

---

## UI Components

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│  VALUATION ROADMAP                                          │
│  Potential EV: $1.375M | In Progress: $450K | Done: $75K   │
├─────────────────────────────────────────────────────────────┤
│  FILTERS: [All Drivers ▼] [All Categories ▼] [All Status ▼]│
├─────────────────────────────────────────────────────────────┤
│  🔴 CRITICAL                                                │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 🎯 Hire Operations Manager              [Pending ▼]  │ │
│  │    Driver: Management Independence                    │ │
│  │    EV Impact: +$250K | Effort: High | Due: Apr 1     │ │
│  └───────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 💰 Launch Maintenance Agreement Program [Pending ▼]  │ │
│  │    Driver: Recurring Revenue                          │ │
│  │    EV Impact: +$300K | Effort: High | Due: Mar 15    │ │
│  └───────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  🟠 HIGH PRIORITY                                           │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 📋 Document SOPs                     [In Progress ▼] │ │
│  │    Driver: Management Independence                    │ │
│  │    EV Impact: +$150K | Effort: Med | Due: Feb 15     │ │
│  └───────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 📊 Implement Monthly Close           [In Progress ▼] │ │
│  │    Driver: Financial Records                          │ │
│  │    EV Impact: +$100K | Effort: Med | Due: Jan 31     │ │
│  └───────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ✅ COMPLETED                                               │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 📚 Clean Up Chart of Accounts          [Completed ✓] │ │
│  │    Driver: Financial Records | EV: +$75K             │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Status Dropdown

```typescript
const STATUS_OPTIONS = [
  { value: 'pending', label: 'Pending', color: 'gray' },
  { value: 'in_progress', label: 'In Progress', color: 'blue' },
  { value: 'completed', label: 'Completed', color: 'green' },
  { value: 'cancelled', label: 'Cancelled', color: 'red' },
  { value: 'blocked', label: 'Blocked', color: 'orange' }
]
```

### Priority Colors

```typescript
const PRIORITY_COLORS = {
  critical: 'bg-red-500',
  high: 'bg-orange-500',
  medium: 'bg-yellow-500',
  low: 'bg-gray-500'
}
```

### Effort Indicators

```typescript
const EFFORT_LABELS = {
  low: '🟢 Low (1-2 weeks)',
  medium: '🟡 Medium (1-2 months)',
  high: '🔴 High (3-6 months)'
}
```

---

## Review Checklist

- [ ] Items sort correctly by EV impact within priority
- [ ] Status updates persist and update timestamp
- [ ] Filters work independently and in combination
- [ ] Demo mode shows realistic roadmap items
- [ ] Driver grouping calculates correctly
- [ ] Total EV calculations are accurate
- [ ] Due dates display and sort correctly
