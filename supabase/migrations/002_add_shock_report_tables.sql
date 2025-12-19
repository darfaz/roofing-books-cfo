-- Valuation Shock Report Tables
-- Migration: 002_add_shock_report_tables.sql
-- Purpose: Support the Valuation Shock Report conversion flow

-- ============================================================
-- Table: valuation_shock_reports
-- Stores generated shock reports with the "expected vs actual" gap
-- ============================================================
CREATE TABLE IF NOT EXISTS valuation_shock_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT now(),

    -- What owner thinks (reported/expected)
    reported_revenue NUMERIC,
    reported_ebitda NUMERIC,
    reported_owner_comp NUMERIC,
    reported_addbacks NUMERIC,
    expected_multiple NUMERIC DEFAULT 10.0,
    expected_valuation NUMERIC,

    -- What buyer sees (defensible)
    defensible_ebitda NUMERIC,
    defensible_sde NUMERIC,
    buyer_multiple_low NUMERIC,
    buyer_multiple_high NUMERIC,
    buyer_valuation_low NUMERIC,
    buyer_valuation_high NUMERIC,

    -- The gap (the shock)
    ebitda_haircut NUMERIC,
    multiple_penalty NUMERIC,
    value_gap NUMERIC,
    value_gap_percentage NUMERIC,

    -- Detailed breakdowns (JSONB for flexibility)
    ebitda_adjustments JSONB DEFAULT '[]'::jsonb,
    multiple_penalties JSONB DEFAULT '[]'::jsonb,
    driver_scores JSONB DEFAULT '{}'::jsonb,

    -- Value recovery opportunities
    value_unlocks JSONB DEFAULT '[]'::jsonb,
    total_recoverable_value NUMERIC,

    -- Tier determination
    tier VARCHAR(20) CHECK (tier IN ('below_avg', 'avg', 'above_avg')),

    -- Data quality metrics
    qbo_data_range_start DATE,
    qbo_data_range_end DATE,
    transaction_count INTEGER,
    invoice_count INTEGER,
    expense_count INTEGER,
    confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),

    -- Tracking
    pdf_generated BOOLEAN DEFAULT false,
    pdf_downloaded BOOLEAN DEFAULT false,
    trial_started BOOLEAN DEFAULT false,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Index for quick lookups
CREATE INDEX IF NOT EXISTS idx_shock_reports_tenant ON valuation_shock_reports(tenant_id);
CREATE INDEX IF NOT EXISTS idx_shock_reports_generated ON valuation_shock_reports(generated_at DESC);

-- ============================================================
-- Table: ebitda_adjustments
-- Tracks individual add-back decisions and their status
-- ============================================================
CREATE TABLE IF NOT EXISTS ebitda_adjustments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    shock_report_id UUID REFERENCES valuation_shock_reports(id) ON DELETE CASCADE,

    -- Adjustment classification
    adjustment_type VARCHAR(50) NOT NULL CHECK (adjustment_type IN (
        'owner_compensation',
        'personal_expense',
        'one_time_revenue',
        'one_time_expense',
        'non_recurring',
        'related_party',
        'discretionary',
        'non_operating'
    )),

    -- Buyer decision
    category VARCHAR(20) NOT NULL CHECK (category IN (
        'accepted',      -- Buyer will accept this add-back
        'rejected',      -- Buyer will reject this add-back
        'partial',       -- Buyer will accept portion
        'needs_review'   -- Requires human CFO review
    )),

    -- Details
    description TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    accepted_amount NUMERIC DEFAULT 0,  -- How much buyer will accept

    -- Evidence linking
    transaction_ids JSONB DEFAULT '[]'::jsonb,
    account_ids JSONB DEFAULT '[]'::jsonb,
    vendor_names JSONB DEFAULT '[]'::jsonb,

    -- Buyer perspective
    buyer_concern TEXT,
    rejection_reason TEXT,

    -- Remediation
    is_recoverable BOOLEAN DEFAULT true,
    remediation_action TEXT,
    remediation_effort VARCHAR(20) CHECK (remediation_effort IN ('low', 'medium', 'high')),
    remediation_impact NUMERIC,  -- $ impact if fixed

    -- Review status
    auto_flagged BOOLEAN DEFAULT true,
    human_reviewed BOOLEAN DEFAULT false,
    reviewer_id UUID,
    reviewer_notes TEXT,
    reviewed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ebitda_adj_tenant ON ebitda_adjustments(tenant_id);
