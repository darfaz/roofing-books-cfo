# CrewCFO Data Model

> **Last Updated**: 2026-01-02
> **Database**: PostgreSQL (Supabase)
> **Multi-tenant**: Yes (RLS enforced)

---

## Overview

CrewCFO uses a multi-tenant PostgreSQL database with Row Level Security (RLS) for tenant isolation. The schema supports:

1. **Core Accounting**: Chart of accounts, transactions, double-entry bookkeeping
2. **Job Costing**: Roofing-specific cost tracking by project
3. **QBO Integration**: OAuth tokens, sync state, transaction mapping
4. **Valuation Engine**: Driver scores, snapshots, shock reports
5. **Financial Analytics**: Cash forecasting, budgets, profit analysis

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              TENANTS                                        │
│  (Multi-tenant root - all data flows through tenant_id)                    │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│    users      │       │tenant_integrations│    │   accounts    │
│  (auth.users) │       │   (QBO, etc)  │       │(chart of accts)│
└───────────────┘       └───────────────┘       └───────┬───────┘
                                                        │
        ┌───────────────────────┬───────────────────────┤
        ▼                       ▼                       ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│   customers   │       │    vendors    │       │     jobs      │
│(homeowners/co)│       │(suppliers/sub)│       │(roofing jobs) │
└───────┬───────┘       └───────┬───────┘       └───────┬───────┘
        │                       │                       │
        └───────────────┬───────┴───────────────────────┘
                        ▼
                ┌───────────────┐
                │ transactions  │
                │(invoices/bills)│
                └───────┬───────┘
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
┌───────────────┐               ┌───────────────┐
│transaction_lines│              │   job_costs   │
│(double-entry) │               │(by category)  │
└───────────────┘               └───────────────┘

VALUATION MODULE:
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│valuation_     │◄─────▶│ driver_scores │       │ roadmap_items │
│snapshots      │       │(6 Matador)    │       │(action items) │
└───────┬───────┘       └───────────────┘       └───────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│              valuation_shock_reports                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ebitda_      │  │multiple_    │  │value_       │           │
│  │adjustments  │  │penalties    │  │unlocks      │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
└───────────────────────────────────────────────────────────────┘
```

---

## Core Tables

### tenants
Multi-tenant root entity. All data references a tenant.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | TEXT | Company name |
| legal_name | TEXT | Legal business name |
| ein | TEXT | Employer ID Number |
| address_* | TEXT | Business address fields |
| phone, email, website | TEXT | Contact info |
| fiscal_year_start_month | INTEGER | 1-12, default January |
| created_at, updated_at | TIMESTAMPTZ | Timestamps |

### users
Linked to Supabase Auth. Multi-tenant via tenant_id.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | FK to auth.users |
| tenant_id | UUID | FK to tenants |
| email | TEXT | User email |
| full_name | TEXT | Display name |
| role | TEXT | 'owner', 'bookkeeper', 'cfo', 'viewer' |

### tenant_integrations
OAuth tokens and integration state for QBO, Plaid, etc.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| provider | TEXT | 'quickbooks', 'plaid', 'slack' |
| access_token | TEXT | OAuth access token (encrypted) |
| refresh_token | TEXT | OAuth refresh token (encrypted) |
| token_expires_at | TIMESTAMPTZ | Token expiration |
| realm_id | TEXT | QBO company ID |
| is_active | BOOLEAN | Integration active flag |
| metadata | JSONB | Provider-specific data |

**Unique Constraint**: (tenant_id, provider)

---

## Chart of Accounts

### accounts
Standard double-entry chart of accounts with roofing extensions.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| code | TEXT | Account code (e.g., '5100') |
| name | TEXT | Account name |
| account_type | TEXT | 'asset', 'liability', 'equity', 'revenue', 'expense' |
| account_subtype | TEXT | e.g., 'bank', 'cogs', 'accounts_receivable' |
| parent_id | UUID | FK to accounts (hierarchy) |
| hierarchy_level | INTEGER | Depth in hierarchy |
| qbo_id | TEXT | QuickBooks account ID |
| is_active | BOOLEAN | Active flag |
| is_system | BOOLEAN | Cannot be deleted |
| normal_balance | TEXT | 'debit' or 'credit' |
| is_job_cost_account | BOOLEAN | Used for job costing |
| job_cost_category | TEXT | 'labor', 'materials', 'subcontractor', 'equipment', 'overhead' |

**Unique Constraint**: (tenant_id, code)

#### Roofing Industry Chart of Accounts
```
1000-1999: Assets
  1000 Operating Checking
  1100 Savings
  1200 Accounts Receivable
  1300 Inventory - Materials
  1500 Vehicles
  1600 Equipment

