# Data Model: Jobs & Job Costs

> **Module**: Books OS  
> **Version**: 1.0.0  

---

## Overview

The jobs data model tracks roofing projects from field service systems and links them to financial transactions for job-level profitability analysis. This is the foundation of job costing—the critical differentiator for construction bookkeeping.

---

## Table: `jobs`

Master record for each roofing project.

```sql
CREATE TABLE jobs (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Multi-tenant
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- External References
    source_system VARCHAR(50) NOT NULL,   -- jobber, servicetitan, manual
    source_job_id VARCHAR(100),           -- External system ID
    qbo_customer_id VARCHAR(50),          -- QBO customer/sub-customer
    
    -- Job Identification
    job_number VARCHAR(50) NOT NULL,      -- Internal job number
    name VARCHAR(255) NOT NULL,           -- Job name/description
    
    -- Customer
    customer_id UUID REFERENCES customers(id),
    customer_name VARCHAR(255),           -- Denormalized for display
    
    -- Location
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    
    -- Job Classification
    job_type VARCHAR(50) NOT NULL,        -- residential_repair, residential_replacement, commercial, storm_insurance
    job_category VARCHAR(50),             -- shingle, metal, flat, tile
    lead_source VARCHAR(100),             -- How they found us
    
    -- Dates
    created_date DATE,
    scheduled_date DATE,
    started_date DATE,
    completed_date DATE,
    invoiced_date DATE,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', 
    
    -- Scope Details (Roofing-Specific)
    roof_squares DECIMAL(10,2),           -- 1 square = 100 sq ft
    roof_pitch VARCHAR(20),               -- e.g., "6/12", "steep"
    stories INTEGER DEFAULT 1,
    tear_off_layers INTEGER DEFAULT 0,
    
    -- Financials - Estimates
    estimated_revenue_cents BIGINT,
    estimated_labor_cents BIGINT,
    estimated_materials_cents BIGINT,
    estimated_other_cents BIGINT,
    estimated_margin_percent DECIMAL(5,2),
    
    -- Financials - Actuals (calculated from job_costs)
    actual_revenue_cents BIGINT DEFAULT 0,
    actual_labor_cents BIGINT DEFAULT 0,
    actual_materials_cents BIGINT DEFAULT 0,
    actual_equipment_cents BIGINT DEFAULT 0,
    actual_subcontractor_cents BIGINT DEFAULT 0,
    actual_overhead_cents BIGINT DEFAULT 0,
    actual_margin_percent DECIMAL(5,2),
    
    -- Crew Assignment
    assigned_crew_id UUID REFERENCES crews(id),
    assigned_crew_name VARCHAR(100),
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    last_synced_at TIMESTAMPTZ,
    
    -- Constraints
    CONSTRAINT unique_tenant_job_number UNIQUE (tenant_id, job_number),
    CONSTRAINT valid_source CHECK (source_system IN ('jobber', 'servicetitan', 'housecall', 'manual')),
    CONSTRAINT valid_job_type CHECK (job_type IN (
        'residential_repair', 'residential_replacement', 
        'commercial_repair', 'commercial_new',
        'storm_insurance', 'gutters_siding', 'other'
    )),
    CONSTRAINT valid_status CHECK (status IN (
        'pending', 'scheduled', 'in_progress', 'completed', 
        'invoiced', 'paid', 'cancelled', 'on_hold'
    ))
);

-- Indexes
CREATE INDEX idx_jobs_tenant ON jobs(tenant_id);
CREATE INDEX idx_jobs_source ON jobs(tenant_id, source_system, source_job_id);
CREATE INDEX idx_jobs_customer ON jobs(tenant_id, customer_id);
CREATE INDEX idx_jobs_status ON jobs(tenant_id, status);
CREATE INDEX idx_jobs_type ON jobs(tenant_id, job_type);
CREATE INDEX idx_jobs_completed ON jobs(tenant_id, completed_date);
CREATE INDEX idx_jobs_crew ON jobs(tenant_id, assigned_crew_id);

-- RLS
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON jobs
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

---

## Table: `job_costs`

Individual cost line items linked to jobs.

```sql
CREATE TABLE job_costs (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Multi-tenant
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Job Reference
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    
    -- Transaction Reference (if from categorized transaction)
    categorized_transaction_id UUID REFERENCES transactions_categorized(id),
    
    -- Cost Details
    cost_date DATE NOT NULL,
    cost_type VARCHAR(50) NOT NULL,       -- labor, materials, equipment, subcontractor, overhead
    cost_code_id UUID REFERENCES cost_codes(id),
    
    -- Description
    description TEXT,
    vendor_id UUID REFERENCES vendors(id),
    vendor_name VARCHAR(255),
    
    -- Amounts
    quantity DECIMAL(10,2),
    unit VARCHAR(20),                     -- hour, sqft, square, each
    unit_cost_cents BIGINT,
    amount_cents BIGINT NOT NULL,
    
    -- Labor-Specific
    labor_hours DECIMAL(10,2),
    labor_rate_cents BIGINT,
    burden_rate_percent DECIMAL(5,2) DEFAULT 20.00, -- Taxes, WC, benefits
    
    -- Source
    source VARCHAR(50) DEFAULT 'transaction', -- transaction, timesheet, manual, estimate
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT valid_cost_type CHECK (cost_type IN ('labor', 'materials', 'equipment', 'subcontractor', 'overhead')),
    CONSTRAINT valid_source CHECK (source IN ('transaction', 'timesheet', 'manual', 'estimate'))
);

