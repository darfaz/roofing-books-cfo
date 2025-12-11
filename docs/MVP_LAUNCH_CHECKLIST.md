# MVP Launch Checklist: Roofing Books CFO

## Phase 0: Setup (Day 1)

### GitHub Repository
- [ ] Create GitHub repo: `roofing-books-cfo` (private)
- [ ] Upload spec-kit files to repo
- [ ] Set up branch protection on `main`
- [ ] Create `develop` branch for active work

```bash
# Commands
gh repo create roofing-books-cfo --private
cd roofing-books-cfo
unzip spec-kit-books-cfo-roofers.zip
mv spec-kit-books-cfo-roofers/* .
rm -rf spec-kit-books-cfo-roofers
git add .
git commit -m "Initial spec kit"
git push origin main
git checkout -b develop
```

### Development Environment
- [ ] Install Python 3.11+
- [ ] Install Docker Desktop
- [ ] Install VS Code + extensions (Python, Docker, GitLens)
- [ ] Clone repo locally
- [ ] Run `./setup.sh` to install dependencies

---

## Phase 1: Credentials & Accounts (Day 1-2)

### QuickBooks Online (Critical Path)
- [ ] Create Intuit Developer account: https://developer.intuit.com
- [ ] Create new app (OAuth 2.0)
- [ ] Get Client ID and Client Secret
- [ ] Set redirect URI: `http://localhost:8000/callback`
- [ ] Enable sandbox company for testing
- [ ] **Test**: Can you fetch Chart of Accounts from sandbox?

### Supabase
- [ ] Create Supabase account: https://supabase.com
- [ ] Create new project: `roofing-books-cfo`
- [ ] Get project URL and anon key
- [ ] Get service role key (for backend)
- [ ] **Test**: Can you connect from Python?

### Anthropic (Claude API)
- [ ] Create Anthropic account: https://console.anthropic.com
- [ ] Generate API key
- [ ] Add billing (usage-based, ~$0.003 per classification)
- [ ] **Test**: Can you call Claude from Python?

### Slack (Notifications)
- [ ] Create Slack workspace (or use existing)
- [ ] Create app: https://api.slack.com/apps
- [ ] Enable Incoming Webhooks
- [ ] Get webhook URL for `#bookkeeping-alerts` channel
- [ ] **Test**: Can you post a message?

### Optional (Week 2+)
- [ ] Avalara sandbox account (tax automation)
- [ ] Plaid account (bank connections beyond QBO)
- [ ] SendGrid/Postmark (email delivery)

---

## Phase 2: Database Schema (Day 2-3)

### Run Migrations in Supabase
Copy SQL from spec kit data models and run in Supabase SQL editor:

```sql
-- From system-design/books_os/data_model/accounts.md
-- From system-design/books_os/data_model/transactions.md  
-- From system-design/books_os/data_model/jobs.md
```

### Tables to Create
- [ ] `tenants` - Multi-tenant organizations
- [ ] `accounts` - Chart of accounts
- [ ] `transactions` - All financial transactions
- [ ] `transaction_lines` - Double-entry lines
- [ ] `jobs` - Roofing jobs/projects
- [ ] `job_costs` - Costs allocated to jobs
- [ ] `vendors` - Supplier master
- [ ] `customers` - Customer master
- [ ] `classification_rules` - Auto-categorization rules
- [ ] `cash_positions` - Daily cash snapshots
- [ ] `cash_forecasts` - 13-week projections

### Row-Level Security
- [ ] Enable RLS on all tables
- [ ] Create policies for tenant isolation
- [ ] **Test**: User A cannot see User B's data

---

## Phase 3: Core Integrations (Day 3-5)

### QBO OAuth Flow
- [ ] Implement `/auth/qbo/connect` endpoint
- [ ] Implement `/auth/qbo/callback` endpoint
- [ ] Store tokens in `tenant_integrations` table
- [ ] Implement token refresh logic
- [ ] **Test**: Complete OAuth flow, fetch transactions

### QBO Sync Service
- [ ] Fetch Chart of Accounts → `accounts` table
- [ ] Fetch Purchases/Bills → `transactions` table
- [ ] Fetch Invoices → `transactions` table
- [ ] Fetch Customers → `customers` table
- [ ] Fetch Vendors → `vendors` table
- [ ] **Test**: Sandbox data appears in Supabase

