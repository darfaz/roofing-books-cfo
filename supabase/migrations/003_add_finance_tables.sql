-- ============================================================
-- FINANCE TABLES MIGRATION
-- ============================================================
-- Adds tables for budgets and cash flow forecasting
-- ============================================================

-- =============================================================================
-- BUDGETS TABLE
-- =============================================================================
-- Stores monthly budgets by category for variance analysis

CREATE TABLE IF NOT EXISTS budgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    budget_period TEXT NOT NULL,  -- Format: YYYY-MM
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month >= 1 AND month <= 12),
    categories JSONB NOT NULL DEFAULT '{}',
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(tenant_id, budget_period)
);

-- Budget Indexes
CREATE INDEX idx_budgets_tenant ON budgets(tenant_id);
CREATE INDEX idx_budgets_period ON budgets(budget_period);
CREATE INDEX idx_budgets_year ON budgets(tenant_id, year);

-- =============================================================================
-- CASH FLOW FORECASTS TABLE
-- =============================================================================
-- Stores generated cash flow forecast snapshots

CREATE TABLE IF NOT EXISTS cash_flow_forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    scenario TEXT NOT NULL CHECK (scenario IN ('base', 'optimistic', 'pessimistic')),
    starting_cash DECIMAL(15,2) NOT NULL,
    ending_cash DECIMAL(15,2) NOT NULL,
    min_cash DECIMAL(15,2) NOT NULL,
    min_cash_week INTEGER NOT NULL,
    runway_weeks INTEGER NOT NULL,
    summary_json JSONB NOT NULL DEFAULT '{}',
    weekly_forecast_json JSONB NOT NULL DEFAULT '[]',
    ar_total DECIMAL(15,2),
    ap_total DECIMAL(15,2),
    computed_by TEXT NOT NULL DEFAULT 'system',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(tenant_id, forecast_date, scenario)
);

-- Cash Flow Forecast Indexes
CREATE INDEX idx_cash_forecasts_tenant ON cash_flow_forecasts(tenant_id);
CREATE INDEX idx_cash_forecasts_date ON cash_flow_forecasts(tenant_id, forecast_date DESC);
CREATE INDEX idx_cash_forecasts_runway ON cash_flow_forecasts(runway_weeks) WHERE runway_weeks < 8;

-- =============================================================================
-- VENDOR PAYMENT SCHEDULES TABLE
-- =============================================================================
-- Stores planned payment schedules for AP management

CREATE TABLE IF NOT EXISTS vendor_payment_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vendor_id UUID REFERENCES vendors(id) ON DELETE SET NULL,
    transaction_id UUID REFERENCES transactions(id) ON DELETE CASCADE,
    scheduled_date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    status TEXT NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'pending', 'paid', 'cancelled')),
    payment_method TEXT,  -- 'check', 'ach', 'credit_card', 'wire'
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Payment Schedule Indexes
CREATE INDEX idx_payment_schedules_tenant ON vendor_payment_schedules(tenant_id);
CREATE INDEX idx_payment_schedules_date ON vendor_payment_schedules(scheduled_date);
CREATE INDEX idx_payment_schedules_vendor ON vendor_payment_schedules(vendor_id);
CREATE INDEX idx_payment_schedules_status ON vendor_payment_schedules(status) WHERE status = 'scheduled';

-- =============================================================================
-- ADD CATEGORY COLUMN TO TRANSACTIONS IF NOT EXISTS
-- =============================================================================
-- This column is used for budget categorization

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'transactions' AND column_name = 'category'
    ) THEN
        ALTER TABLE transactions ADD COLUMN category TEXT;
        CREATE INDEX idx_transactions_category ON transactions(category) WHERE category IS NOT NULL;
    END IF;
END $$;

-- =============================================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- =============================================================================

CREATE TRIGGER update_budgets_updated_at
    BEFORE UPDATE ON budgets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_payment_schedules_updated_at
    BEFORE UPDATE ON vendor_payment_schedules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

ALTER TABLE budgets ENABLE ROW LEVEL SECURITY;
ALTER TABLE cash_flow_forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendor_payment_schedules ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY tenant_isolation ON budgets
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY tenant_isolation ON cash_flow_forecasts
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY tenant_isolation ON vendor_payment_schedules
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE budgets IS 'Monthly budgets by category for variance analysis';
COMMENT ON COLUMN budgets.categories IS 'JSON with revenue, cogs, and operating expense budgets';

COMMENT ON TABLE cash_flow_forecasts IS 'Stored cash flow forecast snapshots for historical tracking';
COMMENT ON COLUMN cash_flow_forecasts.runway_weeks IS 'Weeks until projected cash goes negative';

COMMENT ON TABLE vendor_payment_schedules IS 'Planned payment schedules for AP management';
