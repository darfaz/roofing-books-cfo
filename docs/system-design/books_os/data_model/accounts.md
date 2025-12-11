# Data Model: Accounts

> **Module**: Books OS  
> **Version**: 1.0.0  

---

## Overview

The `accounts` table stores the chart of accounts, optimized for roofing contractor job costing. It follows a hierarchical structure with parent-child relationships and maps to QuickBooks Online account types.

---

## Table: `accounts`

```sql
CREATE TABLE accounts (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Multi-tenant
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- External System Reference
    qbo_account_id VARCHAR(50),           -- QuickBooks Online account ID
    xero_account_id VARCHAR(50),          -- Future: Xero account ID
    
    -- Account Hierarchy
    code VARCHAR(20) NOT NULL,            -- Account code (e.g., "5100")
    name VARCHAR(255) NOT NULL,           -- Account name
    parent_id UUID REFERENCES accounts(id), -- Parent account for hierarchy
    depth INTEGER DEFAULT 0,              -- Nesting level (0 = root)
    
    -- Classification
    account_type VARCHAR(50) NOT NULL,    -- Asset, Liability, Equity, Revenue, Expense
    account_subtype VARCHAR(50),          -- QBO subtypes (e.g., "AccountsReceivable")
    trade_category VARCHAR(50),           -- Roofing-specific: labor, materials, equipment, subs, overhead
    
    -- Behavior
    is_active BOOLEAN DEFAULT true,
    is_system_account BOOLEAN DEFAULT false, -- Cannot be deleted/renamed
    normal_balance VARCHAR(10) NOT NULL,  -- DEBIT or CREDIT
    
    -- Job Costing
    requires_job_tag BOOLEAN DEFAULT false, -- Must be tagged to a job
    default_cost_code_id UUID REFERENCES cost_codes(id),
    
    -- Metadata
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT unique_tenant_code UNIQUE (tenant_id, code),
    CONSTRAINT valid_account_type CHECK (account_type IN ('Asset', 'Liability', 'Equity', 'Revenue', 'Expense')),
    CONSTRAINT valid_normal_balance CHECK (normal_balance IN ('DEBIT', 'CREDIT'))
);

-- Indexes
CREATE INDEX idx_accounts_tenant ON accounts(tenant_id);
CREATE INDEX idx_accounts_parent ON accounts(parent_id);
CREATE INDEX idx_accounts_type ON accounts(tenant_id, account_type);
CREATE INDEX idx_accounts_qbo ON accounts(tenant_id, qbo_account_id);
CREATE INDEX idx_accounts_trade_category ON accounts(tenant_id, trade_category);

-- Row Level Security
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON accounts
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

---

## Table: `cost_codes`

```sql
CREATE TABLE cost_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Hierarchy
    code VARCHAR(20) NOT NULL,            -- e.g., "LAB-001"
    name VARCHAR(255) NOT NULL,           -- e.g., "Installation Labor"
    parent_id UUID REFERENCES cost_codes(id),
    depth INTEGER DEFAULT 0,
    
    -- Classification
    category VARCHAR(50) NOT NULL,        -- labor, materials, equipment, subcontractor, overhead
    
    -- Defaults
    default_account_id UUID REFERENCES accounts(id),
    default_unit VARCHAR(20),             -- hour, sqft, square, each
    default_rate DECIMAL(19,4),           -- Default cost per unit
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    
    CONSTRAINT unique_tenant_cost_code UNIQUE (tenant_id, code),
    CONSTRAINT valid_category CHECK (category IN ('labor', 'materials', 'equipment', 'subcontractor', 'overhead'))
);

-- Indexes
CREATE INDEX idx_cost_codes_tenant ON cost_codes(tenant_id);
CREATE INDEX idx_cost_codes_category ON cost_codes(tenant_id, category);

-- RLS
ALTER TABLE cost_codes ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON cost_codes
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

---

## Roofing-Optimized Chart of Accounts Template

### Revenue Accounts (4000-4999)

