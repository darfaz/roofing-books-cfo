"""
Vector store and retriever for CrewCFO knowledge base.
Uses ChromaDB with HuggingFace embeddings (free, local).
Enhanced with domain-filtered retrieval.
"""
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from loader import load_domain_documents, chunk_documents, DOMAIN_CONFIG, get_domain_stats


# Default settings
DEFAULT_PERSIST_DIR = "./chroma_db"
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_COLLECTION_NAME = "crewcfo_knowledge"


def get_embeddings(model_name: str = DEFAULT_EMBEDDING_MODEL) -> HuggingFaceEmbeddings:
    """
    Initialize HuggingFace embeddings (free, runs locally).

    Args:
        model_name: HuggingFace model name

    Returns:
        HuggingFaceEmbeddings instance
    """
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )


def create_vectorstore(
    documents: List[Document],
    persist_dir: str = DEFAULT_PERSIST_DIR,
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> Chroma:
    """
    Create and persist a ChromaDB vector store from documents.

    Args:
        documents: List of chunked Document objects
        persist_dir: Directory to persist the database
        collection_name: Name of the collection

    Returns:
        Chroma vector store instance
    """
    embeddings = get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_dir,
        collection_name=collection_name,
    )

    print(f"✓ Vector store created with {len(documents)} chunks")
    print(f"✓ Persisted to: {persist_dir}")
    return vectorstore


def load_vectorstore(
    persist_dir: str = DEFAULT_PERSIST_DIR,
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> Optional[Chroma]:
    """
    Load existing vector store from disk.

    Args:
        persist_dir: Directory containing persisted database
        collection_name: Name of the collection

    Returns:
        Chroma vector store instance or None if not found
    """
    if not Path(persist_dir).exists():
        print(f"No existing vector store at {persist_dir}")
        return None

    embeddings = get_embeddings()
    vectorstore = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
        collection_name=collection_name,
    )

    # Check if collection has documents
    count = vectorstore._collection.count()
    if count == 0:
        print("Vector store exists but is empty")
        return None

    print(f"✓ Loaded vector store with {count} chunks")
    return vectorstore


def get_or_create_vectorstore(
    data_dir: str = "./data",
    persist_dir: str = DEFAULT_PERSIST_DIR,
    force_rebuild: bool = False,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    domains: Optional[List[str]] = None,
) -> Chroma:
    """
    Load existing vector store or create new one from documents.

    Args:
        data_dir: Directory containing source documents
        persist_dir: Directory for vector store persistence
        force_rebuild: If True, rebuild even if exists
        chunk_size: Chunk size for text splitting
        chunk_overlap: Overlap between chunks
        domains: Optional list of domains to include

    Returns:
        Chroma vector store instance
    """
    if not force_rebuild:
        vectorstore = load_vectorstore(persist_dir)
        if vectorstore:
            return vectorstore

    print("Building new vector store...")
    documents = load_domain_documents(data_dir, domains=domains)
    chunks = chunk_documents(documents, chunk_size, chunk_overlap)
    return create_vectorstore(chunks, persist_dir)


# =============================================================================
# DOMAIN-FILTERED RETRIEVAL
# =============================================================================

def get_retriever(
    vectorstore: Chroma,
    k: int = 4,
    search_type: str = "similarity",
    domain: Optional[str] = None,
    source_type: Optional[str] = None,
):
    """
    Create a retriever from vector store with optional domain filtering.

    Args:
        vectorstore: Chroma vector store
        k: Number of documents to retrieve
        search_type: "similarity" or "mmr" (maximal marginal relevance)
        domain: Optional domain filter (e.g., "valuation", "software")
        source_type: Optional source type filter (e.g., "technical", "finance")

    Returns:
        Retriever instance
    """
    search_kwargs = {"k": k}

    # Add metadata filters if specified
    if domain or source_type:
        where_filter = {}
        if domain:
            where_filter["domain"] = domain
        if source_type:
            where_filter["source_type"] = source_type
        search_kwargs["filter"] = where_filter

    return vectorstore.as_retriever(
        search_type=search_type,
        search_kwargs=search_kwargs
    )


