# OSS Implementation Guide: Fastest Path to MVP

> Maps specific open source tools to each spec kit component for immediate implementation.

## 🎯 Philosophy: Build vs. Buy vs. Integrate

| Approach | When to Use | Examples |
|----------|-------------|----------|
| **Integrate OSS** | Core functionality exists | python-quickbooks, InvoiceNet |
| **Build Custom** | Differentiated logic | Job costing rules, CFO prompts |
| **Use SaaS** | Commodity + reliability | Supabase, Anthropic API |

---

## Component-by-Component Implementation

### 1. QuickBooks Integration
**Spec**: `automations/books_os/daily_transactions_ingest.yaml`

**Use This Tool**: [python-quickbooks](https://github.com/ej2/python-quickbooks) (MIT)

```bash
pip install python-quickbooks
```

```python
from quickbooks import QuickBooks
from quickbooks.objects.account import Account
from quickbooks.objects.bill import Bill
from quickbooks.objects.invoice import Invoice

# Initialize client
client = QuickBooks(
    sandbox=False,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    company_id=COMPANY_ID
)

# Fetch recent transactions (from spec: daily_transactions_ingest.yaml)
from quickbooks.objects.purchase import Purchase
purchases = Purchase.filter(start_date='2024-01-01', qb=client)

# Create bill (from spec: ar_ap_followup.yaml)
bill = Bill()
bill.VendorRef = vendor.to_ref()
bill.Line = [line_item]
bill.save(qb=client)
```

**Why**: Native Python, MIT license, handles OAuth, covers all QBO endpoints needed.

---

### 2. Double-Entry Ledger & GAAP Reporting
**Spec**: `system-design/books_os/data_model/accounts.md`, `transactions.md`

**Use This Tool**: [python-accounting](https://github.com/ekmungai/python-accounting) (MIT)

```bash
pip install python-accounting
```

```python
from python_accounting import Account, Transaction, Entity
from python_accounting.reports import IncomeStatement, BalanceSheet

# Create chart of accounts (matches spec: accounts.md)
entity = Entity(name="ABC Roofing LLC")
revenue = Account(name="Roofing Revenue", account_type="OPERATING_REVENUE")
materials = Account(name="Materials COGS", account_type="DIRECT_COST")

# Record job transaction with job_id tag (matches spec: jobs.md)
txn = Transaction(
    narration="Roof install - Job #1234",
    transaction_date=date.today(),
    entity=entity
)
txn.add_line(account=revenue, amount=15000, tag="job:1234")
txn.add_line(account=materials, amount=-4500, tag="job:1234")
txn.post()

# Generate GAAP reports
income_stmt = IncomeStatement(entity, start_date, end_date)
balance_sheet = BalanceSheet(entity, as_of_date)

# AR Aging (from spec: ar_ap_followup.yaml)
from python_accounting.reports import AgingSchedule
ar_aging = AgingSchedule(entity, account_type="RECEIVABLE")
```

**Why**: GAAP/IFRS compliant, supports job tagging natively, generates AR/AP aging.

---

### 3. Invoice/Receipt OCR
**Spec**: `automations/books_os/daily_transactions_ingest.yaml` (receipt processing)

**Use This Tool**: [InvoiceNet](https://github.com/naiveHobo/InvoiceNet) (MIT)

```bash
git clone https://github.com/naiveHobo/InvoiceNet.git
pip install -r requirements.txt
```

```python
from invoicenet import InvoiceNet
from invoicenet.acp.acp import ACP

# Extract fields from supplier invoice
model = InvoiceNet()
result = model.predict("vendor_invoice.pdf")

# Returns structured data:
# {
#   "vendor_name": "ABC Supply",
#   "invoice_number": "INV-2024-001",
#   "total": 4500.00,
#   "line_items": [
#     {"description": "Shingles", "qty": 50, "unit_price": 45, "amount": 2250},
#     {"description": "Underlayment", "qty": 10, "unit_price": 225, "amount": 2250}
#   ],
#   "due_date": "2024-02-15"
# }

# Auto-create bill in QBO (connects to component 1)
bill = create_bill_from_ocr(result, qb_client)
```

**Alternative**: [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) (Apache 2.0) for general OCR + custom parsing.

**Why**: Pre-trained on invoices, extracts line items (critical for job costing).

---

### 4. Transaction Classification (AI)
**Spec**: `system-design/books_os/agents/classification_agent.md`

**Use This Tool**: [LangChain](https://github.com/langchain-ai/langchain) (MIT)

```bash
pip install langchain langchain-anthropic
```

```python
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel

# Match spec: classification_agent.md
class TransactionClassification(BaseModel):
    account_code: str
    job_id: str | None
    confidence: float
    reasoning: str

parser = PydanticOutputParser(pydantic_object=TransactionClassification)

# Prompt from spec
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a bookkeeping assistant for roofing contractors.
    Classify this transaction to the correct account code.
    
    Chart of Accounts:
    {chart_of_accounts}
    
    Active Jobs:
    {active_jobs}
    
    {format_instructions}"""),
    ("human", "Transaction: {transaction}")
])

llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)
chain = prompt | llm | parser

# Classify
result = chain.invoke({
    "chart_of_accounts": coa_text,
    "active_jobs": jobs_text,
    "transaction": "Home Depot - $1,234.56 - Materials",
    "format_instructions": parser.get_format_instructions()
})
```

**Why**: MIT license, structured output, easy to swap LLM providers, supports RAG for learning from past classifications.

---

### 5. Tax Automation
**Spec**: Not explicitly covered (gap identified)

**Use This Tool**: [AvaTax Python SDK](https://github.com/avadev/AvaTax-REST-V2-Python-SDK) (Apache 2.0)

```bash
pip install Avalara
```

```python
from avalara import AvataxClient

client = AvataxClient(
    app_name='RoofingCFO',
    app_version='1.0',
    environment='production'
)
client.add_credentials(username, password)

# Calculate sales tax on materials invoice
tax = client.create_transaction({
    'type': 'SalesInvoice',
    'customerCode': 'ABC-ROOFING',
    'date': '2024-01-15',
    'lines': [
        {'number': '1', 'quantity': 50, 'amount': 2250, 'taxCode': 'P0000000'}  # Shingles
    ],
    'addresses': {
        'singleLocation': {'line1': '123 Main St', 'city': 'Denver', 'region': 'CO', 'postalCode': '80202'}
    }
})
# Returns tax amount by jurisdiction
```

**Why**: Real-time tax rates by ZIP, handles contractor exemptions, auto-filing.

---

### 6. Workflow Automation
**Spec**: All `automations/*.yaml` files

**Use This Tool**: [ActivePieces](https://github.com/activepieces/activepieces) (MIT) or n8n

```bash
# ActivePieces (fully MIT, recommended)
docker run -d -p 8080:80 activepieces/activepieces

# OR n8n (Sustainable Use License - check terms)
docker run -d -p 5678:5678 n8nio/n8n
```

**Import YAML Specs**: Convert the YAML automation specs to ActivePieces/n8n JSON format:

```javascript
// Example: daily_transactions_ingest.yaml → ActivePieces flow
{
  "name": "Daily Transactions Ingest",
  "trigger": {
    "type": "schedule",
    "cron": "0 6 * * *"  // 6 AM daily
  },
  "steps": [
    {
      "name": "fetch_qbo_transactions",
      "type": "code",
      "code": "// Call python-quickbooks via HTTP"
    },
    {
      "name": "classify_with_llm",
      "type": "http",
      "url": "{{CLASSIFICATION_API}}"
    },
    {
      "name": "update_supabase",
      "type": "supabase",
      "operation": "upsert"
    }
  ]
}
```

**Why ActivePieces over n8n**: Pure MIT license, built-in AI nodes, MCP support.

---

### 7. Dashboards
**Spec**: `dashboards/owner/owner_dashboard.md`, `dashboards/cfo/cfo_dashboard.md`

**Option A - Fastest**: [Streamlit](https://github.com/streamlit/streamlit) (Apache 2.0)

```bash
pip install streamlit plotly
```

```python
# owner_dashboard.py (matches spec: owner_dashboard.md)
import streamlit as st
import plotly.express as px
from supabase import create_client

st.set_page_config(page_title="Roofing CFO", layout="wide")

# Widget 1: Health Banner (from spec)
col1, col2, col3, col4 = st.columns(4)
with col1:
    cash_runway = get_cash_runway()
    color = "🟢" if cash_runway >= 8 else "🟡" if cash_runway >= 4 else "🔴"
    st.metric(f"{color} Cash Runway", f"{cash_runway} weeks")

# Widget 6: 13-Week Forecast Chart (from spec)
forecast_data = get_forecast_data()
fig = px.line(forecast_data, x='week', y=['pessimistic', 'baseline', 'optimistic'])
st.plotly_chart(fig)

# Widget 7: Job Profitability Heatmap (from spec)
jobs = get_recent_jobs()
fig = px.treemap(jobs, path=['job_name'], values='contract_amount', color='margin_pct',
                 color_continuous_scale=['red', 'yellow', 'green'])
st.plotly_chart(fig)
```

**Option B - More Polished**: [Plotly Dash](https://github.com/plotly/dash) (MIT)

**Option C - Self-Service BI**: [Metabase](https://github.com/metabase/metabase) (AGPL) or [Apache Superset](https://github.com/apache/superset) (Apache 2.0)

**Why Streamlit for MVP**: Single Python file, hot reload, deploy to Streamlit Cloud free.

---

### 8. White-Label Invoicing (Optional)
**Spec**: `prd/books_os_roofers.md` (invoicing mentioned)

**Use This Tool**: [Invoice Ninja](https://github.com/invoiceninja/invoiceninja) (Elastic License 2.0)

```bash
docker run -d -p 80:80 invoiceninja/invoiceninja
```

**Why**: Full AR workflow (quotes → invoices → payments), client portal, recurring billing. Use API to sync with your ledger.

---

## 🏗️ Recommended Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND                                  │
│  Streamlit (MVP) → React + Tailwind (Production)                │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATION                               │
│  ActivePieces (MIT) - Workflow automation                        │
│  - daily_transactions_ingest                                     │
│  - books_month_close                                             │
│  - ar_ap_followup                                                │
│  - cashflow_update                                               │
│  - forecast_rebuild                                              │
│  - cfo_weekly_brief                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     PYTHON SERVICES                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ QBO Sync    │  │ Classifier  │  │ OCR Engine  │              │
│  │ python-     │  │ LangChain + │  │ InvoiceNet  │              │
│  │ quickbooks  │  │ Claude API  │  │             │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Ledger      │  │ Tax Calc    │  │ Forecaster  │              │
│  │ python-     │  │ Avalara SDK │  │ Custom      │              │
│  │ accounting  │  │             │  │ (numpy)     │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                 │
│  Supabase (PostgreSQL + Auth + Realtime + Storage)              │
│  - Row-level security for multi-tenant                          │
│  - Edge functions for API                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                            │
│  QuickBooks Online │ Plaid (banking) │ Anthropic │ Avalara      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📅 MVP Sprint Plan (4 Weeks)

### Week 1: Data Foundation
```bash
# Day 1-2: Supabase setup
- Create project
- Run schema migrations from data_model/*.md
- Configure RLS policies

# Day 3-4: QBO Integration
pip install python-quickbooks
- OAuth flow
- Transaction fetch endpoint
- Bill/Invoice creation

# Day 5: OCR Pipeline
git clone https://github.com/naiveHobo/InvoiceNet.git
- Deploy as FastAPI service
- Test with sample invoices
```

### Week 2: Classification & Automation
```bash
# Day 1-2: Classification Agent
pip install langchain langchain-anthropic
- Implement classification_agent.md spec
- Train on 50 sample transactions
- Measure accuracy

# Day 3-5: Workflow Automation
docker run activepieces/activepieces
- Import daily_transactions_ingest
- Import ar_ap_followup
- Connect to Supabase + QBO
```

### Week 3: Dashboards & Forecasting
```bash
# Day 1-3: Owner Dashboard
pip install streamlit plotly
- Implement owner_dashboard.md widgets
- Connect to Supabase
- Deploy to Streamlit Cloud

# Day 4-5: Cash Forecasting
- Implement cashflow_update logic
- 13-week projection algorithm
- Seasonal adjustments
```

### Week 4: CFO Tools & Polish
```bash
# Day 1-2: CFO Weekly Brief
- LLM prompt engineering
- Email/Slack delivery
- Test with real data

# Day 3-4: Integration Testing
- End-to-end flow testing
- Fix edge cases
- Performance tuning

# Day 5: Beta Prep
- Onboard first pilot customer
- Set up monitoring
- Document known issues
```

---

## 🔧 Quick Start Commands

```bash
# Clone and setup
git clone <your-repo>
cd spec-kit-books-cfo-roofers

# Install Python dependencies
pip install python-quickbooks python-accounting langchain langchain-anthropic \
            streamlit plotly supabase avalara pandas numpy

# Clone OCR engine
git clone https://github.com/naiveHobo/InvoiceNet.git lib/invoicenet

# Start workflow automation
docker run -d -p 8080:80 activepieces/activepieces

# Start dashboard (development)
streamlit run dashboards/owner/app.py

# Run classification service
python services/classification/main.py
```

---

## 📊 Tool License Summary

| Tool | License | Commercial OK? |
|------|---------|----------------|
| python-quickbooks | MIT | ✅ Yes |
| python-accounting | MIT | ✅ Yes |
| InvoiceNet | MIT | ✅ Yes |
| LangChain | MIT | ✅ Yes |
| ActivePieces | MIT | ✅ Yes |
| Streamlit | Apache 2.0 | ✅ Yes |
| Plotly Dash | MIT | ✅ Yes |
| Avalara SDK | Apache 2.0 | ✅ Yes |
| Supabase | Apache 2.0 | ✅ Yes |
| n8n | Sustainable Use | ⚠️ Check terms |
| Invoice Ninja | Elastic 2.0 | ⚠️ Whitelabel fee |
| Metabase | AGPL | ⚠️ Copyleft |

---

## ✅ Checklist: Are You Using All Available Resources?

- [ ] **python-quickbooks** for QBO sync (not custom OAuth)
- [ ] **python-accounting** for ledger (not building from scratch)
- [ ] **InvoiceNet** for OCR (not Tesseract + custom parsing)
- [ ] **LangChain** for LLM orchestration (not raw API calls)
- [ ] **ActivePieces** for workflows (MIT license)
- [ ] **Streamlit** for MVP dashboard (not React initially)
- [ ] **Avalara** for tax (not manual rate tables)
- [ ] **Supabase** for database + auth + realtime

**If you're building any of these from scratch, stop and use the OSS tool instead.**
