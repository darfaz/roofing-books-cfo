# QuickBooks Online Integration Specification

> **Feature**: 08-qbo-integration
> **Status**: Implemented
> **Priority**: P0 (Core)
> **Last Updated**: 2026-01-02

---

## Overview

QuickBooks Online (QBO) integration is the core data pipeline that syncs financial data from the contractor's accounting system into CrewCFO. It handles OAuth authentication, transaction sync, expense classification, and real-time data access.

**Target User**: All users (background service)
**Access Frequency**: Automatic (continuous)
**Key Question Answered**: "Is my financial data up-to-date and properly classified?"

---

## User Stories

### US-01: Connect QuickBooks Account
**As a** roofing contractor owner
**I want to** connect my QuickBooks Online account securely
**So that** my financial data can be analyzed automatically

**Acceptance Criteria**:
- [ ] OAuth2 authorization flow with Intuit
- [ ] Secure token storage in Supabase
- [ ] Display connection status (connected/disconnected)
- [ ] Show company name after successful connection
- [ ] Automatic token refresh before expiration

### US-02: Sync Transactions Automatically
**As a** roofing contractor owner
**I want to** have my transactions synced automatically
**So that** I always see up-to-date financial data

**Acceptance Criteria**:
- [ ] Full sync on initial connection
- [ ] Incremental sync for new transactions
- [ ] Sync purchases, invoices, and deposits
- [ ] Deduplication via qbo_id
- [ ] Sync status indicator in UI

### US-03: Classify Expenses Automatically
**As a** roofing contractor owner
**I want to** have my expenses classified as overhead vs job cost
**So that** I can see accurate profitability metrics

**Acceptance Criteria**:
- [ ] Auto-classify based on QBO account type/subtype
- [ ] Use roofing-specific keyword rules
- [ ] Display confidence level (0-100%)
- [ ] Flag low-confidence for manual review
- [ ] Support manual override

### US-04: View Connection Status
**As a** roofing contractor owner
**I want to** see if my QuickBooks is connected and syncing
**So that** I know my data is current

**Acceptance Criteria**:
- [ ] Show connected/disconnected status
- [ ] Display last sync timestamp
- [ ] Show transaction count synced
- [ ] Ability to disconnect and reconnect
- [ ] Error messages if sync fails

### US-05: Manual Sync Trigger
**As a** roofing contractor owner
**I want to** manually trigger a sync when needed
**So that** I can get the latest data before making decisions

**Acceptance Criteria**:
- [ ] "Sync Now" button in settings
- [ ] Progress indicator during sync
- [ ] Success/failure notification
- [ ] Sync should complete within 30 seconds

---

## OAuth2 Flow

### Authorization URL
```
https://appcenter.intuit.com/connect/oauth2?
  client_id={client_id}&
  response_type=code&
  scope=com.intuit.quickbooks.accounting&
  redirect_uri={redirect_uri}&
  state={state}
```

### Token Exchange
```
POST https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer
Authorization: Basic {base64(client_id:client_secret)}
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code={authorization_code}&
redirect_uri={redirect_uri}
```

### Token Refresh
```
POST https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer
Authorization: Basic {base64(client_id:client_secret)}
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&
refresh_token={refresh_token}
```

### Token Storage
```typescript
interface TenantIntegration {
  id: string
  tenant_id: string
  provider: 'quickbooks'
  realm_id: string
  access_token: string      // Encrypted
  refresh_token: string     // Encrypted
  token_expires_at: string  // ISO timestamp
  is_active: boolean
  metadata: {
    company_name?: string
    last_sync_at?: string
    token_type?: string
    last_refreshed_at?: string
  }
}
```

---

## Transaction Types

### Supported QBO Entities

| QBO Entity | Maps To | Description |
|------------|---------|-------------|
| `Purchase` | bill, expense | Bills and credit card expenses |
| `Invoice` | invoice | Customer invoices (AR) |
| `Deposit` | deposit | Bank deposits and payments received |
| `Bill` | bill | Vendor bills (AP) |

### Transaction Normalization

