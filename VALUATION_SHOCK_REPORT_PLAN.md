# Valuation Shock Report - Implementation Plan

## The WOW Conversion Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: CONNECT QBO (30 seconds)                                           │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • One-click OAuth                                                          │
│  • Auto-sync last 12 months of transactions                                 │
│  • Progress indicator: "Analyzing 1,247 transactions..."                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: GENERATE VALUATION SHOCK REPORT (2 minutes)                        │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • Calculate "Reported EBITDA" (what owner thinks)                          │
│  • Calculate "Defensible EBITDA™" (what buyer will underwrite)              │
│  • Identify questionable add-backs                                          │
│  • Score 6 value drivers automatically                                      │
│  • Determine tier and multiple range                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: SHOW THE SHOCK (1 minute) - THE WOW MOMENT                         │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  "YOUR VALUATION SHOCK REPORT"                                      │   │
│  │                                                                     │   │
│  │  What you think you're worth:     $8,200,000                       │   │
│  │  What a buyer will pay:           $4,850,000                       │   │
│  │  ─────────────────────────────────────────────────                 │   │
│  │  MONEY LEFT ON THE TABLE:         $3,350,000                       │   │
│  │                                                                     │   │
│  │  [Your EBITDA: $820K] × [Your Expected Multiple: 10×] = $8.2M     │   │
│  │  [Defensible EBITDA: $680K] × [Buyer Multiple: 4.5×] = $4.85M     │   │
│  │                                                                     │   │
│  │  WHY THE GAP?                                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │ EBITDA Haircut: -$140K                                      │  │   │
│  │  │  • Owner salary add-back rejected: -$85K (undocumented)     │  │   │
│  │  │  • Personal expenses flagged: -$32K                         │  │   │
│  │  │  • Non-recurring income removed: -$23K                      │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │ Multiple Penalty: 10× → 4.5× (-5.5×)                        │  │   │
│  │  │  • Owner dependence: -2.0× (you ARE the business)           │  │   │
│  │  │  • No recurring revenue: -1.5× (project-based only)         │  │   │
│  │  │  • AR days > 60: -1.0× (cash flow risk)                     │  │   │
│  │  │  • Customer concentration: -0.5× (top 3 = 45%)              │  │   │
│  │  │  • No systems documented: -0.5× (tribal knowledge)          │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  [Download PDF Report - FREE]                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: THE UPSELL - UNLOCK THE ROADMAP (1 minute)                         │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  "HERE'S HOW TO RECOVER $2.1M OF THAT VALUE"                               │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ TOP 5 VALUE UNLOCKS                           IMPACT    LOCKED     │   │
│  │ ───────────────────────────────────────────────────────────────── │   │
│  │ 1. Document owner processes                   +$850K    🔒         │   │
│  │ 2. Launch maintenance contracts               +$620K    🔒         │   │
│  │ 3. Clean up add-backs with CFO review         +$340K    🔒         │   │
│  │ 4. Reduce AR days to <45                      +$180K    🔒         │   │
│  │ 5. Diversify customer base                    +$110K    🔒         │   │
│  │ ───────────────────────────────────────────────────────────────── │   │
│  │ TOTAL RECOVERABLE VALUE:                     +$2,100K              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  UNLOCK YOUR FULL ROADMAP                                           │   │
│  │                                                                     │   │
│  │  ✓ Monthly Defensible EBITDA™ tracking                             │   │
│  │  ✓ Live valuation meter (updated weekly)                           │   │
│  │  ✓ Buyer-grade financial reports                                   │   │
│  │  ✓ 12-month value acceleration roadmap                             │   │
│  │  ✓ CFO review of add-backs & adjustments                           │   │
│  │  ✓ Exit readiness dashboard                                        │   │
│  │                                                                     │   │
│  │  [$299/month] [Start 14-Day Free Trial]                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Technical Implementation

### Phase 1: New Database Schema

