-- ============================================================
-- ROOFING BOOKS CFO - SUPABASE SCHEMA
-- ============================================================
-- Run this entire file in Supabase SQL Editor
-- https://supabase.com/dashboard/project/YOUR_PROJECT/sql
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- CORE TABLES
-- ============================================================

-- Tenants (multi-tenant support)
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    legal_name TEXT,
    ein TEXT,  -- Employer Identification Number
    address_line1 TEXT,
    address_line2 TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    phone TEXT,
    email TEXT,
    website TEXT,
    fiscal_year_start_month INTEGER DEFAULT 1,  -- 1 = January
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users (linked to Supabase Auth)
CREATE TABLE users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'owner' CHECK (role IN ('owner', 'bookkeeper', 'cfo', 'viewer')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Integrations (QBO, Plaid, etc.)
CREATE TABLE tenant_integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    provider TEXT NOT NULL,  -- 'quickbooks', 'plaid', 'slack'
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMPTZ,
    realm_id TEXT,  -- QBO company ID
    metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, provider)
);

-- ============================================================
-- CHART OF ACCOUNTS
-- ============================================================

CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Account identifiers
    code TEXT NOT NULL,  -- e.g., '5100'
    name TEXT NOT NULL,  -- e.g., 'Materials COGS'
    
    -- Classification
    account_type TEXT NOT NULL CHECK (account_type IN (
        'asset', 'liability', 'equity', 'revenue', 'expense'
    )),
    account_subtype TEXT,  -- e.g., 'bank', 'accounts_receivable', 'cogs'
    
    -- Hierarchy
    parent_id UUID REFERENCES accounts(id),
    hierarchy_level INTEGER DEFAULT 1,
    
    -- QBO sync
    qbo_id TEXT,
    qbo_sync_token TEXT,
    
    -- Behavior
    is_active BOOLEAN DEFAULT true,
    is_system BOOLEAN DEFAULT false,  -- System accounts can't be deleted
    normal_balance TEXT DEFAULT 'debit' CHECK (normal_balance IN ('debit', 'credit')),
    
    -- Job costing
    is_job_cost_account BOOLEAN DEFAULT false,
    job_cost_category TEXT CHECK (job_cost_category IN ('labor', 'materials', 'subcontractor', 'equipment', 'overhead')),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(tenant_id, code)
);

-- Index for common queries
CREATE INDEX idx_accounts_tenant ON accounts(tenant_id);
CREATE INDEX idx_accounts_type ON accounts(tenant_id, account_type);
CREATE INDEX idx_accounts_qbo ON accounts(tenant_id, qbo_id);

-- ============================================================
-- CUSTOMERS & VENDORS
-- ============================================================

CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Basic info
    name TEXT NOT NULL,
    display_name TEXT,
    company_name TEXT,
    
    -- Contact
    email TEXT,
    phone TEXT,
    
    -- Address
    billing_address_line1 TEXT,
    billing_address_line2 TEXT,
    billing_city TEXT,
    billing_state TEXT,
    billing_zip TEXT,
    
    -- Classification
    customer_type TEXT DEFAULT 'residential' CHECK (customer_type IN ('residential', 'commercial', 'insurance', 'builder')),
    
    -- Payment terms
    payment_terms_days INTEGER DEFAULT 30,
    
    -- QBO sync
    qbo_id TEXT,
    qbo_sync_token TEXT,
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE vendors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Basic info
    name TEXT NOT NULL,
    display_name TEXT,
    
    -- Contact
    email TEXT,
    phone TEXT,
    
    -- Address
    address_line1 TEXT,
    address_line2 TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    
    -- Classification
    vendor_type TEXT DEFAULT 'supplier' CHECK (vendor_type IN ('supplier', 'subcontractor', 'utility', 'professional', 'other')),
    default_expense_account_id UUID REFERENCES accounts(id),
    
    -- Payment info
    payment_terms_days INTEGER DEFAULT 30,
    
    -- Compliance
    ein TEXT,
    w9_on_file BOOLEAN DEFAULT false,
    w9_received_date DATE,
    insurance_certificate_on_file BOOLEAN DEFAULT false,
    insurance_expiry_date DATE,
    
    -- QBO sync
    qbo_id TEXT,
    qbo_sync_token TEXT,
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_customers_tenant ON customers(tenant_id);
CREATE INDEX idx_vendors_tenant ON vendors(tenant_id);

