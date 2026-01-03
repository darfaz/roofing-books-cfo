-- Friday Payday Tables Migration
-- Creates fp_* tables for collections automation
-- Migration: 006_friday_payday_tables.sql

-- ============================================================================
-- ENUM TYPES
-- ============================================================================

CREATE TYPE fp_invoice_status AS ENUM (
    'draft', 'sent', 'partial', 'paid', 'overdue', 'disputed', 'written_off'
);

CREATE TYPE fp_payer_type AS ENUM (
    'homeowner_direct',
    'insurance_pending',
    'supplement_pending',
    'depreciation_recovery',
    'gc_commercial',
    'retainage'
);

CREATE TYPE fp_sequence_status AS ENUM (
    'not_started', 'active', 'paused', 'completed', 'manual'
);

CREATE TYPE fp_payment_method AS ENUM (
    'card', 'ach', 'check', 'cash', 'other'
);

CREATE TYPE fp_payment_source AS ENUM (
    'quickbooks', 'payment_portal', 'manual'
);

CREATE TYPE fp_reminder_channel AS ENUM ('email', 'sms', 'call');

CREATE TYPE fp_reminder_status AS ENUM ('scheduled', 'sent', 'delivered', 'failed', 'skipped');

-- ============================================================================
-- TENANT SETTINGS EXTENSION
-- ============================================================================

ALTER TABLE tenants ADD COLUMN IF NOT EXISTS fp_settings JSONB DEFAULT '{
    "enabled": false,
    "quiet_hours_start": "19:00",
    "quiet_hours_end": "08:00",
    "weekly_contact_limit": 2,
    "default_payment_methods": ["card", "ach"],
    "auto_sync_enabled": true,
    "ai_personalization_enabled": true,
    "sending_email": null,
    "sending_phone": null,
    "brand_color": "#1E40AF",
    "logo_url": null,
    "last_sync_at": null
}';

-- ============================================================================
-- TABLE: fp_templates (must be created first for FK references)
-- ============================================================================

CREATE TABLE fp_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    channel fp_reminder_channel NOT NULL,
    tone VARCHAR(50) DEFAULT 'friendly',
    subject VARCHAR(255),
    body TEXT NOT NULL,
    is_system BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_fp_templates_tenant ON fp_templates(tenant_id);
CREATE INDEX idx_fp_templates_channel ON fp_templates(tenant_id, channel);

-- ============================================================================
-- TABLE: fp_sequences
-- ============================================================================

CREATE TABLE fp_sequences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    payer_type fp_payer_type NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_fp_sequences_tenant ON fp_sequences(tenant_id);
CREATE UNIQUE INDEX idx_fp_sequences_default ON fp_sequences(tenant_id, payer_type)
    WHERE is_default = TRUE;

-- ============================================================================
-- TABLE: fp_sequence_steps
-- ============================================================================

CREATE TABLE fp_sequence_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sequence_id UUID NOT NULL REFERENCES fp_sequences(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    days_from_due INTEGER NOT NULL,
    channel fp_reminder_channel NOT NULL,
    template_id UUID REFERENCES fp_templates(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(sequence_id, step_order)
);

CREATE INDEX idx_fp_sequence_steps_sequence ON fp_sequence_steps(sequence_id);

-- ============================================================================
-- TABLE: fp_customers
-- ============================================================================

CREATE TABLE fp_customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    qbo_id VARCHAR(255),
    display_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    mobile VARCHAR(50),
    billing_address JSONB,
    customer_type VARCHAR(50) DEFAULT 'homeowner',
    tags TEXT[] DEFAULT '{}',
    notes TEXT,
    total_outstanding DECIMAL(12,2) DEFAULT 0,
    lifetime_value DECIMAL(12,2) DEFAULT 0,
    avg_payment_days INTEGER,
    communication_preferences JSONB DEFAULT '{"email": true, "sms": true}',
    is_suppressed BOOLEAN DEFAULT FALSE,
    suppressed_reason TEXT,
    suppressed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, qbo_id)
);

CREATE INDEX idx_fp_customers_tenant ON fp_customers(tenant_id);
CREATE INDEX idx_fp_customers_qbo_id ON fp_customers(tenant_id, qbo_id);
CREATE INDEX idx_fp_customers_type ON fp_customers(tenant_id, customer_type);

-- ============================================================================
-- TABLE: fp_invoices
-- ============================================================================