```sql
-- New table: valuation_shock_reports
CREATE TABLE valuation_shock_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    generated_at TIMESTAMPTZ DEFAULT now(),

    -- What they think (reported)
    reported_ebitda NUMERIC,
    expected_multiple NUMERIC DEFAULT 10.0,
    expected_valuation NUMERIC,

    -- What buyer sees (defensible)
    defensible_ebitda NUMERIC,
    buyer_multiple_low NUMERIC,
    buyer_multiple_high NUMERIC,
    buyer_valuation_low NUMERIC,
    buyer_valuation_high NUMERIC,

    -- The gap
    ebitda_haircut NUMERIC,
    multiple_penalty NUMERIC,
    value_gap NUMERIC,

    -- Detailed breakdowns (JSONB)
    ebitda_adjustments JSONB,  -- Array of {reason, amount, category}
    multiple_penalties JSONB,  -- Array of {driver, penalty, reason}

    -- Driver scores at time of report
    driver_scores JSONB,
    tier VARCHAR(20),

    -- Value unlocks (roadmap preview)
    value_unlocks JSONB,  -- Array of {action, impact, effort, locked}
    total_recoverable_value NUMERIC,

    -- Metadata
    qbo_data_range_start DATE,
    qbo_data_range_end DATE,
    transaction_count INTEGER,
    confidence_score INTEGER,

    created_at TIMESTAMPTZ DEFAULT now()
);

-- New table: ebitda_adjustments (permanent tracking)
CREATE TABLE ebitda_adjustments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),

    adjustment_type VARCHAR(50),  -- 'owner_comp', 'personal_expense', 'one_time', 'non_recurring'
    category VARCHAR(50),         -- 'accepted', 'rejected', 'needs_review'

    description TEXT,
    amount NUMERIC,

    -- Evidence
    transaction_ids JSONB,  -- Links to transaction_lines
    account_id UUID,

    -- Review status
    auto_flagged BOOLEAN DEFAULT false,
    human_reviewed BOOLEAN DEFAULT false,
    reviewer_notes TEXT,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- New table: multiple_penalties (buyer perspective)
CREATE TABLE multiple_penalties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),

    driver_key VARCHAR(50),  -- management_independence, recurring_revenue, etc.
    penalty_amount NUMERIC,  -- e.g., -1.5x

    -- Buyer language
    reason TEXT,
    buyer_concern TEXT,

    -- Threshold that triggered penalty
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    threshold_value NUMERIC,

    -- How to fix
    remediation_action TEXT,
    remediation_impact NUMERIC,

    created_at TIMESTAMPTZ DEFAULT now()
);
```

### Phase 2: Shock Report Engine

**New File:** `src/services/valuation/shock_report.py`