-- ============================================================
-- JOBS (ROOFING PROJECTS)
-- ============================================================

CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Identification
    job_number TEXT NOT NULL,  -- e.g., 'JOB-2024-001'
    name TEXT NOT NULL,  -- e.g., 'Smith Residence - Roof Replacement'
    description TEXT,
    
    -- Customer
    customer_id UUID REFERENCES customers(id),
    
    -- Location
    job_address_line1 TEXT,
    job_address_line2 TEXT,
    job_city TEXT,
    job_state TEXT,
    job_zip TEXT,
    
    -- Classification
    job_type TEXT DEFAULT 'replacement' CHECK (job_type IN (
        'replacement', 'repair', 'new_construction', 'commercial', 'insurance_claim', 'maintenance'
    )),
    
    -- Dates
    estimate_date DATE,
    start_date DATE,
    target_completion_date DATE,
    actual_completion_date DATE,
    
    -- Status
    status TEXT DEFAULT 'estimate' CHECK (status IN (
        'estimate', 'pending', 'scheduled', 'in_progress', 'completed', 'closed', 'cancelled'
    )),
    
    -- Financials
    contract_amount DECIMAL(12,2) DEFAULT 0,
    estimated_cost DECIMAL(12,2) DEFAULT 0,
    estimated_margin_pct DECIMAL(5,2),
    
    -- Running totals (updated by triggers)
    actual_revenue DECIMAL(12,2) DEFAULT 0,
    actual_cost DECIMAL(12,2) DEFAULT 0,
    actual_margin_pct DECIMAL(5,2),
    
    -- Insurance (if applicable)
    is_insurance_job BOOLEAN DEFAULT false,
    insurance_company TEXT,
    claim_number TEXT,
    deductible_amount DECIMAL(10,2),
    
    -- QBO sync
    qbo_customer_id TEXT,
    qbo_job_id TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(tenant_id, job_number)
);

CREATE INDEX idx_jobs_tenant ON jobs(tenant_id);
CREATE INDEX idx_jobs_status ON jobs(tenant_id, status);
CREATE INDEX idx_jobs_customer ON jobs(customer_id);

-- ============================================================
-- TRANSACTIONS
-- ============================================================

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Transaction info
    transaction_date DATE NOT NULL,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN (
        'invoice', 'payment', 'bill', 'bill_payment', 'expense', 'deposit',
        'transfer', 'journal_entry', 'credit_memo', 'refund'
    )),
    
    -- Reference
    reference_number TEXT,  -- Check #, invoice #, etc.
    memo TEXT,
    
    -- Parties
    customer_id UUID REFERENCES customers(id),
    vendor_id UUID REFERENCES vendors(id),
    
    -- Amounts
    total_amount DECIMAL(12,2) NOT NULL,
    
    -- Status
    status TEXT DEFAULT 'pending' CHECK (status IN (
        'pending', 'posted', 'voided', 'reconciled'
    )),
    
    -- Classification
    classification_status TEXT DEFAULT 'unclassified' CHECK (classification_status IN (
        'unclassified', 'auto_classified', 'manual_classified', 'review_needed'
    )),
    classification_confidence DECIMAL(3,2),  -- 0.00 to 1.00
    classified_by TEXT,  -- 'rule', 'ml', 'llm', 'user'
    classified_at TIMESTAMPTZ,
    
    -- QBO sync
    qbo_id TEXT,
    qbo_type TEXT,  -- QBO object type
    qbo_sync_token TEXT,
    qbo_synced_at TIMESTAMPTZ,
    
    -- Audit
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transaction lines (double-entry)
CREATE TABLE transaction_lines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    
    -- Account
    account_id UUID NOT NULL REFERENCES accounts(id),
    
    -- Job (for job costing)
    job_id UUID REFERENCES jobs(id),
    
    -- Amounts (one will be positive, one negative for double-entry)
    debit_amount DECIMAL(12,2) DEFAULT 0,
    credit_amount DECIMAL(12,2) DEFAULT 0,
    
    -- Description
    description TEXT,
    
    -- Line order
    line_number INTEGER DEFAULT 1,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_transactions_tenant ON transactions(tenant_id);