CREATE TABLE fp_invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES fp_customers(id) ON DELETE CASCADE,
    transaction_id UUID REFERENCES transactions(id),
    qbo_id VARCHAR(255),
    invoice_number VARCHAR(100),
    amount DECIMAL(12,2) NOT NULL,
    balance DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    status fp_invoice_status DEFAULT 'sent',

    -- Classification
    payer_type fp_payer_type DEFAULT 'homeowner_direct',
    payer_type_override BOOLEAN DEFAULT FALSE,
    classification_confidence DECIMAL(3,2),

    -- Sequence tracking
    sequence_id UUID REFERENCES fp_sequences(id),
    sequence_status fp_sequence_status DEFAULT 'not_started',
    sequence_current_step INTEGER DEFAULT 0,
    sequence_next_action_at TIMESTAMPTZ,
    sequence_paused_reason TEXT,

    -- Insurance claim info
    insurance_claim_number VARCHAR(100),
    insurance_adjuster_name VARCHAR(255),
    insurance_adjuster_email VARCHAR(255),
    insurance_adjuster_phone VARCHAR(50),

    -- Job info
    job_name VARCHAR(255),
    job_address TEXT,
    job_id_external VARCHAR(255),

    -- Payment portal
    payment_link VARCHAR(500),
    payment_token VARCHAR(100),
    payment_token_expires_at TIMESTAMPTZ,

    -- Metadata
    description TEXT,
    line_items JSONB,
    qbo_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, qbo_id)
);

CREATE INDEX idx_fp_invoices_tenant ON fp_invoices(tenant_id);
CREATE INDEX idx_fp_invoices_customer ON fp_invoices(customer_id);
CREATE INDEX idx_fp_invoices_status ON fp_invoices(tenant_id, status);
CREATE INDEX idx_fp_invoices_payer_type ON fp_invoices(tenant_id, payer_type);
CREATE INDEX idx_fp_invoices_due_date ON fp_invoices(tenant_id, due_date);
CREATE INDEX idx_fp_invoices_balance ON fp_invoices(tenant_id, balance) WHERE balance > 0;
CREATE INDEX idx_fp_invoices_next_action ON fp_invoices(tenant_id, sequence_next_action_at)
    WHERE sequence_status = 'active';
CREATE INDEX idx_fp_invoices_aging ON fp_invoices(tenant_id, due_date, balance)
    WHERE balance > 0 AND status NOT IN ('paid', 'written_off');
CREATE INDEX idx_fp_invoices_payment_token ON fp_invoices(payment_token) WHERE payment_token IS NOT NULL;

-- ============================================================================
-- TABLE: fp_payments
-- ============================================================================

CREATE TABLE fp_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    invoice_id UUID NOT NULL REFERENCES fp_invoices(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES fp_customers(id) ON DELETE CASCADE,
    qbo_id VARCHAR(255),
    amount DECIMAL(12,2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_method fp_payment_method DEFAULT 'other',
    source fp_payment_source DEFAULT 'quickbooks',
    stripe_payment_id VARCHAR(255),
    reference_number VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, qbo_id)
);

CREATE INDEX idx_fp_payments_tenant ON fp_payments(tenant_id);
CREATE INDEX idx_fp_payments_invoice ON fp_payments(invoice_id);
CREATE INDEX idx_fp_payments_date ON fp_payments(tenant_id, payment_date);

-- ============================================================================
-- TABLE: fp_reminders
-- ============================================================================