def search_with_domain(
    vectorstore: Chroma,
    query: str,
    domain: Optional[str] = None,
    k: int = 5,
) -> List[Document]:
    """
    Search vector store with optional domain filtering.

    Args:
        vectorstore: Chroma vector store
        query: Search query
        domain: Optional domain to filter by
        k: Number of results

    Returns:
        List of matching documents
    """
    if domain:
        return vectorstore.similarity_search(
            query,
            k=k,
            filter={"domain": domain}
        )
    return vectorstore.similarity_search(query, k=k)


def search_multiple_domains(
    vectorstore: Chroma,
    query: str,
    domains: List[str],
    k_per_domain: int = 2,
) -> Dict[str, List[Document]]:
    """
    Search across multiple domains and return grouped results.

    Args:
        vectorstore: Chroma vector store
        query: Search query
        domains: List of domains to search
        k_per_domain: Number of results per domain

    Returns:
        Dict mapping domain names to document lists
    """
    results = {}
    for domain in domains:
        if domain in DOMAIN_CONFIG:
            docs = search_with_domain(vectorstore, query, domain, k_per_domain)
            if docs:
                results[domain] = docs
    return results


def cross_domain_search(
    vectorstore: Chroma,
    query: str,
    k: int = 10,
    dedupe: bool = True,
) -> List[Document]:
    """
    Search across all domains without filtering.
    Optionally deduplicate similar results.

    Args:
        vectorstore: Chroma vector store
        query: Search query
        k: Number of results
        dedupe: Whether to remove near-duplicate results

    Returns:
        List of matching documents with domain metadata
    """
    results = vectorstore.similarity_search(query, k=k * 2 if dedupe else k)

    if not dedupe:
        return results[:k]

    # Simple deduplication by content hash
    seen_content = set()
    unique_results = []

    for doc in results:
        # Use first 200 chars as fingerprint
        fingerprint = doc.page_content[:200].strip().lower()
        if fingerprint not in seen_content:
            seen_content.add(fingerprint)
            unique_results.append(doc)
            if len(unique_results) >= k:
                break

    return unique_results


# =============================================================================
# DOMAIN STATS
# =============================================================================

def get_vectorstore_stats(vectorstore: Chroma) -> Dict[str, Any]:
    """Get statistics about the vector store contents."""
    collection = vectorstore._collection

    # Get all documents with metadata
    all_data = collection.get(include=["metadatas"])
    metadatas = all_data.get("metadatas", [])

    # Count by domain
    domain_counts = {}
    source_type_counts = {}

    for meta in metadatas:
        domain = meta.get("domain", "unknown")
        source_type = meta.get("source_type", "unknown")

        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        source_type_counts[source_type] = source_type_counts.get(source_type, 0) + 1

    return {
        "total_chunks": len(metadatas),
        "by_domain": domain_counts,
        "by_source_type": source_type_counts,
    }


def print_vectorstore_stats(vectorstore: Chroma):
    """Print formatted vector store statistics."""
    stats = get_vectorstore_stats(vectorstore)

    print("\n📊 Vector Store Statistics")
    print(f"   Total chunks: {stats['total_chunks']}")

    print("\n   By Domain:")
    for domain, count in sorted(stats["by_domain"].items()):
        bar = "█" * min(count // 10, 20)
        print(f"   {domain:20} {count:4} {bar}")

    print("\n   By Source Type:")
    for stype, count in sorted(stats["by_source_type"].items()):
        print(f"   {stype:20} {count:4}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import sys

    # Check for rebuild flag
    force_rebuild = "--rebuild" in sys.argv or "-r" in sys.argv

    # Get or create vector store
    vectorstore = get_or_create_vectorstore(force_rebuild=force_rebuild)

    # Print stats
    print_vectorstore_stats(vectorstore)

    # Test retrieval
    if "--test" in sys.argv:
        test_queries = [
            ("valuation", "What are the valuation multiples for roofing companies?"),
            ("software", "What is the database schema for the valuation module?"),
            ("roofing_industry", "What is the market size for roofing contractors?"),
        ]

        print("\n🔍 Test Searches:")
        for domain, query in test_queries:
            print(f"\n   Domain: {domain}")
            print(f"   Query: {query}")
            results = search_with_domain(vectorstore, query, domain, k=2)
            for i, doc in enumerate(results):
                print(f"   [{i+1}] {doc.metadata.get('filename', 'unknown')}: {doc.page_content[:100]}...")