CREATE INDEX idx_transactions_date ON transactions(tenant_id, transaction_date);
CREATE INDEX idx_transactions_type ON transactions(tenant_id, transaction_type);
CREATE INDEX idx_transactions_status ON transactions(tenant_id, classification_status);
CREATE INDEX idx_transaction_lines_account ON transaction_lines(account_id);
CREATE INDEX idx_transaction_lines_job ON transaction_lines(job_id);

-- ============================================================
-- JOB COSTS
-- ============================================================

CREATE TABLE job_costs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    
    -- Source transaction
    transaction_id UUID REFERENCES transactions(id),
    transaction_line_id UUID REFERENCES transaction_lines(id),
    
    -- Cost details
    cost_date DATE NOT NULL,
    cost_category TEXT NOT NULL CHECK (cost_category IN (
        'labor', 'materials', 'subcontractor', 'equipment', 'overhead', 'other'
    )),
    
    -- Description
    description TEXT,
    vendor_id UUID REFERENCES vendors(id),
    
    -- Amounts
    quantity DECIMAL(10,2),
    unit_cost DECIMAL(10,2),
    total_cost DECIMAL(12,2) NOT NULL,
    
    -- Labor-specific
    labor_hours DECIMAL(6,2),
    labor_rate DECIMAL(8,2),
    labor_burden_rate DECIMAL(5,2) DEFAULT 0.20,  -- 20% burden
    
    -- Billing status
    is_billable BOOLEAN DEFAULT true,
    is_billed BOOLEAN DEFAULT false,
    billed_amount DECIMAL(12,2),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_job_costs_job ON job_costs(job_id);
CREATE INDEX idx_job_costs_category ON job_costs(tenant_id, cost_category);

-- ============================================================
-- CLASSIFICATION RULES
-- ============================================================

CREATE TABLE classification_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Rule info
    name TEXT NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 100,  -- Lower = higher priority
    is_active BOOLEAN DEFAULT true,
    
    -- Match conditions (all must match)
    match_vendor_name TEXT,  -- ILIKE pattern
    match_memo TEXT,  -- ILIKE pattern
    match_amount_min DECIMAL(12,2),
    match_amount_max DECIMAL(12,2),
    match_transaction_type TEXT,
    
    -- Classification result
    target_account_id UUID NOT NULL REFERENCES accounts(id),
    target_job_id UUID REFERENCES jobs(id),  -- Optional: assign to specific job
    
    -- Stats
    times_applied INTEGER DEFAULT 0,
    last_applied_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_classification_rules_tenant ON classification_rules(tenant_id, is_active, priority);

-- ============================================================
-- CASH FLOW & FORECASTING
-- ============================================================

-- Daily cash position snapshots
CREATE TABLE cash_positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    position_date DATE NOT NULL,
    
    -- Bank balances
    total_cash DECIMAL(14,2) NOT NULL,
    operating_account DECIMAL(14,2) DEFAULT 0,
    savings_account DECIMAL(14,2) DEFAULT 0,
    
    -- AR/AP
    ar_total DECIMAL(14,2) DEFAULT 0,
    ar_current DECIMAL(14,2) DEFAULT 0,
    ar_overdue DECIMAL(14,2) DEFAULT 0,
    ap_total DECIMAL(14,2) DEFAULT 0,
    ap_overdue DECIMAL(14,2) DEFAULT 0,
    
    -- Metrics
    runway_weeks INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(tenant_id, position_date)
);