```typescript
interface NormalizedTransaction {
  qbo_id: string
  qbo_type: 'Purchase' | 'Invoice' | 'Deposit' | 'Bill'
  transaction_date: string
  transaction_type: 'bill' | 'expense' | 'invoice' | 'deposit'
  total_amount: number
  memo: string
  vendor_name?: string
  customer_name?: string
  reference_number?: string
  status: 'pending' | 'posted'
  classification_status: 'unclassified' | 'auto_classified' | 'review_needed' | 'approved'
  qbo_synced_at: string
  metadata: {
    payment_type?: string
    balance?: number
    due_date?: string
    sync_token?: string
    raw_data: object
  }
}
```

---

## Expense Classification

### Classification Categories

#### Overhead Categories
| Key | Label | QBO SubTypes | Keywords |
|-----|-------|--------------|----------|
| payroll | Payroll & Taxes | PayrollExpenses, PayrollTaxExpenses | salary, wages, fica |
| insurance | Insurance | Insurance | liability, general insurance |
| office | Office & Admin | OfficeGeneralAdministrativeExpenses | office, admin, supplies |
| professional_fees | Professional Fees | LegalProfessionalFees | lawyer, accounting, legal |
| marketing | Marketing | AdvertisingPromotional | advertising, promotion |
| utilities | Utilities | Utilities | electric, gas, phone, internet |
| rent | Rent | RentOrLeaseOfBuildings | rent, lease, mortgage |
| depreciation | Depreciation | Depreciation | depreciation, amortization |

#### Job Cost Categories
| Key | Label | QBO SubTypes | Keywords |
|-----|-------|--------------|----------|
| materials | Materials | SuppliesMaterials, COGS | shingle, lumber, material |
| direct_labor | Direct Labor | CostOfLaborCos | labor, wages, crew |
| equipment | Equipment Rental | EquipmentRental | rental, tool, equipment |
| subcontractors | Subcontractors | OtherMiscellaneousServiceCost | subcontract, sub |
| disposal | Disposal | - | dump, haul, disposal |
| permits | Permits | - | permit, inspection |
| workers_comp | Workers Comp | - | workers comp, workman |

### Classification Logic

```python
def classify_expense_account(account):
    """
    Classification hierarchy:
    1. COGS account type -> always job_cost
    2. Workers comp keywords -> job_cost (scales with labor)
    3. QBO AccountSubType lookup
    4. Account name keyword matching
    5. Default to "mixed" for manual review
    """

    # Priority 1: COGS
    if account.type == "Cost of Goods Sold":
        return "job_cost", 1.0

    # Priority 2: Workers comp
    if any(kw in account.name.lower() for kw in WORKERS_COMP_KEYWORDS):
        return "job_cost", 0.95

    # Priority 3: AccountSubType
    if account.subtype in OVERHEAD_SUBTYPES:
        return "overhead", 0.85
    if account.subtype in JOB_COST_SUBTYPES:
        return "job_cost", 0.75

    # Priority 4: Name keywords
    for kw in JOB_COST_KEYWORDS:
        if kw in account.name.lower():
            return "job_cost", 0.80

    for kw in OVERHEAD_KEYWORDS:
        if kw in account.name.lower():
            return "overhead", 0.80

    # Priority 5: Default
    return "mixed", 0.50
```

### Confidence-Based Routing

