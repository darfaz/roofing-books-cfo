# Friday Payday - Quickstart & Validation Guide

> **Feature**: 09-friday-payday
> **Status**: Planned
> **Priority**: P0 (Core)
> **Last Updated**: 2026-01-02
> **Purpose**: Validate key scenarios before launch

---

## Overview

This document provides step-by-step validation scenarios to ensure Friday Payday works correctly within the CrewCFO platform. Each scenario should be tested in staging before production launch.

---

## Prerequisites

Before testing, ensure:

1. **CrewCFO environment deployed**
   - Frontend running (Vite dev or production)
   - FastAPI backend running
   - n8n deployed (Railway or local Docker)
   - Supabase project with fp_* tables migrated

2. **Test accounts ready**
   - QuickBooks Sandbox account with test data
   - SendGrid account with verified sender (reuse existing)
   - Twilio account with test phone (new)
   - Stripe test mode enabled (new)

3. **Test data prepared**
   - Test tenant with QBO connected
   - 10+ invoices in various states (current, 1-30, 31-60, 61-90, 90+)
   - 5+ customers with email/phone
   - Demo mode data for offline testing

---

## Scenario 1: Collections Tab Access

**Goal:** Verify Friday Payday tab appears and loads within CrewCFO dashboard

### Steps

```
1. Log in to CrewCFO with test tenant credentials
2. Verify sidebar/tabs show "Collections" option
3. Click "Collections" tab
4. Verify Friday Payday dashboard loads
5. If demo mode: verify mock data displays
6. If QBO connected: verify invoice data syncs
```

### Expected Results

| Checkpoint | Expected |
|------------|----------|
| Tab visible | ✅ "Collections" in navigation |
| Dashboard loads | ✅ No errors, < 3 seconds |
| Demo mode works | ✅ Mock data displays |
| Real data works | ✅ Invoices from QBO appear |

---

## Scenario 2: Invoice Sync from QBO

**Goal:** Verify invoices sync from existing QBO integration to fp_invoices

### Steps

```
1. Log in as tenant with QBO connected
2. Trigger QBO sync from settings (or wait for automatic)
3. Navigate to Collections tab
4. Verify invoices appear in invoice list
5. Verify customer data populated
6. Check invoice classification applied
```

### Expected Results

| Checkpoint | Expected |
|------------|----------|
| Sync completes | ✅ < 60 seconds for 500 invoices |
| Invoices appear | ✅ Match QBO invoice count |
| Customers synced | ✅ fp_customers populated |
| Classification applied | ✅ payer_type assigned |

### Validation Query

```sql
-- Verify data synced
SELECT
    (SELECT COUNT(*) FROM fp_invoices WHERE tenant_id = '[TEST_TENANT_ID]') as invoice_count,
    (SELECT COUNT(*) FROM fp_customers WHERE tenant_id = '[TEST_TENANT_ID]') as customer_count,
    (SELECT fp_settings->>'last_sync_at' FROM tenants WHERE id = '[TEST_TENANT_ID]') as last_sync;
```

---

## Scenario 3: Invoice Classification

**Goal:** Verify invoices are correctly classified by payer type

### Steps

```
1. Navigate to Collections > Invoices
2. Verify auto-classification:
   - Invoice with "Insurance claim" in memo → insurance_pending
   - Invoice with "Supplement" in memo → supplement_pending
   - Invoice with "ACV" or "depreciation" → depreciation_recovery
   - Invoice > $25K → gc_commercial
   - Regular invoice → homeowner_direct
3. Override classification manually:
   - Click invoice
   - Change payer_type
   - Save
4. Verify sequence assigned based on classification
```

### Expected Results

| Invoice Type | Expected Classification | Expected Sequence |
|--------------|------------------------|-------------------|
| Normal residential | homeowner_direct | Homeowner Standard |
| Contains "claim #" | insurance_pending | Insurance Claim |
| Contains "supplement" | supplement_pending | Supplement Follow-up |
| Contains "depreciation" | depreciation_recovery | Depreciation Recovery |
| Amount > $25,000 | gc_commercial | Commercial 30-45-60 |

---

## Scenario 4: Automated Email Reminder

**Goal:** Verify email reminders send correctly via n8n

### Steps

```
1. Create/identify invoice that is 7 days past due
2. Ensure customer has valid email in fp_customers
3. Run n8n daily-aging-check workflow manually
4. Verify reminder record created in fp_reminders
5. Run n8n send-reminder workflow
6. Check SendGrid dashboard for delivery
7. Verify fp_communication_log entry created
8. Verify invoice sequence_current_step incremented
```

