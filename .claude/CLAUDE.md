# CrewCFO - Roofing Industry AI Assistant

This project provides fractional CFO services and business intelligence for roofing contractors. Claude Code is equipped with specialized skills to help with common roofing business operations.

## Available Skills

| Skill | Description | Trigger Examples |
|-------|-------------|------------------|
| **roofing-estimates** | Generate detailed roof estimates with materials, labor, and profit margins | "Create an estimate", "Calculate materials for a roof", "Quote a job" |
| **insurance-claims** | Insurance claim documentation, supplements, and adjuster communications | "Write a supplement", "Document storm damage", "Insurance claim help" |
| **customer-communications** | Professional emails, SMS, follow-ups, and review requests | "Draft a customer email", "Write a follow-up", "Send appointment reminder" |
| **project-documentation** | Job checklists, safety docs, completion certificates, warranties | "Create a pre-job checklist", "Generate warranty document" |
| **sales-proposals** | Sales proposals with Good/Better/Best options and financing | "Create a sales proposal", "Compare roofing options", "Present financing" |
| **financial-analysis** | P&L analysis, cash flow, job costing, and profitability metrics | "Analyze my financials", "Review job profitability", "Check margins" |
| **valuation-prep** | Business valuation preparation and value driver optimization | "Prepare for valuation", "Improve business value", "Exit planning" |
| **operations-sops** | Standard Operating Procedures for all roofing company operations | "Show me the lead response SOP", "Create installation procedure", "Document our process" |
| **roofing-cfo-research** | Industry research: PE consolidation, valuation multiples, competitor analysis, BLS wage data | "What are roofing PE multiples?", "Track roofing acquisitions", "Compare to competitors" |

## Operations SOPs Overview

The **operations-sops** skill provides comprehensive Standard Operating Procedures organized by department:

### Sales SOPs
- `SALES-001` Lead Response Protocol
- `SALES-002` Appointment Confirmation
- `SALES-003` Estimate Presentation Process
- `SALES-004` Follow-Up Cadence

### Production SOPs
- `PROD-001` Job Scheduling
- `PROD-002` Pre-Job Setup
- `PROD-003` Installation Standards
- `PROD-004` Completion & Closeout

### Office SOPs
- `OFFICE-001` Permit Process
- `OFFICE-002` Invoicing & Collections

### Safety SOPs
- `SAFETY-001` Daily Safety Briefing
- `SAFETY-002` Fall Protection

### Quality Control SOPs
- `QC-001` Final Quality Inspection

### Customer Service SOPs
- `CS-001` Complaint Handling

SOPs are located in `.claude/skills/operations-sops/` organized by department.

## Market Research Overview

The **roofing-cfo-research** skill provides industry intelligence for platform development:

### Research Workflows
- **PE Consolidation Tracker**: Track 56+ PE platforms and 134+ annual acquisitions
- **Valuation Multiples**: EBITDA multiples (2.5-7x range), SDE, revenue multiples
- **Labor Benchmarking**: BLS OEWS data for NAICS 238160
- **Competitor Analysis**: Adaptive, Briq, Pilot, Digits feature comparison

### Key Industry Metrics (Dec 2025)
- Market size: ~$100B revenue, 238,000+ establishments
- PE deal pace: ~1 acquisition every 48 hours
- Industry consolidation: 96%+ still unconsolidated
- Typical multiples: 3-7x EBITDA based on quality

Research files are located in `.claude/skills/roofing-cfo-research/references/`.

## Project Context

This is a **Next.js + FastAPI application** with:
- **Frontend**: React/TypeScript with Vite
- **Backend**: Python FastAPI with Supabase
- **Features**: QuickBooks integration, financial dashboards, valuation modeling

## Key Directories

```
frontend/          # React TypeScript frontend
backend/           # Python FastAPI backend
supabase/          # Database migrations and functions
crewcfo-knowledge-base/  # Industry knowledge and templates
```

## Database

Uses **Supabase** (PostgreSQL) with tables for:
- `tenants` - Roofing company accounts
- `transactions` - Financial transactions (synced from QuickBooks)
- `valuation_shock_reports` - Business valuation analysis
- `action_items` - Strategic recommendations

## When Working on This Project

1. **Financial calculations** should use the roofing industry standard Chart of Accounts
2. **Valuation metrics** follow the EBITDA-based methodology in `crewcfo-knowledge-base/`
3. **Customer-facing content** should maintain a professional yet approachable tone
4. **All estimates** should include waste factors and roof pitch multipliers
