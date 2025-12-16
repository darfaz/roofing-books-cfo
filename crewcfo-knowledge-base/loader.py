"""
Document loader for CrewCFO knowledge base.
Supports: .md, .docx, .pdf, .txt
"""
import os
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    PyPDFLoader,
    Docx2txtLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter


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


def load_documents(docs_dir: str = "./docs") -> List[Document]:
    """
    Load all supported documents from directory.
    
    Args:
        docs_dir: Path to documents directory
        
    Returns:
        List of Document objects with metadata
    """
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
                    # Add source metadata
                    for doc in docs:
                        doc.metadata["source"] = str(file_path)
                        doc.metadata["filename"] = file_path.name
                    all_docs.extend(docs)
                    print(f"✓ Loaded: {file_path.name}")
            except Exception as e:
                print(f"✗ Error loading {file_path.name}: {e}")
    
    print(f"\nTotal documents loaded: {len(all_docs)}")
    return all_docs


def chunk_documents(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Document]:
    """
    Split documents into chunks for embedding.
    
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


if __name__ == "__main__":
    # Test loading
    docs = load_documents()
    chunks = chunk_documents(docs)
    print(f"\nSample chunk:\n{chunks[0].page_content[:500]}...")
