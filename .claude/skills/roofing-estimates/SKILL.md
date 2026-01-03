---
name: roofing-estimates
description: Generate detailed roofing estimates with materials, labor costs, and profit margins. Use when creating roof replacement/repair estimates, calculating shingles, underlayment, flashing, labor, and generating itemized quotes for customers.
---

# Roofing Estimate Generator

Generate professional, accurate roofing estimates with proper material calculations, labor costs, and profit margins.

## When to Use This Skill

- Creating new roof replacement or repair estimates
- Calculating material quantities (shingles, underlayment, flashing, etc.)
- Generating itemized quotes for customers
- Adjusting estimates for roof complexity (pitch, valleys, dormers)
- Comparing material options for customers

## Estimate Components

### 1. Roof Measurements
- **Squares**: 1 square = 100 sq ft of roof area
- **Pitch Multiplier**: Adjusts for roof slope steepness
- **Waste Factor**: Additional material for cuts and waste

### 2. Pitch Multipliers (Industry Standard)

| Pitch | Multiplier | Description |
|-------|------------|-------------|
| 4/12 | 1.054 | Low slope |
| 5/12 | 1.083 | Standard |
| 6/12 | 1.118 | Standard |
| 7/12 | 1.158 | Moderate |
| 8/12 | 1.202 | Steep |
| 9/12 | 1.250 | Steep |
| 10/12 | 1.302 | Very steep |
| 12/12 | 1.414 | Very steep |

### 3. Waste Factors

| Roof Complexity | Waste Factor |
|-----------------|--------------|
| Simple (few cuts) | 5-10% |
| Average | 10-15% |
| Complex (many valleys, dormers) | 15-20% |
| Cut-up roof | 20-25% |

## Material Calculations

### Shingles
```
Bundles needed = (Roof sq ft × Pitch Multiplier × Waste Factor) / 33.3
Note: 3 bundles = 1 square for architectural shingles
```

### Underlayment
```
Rolls needed = (Roof sq ft × Pitch Multiplier) / 400
Note: 1 roll synthetic = 400 sq ft coverage
```

### Starter Strip
```
Linear feet = Eave length + Rake length (both sides)
Bundles = Linear feet / 120 (approx 120 linear ft per bundle)
```

### Ridge Cap
```
Bundles = Ridge/Hip linear feet / 31
```

### Drip Edge
```
10' pieces = (Eave + Rake length) / 10
```

### Flashing
- Step flashing: Estimate 1 piece per linear foot where roof meets wall
- Pipe boots: Count all plumbing vents
- Valley metal: Measure valley length (if using metal valleys)

### Nails
```
Coils = Squares × 1.5 (for high-wind areas, use 2× factor)
```

## Labor Calculations

### Base Labor Rates (adjust for local market)

| Task | Rate per Square |
|------|-----------------|
| Tear-off (1 layer) | $25-40 |
| Tear-off (2+ layers) | $35-50 |
| Install shingles | $45-75 |
| Install underlayment | $15-25 |

### Complexity Adjustments
- Add 10-15% for 7/12+ pitch
- Add 20-30% for 10/12+ pitch
- Add 15-25% for cut-up roofs
- Add 10-20% for 2+ story homes

## Estimate Template Structure

```
ROOFING ESTIMATE
================
Customer: [Name]
Address: [Property Address]
Date: [Date]
Valid for: 30 days

ROOF SPECIFICATIONS
- Total Roof Area: ___ sq ft
- Roof Pitch: ___/12
- Number of Layers: ___
- Complexity: Simple / Average / Complex

MATERIALS
-----------------------------------------
Item                  Qty    Unit    Total
-----------------------------------------
Architectural Shingles ___ bdl  $___   $___
Synthetic Underlayment ___ roll $___   $___
Starter Strip         ___ bdl  $___   $___
Ridge Cap             ___ bdl  $___   $___
Drip Edge             ___ pc   $___   $___
Ice & Water Shield    ___ roll $___   $___
Pipe Boots            ___ ea   $___   $___
Nails                 ___ coil $___   $___
-----------------------------------------
MATERIALS SUBTOTAL                    $___

LABOR
-----------------------------------------
Tear-off & Disposal   ___ sq   $___   $___
Installation          ___ sq   $___   $___
-----------------------------------------
LABOR SUBTOTAL                        $___

-----------------------------------------
SUBTOTAL                              $___
Overhead & Profit (___%)              $___
-----------------------------------------
TOTAL INVESTMENT                      $___

WARRANTY INFORMATION
- Manufacturer: ___ years
- Workmanship: ___ years

INCLUDED SERVICES
✓ Complete tear-off to deck
✓ Deck inspection and repairs (if needed)
✓ New drip edge on all eaves and rakes
✓ Ice & water shield in valleys and eaves
✓ Magnetic nail sweep of property
✓ Final walk-through inspection
```

## Profit Margin Guidelines

| Job Size | Suggested Margin |
|----------|------------------|
| Under $5,000 | 35-45% |
| $5,000-15,000 | 30-40% |
| $15,000-30,000 | 25-35% |
| Over $30,000 | 20-30% |

## Common Material Pricing (Update Regularly)

See [references/material-pricing.md](references/material-pricing.md) for current pricing.

## Example Prompts

- "Create an estimate for a 2,000 sq ft roof with 6/12 pitch"
- "How many bundles of shingles do I need for 25 squares?"
- "Generate a Good/Better/Best estimate for this job"
- "Calculate materials for a complex hip roof"
- "What's the labor cost for tear-off and install on a steep roof?"