CREATE TABLE fp_reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    invoice_id UUID NOT NULL REFERENCES fp_invoices(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES fp_customers(id) ON DELETE CASCADE,
    sequence_step_id UUID REFERENCES fp_sequence_steps(id),

    channel fp_reminder_channel NOT NULL,
    status fp_reminder_status DEFAULT 'scheduled',
    scheduled_for TIMESTAMPTZ NOT NULL,
    sent_at TIMESTAMPTZ,

    template_id UUID REFERENCES fp_templates(id),
    subject VARCHAR(255),
    body TEXT,
    personalized_body TEXT,

    external_id VARCHAR(255),
    delivery_status VARCHAR(50),
    opened_at TIMESTAMPTZ,
    clicked_at TIMESTAMPTZ,

    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_fp_reminders_tenant ON fp_reminders(tenant_id);
CREATE INDEX idx_fp_reminders_invoice ON fp_reminders(invoice_id);
CREATE INDEX idx_fp_reminders_scheduled ON fp_reminders(tenant_id, scheduled_for)
    WHERE status = 'scheduled';
CREATE INDEX idx_fp_reminders_status ON fp_reminders(tenant_id, status);

-- ============================================================================
-- TABLE: fp_communication_log
-- ============================================================================

CREATE TABLE fp_communication_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES fp_invoices(id) ON DELETE SET NULL,
    customer_id UUID REFERENCES fp_customers(id) ON DELETE SET NULL,
    reminder_id UUID REFERENCES fp_reminders(id) ON DELETE SET NULL,

    direction VARCHAR(10) NOT NULL, -- 'inbound' or 'outbound'
    channel fp_reminder_channel NOT NULL,

    -- Email fields
    from_address VARCHAR(255),
    to_address VARCHAR(255),
    subject VARCHAR(255),
    body TEXT,

    -- SMS/Phone fields
    from_phone VARCHAR(50),
    to_phone VARCHAR(50),
    message TEXT,

    status VARCHAR(50) NOT NULL,
    external_id VARCHAR(255),

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_fp_comm_log_tenant ON fp_communication_log(tenant_id);
CREATE INDEX idx_fp_comm_log_invoice ON fp_communication_log(invoice_id);
CREATE INDEX idx_fp_comm_log_customer ON fp_communication_log(customer_id);
CREATE INDEX idx_fp_comm_log_created ON fp_communication_log(tenant_id, created_at);

-- ============================================================================
-- TABLE: fp_daily_metrics
-- ============================================================================

CREATE TABLE fp_daily_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,

    -- AR Aging amounts
    bucket_current DECIMAL(12,2) DEFAULT 0,
    bucket_1_30 DECIMAL(12,2) DEFAULT 0,
    bucket_31_60 DECIMAL(12,2) DEFAULT 0,
    bucket_61_90 DECIMAL(12,2) DEFAULT 0,
    bucket_90_plus DECIMAL(12,2) DEFAULT 0,
    total_ar DECIMAL(12,2) DEFAULT 0,

    -- Invoice counts
    invoices_current INTEGER DEFAULT 0,
    invoices_1_30 INTEGER DEFAULT 0,
    invoices_31_60 INTEGER DEFAULT 0,
    invoices_61_90 INTEGER DEFAULT 0,
    invoices_90_plus INTEGER DEFAULT 0,
    total_invoices INTEGER DEFAULT 0,

    -- Collections
    amount_collected DECIMAL(12,2) DEFAULT 0,
    invoices_paid INTEGER DEFAULT 0,

    -- Communications
    reminders_sent INTEGER DEFAULT 0,
    reminders_opened INTEGER DEFAULT 0,
    reminders_clicked INTEGER DEFAULT 0,

    -- DSO
    dso DECIMAL(6,2),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, metric_date)
);

CREATE INDEX idx_fp_daily_metrics_tenant_date ON fp_daily_metrics(tenant_id, metric_date);

-- ============================================================================
-- ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE fp_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE fp_sequences ENABLE ROW LEVEL SECURITY;
ALTER TABLE fp_sequence_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE fp_customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE fp_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE fp_payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE fp_reminders ENABLE ROW LEVEL SECURITY;
ALTER TABLE fp_communication_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE fp_daily_metrics ENABLE ROW LEVEL SECURITY;

-- RLS Policies for authenticated users (using tenant_id from JWT)
CREATE POLICY "fp_templates_tenant_isolation" ON fp_templates FOR ALL
    USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY "fp_sequences_tenant_isolation" ON fp_sequences FOR ALL
    USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY "fp_sequence_steps_tenant_isolation" ON fp_sequence_steps FOR ALL
    USING (sequence_id IN (SELECT id FROM fp_sequences WHERE tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid));

CREATE POLICY "fp_customers_tenant_isolation" ON fp_customers FOR ALL
    USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY "fp_invoices_tenant_isolation" ON fp_invoices FOR ALL
    USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY "fp_payments_tenant_isolation" ON fp_payments FOR ALL
    USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY "fp_reminders_tenant_isolation" ON fp_reminders FOR ALL
    USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY "fp_communication_log_tenant_isolation" ON fp_communication_log FOR ALL
    USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

CREATE POLICY "fp_daily_metrics_tenant_isolation" ON fp_daily_metrics FOR ALL
    USING (tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid);

