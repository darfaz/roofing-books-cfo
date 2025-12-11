# Spec-Kit: AI-Powered Bookkeeping & CFO for Roofing Contractors

> A comprehensive specification package for building automated bookkeeping and fractional CFO software tailored for roofing contractors ($1-10M revenue, 3+ crews).

## ⚡ Quick Start (Fastest Path to MVP)

```bash
# 1. Clone and setup
git clone <your-repo>
cd spec-kit-books-cfo-roofers
chmod +x setup.sh && ./setup.sh

# 2. Configure credentials
cp .env.example .env
# Edit .env with your QBO, Supabase, Anthropic keys

# 3. Start services
python src/main.py                          # API server
streamlit run src/dashboard/owner.py        # Dashboard
docker run -d -p 8080:80 activepieces/activepieces  # Workflows
```

**📖 See [`implementation/oss_implementation_guide.md`](implementation/oss_implementation_guide.md) for detailed tool-by-tool implementation instructions.**

---

## 🎯 Overview

This Spec-Kit provides everything needed to implement:
- **Books OS**: Automated bookkeeping with intelligent transaction classification
- **Finance Command Center**: CFO-level insights with forecasting and scenario planning

### Target Customer Profile (ICP)
- **Trade**: Roofing contractors only
- **Size**: $1–10M annual revenue, 3+ crews
- **Stack**: QuickBooks Online, Jobber/ServiceTitan, standard banking
- **Pain Points**: Manual bookkeeping, 20+ day close cycles, no cash visibility

## 📁 Repository Structure

```
spec-kit-books-cfo-roofers/
├── README.md
├── setup.sh                                    # 🆕 One-command MVP setup
├── speckit.constitution.books_cfo_roofers.md   # Core principles & KPIs
├── speckit.plan.books_cfo_roofers.md           # Phased build plan
├── implementation/
│   └── oss_implementation_guide.md             # 🆕 Tool-by-tool implementation
├── prd/
│   ├── books_os_roofers.md                     # Bookkeeping PRD
│   └── finance_command_center_roofers.md       # CFO tools PRD
├── system-design/
│   └── books_os/
│       ├── data_model/
│       │   ├── accounts.md                     # Chart of accounts schema
│       │   ├── transactions.md                 # Transaction pipeline
│       │   └── jobs.md                         # Job costing model
│       └── agents/
│           ├── classification_agent.md         # AI classification spec
│           └── close_orchestrator.md           # Month-end automation
├── automations/
│   ├── books_os/
│   │   ├── daily_transactions_ingest.yaml      # Daily bank sync
│   │   ├── books_month_close.yaml              # Month-end close
│   │   └── ar_ap_followup.yaml                 # Collection automation
│   └── finance_command_center/
│       ├── cashflow_update.yaml                # 13-week cash forecast
│       ├── forecast_rebuild.yaml               # Scenario modeling
│       └── cfo_weekly_brief.yaml               # AI-generated CFO brief
└── dashboards/
    ├── owner/
    │   └── owner_dashboard.md                  # "Am I okay?" view
    └── cfo/
        └── cfo_dashboard.md                    # "Where's the leverage?" view
```

## 🚀 Quick Start

### 1. Review Core Principles
Start with `speckit.constitution.books_cfo_roofers.md` to understand the non-negotiables and automation principles.

### 2. Understand the Build Plan
Read `speckit.plan.books_cfo_roofers.md` for the phased approach (Discovery → Productization).

### 3. Implement Data Layer (Supabase)
Use the data model specs in `system-design/books_os/data_model/` to create your Supabase schema:
- Accounts, transactions, jobs, job_costs tables
- Row-level security for multi-tenant
- Audit trail triggers

### 4. Build Automations (n8n)
Import the YAML specs from `automations/` into n8n:
- Configure QBO OAuth credentials
- Set up Supabase connection
- Configure Slack webhooks

### 5. Deploy Agents (Dify/LangChain)
Use the agent specs in `system-design/books_os/agents/` to build:
- Classification Agent (Claude 3.5 Sonnet recommended)
- Close Orchestrator for month-end automation

