# CrewCFO Multi-Agent RAG System - Execution Plan

## Overview

Transform the existing single-agent RAG system into a **multi-domain command center** with specialized agents and a Librarian Agent for knowledge management.

---

## Architecture

```
crewcfo-knowledge-base/
├── data/                          # Knowledge domains
│   ├── software/                  # Tech specs, API docs, architecture
│   ├── marketing/                 # Brand, website copy, personas
│   ├── outreach/                  # Email templates, CRM, case studies
│   ├── valuation/                 # Valuation models, M&A, exit strategy
│   ├── accounting/                # QBO, bookkeeping, chart of accounts
│   ├── sales/                     # Proposals, pricing, objection handling
│   ├── roofing_industry/          # Industry reports, benchmarks, trends
│   └── imports/                   # Raw imports (Claude/ChatGPT exports)
│
├── agents/                        # Specialized agents
│   ├── __init__.py
│   ├── librarian.py               # Knowledge manager (sort, dedupe, find)
│   ├── software_agent.py          # Tech/architecture queries
│   ├── marketing_agent.py         # Brand/messaging queries
│   ├── outreach_agent.py          # Sales/email queries
│   ├── valuation_agent.py         # Valuation/exit queries
│   ├── accounting_agent.py        # Bookkeeping/QBO queries
│   └── router.py                  # Routes queries to correct agent
│
├── chroma_db/                     # Vector store (domain-tagged)
├── loader.py                      # Enhanced with domain metadata
├── retriever.py                   # Domain-filtered retrieval
├── mcp_server.py                  # Claude Code integration
└── consolidate_knowledge.py       # Import processor
```

---

## Phase 1: Directory Structure & Document Migration

### 1.1 Create Domain Directories

```bash
mkdir -p data/{software,marketing,outreach,valuation,accounting,sales,roofing_industry,imports}
mkdir -p agents
```

### 1.2 Auto-Categorize Existing Documents

| Current File | Target Domain |
|--------------|---------------|
| `23816 Roofing Contractors in the US Industry Report.pdf` | `roofing_industry/` |
| `Comprehensive US Roofing M&A Transaction Database.pdf` | `valuation/` |
| `Private Equity Transforms Americas Roofing Industry.pdf` | `valuation/` |
| `Increasing Roofing Company Valuation & Exit Strategy Blueprint.docx` | `valuation/` |
| `US_Roofing_MA_Master_Database.xlsx` | `valuation/` |
| `CrewCFO_Valuation_Feature_20251213.docx` | `software/` |
| `Spec-OS_Automation_Plan_20251211.docx` | `software/` |
| `Spec-OS_Roofing_Bookkeeping_automation_spec_kit.docx` | `software/` |
| `Roofers_Productized_Spec-OS_20251210.docx` | `software/` |
| `Open-Source_Tools___Frameworks_for_Roofing_CFO_MVP.docx` | `software/` |
| `AI-Powered_Bookkeeping_for_Roofing_Contractors.md` | `software/` |
| `Competitive_Landscape__Automated_Bookkeeping.docx` | `marketing/` |
| `U_S__Roofing_Contractor_Industry_Analysis.docx` | `roofing_industry/` |
| `Roofing_Salary_Benchmarking_Tool.xlsx` | `accounting/` |
| `valuation_quick_reference.md` | `valuation/` |

### 1.3 Preserve Generated Files
- Keep `docs/generated/` for agent outputs
- Symlink or reference from main structure

---

## Phase 2: Loader Enhancement

### 2.1 Domain Metadata Tagging

