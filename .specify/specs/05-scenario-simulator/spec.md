# Scenario Simulator Specification

> **Feature**: 05-scenario-simulator
> **Status**: Implemented
> **Priority**: P1 (High)
> **Last Updated**: 2026-01-02

---

## Overview

The Scenario Simulator provides "what-if" modeling without Excel, allowing owners to see how changes to key business levers would impact their EBITDA, multiple, and enterprise value.

**Target User**: Owner, fractional CFO
**Access Frequency**: Monthly to quarterly
**Key Question Answered**: "What if I improved X? How much more would my business be worth?"

---

## User Stories

### US-01: Adjust Recurring Revenue
**As a** roofing contractor owner
**I want to** see how adding recurring revenue would impact my valuation
**So that** I can decide whether to invest in maintenance contracts

**Acceptance Criteria**:
- [ ] Slider from -20% to +100% of current recurring revenue
- [ ] Show impact on EBITDA (assumes margin on recurring)
- [ ] Show impact on multiple (recurring revenue improves multiple)
- [ ] Update projected EV in real-time

### US-02: Adjust Gross Margin
**As a** roofing contractor owner
**I want to** see how improving my margin would impact valuation
**So that** I understand the value of operational improvements

**Acceptance Criteria**:
- [ ] Slider from -5% to +10% margin points
- [ ] Show direct impact on EBITDA
- [ ] Calculate new projected EBITDA
- [ ] Update EV calculation

### US-03: Reduce Owner Hours
**As a** roofing contractor owner
**I want to** see how reducing my involvement would impact valuation
**So that** I understand the value of building a management team

**Acceptance Criteria**:
- [ ] Slider from current hours to 0 hours/week
- [ ] Show impact on multiple (management independence driver)
- [ ] Calculate value of owner time replaced
- [ ] Show total EV impact

### US-04: Improve Productivity
**As a** roofing contractor owner
**I want to** see how crew productivity improvements impact valuation
**So that** I can prioritize operational investments

**Acceptance Criteria**:
- [ ] Slider from -10% to +20% productivity
- [ ] Show impact on effective revenue or cost reduction
- [ ] Calculate EBITDA impact
- [ ] Update projected EV

### US-05: See Combined Impact
**As a** roofing contractor owner
**I want to** see the combined effect of all adjustments
**So that** I can create a comprehensive improvement plan

**Acceptance Criteria**:
- [ ] Show all four levers simultaneously
- [ ] Calculate combined EBITDA impact
- [ ] Calculate combined multiple impact
- [ ] Display projected EV range (low/high)
- [ ] Compare to baseline valuation

---

## Simulation Model

### Input Levers

| Lever | Range | Unit | Default |
|-------|-------|------|---------|
| Recurring Revenue Delta | -20% to +100% | % | 0% |
| Margin Delta | -5% to +10% | % points | 0% |
| Owner Hours | 0 to current | hours/week | Current |
| Productivity Delta | -10% to +20% | % | 0% |

### Impact Calculations

```typescript
function simulateImpact(baseline: ValuationSnapshot, levers: SimulationLevers): SimulationResult {
  let ebitda = baseline.ttm_ebitda
  let multiple = baseline.multiple_mid

  // Recurring Revenue Impact
  // Each % of recurring revenue adds 0.3x of its margin to EBITDA
  const recurringImpact = levers.recurring_revenue_delta * 0.01 * ebitda * 0.3
  ebitda += recurringImpact

  // Also improves multiple (buyers pay more for recurring)
  if (levers.recurring_revenue_delta > 0) {
    multiple += Math.min(levers.recurring_revenue_delta * 0.01, 0.5) // Cap at +0.5x
  }

  // Margin Impact
  // Direct EBITDA improvement: delta points * 2x multiplier
  const marginImpact = levers.margin_delta * 0.01 * baseline.ttm_revenue * 2
  ebitda += marginImpact

  // Owner Hours Impact
  // Reducing hours improves management independence driver
  const hoursReduced = baseline.owner_hours - levers.owner_hours
  const ownerHoursValue = hoursReduced * 1500 // $1,500 per hour value
  multiple += Math.min(hoursReduced / 50, 1.0) // Up to +1.0x for full independence

  // Productivity Impact
  // Productivity translates to effective EBITDA improvement
  const productivityImpact = levers.productivity_delta * 0.01 * ebitda * 0.5
  ebitda += productivityImpact

  // Calculate EV
  const ev_low = ebitda * (multiple - 0.5)
  const ev_high = ebitda * (multiple + 0.5)

  return {
    projected_ebitda: ebitda,
    projected_multiple: multiple,
    projected_ev_low: ev_low,
    projected_ev_high: ev_high,
    changes: {
      ebitda_delta: ebitda - baseline.ttm_ebitda,
      multiple_delta: multiple - baseline.multiple_mid,
      ev_delta_low: ev_low - baseline.ev_low,
      ev_delta_high: ev_high - baseline.ev_high
    }
  }
}
```