-- Indexes
CREATE INDEX idx_job_costs_tenant ON job_costs(tenant_id);
CREATE INDEX idx_job_costs_job ON job_costs(job_id);
CREATE INDEX idx_job_costs_type ON job_costs(job_id, cost_type);
CREATE INDEX idx_job_costs_date ON job_costs(tenant_id, cost_date);
CREATE INDEX idx_job_costs_vendor ON job_costs(tenant_id, vendor_id);
CREATE INDEX idx_job_costs_transaction ON job_costs(categorized_transaction_id);

-- RLS
ALTER TABLE job_costs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON job_costs
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

---

## Table: `job_revenue`

Revenue line items linked to jobs (from invoices).

```sql
CREATE TABLE job_revenue (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Multi-tenant
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Job Reference
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    
    -- Invoice Reference
    invoice_id UUID REFERENCES invoices(id),
    qbo_invoice_id VARCHAR(50),
    
    -- Revenue Details
    revenue_date DATE NOT NULL,
    description TEXT,
    
    -- Amounts
    quantity DECIMAL(10,2),
    unit_price_cents BIGINT,
    amount_cents BIGINT NOT NULL,
    
    -- Payment Status
    paid_amount_cents BIGINT DEFAULT 0,
    payment_date DATE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX idx_job_revenue_job ON job_revenue(job_id);
CREATE INDEX idx_job_revenue_invoice ON job_revenue(invoice_id);

-- RLS
ALTER TABLE job_revenue ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON job_revenue
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

---

## Table: `crews`

Crew definitions for assignment and productivity tracking.

```sql
CREATE TABLE crews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    name VARCHAR(100) NOT NULL,
    lead_name VARCHAR(255),
    lead_phone VARCHAR(20),
    
    -- Crew Size
    typical_size INTEGER DEFAULT 3,
    
    -- Performance Metrics (calculated)
    avg_squares_per_day DECIMAL(10,2),
    avg_margin_percent DECIMAL(5,2),
    jobs_completed INTEGER DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    
    CONSTRAINT unique_tenant_crew UNIQUE (tenant_id, name)
);

-- RLS
ALTER TABLE crews ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON crews
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

---

## Job Costing Calculation Logic

### Margin Calculation

```sql
-- Function to recalculate job financials
CREATE OR REPLACE FUNCTION recalculate_job_financials(p_job_id UUID)
RETURNS void AS $$
DECLARE
    v_tenant_id UUID;
    v_revenue BIGINT;
    v_labor BIGINT;
    v_materials BIGINT;
    v_equipment BIGINT;
    v_subcontractor BIGINT;
    v_overhead BIGINT;
    v_total_cost BIGINT;
    v_margin_percent DECIMAL(5,2);
BEGIN
    -- Get tenant_id
    SELECT tenant_id INTO v_tenant_id FROM jobs WHERE id = p_job_id;
    
    -- Calculate revenue
    SELECT COALESCE(SUM(amount_cents), 0) INTO v_revenue
    FROM job_revenue WHERE job_id = p_job_id;
    
    -- Calculate costs by type
    SELECT 
        COALESCE(SUM(CASE WHEN cost_type = 'labor' THEN amount_cents ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN cost_type = 'materials' THEN amount_cents ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN cost_type = 'equipment' THEN amount_cents ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN cost_type = 'subcontractor' THEN amount_cents ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN cost_type = 'overhead' THEN amount_cents ELSE 0 END), 0)
    INTO v_labor, v_materials, v_equipment, v_subcontractor, v_overhead
    FROM job_costs WHERE job_id = p_job_id;
    
    -- Add labor burden to labor costs
    v_labor := v_labor * 1.20; -- 20% burden
    
    -- Calculate total and margin
    v_total_cost := v_labor + v_materials + v_equipment + v_subcontractor + v_overhead;
    
    IF v_revenue > 0 THEN
        v_margin_percent := ((v_revenue - v_total_cost)::DECIMAL / v_revenue) * 100;
    ELSE
        v_margin_percent := 0;
    END IF;
    
    -- Update job record
    UPDATE jobs SET
        actual_revenue_cents = v_revenue,
        actual_labor_cents = v_labor,
        actual_materials_cents = v_materials,
        actual_equipment_cents = v_equipment,
        actual_subcontractor_cents = v_subcontractor,
        actual_overhead_cents = v_overhead,
        actual_margin_percent = v_margin_percent,
        updated_at = now()
    WHERE id = p_job_id;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-recalculate on cost/revenue change
CREATE OR REPLACE FUNCTION trigger_job_recalc()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        PERFORM recalculate_job_financials(OLD.job_id);
        RETURN OLD;
    ELSE
        PERFORM recalculate_job_financials(NEW.job_id);
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER job_costs_recalc
    AFTER INSERT OR UPDATE OR DELETE ON job_costs
    FOR EACH ROW
    EXECUTE FUNCTION trigger_job_recalc();

CREATE TRIGGER job_revenue_recalc
    AFTER INSERT OR UPDATE OR DELETE ON job_revenue
    FOR EACH ROW
    EXECUTE FUNCTION trigger_job_recalc();
```

