# Friday Payday - Data Model

> **Feature**: 09-friday-payday
> **Database**: PostgreSQL (via Supabase)
> **Last Updated**: 2026-01-02

---

## Overview

This document defines the database schema for Friday Payday. The design prioritizes:
1. **Multi-tenancy** - Complete data isolation via existing `tenant_id`
2. **QuickBooks as source of truth** - Extends existing `transactions` table
3. **Audit trail** - Full history of all actions
4. **Performance** - Optimized for dashboard queries

---

## Integration with Existing Schema

Friday Payday builds on existing CrewCFO tables:

| Existing Table | Friday Payday Usage |
|----------------|---------------------|
| `tenants` | Root tenant table, extends with collections settings |
| `tenant_integrations` | Uses existing QBO OAuth tokens |
| `transactions` | Source for invoice data (qbo_type='Invoice') |

---

## Entity Relationship Diagram

```
+------------------+          +-------------------+          +------------------+
|     tenants      |          |    fp_customers   |          |   fp_invoices    |
|------------------|          |-------------------|          |------------------|
| id (PK)          |<---------| tenant_id (FK)    |<---------| tenant_id (FK)   |
| fp_settings      |          | id (PK)           |          | id (PK)          |
|                  |          | qbo_id            |          | customer_id (FK) |
+------------------+          | display_name      |          | qbo_id           |
        |                     | email             |          | amount           |
        |                     | phone             |          | balance          |
        |                     | customer_type     |          | payer_type       |
        |                     | is_suppressed     |          | sequence_id (FK) |
        |                     +-------------------+          +------------------+
        |                              |                            |
        |                              |                     +------+------+
        |                              |                     |             |
        |                     +--------+--------+    +-------+----+ +------+-------+
        |                     |   fp_payments   |    | fp_reminders | | fp_comm_log  |
        |                     |-----------------|    |--------------|  |--------------|
        |                     | id (PK)         |    | id (PK)      |  | id (PK)      |
        |                     | invoice_id (FK) |    | invoice_id   |  | invoice_id   |
        |                     | amount          |    | channel      |  | channel      |
        |                     | payment_date    |    | status       |  | status       |
        |                     | source          |    | scheduled_for|  | content      |
        |                     +-----------------+    +--------------+  +--------------+
        |
        |     +-----------------+     +------------------+     +-----------------+
        +---->|  fp_sequences   |---->| fp_sequence_steps|     |  fp_templates   |
              |-----------------|     |------------------|     |-----------------|
              | id (PK)         |     | id (PK)          |<----| id (PK)         |
              | tenant_id (FK)  |     | sequence_id (FK) |     | tenant_id (FK)  |
              | name            |     | day              |     | name            |
              | payer_type      |     | channel          |     | channel         |
              | is_default      |     | template_id (FK) |     | body            |
              +-----------------+     +------------------+     +-----------------+
```

---

## New Tables

### fp_customers

Customer records synced from QuickBooks with collections enrichments.

```sql
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

-- customer_type options: 'homeowner', 'insurance_company', 'gc', 'commercial'

CREATE INDEX idx_fp_customers_tenant ON fp_customers(tenant_id);
CREATE INDEX idx_fp_customers_qbo_id ON fp_customers(tenant_id, qbo_id);
CREATE INDEX idx_fp_customers_type ON fp_customers(tenant_id, customer_type);
```

### fp_invoices

Invoice records with classification and sequence status.

```sql
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
```

### fp_payments

Payment records (synced from QuickBooks and payment portal).

```sql
CREATE TYPE fp_payment_method AS ENUM (
    'card', 'ach', 'check', 'cash', 'other'
);

CREATE TYPE fp_payment_source AS ENUM (
    'quickbooks', 'payment_portal', 'manual'
);

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
```

### fp_sequences

Dunning sequence definitions.

```sql
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
```

### fp_sequence_steps

Individual steps within a sequence.

```sql
CREATE TYPE fp_reminder_channel AS ENUM ('email', 'sms', 'call');

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
```

### fp_templates

Email and SMS message templates.