### Demo Mode Calculation

When in demo mode, calculate locally without API:

```typescript
const DEMO_BASELINE = {
  ttm_ebitda: 350000,
  ttm_revenue: 3500000,
  multiple_mid: 4.5,
  ev_low: 1400000,
  ev_high: 1925000,
  owner_hours: 50
}
```

---

## Data Model

### Simulation Input
```typescript
interface SimulationLevers {
  recurring_revenue_delta: number  // -0.2 to 1.0
  margin_delta: number             // -0.05 to 0.10
  owner_hours: number              // 0 to current
  productivity_delta: number       // -0.1 to 0.2
}
```

### Simulation Output
```typescript
interface SimulationResult {
  projected_ebitda: number
  projected_multiple: number
  projected_ev_low: number
  projected_ev_high: number
  changes: {
    ebitda_delta: number
    multiple_delta: number
    ev_delta_low: number
    ev_delta_high: number
  }
}
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/valuation/simulate` | POST | Run simulation with levers |
| `/api/valuation/snapshot` | GET | Get baseline for simulation |

### Request Example
```json
POST /api/valuation/simulate
{
  "levers": {
    "recurring_revenue_delta": 0.25,
    "margin_delta": 0.03,
    "owner_hours_delta": -20,
    "productivity_delta": 0.10
  }
}
```

### Response Example
```json
{
  "projected_ebitda": 425000,
  "projected_multiple": 5.2,
  "projected_ev_low": 1912500,
  "projected_ev_high": 2422500
}
```

---

## UI Components

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│  SCENARIO SIMULATOR                    "What if I..."       │
├─────────────────────────────────────────────────────────────┤
│  BASELINE                         PROJECTED                 │
│  ┌─────────────────────┐          ┌─────────────────────┐  │
│  │ EBITDA: $350,000    │    →     │ EBITDA: $425,000    │  │
│  │ Multiple: 4.5x      │          │ Multiple: 5.2x      │  │
│  │ EV: $1.4-1.9M       │          │ EV: $1.9-2.4M       │  │
│  └─────────────────────┘          └─────────────────────┘  │
│                                                             │
│                    VALUE CREATED: +$500K                    │
├─────────────────────────────────────────────────────────────┤
│  🔄 RECURRING REVENUE                                       │
│  [-20%] ═══════════╪══════════════════════════ [+100%]    │
│                  +25%                                       │
│  Impact: +$26K EBITDA | +0.25x Multiple                    │
├─────────────────────────────────────────────────────────────┤
│  📈 GROSS MARGIN                                           │
│  [-5%] ═══════════════════╪════════════════════ [+10%]    │
│                         +3%                                 │
│  Impact: +$52K EBITDA                                      │
├─────────────────────────────────────────────────────────────┤
│  👤 OWNER HOURS PER WEEK                                   │
│  [0 hrs] ══════════════════════════════════╪═══ [50 hrs]  │
│                                           30 hrs           │
│  Impact: +$30K value | +0.4x Multiple                      │
├─────────────────────────────────────────────────────────────┤
│  ⚡ PRODUCTIVITY                                           │
│  [-10%] ════════════════════════════╪══════════ [+20%]    │
│                                   +10%                      │
│  Impact: +$17K EBITDA                                      │
├─────────────────────────────────────────────────────────────┤
│  [Reset All]                          [Save Scenario]      │
└─────────────────────────────────────────────────────────────┘
```

### Slider Component

```typescript
interface SliderProps {
  label: string
  icon: string
  min: number
  max: number
  step: number
  value: number
  unit: string
  onChange: (value: number) => void
  impactLabel: string
}
```

---

## Debouncing

API calls are debounced to prevent excessive requests:

```typescript
const debouncedSimulate = useMemo(
  () => debounce(async (levers) => {
    const result = await fetch('/api/valuation/simulate', {
      method: 'POST',
      body: JSON.stringify({ levers })
    })
    setSimulationResult(await result.json())
  }, 250),
  []
)
```

---

## Review Checklist

- [ ] All four sliders work independently
- [ ] Combined calculation is accurate
- [ ] Demo mode calculates locally without API
- [ ] Debouncing prevents excessive API calls
- [ ] Results update smoothly (no jank)
- [ ] Reset button clears all values
- [ ] Impact labels are helpful and accurate
