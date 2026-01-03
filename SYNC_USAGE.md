# QBO Transaction Sync - Usage Guide

## Overview

The transaction sync service pulls transactions from QuickBooks Online and stores them in your Supabase database. This enables:
- Historical transaction storage
- Classification workflows
- Reporting and analytics
- Job costing

## API Endpoint

### POST `/api/sync/qbo`

Sync transactions from QBO to Supabase.

**Parameters:**
- `tenant_id` (required): Your tenant UUID
- `start_date` (optional): Start date in YYYY-MM-DD format (defaults to 30 days ago)
- `end_date` (optional): End date in YYYY-MM-DD format (defaults to today)
- `incremental` (optional): If `true`, only syncs since last sync (ignores start_date/end_date)

**Example Requests:**

```bash
# Full sync for date range
curl -X POST "http://localhost:8000/api/sync/qbo?tenant_id=YOUR_TENANT_ID&start_date=2024-01-01&end_date=2024-12-31"

# Incremental sync (recommended for scheduled jobs)
curl -X POST "http://localhost:8000/api/sync/qbo?tenant_id=YOUR_TENANT_ID&incremental=true"

# Default sync (last 30 days)
curl -X POST "http://localhost:8000/api/sync/qbo?tenant_id=YOUR_TENANT_ID"
```

**Response:**
```json
{
  "status": "success",
  "sync_result": {
    "status": "success",
    "synced_count": 42,
    "total_fetched": 42,
    "errors": [],
    "start_date": "2024-11-12",
    "end_date": "2024-12-12"
  }
}
```

## Python Usage

### Basic Sync

```python
from services.qbo.sync import QBOSyncService

tenant_id = "your-tenant-uuid"
sync_service = QBOSyncService(tenant_id)

# Incremental sync (recommended)
result = sync_service.sync_incremental()

# Full sync with date range
result = sync_service.sync_transactions(
    start_date="2024-01-01",
    end_date="2024-12-31"
)

print(f"Synced {result['synced_count']} transactions")
```

### What Gets Synced

The sync service fetches and normalizes:

1. **Purchases** (Bills/Expenses)
   - Maps to `transaction_type`: `bill` or `expense` (based on PaymentType)
   - Includes vendor information
   - Stores in `transactions` table

2. **Invoices**
   - Maps to `transaction_type`: `invoice`
   - Includes customer information
   - Tracks balance for AR aging

3. **Deposits** (Payments Received)
   - Maps to `transaction_type`: `deposit`
   - Links to related invoices when possible

## Features

### ✅ Deduplication
- Uses `qbo_id` to prevent duplicate transactions
- Updates existing records if they already exist
- Safe to run multiple times

### ✅ Vendor/Customer Matching
- Automatically tries to match vendor/customer names to existing records
- Sets `vendor_id` or `customer_id` if match found
- Falls back to storing names in metadata

### ✅ Error Handling
- Continues processing even if individual transactions fail
- Returns list of errors in response
- Logs errors for debugging

### ✅ Incremental Sync
- Tracks last sync date
- Only fetches new transactions on subsequent runs
- Efficient for scheduled/automated syncs

## Testing

Use the test script:

```bash
python3 test_sync.py
```

Or test via API:

```bash
# Start the API server
python src/main.py

# In another terminal, trigger sync
curl -X POST "http://localhost:8000/api/sync/qbo?tenant_id=YOUR_TENANT_ID&incremental=true"
```

## Scheduled Sync

To automate syncs, you can:

1. **Add a scheduled job** (cron, Celery, etc.)
2. **Use Supabase Edge Functions** (if using Supabase)
3. **Create a simple script** and run via cron:

```bash
#!/bin/bash
# sync_transactions.sh
source .venv/bin/activate
python -c "
from services.qbo.sync import QBOSyncService
import os
from dotenv import load_dotenv

load_dotenv()
tenant_id = os.getenv('TENANT_ID')
sync_service = QBOSyncService(tenant_id)
result = sync_service.sync_incremental()
print(f'Synced {result[\"synced_count\"]} transactions')
"
```

Then add to crontab:
```bash
# Run every hour
0 * * * * /path/to/sync_transactions.sh
```

## Next Steps

After syncing transactions:

1. **Run Classification**: Use the classification agent to categorize transactions
2. **Review Dashboard**: Check your dashboard to see synced transactions
3. **Set Up Automation**: Schedule regular syncs (hourly/daily)

## Troubleshooting

### No transactions synced
- Check your QBO sandbox/production company has transactions in the date range
- Verify QBO connection is active (check `tenant_integrations` table)
- Check error messages in response

### Vendor/Customer not matching
- Ensure vendors/customers exist in Supabase `vendors` and `customers` tables
- Names must match exactly (case-sensitive)
- Consider creating vendors/customers during sync if they don't exist

### Sync errors
- Check QBO token expiration
- Verify Supabase credentials
- Review error messages in response for specific issues