### Expected Results

| Checkpoint | Expected |
|------------|----------|
| Reminder queued | ✅ fp_reminders record created |
| Email sent | ✅ SendGrid shows delivered |
| Log entry | ✅ fp_communication_log updated |
| Invoice updated | ✅ sequence_current_step incremented |

### Test Email Content Should Include

- Customer name
- Invoice number
- Amount due
- Due date
- Payment link (clickable)
- Company contact info

---

## Scenario 5: Automated SMS Reminder

**Goal:** Verify SMS reminders send correctly

### Steps

```
1. Create/identify invoice that is 14 days past due
2. Ensure customer has valid phone in fp_customers
3. Customer should have email_opt_in = true OR sms_opt_in = true
4. Run daily-aging-check workflow
5. Run send-reminder workflow (SMS step)
6. Check Twilio dashboard for delivery
7. Verify link in SMS opens payment portal
```

### Expected Results

| Checkpoint | Expected |
|------------|----------|
| SMS sent | ✅ Twilio shows delivered |
| Message content | ✅ Contains amount, payment link |
| Link works | ✅ Opens payment portal |
| Character count | ✅ Under 160 characters |

### Sample SMS

```
Hi John! Your Reliable Roofing invoice ($2,450) is 14 days past due.
Pay securely: https://pay.crewcfo.com/abc123
```

---

## Scenario 6: Payment Portal Flow

**Goal:** Verify payment collection works end-to-end

### Steps

```
1. Get payment link from reminder email
2. Open link in incognito browser
3. Verify portal shows:
   - Company logo and branding
   - Invoice details (number, amount, job address)
   - Payment options (card, ACH)
4. Enter test card: 4242 4242 4242 4242
5. Complete payment
6. Verify confirmation page
7. Check fp_invoices balance updated
8. Verify sequence stopped
9. Check if payment posted to QuickBooks
```

### Expected Results

| Checkpoint | Expected |
|------------|----------|
| Portal loads | ✅ Branded correctly |
| Invoice displays | ✅ Correct amount |
| Payment succeeds | ✅ Stripe shows charge |
| Confirmation shows | ✅ Thank you page |
| Invoice updated | ✅ status = 'paid', balance = 0 |
| Sequence stopped | ✅ sequence_status = 'completed' |
| QB payment | ✅ Payment appears in QuickBooks |

### Stripe Test Cards

| Card Number | Result |
|-------------|--------|
| 4242 4242 4242 4242 | Success |
| 4000 0000 0000 0002 | Declined |
| 4000 0000 0000 9995 | Insufficient funds |

---

## Scenario 7: Friday Cash Release Summary

**Goal:** Verify weekly summary email sends correctly

### Steps

```
1. Trigger n8n friday-summary workflow manually
2. Check test inbox for email
3. Verify email content:
   - Total collected this week
   - Number of invoices paid
   - Comparison to last week
   - Top payments list
   - Outstanding balance
   - Link to dashboard
```

### Expected Results

| Checkpoint | Expected |
|------------|----------|
| Email received | ✅ In inbox |
| Subject line | ✅ "Friday Payday - Your Weekly Cash Release" |
| Amounts correct | ✅ Matches database calculations |
| Formatting | ✅ Readable, mobile-friendly |

---

## Scenario 8: Sequence Pause/Resume

**Goal:** Verify manual sequence controls work

### Steps

```
1. Navigate to Collections > Invoices
2. Click on an invoice with active sequence
3. Click "Pause Sequence"
4. Enter reason: "Customer requested"
5. Save
6. Verify sequence paused
7. Run daily-aging-check
8. Verify no reminder queued for this invoice
9. Resume sequence
10. Verify next action scheduled
```

### Expected Results

| Checkpoint | Expected |
|------------|----------|
| Pause saves | ✅ sequence_status = 'paused' |
| Reason stored | ✅ sequence_paused_at set |
| No new reminders | ✅ Daily check skips paused |
| Resume works | ✅ sequence_status = 'active' |

---

## Scenario 9: Customer Suppression

**Goal:** Verify customer opt-out works

### Steps

```
1. Navigate to Collections > Customers
2. Find customer with active invoices
3. Click "Suppress Communications"
4. Confirm suppression
5. Verify customer marked suppressed
6. Run daily-aging-check
7. Verify no reminders queued for this customer
8. Check that invoices still visible in dashboard
```

### Expected Results