| Confidence | Action | UI Treatment |
|------------|--------|--------------|
| ≥95% | Auto-commit | No review needed |
| 80-94% | Flagged review | Yellow indicator, optional review |
| 60-79% | Human required | Requires approval before use |
| <60% | Exception queue | Must be manually classified |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/qbo/connect` | GET | Initiate OAuth flow |
| `/api/qbo/callback` | GET | OAuth callback handler |
| `/api/qbo/status` | GET | Get connection status |
| `/api/qbo/sync` | POST | Trigger manual sync |
| `/api/qbo/disconnect` | POST | Disconnect integration |
| `/api/qbo/accounts` | GET | Get chart of accounts |
| `/api/qbo/overhead/summary` | GET | Get overhead analysis |
| `/api/qbo/expenses/classified` | GET | Get classified expenses |

### Sync Response
```json
{
  "status": "success",
  "synced_count": 147,
  "total_fetched": 150,
  "errors": [],
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

### Status Response
```json
{
  "connected": true,
  "company_name": "Apex Roofing Solutions",
  "realm_id": "1234567890",
  "last_sync_at": "2025-01-15T10:30:00Z",
  "transaction_count": 1247,
  "next_refresh_at": "2025-01-15T11:00:00Z"
}
```

---

## Sync Service Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      QBOSyncService                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. FETCH FROM QBO                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Purchases  │  │  Invoices   │  │  Deposits   │            │
│  │  (expenses) │  │    (AR)     │  │ (payments)  │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                │                │                    │
│         ▼                ▼                ▼                    │
│  2. NORMALIZE        3. DEDUPLICATE     4. CLASSIFY           │
│  ┌─────────────────────────────────────────────────┐          │
│  │  - Standard transaction format                   │          │
│  │  - Extract vendor/customer names                 │          │
│  │  - Parse amounts and dates                       │          │
│  │  - Check for existing qbo_id                     │          │
│  │  - Auto-classify expense accounts                │          │
│  └─────────────────────────────────────────────────┘          │
│                          │                                     │
│                          ▼                                     │
│  5. STORE IN SUPABASE                                         │
│  ┌─────────────────────────────────────────────────┐          │
│  │  transactions table                              │          │
│  │  - tenant_id, qbo_id (unique)                   │          │
│  │  - classification_status, confidence            │          │
│  │  - metadata with raw QBO data                   │          │
│  └─────────────────────────────────────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## QBO Query Examples

### Get Purchases
```sql
SELECT * FROM Purchase
WHERE TxnDate >= '2024-01-01' AND TxnDate <= '2024-12-31'
```

### Get Invoices
```sql
SELECT * FROM Invoice
WHERE TxnDate >= '2024-01-01' AND TxnDate <= '2024-12-31'
```

### Get Chart of Accounts
```sql
SELECT * FROM Account WHERE Active = true
```

### Get Company Info
```sql
SELECT * FROM CompanyInfo
```

---

## Error Handling

### Token Expiration
```python
# Token expired - refresh automatically
if response.status_code == 401:
    if refresh_token:
        new_tokens = refresh_access_token(refresh_token)
        retry_request(new_tokens.access_token)
    else:
        mark_integration_inactive()
        raise "QBO connection expired. Please reconnect."
```

### Invalid Grant
```python
# Refresh token revoked - require reconnection
if error_type == "invalid_grant":
    mark_integration_inactive()
    notify_user("QuickBooks disconnected. Please reconnect.")
```

### Rate Limiting
```python
# QBO rate limit: 500 requests per minute
if response.status_code == 429:
    wait(response.headers["Retry-After"])
    retry_request()
```

---

## Environment Variables

```bash
QBO_CLIENT_ID=your_client_id
QBO_CLIENT_SECRET=your_client_secret
QBO_ENVIRONMENT=production  # or 'sandbox'
QBO_REDIRECT_URI=https://app.crewcfo.com/api/qbo/callback
```

---

## Security Considerations

1. **Token Encryption**: Access/refresh tokens stored encrypted in Supabase
2. **RLS Policies**: Tenant isolation via Row Level Security
3. **Token Rotation**: Refresh tokens before expiration (5 min buffer)
4. **Audit Logging**: Track all QBO API calls and sync events
5. **No PII Storage**: Minimize storage of sensitive financial data

---

## UI Components

### Connection Status Card
```
┌─────────────────────────────────────────────────────────────┐
│  QUICKBOOKS ONLINE                                          │
│                                                             │
│  ✅ Connected                                               │
│  Company: Apex Roofing Solutions                           │
│  Last Sync: 2 minutes ago                                   │
│  Transactions: 1,247 synced                                │
│                                                             │
│  [Sync Now]  [Disconnect]                                   │
└─────────────────────────────────────────────────────────────┘
```

### Disconnected State
```
┌─────────────────────────────────────────────────────────────┐
│  QUICKBOOKS ONLINE                                          │
│                                                             │
│  ❌ Not Connected                                           │
│                                                             │
│  Connect your QuickBooks account to sync your              │
│  financial data automatically.                              │
│                                                             │
│  [Connect QuickBooks]                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Review Checklist

- [ ] OAuth flow completes successfully
- [ ] Tokens refresh automatically before expiration
- [ ] All transaction types sync correctly
- [ ] Deduplication prevents duplicate transactions
- [ ] Expense classification accuracy >85%
- [ ] Error handling for token expiration
- [ ] Connection status displays correctly
- [ ] Manual sync completes within 30 seconds
- [ ] Demo mode works without QBO connection