```python
"""
Valuation Shock Report Generator
Calculates the gap between owner expectations and buyer reality
"""

class ShockReportEngine:

    # EBITDA Adjustment Rules
    ADJUSTMENT_RULES = {
        'owner_compensation': {
            'max_acceptable': 150000,  # Market rate for ops manager
            'keywords': ['owner', 'officer', 'shareholder', 'draw'],
            'buyer_treatment': 'Replace with market-rate manager salary'
        },
        'personal_expenses': {
            'patterns': ['auto', 'vehicle', 'travel', 'entertainment', 'meals'],
            'rejection_rate': 0.5,  # Buyers reject 50% of these
            'buyer_concern': 'Mixed personal/business expenses'
        },
        'one_time_revenue': {
            'patterns': ['insurance claim', 'settlement', 'refund', 'grant'],
            'buyer_treatment': 'Removed entirely from EBITDA'
        },
        'related_party': {
            'patterns': ['related party', 'family', 'spouse'],
            'buyer_concern': 'Above-market payments to family members'
        }
    }

    # Multiple Penalty Matrix
    MULTIPLE_PENALTIES = {
        'management_independence': {
            'thresholds': [
                {'score': (0, 40), 'penalty': -2.0, 'reason': 'Owner IS the business'},
                {'score': (40, 60), 'penalty': -1.0, 'reason': 'High owner dependency'},
                {'score': (60, 80), 'penalty': -0.5, 'reason': 'Some owner dependency'},
            ]
        },
        'recurring_revenue': {
            'thresholds': [
                {'score': (0, 20), 'penalty': -1.5, 'reason': 'No recurring revenue'},
                {'score': (20, 40), 'penalty': -1.0, 'reason': 'Minimal recurring revenue'},
                {'score': (40, 60), 'penalty': -0.5, 'reason': 'Low recurring revenue'},
            ]
        },
        'financial_records': {
            'thresholds': [
                {'score': (0, 40), 'penalty': -1.0, 'reason': 'Unreliable financials'},
                {'score': (40, 60), 'penalty': -0.5, 'reason': 'Inconsistent records'},
            ]
        },
        'customer_diversity': {
            'thresholds': [
                {'score': (0, 40), 'penalty': -0.8, 'reason': 'High customer concentration'},
                {'score': (40, 60), 'penalty': -0.4, 'reason': 'Moderate concentration risk'},
            ]
        },
        'operational_systems': {
            'thresholds': [
                {'score': (0, 40), 'penalty': -0.5, 'reason': 'No documented systems'},
                {'score': (40, 60), 'penalty': -0.3, 'reason': 'Partial documentation'},
            ]
        }
    }

    def generate_shock_report(self, tenant_id: str) -> dict:
        """Generate the complete Valuation Shock Report"""

        # 1. Calculate Reported EBITDA (owner's view)
        reported = self._calculate_reported_ebitda(tenant_id)

        # 2. Calculate Defensible EBITDA (buyer's view)
        defensible, adjustments = self._calculate_defensible_ebitda(tenant_id)

        # 3. Score value drivers
        driver_scores = self._score_drivers(tenant_id)

        # 4. Calculate multiple penalties
        penalties, buyer_multiple = self._calculate_multiple_penalties(driver_scores)

        # 5. Calculate valuations
        owner_expected = reported['ebitda'] * 10  # Owners typically expect 10x
        buyer_low = defensible * buyer_multiple['low']
        buyer_high = defensible * buyer_multiple['high']

        # 6. Generate value unlocks (roadmap preview)
        value_unlocks = self._generate_value_unlocks(adjustments, penalties)

        return {
            'reported': {
                'ebitda': reported['ebitda'],
                'multiple': 10.0,
                'valuation': owner_expected
            },
            'defensible': {
                'ebitda': defensible,
                'multiple_low': buyer_multiple['low'],
                'multiple_high': buyer_multiple['high'],
                'valuation_low': buyer_low,
                'valuation_high': buyer_high
            },
            'gap': {
                'ebitda_haircut': reported['ebitda'] - defensible,
                'multiple_penalty': 10.0 - buyer_multiple['high'],
                'value_gap': owner_expected - buyer_high
            },
            'adjustments': adjustments,
            'penalties': penalties,
            'driver_scores': driver_scores,
            'value_unlocks': value_unlocks,
            'total_recoverable': sum(u['impact'] for u in value_unlocks)
        }

    def _calculate_defensible_ebitda(self, tenant_id: str) -> tuple:
        """
        Calculate buyer-defensible EBITDA by:
        1. Starting with reported EBITDA
        2. Rejecting questionable add-backs
        3. Removing one-time items
        4. Adjusting owner comp to market rate
        """
        adjustments = []

        # Analyze transactions for red flags
        # ... implementation details

        return defensible_ebitda, adjustments

    def _generate_value_unlocks(self, adjustments, penalties) -> list:
        """
        Generate prioritized list of actions to recover value
        Each action shows: what to do, expected impact, effort level
        """
        unlocks = []

        # From EBITDA adjustments
        for adj in adjustments:
            if adj['recoverable']:
                unlocks.append({
                    'action': adj['remediation'],
                    'impact': adj['amount'] * 5,  # 5x multiple on recovered EBITDA
                    'effort': adj['effort'],
                    'category': 'ebitda_recovery',
                    'locked': True
                })

        # From multiple penalties
        for penalty in penalties:
            unlocks.append({
                'action': penalty['remediation_action'],
                'impact': penalty['remediation_impact'],
                'effort': penalty['effort'],
                'category': 'multiple_expansion',
                'locked': True
            })

        # Sort by impact descending
        return sorted(unlocks, key=lambda x: x['impact'], reverse=True)[:10]
```

### Phase 3: API Endpoints

**Add to:** `src/main.py`

```python
# POST /api/valuation/shock-report
@app.post("/api/valuation/shock-report")
async def generate_shock_report(tenant_id: str = Depends(get_tenant)):
    """Generate the Valuation Shock Report"""
    engine = ShockReportEngine()
    report = engine.generate_shock_report(tenant_id)

    # Store in database
    supabase.table("valuation_shock_reports").insert({
        "tenant_id": tenant_id,
        "reported_ebitda": report['reported']['ebitda'],
        "defensible_ebitda": report['defensible']['ebitda'],
        # ... all fields
    }).execute()

    return report

# GET /api/valuation/shock-report/latest
@app.get("/api/valuation/shock-report/latest")
async def get_latest_shock_report(tenant_id: str = Depends(get_tenant)):
    """Get the most recent shock report"""
    result = supabase.table("valuation_shock_reports")\
        .select("*")\
        .eq("tenant_id", tenant_id)\
        .order("generated_at", desc=True)\
        .limit(1)\
        .execute()

    return result.data[0] if result.data else None

# POST /api/valuation/shock-report/pdf
@app.post("/api/valuation/shock-report/pdf")
async def generate_shock_report_pdf(tenant_id: str = Depends(get_tenant)):
    """Generate downloadable PDF of shock report"""
    # Use reportlab or weasyprint to generate PDF
    # Return file download
    pass
```