CREATE INDEX IF NOT EXISTS idx_ebitda_adj_report ON ebitda_adjustments(shock_report_id);
CREATE INDEX IF NOT EXISTS idx_ebitda_adj_type ON ebitda_adjustments(adjustment_type);

-- ============================================================
-- Table: multiple_penalties
-- Documents why the multiple is reduced from buyer perspective
-- ============================================================
CREATE TABLE IF NOT EXISTS multiple_penalties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    shock_report_id UUID REFERENCES valuation_shock_reports(id) ON DELETE CASCADE,

    -- Which driver caused the penalty
    driver_key VARCHAR(50) NOT NULL CHECK (driver_key IN (
        'management_independence',
        'financial_records',
        'recurring_revenue',
        'operational_systems',
        'customer_diversity',
        'market_outlook'
    )),

    -- The penalty
    penalty_amount NUMERIC NOT NULL,  -- e.g., -1.5 means -1.5x multiple
    baseline_multiple NUMERIC,         -- Starting multiple before penalty
    resulting_multiple NUMERIC,        -- Multiple after this penalty

    -- Driver score that triggered penalty
    driver_score INTEGER CHECK (driver_score >= 0 AND driver_score <= 100),

    -- Buyer language (this is key for the "shock" effect)
    reason TEXT NOT NULL,              -- Short reason: "Owner IS the business"
    buyer_concern TEXT,                -- Detailed concern buyers have
    due_diligence_flag TEXT,           -- What buyer will investigate

    -- Threshold info
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    threshold_value NUMERIC,
    threshold_comparison VARCHAR(10),  -- 'lt', 'gt', 'eq', 'lte', 'gte'

    -- Remediation
    remediation_action TEXT NOT NULL,
    remediation_timeline VARCHAR(50),  -- "3-6 months", "6-12 months"
    remediation_effort VARCHAR(20) CHECK (remediation_effort IN ('low', 'medium', 'high')),
    remediation_impact NUMERIC,        -- $ value if fixed (EV increase)
    multiple_recovery NUMERIC,         -- How much multiple recovers if fixed

    created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_mult_penalties_tenant ON multiple_penalties(tenant_id);
CREATE INDEX IF NOT EXISTS idx_mult_penalties_report ON multiple_penalties(shock_report_id);
CREATE INDEX IF NOT EXISTS idx_mult_penalties_driver ON multiple_penalties(driver_key);

-- ============================================================
-- Table: value_unlocks
-- Prioritized actions to recover lost value
-- ============================================================
CREATE TABLE IF NOT EXISTS value_unlocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    shock_report_id UUID REFERENCES valuation_shock_reports(id) ON DELETE CASCADE,

    -- Priority ordering
    priority_rank INTEGER NOT NULL,

    -- Action details
    title TEXT NOT NULL,
    description TEXT,
    action_type VARCHAR(50) CHECK (action_type IN (
        'ebitda_recovery',      -- Recover rejected add-backs
        'multiple_expansion',   -- Improve driver scores
        'revenue_quality',      -- Improve revenue mix
        'cost_optimization',    -- Reduce expenses
        'risk_reduction'        -- Reduce buyer risk
    )),

    -- Impact
    ebitda_impact NUMERIC DEFAULT 0,
    multiple_impact NUMERIC DEFAULT 0,
    ev_impact NUMERIC NOT NULL,  -- Total enterprise value impact

    -- Effort
    effort_level VARCHAR(20) CHECK (effort_level IN ('low', 'medium', 'high')),
    estimated_hours INTEGER,
    timeline VARCHAR(50),

    -- Related items
    related_driver VARCHAR(50),
    related_adjustment_id UUID REFERENCES ebitda_adjustments(id),
    related_penalty_id UUID REFERENCES multiple_penalties(id),

    -- Paywall
    is_locked BOOLEAN DEFAULT true,  -- Locked until paid
    is_preview BOOLEAN DEFAULT false, -- Shown as teaser

    -- Tracking
    unlocked_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_value_unlocks_tenant ON value_unlocks(tenant_id);
