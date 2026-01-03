# Friday Payday - Implementation Tasks

> **Feature**: 09-friday-payday
> **Status**: Planned
> **Priority**: P0 (Core)
> **Last Updated**: 2026-01-02
> **Input**: plan.md, spec.md, data-model.md
> **Prerequisites**: Existing CrewCFO platform with QBO integration

---

## Task Organization

Tasks are organized by:
- **Phase** - Foundation → Invoice Management → Dunning → Payments → Reporting
- **[P]** - Can run in parallel (different files, no dependencies)
- **[D:X]** - Depends on task X completing first
- **[EXT]** - Extends existing CrewCFO code

---

## Phase 0: Foundation

**Purpose:** Set up Friday Payday infrastructure within existing CrewCFO platform.

### 0.1 Database Setup

```
Task 0.1.1: Create Friday Payday migration
  Files: supabase/migrations/002_friday_payday_tables.sql
  Content: All fp_* tables from data-model.md

Task 0.1.2 [D:0.1.1]: Add fp_settings to tenants table
  Files: supabase/migrations/002_friday_payday_tables.sql
  Content: ALTER TABLE tenants ADD COLUMN fp_settings JSONB

Task 0.1.3 [D:0.1.1]: Create RLS policies
  Files: supabase/migrations/002_friday_payday_tables.sql
  Content: Policies for all fp_* tables using tenant_id

Task 0.1.4 [D:0.1.3]: Create default sequence seed data
  Files: supabase/migrations/002_friday_payday_tables.sql
  Content: Default sequences for each payer type

Task 0.1.5 [D:0.1.4]: Create message template seed data
  Files: supabase/migrations/002_friday_payday_tables.sql
  Content: Default email/SMS templates
```

**Checkpoint 0.1:** Migration runs, fp_* tables created, demo data loads

---

### 0.2 n8n Automation Setup

```
Task 0.2.1: Create n8n Docker configuration
  Files:
    - n8n/docker-compose.yml
    - n8n/.env.example

Task 0.2.2 [D:0.2.1]: Deploy n8n (Railway or local Docker)
  Actions:
    - Create Railway project OR
    - Add n8n to docker-compose.override.yml
    - Configure domain/internal access

Task 0.2.3 [D:0.2.2]: Configure n8n credentials
  Actions:
    - Add SendGrid API key (reuse existing)
    - Add Twilio credentials (new)
    - Add Supabase connection
    - Add internal webhook token

Task 0.2.4 [D:0.2.3]: Create base webhook handler workflow
  Files: n8n/workflows/base-webhook-handler.json
```

**Checkpoint 0.2:** n8n accessible, can trigger test webhook

---

### 0.3 Frontend Tab & Routing

```
Task 0.3.1: Add Collections tab to dashboard
  Files: frontend/src/components/Dashboard.tsx [EXT]
  Changes: Add new tab alongside existing tabs

Task 0.3.2 [D:0.3.1]: Create FridayPaydayDashboard component
  Files: frontend/src/components/FridayPayday/FridayPaydayDashboard.tsx
  Content: Main container component

Task 0.3.3 [P]: Create demo mode data for Friday Payday
  Files: frontend/src/components/FridayPayday/demoData.ts
  Content: Mock invoices, customers, sequences, metrics
```

**Checkpoint 0.3:** Collections tab appears, demo data displays

---

### 0.4 API Routes

```
Task 0.4.1: Create Friday Payday route file
  Files: src/api/routes/friday_payday.py
  Content: Router with auth dependency

Task 0.4.2 [D:0.4.1]: Register routes in main.py
  Files: src/main.py [EXT]
  Content: Add friday_payday router

Task 0.4.3 [D:0.4.2]: Create base schemas
  Files: src/services/friday_payday/schemas.py
  Content: Pydantic models for invoices, customers, sequences
```