```python
DOMAIN_CONFIG = {
    "software": {
        "source_type": "technical",
        "tags": ["architecture", "specs", "api", "database"]
    },
    "marketing": {
        "source_type": "brand",
        "tags": ["copy", "messaging", "personas", "positioning"]
    },
    "outreach": {
        "source_type": "sales",
        "tags": ["email", "templates", "crm", "follow-up"]
    },
    "valuation": {
        "source_type": "finance",
        "tags": ["m&a", "exit", "multiples", "drivers"]
    },
    "accounting": {
        "source_type": "operations",
        "tags": ["qbo", "bookkeeping", "reconciliation", "coa"]
    },
    "sales": {
        "source_type": "revenue",
        "tags": ["proposals", "pricing", "objections", "closing"]
    },
    "roofing_industry": {
        "source_type": "research",
        "tags": ["market", "benchmarks", "trends", "competitors"]
    },
    "imports": {
        "source_type": "raw",
        "tags": ["chat", "brainstorm", "ideas", "unsorted"]
    }
}
```

### 2.2 JSON Loader for Chat Exports

Add support for:
- Claude export format (JSON with conversations)
- ChatGPT export format (conversations.json)
- Extract assistant responses as knowledge chunks

---

## Phase 3: Multi-Agent Router System

### 3.1 The Librarian Agent

**Purpose:** Master knowledge manager that can:
1. **Ingest** - Process new documents, auto-tag, add to ChromaDB
2. **Classify** - Determine which domain a document belongs to
3. **Dedupe** - Find and flag redundant information
4. **Search** - Cross-domain semantic search
5. **Curate** - Suggest documents to archive/promote

**Tools:**
- `ingest_document(file_path, domain=None)` - Auto-detect or specify domain
- `search_all_domains(query, top_k=10)` - Search across everything
- `find_duplicates(threshold=0.9)` - Find similar chunks
- `reclassify_document(doc_id, new_domain)` - Move document
- `get_domain_stats()` - Show document counts per domain

### 3.2 Domain-Specific Agents

Each agent has:
- Filtered retriever (only searches its domain)
- Domain-specific system prompt
- Specialized tools

| Agent | Domain | Special Capabilities |
|-------|--------|---------------------|
| `SoftwareAgent` | software/ | Generate schemas, specs, API docs |
| `MarketingAgent` | marketing/ | Write copy, analyze competitors |
| `OutreachAgent` | outreach/ | Draft emails, sequence templates |
| `ValuationAgent` | valuation/ | Calculate multiples, driver analysis |
| `AccountingAgent` | accounting/ | QBO queries, COA recommendations |
| `SalesAgent` | sales/ | Proposal drafts, pricing strategies |

### 3.3 Router Agent

**Purpose:** Analyzes user query and routes to appropriate agent(s)

```python
ROUTING_PROMPT = """
Analyze the user's query and determine which agent(s) should handle it.

Available agents:
- librarian: Knowledge management, finding docs, organization
- software: Technical specs, architecture, database, API
- marketing: Brand, messaging, website copy, positioning
- outreach: Email templates, follow-ups, CRM
- valuation: Exit strategy, multiples, M&A, driver scores
- accounting: QBO, bookkeeping, chart of accounts
- sales: Proposals, pricing, objections

Query: {query}

Return JSON: {"primary": "agent_name", "secondary": ["optional", "agents"]}
"""
```

---

## Phase 4: Knowledge Consolidation

### 4.1 Export Sources (Your Action Required)

1. **Claude.ai**: Settings > Privacy > Export Data
   - You'll receive a ZIP with JSON files
   - Place in `data/imports/claude_export/`

2. **ChatGPT**: Profile > Settings > Data Controls > Export
   - You'll receive a ZIP with `conversations.json`
   - Place in `data/imports/chatgpt_export/`

3. **crewcfo.com**: We'll scrape your own site
   - Output to `data/marketing/website/`

### 4.2 Consolidation Script

`consolidate_knowledge.py` will:

```python
# 1. Parse Claude exports
def parse_claude_export(zip_path: str) -> List[Document]:
    """Extract assistant messages from Claude conversations."""

# 2. Parse ChatGPT exports
def parse_chatgpt_export(zip_path: str) -> List[Document]:
    """Extract assistant messages from ChatGPT conversations."""

# 3. Classify and route
def auto_classify(doc: Document) -> str:
    """Use LLM to determine best domain for document."""

# 4. Deduplicate
def deduplicate(docs: List[Document], threshold: float = 0.85) -> List[Document]:
    """Remove near-duplicate chunks using cosine similarity."""

# 5. Scrape website
def scrape_website(url: str, output_dir: str):
    """Scrape crewcfo.com pages to markdown."""
```

---

## Phase 5: MCP Server Integration

### 5.1 MCP Server Tools

```python
# mcp_server.py

@mcp.tool()
async def search_knowledge(query: str, domain: str = None) -> str:
    """Search CrewCFO knowledge base. Optionally filter by domain."""

@mcp.tool()
async def ask_agent(query: str, agent: str = "auto") -> str:
    """Route query to specialized agent. Use 'auto' for smart routing."""

@mcp.tool()
async def list_domains() -> str:
    """List all knowledge domains and document counts."""

@mcp.tool()
async def ingest_document(content: str, domain: str, title: str) -> str:
    """Add new knowledge to the system."""
```

### 5.2 Claude Code Configuration

Add to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "crewcfo-knowledge": {
      "command": "python",
      "args": ["/path/to/crewcfo-knowledge-base/mcp_server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

---

## Execution Order

### Step 1: Structure (30 min)
- [ ] Create directory structure
- [ ] Move and categorize existing docs
- [ ] Verify file organization

### Step 2: Loader (1 hour)
- [ ] Update `loader.py` with domain scanning
- [ ] Add metadata injection
- [ ] Add JSON parser for chat exports
- [ ] Test with existing docs

### Step 3: Agents (2 hours)
- [ ] Create `agents/` module
- [ ] Implement Librarian agent
- [ ] Implement domain-specific agents
- [ ] Build router logic
- [ ] Create unified CLI

### Step 4: Consolidation (1 hour)
- [ ] Create `consolidate_knowledge.py`
- [ ] Add website scraper
- [ ] Add chat export parsers
- [ ] Test with sample data

### Step 5: MCP Server (1 hour)
- [ ] Create `mcp_server.py`
- [ ] Register tools
- [ ] Configure for Claude Code
- [ ] Test integration

---

## Success Metrics

1. **Domain Isolation**: Software agent never returns marketing advice
2. **Cross-Domain Search**: Librarian can find related info across all domains
3. **No Redundancy**: Duplicate chunks identified and flagged
4. **Easy Ingestion**: New docs auto-classified to correct domain
5. **Claude Code Integration**: Query knowledge directly from terminal

---

## Your Next Steps

1. **Export your chat history** from Claude.ai and ChatGPT
2. **Review this plan** - any changes to domains or agent capabilities?
3. **Approve** and I'll start building Phase 1

---

*Plan created: 2024-12-19*
*Status: COMPLETED*

---

## Quick Start Guide

### 1. Process Your Chat History (Auto-classify)

```bash
cd crewcfo-knowledge-base
source venv/bin/activate

# Dry run first to see classifications
python consolidate_knowledge.py --process-imports --dry-run

# Actually process and move files
python consolidate_knowledge.py --process-imports
```

### 2. Use the Multi-Agent Router

```bash
# Interactive chat with auto-routing
python agents/router.py --chat

# Single query
python agents/router.py "What are the valuation multiples for roofing?"
```

### 3. Use the Librarian

```bash
# Show stats
python agents/librarian.py stats

# Search across all domains
python agents/librarian.py search "valuation drivers"

# Classify a file
python agents/librarian.py classify /path/to/file.md
```

### 4. Scrape Your Website (Optional)

```bash
python consolidate_knowledge.py --scrape-website https://crewcfo.com
```

### 5. Set Up Claude Code Integration (Optional)

```bash
# Test MCP server
python mcp_server.py --test

# Add to Claude Code config (copy the output)
```