-- Service role bypass for backend operations
CREATE POLICY "fp_templates_service_role" ON fp_templates FOR ALL TO service_role USING (true);
CREATE POLICY "fp_sequences_service_role" ON fp_sequences FOR ALL TO service_role USING (true);
CREATE POLICY "fp_sequence_steps_service_role" ON fp_sequence_steps FOR ALL TO service_role USING (true);
CREATE POLICY "fp_customers_service_role" ON fp_customers FOR ALL TO service_role USING (true);
CREATE POLICY "fp_invoices_service_role" ON fp_invoices FOR ALL TO service_role USING (true);
CREATE POLICY "fp_payments_service_role" ON fp_payments FOR ALL TO service_role USING (true);
CREATE POLICY "fp_reminders_service_role" ON fp_reminders FOR ALL TO service_role USING (true);
CREATE POLICY "fp_communication_log_service_role" ON fp_communication_log FOR ALL TO service_role USING (true);
CREATE POLICY "fp_daily_metrics_service_role" ON fp_daily_metrics FOR ALL TO service_role USING (true);

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to calculate days overdue
CREATE OR REPLACE FUNCTION fp_days_overdue(due_date DATE)
RETURNS INTEGER AS $$
BEGIN
    RETURN GREATEST(0, CURRENT_DATE - due_date);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to get AR aging bucket
CREATE OR REPLACE FUNCTION fp_aging_bucket(due_date DATE)
RETURNS TEXT AS $$
DECLARE
    days INTEGER;
BEGIN
    days := fp_days_overdue(due_date);
    IF days <= 0 THEN RETURN 'current';
    ELSIF days <= 30 THEN RETURN '1-30';
    ELSIF days <= 60 THEN RETURN '31-60';
    ELSIF days <= 90 THEN RETURN '61-90';
    ELSE RETURN '90+';
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to update customer outstanding balance
CREATE OR REPLACE FUNCTION fp_update_customer_outstanding()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE fp_customers
    SET total_outstanding = (
        SELECT COALESCE(SUM(balance), 0)
        FROM fp_invoices
        WHERE customer_id = COALESCE(NEW.customer_id, OLD.customer_id)
        AND status NOT IN ('paid', 'written_off')
    ),
    updated_at = NOW()
    WHERE id = COALESCE(NEW.customer_id, OLD.customer_id);

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_fp_invoices_update_customer_outstanding
    AFTER INSERT OR UPDATE OF balance, status OR DELETE ON fp_invoices
    FOR EACH ROW EXECUTE FUNCTION fp_update_customer_outstanding();

-- Function to auto-update updated_at
CREATE OR REPLACE FUNCTION fp_update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_fp_templates_updated_at BEFORE UPDATE ON fp_templates
    FOR EACH ROW EXECUTE FUNCTION fp_update_updated_at();

CREATE TRIGGER tr_fp_sequences_updated_at BEFORE UPDATE ON fp_sequences
    FOR EACH ROW EXECUTE FUNCTION fp_update_updated_at();

CREATE TRIGGER tr_fp_customers_updated_at BEFORE UPDATE ON fp_customers
    FOR EACH ROW EXECUTE FUNCTION fp_update_updated_at();

CREATE TRIGGER tr_fp_invoices_updated_at BEFORE UPDATE ON fp_invoices
    FOR EACH ROW EXECUTE FUNCTION fp_update_updated_at();

CREATE TRIGGER tr_fp_reminders_updated_at BEFORE UPDATE ON fp_reminders
    FOR EACH ROW EXECUTE FUNCTION fp_update_updated_at();

-- ============================================================================
-- SEED DATA: Default Templates
-- ============================================================================

-- System-wide default templates (tenant_id will be set per-tenant on copy)
-- Note: These are inserted with a placeholder and should be copied to each tenant

-- We'll create a function to seed default data for a tenant
CREATE OR REPLACE FUNCTION fp_seed_tenant_defaults(p_tenant_id UUID)
RETURNS VOID AS $$
DECLARE
    v_homeowner_seq_id UUID;
    v_insurance_seq_id UUID;
    v_supplement_seq_id UUID;
    v_depreciation_seq_id UUID;
    v_gc_seq_id UUID;
    v_upcoming_template_id UUID;
    v_due_today_template_id UUID;
    v_first_reminder_template_id UUID;
    v_second_reminder_template_id UUID;
    v_escalation_template_id UUID;
    v_final_notice_template_id UUID;
    v_insurance_status_template_id UUID;
    v_insurance_reminder_template_id UUID;
    v_sms_reminder_template_id UUID;
