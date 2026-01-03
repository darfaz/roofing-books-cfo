---
name: roofing-cfo-research
description: |
  Roofing contractor industry research and CFO intelligence for CrewCFO platform development.
  Use when: (1) Researching roofing industry M&A/PE consolidation activity, (2) Finding valuation
  multiples (EBITDA, SDE, revenue) for roofing/construction businesses, (3) Competitive analysis
  of bookkeeping/CFO software, (4) BLS/labor market wage benchmarking for NAICS 238160,
  (5) Industry financial ratio benchmarking, (6) Tracking PE-backed roofing platforms.
---

# Roofing CFO Market Research

Research agent for CrewCFO platform—AI-powered bookkeeping and fractional CFO for roofing contractors.

## When to Use This Skill

- Researching roofing industry M&A and PE consolidation activity
- Finding valuation multiples for roofing/construction businesses
- Competitive analysis of bookkeeping/CFO software platforms
- BLS/labor market wage benchmarking for NAICS 238160
- Industry financial ratio benchmarking
- Tracking PE-backed roofing platforms and acquisition pace
- Finding transaction data and market comps

## Core Data Sources

### Industry Analysis

| Source | URL Pattern | Data Type |
|--------|-------------|-----------|
| IBISWorld NAICS 23816 | ibisworld.com/united-states/industry/roofing-contractors | Market size, concentration, outlook |
| Roofing Contractor Mag | roofingcontractor.com/articles | PE activity, industry surveys |
| BLS OEWS 238160 | bls.gov/oes/current/naics4_238100.htm | Wage benchmarks by role |
| Census Construction | census.gov/construction | Housing starts, permits |

### Valuation & M&A Sources

| Source | Use Case |
|--------|----------|
| BizBuySell | Transaction multiples, listing comps |
| Peak Business Valuation | SDE/EBITDA multiple ranges |
| Industry Pro / Matador | Trade-specific value drivers |
| LinkedIn M&A posts | Real-time deal announcements |

### Competitive Intelligence

| Competitor | Focus | Funding |
|------------|-------|---------|
| Adaptive.build | Construction AP/AR, WIP | $26.4M |
| Briq | Construction automation, Otto AI | $30M Series B |
| Pilot | SMB bookkeeping + CFO | $222M total |
| Bench | SMB bookkeeping (acquired by Employer.com) | — |
| Digits | AI-native accounting | $92M |

## Research Workflows

### Workflow 1: PE Consolidation Tracker

Search sequence:
1. `"roofing contractor acquisition [year]" site:roofingcontractor.com`
2. `"private equity roofing platform" site:linkedin.com`
3. Extract: Platform name, acquirer, target, deal value

**Key metrics (as of Dec 2025):**
- 56 PE-backed platforms (up 229% from 17 in early 2023)
- 134 acquisitions in 2024 (up from 106 in 2023)
- Deal pace: ~1 acquisition every 48 hours
- Industry remains 96%+ unconsolidated

**Major PE-Backed Platforms to Track:**
- Omnia Exterior Services
- Tecta America
- CentiMark Corporation
- Roofing Solutions Group
- Flynn Group of Companies
- Nations Roof
- Baker Roofing Company

### Workflow 2: Valuation Multiples Research

Apply the Matador tier framework:

| Tier | EBITDA Multiple | Revenue Multiple | Typical Profile |
|------|-----------------|------------------|-----------------|
| Below-average | ~3x | 0.3x | Owner-dependent, poor records |
| Average | 4.5-5x | 0.4x | Stable business, some systems |
| Above-average | 7x+ | 0.75x | Strong team, recurring revenue |

**Standard ranges (small contractors):**
- SDE Multiple: 1.9x - 2.7x
- EBITDA Multiple: 2.5x - 3.6x
- Revenue Multiple: 0.3x - 0.5x

**Platform/PE targets:**
- Min revenue: $10M+ (platforms), $2-5M (add-ons)
- Min EBITDA: $750K for add-on consideration
- Premium multiples: 6.5-7.5x for strong regional players

### Workflow 3: Labor Market Benchmarking

BLS OEWS codes for NAICS 238160 (Roofing Contractors):

| SOC Code | Role | National Median Hourly |
|----------|------|------------------------|
| 47-2181 | Roofers | $24.50 |
| 47-1011 | First-Line Supervisors | $35.00 |
| 43-3031 | Bookkeeping/Accounting Clerks | $22.00 |
| 11-1021 | General Managers | $55.00 |

