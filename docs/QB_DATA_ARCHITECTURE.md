# QuickBooks Data Architecture for Roofing CFO Analytics

## Overview

This document defines the comprehensive data model for pulling and analyzing QuickBooks data to provide roofing contractors with actionable financial intelligence.

## 1. Available QuickBooks Reports API

The `node-quickbooks` library provides these report methods:

### Financial Reports (Core Analytics)
| Report | Method | Use Case |
|--------|--------|----------|
| P&L (Income Statement) | `reportProfitAndLoss` | Revenue, COGS, gross profit, expenses, net income |
| P&L Detail | `reportProfitAndLossDetail` | Transaction-level P&L breakdown |
| Balance Sheet | `reportBalanceSheet` | Assets, liabilities, equity snapshot |
| Cash Flow | `reportCashFlow` | Operating, investing, financing cash flows |
| Trial Balance | `reportTrialBalance` | All account balances |
| General Ledger | `reportGeneralLedgerDetail` | Complete transaction history |

### Receivables Reports (Cash Flow)
| Report | Method | Use Case |
|--------|--------|----------|
| AR Aging Summary | `reportAgedReceivables` | Customer payment timeliness |
| AR Aging Detail | `reportAgedReceivableDetail` | Individual invoice aging |
| Customer Balance | `reportCustomerBalance` | Outstanding by customer |
| Customer Income | `reportCustomerIncome` | Revenue by customer |
| Customer Sales | `reportCustomerSales` | Sales performance by customer |

### Payables Reports (Cash Flow)
| Report | Method | Use Case |
|--------|--------|----------|
| AP Aging Summary | `reportAgedPayables` | Vendor payment obligations |
| AP Aging Detail | `reportAgedPayableDetail` | Individual bill aging |
| Vendor Balance | `reportVendorBalance` | Outstanding by vendor |
| Vendor Expenses | `reportVendorExpenses` | Spending by vendor |

### Other Reports
| Report | Method | Use Case |
|--------|--------|----------|
| Item Sales | `reportItemSales` | Product/service revenue |
| Inventory Valuation | `reportInventoryValuationSummary` | Inventory value |
| Transaction List | `reportTransactionList` | All transactions |

## 2. CFO Analytics Metrics

### Break-Even Analysis
```
Break-Even Revenue = Fixed Costs / Gross Margin %

Required Data:
- P&L Report: Revenue, COGS, Fixed Expenses
- Calculate: Variable costs (COGS) vs Fixed costs
```

### Valuation Metrics
```
EBITDA = Net Income + Interest + Taxes + Depreciation + Amortization
SDE = EBITDA + Owner Salary + Owner Benefits + Owner Discretionary

Required Data:
- P&L Report: Net income, interest expense
- Chart of Accounts: Identify owner compensation accounts
- Depreciation from expense accounts
```

### Profit Leak Detection
```
Key Metrics:
1. Gross Margin % by month (trend analysis)
2. Labor Cost % (payroll / revenue)
3. Material Cost % (COGS - labor) / revenue
4. Overhead Cost % (fixed expenses / revenue)
5. Customer Concentration (top 5 customers % of revenue)
6. AR Days Outstanding (AR / daily revenue)
7. AP Days Outstanding (AP / daily expenses)
```

### Cash Flow Analysis
```
Operating Cash = Net Income + Non-Cash Expenses +/- Working Capital Changes
Free Cash Flow = Operating Cash - CapEx

Required Data:
- Cash Flow Report or calculated from P&L + Balance Sheet changes
- AR/AP aging for working capital analysis
```

## 3. Roofing Industry Chart of Accounts Mapping

### Revenue Categories
- `4000` - Roofing Income (primary services)
- `4100` - Residential Roofing
- `4200` - Commercial Roofing
- `4300` - Repairs & Maintenance
- `4400` - Insurance Restoration

### Cost of Goods Sold (Variable Costs)
- `5000` - Materials
- `5100` - Labor - Direct (production wages)
- `5200` - Subcontractor Costs
- `5300` - Equipment Rental
- `5400` - Permits & Fees