BEGIN
    -- Skip if already seeded
    IF EXISTS (SELECT 1 FROM fp_sequences WHERE tenant_id = p_tenant_id) THEN
        RETURN;
    END IF;

    -- Create Email Templates
    INSERT INTO fp_templates (id, tenant_id, name, channel, tone, subject, body, is_system)
    VALUES
    (gen_random_uuid(), p_tenant_id, 'Upcoming Due Reminder', 'email', 'friendly',
     'Your invoice from {{company_name}} is due soon',
     E'Hi {{customer_name}},\n\nThis is a friendly reminder that invoice #{{invoice_number}} for {{amount}} is due on {{due_date}}.\n\nFor your convenience, you can pay online here: {{payment_link}}\n\nJob: {{job_address}}\n\nThank you for choosing {{company_name}}!\n\nQuestions? Call us at {{company_phone}}',
     TRUE)
    RETURNING id INTO v_upcoming_template_id;

    INSERT INTO fp_templates (id, tenant_id, name, channel, tone, subject, body, is_system)
    VALUES
    (gen_random_uuid(), p_tenant_id, 'Due Today Reminder', 'email', 'friendly',
     'Payment due today - Invoice #{{invoice_number}}',
     E'Hi {{customer_name}},\n\nJust a quick reminder that your invoice #{{invoice_number}} for {{amount}} is due today.\n\nPay now: {{payment_link}}\n\nThank you!\n{{company_name}}\n{{company_phone}}',
     TRUE)
    RETURNING id INTO v_due_today_template_id;

    INSERT INTO fp_templates (id, tenant_id, name, channel, tone, subject, body, is_system)
    VALUES
    (gen_random_uuid(), p_tenant_id, 'First Payment Reminder', 'email', 'professional',
     'Payment reminder - {{amount}} past due',
     E'Hi {{customer_name}},\n\nWe wanted to follow up on invoice #{{invoice_number}} for {{amount}}, which is now {{days_overdue}} days past the due date of {{due_date}}.\n\nYou can pay securely online: {{payment_link}}\n\nIf you''ve already sent payment, please disregard this message. If you have any questions about your invoice for the work at {{job_address}}, please give us a call.\n\nThank you,\n{{company_name}}\n{{company_phone}}',
     TRUE)
    RETURNING id INTO v_first_reminder_template_id;

    INSERT INTO fp_templates (id, tenant_id, name, channel, tone, subject, body, is_system)
    VALUES
    (gen_random_uuid(), p_tenant_id, 'Second Payment Reminder', 'email', 'professional',
     'Important: Invoice #{{invoice_number}} - {{days_overdue}} days overdue',
     E'Hi {{customer_name}},\n\nThis is a follow-up regarding invoice #{{invoice_number}} for {{balance}}, which is now {{days_overdue}} days past due.\n\nWe understand things get busy, and we''re here to help if you need to discuss payment options.\n\nPay online now: {{payment_link}}\n\nPlease contact us at {{company_phone}} if you have any questions.\n\nThank you,\n{{company_name}}',
     TRUE)
    RETURNING id INTO v_second_reminder_template_id;

    INSERT INTO fp_templates (id, tenant_id, name, channel, tone, subject, body, is_system)
    VALUES
    (gen_random_uuid(), p_tenant_id, 'Escalation Warning', 'email', 'firm',
     'Action Required: Invoice #{{invoice_number}} - 30 days overdue',
     E'Dear {{customer_name}},\n\nYour invoice #{{invoice_number}} for {{balance}} is now 30 days past due.\n\nTo avoid any further action, please remit payment immediately: {{payment_link}}\n\nIf there are circumstances preventing payment, please contact us at {{company_phone}} to discuss options.\n\nRegards,\n{{company_name}}',
     TRUE)
    RETURNING id INTO v_escalation_template_id;

    INSERT INTO fp_templates (id, tenant_id, name, channel, tone, subject, body, is_system)
    VALUES
    (gen_random_uuid(), p_tenant_id, 'Final Notice', 'email', 'formal',
     'Final Notice: Invoice #{{invoice_number}} - Immediate Payment Required',
     E'Dear {{customer_name}},\n\nThis is a final notice regarding invoice #{{invoice_number}} for {{balance}}, which is now {{days_overdue}} days past due.\n\nImmediate payment is required to avoid further collection activity.\n\nPay now: {{payment_link}}\n\nIf you believe this is in error or need to discuss this matter, please contact us immediately at {{company_phone}}.\n\n{{company_name}}',
     TRUE)
    RETURNING id INTO v_final_notice_template_id;

    INSERT INTO fp_templates (id, tenant_id, name, channel, tone, subject, body, is_system)
    VALUES
    (gen_random_uuid(), p_tenant_id, 'Insurance Status Check', 'email', 'professional',
     'Insurance claim status - Invoice #{{invoice_number}}',
     E'Hi {{customer_name}},\n\nWe''re following up on invoice #{{invoice_number}} related to your insurance claim for the work at {{job_address}}.\n\nCould you provide an update on the status of your claim? If you''ve received your insurance check, please let us know so we can help you process payment.\n\nPay online: {{payment_link}}\n\nQuestions? Call us at {{company_phone}}.\n\nThank you,\n{{company_name}}',
     TRUE)
    RETURNING id INTO v_insurance_status_template_id;

    INSERT INTO fp_templates (id, tenant_id, name, channel, tone, subject, body, is_system)
    VALUES
    (gen_random_uuid(), p_tenant_id, 'Insurance Claim Reminder', 'email', 'professional',
     'Follow-up: Insurance payment for {{job_address}}',
     E'Hi {{customer_name}},\n\nWe wanted to check in about the insurance claim for your roof work at {{job_address}}.\n\nInvoice #{{invoice_number}}: {{balance}}\n\nIf you''ve received your insurance check, we can help coordinate the endorsement process if needed. Many mortgage companies require this, and we''re happy to guide you through it.\n\nPay securely: {{payment_link}}\n\nCall us at {{company_phone}} with any questions.\n\n{{company_name}}',
     TRUE)
    RETURNING id INTO v_insurance_reminder_template_id;

    INSERT INTO fp_templates (id, tenant_id, name, channel, tone, subject, body, is_system)
    VALUES
    (gen_random_uuid(), p_tenant_id, 'SMS Payment Reminder', 'sms', 'friendly',
     NULL,
     E'Hi {{customer_name}}! Your {{company_name}} invoice for {{balance}} is {{days_overdue}} days overdue. Pay now: {{payment_link}}',
     TRUE)
    RETURNING id INTO v_sms_reminder_template_id;

    -- Create Homeowner Sequence
    INSERT INTO fp_sequences (id, tenant_id, name, description, payer_type, is_default)
    VALUES (gen_random_uuid(), p_tenant_id, 'Homeowner Standard',
            'Standard collection sequence for direct homeowner payments', 'homeowner_direct', TRUE)
    RETURNING id INTO v_homeowner_seq_id;

    INSERT INTO fp_sequence_steps (sequence_id, step_order, days_from_due, channel, template_id) VALUES
    (v_homeowner_seq_id, 1, -3, 'email', v_upcoming_template_id),
    (v_homeowner_seq_id, 2, 0, 'email', v_due_today_template_id),
    (v_homeowner_seq_id, 3, 7, 'email', v_first_reminder_template_id),
    (v_homeowner_seq_id, 4, 14, 'email', v_second_reminder_template_id),
    (v_homeowner_seq_id, 5, 14, 'sms', v_sms_reminder_template_id),
    (v_homeowner_seq_id, 6, 30, 'email', v_escalation_template_id),
    (v_homeowner_seq_id, 7, 45, 'email', v_final_notice_template_id),
    (v_homeowner_seq_id, 8, 45, 'sms', v_sms_reminder_template_id);

    -- Create Insurance Pending Sequence
    INSERT INTO fp_sequences (id, tenant_id, name, description, payer_type, is_default)
    VALUES (gen_random_uuid(), p_tenant_id, 'Insurance Claim',
            'Extended timeline for insurance-related payments', 'insurance_pending', TRUE)
    RETURNING id INTO v_insurance_seq_id;

    INSERT INTO fp_sequence_steps (sequence_id, step_order, days_from_due, channel, template_id) VALUES
    (v_insurance_seq_id, 1, 14, 'email', v_insurance_status_template_id),
    (v_insurance_seq_id, 2, 30, 'email', v_insurance_reminder_template_id),
    (v_insurance_seq_id, 3, 30, 'sms', v_sms_reminder_template_id),
    (v_insurance_seq_id, 4, 45, 'email', v_insurance_reminder_template_id),
    (v_insurance_seq_id, 5, 60, 'email', v_escalation_template_id);

    -- Create Supplement Pending Sequence
    INSERT INTO fp_sequences (id, tenant_id, name, description, payer_type, is_default)
    VALUES (gen_random_uuid(), p_tenant_id, 'Supplement Follow-up',
            'Sequence for supplement approval tracking', 'supplement_pending', TRUE)
    RETURNING id INTO v_supplement_seq_id;

    INSERT INTO fp_sequence_steps (sequence_id, step_order, days_from_due, channel, template_id) VALUES
    (v_supplement_seq_id, 1, 21, 'email', v_insurance_status_template_id),
    (v_supplement_seq_id, 2, 35, 'email', v_insurance_reminder_template_id),
    (v_supplement_seq_id, 3, 50, 'email', v_insurance_reminder_template_id),
    (v_supplement_seq_id, 4, 65, 'email', v_escalation_template_id);

    -- Create Depreciation Recovery Sequence
    INSERT INTO fp_sequences (id, tenant_id, name, description, payer_type, is_default)
    VALUES (gen_random_uuid(), p_tenant_id, 'Depreciation Recovery',
            'Sequence for ACV to RCV recovery', 'depreciation_recovery', TRUE)
    RETURNING id INTO v_depreciation_seq_id;

    INSERT INTO fp_sequence_steps (sequence_id, step_order, days_from_due, channel, template_id) VALUES
    (v_depreciation_seq_id, 1, 7, 'email', v_first_reminder_template_id),
    (v_depreciation_seq_id, 2, 21, 'email', v_second_reminder_template_id),
    (v_depreciation_seq_id, 3, 35, 'email', v_escalation_template_id),
    (v_depreciation_seq_id, 4, 35, 'sms', v_sms_reminder_template_id);

    -- Create GC/Commercial Sequence
    INSERT INTO fp_sequences (id, tenant_id, name, description, payer_type, is_default)
    VALUES (gen_random_uuid(), p_tenant_id, 'Commercial 30-45-60',
            'Sequence for GC and commercial accounts', 'gc_commercial', TRUE)
    RETURNING id INTO v_gc_seq_id;

    INSERT INTO fp_sequence_steps (sequence_id, step_order, days_from_due, channel, template_id) VALUES
    (v_gc_seq_id, 1, 30, 'email', v_first_reminder_template_id),
    (v_gc_seq_id, 2, 45, 'email', v_second_reminder_template_id),
    (v_gc_seq_id, 3, 60, 'email', v_escalation_template_id);