| Code | Name | Trade Category | Requires Job |
|------|------|----------------|--------------|
| 4000 | Revenue | - | No |
| 4100 | Residential Revenue | - | Yes |
| 4110 | Residential - Repair | - | Yes |
| 4120 | Residential - Replacement | - | Yes |
| 4130 | Residential - Storm/Insurance | - | Yes |
| 4200 | Commercial Revenue | - | Yes |
| 4210 | Commercial - Repair | - | Yes |
| 4220 | Commercial - New Construction | - | Yes |
| 4300 | Gutters & Siding | - | Yes |

### Cost of Goods Sold (5000-5999)

| Code | Name | Trade Category | Requires Job |
|------|------|----------------|--------------|
| 5000 | Cost of Goods Sold | - | No |
| 5100 | Labor - Direct | labor | Yes |
| 5110 | Installation Labor | labor | Yes |
| 5120 | Tear-off Labor | labor | Yes |
| 5130 | Repair Labor | labor | Yes |
| 5200 | Materials | materials | Yes |
| 5210 | Shingles | materials | Yes |
| 5220 | Underlayment | materials | Yes |
| 5230 | Flashing & Trim | materials | Yes |
| 5240 | Vents & Accessories | materials | Yes |
| 5250 | Gutters & Downspouts | materials | Yes |
| 5300 | Equipment | equipment | Yes |
| 5310 | Equipment Rental | equipment | Yes |
| 5320 | Small Tools | equipment | Yes |
| 5400 | Subcontractors | subcontractor | Yes |
| 5410 | Sub - Dumpster/Disposal | subcontractor | Yes |
| 5420 | Sub - Specialty Trade | subcontractor | Yes |

### Operating Expenses (6000-6999)

| Code | Name | Trade Category | Requires Job |
|------|------|----------------|--------------|
| 6000 | Operating Expenses | overhead | No |
| 6100 | Payroll - Indirect | overhead | No |
| 6110 | Salaries - Admin | overhead | No |
| 6120 | Salaries - Sales | overhead | No |
| 6130 | Payroll Taxes | overhead | No |
| 6140 | Workers Comp | overhead | No |
| 6150 | Health Insurance | overhead | No |
| 6200 | Vehicle & Equipment | overhead | No |
| 6210 | Vehicle Fuel | overhead | No |
| 6220 | Vehicle Maintenance | overhead | No |
| 6230 | Vehicle Insurance | overhead | No |
| 6240 | Vehicle Payments | overhead | No |
| 6300 | Facilities | overhead | No |
| 6310 | Rent | overhead | No |
| 6320 | Utilities | overhead | No |
| 6330 | Office Supplies | overhead | No |
| 6400 | Marketing | overhead | No |
| 6410 | Advertising | overhead | No |
| 6420 | Lead Generation | overhead | No |
| 6500 | Insurance | overhead | No |
| 6510 | General Liability | overhead | No |
| 6520 | Commercial Auto | overhead | No |
| 6600 | Professional Services | overhead | No |
| 6610 | Accounting | overhead | No |
| 6620 | Legal | overhead | No |
| 6700 | Technology | overhead | No |
| 6710 | Software Subscriptions | overhead | No |
| 6720 | Phone & Internet | overhead | No |

---

## Relationships

```
┌─────────────┐       ┌─────────────┐
│   tenants   │───────│  accounts   │
└─────────────┘       └──────┬──────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │ cost_codes  │   │transactions │   │  journal    │
    └─────────────┘   │ _categorized│   │  _entries   │
                      └─────────────┘   └─────────────┘
```

---

## Data Sources & Sync

| Field | Source | Sync Frequency |
|-------|--------|----------------|
| qbo_account_id | QuickBooks Online | On account change webhook |
| name, type, subtype | QuickBooks Online | On account change webhook |
| code | Spec-OS (mapped from QBO) | On sync |
| trade_category | Spec-OS (template-based) | On onboarding |
| requires_job_tag | Spec-OS configuration | Manual |

---

## Update Triggers

```sql
-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_accounts_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER accounts_updated
    BEFORE UPDATE ON accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_accounts_timestamp();

-- Validate hierarchy depth
CREATE OR REPLACE FUNCTION validate_account_depth()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.parent_id IS NOT NULL THEN
        SELECT depth + 1 INTO NEW.depth
        FROM accounts WHERE id = NEW.parent_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER accounts_depth
    BEFORE INSERT OR UPDATE ON accounts
    FOR EACH ROW
    EXECUTE FUNCTION validate_account_depth();
```
