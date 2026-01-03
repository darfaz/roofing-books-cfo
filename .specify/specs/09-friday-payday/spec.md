# Friday Payday - Cash Release Autopilot Specification

> **Feature**: 09-friday-payday
> **Status**: Planned
> **Priority**: P0 (Core)
> **Last Updated**: 2026-01-02

---

## Overview

Friday Payday is an AI-powered collections automation system that helps roofing contractors get paid for work they've already completed—without changing how they run their business. It embodies the "Ozempic Principle": zero behavior change, automatic results, visceral outcomes (cash in bank account).

**Target User**: Roofing business owner/operator
**Access Frequency**: Weekly (Friday Cash Release Summary)
**Key Question Answered**: "How much cash did Friday Payday recover for me this week?"

---

## Problem Statement

Roofing contractors complete work but wait 83+ days on average to get paid:
- **82% of contractors** wait 30+ days for payment (up from 49% in 2023)
- **$280 billion annual cost** to the construction industry from payment delays
- **60-70% of residential work** involves insurance claims with complex lifecycles
- **Average DSO**: 75-120 days for roofing contractors

Contractors deal with:
- Insurance claims stuck in supplement review
- Homeowners who "forget" to forward insurance payments
- Depreciation recovery never collected
- General contractors with 60+ day payment terms
- No time to chase payments while running crews

---

## Solution: The "Ozempic" Approach

**"Connect QuickBooks once. Check your bank on Fridays. That's it."**

| Ozempic | Friday Payday |
|---------|---------------|
| One weekly injection | One QuickBooks connection |
| No diet change needed | No workflow change needed |
| Weight drops automatically | Cash appears automatically |
| See results on the scale | See results in bank account |
| Others ask "what's your secret?" | Others ask "how do you always have cash?" |

---

## Integration with CrewCFO

Friday Payday extends the existing CrewCFO platform:

| Existing Feature | Friday Payday Enhancement |
|------------------|---------------------------|
| **QBO Integration** (08-qbo-integration) | Uses existing OAuth, adds invoice sync with classification |
| **Owner Dashboard** (01-owner-dashboard) | AR Aging feeds Friday Payday priorities |
| **Financial Records** | Clean books enable accurate collections |
| **Valuation Drivers** | Faster collections improve cash flow metrics |

---

## User Stories

### Epic 1: Onboarding & Setup

#### US-01: QuickBooks Connection
**As a** roofing contractor owner
**I want to** connect my QuickBooks account in under 5 minutes
**So that** Friday Payday can start identifying my stuck cash

**Acceptance Criteria**:
- [ ] OAuth 2.0 connection flow completes in < 3 clicks
- [ ] Uses existing CrewCFO QBO integration
- [ ] User sees "Connected Successfully" confirmation
- [ ] Initial sync begins automatically
- [ ] Progress indicator shows sync status

#### US-02: Stuck Cash Calculator
**As a** roofing contractor owner
**I want to** see exactly how much money is stuck in my business
**So that** I understand the value Friday Payday can provide

**Acceptance Criteria**:
- [ ] Scan completes within 60 seconds for < 500 invoices
- [ ] Display total stuck AR by aging bucket
- [ ] Highlight top 10 largest overdue invoices
- [ ] Show estimated recoverable amount
- [ ] "Holy shit" moment visualization

#### US-03: Company Profile Setup
**As a** roofing contractor owner
**I want to** configure my company's sending details
**So that** communications go out under my brand

**Acceptance Criteria**:
- [ ] Capture company name, logo, colors
- [ ] Verify sending email address
- [ ] Verify SMS sending number
- [ ] Set default payment methods accepted
- [ ] Configure business hours for contact

---

### Epic 2: Invoice Management

#### US-04: Invoice Classification
**As an** office manager
**I want** invoices automatically classified by payer type
**So that** each gets the appropriate collection sequence

**Acceptance Criteria**:
- [ ] Classify as: Homeowner Direct, Insurance Pending, Supplement Pending, Depreciation Recovery, GC/Commercial, Retainage
- [ ] Classification based on invoice notes, customer type, amount patterns
- [ ] Manual override capability
- [ ] Classification visible on invoice detail
- [ ] Integrates with existing transaction classification (08-qbo-integration)

**Classification Rules**:

| Type | Identification | Default Sequence |
|------|----------------|------------------|
| Homeowner Direct | No insurance keywords, residential | Standard 7-14-30-45 |
| Insurance Pending | "Insurance", "Claim #", adjuster refs | Extended 14-30-45-60 |
| Supplement Pending | "Supplement", "Additional work" | Supplement-specific |
| Depreciation Recovery | "ACV", "Depreciation", "RCV" | Recovery sequence |
| GC/Commercial | Business customer, >$25K | Commercial 30-45-60 |

#### US-05: Invoice Detail View
**As an** office manager
**I want to** see complete invoice history and status
**So that** I can quickly answer customer questions

**Acceptance Criteria**:
- [ ] Invoice amount, date, due date, balance
- [ ] Customer contact information
- [ ] Complete communication history (emails, SMS)
- [ ] Payment history and partial payments
- [ ] Current sequence position and next action
- [ ] Linked job/claim information

#### US-06: Manual Invoice Actions
**As an** office manager
**I want to** manually trigger actions on any invoice
**So that** I can handle special situations

**Acceptance Criteria**:
- [ ] Send reminder now (email/SMS)
- [ ] Pause sequence (with reason)
- [ ] Skip to next step
- [ ] Mark as disputed
- [ ] Add internal note
- [ ] Override classification

---

### Epic 3: Automated Dunning

#### US-07: Configurable Dunning Sequences
**As a** roofing contractor owner
**I want to** configure when and how reminders are sent
**So that** they match my business style

**Acceptance Criteria**:
- [ ] Default sequences pre-configured (start working immediately)
- [ ] Customize timing (days before/after due date)
- [ ] Customize channels (email, SMS, both)
- [ ] Set quiet hours (no messages before 8am or after 7pm)
- [ ] Set weekly contact limits (max 2 per week)

**Default Homeowner Sequence**:

| Day | Channel | Template | Tone |
|-----|---------|----------|------|
| -3 | Email | Upcoming Due | Friendly reminder |
| 0 | Email + SMS | Due Today | Polite urgency |
| 7 | Email | First Past-Due | Understanding |
| 14 | Email + SMS | Second Reminder | Firmer |
| 30 | Email | Escalation Warning | Serious |
| 45 | Email + SMS | Final Notice | Last chance |

#### US-08: AI-Personalized Messages
**As a** roofing contractor owner
**I want** reminder messages personalized to each customer
**So that** they feel personal rather than automated

**Acceptance Criteria**:
- [ ] Messages include customer name, address, specific amount
- [ ] Reference job details when available
- [ ] Tone adjusts based on payment history
- [ ] Avoid generic/robotic language
- [ ] Always include clear payment link

**Example Generated Message**:
```
Hi [John],

Hope the new roof at [123 Oak St] is keeping you dry!

Just a friendly reminder that the final payment of [$2,450]
was due [7 days ago].

Click here to pay securely: [payment-link]

If you have any questions or need to set up a payment plan,
just reply to this email.

Thanks,
[Mike] at [Reliable Roofing]
```

#### US-09: Insurance-Specific Sequences
**As a** roofing contractor owner
**I want** different handling for insurance-related invoices
**So that** we follow up appropriately with longer timelines

**Acceptance Criteria**:
- [ ] Identify insurance payer vs homeowner portion
- [ ] Longer grace periods (insurance is slow)
- [ ] Track claim status separately
- [ ] Reminder to homeowner about endorsements
- [ ] Escalation path for stuck claims

---

### Epic 4: Payment Collection

#### US-10: Payment Portal
**As a** homeowner (end customer)
**I want to** easily pay my roofing invoice online
**So that** I don't have to mail a check or make a call

**Acceptance Criteria**:
- [ ] Branded portal with roofing company logo
- [ ] Invoice details clearly displayed
- [ ] Accept credit card, debit card, ACH
- [ ] Partial payment option
- [ ] Payment confirmation email

#### US-11: Payment Links in Messages
**As a** homeowner
**I want** a direct link to pay in every reminder
**So that** I can pay in two clicks

**Acceptance Criteria**:
- [ ] Unique, secure payment link per invoice
- [ ] Link pre-fills customer and amount
- [ ] Works on mobile
- [ ] Track link clicks (analytics)

#### US-12: Payment Plans
**As a** homeowner
**I want to** set up a payment plan for larger invoices
**So that** I can pay over time

