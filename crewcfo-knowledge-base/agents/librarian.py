"""
Librarian Agent - Master Knowledge Manager

The Librarian is responsible for:
1. Ingesting new documents and auto-classifying to domains
2. Finding and flagging duplicate/redundant content
3. Cross-domain semantic search
4. Reclassifying documents between domains
5. Archiving deprecated content
6. Reporting on knowledge gaps
"""
import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from langchain_core.documents import Document
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from loader import (
    DOMAIN_CONFIG,
    load_domain_documents,
    chunk_documents,
    get_domain_stats,
    move_to_archive,
    get_loader_for_file,
    add_domain_metadata,
)
from retriever import (
    get_or_create_vectorstore,
    cross_domain_search,
    search_with_domain,
    search_multiple_domains,
    get_vectorstore_stats,
)


LIBRARIAN_SYSTEM_PROMPT = """You are the Librarian, the master knowledge manager for CrewCFO.

Your responsibilities:
1. Classify documents into the correct domain
2. Identify duplicate or redundant content
3. Search across all knowledge domains
4. Suggest which domain a query should be routed to
5. Maintain knowledge quality and organization

Available domains:
- software: Tech specs, API docs, architecture, database schemas
- marketing: Brand guidelines, website copy, personas, positioning
- outreach: Email templates, CRM exports, follow-up sequences
- valuation: M&A, exit strategy, valuation multiples, drivers
- accounting: QBO, bookkeeping, chart of accounts, reconciliation
- sales: Proposals, pricing strategies, objection handling
- roofing_industry: Market reports, industry benchmarks, trends
- imports: Unprocessed/unsorted content

When classifying content, consider:
- The primary purpose of the document
- Who would use this information
- What decisions it supports

Always be precise and explain your reasoning."""