### Classification Agent
- [ ] Implement LangChain agent from `classification_agent.md`
- [ ] Create prompt with roofing-specific rules
- [ ] Add confidence threshold (>0.8 = auto-apply)
- [ ] Log classifications for review queue
- [ ] **Test**: Classify 10 sample transactions, check accuracy

---

## Phase 4: MVP Dashboard (Day 5-7)

### Owner Dashboard (Streamlit)
- [ ] Cash balance widget (from Supabase)
- [ ] Revenue MTD widget
- [ ] AR aging summary
- [ ] 13-week forecast chart (placeholder data first)
- [ ] Action items list
- [ ] **Test**: Dashboard loads in <3 seconds

### Deploy Dashboard
- [ ] Deploy to Streamlit Cloud (free tier)
- [ ] Or deploy to Railway/Render
- [ ] Set up authentication (Supabase Auth)
- [ ] **Test**: Access dashboard from phone

---

## Phase 5: Automation Workflows (Week 2)

### ActivePieces Setup
```bash
docker run -d -p 8080:80 \
  -e AP_ENCRYPTION_KEY=your-key \
  -e AP_JWT_SECRET=your-secret \
  activepieces/activepieces
```

### Workflows to Build
- [ ] **Daily Transaction Ingest** (6 AM)
  - Fetch new QBO transactions
  - Run through classifier
  - Update Supabase
  - Slack summary

- [ ] **AR Reminder Sequence**
  - Query overdue invoices
  - Send email reminders (7/14/30/45/60 days)
  - Log reminder in CRM

- [ ] **Weekly CFO Brief** (Friday 4 PM)
  - Aggregate week's metrics
  - Call Claude for narrative
  - Send email + Slack

---

## Phase 6: Pilot Customer (Week 3-4)

### Find First Pilot
- [ ] Identify 1-3 roofing contractors in network
- [ ] Offer free 90-day pilot
- [ ] Requirements: QBO, $1-5M revenue, willing to give feedback
- [ ] Sign simple pilot agreement

### Onboarding Checklist
- [ ] Connect their QBO (OAuth)
- [ ] Import Chart of Accounts
- [ ] Import last 3 months transactions
- [ ] Train classifier on their data (20-50 samples)
- [ ] Review classification accuracy
- [ ] Set up Slack notifications
- [ ] 30-minute training call

### Success Metrics for Pilot
- [ ] ≥70% auto-categorization rate
- [ ] Dashboard used 3+ times/week
- [ ] Positive feedback on weekly brief
- [ ] No critical bugs after Week 1

---

## Immediate Next Actions (Today)

### If you have 1 hour:
1. Create GitHub repo
2. Upload spec kit
3. Create Intuit Developer account
4. Create Supabase project

### If you have 4 hours:
1. All of the above
2. Run setup.sh locally
3. Get QBO OAuth working with sandbox
4. Fetch first transactions

### If you have 1 day:
1. All of the above
2. Set up Supabase schema
3. Build basic classification agent
4. Deploy Streamlit dashboard to cloud

---

## Resource Links

| Resource | URL |
|----------|-----|
| Intuit Developer | https://developer.intuit.com |
| QBO API Docs | https://developer.intuit.com/app/developer/qbo/docs |
| Supabase | https://supabase.com |
| Anthropic Console | https://console.anthropic.com |
| ActivePieces | https://www.activepieces.com |
| Streamlit Cloud | https://streamlit.io/cloud |
| python-quickbooks | https://github.com/ej2/python-quickbooks |
| LangChain Docs | https://python.langchain.com |

---

## Budget for First Month

| Item | Cost |
|------|------|
| Supabase Pro | $25 |
| Anthropic API (~1000 classifications) | $5-10 |
| Streamlit Cloud | $0 (free tier) |
| ActivePieces (self-hosted) | $0 |
| Domain (optional) | $12/year |
| **Total** | **~$35-50** |

---

## Decision Points

### Build vs. Buy
| Component | Recommendation |
|-----------|----------------|
| OAuth/Auth | Use Supabase Auth (don't build) |
| QBO Sync | Use python-quickbooks (don't build) |
| OCR | Start without it, add InvoiceNet in Week 4 |
| Email | Use Resend or SendGrid (don't build SMTP) |
| Dashboards | Streamlit MVP → React later |

### What to Skip for MVP
- ❌ Multi-entity support
- ❌ AIA billing / progress invoicing
- ❌ Lien waiver automation
- ❌ Xero integration
- ❌ Mobile app
- ❌ Custom report builder

These are all P1/P2 features for after you validate with pilots.