**Checkpoint 0.4:** /api/friday-payday/* routes respond

---

## Phase 1: Invoice Management

**Purpose:** Sync invoices from existing QBO integration and classify them.

### 1.1 Invoice Sync Extension

```
Task 1.1.1: Create fp_invoices sync from transactions
  Files: src/services/friday_payday/invoice_sync.py
  Content: Sync QBO invoices from transactions table to fp_invoices

Task 1.1.2 [D:1.1.1]: Create fp_customers sync
  Files: src/services/friday_payday/customer_sync.py
  Content: Sync customers from QBO data to fp_customers

Task 1.1.3 [D:1.1.1]: Add sync trigger on QBO sync completion
  Files: src/services/qbo/sync.py [EXT]
  Changes: Call Friday Payday sync after transaction sync

Task 1.1.4 [D:1.1.3]: Create sync status tracking
  Files: src/services/friday_payday/invoice_sync.py
  Content: Update fp_settings with last_sync_at
```

**Checkpoint 1.1:** QBO sync populates fp_invoices

---

### 1.2 Invoice Classification

```
Task 1.2.1: Create classification engine
  Files: src/services/friday_payday/classification.py
  Content:
    - PayerType enum
    - Keyword matching logic
    - Default sequence assignment

Task 1.2.2 [D:1.2.1]: Integrate classification into sync
  Files: src/services/friday_payday/invoice_sync.py [EXT]
  Changes: Apply classification on sync

Task 1.2.3 [D:1.2.2]: Create classification override endpoint
  Files: src/api/routes/friday_payday.py
  Content: PATCH /invoices/{id} with payer_type
```

**Checkpoint 1.2:** New invoices auto-classified, can override

---

### 1.3 Invoice Dashboard UI

```
Task 1.3.1: Create InvoiceList component
  Files: frontend/src/components/FridayPayday/InvoiceList.tsx
  Content: Paginated table with status, payer type, amount, days overdue

Task 1.3.2 [D:1.3.1]: Create invoice filters
  Files: frontend/src/components/FridayPayday/InvoiceFilters.tsx
  Content: Status filter, payer type filter, date range

Task 1.3.3 [D:1.3.1]: Create InvoiceDetail component
  Files: frontend/src/components/FridayPayday/InvoiceDetail.tsx
  Content: Invoice info, communication timeline, actions

Task 1.3.4 [D:1.3.3]: Create action buttons
  Files: frontend/src/components/FridayPayday/InvoiceActions.tsx
  Content: Send reminder, Pause, Resume, Mark disputed

Task 1.3.5: Create invoice API endpoints
  Files: src/api/routes/friday_payday.py
  Content:
    - GET /invoices (list with filters)
    - GET /invoices/{id} (detail)
    - PATCH /invoices/{id} (update)
    - POST /invoices/{id}/remind (send now)
    - POST /invoices/{id}/pause
    - POST /invoices/{id}/resume
```

**Checkpoint 1.3:** Invoice list displays, detail view works, actions work

---

### 1.4 AR Aging Integration

```
Task 1.4.1: Create AR aging analytics endpoint
  Files: src/api/routes/friday_payday.py
  Content: GET /analytics/aging

Task 1.4.2 [D:1.4.1]: Create ARAgingChart component
  Files: frontend/src/components/FridayPayday/ARAgingChart.tsx
  Content: Horizontal bar chart by bucket

Task 1.4.3 [D:1.4.2]: Integrate with Owner Dashboard
  Files: frontend/src/components/OwnerDashboard.tsx [EXT]
  Changes: Use Friday Payday AR data if available
```

**Checkpoint 1.4:** AR aging shows in both dashboards

---

## Phase 2: Dunning Automation

**Purpose:** Implement automated reminder sequences.

### 2.1 Sequence Engine

```
Task 2.1.1: Create sequence configuration endpoints
  Files: src/api/routes/friday_payday.py
  Content:
    - GET /sequences
    - GET /sequences/{id}
    - POST /sequences
    - PATCH /sequences/{id}

Task 2.1.2 [D:2.1.1]: Create dunning engine service
  Files: src/services/friday_payday/dunning_engine.py
  Content:
    - Calculate next action for invoice
    - Check if action is due
    - Queue reminder creation

Task 2.1.3 [D:2.1.2]: Create n8n daily-aging-check workflow
  Files: n8n/workflows/daily-aging-check.json
  Flow:
    1. Get active tenants with Friday Payday
    2. For each: get invoices due for action
    3. Call API to queue reminders

Task 2.1.4 [D:2.1.3]: Create reminder queue endpoint
  Files: src/api/routes/friday_payday.py
  Content: POST /reminders/queue
```

**Checkpoint 2.1:** Daily check identifies due reminders

---

### 2.2 Email Reminders

```
Task 2.2.1: Create messaging service
  Files: src/services/friday_payday/messaging.py
  Content:
    - SendGrid email sending
    - Template variable replacement
    - Delivery tracking

Task 2.2.2 [D:2.2.1]: Create n8n send-reminder workflow
  Files: n8n/workflows/send-reminder.json
  Flow:
    1. Receive reminder_id
    2. Fetch context (invoice, customer, company)
    3. Apply template
    4. Optionally personalize with AI
    5. Send via SendGrid/Twilio
    6. Log to communication_log

Task 2.2.3 [D:2.2.2]: Create template management
  Files: src/api/routes/friday_payday.py
  Content:
    - GET /templates
    - POST /templates
    - PATCH /templates/{id}
```

**Checkpoint 2.2:** Email reminders send on schedule

---

### 2.3 SMS Reminders

```
Task 2.3.1: Add Twilio to messaging service
  Files: src/services/friday_payday/messaging.py [EXT]
  Content: Twilio SMS sending

Task 2.3.2 [D:2.3.1]: Update n8n workflow for SMS
  Files: n8n/workflows/send-reminder.json [EXT]
  Changes: Branch for SMS channel

Task 2.3.3: Create opt-out handling
  Files: src/api/routes/friday_payday.py
  Content: POST /customers/{id}/suppress
```

**Checkpoint 2.3:** SMS reminders send, opt-out works

---

### 2.4 AI Personalization

```
Task 2.4.1: Create AI personalization service
  Files: src/services/friday_payday/ai_personalization.py
  Content:
    - Claude API integration
    - Message enhancement prompts
    - Fallback to template

Task 2.4.2 [D:2.4.1]: Integrate into messaging
  Files: src/services/friday_payday/messaging.py [EXT]
  Changes: Optional AI enhancement step

Task 2.4.3 [D:2.4.2]: Add personalization setting
  Files: src/api/routes/friday_payday.py
  Content: Toggle in tenant fp_settings
```

**Checkpoint 2.4:** Messages are personalized when enabled

---

## Phase 3: Payment Collection

**Purpose:** Enable online payment acceptance.

### 3.1 Stripe Integration

```
Task 3.1.1: Add Stripe configuration
  Files: src/services/friday_payday/stripe_service.py
  Content:
    - Stripe client setup
    - Payment link generation
    - Webhook signature verification

Task 3.1.2 [D:3.1.1]: Generate payment links
  Files: src/services/friday_payday/invoice_sync.py [EXT]
  Changes: Generate payment link on invoice creation

Task 3.1.3 [D:3.1.2]: Include links in reminders
  Files: src/services/friday_payday/messaging.py [EXT]
  Changes: Add {payment_link} to context
```

**Checkpoint 3.1:** Payment links generated and included in messages

---

### 3.2 Payment Portal

```
Task 3.2.1: Create payment portal page
  Files: frontend/src/components/PaymentPortal/PaymentPage.tsx
  Content: Public page with Stripe Elements

Task 3.2.2 [D:3.2.1]: Create payment token validation
  Files: src/api/routes/friday_payday.py
  Content: GET /payments/portal/{token}

Task 3.2.3 [D:3.2.2]: Create payment confirmation
  Files: frontend/src/components/PaymentPortal/PaymentConfirmation.tsx
  Content: Success page with receipt

Task 3.2.4 [D:3.2.1]: Add routing for public payment page
  Files: frontend/src/App.tsx [EXT]
  Changes: Route /pay/:token
```

**Checkpoint 3.2:** Payment portal accepts payments

---

### 3.3 Payment Processing

```
Task 3.3.1: Create Stripe webhook handler
  Files: src/api/routes/friday_payday.py
  Content: POST /webhooks/stripe

Task 3.3.2 [D:3.3.1]: Create payment reconciliation
  Files: src/services/friday_payday/payment_processing.py
  Content:
    - Create fp_payments record
    - Update fp_invoices balance
    - Stop dunning sequence

Task 3.3.3 [D:3.3.2]: Post payment to QuickBooks
  Files: src/services/friday_payday/payment_processing.py [EXT]
  Content: Use existing QBO integration to post payment

Task 3.3.4 [D:3.3.3]: Send payment confirmation
  Files: src/services/friday_payday/messaging.py [EXT]
  Content: Payment received template
```

**Checkpoint 3.3:** Payments update invoice, post to QBO, sequence stops

---

## Phase 4: Dashboard & Reporting

**Purpose:** Analytics and weekly summary.

### 4.1 Weekly Summary Email

```
Task 4.1.1: Create weekly metrics service
  Files: src/services/friday_payday/analytics.py
  Content:
    - Cash collected this week
    - Invoice count paid
    - Week-over-week comparison
    - Top payments

Task 4.1.2 [D:4.1.1]: Create summary email template
  Files: src/services/friday_payday/templates/weekly_summary.html
  Content: Friday Cash Release email HTML

Task 4.1.3 [D:4.1.2]: Create n8n Friday workflow
  Files: n8n/workflows/friday-summary.json
  Flow:
    1. Trigger Friday 8 AM
    2. For each tenant: calculate metrics
    3. Send summary email
```

**Checkpoint 4.1:** Friday emails send with weekly metrics

---

### 4.2 DSO Analytics

```
Task 4.2.1: Create DSO calculation service
  Files: src/services/friday_payday/analytics.py [EXT]
  Content:
    - Current DSO
    - DSO trend (30/60/90 day)
    - Industry benchmark comparison

Task 4.2.2 [D:4.2.1]: Create analytics endpoints
  Files: src/api/routes/friday_payday.py
  Content:
    - GET /analytics/dso
    - GET /analytics/collected
    - GET /analytics/trends

Task 4.2.3 [D:4.2.2]: Create analytics dashboard components
  Files:
    - frontend/src/components/FridayPayday/DSOChart.tsx
    - frontend/src/components/FridayPayday/CollectedChart.tsx
    - frontend/src/components/FridayPayday/TrendChart.tsx
```

**Checkpoint 4.2:** Analytics charts display DSO and trends

---

### 4.3 Customer Management UI

```
Task 4.3.1: Create CustomerList component
  Files: frontend/src/components/FridayPayday/CustomerList.tsx
  Content: Customer table with AR totals, contact info

Task 4.3.2 [D:4.3.1]: Create CustomerDetail component
  Files: frontend/src/components/FridayPayday/CustomerDetail.tsx
  Content: Invoices, communication history, preferences

Task 4.3.3 [D:4.3.2]: Create suppression dialog
  Files: frontend/src/components/FridayPayday/SuppressionDialog.tsx
  Content: Reason selection, confirmation
```

**Checkpoint 4.3:** Customer list and detail views work

---

### 4.4 Sequence Configuration UI

```
Task 4.4.1: Create SequenceList component
  Files: frontend/src/components/FridayPayday/SequenceList.tsx
  Content: List of dunning sequences by payer type

Task 4.4.2 [D:4.4.1]: Create SequenceEditor component
  Files: frontend/src/components/FridayPayday/SequenceEditor.tsx
  Content: Edit steps, timing, channels, templates

Task 4.4.3 [D:4.4.2]: Create TemplateEditor component
  Files: frontend/src/components/FridayPayday/TemplateEditor.tsx
  Content: Edit email/SMS templates with variables
```

**Checkpoint 4.4:** Sequences and templates configurable

---

## Phase 5: Production Hardening

**Purpose:** Prepare for production launch.

### 5.1 Error Handling & Logging

```
Task 5.1.1: Add structured logging
  Files: src/services/friday_payday/*.py
  Changes: Add logging to all services

Task 5.1.2 [P]: Add error handling
  Files: src/api/routes/friday_payday.py
  Changes: Proper error responses, retry logic

Task 5.1.3 [P]: Add Sentry integration
  Files: src/main.py [EXT]
  Changes: Capture Friday Payday errors
```

---

### 5.2 Security

```
Task 5.2.1: Verify RLS policies
  Actions: Test isolation between tenants

Task 5.2.2 [P]: Add rate limiting
  Files: src/api/routes/friday_payday.py
  Changes: Rate limit public endpoints

Task 5.2.3 [P]: Validate webhook signatures
  Files: src/api/routes/friday_payday.py
  Changes: Stripe, Twilio signature validation

Task 5.2.4 [P]: Audit token handling
  Actions: Review payment portal token security
```

---

### 5.3 Testing

```
Task 5.3.1: Create unit tests
  Files: tests/friday_payday/
  Content: Classification, DSO calculation, sequence logic

Task 5.3.2 [D:5.3.1]: Create integration tests
  Files: tests/friday_payday/
  Content: API endpoint tests, sync tests

Task 5.3.3 [D:5.3.2]: Create E2E tests
  Files: tests/e2e/friday_payday.spec.ts
  Content: Full flow tests
```

---

## Final Checklist

### Pre-Launch

- [ ] All fp_* tables created and migrated
- [ ] n8n deployed and workflows tested
- [ ] Invoice sync working from QBO
- [ ] Classification accuracy > 85%
- [ ] Email reminders sending
- [ ] SMS reminders sending
- [ ] Payment portal accepting payments
- [ ] Friday summary email working
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Security review complete

### Launch Day

- [ ] Production environment configured
- [ ] All environment variables set
- [ ] n8n production credentials configured
- [ ] Stripe production keys active
- [ ] Twilio production number configured
- [ ] Monitoring dashboards ready

### Post-Launch

- [ ] Monitor error rates
- [ ] Track DSO improvements
- [ ] Collect user feedback
- [ ] Plan V2 features (payment plans, JobNimbus integration)

---

*Tasks version 1.0 - January 2026*
