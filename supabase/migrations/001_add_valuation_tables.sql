-- ============================================================
-- VALUATION TABLES MIGRATION
-- ============================================================
-- Adds tables for valuation snapshots, driver scores, and roadmap items
-- Generated from: crewcfo-knowledge-base/docs/generated/01_database_schema.sql
-- Adapted to match existing schema patterns
-- ============================================================

-- =============================================================================
-- VALUATION SNAPSHOTS TABLE
-- =============================================================================
-- Stores point-in-time valuation calculations with TTM financials, tier assessment, and confidence scoring

CREATE TABLE valuation_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    as_of_date DATE NOT NULL,
    ttm_revenue DECIMAL(15,2) NOT NULL,
    ttm_sde DECIMAL(15,2) NOT NULL,
    ttm_ebitda DECIMAL(15,2) NOT NULL,
    tier TEXT NOT NULL CHECK (tier IN ('below_avg', 'avg', 'above_avg')),
    multiple_low DECIMAL(4,2) NOT NULL,
    multiple_high DECIMAL(4,2) NOT NULL,
    ev_low DECIMAL(15,2) NOT NULL,
    ev_high DECIMAL(15,2) NOT NULL,
    confidence_score INTEGER NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 100),
    drivers_json JSONB NOT NULL DEFAULT '{}',
    audit_log_ref UUID,
    computed_by TEXT NOT NULL DEFAULT 'system',
    automation_tier TEXT NOT NULL CHECK (automation_tier IN ('rules', 'ml', 'llm', 'hybrid')),
    human_reviewed BOOLEAN NOT NULL DEFAULT FALSE,
    review_required BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Valuation Snapshots Indexes
CREATE INDEX idx_valuation_snapshots_tenant_date ON valuation_snapshots(tenant_id, as_of_date DESC);
CREATE INDEX idx_valuation_snapshots_confidence ON valuation_snapshots(confidence_score) WHERE confidence_score < 80;
CREATE INDEX idx_valuation_snapshots_review ON valuation_snapshots(tenant_id) WHERE review_required = TRUE;
CREATE INDEX idx_valuation_snapshots_tier ON valuation_snapshots(tier);
CREATE INDEX idx_valuation_snapshots_ev ON valuation_snapshots(ev_low, ev_high);

-- =============================================================================
-- DRIVER SCORES TABLE
-- =============================================================================
-- Stores individual value driver scores across 6 Matador-style categories with evidence tracking