-- 13-week cash forecast
CREATE TABLE cash_forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    forecast_date DATE NOT NULL,  -- When forecast was generated
    week_number INTEGER NOT NULL,  -- 1-13
    week_start_date DATE NOT NULL,
    
    -- Projections
    starting_cash DECIMAL(14,2),
    projected_inflows DECIMAL(14,2) DEFAULT 0,
    projected_outflows DECIMAL(14,2) DEFAULT 0,
    ending_cash DECIMAL(14,2),
    
    -- Confidence bands
    optimistic_cash DECIMAL(14,2),
    pessimistic_cash DECIMAL(14,2),
    confidence_pct DECIMAL(5,2),
    
    -- Details (JSONB for flexibility)
    inflow_details JSONB DEFAULT '{}',
    outflow_details JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_cash_positions_tenant ON cash_positions(tenant_id, position_date DESC);
CREATE INDEX idx_cash_forecasts_tenant ON cash_forecasts(tenant_id, forecast_date DESC);

-- ============================================================
-- CFO BRIEFS
-- ============================================================

CREATE TABLE cfo_briefs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    brief_date DATE NOT NULL,
    brief_type TEXT DEFAULT 'weekly' CHECK (brief_type IN ('weekly', 'monthly', 'custom')),
    
    -- Metrics snapshot
    metrics JSONB NOT NULL,
    
    -- AI-generated content
    narrative TEXT,
    html_content TEXT,
    
    -- Delivery
    sent_at TIMESTAMPTZ,
    sent_to TEXT[],  -- Email addresses
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- AUDIT LOG
-- ============================================================

CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- What happened
    action TEXT NOT NULL,  -- 'create', 'update', 'delete', 'login', etc.
    table_name TEXT,
    record_id UUID,
    
    -- Details
    old_values JSONB,
    new_values JSONB,
    metadata JSONB DEFAULT '{}',
    
    -- When
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- IP/device (optional)
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX idx_audit_log_tenant ON audit_log(tenant_id, created_at DESC);
CREATE INDEX idx_audit_log_table ON audit_log(table_name, record_id);

-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================

