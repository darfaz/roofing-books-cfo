# CrewCFO Knowledge Base

A LangChain + Claude RAG system for querying CrewCFO documentation, including:
- Valuation Intelligence Module specs
- Spec-OS architecture (Torch, Takeoff, Ridgeline)
- Books OS Constitution
- Roofing industry benchmarks

## Quick Start

### 1. Setup Environment

```bash
# Clone/copy this directory
cd crewcfo-knowledge-base

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Copy env template
cp .env.example .env

# Edit .env and add your Anthropic API key
# ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### 3. Add Your Documents

Copy your CrewCFO documentation to the `docs/` folder:
- `.md` files (Markdown)
- `.docx` files (Word)
- `.pdf` files (PDF)
- `.txt` files (Plain text)

```bash
# Example: copy your project docs
cp ~/projects/crewcfo/docs/*.md ./docs/
cp ~/projects/crewcfo/specs/*.docx ./docs/
```

### 4. Run

**Interactive Chat:**
```bash
python cli.py chat
```

**Single Question:**
```bash
python cli.py ask "What are the 5 core features of the Valuation Module?"
```

**Ingest/Rebuild Documents:**
```bash
python cli.py ingest --docs ./docs
```

**Search Only (no LLM):**
```bash
python cli.py search "valuation driver scoring"
```

## CLI Commands

### RAG (Simple Q&A)
| Command | Description |
|---------|-------------|
| `python cli.py chat` | Interactive chat mode |
| `python cli.py chat --rebuild` | Rebuild vector store and chat |
| `python cli.py ask "question"` | Single question |
| `python cli.py ingest` | Rebuild vector store |
| `python cli.py search "query"` | Retrieve without LLM |

### Agent (Planning & Generation)
| Command | Description |
|---------|-------------|
| `python agent.py chat` | Interactive agent with tools |
| `python agent.py task "query"` | Single task execution |
| `python agent.py demo` | Run demo queries |

The agent can:
- Search knowledge base
- Generate database schemas
- Create Epic/Story breakdowns
- Write feature specifications
- Produce implementation roadmaps
- Create Mermaid ERD diagrams

## Options

```bash
--docs, -d     Documents directory (default: ./docs)
--k            Number of documents to retrieve (default: 6)
--rebuild, -r  Force rebuild vector store
--chunk-size   Chunk size for splitting (default: 1000)
--overlap      Chunk overlap (default: 200)
```

## Project Structure

```
crewcfo-knowledge-base/
├── docs/                 # Your documents go here
├── chroma_db/           # Vector store (auto-generated)
├── loader.py            # Document loading & chunking
├── retriever.py         # Vector store management
├── chain.py             # RAG chain with Claude
├── cli.py               # Interactive CLI
├── requirements.txt     # Dependencies
├── .env.example         # Environment template
└── README.md
```

## Programmatic Usage

```python
from chain import ask, create_rag_chain

# Simple query
answer = ask("What schema tables are needed for valuation?")
print(answer)

# Or create reusable chain
chain = create_rag_chain(k=8)
answer1 = chain.invoke("What is the Value Driver Scoring Engine?")
answer2 = chain.invoke("How does the Scenario Simulator work?")
```

## Example Questions

- "What are the 5 core features of the Valuation Intelligence Module?"
- "What database schema is needed for driver_scores?"
- "How does the automation tiering work in Books OS?"
- "What are the Matador tier multiples for roofing companies?"
- "How should I implement the Exit Readiness Deal Room feature?"
- "What data dependencies does Feature A (Valuation Engine) have?"

## Customization

### Change Embedding Model
Edit `retriever.py`:
```python
DEFAULT_EMBEDDING_MODEL = "all-mpnet-base-v2"  # Higher quality, slower
```

### Change Claude Model
Edit `.env`:
```
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

### Adjust System Prompt
Edit `chain.py` → `SYSTEM_PROMPT` to customize Claude's behavior.

## Troubleshooting

**"ANTHROPIC_API_KEY not set"**
- Copy `.env.example` to `.env` and add your API key

**"Documents directory not found"**
- Create `./docs` folder and add your documents

**Slow first run**
- First run downloads embedding model (~90MB). Subsequent runs are fast.

**Out of memory**
- Reduce `--k` parameter or use smaller embedding model

## Next Steps

1. **Add LangGraph Agent**: See `UPGRADE_TO_LANGGRAPH.md` for agent capabilities
2. **Connect to Database**: Query live CrewCFO data alongside docs
3. **Add MCP Server**: Native Claude integration without LangChain