CREATE INDEX IF NOT EXISTS idx_value_unlocks_report ON value_unlocks(shock_report_id);
CREATE INDEX IF NOT EXISTS idx_value_unlocks_priority ON value_unlocks(priority_rank);

-- ============================================================
-- Table: shock_report_analytics
-- Track user engagement with shock reports
-- ============================================================
CREATE TABLE IF NOT EXISTS shock_report_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    shock_report_id UUID REFERENCES valuation_shock_reports(id) ON DELETE CASCADE,

    -- Event tracking
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN (
        'report_generated',
        'report_viewed',
        'section_expanded',
        'pdf_downloaded',
        'share_clicked',
        'trial_cta_clicked',
        'trial_started',
        'paid_converted'
    )),

    -- Event details
    section_name VARCHAR(100),  -- Which section was expanded
    time_on_page INTEGER,       -- Seconds spent
    scroll_depth INTEGER,       -- Percentage scrolled

    -- Context
    referrer TEXT,
    user_agent TEXT,
    ip_address INET,

    created_at TIMESTAMPTZ DEFAULT now()
);

-- Index for analytics queries
CREATE INDEX IF NOT EXISTS idx_analytics_tenant ON shock_report_analytics(tenant_id);
CREATE INDEX IF NOT EXISTS idx_analytics_event ON shock_report_analytics(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_created ON shock_report_analytics(created_at);

-- ============================================================
-- Enable RLS
-- ============================================================
ALTER TABLE valuation_shock_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE ebitda_adjustments ENABLE ROW LEVEL SECURITY;
ALTER TABLE multiple_penalties ENABLE ROW LEVEL SECURITY;
ALTER TABLE value_unlocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE shock_report_analytics ENABLE ROW LEVEL SECURITY;

-- RLS Policies (tenant isolation)
CREATE POLICY "Tenants can view own shock reports" ON valuation_shock_reports
    FOR SELECT USING (tenant_id = auth.uid() OR tenant_id IN (
        SELECT tenant_id FROM tenant_users WHERE user_id = auth.uid()
    ));

CREATE POLICY "Tenants can insert own shock reports" ON valuation_shock_reports
    FOR INSERT WITH CHECK (tenant_id = auth.uid() OR tenant_id IN (
        SELECT tenant_id FROM tenant_users WHERE user_id = auth.uid()
    ));

CREATE POLICY "Tenants can view own adjustments" ON ebitda_adjustments
    FOR SELECT USING (tenant_id = auth.uid() OR tenant_id IN (
        SELECT tenant_id FROM tenant_users WHERE user_id = auth.uid()
    ));

CREATE POLICY "Tenants can view own penalties" ON multiple_penalties
    FOR SELECT USING (tenant_id = auth.uid() OR tenant_id IN (
        SELECT tenant_id FROM tenant_users WHERE user_id = auth.uid()
    ));

CREATE POLICY "Tenants can view own unlocks" ON value_unlocks
    FOR SELECT USING (tenant_id = auth.uid() OR tenant_id IN (
        SELECT tenant_id FROM tenant_users WHERE user_id = auth.uid()
    ));

-- ============================================================
-- Helper function: Calculate value gap percentage
-- ============================================================
CREATE OR REPLACE FUNCTION calculate_value_gap_percentage(
    expected_val NUMERIC,
    actual_val NUMERIC
) RETURNS NUMERIC AS $$
BEGIN
    IF expected_val IS NULL OR expected_val = 0 THEN
        RETURN 0;
    END IF;
    RETURN ROUND(((expected_val - actual_val) / expected_val) * 100, 1);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================
-- Trigger: Update updated_at timestamp
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_shock_reports_updated_at
    BEFORE UPDATE ON valuation_shock_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ebitda_adjustments_updated_at
    BEFORE UPDATE ON ebitda_adjustments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
