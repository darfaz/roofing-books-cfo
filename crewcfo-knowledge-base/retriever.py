"""
Vector store and retriever for CrewCFO knowledge base.
Uses ChromaDB with HuggingFace embeddings (free, local).
"""
import os
from pathlib import Path
from typing import List, Optional

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from loader import load_documents, chunk_documents


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
    docs_dir: str = "./docs",
    persist_dir: str = DEFAULT_PERSIST_DIR,
    force_rebuild: bool = False,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> Chroma:
    """
    Load existing vector store or create new one from documents.
    
    Args:
        docs_dir: Directory containing source documents
        persist_dir: Directory for vector store persistence
        force_rebuild: If True, rebuild even if exists
        chunk_size: Chunk size for text splitting
        chunk_overlap: Overlap between chunks
        
    Returns:
        Chroma vector store instance
    """
    if not force_rebuild:
        vectorstore = load_vectorstore(persist_dir)
        if vectorstore:
            return vectorstore
    
    print("Building new vector store...")
    documents = load_documents(docs_dir)
    chunks = chunk_documents(documents, chunk_size, chunk_overlap)
    return create_vectorstore(chunks, persist_dir)


def get_retriever(
    vectorstore: Chroma,
    k: int = 4,
    search_type: str = "similarity",
):
    """
    Create a retriever from vector store.
    
    Args:
        vectorstore: Chroma vector store
        k: Number of documents to retrieve
        search_type: "similarity" or "mmr" (maximal marginal relevance)
        
    Returns:
        Retriever instance
    """
    return vectorstore.as_retriever(
        search_type=search_type,
        search_kwargs={"k": k}
    )


if __name__ == "__main__":
    # Test vector store creation
    vectorstore = get_or_create_vectorstore(force_rebuild=True)
    
    # Test retrieval
    retriever = get_retriever(vectorstore)
    results = retriever.invoke("What are the valuation drivers?")
    print(f"\nRetrieved {len(results)} documents")
    for i, doc in enumerate(results):
        print(f"\n--- Result {i+1} ({doc.metadata.get('filename', 'unknown')}) ---")
        print(doc.page_content[:300] + "...")