class Librarian:
    """Master knowledge manager for the CrewCFO system."""

    def __init__(
        self,
        data_dir: str = "./data",
        persist_dir: str = "./chroma_db",
    ):
        self.data_dir = Path(data_dir)
        self.persist_dir = persist_dir
        self.vectorstore = None
        self._llm = None

    @property
    def llm(self):
        """Lazy-load the LLM."""
        if self._llm is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
            self._llm = ChatAnthropic(
                model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
                api_key=api_key,
                max_tokens=4096,
            )
        return self._llm

    def get_vectorstore(self, force_rebuild: bool = False):
        """Get or create the vector store."""
        if self.vectorstore is None or force_rebuild:
            self.vectorstore = get_or_create_vectorstore(
                data_dir=str(self.data_dir),
                persist_dir=self.persist_dir,
                force_rebuild=force_rebuild,
            )
        return self.vectorstore

    # =========================================================================
    # SEARCH
    # =========================================================================

    def search(
        self,
        query: str,
        domain: Optional[str] = None,
        k: int = 5,
    ) -> List[Document]:
        """
        Search the knowledge base.

        Args:
            query: Search query
            domain: Optional domain filter
            k: Number of results

        Returns:
            List of matching documents
        """
        vs = self.get_vectorstore()
        if domain:
            return search_with_domain(vs, query, domain, k)
        return cross_domain_search(vs, query, k)

    def search_all_domains(
        self,
        query: str,
        k_per_domain: int = 2,
    ) -> Dict[str, List[Document]]:
        """
        Search across all domains and return grouped results.

        Args:
            query: Search query
            k_per_domain: Results per domain

        Returns:
            Dict of domain -> documents
        """
        vs = self.get_vectorstore()
        domains = list(DOMAIN_CONFIG.keys())
        return search_multiple_domains(vs, query, domains, k_per_domain)

    # =========================================================================
    # CLASSIFICATION
    # =========================================================================

    def classify_content(self, content: str, filename: str = "") -> Tuple[str, str]:
        """
        Use LLM to classify content into a domain.

        Args:
            content: The text content to classify
            filename: Optional filename for context

        Returns:
            Tuple of (domain, reasoning)
        """
        domains_list = "\n".join([
            f"- {name}: {config['description']}"
            for name, config in DOMAIN_CONFIG.items()
            if name != "archive"
        ])

        prompt = f"""Classify the following content into the most appropriate domain.

Available domains:
{domains_list}

Filename: {filename or 'Unknown'}

Content (first 2000 chars):
{content[:2000]}

Respond in JSON format:
{{"domain": "domain_name", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}
"""

        response = self.llm.invoke([
            SystemMessage(content=LIBRARIAN_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])

        try:
            # Extract JSON from response
            text = response.content
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                result = json.loads(text[start:end])
                return result.get("domain", "imports"), result.get("reasoning", "")
        except (json.JSONDecodeError, KeyError):
            pass

        return "imports", "Could not classify - defaulting to imports"

    def classify_file(self, file_path: str) -> Tuple[str, str]:
        """
        Classify a file by loading and analyzing its content.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (domain, reasoning)
        """
        loader = get_loader_for_file(file_path)
        if not loader:
            return "imports", f"Unsupported file type: {Path(file_path).suffix}"

        try:
            docs = loader.load()
            content = "\n".join([doc.page_content for doc in docs])
            return self.classify_content(content, Path(file_path).name)
        except Exception as e:
            return "imports", f"Error loading file: {e}"

    # =========================================================================
    # INGESTION
    # =========================================================================

    def ingest_file(
        self,
        file_path: str,
        domain: Optional[str] = None,
        auto_classify: bool = True,
    ) -> Dict:
        """
        Ingest a new file into the knowledge base.

        Args:
            file_path: Path to file
            domain: Target domain (auto-detect if None)
            auto_classify: Whether to auto-classify if domain not specified

        Returns:
            Result dict with status and details
        """
        source = Path(file_path)
        if not source.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        # Determine target domain
        if domain is None and auto_classify:
            domain, reasoning = self.classify_file(file_path)
            classified = True
        else:
            domain = domain or "imports"
            reasoning = "Manual classification" if domain != "imports" else "No classification"
            classified = False

        # Move file to domain folder
        target_dir = self.data_dir / domain
        target_dir.mkdir(exist_ok=True)
        target_path = target_dir / source.name

        # Handle name conflicts
        if target_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_path = target_dir / f"{timestamp}_{source.name}"

        shutil.copy2(source, target_path)

        return {
            "success": True,
            "file": source.name,
            "domain": domain,
            "path": str(target_path),
            "auto_classified": classified,
            "reasoning": reasoning,
        }

    def ingest_text(
        self,
        content: str,
        title: str,
        domain: Optional[str] = None,
    ) -> Dict:
        """
        Ingest raw text content as a new document.

        Args:
            content: Text content
            title: Document title (used as filename)
            domain: Target domain (auto-detect if None)

        Returns:
            Result dict
        """
        # Auto-classify if needed
        if domain is None:
            domain, reasoning = self.classify_content(content, title)
        else:
            reasoning = "Manual classification"

        # Create file
        safe_title = "".join(c for c in title if c.isalnum() or c in " _-").strip()
        safe_title = safe_title.replace(" ", "_")
        filename = f"{safe_title}.md"

        target_dir = self.data_dir / domain
        target_dir.mkdir(exist_ok=True)
        target_path = target_dir / filename

        # Handle conflicts
        if target_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_path = target_dir / f"{timestamp}_{filename}"

        with open(target_path, "w") as f:
            f.write(f"# {title}\n\n")
            f.write(f"*Added: {datetime.now().isoformat()}*\n\n")
            f.write(content)

        return {
            "success": True,
            "file": target_path.name,
            "domain": domain,
            "path": str(target_path),
            "reasoning": reasoning,
        }

    # =========================================================================
    # DEDUPLICATION
    # =========================================================================

    def find_duplicates(
        self,
        threshold: float = 0.85,
        sample_size: int = 100,
    ) -> List[Dict]:
        """
        Find potential duplicate chunks in the vector store.

        Args:
            threshold: Similarity threshold (0.85 = 85% similar)
            sample_size: Number of chunks to sample

        Returns:
            List of duplicate pairs with similarity scores
        """
        vs = self.get_vectorstore()
        collection = vs._collection

        # Get sample of documents
        all_data = collection.get(
            include=["documents", "metadatas", "embeddings"],
            limit=sample_size,
        )

        documents = all_data.get("documents", [])
        metadatas = all_data.get("metadatas", [])
        embeddings = all_data.get("embeddings", [])
        ids = all_data.get("ids", [])

        if not embeddings:
            return []

        duplicates = []

        # Compare each pair (expensive but thorough)
        import numpy as np
        embeddings = np.array(embeddings)

        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                # Cosine similarity
                sim = np.dot(embeddings[i], embeddings[j]) / (
                    np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
                )

                if sim >= threshold:
                    duplicates.append({
                        "similarity": float(sim),
                        "doc1": {
                            "id": ids[i],
                            "domain": metadatas[i].get("domain", "unknown"),
                            "filename": metadatas[i].get("filename", "unknown"),
                            "preview": documents[i][:100] if documents[i] else "",
                        },
                        "doc2": {
                            "id": ids[j],
                            "domain": metadatas[j].get("domain", "unknown"),
                            "filename": metadatas[j].get("filename", "unknown"),
                            "preview": documents[j][:100] if documents[j] else "",
                        },
                    })

        # Sort by similarity (highest first)
        duplicates.sort(key=lambda x: x["similarity"], reverse=True)
        return duplicates

    # =========================================================================
    # ARCHIVE
    # =========================================================================

    def archive_file(self, file_path: str, reason: str = "") -> str:
        """
        Move a file to the archive.

        Args:
            file_path: Path to file
            reason: Reason for archiving

        Returns:
            Status message
        """
        return move_to_archive(file_path, str(self.data_dir), reason)

    # =========================================================================
    # STATS & REPORTING
    # =========================================================================

    def get_stats(self) -> Dict:
        """Get comprehensive knowledge base statistics."""
        file_stats = get_domain_stats(str(self.data_dir))

        vs = self.get_vectorstore()
        vs_stats = get_vectorstore_stats(vs)

        return {
            "files_by_domain": file_stats,
            "chunks_by_domain": vs_stats["by_domain"],
            "chunks_by_source_type": vs_stats["by_source_type"],
            "total_files": sum(file_stats.values()),
            "total_chunks": vs_stats["total_chunks"],
        }

    def get_domain_summary(self, domain: str) -> Dict:
        """Get summary of a specific domain."""
        domain_path = self.data_dir / domain
        if not domain_path.exists():
            return {"error": f"Domain not found: {domain}"}

        files = list(domain_path.glob("**/*"))
        files = [f for f in files if f.is_file()]

        return {
            "domain": domain,
            "description": DOMAIN_CONFIG.get(domain, {}).get("description", ""),
            "file_count": len(files),
            "files": [f.name for f in files[:20]],  # First 20
            "total_size_kb": sum(f.stat().st_size for f in files) / 1024,
        }

    def suggest_routing(self, query: str) -> Dict:
        """
        Analyze a query and suggest which agent(s) should handle it.

        Args:
            query: User query

        Returns:
            Routing suggestion with reasoning
        """
        prompt = f"""Analyze this query and determine which knowledge domain(s) should handle it.

Query: "{query}"

Available domains:
- software: Tech specs, architecture, API, database
- marketing: Brand, messaging, website copy
- outreach: Email templates, CRM, follow-ups
- valuation: M&A, exit strategy, multiples
- accounting: QBO, bookkeeping, reconciliation
- sales: Proposals, pricing, objections
- roofing_industry: Market research, benchmarks

Respond in JSON:
{{"primary": "domain_name", "secondary": ["optional", "domains"], "reasoning": "why"}}
"""

        response = self.llm.invoke([
            SystemMessage(content=LIBRARIAN_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])

        try:
            text = response.content
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except (json.JSONDecodeError, KeyError):
            pass

        return {"primary": "imports", "secondary": [], "reasoning": "Could not determine"}

    # =========================================================================
    # REBUILD
    # =========================================================================

    def rebuild_index(self) -> Dict:
        """Rebuild the entire vector store from files."""
        self.vectorstore = get_or_create_vectorstore(
            data_dir=str(self.data_dir),
            persist_dir=self.persist_dir,
            force_rebuild=True,
        )
        stats = get_vectorstore_stats(self.vectorstore)
        return {
            "success": True,
            "total_chunks": stats["total_chunks"],
            "by_domain": stats["by_domain"],
        }


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    load_dotenv()

    librarian = Librarian()

    if len(sys.argv) < 2:
        print("Usage: python librarian.py <command> [args]")
        print("\nCommands:")
        print("  stats           - Show knowledge base statistics")
        print("  search <query>  - Search all domains")
        print("  classify <file> - Classify a file")
        print("  ingest <file>   - Ingest a file (auto-classify)")
        print("  duplicates      - Find duplicate content")
        print("  rebuild         - Rebuild vector store")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "stats":
        stats = librarian.get_stats()
        print("\n📊 Knowledge Base Statistics")
        print(f"   Total files: {stats['total_files']}")
        print(f"   Total chunks: {stats['total_chunks']}")
        print("\n   Files by Domain:")
        for domain, count in sorted(stats["files_by_domain"].items()):
            print(f"   {domain:20} {count:4}")

    elif cmd == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        print(f"\n🔍 Searching: {query}\n")
        results = librarian.search(query, k=5)
        for i, doc in enumerate(results):
            domain = doc.metadata.get("domain", "?")
            filename = doc.metadata.get("filename", "?")
            print(f"[{i+1}] [{domain}] {filename}")
            print(f"    {doc.page_content[:150]}...\n")

    elif cmd == "classify" and len(sys.argv) > 2:
        file_path = sys.argv[2]
        domain, reasoning = librarian.classify_file(file_path)
        print(f"\n📁 Classification: {domain}")
        print(f"   Reasoning: {reasoning}")

    elif cmd == "ingest" and len(sys.argv) > 2:
        file_path = sys.argv[2]
        result = librarian.ingest_file(file_path)
        if result["success"]:
            print(f"\n✅ Ingested: {result['file']}")
            print(f"   Domain: {result['domain']}")
            print(f"   Reasoning: {result['reasoning']}")
        else:
            print(f"\n❌ Error: {result['error']}")

    elif cmd == "duplicates":
        print("\n🔍 Finding duplicates (this may take a moment)...")
        dupes = librarian.find_duplicates(threshold=0.9, sample_size=50)
        if dupes:
            print(f"\n   Found {len(dupes)} potential duplicates:\n")
            for d in dupes[:10]:
                print(f"   {d['similarity']:.1%} similar:")
                print(f"     [{d['doc1']['domain']}] {d['doc1']['filename']}")
                print(f"     [{d['doc2']['domain']}] {d['doc2']['filename']}\n")
        else:
            print("   No duplicates found above threshold.")

    elif cmd == "rebuild":
        print("\n🔄 Rebuilding vector store...")
        result = librarian.rebuild_index()
        print(f"   ✅ Rebuilt with {result['total_chunks']} chunks")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