### 6. Create Dashboards
Follow `dashboards/` specs for owner and CFO views using your preferred framework (Retool, custom React, etc.).

## 🛠️ Tech Stack (OSS-First for Fastest MVP)

| Component | Tool | License | Purpose |
|-----------|------|---------|---------|
| **QBO Integration** | [python-quickbooks](https://github.com/ej2/python-quickbooks) | MIT | OAuth, transactions, bills, invoices |
| **Double-Entry Ledger** | [python-accounting](https://github.com/ekmungai/python-accounting) | MIT | GAAP reports, job costing, AR/AP aging |
| **Invoice OCR** | [InvoiceNet](https://github.com/naiveHobo/InvoiceNet) | MIT | Extract vendor, amount, line items from PDFs |
| **AI Classification** | [LangChain](https://github.com/langchain-ai/langchain) + Claude | MIT | Transaction categorization |
| **Tax Automation** | [Avalara SDK](https://github.com/avadev/AvaTax-REST-V2-Python-SDK) | Apache 2.0 | Sales tax by jurisdiction |
| **Workflow Automation** | [ActivePieces](https://github.com/activepieces/activepieces) | MIT | Orchestrate all automations |
| **MVP Dashboard** | [Streamlit](https://github.com/streamlit/streamlit) | Apache 2.0 | Owner + CFO dashboards |
| **Database + Auth** | [Supabase](https://supabase.com) | Apache 2.0 | PostgreSQL, RLS, realtime |
| **Production Dashboard** | React + Tailwind | MIT | Custom UI (post-MVP) |

**⚠️ Don't build from scratch what these tools already provide.**

## 📊 Key Metrics (Success Criteria)

| Metric | Target |
|--------|--------|
| Auto-categorization rate | ≥70% touchless |
| Month-end close time | ≤7 days |
| Cash forecast accuracy | ≤20% variance |
| Owner dashboard load time | <3 seconds |
| NPS | ≥40 |

## 🔐 Security & Compliance

- **Multi-tenant**: Row-level security on all tables
- **Audit trails**: Every write operation logged
- **Encryption**: At rest (AES-256) and in transit (TLS 1.3)
- **Compliance**: SOC 2 Type 1 by beta launch

## 💰 Infrastructure Costs (Estimated)

| Service | Monthly Cost |
|---------|--------------|
| Supabase Pro | $25 |
| AWS/Cloud | $100-150 |
| n8n | $0-50 |
| OpenAI/Anthropic | $50-100 |
| Monitoring | $25 |
| **Total** | **$200-350** |

## 👥 Team Requirements

- 2 FTE Full-stack engineers
- 1 FTE ML/AI engineer
- 0.5 FTE Frontend specialist
- 0.5 FTE Product manager
- 0.25 FTE Finance SME (part-time advisor)

## 📅 Timeline

### 4-Week MVP Sprint (Using OSS Tools)
| Week | Focus | Deliverables |
|------|-------|--------------|
| **1** | Data Foundation | Supabase schema, QBO OAuth, InvoiceNet OCR |
| **2** | Classification | LangChain agent, ActivePieces workflows |
| **3** | Dashboards | Streamlit owner view, cash forecasting |
| **4** | CFO Tools & Launch | Weekly brief, pilot customer onboarding |

### Extended Roadmap (Post-MVP)
- **Weeks 5-8**: Production React dashboard, month-end close automation
- **Weeks 9-12**: Scenario modeling, AR/AP automation
- **Weeks 13-16**: Multi-entity, AIA billing, advanced reporting

## 📚 Related Documents

- [Competitive Analysis](./docs/competitive_landscape.md)
- [Industry Analysis](./docs/roofing_industry.md)
- [Open Source Tools](./docs/oss_tools.md)

## 🤝 Contributing

This is a specification package. Implementation contributions should follow the patterns defined in these specs.

## 📝 License

Proprietary - Internal Use Only

---

**Built for roofing contractors who deserve enterprise-grade financial tools without enterprise complexity.**