**Acceptance Criteria**:
- [ ] Office manager can offer payment plans
- [ ] 2-6 month options
- [ ] Automatic recurring charges
- [ ] Missed payment triggers follow-up

---

### Epic 5: Dashboard & Reporting

#### US-13: Friday Cash Release Summary
**As a** roofing contractor owner
**I want to** receive a weekly summary of cash recovered
**So that** I can see Friday Payday working without checking dashboards

**Acceptance Criteria**:
- [ ] Email every Friday at 8am
- [ ] Total cash collected this week
- [ ] Number of invoices paid
- [ ] Comparison to previous week
- [ ] Top 5 payments received
- [ ] Simple, scannable format

**Example Summary**:
```
FRIDAY PAYDAY - Your Weekly Cash Release

This week you collected: $14,750
Invoices paid: 7
vs last week: +$3,200 (+28%)

Top payments:
1. Johnson Roof Replacement - $8,500
2. Smith Insurance Final - $3,200
3. Garcia Repair - $1,450
...

Still outstanding: $42,000 across 23 invoices
[View Dashboard]
```

#### US-14: AR Aging Dashboard
**As an** office manager
**I want to** see AR aging at a glance
**So that** I know where to focus attention

**Acceptance Criteria**:
- [ ] Current/0-30/31-60/61-90/90+ buckets
- [ ] Dollar amounts and invoice counts
- [ ] Click to drill into any bucket
- [ ] Filter by payer type, date range
- [ ] Integrates with Owner Dashboard AR Aging

#### US-15: DSO Metrics
**As a** roofing contractor owner
**I want to** see my Days Sales Outstanding trend
**So that** I can measure improvement

**Acceptance Criteria**:
- [ ] Current DSO calculation
- [ ] DSO trend (30/60/90 day)
- [ ] Benchmark vs industry (83 days)
- [ ] Goal setting capability

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/friday-payday/invoices` | GET | List invoices with classification |
| `/api/friday-payday/invoices/{id}` | GET | Get invoice detail |
| `/api/friday-payday/invoices/{id}` | PATCH | Update invoice |
| `/api/friday-payday/invoices/{id}/remind` | POST | Send reminder now |
| `/api/friday-payday/invoices/{id}/pause` | POST | Pause sequence |
| `/api/friday-payday/invoices/{id}/resume` | POST | Resume sequence |
| `/api/friday-payday/customers` | GET | List customers |
| `/api/friday-payday/customers/{id}/suppress` | POST | Suppress communications |
| `/api/friday-payday/analytics/aging` | GET | AR aging buckets |
| `/api/friday-payday/analytics/dso` | GET | DSO metrics |
| `/api/friday-payday/analytics/collected` | GET | Cash collected |
| `/api/friday-payday/sequences` | GET | List dunning sequences |
| `/api/friday-payday/sequences` | POST | Create custom sequence |
| `/api/friday-payday/payments/portal/{token}` | GET | Payment portal data |

---

## Pricing Model

### Option A: Pure Performance (Most "Ozempic")

| Component | Cost |
|-----------|------|
| Setup | $0 |
| First 90 Days | 15% of recovered past-due AR only |
| After 90 Days | $599/mo flat |

### Option B: Matador Bundle

| Component | Cost |
|-----------|------|
| For Matador clients | $399/mo (discounted from $599) |
| Includes | Full Friday Payday + Lead-to-Cash tracking |

**Matador Synergy**: "Matador gets your phone ringing. Friday Payday makes sure you actually get paid."

---

## The Guarantee

**"Your first Friday deposit within 14 days—or we work for free until it happens."**

Concrete. Measurable. Impossible to argue with.

---

## Out of Scope (V1)

1. Mobile native apps (web responsive only)
2. Multiple language support
3. Advanced analytics/BI
4. Mechanic's lien filing
5. Customer credit scoring
6. JobNimbus/AccuLynx integration (V2)
7. White-label deployment
8. API access for customers

---

## Review Checklist

- [ ] QuickBooks connection works in < 5 minutes
- [ ] Stuck cash calculator shows accurate totals
- [ ] Invoice classification accuracy > 85%
- [ ] Reminders send on schedule
- [ ] Payment portal accepts payments
- [ ] Friday summary emails deliver
- [ ] DSO improves within 30 days
- [ ] Zero behavior change required from contractor
