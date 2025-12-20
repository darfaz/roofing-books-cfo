"""
Document loader for CrewCFO knowledge base.
Supports: .md, .docx, .pdf, .txt, .json (chat exports)
Enhanced with domain-based metadata tagging.
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredMarkdownLoader,
    PyPDFLoader,
    Docx2txtLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter


# =============================================================================
# DOMAIN CONFIGURATION
# =============================================================================

DOMAIN_CONFIG = {
    "software": {
        "source_type": "technical",
        "description": "Tech specs, API docs, architecture, database schemas",
        "tags": ["architecture", "specs", "api", "database", "code"],
    },
    "marketing": {
        "source_type": "brand",
        "description": "Brand guidelines, website copy, personas, positioning",
        "tags": ["copy", "messaging", "personas", "positioning", "brand"],
    },
    "outreach": {
        "source_type": "sales",
        "description": "Email templates, CRM exports, follow-up sequences",
        "tags": ["email", "templates", "crm", "follow-up", "sequences"],
    },
    "valuation": {
        "source_type": "finance",
        "description": "M&A, exit strategy, valuation multiples, drivers",
        "tags": ["m&a", "exit", "multiples", "drivers", "valuation"],
    },
    "accounting": {
        "source_type": "operations",
        "description": "QBO, bookkeeping, chart of accounts, reconciliation",
        "tags": ["qbo", "bookkeeping", "reconciliation", "coa", "accounting"],
    },
    "sales": {
        "source_type": "revenue",
        "description": "Proposals, pricing strategies, objection handling",
        "tags": ["proposals", "pricing", "objections", "closing", "deals"],
    },
    "roofing_industry": {
        "source_type": "research",
        "description": "Market reports, industry benchmarks, trends",
        "tags": ["market", "benchmarks", "trends", "competitors", "industry"],
    },
    "imports": {
        "source_type": "raw",
        "description": "Unprocessed chat exports and brainstorming",
        "tags": ["chat", "brainstorm", "ideas", "unsorted", "raw"],
    },
    "archive": {
        "source_type": "archived",
        "description": "Deprecated or superseded documents",
        "tags": ["archived", "deprecated", "old", "superseded"],
    },
}

# Default data directory
DEFAULT_DATA_DIR = "./data"
LEGACY_DOCS_DIR = "./docs"


# =============================================================================
# LOADERS
# =============================================================================

def get_loader_for_file(file_path: str):
    """Return appropriate loader based on file extension."""
    ext = Path(file_path).suffix.lower()
    loaders = {
        ".md": UnstructuredMarkdownLoader,
        ".txt": TextLoader,
        ".pdf": PyPDFLoader,
        ".docx": Docx2txtLoader,
    }
    loader_cls = loaders.get(ext)
    if loader_cls:
        return loader_cls(file_path)
    return None


def load_json_chat_export(file_path: str) -> List[Document]:
    """
    Load Claude or ChatGPT JSON export files.
    Extracts assistant messages as knowledge chunks.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    documents = []
    filename = Path(file_path).name

    # Handle different export formats
    if isinstance(data, list):
        # Claude format: list of conversations
        for conv in data:
            if isinstance(conv, dict):
                messages = conv.get('messages', conv.get('chat_messages', []))
                title = conv.get('title', conv.get('name', 'Untitled'))
                for msg in messages:
                    if msg.get('role') == 'assistant' or msg.get('sender') == 'assistant':
                        content = msg.get('content', msg.get('text', ''))
                        if content and len(content) > 100:  # Skip short responses
                            documents.append(Document(
                                page_content=content,
                                metadata={
                                    "source": str(file_path),
                                    "filename": filename,
                                    "conversation_title": title,
                                    "message_type": "assistant",
                                }
                            ))
    elif isinstance(data, dict):
        # ChatGPT format: conversations.json structure
        conversations = data.get('conversations', [data])
        for conv in conversations:
            title = conv.get('title', 'Untitled')
            mapping = conv.get('mapping', {})
            for node_id, node in mapping.items():
                message = node.get('message', {})
                if message and message.get('author', {}).get('role') == 'assistant':
                    parts = message.get('content', {}).get('parts', [])
                    content = '\n'.join(str(p) for p in parts if p)
                    if content and len(content) > 100:
                        documents.append(Document(
                            page_content=content,
                            metadata={
                                "source": str(file_path),
                                "filename": filename,
                                "conversation_title": title,
                                "message_type": "assistant",
                            }
                        ))

    return documents