Pull regional wage differentials and compare to internal Salary Benchmarking Tool.

### Workflow 4: Competitor Feature Analysis

Map competitors to CrewCFO feature matrix:

| Feature | Adaptive | Briq | Pilot | CrewCFO Target |
|---------|----------|------|-------|----------------|
| Job Costing | Yes | Yes | — | Yes |
| WIP Tracking | Yes | Yes | — | Yes |
| AI Insights | Partial | Otto | Partial | Full LLM |
| Valuation Module | — | — | — | Yes |
| Trade-specific | Yes | Yes | — | Yes |
| QBO Integration | Yes | Yes | Yes | Yes |
| Roofing-specific | — | — | — | Yes |

## Industry Benchmarks (Dec 2025)

### Market Size
- Total US roofing contractor market: ~$100B revenue
- 238,000+ establishments
- Highly fragmented: Top 4 companies = 12.5% market share

### Cost Structure Benchmarks (% of Revenue)

| Cost Category | Industry % | Good Target |
|---------------|------------|-------------|
| Materials/Purchases | 48.5% | 45-48% |
| Wages | 18.5% | 18-22% |
| Contracted Labor | 18.3% | 15-20% |
| Profit Margin | 6.9% | 10-15% |

### Financial Ratios (Industry Medians)

| Ratio | Median | Strong |
|-------|--------|--------|
| Current Ratio | 1.4 | 2.0+ |
| Quick Ratio | 1.1 | 1.5+ |
| Days Receivables | 43-47 | <35 |
| EBITDA/Revenue | 10-14% | 18%+ |
| Return on Net Worth | 48-90% | 100%+ |

## Search Query Templates

### PE/M&A Activity
```
"roofing contractor" "acquired by" [year]
"private equity" "roofing" "platform" investment
site:roofingcontractor.com "acquisition" OR "private equity"
"Omnia Exterior" OR "Tecta America" OR "CentiMark" acquisition
```

### Valuation Research
```
site:bizbuysell.com roofing business sale
"roofing company" "EBITDA multiple" valuation
"roofing contractor" "sold for" million
site:peakbusinessvaluation.com roofing
```

### Competitor Intelligence
```
site:adaptive.build features pricing
"Briq construction" "Otto AI" features
site:pilot.com construction accounting
"Digits accounting" "construction" OR "contractor"
```

### BLS/Labor Data
```
site:bls.gov "238160" OR "roofing contractors" wages
OEWS "roofers" "47-2181" [state]
```

## Output Templates

### Transaction Record
```
Date: YYYY-MM-DD
Target: [Company Name]
Acquirer: [Platform/PE Firm]
Revenue: $X.XM
EBITDA: $X.XM
Multiple: X.Xx
Region: [State/Market]
Deal Type: Platform | Add-on
PE Sponsor: [Firm Name]
Notes: [Key deal terms]
```

### Valuation Summary
```
Company: [Name]
Revenue: $X.XM | EBITDA: $X.XK
Owner Dependence: High/Med/Low
Recurring Revenue: X%

Implied EV Range:
- Conservative (3x): $X.XM
- Market (5x): $X.XM
- Premium (7x): $X.XM

Key Value Drivers:
1. [Driver] - [Score/Assessment]
2. [Driver] - [Score/Assessment]
3. [Driver] - [Score/Assessment]
```

### Competitive Matrix
```
| Feature | Us | Competitor A | Competitor B |
|---------|----|--------------| -------------|
| [Feature 1] | Yes/No | Yes/No | Yes/No |
| Pricing | $X/mo | $X/mo | $X/mo |
| Target Customer | [Description] | [Description] | [Description] |
```

## Integration with CrewCFO

This skill integrates with the CrewCFO platform features:

- **Valuation Shock Report**: Uses industry multiples and benchmarks
- **Value Driver Analysis**: Applies PE-informed value drivers
- **Action Items**: Strategic recommendations based on industry best practices
- **Financial Analysis**: Compare client metrics to industry benchmarks

See `crewcfo-knowledge-base/data/valuation/` for additional resources.

## Example Prompts

- "What are the latest roofing PE acquisitions?"
- "What EBITDA multiples are roofing companies selling for?"
- "Compare CrewCFO features to Adaptive.build"
- "What are BLS wage benchmarks for roofers in Texas?"
- "How many PE platforms are acquiring roofing companies?"
- "What makes a roofing company attractive to PE buyers?"
- "Track recent roofing industry M&A activity"