```sql
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

-- Template variables:
-- {{customer_name}}, {{invoice_number}}, {{amount}}, {{balance}},
-- {{due_date}}, {{days_overdue}}, {{job_address}}, {{payment_link}},
-- {{company_name}}, {{company_phone}}

CREATE INDEX idx_fp_templates_tenant ON fp_templates(tenant_id);
CREATE INDEX idx_fp_templates_channel ON fp_templates(tenant_id, channel);
```

### fp_reminders

Scheduled and sent reminder records.

```sql
CREATE TYPE fp_reminder_status AS ENUM ('scheduled', 'sent', 'delivered', 'failed', 'skipped');

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
```

### fp_communication_log

Complete communication history for audit trail.

```sql
CREATE TABLE fp_communication_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES fp_invoices(id) ON DELETE SET NULL,
    customer_id UUID REFERENCES fp_customers(id) ON DELETE SET NULL,
    reminder_id UUID REFERENCES fp_reminders(id) ON DELETE SET NULL,

    direction VARCHAR(10) NOT NULL,
    channel fp_reminder_channel NOT NULL,

    from_address VARCHAR(255),
    to_address VARCHAR(255),
    subject VARCHAR(255),
    body TEXT,

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
```

### fp_daily_metrics

Pre-computed daily metrics for dashboard performance.

```sql
CREATE TABLE fp_daily_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,

    -- AR Aging
    bucket_current DECIMAL(12,2) DEFAULT 0,
    bucket_1_30 DECIMAL(12,2) DEFAULT 0,
    bucket_31_60 DECIMAL(12,2) DEFAULT 0,
    bucket_61_90 DECIMAL(12,2) DEFAULT 0,
    bucket_90_plus DECIMAL(12,2) DEFAULT 0,
    total_ar DECIMAL(12,2) DEFAULT 0,

    -- Counts
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
```

---

## Tenant Settings Extension

Add Friday Payday settings to existing tenants table:

```sql
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
    "logo_url": null
}';
```

---

## Row-Level Security Policies

All tables use tenant_id for RLS:

```sql
-- Enable RLS on all Friday Payday tables
ALTER TABLE fp_customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE fp_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE fp_payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE fp_sequences ENABLE ROW LEVEL SECURITY;
ALTER TABLE fp_sequence_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE fp_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE fp_reminders ENABLE ROW LEVEL SECURITY;
ALTER TABLE fp_communication_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE fp_daily_metrics ENABLE ROW LEVEL SECURITY;

-- Example policy (similar for all tables)
CREATE POLICY "fp_invoices_tenant_isolation"
    ON fp_invoices FOR ALL
    USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);
```

---

## Seed Data: Default Sequences

```sql
-- Default Homeowner Sequence
INSERT INTO fp_sequences (tenant_id, name, payer_type, is_default) VALUES
('[TENANT_ID]', 'Homeowner Standard', 'homeowner_direct', TRUE);

INSERT INTO fp_sequence_steps (sequence_id, step_order, days_from_due, channel) VALUES
('[SEQUENCE_ID]', 1, -3, 'email'),
('[SEQUENCE_ID]', 2, 0, 'email'),
('[SEQUENCE_ID]', 3, 0, 'sms'),
('[SEQUENCE_ID]', 4, 7, 'email'),
('[SEQUENCE_ID]', 5, 14, 'email'),
('[SEQUENCE_ID]', 6, 14, 'sms'),
('[SEQUENCE_ID]', 7, 30, 'email'),
('[SEQUENCE_ID]', 8, 45, 'email'),
('[SEQUENCE_ID]', 9, 45, 'sms');

-- Default Insurance Sequence
INSERT INTO fp_sequences (tenant_id, name, payer_type, is_default) VALUES
('[TENANT_ID]', 'Insurance Claim', 'insurance_pending', TRUE);

INSERT INTO fp_sequence_steps (sequence_id, step_order, days_from_due, channel) VALUES
('[SEQUENCE_ID]', 1, 14, 'email'),
('[SEQUENCE_ID]', 2, 30, 'email'),
('[SEQUENCE_ID]', 3, 30, 'sms'),
('[SEQUENCE_ID]', 4, 45, 'email'),
('[SEQUENCE_ID]', 5, 60, 'email');
```

---

## Migration Strategy

1. Create enum types first
2. Create tables in dependency order
3. Add RLS policies
4. Seed default sequences and templates
5. Create migration for existing tenants' fp_settings

---

*Data model version 1.0 - January 2026*