# =============================================================================
# DOMAIN-AWARE LOADING
# =============================================================================

def detect_domain_from_path(file_path: Path) -> str:
    """Detect domain from file path."""
    parts = file_path.parts
    for part in parts:
        if part in DOMAIN_CONFIG:
            return part
    return "imports"  # Default to imports if no domain detected


def add_domain_metadata(doc: Document, domain: str) -> Document:
    """Add domain-specific metadata to document."""
    config = DOMAIN_CONFIG.get(domain, DOMAIN_CONFIG["imports"])

    doc.metadata["domain"] = domain
    doc.metadata["source_type"] = config["source_type"]
    # ChromaDB requires string values, so join tags
    doc.metadata["domain_tags"] = ",".join(config["tags"])
    doc.metadata["indexed_at"] = datetime.now().isoformat()

    return doc


def load_domain_documents(
    data_dir: str = DEFAULT_DATA_DIR,
    domains: Optional[List[str]] = None,
    include_legacy: bool = False,
) -> List[Document]:
    """
    Load documents from domain directories with metadata tagging.

    Args:
        data_dir: Path to data directory (default: ./data)
        domains: List of domains to load (None = all)
        include_legacy: Whether to include ./docs folder

    Returns:
        List of Document objects with domain metadata
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    all_docs = []
    supported_extensions = [".md", ".txt", ".pdf", ".docx"]

    # Determine which domains to load
    target_domains = domains or list(DOMAIN_CONFIG.keys())

    for domain in target_domains:
        domain_path = data_path / domain
        if not domain_path.exists():
            continue

        print(f"\n📁 Loading domain: {domain}")
        domain_doc_count = 0

        for ext in supported_extensions:
            for file_path in domain_path.glob(f"**/*{ext}"):
                try:
                    loader = get_loader_for_file(str(file_path))
                    if loader:
                        docs = loader.load()
                        for doc in docs:
                            doc.metadata["source"] = str(file_path)
                            doc.metadata["filename"] = file_path.name
                            add_domain_metadata(doc, domain)
                        all_docs.extend(docs)
                        domain_doc_count += len(docs)
                        print(f"  ✓ {file_path.name}")
                except Exception as e:
                    print(f"  ✗ Error loading {file_path.name}: {e}")

        # Handle JSON files (chat exports)
        for file_path in domain_path.glob("**/*.json"):
            try:
                docs = load_json_chat_export(str(file_path))
                for doc in docs:
                    add_domain_metadata(doc, domain)
                all_docs.extend(docs)
                domain_doc_count += len(docs)
                print(f"  ✓ {file_path.name} ({len(docs)} messages)")
            except Exception as e:
                print(f"  ✗ Error loading {file_path.name}: {e}")

        print(f"  📊 {domain}: {domain_doc_count} documents")

    # Include legacy docs if requested
    if include_legacy:
        legacy_path = Path(LEGACY_DOCS_DIR)
        if legacy_path.exists():
            print(f"\n📁 Loading legacy docs from {LEGACY_DOCS_DIR}")
            for ext in supported_extensions:
                for file_path in legacy_path.glob(f"*{ext}"):
                    try:
                        loader = get_loader_for_file(str(file_path))
                        if loader:
                            docs = loader.load()
                            for doc in docs:
                                doc.metadata["source"] = str(file_path)
                                doc.metadata["filename"] = file_path.name
                                doc.metadata["domain"] = "legacy"
                                doc.metadata["source_type"] = "legacy"
                            all_docs.extend(docs)
                            print(f"  ✓ {file_path.name}")
                    except Exception as e:
                        print(f"  ✗ Error loading {file_path.name}: {e}")

    print(f"\n📊 Total documents loaded: {len(all_docs)}")
    return all_docs


def load_documents(docs_dir: str = DEFAULT_DATA_DIR) -> List[Document]:
    """
    Backward-compatible wrapper for load_domain_documents.

    Args:
        docs_dir: Path to documents directory

    Returns:
        List of Document objects with metadata
    """
    # Check if it's the new data structure or legacy
    if Path(docs_dir).name == "data" or (Path(docs_dir) / "software").exists():
        return load_domain_documents(docs_dir)
    else:
        # Legacy mode - single flat directory
        return _load_legacy_documents(docs_dir)


def _load_legacy_documents(docs_dir: str) -> List[Document]:
    """Load documents from a flat directory (legacy mode)."""
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        raise FileNotFoundError(f"Documents directory not found: {docs_dir}")

    all_docs = []
    supported_extensions = [".md", ".txt", ".pdf", ".docx"]

    for ext in supported_extensions:
        for file_path in docs_path.glob(f"**/*{ext}"):
            try:
                loader = get_loader_for_file(str(file_path))
                if loader:
                    docs = loader.load()
                    for doc in docs:
                        doc.metadata["source"] = str(file_path)
                        doc.metadata["filename"] = file_path.name
                    all_docs.extend(docs)
                    print(f"✓ Loaded: {file_path.name}")
            except Exception as e:
                print(f"✗ Error loading {file_path.name}: {e}")

    print(f"\nTotal documents loaded: {len(all_docs)}")
    return all_docs


# =============================================================================
# CHUNKING
# =============================================================================

def chunk_documents(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Document]:
    """
    Split documents into chunks for embedding.
    Preserves all metadata through chunking.

    Args:
        documents: List of Document objects
        chunk_size: Maximum chunk size in characters
        chunk_overlap: Overlap between chunks

    Returns:
        List of chunked Document objects
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    return chunks