---

## Job Type Profitability Analysis View

```sql
CREATE OR REPLACE VIEW job_type_profitability AS
SELECT 
    tenant_id,
    job_type,
    COUNT(*) as job_count,
    AVG(actual_revenue_cents) / 100.0 as avg_revenue,
    AVG(actual_labor_cents + actual_materials_cents + actual_equipment_cents + 
        actual_subcontractor_cents + actual_overhead_cents) / 100.0 as avg_cost,
    AVG(actual_margin_percent) as avg_margin_percent,
    SUM(actual_revenue_cents) / 100.0 as total_revenue,
    SUM(actual_revenue_cents - actual_labor_cents - actual_materials_cents - 
        actual_equipment_cents - actual_subcontractor_cents - actual_overhead_cents) / 100.0 as total_profit
FROM jobs
WHERE status IN ('completed', 'invoiced', 'paid')
  AND actual_revenue_cents > 0
GROUP BY tenant_id, job_type;
```

---

## Relationships Diagram

```
┌─────────────┐
│   tenants   │
└──────┬──────┘
       │
       │ 1:n
       ▼
┌─────────────┐       ┌─────────────┐
│    jobs     │───────│   crews     │
└──────┬──────┘       └─────────────┘
       │
       │ 1:n
       ├─────────────────┬─────────────────┐
       ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ job_costs   │   │ job_revenue │   │ transactions│
└──────┬──────┘   └──────┬──────┘   │_categorized │
       │                 │          └─────────────┘
       │                 │
       ▼                 ▼
┌─────────────┐   ┌─────────────┐
│ cost_codes  │   │  invoices   │
└─────────────┘   └─────────────┘
```

---

## Data Sources & Sync

| Table | Source | Sync Frequency | Method |
|-------|--------|----------------|--------|
| jobs | Jobber/ServiceTitan | Every 30 min | Polling |
| jobs | QBO (Customer jobs) | Hourly | Polling |
| job_costs | transactions_categorized | On categorization | Event-driven |
| job_costs | Timesheet import | Manual | Batch import |
| job_revenue | Invoices | On invoice sync | Event-driven |
| crews | Manual entry | As needed | Manual |

---

## Key Queries

### Job Profitability Report

```sql
SELECT 
    j.job_number,
    j.name,
    j.customer_name,
    j.job_type,
    j.completed_date,
    j.actual_revenue_cents / 100.0 as revenue,
    j.actual_labor_cents / 100.0 as labor,
    j.actual_materials_cents / 100.0 as materials,
    (j.actual_labor_cents + j.actual_materials_cents + j.actual_equipment_cents + 
     j.actual_subcontractor_cents + j.actual_overhead_cents) / 100.0 as total_cost,
    j.actual_margin_percent,
    j.estimated_margin_percent,
    j.actual_margin_percent - j.estimated_margin_percent as margin_variance
FROM jobs j
WHERE j.tenant_id = :tenant_id
  AND j.status IN ('completed', 'invoiced', 'paid')
  AND j.completed_date BETWEEN :start_date AND :end_date
ORDER BY j.completed_date DESC;
```

### Jobs Missing Costs

```sql
SELECT j.*
FROM jobs j
LEFT JOIN job_costs jc ON j.id = jc.job_id
WHERE j.tenant_id = :tenant_id
  AND j.status = 'completed'
  AND jc.id IS NULL;
```

### Crew Performance

```sql
SELECT 
    c.name as crew_name,
    COUNT(j.id) as jobs_completed,
    AVG(j.actual_margin_percent) as avg_margin,
    SUM(j.roof_squares) as total_squares,
    SUM(j.roof_squares) / NULLIF(COUNT(DISTINCT j.completed_date), 0) as squares_per_day
FROM crews c
LEFT JOIN jobs j ON c.id = j.assigned_crew_id 
    AND j.status IN ('completed', 'invoiced', 'paid')
    AND j.completed_date > now() - interval '90 days'
WHERE c.tenant_id = :tenant_id
GROUP BY c.id, c.name;
```
