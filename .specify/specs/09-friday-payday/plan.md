# Friday Payday - Technical Implementation Plan

> **Feature**: 09-friday-payday
> **Status**: Planned
> **Priority**: P0 (Core)
> **Last Updated**: 2026-01-02
> **Input**: specs/09-friday-payday/spec.md

---

## Technical Context

### Integration with CrewCFO Stack

Friday Payday extends the existing CrewCFO platform rather than creating a standalone application.

| Layer | Technology | CrewCFO Status | Friday Payday Extension |
|-------|------------|----------------|------------------------|
| Frontend | React/Vite | Existing | New tabs/components in dashboard |
| UI Components | Custom | Existing | Reuse existing + new AR components |
| Styling | Tailwind CSS | Existing | Continue existing patterns |
| Backend API | FastAPI | Existing | New `/api/friday-payday/*` routes |
| Database | Supabase (PostgreSQL) | Existing | New `fp_*` tables |
| Auth | Supabase Auth | Existing | Reuse tenant auth |
| QBO Integration | OAuth + Sync | Existing (08-qbo-integration) | Extend for invoice management |
| Automation | n8n | New | Self-hosted for dunning workflows |
| AI | Claude API | Existing | Message personalization |
| Email | SendGrid/Resend | Existing | Dunning communications |
| SMS | Twilio | New | SMS reminders |
| Payments | Stripe | New | Payment portal |

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    CREWCFO + FRIDAY PAYDAY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   EXISTING CREWCFO                                              │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  React Dashboard                                         │   │
│   │  • Owner Dashboard (cash, AR aging)                     │   │
│   │  • Finance Dashboard                                    │   │
│   │  • Valuation Dashboard                                  │   │
│   │  └─► NEW: Friday Payday Tab (invoices, dunning)         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│   EXISTING BACKEND           │   NEW: FRIDAY PAYDAY              │
│   ┌─────────────────────────┴───────────────────────────────┐   │
│   │                                                         │   │
│   │  FastAPI                    n8n (Railway)               │   │
│   │  ┌─────────────────────┐   ┌─────────────────────────┐  │   │
│   │  │ /api/qbo/* (exists) │   │ Dunning Workflows       │  │   │
│   │  │ /api/analytics/*    │◀─▶│ • daily-aging-check     │  │   │
│   │  │ /api/friday-payday/*│   │ • send-reminder         │  │   │
│   │  └─────────────────────┘   │ • friday-summary        │  │   │
│   │           │                 └─────────────────────────┘  │   │
│   │           │                          │                   │   │
│   └───────────┼──────────────────────────┼───────────────────┘   │
│               │                          │                        │
│   SUPABASE    │                          │                        │
│   ┌───────────┴──────────────────────────┴───────────────────┐   │
│   │  Existing Tables        New Tables (fp_*)                │   │
│   │  • tenants              • fp_customers                   │   │
│   │  • transactions         • fp_invoices                    │   │
│   │  • tenant_integrations  • fp_sequences                   │   │
│   │                         • fp_reminders                   │   │
│   │                         • fp_communication_log           │   │
│   └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│   EXTERNAL SERVICES                                              │
│   ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐       │
│   │QuickBooks │ │ SendGrid  │ │  Twilio   │ │  Stripe   │       │
│   │ (exists)  │ │ (exists)  │ │  (new)    │ │  (new)    │       │
│   └───────────┘ └───────────┘ └───────────┘ └───────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure Extensions

```
roofing-books-cfo/
├── frontend/
│   └── src/
│       └── components/
│           ├── FridayPayday/               # NEW: Friday Payday components
│           │   ├── FridayPaydayDashboard.tsx
│           │   ├── InvoiceList.tsx
│           │   ├── InvoiceDetail.tsx
│           │   ├── CustomerList.tsx
│           │   ├── DunningSequences.tsx
│           │   ├── ARAgingChart.tsx
│           │   └── CashCollectedCard.tsx
│           └── PaymentPortal/              # NEW: Public payment page
│               └── PaymentPage.tsx
│
├── src/
│   ├── services/
│   │   ├── friday_payday/                  # NEW: Friday Payday services
│   │   │   ├── __init__.py
│   │   │   ├── invoice_sync.py             # Sync invoices from QBO
│   │   │   ├── classification.py           # Invoice classification
│   │   │   ├── dunning_engine.py           # Sequence management
│   │   │   ├── messaging.py                # Email/SMS sending
│   │   │   ├── ai_personalization.py       # Claude message enhancement
│   │   │   └── analytics.py                # DSO, aging calculations
│   │   └── qbo/                            # Existing - extend
│   │       └── invoice_management.py       # NEW: Invoice-specific sync
│   │
│   └── api/
│       └── routes/
│           └── friday_payday.py            # NEW: API routes
│
├── n8n/                                    # NEW: n8n workflows
│   ├── workflows/
│   │   ├── daily-aging-check.json
│   │   ├── send-reminder.json
│   │   ├── quickbooks-sync.json
│   │   └── friday-summary.json
│   └── docker-compose.yml
│
└── supabase/
    └── migrations/
        └── 002_friday_payday_tables.sql    # NEW: fp_* tables
```

---

## Implementation Phases

### Phase 0: Foundation (Week 1)

**Objective:** Set up Friday Payday infrastructure within CrewCFO.

#### 0.1 Database Setup
- [ ] Create migration for `fp_*` tables (see data-model.md)
- [ ] Add `fp_settings` JSONB column to tenants table
- [ ] Configure RLS policies for all Friday Payday tables
- [ ] Create seed data for demo mode

#### 0.2 n8n Setup
- [ ] Deploy n8n on Railway (or local Docker for dev)
- [ ] Configure internal webhook authentication
- [ ] Create n8n credentials (SendGrid, Twilio)
- [ ] Test basic workflow execution
- [ ] Configure Supabase connection from n8n

#### 0.3 Frontend Tab
- [ ] Add "Collections" tab to CrewCFO dashboard
- [ ] Create empty FridayPaydayDashboard component
- [ ] Set up routing for invoice detail pages
- [ ] Ensure demo mode toggle works

#### 0.4 API Routes
- [ ] Create `/api/friday-payday/` route namespace
- [ ] Implement auth middleware (reuse existing)
- [ ] Set up basic CRUD endpoints scaffold

---

### Phase 1: Invoice Management (Week 2)

**Objective:** Sync and classify invoices from QuickBooks.

#### 1.1 Invoice Sync Extension
- [ ] Extend existing QBO sync to populate `fp_invoices`
- [ ] Map QBO Invoice fields to Friday Payday schema
- [ ] Calculate `days_overdue` from due_date
- [ ] Handle partial payments and balance updates
- [ ] Sync customers to `fp_customers`

#### 1.2 Invoice Classification
- [ ] Implement keyword-based classification engine
- [ ] Apply default payer_type based on rules
- [ ] Assign default dunning sequence
- [ ] Support manual override via API
- [ ] Store classification in `fp_invoices.payer_type`

**Classification Logic:**
```python
INSURANCE_KEYWORDS = ['insurance', 'claim', 'adjuster', 'supplement', 'aob']
DEPRECIATION_KEYWORDS = ['acv', 'rcv', 'depreciation', 'recoverable']
GC_KEYWORDS = ['general contractor', 'commercial', 'builder']

def classify_invoice(invoice: FPInvoice) -> PayerType:
    text = f"{invoice.memo} {invoice.line_items}".lower()

    if any(kw in text for kw in DEPRECIATION_KEYWORDS):
        return PayerType.DEPRECIATION_RECOVERY
    if any(kw in text for kw in INSURANCE_KEYWORDS):
        return PayerType.INSURANCE_PENDING
    if invoice.total_amount > 25000 or any(kw in text for kw in GC_KEYWORDS):
        return PayerType.GC_COMMERCIAL
    return PayerType.HOMEOWNER_DIRECT
```

#### 1.3 Invoice Dashboard
- [ ] Create InvoiceList component with filtering
- [ ] Implement AR aging buckets visualization
- [ ] Add search and pagination
- [ ] Create InvoiceDetail view with history

---

### Phase 2: Dunning Automation (Week 3-4)

**Objective:** Implement automated reminder sequences.

#### 2.1 Sequence Engine
- [ ] Create default sequences for each payer type
- [ ] Implement sequence step calculation
- [ ] Build n8n workflow: `daily-aging-check`
- [ ] Queue reminders based on schedule

**Default Sequences:**
```python
HOMEOWNER_SEQUENCE = [
    {"day": -3, "channel": "email", "template": "upcoming_due"},
    {"day": 0, "channel": "both", "template": "due_today"},
    {"day": 7, "channel": "email", "template": "first_reminder"},
    {"day": 14, "channel": "both", "template": "second_reminder"},
    {"day": 30, "channel": "email", "template": "escalation_warning"},
    {"day": 45, "channel": "both", "template": "final_notice"},
]

INSURANCE_SEQUENCE = [
    {"day": 14, "channel": "email", "template": "insurance_status_check"},
    {"day": 30, "channel": "email", "template": "insurance_reminder"},
    {"day": 45, "channel": "both", "template": "endorsement_reminder"},
    {"day": 60, "channel": "email", "template": "claim_escalation"},
]
```

#### 2.2 Email Reminders
- [ ] Build n8n workflow: `send-email-reminder`
- [ ] Configure SendGrid transactional templates
- [ ] Implement template variable replacement
- [ ] Track delivery status in `fp_communication_log`

#### 2.3 SMS Reminders
- [ ] Set up Twilio account and numbers
- [ ] Build n8n workflow: `send-sms-reminder`
- [ ] Implement short message templates
- [ ] Handle opt-out/suppression

#### 2.4 AI Personalization
- [ ] Create Claude API integration for messages
- [ ] Build message enhancement service
- [ ] Adjust tone based on payment history
- [ ] Implement template fallback

**AI Personalization:**
```python
async def personalize_message(template: str, context: dict) -> str:
    response = await anthropic.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{
            "role": "user",
            "content": f"""Personalize this payment reminder for a roofing customer.

            Template: {template}
            Customer Name: {context['customer_name']}
            Job Address: {context['property_address']}
            Amount: ${context['balance']:,.2f}
            Days Overdue: {context['days_overdue']}
            Payment History: {context['payment_history']}

            Guidelines:
            - Keep friendly but professional tone
            - Reference the roofing job if available
            - Include clear call to action
            - Keep under 150 words
            - Maintain {{payment_link}} variable"""
        }],
        max_tokens=500
    )
    return response.content[0].text
```

---

### Phase 3: Payment Collection (Week 5)

**Objective:** Enable online payment acceptance.

#### 3.1 Stripe Integration
- [ ] Set up Stripe account (or Connect for multi-tenant)
- [ ] Implement payment link generation per invoice
- [ ] Store payment links in `fp_invoices.payment_link`
- [ ] Configure Stripe webhooks

#### 3.2 Payment Portal
- [ ] Create public `/pay/{token}` page
- [ ] Display invoice details and amount
- [ ] Brand with tenant company info
- [ ] Accept credit card and ACH
- [ ] Show payment confirmation

#### 3.3 Payment Processing
- [ ] Build Stripe webhook handler
- [ ] Update `fp_invoices.balance` on payment
- [ ] Create `fp_payments` record
- [ ] Stop dunning sequence on full payment
- [ ] Post payment to QuickBooks

---

### Phase 4: Dashboard & Reporting (Week 6)

**Objective:** Analytics, weekly summary, and polish.

#### 4.1 Friday Cash Release Summary
- [ ] Build n8n workflow: `friday-summary`
- [ ] Calculate weekly collections metrics
- [ ] Design email template
- [ ] Schedule Friday 8 AM delivery (tenant timezone)

**Weekly Summary Content:**
```
FRIDAY PAYDAY - Your Weekly Cash Release

This week you collected: $14,750
Invoices paid: 7
vs last week: +$3,200 (+28%)

Top payments:
1. Johnson Roof Replacement - $8,500
2. Smith Insurance Final - $3,200
3. Garcia Repair - $1,450

Still outstanding: $42,000 across 23 invoices
[View Dashboard]
```

#### 4.2 DSO Analytics
- [ ] Implement DSO calculation service
- [ ] Build daily metrics aggregation
- [ ] Create trend visualization component
- [ ] Add industry benchmark comparison (83 days)

#### 4.3 Integration with Owner Dashboard
- [ ] Feed Friday Payday data into AR Aging widget
- [ ] Add "Collections" quick action from dashboard
- [ ] Show cash runway impact

#### 4.4 Production Hardening
- [ ] Error handling and retry logic
- [ ] Rate limiting for external APIs
- [ ] Logging and monitoring setup
- [ ] Security review (RLS, webhooks, tokens)

---

## Key Technical Decisions

### Decision 1: Extend vs. New Application

**Decision:** Integrate Friday Payday into existing CrewCFO dashboard.

**Rationale:**
- Leverages existing auth, tenants, and QBO integration
- Single login for contractors
- Shared data model (transactions → invoices)
- Lower deployment complexity
- Unified analytics and reporting

### Decision 2: n8n as Invisible Backend

**Decision:** Self-host n8n for workflow automation.

**Rationale:**
- Pre-built AR workflow templates available
- Visual debugging accelerates development
- Self-hosting avoids licensing costs
- Internal webhooks keep n8n invisible to users

**Implementation:**
```python
# FastAPI triggers n8n via internal webhook
async def trigger_reminder(invoice_id: UUID):
    await httpx.post(
        f"{settings.N8N_WEBHOOK_URL}/send-reminder",
        json={"invoice_id": str(invoice_id)},
        headers={"X-N8N-Token": settings.N8N_INTERNAL_TOKEN}
    )
```

### Decision 3: Invoice Source of Truth

**Decision:** `fp_invoices` syncs FROM `transactions` (which syncs from QBO).

**Rationale:**
- Avoids duplicate QBO sync logic
- Reuses existing transaction classification
- `fp_invoices` adds Friday Payday-specific fields
- Write-backs to QBO for payments

**Data Flow:**
```
QBO Invoices → transactions (08-qbo-integration)
            → fp_invoices (09-friday-payday)
            → Classification + Dunning
            → Payments → QBO
```

---

## Testing Strategy

### Unit Tests

**Coverage target:** 80%

**Focus areas:**
- Invoice classification logic
- DSO calculation
- Template variable replacement
- Sequence step progression
- Days overdue calculation

### Integration Tests

```python
async def test_invoice_sync(test_tenant):
    """Verify invoices sync from transactions to fp_invoices."""
    await sync_invoices_for_tenant(test_tenant.id)
    invoices = await get_fp_invoices(test_tenant.id)
    assert len(invoices) > 0
    assert all(inv.payer_type is not None for inv in invoices)

async def test_dunning_sequence_progression(test_invoice):
    """Verify sequence steps trigger correctly."""
    test_invoice.days_overdue = 7
    next_action = calculate_next_action(test_invoice)
    assert next_action.step == 3
    assert next_action.channel == "email"
```

### E2E Tests

1. Connect QBO → Invoices appear → Classification applied
2. Invoice overdue → Reminder sent → Logged
3. Payment received → Balance updated → Sequence stopped

---

## Security Checklist

- [ ] All secrets in environment variables
- [ ] QB tokens encrypted at rest (existing)
- [ ] RLS policies on all `fp_*` tables
- [ ] API rate limiting enabled
- [ ] Stripe webhook signatures validated
- [ ] Twilio request validation
- [ ] n8n internal auth token required
- [ ] Payment portal token expiration (24 hours)

---

## Progress Tracking

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0: Foundation | Not Started | |
| Phase 1: Invoice Management | Not Started | Depends on existing QBO sync |
| Phase 2: Dunning Automation | Not Started | Core value delivery |
| Phase 3: Payment Collection | Not Started | Stripe integration |
| Phase 4: Dashboard & Reporting | Not Started | Friday summary |

---

## Environment Variables (New)

```bash
# n8n Configuration
N8N_WEBHOOK_URL=https://n8n.crewcfo.com
N8N_INTERNAL_TOKEN=<secure-token>

# Twilio (SMS)
TWILIO_ACCOUNT_SID=<sid>
TWILIO_AUTH_TOKEN=<token>
TWILIO_PHONE_NUMBER=+1234567890

# Stripe (Payments)
STRIPE_SECRET_KEY=<sk_live_...>
STRIPE_WEBHOOK_SECRET=<whsec_...>

# AI Personalization (existing Claude config)
ANTHROPIC_API_KEY=<existing>
```

---

*Implementation plan version 1.0 - January 2026*