# =============================================================================
# UTILITIES
# =============================================================================

def get_domain_stats(data_dir: str = DEFAULT_DATA_DIR) -> Dict[str, int]:
    """Get document count per domain."""
    data_path = Path(data_dir)
    stats = {}

    for domain in DOMAIN_CONFIG.keys():
        domain_path = data_path / domain
        if domain_path.exists():
            count = sum(1 for _ in domain_path.glob("**/*") if _.is_file())
            stats[domain] = count
        else:
            stats[domain] = 0

    return stats


def list_domain_files(domain: str, data_dir: str = DEFAULT_DATA_DIR) -> List[str]:
    """List all files in a domain."""
    domain_path = Path(data_dir) / domain
    if not domain_path.exists():
        return []
    return [f.name for f in domain_path.glob("**/*") if f.is_file()]


def move_to_archive(
    file_path: str,
    data_dir: str = DEFAULT_DATA_DIR,
    reason: str = ""
) -> str:
    """Move a file to the archive domain."""
    source = Path(file_path)
    if not source.exists():
        return f"File not found: {file_path}"

    archive_dir = Path(data_dir) / "archive"
    archive_dir.mkdir(exist_ok=True)

    # Add timestamp to avoid conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_name = f"{timestamp}_{source.name}"
    dest = archive_dir / new_name

    source.rename(dest)

    # Log the archive action
    log_file = archive_dir / "archive_log.txt"
    with open(log_file, "a") as f:
        f.write(f"{datetime.now().isoformat()} | {source.name} -> {new_name} | {reason}\n")

    return f"Archived: {source.name} -> {dest}"


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import sys

    # Check for command line args
    if len(sys.argv) > 1 and sys.argv[1] == "--stats":
        stats = get_domain_stats()
        print("\n📊 Domain Statistics:")
        for domain, count in sorted(stats.items()):
            config = DOMAIN_CONFIG.get(domain, {})
            desc = config.get("description", "")[:40]
            print(f"  {domain:20} {count:3} files  | {desc}")
        sys.exit(0)

    # Test loading
    print("🚀 Loading documents from all domains...")
    docs = load_domain_documents()

    if docs:
        chunks = chunk_documents(docs)

        # Show sample with metadata
        print(f"\n📄 Sample chunk metadata:")
        sample = chunks[0]
        for key, value in sample.metadata.items():
            print(f"  {key}: {value}")
        print(f"\n📝 Content preview:\n{sample.page_content[:300]}...")