2000-2999: Liabilities
  2000 Accounts Payable
  2100 Credit Card
  2200 Payroll Liabilities
  2500 Vehicle Loans

3000-3999: Equity
  3000 Owner Equity
  3100 Owner Draws
  3200 Retained Earnings

4000-4999: Revenue
  4000 Roofing Revenue
  4100 Repair Revenue
  4200 Insurance Revenue

5000-5999: Cost of Goods Sold (Job Costs)
  5100 Materials [job_cost: materials]
  5200 Subcontractors [job_cost: subcontractor]
  5300 Labor - Direct [job_cost: labor]
  5400 Equipment Rental [job_cost: equipment]
  5500 Permits & Fees [job_cost: overhead]
  5600 Dump Fees [job_cost: overhead]

6000-7999: Operating Expenses (Overhead)
  6100 Advertising & Marketing
  6200 Office Expenses
  6300-6320 Insurance (GL, WC, Vehicle)
  6400 Vehicle Expense
  6500 Fuel
  6700 Professional Fees
  6900 Payroll - Admin
  7000 Rent
  7100 Utilities
```

---

## Customers & Vendors

### customers
Residential and commercial customers.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| name | TEXT | Customer name |
| display_name | TEXT | Display name |
| company_name | TEXT | For commercial |
| email, phone | TEXT | Contact info |
| billing_address_* | TEXT | Billing address |
| customer_type | TEXT | 'residential', 'commercial', 'insurance', 'builder' |
| payment_terms_days | INTEGER | Default 30 |
| qbo_id | TEXT | QuickBooks ID |

### vendors
Suppliers, subcontractors, and service providers.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| name | TEXT | Vendor name |
| vendor_type | TEXT | 'supplier', 'subcontractor', 'utility', 'professional' |
| default_expense_account_id | UUID | Default account for bills |
| payment_terms_days | INTEGER | Default 30 |
| ein | TEXT | For 1099 reporting |
| w9_on_file | BOOLEAN | W9 received |
| insurance_certificate_on_file | BOOLEAN | COI on file |
| insurance_expiry_date | DATE | COI expiration |
| qbo_id | TEXT | QuickBooks ID |

---

## Jobs (Roofing Projects)

### jobs
Roofing projects with job costing.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| job_number | TEXT | e.g., 'JOB-2024-001' |
| name | TEXT | Project name |
| customer_id | UUID | FK to customers |
| job_address_* | TEXT | Project location |
| job_type | TEXT | 'replacement', 'repair', 'new_construction', 'commercial', 'insurance_claim', 'maintenance' |
| estimate_date | DATE | Date estimated |
| start_date | DATE | Actual start |
| target_completion_date | DATE | Target finish |
| actual_completion_date | DATE | Actual finish |
| status | TEXT | 'estimate', 'pending', 'scheduled', 'in_progress', 'completed', 'closed', 'cancelled' |
| contract_amount | DECIMAL | Contracted price |
| estimated_cost | DECIMAL | Estimated costs |
| estimated_margin_pct | DECIMAL | Target margin |
| actual_revenue | DECIMAL | Running total (trigger-updated) |
| actual_cost | DECIMAL | Running total (trigger-updated) |
| actual_margin_pct | DECIMAL | Calculated margin |
| is_insurance_job | BOOLEAN | Insurance claim flag |
| insurance_company | TEXT | Carrier name |
| claim_number | TEXT | Claim reference |
| deductible_amount | DECIMAL | Customer deductible |

**Unique Constraint**: (tenant_id, job_number)

### job_costs
Individual cost entries linked to jobs.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| job_id | UUID | FK to jobs |
| transaction_id | UUID | FK to transactions |
| cost_date | DATE | Date incurred |
| cost_category | TEXT | 'labor', 'materials', 'subcontractor', 'equipment', 'overhead' |
| description | TEXT | Line item description |
| vendor_id | UUID | FK to vendors |
| quantity | DECIMAL | Units |
| unit_cost | DECIMAL | Per unit cost |
| total_cost | DECIMAL | Total |
| labor_hours | DECIMAL | Hours worked (labor) |
| labor_rate | DECIMAL | Hourly rate |
| labor_burden_rate | DECIMAL | Burden % (default 20%) |
| is_billable | BOOLEAN | Billable to customer |
| is_billed | BOOLEAN | Already invoiced |

**Trigger**: `recalculate_job_totals` updates jobs.actual_cost on insert/update/delete

---

## Transactions

### transactions
All financial transactions synced from QBO or entered manually.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| transaction_date | DATE | Transaction date |
| transaction_type | TEXT | 'invoice', 'payment', 'bill', 'bill_payment', 'expense', 'deposit', 'transfer', 'journal_entry' |
| reference_number | TEXT | Check #, invoice # |
| memo | TEXT | Description |
| customer_id | UUID | FK to customers |
| vendor_id | UUID | FK to vendors |
| total_amount | DECIMAL | Total amount |
| status | TEXT | 'pending', 'posted', 'voided', 'reconciled' |
| classification_status | TEXT | 'unclassified', 'auto_classified', 'manual_classified', 'review_needed' |
| classification_confidence | DECIMAL | 0.00 to 1.00 |
| classified_by | TEXT | 'rule', 'ml', 'llm', 'user' |
| classified_at | TIMESTAMPTZ | When classified |
| category | TEXT | Budget category |
| qbo_id | TEXT | QuickBooks transaction ID |
| qbo_type | TEXT | 'Purchase', 'Invoice', 'Deposit' |
| qbo_synced_at | TIMESTAMPTZ | Last sync time |
| metadata | JSONB | Raw QBO data |

### transaction_lines
Double-entry accounting lines.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| transaction_id | UUID | FK to transactions |
| account_id | UUID | FK to accounts |
| job_id | UUID | FK to jobs (optional) |
| debit_amount | DECIMAL | Debit |
| credit_amount | DECIMAL | Credit |
| description | TEXT | Line description |
| line_number | INTEGER | Order |

---

## Valuation Module

### valuation_snapshots
Point-in-time business valuations.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| as_of_date | DATE | Snapshot date |
| ttm_revenue | DECIMAL | Trailing 12-month revenue |
| ttm_sde | DECIMAL | Seller's discretionary earnings |
| ttm_ebitda | DECIMAL | EBITDA |
| tier | TEXT | 'below_avg', 'avg', 'above_avg' |
| multiple_low | DECIMAL | Low multiple |
| multiple_high | DECIMAL | High multiple |
| ev_low | DECIMAL | Low enterprise value |
| ev_high | DECIMAL | High enterprise value |
| confidence_score | INTEGER | 0-100 |
| drivers_json | JSONB | Aggregated driver data |
| computed_by | TEXT | 'system', 'user' |
| automation_tier | TEXT | 'rules', 'ml', 'llm', 'hybrid' |
| human_reviewed | BOOLEAN | CFO reviewed |
| review_required | BOOLEAN | Needs review |

### driver_scores
Individual Matador driver scores.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| valuation_snapshot_id | UUID | FK to valuation_snapshots |
| as_of_date | DATE | Score date |
| driver_key | TEXT | See Driver Keys below |
| score | INTEGER | 0-100 |
| weight | DECIMAL | Driver weight |
| evidence_refs | JSONB | Supporting evidence |
| confidence | INTEGER | 0-100 |
| impact_on_multiple | DECIMAL | Multiple impact |
| human_reviewed | BOOLEAN | CFO reviewed |

#### Driver Keys
| Key | Driver | Weight |
|-----|--------|--------|
| management_independence | Management Independence | High |
| financial_records | Financial Records Quality | High |
| recurring_revenue | Recurring Revenue | Medium |
| operational_systems | Operational Systems | Medium |
| customer_diversity | Customer Base Diversity | Medium |
| market_outlook | Market Outlook | Low |

### roadmap_items
Value improvement action items.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| driver_key | TEXT | Related driver |
| title | TEXT | Action title |
| description | TEXT | Details |
| category | TEXT | 'weekly_ops', 'monthly_close', 'quarterly_review', 'strategic', 'compliance' |
| priority | TEXT | 'low', 'medium', 'high', 'critical' |
| status | TEXT | 'pending', 'in_progress', 'completed', 'cancelled', 'blocked' |
| expected_impact_ev | DECIMAL | EV impact if completed |
| effort_level | TEXT | 'low', 'medium', 'high' |
| estimated_hours | INTEGER | Time estimate |
| due_date | DATE | Target date |
| completed_at | TIMESTAMPTZ | Completion timestamp |

---

## Shock Report Tables

### valuation_shock_reports
The "WOW moment" gap analysis.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| generated_at | TIMESTAMPTZ | Generation time |
| **Owner View** | | |
| reported_revenue | NUMERIC | Owner's reported revenue |
| reported_ebitda | NUMERIC | Owner's EBITDA |
| reported_owner_comp | NUMERIC | Owner compensation |
| reported_addbacks | NUMERIC | Total add-backs |
| expected_multiple | NUMERIC | Owner's expected (usually 10x) |
| expected_valuation | NUMERIC | Owner's expected value |
| **Buyer View** | | |
| defensible_ebitda | NUMERIC | Buyer's EBITDA |
| defensible_sde | NUMERIC | Buyer's SDE |
| buyer_multiple_low | NUMERIC | Low multiple |
| buyer_multiple_high | NUMERIC | High multiple |
| buyer_valuation_low | NUMERIC | Low valuation |
| buyer_valuation_high | NUMERIC | High valuation |
| **Gap Analysis** | | |
| ebitda_haircut | NUMERIC | EBITDA reduction |
| multiple_penalty | NUMERIC | Multiple reduction |
| value_gap | NUMERIC | $ gap |
| value_gap_percentage | NUMERIC | % gap |
| total_recoverable_value | NUMERIC | Potential recovery |
| **Data Quality** | | |
| qbo_data_range_start | DATE | Data start |
| qbo_data_range_end | DATE | Data end |
| transaction_count | INTEGER | Transactions analyzed |
| confidence_score | INTEGER | 0-100 |
| **Tracking** | | |
| pdf_generated | BOOLEAN | PDF created |
| pdf_downloaded | BOOLEAN | PDF downloaded |
| trial_started | BOOLEAN | User started trial |

### ebitda_adjustments
Individual add-back/haircut decisions.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| shock_report_id | UUID | FK to shock reports |
| adjustment_type | TEXT | 'owner_compensation', 'personal_expense', 'one_time_revenue', 'one_time_expense', 'non_recurring', 'related_party', 'discretionary', 'non_operating' |
| category | TEXT | 'accepted', 'rejected', 'partial', 'needs_review' |
| description | TEXT | Description |
| amount | NUMERIC | Original amount |
| accepted_amount | NUMERIC | Buyer accepted |
| transaction_ids | JSONB | Source transactions |
| buyer_concern | TEXT | Buyer's concern |
| rejection_reason | TEXT | Why rejected |
| is_recoverable | BOOLEAN | Can be fixed |
| remediation_action | TEXT | How to fix |
| remediation_effort | TEXT | 'low', 'medium', 'high' |
| remediation_impact | NUMERIC | $ if fixed |

### multiple_penalties
Why the multiple is reduced.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| shock_report_id | UUID | FK to shock reports |
| driver_key | TEXT | Which driver |
| penalty_amount | NUMERIC | e.g., -1.5 |
| baseline_multiple | NUMERIC | Starting multiple |
| resulting_multiple | NUMERIC | After penalty |
| driver_score | INTEGER | 0-100 |
| reason | TEXT | Short reason |
| buyer_concern | TEXT | Detailed concern |
| due_diligence_flag | TEXT | What buyer investigates |
| remediation_action | TEXT | How to fix |
| remediation_timeline | TEXT | '3-6 months' |
| multiple_recovery | NUMERIC | Recovery potential |

### value_unlocks
Prioritized recovery actions.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| shock_report_id | UUID | FK to shock reports |
| priority_rank | INTEGER | Sort order |
| title | TEXT | Action title |
| description | TEXT | Details |
| action_type | TEXT | 'ebitda_recovery', 'multiple_expansion', 'revenue_quality' |
| ebitda_impact | NUMERIC | EBITDA improvement |
| multiple_impact | NUMERIC | Multiple improvement |
| ev_impact | NUMERIC | Total EV impact |
| effort_level | TEXT | 'low', 'medium', 'high' |
| timeline | TEXT | Time to complete |
| is_locked | BOOLEAN | Paywall locked |
| is_preview | BOOLEAN | Show as teaser |

---

## Finance Tables

### budgets
Monthly budget by category.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| budget_period | TEXT | 'YYYY-MM' |
| year | INTEGER | Year |
| month | INTEGER | 1-12 |
| categories | JSONB | {revenue: x, cogs: y, ...} |
| notes | TEXT | Budget notes |

**Unique Constraint**: (tenant_id, budget_period)

### cash_flow_forecasts
13-week cash forecast snapshots.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| forecast_date | DATE | When generated |
| scenario | TEXT | 'base', 'optimistic', 'pessimistic' |
| starting_cash | DECIMAL | Opening cash |
| ending_cash | DECIMAL | 13-week ending |
| min_cash | DECIMAL | Lowest point |
| min_cash_week | INTEGER | Week of lowest |
| runway_weeks | INTEGER | Weeks until $0 |
| summary_json | JSONB | Summary data |
| weekly_forecast_json | JSONB | Week-by-week |
| ar_total | DECIMAL | Total AR |
| ap_total | DECIMAL | Total AP |

**Unique Constraint**: (tenant_id, forecast_date, scenario)

### cash_positions
Daily cash position snapshots.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| position_date | DATE | Snapshot date |
| total_cash | DECIMAL | Total cash |
| operating_account | DECIMAL | Primary checking |
| savings_account | DECIMAL | Savings |
| ar_total | DECIMAL | Total AR |
| ar_current | DECIMAL | AR current |
| ar_overdue | DECIMAL | AR overdue |
| ap_total | DECIMAL | Total AP |
| ap_overdue | DECIMAL | AP overdue |
| runway_weeks | INTEGER | Weeks of runway |

**Unique Constraint**: (tenant_id, position_date)

### vendor_payment_schedules
Planned AP payments.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| vendor_id | UUID | FK to vendors |
| transaction_id | UUID | FK to transactions (bill) |
| scheduled_date | DATE | Payment date |
| amount | DECIMAL | Payment amount |
| status | TEXT | 'scheduled', 'pending', 'paid', 'cancelled' |
| payment_method | TEXT | 'check', 'ach', 'credit_card', 'wire' |

---

## Classification & Automation

### classification_rules
Rule-based transaction classification.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| name | TEXT | Rule name |
| priority | INTEGER | Lower = higher priority |
| is_active | BOOLEAN | Active flag |
| **Match Conditions** | | |
| match_vendor_name | TEXT | ILIKE pattern |
| match_memo | TEXT | ILIKE pattern |
| match_amount_min | DECIMAL | Min amount |
| match_amount_max | DECIMAL | Max amount |
| match_transaction_type | TEXT | Transaction type |
| **Result** | | |
| target_account_id | UUID | FK to accounts |
| target_job_id | UUID | FK to jobs (optional) |
| **Stats** | | |
| times_applied | INTEGER | Usage count |
| last_applied_at | TIMESTAMPTZ | Last used |

---

## Supporting Tables

### cfo_briefs
Weekly/monthly CFO summary emails.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| brief_date | DATE | Brief date |
| brief_type | TEXT | 'weekly', 'monthly', 'custom' |
| metrics | JSONB | Metrics snapshot |
| narrative | TEXT | AI-generated text |
| html_content | TEXT | Formatted HTML |
| sent_at | TIMESTAMPTZ | Delivery time |
| sent_to | TEXT[] | Recipients |

### audit_log
System-wide audit trail.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| user_id | UUID | FK to users |
| action | TEXT | 'create', 'update', 'delete', 'login' |
| table_name | TEXT | Affected table |
| record_id | UUID | Affected record |
| old_values | JSONB | Before state |
| new_values | JSONB | After state |
| metadata | JSONB | Additional context |
| ip_address | INET | Client IP |
| user_agent | TEXT | Browser/client |

### shock_report_analytics
User engagement tracking.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK to tenants |
| shock_report_id | UUID | FK to shock reports |
| event_type | TEXT | 'report_viewed', 'pdf_downloaded', etc. |
| section_name | TEXT | Which section |
| time_on_page | INTEGER | Seconds |
| scroll_depth | INTEGER | % scrolled |

---

## Views

### v_ar_aging
AR aging analysis with bucket classification.

```sql
SELECT
    tenant_id,
    transaction_id,
    invoice_number,
    customer_name,
    total_amount,
    balance_due,
    days_outstanding,
    aging_bucket  -- 'current', '31-60', '61-90', '90+'