### Phase 4: React Components

**New Component:** `frontend/src/components/ShockReport.tsx`

```tsx
// Key sections:

// 1. The Shock Header
<div className="shock-header">
  <h1>Your Valuation Shock Report</h1>
  <div className="shock-comparison">
    <div className="expected">
      <span className="label">What you think you're worth</span>
      <span className="value">${formatCurrency(report.reported.valuation)}</span>
    </div>
    <div className="actual">
      <span className="label">What a buyer will pay</span>
      <span className="value">${formatCurrency(report.defensible.valuation_high)}</span>
    </div>
    <div className="gap">
      <span className="label">Money left on the table</span>
      <span className="value negative">${formatCurrency(report.gap.value_gap)}</span>
    </div>
  </div>
</div>

// 2. EBITDA Breakdown
<div className="ebitda-breakdown">
  <h2>Why Your EBITDA Got Haircut</h2>
  {report.adjustments.map(adj => (
    <div className="adjustment-row" key={adj.id}>
      <span className="icon">✖</span>
      <span className="reason">{adj.reason}</span>
      <span className="amount">-${formatCurrency(adj.amount)}</span>
    </div>
  ))}
</div>

// 3. Multiple Penalties
<div className="multiple-penalties">
  <h2>Why Your Multiple Got Crushed</h2>
  <div className="multiple-visual">
    <span>10×</span>
    <div className="penalty-bar">
      {report.penalties.map(p => (
        <div className="penalty-segment" style={{width: `${p.penalty * 10}%`}}>
          -{p.penalty}×
        </div>
      ))}
    </div>
    <span>{report.defensible.multiple_high}×</span>
  </div>
  {report.penalties.map(penalty => (
    <div className="penalty-row" key={penalty.driver}>
      <span className="driver">{penalty.driver}</span>
      <span className="reason">{penalty.reason}</span>
      <span className="penalty">-{penalty.penalty}×</span>
    </div>
  ))}
</div>

// 4. Value Unlocks (Teaser)
<div className="value-unlocks">
  <h2>How to Recover ${formatCurrency(report.total_recoverable)}</h2>
  {report.value_unlocks.slice(0, 5).map((unlock, i) => (
    <div className="unlock-row" key={i}>
      <span className="number">{i + 1}.</span>
      <span className="action">{unlock.action}</span>
      <span className="impact">+${formatCurrency(unlock.impact)}</span>
      <span className="locked">🔒</span>
    </div>
  ))}
  <div className="cta">
    <button onClick={startTrial}>Unlock Full Roadmap - Start Free Trial</button>
  </div>
</div>
```

### Phase 5: Onboarding Flow Integration

**Updated Flow:** `frontend/src/components/Onboarding.tsx`

```tsx
const ONBOARDING_STEPS = [
  {
    id: 'connect',
    title: 'Connect QuickBooks',
    subtitle: 'One-click sync of your financial data',
    component: <QBOConnect />,
    duration: '30 seconds'
  },
  {
    id: 'analyzing',
    title: 'Analyzing Your Business',
    subtitle: 'Calculating your buyer-grade EBITDA...',
    component: <AnalyzingAnimation />,
    duration: '2 minutes',
    autoProgress: true
  },
  {
    id: 'shock',
    title: 'Your Valuation Shock Report',
    subtitle: 'See what a buyer would really pay',
    component: <ShockReport />,
    duration: '1 minute'
  },
  {
    id: 'unlock',
    title: 'Unlock Your Value',
    subtitle: 'Start your free trial',
    component: <TrialSignup />,
    duration: '1 minute'
  }
];
```

---

## Value Driver Auto-Scoring

### From QBO Data