-- Enable RLS on all tenant-scoped tables
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendors ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE transaction_lines ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_costs ENABLE ROW LEVEL SECURITY;
ALTER TABLE classification_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE cash_positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE cash_forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE cfo_briefs ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Create policies (users can only see their tenant's data)
-- Note: These assume user's tenant_id is stored in auth.jwt() -> user_metadata -> tenant_id

CREATE POLICY tenant_isolation ON tenants
    FOR ALL USING (id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY tenant_isolation ON users
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY tenant_isolation ON tenant_integrations
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY tenant_isolation ON accounts
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY tenant_isolation ON customers
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY tenant_isolation ON vendors
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY tenant_isolation ON jobs
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY tenant_isolation ON transactions
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY tenant_isolation ON transaction_lines
    FOR ALL USING (
        transaction_id IN (
            SELECT id FROM transactions 
            WHERE tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid
        )
    );

CREATE POLICY tenant_isolation ON job_costs
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY tenant_isolation ON classification_rules
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY tenant_isolation ON cash_positions
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY tenant_isolation ON cash_forecasts
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY tenant_isolation ON cfo_briefs
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY tenant_isolation ON audit_log
    FOR ALL USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

-- ============================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_vendors_updated_at BEFORE UPDATE ON vendors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_job_costs_updated_at BEFORE UPDATE ON job_costs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_classification_rules_updated_at BEFORE UPDATE ON classification_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Recalculate job totals when job_costs change
CREATE OR REPLACE FUNCTION recalculate_job_totals()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE jobs SET
        actual_cost = (
            SELECT COALESCE(SUM(total_cost), 0) 
            FROM job_costs 
            WHERE job_id = COALESCE(NEW.job_id, OLD.job_id)
        ),
        actual_margin_pct = CASE 
            WHEN actual_revenue > 0 THEN 
                ((actual_revenue - actual_cost) / actual_revenue * 100)::DECIMAL(5,2)
            ELSE 0
        END,
        updated_at = NOW()
    WHERE id = COALESCE(NEW.job_id, OLD.job_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER recalculate_job_totals_trigger
    AFTER INSERT OR UPDATE OR DELETE ON job_costs
    FOR EACH ROW EXECUTE FUNCTION recalculate_job_totals();

-- ============================================================
-- SEED DATA: DEFAULT CHART OF ACCOUNTS (Roofing-specific)
-- ============================================================

-- Run this after creating a tenant to set up their chart of accounts
-- Replace 'YOUR_TENANT_ID' with actual tenant UUID

/*
INSERT INTO accounts (tenant_id, code, name, account_type, account_subtype, is_system, is_job_cost_account, job_cost_category) VALUES
-- Assets
('YOUR_TENANT_ID', '1000', 'Operating Checking', 'asset', 'bank', true, false, null),
('YOUR_TENANT_ID', '1100', 'Savings', 'asset', 'bank', false, false, null),
('YOUR_TENANT_ID', '1200', 'Accounts Receivable', 'asset', 'accounts_receivable', true, false, null),
('YOUR_TENANT_ID', '1300', 'Inventory - Materials', 'asset', 'inventory', false, false, null),
('YOUR_TENANT_ID', '1500', 'Vehicles', 'asset', 'fixed_asset', false, false, null),
('YOUR_TENANT_ID', '1600', 'Equipment', 'asset', 'fixed_asset', false, false, null),

-- Liabilities
('YOUR_TENANT_ID', '2000', 'Accounts Payable', 'liability', 'accounts_payable', true, false, null),
('YOUR_TENANT_ID', '2100', 'Credit Card', 'liability', 'credit_card', false, false, null),
('YOUR_TENANT_ID', '2200', 'Payroll Liabilities', 'liability', 'other_current_liability', false, false, null),
('YOUR_TENANT_ID', '2300', 'Sales Tax Payable', 'liability', 'other_current_liability', false, false, null),
('YOUR_TENANT_ID', '2500', 'Vehicle Loans', 'liability', 'long_term_liability', false, false, null),
('YOUR_TENANT_ID', '2600', 'Equipment Loans', 'liability', 'long_term_liability', false, false, null),

-- Equity
('YOUR_TENANT_ID', '3000', 'Owner Equity', 'equity', 'owners_equity', true, false, null),
('YOUR_TENANT_ID', '3100', 'Owner Draws', 'equity', 'owners_equity', false, false, null),
('YOUR_TENANT_ID', '3200', 'Retained Earnings', 'equity', 'retained_earnings', true, false, null),

-- Revenue
('YOUR_TENANT_ID', '4000', 'Roofing Revenue', 'revenue', 'income', true, false, null),
('YOUR_TENANT_ID', '4100', 'Repair Revenue', 'revenue', 'income', false, false, null),
('YOUR_TENANT_ID', '4200', 'Insurance Revenue', 'revenue', 'income', false, false, null),
('YOUR_TENANT_ID', '4900', 'Other Income', 'revenue', 'other_income', false, false, null),

-- Cost of Goods Sold (Job Costs)
('YOUR_TENANT_ID', '5000', 'Cost of Goods Sold', 'expense', 'cogs', true, false, null),
('YOUR_TENANT_ID', '5100', 'Materials', 'expense', 'cogs', false, true, 'materials'),
('YOUR_TENANT_ID', '5200', 'Subcontractors', 'expense', 'cogs', false, true, 'subcontractor'),
('YOUR_TENANT_ID', '5300', 'Labor - Direct', 'expense', 'cogs', false, true, 'labor'),
('YOUR_TENANT_ID', '5400', 'Equipment Rental', 'expense', 'cogs', false, true, 'equipment'),
('YOUR_TENANT_ID', '5500', 'Permits & Fees', 'expense', 'cogs', false, true, 'overhead'),
('YOUR_TENANT_ID', '5600', 'Dump Fees', 'expense', 'cogs', false, true, 'overhead'),

-- Operating Expenses
('YOUR_TENANT_ID', '6000', 'Operating Expenses', 'expense', 'expense', true, false, null),
('YOUR_TENANT_ID', '6100', 'Advertising & Marketing', 'expense', 'expense', false, false, null),
('YOUR_TENANT_ID', '6200', 'Office Expenses', 'expense', 'expense', false, false, null),
('YOUR_TENANT_ID', '6300', 'Insurance - General Liability', 'expense', 'expense', false, false, null),
('YOUR_TENANT_ID', '6310', 'Insurance - Workers Comp', 'expense', 'expense', false, false, null),
('YOUR_TENANT_ID', '6320', 'Insurance - Vehicle', 'expense', 'expense', false, false, null),
('YOUR_TENANT_ID', '6400', 'Vehicle Expense', 'expense', 'expense', false, false, null),
('YOUR_TENANT_ID', '6500', 'Fuel', 'expense', 'expense', false, false, null),
('YOUR_TENANT_ID', '6600', 'Tools & Small Equipment', 'expense', 'expense', false, false, null),
('YOUR_TENANT_ID', '6700', 'Professional Fees', 'expense', 'expense', false, false, null),
('YOUR_TENANT_ID', '6800', 'Software & Subscriptions', 'expense', 'expense', false, false, null),
('YOUR_TENANT_ID', '6900', 'Payroll - Admin', 'expense', 'expense', false, false, null),
('YOUR_TENANT_ID', '6950', 'Payroll Taxes', 'expense', 'expense', false, false, null),
('YOUR_TENANT_ID', '7000', 'Rent', 'expense', 'expense', false, false, null),
('YOUR_TENANT_ID', '7100', 'Utilities', 'expense', 'expense', false, false, null),
('YOUR_TENANT_ID', '7200', 'Phone & Internet', 'expense', 'expense', false, false, null),
('YOUR_TENANT_ID', '7500', 'Interest Expense', 'expense', 'expense', false, false, null),
('YOUR_TENANT_ID', '7900', 'Miscellaneous', 'expense', 'expense', false, false, null);
*/

-- ============================================================
-- VIEWS (for common queries)
-- ============================================================

-- AR Aging view
CREATE OR REPLACE VIEW v_ar_aging AS
SELECT 
    t.tenant_id,
    t.id as transaction_id,
    t.transaction_date,
    t.reference_number as invoice_number,
    c.name as customer_name,
    t.total_amount,
    t.total_amount - COALESCE(payments.paid, 0) as balance_due,
    CURRENT_DATE - t.transaction_date as days_outstanding,
    CASE 
        WHEN CURRENT_DATE - t.transaction_date <= 30 THEN 'current'
        WHEN CURRENT_DATE - t.transaction_date <= 60 THEN '31-60'
        WHEN CURRENT_DATE - t.transaction_date <= 90 THEN '61-90'
        ELSE '90+'
    END as aging_bucket
FROM transactions t
LEFT JOIN customers c ON t.customer_id = c.id
LEFT JOIN (
    SELECT 
        reference_number,
        SUM(total_amount) as paid
    FROM transactions 
    WHERE transaction_type = 'payment'
    GROUP BY reference_number
) payments ON t.reference_number = payments.reference_number
WHERE t.transaction_type = 'invoice'
AND t.status != 'voided';

-- Job profitability view
CREATE OR REPLACE VIEW v_job_profitability AS
SELECT 
    j.tenant_id,
    j.id as job_id,
    j.job_number,
    j.name as job_name,
    j.customer_id,
    c.name as customer_name,
    j.job_type,
    j.status,
    j.contract_amount,
    j.actual_revenue,
    j.actual_cost,
    j.actual_revenue - j.actual_cost as gross_profit,
    CASE 
        WHEN j.actual_revenue > 0 
        THEN ((j.actual_revenue - j.actual_cost) / j.actual_revenue * 100)::DECIMAL(5,2)
        ELSE 0 
    END as gross_margin_pct,
    j.start_date,
    j.actual_completion_date
FROM jobs j
LEFT JOIN customers c ON j.customer_id = c.id;

-- ============================================================
-- DONE!
-- ============================================================
-- Your schema is ready. Next steps:
-- 1. Create a tenant record
-- 2. Run the seed data (chart of accounts) with your tenant_id
-- 3. Set up Supabase Auth and link users to tenants
-- ============================================================