| Checkpoint | Expected |
|------------|----------|
| Suppression saves | ✅ is_suppressed = true |
| Invoices visible | ✅ Still in dashboard |
| No reminders | ✅ Skipped in daily check |
| Manual allowed | ✅ Can still send manual reminder with confirmation |

---

## Scenario 10: Integration with Owner Dashboard

**Goal:** Verify Friday Payday data appears in existing Owner Dashboard

### Steps

```
1. Navigate to Owner Dashboard (main dashboard)
2. Verify AR Aging widget shows Friday Payday data
3. Click on AR aging bucket
4. Verify drills down to Collections > Invoices
5. Check that DSO metric includes Friday Payday calculations
```

### Expected Results

| Checkpoint | Expected |
|------------|----------|
| AR Aging displays | ✅ Uses fp_invoices data |
| Drill-down works | ✅ Opens Collections with filter |
| DSO accurate | ✅ Calculated from fp_invoices |

---

## Quick Validation Commands

### Check System Health

```bash
# CrewCFO API health
curl http://localhost:8000/health

# n8n status
curl http://localhost:5678/healthz

# Database connection
curl http://localhost:8000/api/qbo/status
```

### Database Quick Checks

```sql
-- Active tenants with Friday Payday
SELECT COUNT(*) FROM tenants
WHERE fp_settings IS NOT NULL
AND fp_settings->>'enabled' = 'true';

-- Pending reminders
SELECT COUNT(*) FROM fp_reminders WHERE status = 'scheduled';

-- Today's sent reminders
SELECT COUNT(*) FROM fp_reminders
WHERE sent_at::date = CURRENT_DATE;

-- Payment success rate (last 7 days)
SELECT
    COUNT(*) FILTER (WHERE status = 'paid') as paid,
    COUNT(*) as total,
    ROUND(COUNT(*) FILTER (WHERE status = 'paid')::numeric / NULLIF(COUNT(*), 0) * 100, 2) as rate
FROM fp_invoices
WHERE created_at > NOW() - INTERVAL '7 days';

-- DSO calculation
SELECT tenant_id,
       ROUND(AVG(
           CASE
               WHEN status = 'paid' THEN
                   EXTRACT(DAY FROM (updated_at - invoice_date))
               ELSE
                   EXTRACT(DAY FROM (CURRENT_DATE - invoice_date))
           END
       )::numeric, 1) as current_dso
FROM fp_invoices
WHERE invoice_date > NOW() - INTERVAL '90 days'
GROUP BY tenant_id;
```

---

## Troubleshooting Guide

### Issue: Invoices not syncing

```
1. Check QBO connection status:
   SELECT is_active, token_expires_at FROM tenant_integrations
   WHERE tenant_id = '[ID]' AND provider = 'quickbooks';

2. Check for sync errors in logs

3. Manually trigger sync:
   POST /api/qbo/sync

4. Verify transactions exist:
   SELECT COUNT(*) FROM transactions WHERE tenant_id = '[ID]';
```

### Issue: Emails not sending

```
1. Check SendGrid dashboard for bounces/blocks
2. Verify sender domain is authenticated
3. Check reminder status:
   SELECT * FROM fp_reminders WHERE status = 'failed';
4. Check n8n workflow execution logs
5. Verify customer has email and is not suppressed
```

### Issue: Payments not recording

```
1. Check Stripe dashboard for webhook failures
2. Verify webhook signature secret is correct
3. Check payment reconciliation logs
4. Verify fp_invoices.payment_link is valid
5. Check fp_payments table for partial records
```

### Issue: Classification incorrect

```
1. Check invoice memo/notes content
2. Verify classification keywords in code
3. Override manually and note pattern for improvement
4. Check if amount threshold correct for gc_commercial
```

---

## Sign-Off Checklist

Before production launch, all scenarios must pass:

- [ ] Scenario 1: Collections Tab Access - PASS
- [ ] Scenario 2: Invoice Sync from QBO - PASS
- [ ] Scenario 3: Invoice Classification - PASS
- [ ] Scenario 4: Email Reminders - PASS
- [ ] Scenario 5: SMS Reminders - PASS
- [ ] Scenario 6: Payment Portal - PASS
- [ ] Scenario 7: Friday Summary - PASS
- [ ] Scenario 8: Sequence Pause/Resume - PASS
- [ ] Scenario 9: Customer Suppression - PASS
- [ ] Scenario 10: Owner Dashboard Integration - PASS

**Tested by:** _________________
**Date:** _________________
**Approved for launch:** ☐ Yes ☐ No

---

*Quickstart guide version 1.0 - January 2026*