```python
DRIVER_AUTO_CALCULATIONS = {
    'management_independence': {
        'signals': [
            {'metric': 'owner_hours_per_week', 'source': 'questionnaire'},
            {'metric': 'owner_comp_ratio', 'source': 'transactions'},
            {'metric': 'admin_staff_count', 'source': 'payroll'}
        ],
        'score_formula': '100 - (owner_hours * 2)'
    },
    'recurring_revenue': {
        'signals': [
            {'metric': 'maintenance_contract_revenue', 'source': 'invoices'},
            {'metric': 'repeat_customer_rate', 'source': 'customers'},
            {'metric': 'revenue_from_repeat', 'source': 'invoices'}
        ],
        'score_formula': '(recurring_revenue / total_revenue) * 100'
    },
    'financial_records': {
        'signals': [
            {'metric': 'reconciliation_lag_days', 'source': 'qbo_metadata'},
            {'metric': 'uncategorized_transactions', 'source': 'transactions'},
            {'metric': 'negative_accounts', 'source': 'accounts'}
        ],
        'score_formula': '100 - (uncategorized_pct * 50) - (lag_days * 2)'
    },
    'customer_diversity': {
        'signals': [
            {'metric': 'top_3_customer_pct', 'source': 'invoices'},
            {'metric': 'customer_count', 'source': 'customers'},
            {'metric': 'new_customer_rate', 'source': 'invoices'}
        ],
        'score_formula': '100 - (top_3_pct * 1.5)'
    },
    'operational_systems': {
        'signals': [
            {'metric': 'has_crm', 'source': 'questionnaire'},
            {'metric': 'has_project_tracking', 'source': 'questionnaire'},
            {'metric': 'documented_processes', 'source': 'questionnaire'}
        ],
        'score_formula': '(has_crm * 30) + (has_pm * 30) + (docs * 40)'
    }
}
```

---

## Implementation Phases

### Week 1: Foundation
- [ ] Create new database tables
- [ ] Build ShockReportEngine core
- [ ] API endpoints for report generation/retrieval
- [ ] Basic React component structure

### Week 2: EBITDA Analysis
- [ ] Owner compensation detection and analysis
- [ ] Personal expense flagging
- [ ] One-time item identification
- [ ] Add-back categorization logic

### Week 3: Multiple Penalties
- [ ] Auto-scoring from QBO data
- [ ] Penalty calculation engine
- [ ] Value unlock generation
- [ ] Roadmap item creation

### Week 4: UI/UX Polish
- [ ] Shock report visualization
- [ ] Animated comparisons
- [ ] PDF generation
- [ ] Onboarding flow integration
- [ ] Trial conversion CTA

---

## Key Metrics to Track

1. **Conversion Funnel**
   - QBO connected → Report generated
   - Report viewed → PDF downloaded
   - Report viewed → Trial started
   - Trial → Paid

2. **Shock Impact**
   - Average value gap shown
   - Average EBITDA haircut
   - Average multiple penalty
   - Most common penalties

3. **Engagement**
   - Time on shock report page
   - Sections expanded
   - PDF downloads
   - Share rate

---

## Pricing Tiers (Post-Shock)

| Feature | Free | Starter $149/mo | Pro $299/mo | Scale $499/mo |
|---------|------|-----------------|-------------|---------------|
| Shock Report (one-time) | ✓ | ✓ | ✓ | ✓ |
| Monthly Defensible EBITDA | - | ✓ | ✓ | ✓ |
| Live Valuation Meter | - | ✓ | ✓ | ✓ |
| Top 3 Value Unlocks | - | ✓ | ✓ | ✓ |
| Full Roadmap (10+ items) | - | - | ✓ | ✓ |
| CFO Add-back Review | - | - | ✓ | ✓ |
| Exit Readiness Dashboard | - | - | ✓ | ✓ |
| Quarterly CFO Call | - | - | - | ✓ |
| Deal-room Preparation | - | - | - | ✓ |

---

## The Psychology of the Shock

### Why This Works

1. **Expectation Gap**: Owner thinks 10×, buyer pays 4.5× = visceral reaction
2. **Specific Dollar Amount**: "$3.35M left on the table" is tangible
3. **Blame Assignment**: Not "you're bad" but "buyers penalize X"
4. **Hope Injection**: "Here's how to recover $2.1M"
5. **Urgency Creation**: "Every month without fixing this costs you..."
6. **Easy First Step**: "Start free trial" not "Buy now"

### Messaging Framework

**Before (Generic CFO Pitch):**
> "We help roofing contractors with bookkeeping and financial management."

**After (Shock Report Pitch):**
> "Most roofers lose 40% of their exit value because their EBITDA isn't defensible. We show you exactly how much you're leaving on the table—and how to recover it."
