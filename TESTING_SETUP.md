# Testing Setup Guide

This guide explains what's needed to test the dashboard with a real QuickBooks Online sandbox company.

## ✅ Completed Setup

You mentioned you've already:
- ✅ Connected QBO app to a sandbox QBO company
- ✅ Updated `.env` file with QBO, Supabase, OpenAI, and Anthropic secrets

## 🔧 Additional Steps Needed

### 1. Supabase Database Setup

**Required:**
- Run the schema SQL in your Supabase project:
  ```bash
  # Copy contents of supabase/schema.sql and run in Supabase SQL Editor
  ```

**Required Tables:**
- `tenants` - At least one tenant record
- `tenant_integrations` - QBO OAuth tokens and connection info

### 2. Create a Tenant Record

You need at least one tenant in the database. Run this in Supabase SQL Editor:

```sql
INSERT INTO tenants (id, name, legal_name) 
VALUES (gen_random_uuid(), 'Demo Roofing Company', 'Demo Roofing Co LLC')
ON CONFLICT DO NOTHING;
```

Note the `id` - you'll use this as `TENANT_ID` in your `.env` file.

### 3. QBO OAuth Connection

**Option A: If you already completed OAuth flow**
- Your tokens should be stored in `tenant_integrations` table
- Verify with:
  ```sql
  SELECT tenant_id, provider, realm_id, is_active, created_at 
  FROM tenant_integrations 
  WHERE provider = 'quickbooks';
  ```

**Option B: If you need to connect QBO**
1. Start the FastAPI server:
   ```bash
   python src/main.py
   # or
   uvicorn src.main:app --reload --port 8000
   ```

2. Visit the OAuth connect endpoint:
   ```
   http://localhost:8000/auth/qbo/connect?tenant_id=YOUR_TENANT_ID
   ```

3. Authorize the app in QuickBooks
4. Tokens will be stored automatically

### 4. Environment Variables

Ensure your `.env` file has:

```env
# QuickBooks Online (already configured ✅)
QBO_CLIENT_ID=your_client_id
QBO_CLIENT_SECRET=your_client_secret
QBO_REDIRECT_URI=http://localhost:8000/auth/qbo/callback
QBO_ENVIRONMENT=sandbox

# Supabase (already configured ✅)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# Tenant ID (ADD THIS)
TENANT_ID=your-tenant-uuid-from-supabase

# Optional but recommended
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### 5. QuickBooks Sandbox Data

**To test with meaningful data, ensure your QBO sandbox company has:**

1. **Bank Accounts** (for cash balance):
   - At least one checking/savings account with transactions
   - Account Type should be "Bank"

2. **Invoices** (for AR and Revenue):
   - Create some invoices with different dates
   - Some should be unpaid (to show in AR aging)
   - Some should be in the current month (for revenue MTD)

3. **Bills** (for AP):
   - Create some bills with outstanding balances

**Quick Test Data Setup:**
- Log into your QBO sandbox company
- Create a few sample invoices dated in the current month
- Create a bill or two
- Make sure you have at least one bank account with a balance

### 6. Start the Dashboard

```bash
streamlit run src/dashboard/owner.py --server.port 8503
```

The dashboard will:
- Try to connect to QBO automatically
- If QBO is connected, use real data
- If not connected, show a warning and use mock data

### 7. Verify Connection

The dashboard will display:
- ✅ **Green status**: If QBO data loads successfully
- ⚠️ **Warning banner**: If QBO is not connected, with mock data fallback

Check the browser console (F12) for any connection errors.

## 🐛 Troubleshooting

### "No active QBO integration found"
- Verify `tenant_integrations` table has a record for your tenant_id
- Check that `is_active = true`
- Ensure `provider = 'quickbooks'`

### "QBO token expired or invalid"
- Tokens expire after 1 hour for sandbox
- Re-run the OAuth flow to get new tokens
- Or implement token refresh (TODO in code)

### Dashboard shows mock data
- Check if QBO client initialization succeeds
- Verify TENANT_ID in .env matches your Supabase tenant
- Check Supabase credentials are correct
- Look for error messages in Streamlit sidebar/logs

### Empty data or zero values
- Ensure your QBO sandbox company has:
  - Bank accounts with balances
  - Invoices (especially in current month)
  - Bills (for AP)
- Check QBO API permissions in your Intuit app settings

## 📊 What the Dashboard Shows

With real QBO data, you'll see:

1. **Cash Balance**: Sum of all Bank account balances
2. **Revenue MTD**: Sum of invoices from current month
3. **AR Outstanding**: Unpaid invoice balances, aged by date
4. **AR Aging**: Buckets by days outstanding (Current, 31-60, 61-90, 90+)
5. **Forecast**: Simple 13-week projection (basic version, can be enhanced)

**Note:** Job profitability and backlog still use mock data since QBO doesn't have job costing by default.

## 🚀 Next Steps

1. **Token Refresh**: Implement automatic token refresh when expired
2. **Historical Cash Data**: Store historical cash positions for WoW comparison
3. **Job Costing**: Integrate with QBO Projects/Jobs if enabled
4. **Forecast Accuracy**: Enhance forecast with actual expense data
5. **Action Items**: Generate real action items from overdue invoices

## 📝 Quick Checklist

- [ ] Supabase schema deployed
- [ ] Tenant record created
- [ ] QBO OAuth completed and tokens in database
- [ ] `.env` file has all required variables including `TENANT_ID`
- [ ] QBO sandbox has sample data (accounts, invoices, bills)
- [ ] Dashboard running on port 8503
- [ ] Dashboard shows real data (not mock)






