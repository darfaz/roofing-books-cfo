# Valuation Engine Specification

## Core Calculations
- TTM Revenue
- TTM EBITDA (normalized operating earnings)
- TTM Seller’s Discretionary Earnings (SDE)

## Normalization Rules
- Owner compensation normalization
- One-time expenses flagged (human review required)
- No auto-posting adjustments

## Multiple Selection Logic
- Base multiple derived from Matador tier
- Revenue multiples shown as secondary reference
- Confidence bands applied based on data quality

## Scenario Simulator
Owners may adjust:
- Gross margin
- Overhead %
- AR days
- Recurring revenue %
- Owner dependence signals

System recomputes:
- EBITDA delta
- Multiple delta
- Enterprise value delta

## Exit Readiness Outputs
- Due diligence checklist
- Financial package readiness
- Red flag indicators