FROM v_ar_aging
```

### v_job_profitability
Job-level profit metrics.

```sql
SELECT
    tenant_id,
    job_id,
    job_number,
    job_name,
    customer_name,
    contract_amount,
    actual_revenue,
    actual_cost,
    gross_profit,
    gross_margin_pct
FROM v_job_profitability
```

---

## Row Level Security

All tenant-scoped tables have RLS policies:

```sql
CREATE POLICY tenant_isolation ON table_name
    FOR ALL USING (
        tenant_id = (auth.jwt() -> 'user_metadata' ->> 'tenant_id')::uuid
    );
```

The tenant_id is stored in the user's JWT claims via Supabase Auth.

---

## Indexes

Key performance indexes:

| Table | Index | Purpose |
|-------|-------|---------|
| transactions | (tenant_id, transaction_date) | Date queries |
| transactions | (tenant_id, classification_status) | Unclassified lookup |
| transactions | (tenant_id, qbo_id) | Deduplication |
| jobs | (tenant_id, status) | Active jobs |
| job_costs | (job_id) | Job costing |
| valuation_snapshots | (tenant_id, as_of_date DESC) | Latest snapshot |
| driver_scores | (tenant_id, as_of_date, driver_key) | Unique constraint |
| roadmap_items | (expected_impact_ev DESC) | Priority sorting |

---

## Migration Order

1. `schema.sql` - Core tables (tenants, users, accounts, customers, vendors, jobs, transactions)
2. `001_add_valuation_tables.sql` - Valuation snapshots, driver scores, roadmap items
3. `002_add_shock_report_tables.sql` - Shock reports, adjustments, penalties, unlocks
4. `003_add_finance_tables.sql` - Budgets, cash flow forecasts
5. `004_auto_create_tenant.sql` - Auto-create tenant on signup
6. `005_seed_demo_data.sql` - Demo tenant data