END;
$$ LANGUAGE plpgsql;

-- Seed defaults for existing tenants with fp_settings enabled
DO $$
DECLARE
    t_record RECORD;
BEGIN
    FOR t_record IN
        SELECT id FROM tenants
        WHERE fp_settings IS NOT NULL
        AND (fp_settings->>'enabled')::boolean = TRUE
    LOOP
        PERFORM fp_seed_tenant_defaults(t_record.id);
    END LOOP;
END $$;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE fp_customers IS 'Friday Payday customer records synced from QuickBooks';
COMMENT ON TABLE fp_invoices IS 'Friday Payday invoice records with classification and sequence status';
COMMENT ON TABLE fp_payments IS 'Payment records from QuickBooks sync and payment portal';
COMMENT ON TABLE fp_sequences IS 'Dunning sequence definitions by payer type';
COMMENT ON TABLE fp_sequence_steps IS 'Individual steps within a dunning sequence';
COMMENT ON TABLE fp_templates IS 'Email and SMS message templates';
COMMENT ON TABLE fp_reminders IS 'Scheduled and sent reminder records';
COMMENT ON TABLE fp_communication_log IS 'Complete communication history for audit trail';
COMMENT ON TABLE fp_daily_metrics IS 'Pre-computed daily metrics for dashboard performance';

COMMENT ON FUNCTION fp_seed_tenant_defaults IS 'Seeds default sequences and templates for a new Friday Payday tenant';
COMMENT ON FUNCTION fp_days_overdue IS 'Calculates days overdue from due date';
COMMENT ON FUNCTION fp_aging_bucket IS 'Returns AR aging bucket name based on due date';
