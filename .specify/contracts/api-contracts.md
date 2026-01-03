# API Contracts

> **Version**: 1.0.0
> **Base URL**: `http://localhost:8000` (dev) | `https://api.crewcfo.com` (prod)
> **Last Updated**: 2026-01-02

---

## Table of Contents

1. [Authentication](#authentication)
2. [QuickBooks Integration](#quickbooks-integration)
3. [Transactions](#transactions)
4. [Finance & Cash Flow](#finance--cash-flow)
5. [Valuation](#valuation)
6. [Analytics](#analytics)
7. [Demo Mode](#demo-mode)
8. [Error Handling](#error-handling)

---

## Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer {jwt_token}
```

Tokens are obtained via Supabase Auth and contain:
- `sub`: User ID
- `tenant_id`: Tenant UUID (in user_metadata)
- `exp`: Expiration timestamp

---

## QuickBooks Integration

### Connect to QuickBooks
Initiates OAuth2 flow with Intuit.

```http
GET /auth/qbo/connect?tenant_id={tenant_id}&return_url={return_url}
```

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | string | Yes | Tenant UUID |
| return_url | string | No | URL to redirect after connection |

**Response**: Redirects to Intuit OAuth consent page

---

### OAuth Callback
Handles OAuth callback from Intuit.

```http
GET /auth/qbo/callback?code={code}&state={state}&realmId={realm_id}
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| code | string | Authorization code |
| state | string | State parameter (contains tenant_id) |
| realmId | string | QuickBooks company ID |

**Response**: Redirects to `return_url` with success/error

---

### Disconnect QuickBooks

```http
POST /auth/qbo/disconnect
Content-Type: application/json
Authorization: Bearer {token}

{
  "tenant_id": "uuid"
}
```

**Response**:
```json
{
  "success": true,
  "message": "QuickBooks disconnected successfully"
}
```

---

### Get Connection Status

```http
GET /api/qbo/status?tenant_id={tenant_id}
Authorization: Bearer {token}
```

**Response**:
```json
{
  "connected": true,
  "company_name": "Apex Roofing Solutions",
  "realm_id": "1234567890",
  "last_sync_at": "2025-01-15T10:30:00Z",
  "transaction_count": 1247,
  "token_expires_at": "2025-01-15T11:30:00Z",
  "is_active": true
}
```

---

### Sync Transactions

```http
POST /api/sync/qbo
Content-Type: application/json
Authorization: Bearer {token}

{
  "tenant_id": "uuid",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "purchases_synced": 523,
    "invoices_synced": 412,
    "deposits_synced": 312,
    "total_synced": 1247,
    "sync_duration_ms": 4532
  }
}
```

---

## Transactions

### List Transactions

```http
GET /api/transactions?tenant_id={tenant_id}&type={type}&status={status}&limit={limit}&offset={offset}
Authorization: Bearer {token}
```

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| tenant_id | string | Required | Tenant UUID |
| type | string | null | Filter by qbo_type (Purchase, Invoice, Deposit) |
| status | string | null | Filter by classification_status |
| limit | number | 100 | Max results |
| offset | number | 0 | Pagination offset |

**Response**:
```json
{
  "data": [
    {
      "id": "uuid",
      "qbo_id": "123",
      "qbo_type": "Purchase",
      "transaction_date": "2024-12-15",
      "total_amount": 1250.00,
      "vendor_name": "Home Depot",
      "memo": "Shingles for Smith job",
      "classification": "job_cost",
      "classification_status": "auto_classified",
      "confidence": 0.92,
      "category": "materials"
    }
  ],
  "total": 1247,
  "limit": 100,
  "offset": 0
}
```

---

### Classify Transaction

```http
POST /api/transactions/{transaction_id}/classify
Content-Type: application/json
Authorization: Bearer {token}

{
  "classification": "job_cost",
  "category": "materials",
  "confidence": 1.0,
  "job_id": "uuid"
}
```

**Response**:
```json
{
  "success": true,
  "transaction": {
    "id": "uuid",
    "classification": "job_cost",
    "classification_status": "approved",
    "category": "materials",
    "confidence": 1.0
  }
}
```

---

### Batch Classify Transactions

```http
POST /api/transactions/classify/batch
Content-Type: application/json
Authorization: Bearer {token}

{
  "transactions": [
    {
      "id": "uuid1",
      "classification": "overhead",
      "category": "insurance"
    },
    {
      "id": "uuid2",
      "classification": "job_cost",
      "category": "materials"
    }
  ]
}
```

---

## Finance & Cash Flow

### Get Cash Position

```http
GET /api/cash/position?tenant_id={tenant_id}
Authorization: Bearer {token}
```

**Response**:
```json
{
  "total_cash": 187500,
  "runway_weeks": 14,
  "change_wow": 0.12,
  "as_of_date": "2024-12-31"
}
```

---

### Get Cash Forecast

```http
GET /api/finance/cash-forecast?tenant_id={tenant_id}&scenario={scenario}&weeks={weeks}
Authorization: Bearer {token}
```

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| tenant_id | string | Required | Tenant UUID |
| scenario | string | "base" | Scenario: base, optimistic, pessimistic |
| weeks | number | 13 | Forecast horizon in weeks |

**Response**:
```json
{
  "data": {
    "forecast_date": "2024-12-31T00:00:00Z",
    "scenario": "base",
    "starting_cash": 187500,
    "ending_cash": 285000,
    "min_cash": 145000,
    "min_cash_week": 6,
    "runway_weeks": 14,
    "ar_total": 251500,
    "ap_total": 89000,
    "summary": {
      "total_inflows": 546000,
      "total_outflows": 448500,
      "net_change": 97500
    },
    "weekly_forecast": [
      {
        "week_number": 1,
        "week_start": "2025-01-06",
        "week_end": "2025-01-12",
        "starting_cash": 187500,
        "ending_cash": 195000,
        "net_cash_flow": 7500,
        "inflows": { "collections": 42000, "total": 42000 },
        "outflows": { "ap_payments": 28000, "recurring_expenses": 6500, "total": 34500 }
      }
    ]
  }
}
```

---

### Get All Forecast Scenarios

```http
GET /api/finance/cash-forecast/all-scenarios?tenant_id={tenant_id}
Authorization: Bearer {token}
```

**Response**:
```json
{
  "data": {
    "base": { /* CashForecast */ },
    "optimistic": { /* CashForecast */ },
    "pessimistic": { /* CashForecast */ }
  }
}
```

---

### Get Cash Alert Status

```http
GET /api/finance/cash-forecast/alert?tenant_id={tenant_id}
Authorization: Bearer {token}
```

**Response**:
```json
{
  "data": {
    "status": "good",
    "color": "green",
    "message": "Cash position is healthy with 14+ weeks of runway",
    "runway_weeks": 14,
    "current_cash": 187500,
    "min_projected_cash": 145000,
    "min_cash_week": 6,
    "recommendations": [
      "Consider accelerating collection on $18,000 in 90+ day AR",
      "Review upcoming $40,000 AP payment - negotiate extended terms if needed"
    ]
  }
}
```

---

### Get AP Aging

```http
GET /api/finance/ap/aging?tenant_id={tenant_id}
Authorization: Bearer {token}
```

**Response**:
```json
{
  "data": {
    "aging": {
      "current": 35000,
      "1-30": 28000,
      "31-60": 15000,
      "61-90": 8000,
      "90+": 3000
    },
    "total": 89000,
    "overdue": 11000,
    "overdue_pct": 12.4
  }
}
```

---

### Get Budget Variance

```http
GET /api/finance/budget/variance?tenant_id={tenant_id}&period={period}
Authorization: Bearer {token}
```

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| period | string | Current month | Period in YYYY-MM format |

**Response**:
```json
{
  "data": {
    "period": "December 2024",
    "categories": [
      {
        "category": "materials",
        "budget": 125000,
        "actual": 118500,
        "variance": -6500,
        "variance_pct": -5.2,
        "status": "under"
      }
    ],
    "totals": {
      "budget": 305000,
      "actual": 304700,
      "variance": -300,
      "variance_pct": -0.1
    }
  }
}
```

---

### Create Budget

```http
POST /api/finance/budget
Content-Type: application/json
Authorization: Bearer {token}

{
  "tenant_id": "uuid",
  "period": "2025-01",
  "categories": {
    "materials": 125000,
    "labor": 95000,
    "equipment_rental": 12000,
    "subcontractors": 45000,
    "overhead": 28000
  }
}
```

---

## Valuation

### Get Latest Valuation Snapshot

```http
GET /api/valuation/snapshot?tenant_id={tenant_id}
Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "as_of_date": "2024-12-31",
    "ttm_revenue": 3500000,
    "ttm_sde": 350000,
    "ttm_ebitda": 245000,
    "tier": "below_avg",
    "multiple_low": 2.5,
    "multiple_high": 3.5,
    "ev_low": 612500,
    "ev_high": 857500,
    "confidence_score": 72,
    "created_at": "2024-12-31T10:00:00Z"
  }
}
```

---

### Create Valuation Snapshot

```http
POST /api/valuation/snapshot
Content-Type: application/json
Authorization: Bearer {token}

{
  "tenant_id": "uuid"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "as_of_date": "2024-12-31",
    "ttm_revenue": 3500000,
    "ttm_ebitda": 245000,
    "tier": "below_avg",
    "multiple_low": 2.5,
    "multiple_high": 3.5,
    "ev_low": 612500,
    "ev_high": 857500
  }
}
```

---

### Get Driver Scores

```http
GET /api/valuation/drivers?tenant_id={tenant_id}
Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "driver_key": "management_independence",
      "score": 45,
      "weight": 0.25,
      "factors": {
        "owner_hours_per_week": 50,
        "has_operations_manager": false,
        "documented_sops": false
      }
    },
    {
      "driver_key": "financial_records",
      "score": 72,
      "weight": 0.20,
      "factors": {
        "monthly_close_process": true,
        "job_costing_accuracy": 0.85
      }
    }
  ]
}
```

---

### Run Simulation

```http
POST /api/valuation/simulate
Content-Type: application/json
Authorization: Bearer {token}

{
  "levers": {
    "recurring_revenue_delta": 0.25,
    "margin_delta": 0.03,
    "owner_hours_delta": -20,
    "productivity_delta": 0.10
  }
}
```

**Response**:
```json
{
  "projected_ebitda": 425000,
  "projected_multiple": 5.2,
  "projected_ev_low": 1912500,
  "projected_ev_high": 2422500
}
```

---

### Get Valuation Roadmap

```http
GET /api/valuation/roadmap?tenant_id={tenant_id}&driver={driver}&status={status}
Authorization: Bearer {token}
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| driver | string | Filter by driver_key |
| status | string | Filter by status |

**Response**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "uuid",
        "driver_key": "management_independence",
        "title": "Document Standard Operating Procedures",
        "description": "Create comprehensive SOPs for all key business processes",
        "category": "strategic",
        "priority": "high",
        "status": "in_progress",
        "expected_impact_ev": 150000,
        "effort_level": "medium",
        "due_date": "2025-02-15"
      }
    ],
    "summary": {
      "total_items": 8,
      "by_status": { "pending": 4, "in_progress": 3, "completed": 1 },
      "total_potential_ev": 1375000
    }
  }
}
```

---

### Update Roadmap Item

```http
PATCH /api/valuation/roadmap/{item_id}
Content-Type: application/json
Authorization: Bearer {token}

{
  "status": "completed",
  "completed_at": "2025-01-15T10:30:00Z"
}
```

---

### Generate Shock Report

```http
POST /api/valuation/shock-report
Content-Type: application/json
Authorization: Bearer {token}

{
  "tenant_id": "uuid"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "report": {
      "id": "uuid",
      "generated_at": "2024-12-31T10:00:00Z",
      "owner_view": {
        "revenue": 3500000,
        "ebitda": 350000,
        "owner_comp": 180000,
        "addbacks": 280000,
        "expected_multiple": 10.0,
        "expected_valuation": 3500000
      },
      "buyer_view": {
        "defensible_ebitda": 245000,
        "defensible_sde": 395000,
        "multiple_low": 2.5,
        "multiple_high": 3.5,
        "valuation_low": 612500,
        "valuation_high": 857500
      },
      "gap_analysis": {
        "ebitda_haircut": 105000,
        "multiple_penalty": 6.5,
        "value_gap": 2520000,
        "value_gap_percentage": 72
      },
      "tier": "below_avg",
      "confidence_score": 78,
      "total_recoverable_value": 1080000
    },
    "ebitda_adjustments": [
      {
        "id": "uuid",
        "type": "owner_compensation",
        "category": "partial",
        "description": "Owner salary of $180K - $60K above market rate",
        "amount": 180000,
        "accepted_amount": 120000,
        "buyer_concern": "Market rate for GM is $110-130K",
        "is_recoverable": true,
        "remediation_action": "Document market-rate salary"
      }
    ],
    "multiple_penalties": [
      {
        "id": "uuid",
        "driver_key": "management_independence",
        "penalty_amount": 2.0,
        "reason": "Owner-dependent operations",
        "remediation_action": "Hire operations manager"
      }
    ],
    "value_unlocks": [
      {
        "id": "uuid",
        "priority_rank": 1,
        "title": "Reduce Owner Hours",
        "ebitda_impact": 0,
        "multiple_impact": 1.5,
        "ev_impact": 367500,
        "effort_level": "high"
      }
    ]
  }
}
```

---

### Get Latest Shock Report

```http
GET /api/valuation/shock-report/latest?tenant_id={tenant_id}
Authorization: Bearer {token}
```

---

### Get Exit Readiness

```http
GET /api/valuation/exit-readiness?tenant_id={tenant_id}
Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "checklist": [
      {
        "id": "financial-statements",
        "category": "Financial Statements",
        "title": "3-5 Years of Financial Statements",
        "priority": "critical",
        "status": "complete",
        "documents": [
          {
            "id": "uuid",
            "file_name": "2023-pnl.pdf",
            "size_bytes": 245678,
            "uploaded_at": "2024-01-15T10:00:00Z"
          }
        ]
      }
    ],
    "summary": {
      "readiness_score": 43,
      "items_complete": 3,
      "items_total": 7,
      "critical_missing": ["Tax Returns", "Asset List"]
    }
  }
}
```

---

### Upload Exit Readiness Document

```http
POST /api/valuation/exit-readiness/upload
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: [binary]
checklist_item_id: "financial-statements"
tenant_id: "uuid"
```

**Response**:
```json
{
  "success": true,
  "data": {
    "doc_id": "uuid",
    "file_name": "2023-pnl.pdf",
    "storage_path": "deal-room/tenant-123/financial-statements/2023-pnl.pdf",
    "size_bytes": 245678
  }
}
```

---

### Delete Exit Readiness Document

```http
DELETE /api/valuation/exit-readiness/files/{doc_id}
Authorization: Bearer {token}
```

---

## Analytics

### Get P&L Analytics

```http
GET /api/analytics/pnl?tenant_id={tenant_id}&start_date={start}&end_date={end}
Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "period": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    },
    "summary": {
      "total_revenue": 3500000,
      "total_cogs": 2275000,
      "gross_profit": 1225000,
      "gross_margin_pct": 35,
      "total_overhead": 980000,
      "net_income": 245000,
      "net_margin_pct": 7
    },
    "monthly": {
      "revenue": 291667,
      "cogs": 189583,
      "overhead": 81667,
      "net_income": 20417
    },
    "expense_breakdown": {
      "cogs": {
        "total": 2275000,
        "items": {
          "materials": 1225000,
          "direct_labor": 630000,
          "subcontractors": 280000,
          "equipment": 140000
        }
      },
      "overhead": {
        "total": 980000,
        "items": {
          "payroll": 420000,
          "insurance": 168000,
          "office": 144000,
          "marketing": 120000,
          "utilities": 72000,
          "professional_fees": 56000
        }
      }
    },
    "break_even": {
      "current_margin": {
        "margin": 0.35,
        "monthly": 233333,
        "annual": 2800000
      },
      "scenarios": {
        "25%": { "margin": 0.25, "monthly_break_even": 326667, "annual_break_even": 3920000 },
        "30%": { "margin": 0.30, "monthly_break_even": 272222, "annual_break_even": 3266667 },
        "35%": { "margin": 0.35, "monthly_break_even": 233333, "annual_break_even": 2800000 },
        "40%": { "margin": 0.40, "monthly_break_even": 204167, "annual_break_even": 2450000 }
      }
    },
    "profit_leaks": [
      {
        "category": "Gross Margin",
        "issue": "Margin is below industry benchmark",
        "current_ratio": 0.35,
        "benchmark": 0.40,
        "impact": "5% below target",
        "severity": "medium",
        "recommendation": "Review pricing and job costing"
      }
    ]
  }
}
```

---

### Get Break-Even Analysis

```http
GET /api/analytics/break-even?tenant_id={tenant_id}
Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "current_margin": 0.35,
    "monthly_overhead": 81667,
    "monthly_break_even": 233333,
    "annual_break_even": 2800000,
    "current_revenue": 3500000,
    "cushion": 700000,
    "cushion_pct": 20,
    "scenarios": {
      "25%": { "monthly": 326667, "annual": 3920000 },
      "30%": { "monthly": 272222, "annual": 3266667 },
      "35%": { "monthly": 233333, "annual": 2800000 },
      "40%": { "monthly": 204167, "annual": 2450000 }
    }
  }
}
```

---

### Get Profit Leaks

```http
GET /api/analytics/profit-leaks?tenant_id={tenant_id}
Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "leaks": [
      {
        "category": "Gross Margin",
        "issue": "Gross margin is below healthy threshold",
        "current_ratio": 0.22,
        "benchmark": 0.35,
        "impact": "13% below target",
        "severity": "high",
        "recommendation": "Review pricing strategy and job costing"
      },
      {
        "category": "Labor Ratio",
        "issue": "Labor costs are elevated",
        "current_ratio": 0.38,
        "benchmark": 0.30,
        "impact": "8% above target",
        "severity": "medium",
        "recommendation": "Improve crew productivity and scheduling"
      }
    ],
    "total_leak_impact": 182000,
    "summary": {
      "high_severity": 1,
      "medium_severity": 1,
      "low_severity": 0
    }
  }
}
```

---

## Demo Mode

Demo endpoints provide realistic sample data for Apex Roofing Solutions ($3.5M contractor).

### Get Demo Dashboard

```http
GET /api/demo/dashboard
```

### Get Demo Finance Data

```http
GET /api/demo/finance
```

### Get Demo Shock Report

```http
GET /api/demo/shock-report
```

### Get Demo Simulator Data

```http
GET /api/demo/simulator
```

### Get Demo Exit Readiness

```http
GET /api/demo/exit-readiness
```

### Get Demo Roadmap

```http
GET /api/demo/roadmap
```

### Get Demo Profit Leaks

```http
GET /api/demo/profit-leaks
```

---

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { /* Optional additional context */ }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | User lacks permission for this resource |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Invalid request parameters |
| `QBO_NOT_CONNECTED` | 400 | QuickBooks not connected |
| `QBO_TOKEN_EXPIRED` | 401 | QuickBooks token needs refresh |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

### QBO-Specific Errors

```json
{
  "success": false,
  "error": {
    "code": "QBO_TOKEN_EXPIRED",
    "message": "QuickBooks connection has expired. Please reconnect.",
    "details": {
      "reconnect_url": "/auth/qbo/connect?tenant_id=uuid"
    }
  }
}
```

---

## Rate Limits

| Endpoint Category | Limit |
|-------------------|-------|
| Authentication | 10/min |
| QBO Sync | 5/min |
| Analytics | 60/min |
| Valuations | 30/min |
| Other | 120/min |

---

## Webhooks (Future)

Planned webhook events for external integrations:

| Event | Trigger |
|-------|---------|
| `qbo.connected` | QuickBooks successfully connected |
| `qbo.disconnected` | QuickBooks disconnected |
| `sync.completed` | Transaction sync completed |
| `valuation.updated` | New valuation snapshot created |
| `shock_report.generated` | New shock report generated |

---

## SDK Examples

### JavaScript/TypeScript

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Get user session
const { data: { session } } = await supabase.auth.getSession()
const accessToken = session?.access_token

// Fetch valuation snapshot
const response = await fetch(`${API_BASE_URL}/api/valuation/snapshot?tenant_id=${tenantId}`, {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
})

const { data } = await response.json()
console.log('EV Range:', data.ev_low, '-', data.ev_high)
```

### Python

```python
import requests

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Run simulation
response = requests.post(
    f'{API_BASE_URL}/api/valuation/simulate',
    headers=headers,
    json={
        'levers': {
            'recurring_revenue_delta': 0.25,
            'margin_delta': 0.03,
            'owner_hours_delta': -20,
            'productivity_delta': 0.10
        }
    }
)

result = response.json()
print(f"Projected EV: ${result['projected_ev_low']:,} - ${result['projected_ev_high']:,}")
```

---

## Changelog

### v1.0.0 (2026-01-02)
- Initial API contracts documentation
- Full coverage of all endpoints
- Request/response schemas documented