CREATE TABLE driver_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    valuation_snapshot_id UUID REFERENCES valuation_snapshots(id) ON DELETE SET NULL,
    as_of_date DATE NOT NULL,
    driver_key TEXT NOT NULL CHECK (driver_key IN ('management_independence', 'financial_records', 'recurring_revenue', 'operational_systems', 'customer_diversity', 'market_outlook')),
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    weight DECIMAL(3,2) NOT NULL DEFAULT 1.00,
    evidence_refs JSONB NOT NULL DEFAULT '[]',
    computed_by TEXT NOT NULL DEFAULT 'system',
    confidence INTEGER NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
    automation_tier TEXT NOT NULL CHECK (automation_tier IN ('rules', 'ml', 'llm', 'hybrid')),
    human_reviewed BOOLEAN NOT NULL DEFAULT FALSE,
    review_notes TEXT,
    impact_on_multiple DECIMAL(3,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Driver Scores Indexes
CREATE INDEX idx_driver_scores_tenant_date ON driver_scores(tenant_id, as_of_date DESC);
CREATE INDEX idx_driver_scores_driver ON driver_scores(driver_key);
CREATE INDEX idx_driver_scores_snapshot ON driver_scores(valuation_snapshot_id);
CREATE INDEX idx_driver_scores_confidence ON driver_scores(confidence) WHERE confidence < 80;
CREATE INDEX idx_driver_scores_score ON driver_scores(score);
CREATE UNIQUE INDEX idx_driver_scores_unique ON driver_scores(tenant_id, as_of_date, driver_key);

-- =============================================================================
-- ROADMAP ITEMS TABLE
-- =============================================================================
-- Stores actionable improvement tasks with EV impact estimates and automation tier tracking

CREATE TABLE roadmap_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    driver_key TEXT CHECK (driver_key IN ('management_independence', 'financial_records', 'recurring_revenue', 'operational_systems', 'customer_diversity', 'market_outlook')),
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL CHECK (category IN ('weekly_ops', 'monthly_close', 'quarterly_review', 'strategic', 'compliance')),
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled', 'blocked')),
    expected_impact_ev DECIMAL(15,2),
    effort_level TEXT NOT NULL CHECK (effort_level IN ('low', 'medium', 'high')),
    estimated_hours INTEGER,
    automation_tier TEXT NOT NULL CHECK (automation_tier IN ('rules', 'ml', 'llm', 'hybrid')),
    task_refs JSONB NOT NULL DEFAULT '[]',
    assigned_to TEXT,
    due_date DATE,
    completed_at TIMESTAMPTZ,
    evidence_required BOOLEAN NOT NULL DEFAULT FALSE,
    human_approval_required BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Roadmap Items Indexes
CREATE INDEX idx_roadmap_items_tenant ON roadmap_items(tenant_id);
CREATE INDEX idx_roadmap_items_driver ON roadmap_items(driver_key);
CREATE INDEX idx_roadmap_items_status ON roadmap_items(status);
CREATE INDEX idx_roadmap_items_priority ON roadmap_items(priority);
CREATE INDEX idx_roadmap_items_due_date ON roadmap_items(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_roadmap_items_impact ON roadmap_items(expected_impact_ev DESC) WHERE expected_impact_ev IS NOT NULL;
CREATE INDEX idx_roadmap_items_category ON roadmap_items(category);
CREATE INDEX idx_roadmap_items_approval ON roadmap_items(tenant_id) WHERE human_approval_required = TRUE;

-- =============================================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- =============================================================================

-- Use existing update_updated_at() function (defined in schema.sql)
CREATE TRIGGER update_valuation_snapshots_updated_at 
    BEFORE UPDATE ON valuation_snapshots 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_driver_scores_updated_at 
    BEFORE UPDATE ON driver_scores 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_roadmap_items_updated_at 
    BEFORE UPDATE ON roadmap_items 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

-- Enable RLS on all tables
ALTER TABLE valuation_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE driver_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE roadmap_items ENABLE ROW LEVEL SECURITY;

-- RLS Policies (matching existing pattern using auth.jwt())
CREATE POLICY tenant_isolation ON valuation_snapshots
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY tenant_isolation ON driver_scores
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY tenant_isolation ON roadmap_items
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE valuation_snapshots IS 'Point-in-time business valuations with TTM financials and Matador tier assessment';
COMMENT ON COLUMN valuation_snapshots.tier IS 'Matador tier: below_avg (~3x), avg (~4.5-5x), above_avg (~7x+)';
COMMENT ON COLUMN valuation_snapshots.confidence_score IS 'AI confidence 0-100. <80 requires human review per Books OS Constitution';
COMMENT ON COLUMN valuation_snapshots.drivers_json IS 'Aggregated driver scores and evidence for this snapshot';

COMMENT ON TABLE driver_scores IS 'Individual value driver scores across 6 Matador categories with evidence tracking';
COMMENT ON COLUMN driver_scores.driver_key IS 'One of 6 drivers: management_independence, financial_records, recurring_revenue, operational_systems, customer_diversity, market_outlook';
COMMENT ON COLUMN driver_scores.evidence_refs IS 'Array of evidence IDs supporting this score';

COMMENT ON TABLE roadmap_items IS 'Actionable improvement tasks with EV impact estimates and automation tracking';
COMMENT ON COLUMN roadmap_items.expected_impact_ev IS 'Expected enterprise value increase from completing this task';
COMMENT ON COLUMN roadmap_items.human_approval_required IS 'TRUE for tasks with EV impact > $5,000 per Books OS Constitution';