### Fixed Operating Expenses
- `6000` - Office Salaries
- `6100` - Rent/Lease
- `6200` - Insurance
- `6300` - Utilities
- `6400` - Marketing & Advertising
- `6500` - Vehicle Expenses
- `6600` - Professional Services

### Owner Discretionary Expenses (for SDE calculation)
- Officer Salaries
- Owner Health Insurance
- Owner Auto
- Owner Cell Phone
- Retirement Contributions

## 4. Data Sync Strategy

### Real-Time Sync (via MCP)
- Pull reports on-demand for dashboard display
- No storage needed for current period data

### Periodic Sync (for trend analysis)
- Store monthly snapshots in Supabase
- Track changes over time
- Enable YoY comparisons

### Supabase Schema Extensions

```sql
-- Monthly P&L snapshots
CREATE TABLE monthly_pnl_snapshots (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id),
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  total_revenue DECIMAL(15,2),
  total_cogs DECIMAL(15,2),
  gross_profit DECIMAL(15,2),
  gross_margin_pct DECIMAL(5,2),
  total_expenses DECIMAL(15,2),
  net_income DECIMAL(15,2),
  net_margin_pct DECIMAL(5,2),
  -- EBITDA components
  interest_expense DECIMAL(15,2),
  depreciation DECIMAL(15,2),
  amortization DECIMAL(15,2),
  ebitda DECIMAL(15,2),
  -- Owner add-backs
  owner_salary DECIMAL(15,2),
  owner_benefits DECIMAL(15,2),
  sde DECIMAL(15,2),
  raw_report_json JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(tenant_id, period_start)
);

-- AR/AP aging snapshots
CREATE TABLE aging_snapshots (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id),
  snapshot_date DATE NOT NULL,
  report_type VARCHAR(20) NOT NULL, -- 'receivables' or 'payables'
  current_amount DECIMAL(15,2),
  days_1_30 DECIMAL(15,2),
  days_31_60 DECIMAL(15,2),
  days_61_90 DECIMAL(15,2),
  days_over_90 DECIMAL(15,2),
  total_amount DECIMAL(15,2),
  raw_report_json JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Customer concentration analysis
CREATE TABLE customer_revenue_analysis (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id),
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  customer_id VARCHAR(50),
  customer_name VARCHAR(255),
  revenue DECIMAL(15,2),
  pct_of_total DECIMAL(5,2),
  rank_order INT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 5. MCP Tools to Add

### Priority 1: Core Financial Reports
1. `report_profit_and_loss` - P&L for any date range
2. `report_balance_sheet` - Balance sheet snapshot
3. `report_cash_flow` - Cash flow statement
4. `report_aged_receivables` - AR aging
5. `report_aged_payables` - AP aging

### Priority 2: Analytics Reports
6. `report_customer_income` - Revenue by customer
7. `report_customer_sales` - Sales by customer
8. `report_vendor_expenses` - Expenses by vendor
9. `report_trial_balance` - All account balances
10. `report_general_ledger` - Transaction detail

## 6. Dashboard Data Flow

```
QuickBooks API
     │
     ▼
MCP Report Tools ──────────────────┐
     │                             │
     ▼                             ▼
Real-time Reports          Supabase Snapshots
(current period)           (historical data)
     │                             │
     └──────────┬──────────────────┘
                │
                ▼
        Analytics Engine
                │
     ┌──────────┼──────────┐
     ▼          ▼          ▼
Break-Even  Valuation  Profit Leaks
Analysis    Metrics    Detection
     │          │          │
     └──────────┴──────────┘
                │
                ▼
         Dashboard UI
```

## 7. Implementation Order

1. **Phase 1: Core Reports MCP Tools**
   - Add P&L, Balance Sheet, Cash Flow report tools
   - Add AR/AP Aging report tools
   - Test with Phoenix Design QB account

2. **Phase 2: Analytics Calculations**
   - Build break-even calculator
   - Build EBITDA/SDE calculator
   - Build profit leak detector

3. **Phase 3: Dashboard Integration**
   - Update FinanceDashboard to use real P&L data
   - Update OwnerDashboard with break-even metrics
   - Add profit leak alerts

4. **Phase 4: Historical Tracking**
   - Add monthly snapshot jobs
   - Build trend analysis
   - Add YoY comparisons
