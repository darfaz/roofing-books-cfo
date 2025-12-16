#!/usr/bin/env python3
"""
Quick test script - run this first to validate setup.
Usage: python quick_test.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key.startswith("sk-ant-api03-your"):
        print("❌ ANTHROPIC_API_KEY not configured")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Anthropic API key")
        return False
    print("✓ API key configured")
    
    # Check docs folder
    if not os.path.exists("./docs") or not os.listdir("./docs"):
        print("❌ No documents in ./docs folder")
        print("   Add your .md, .docx, or .pdf files")
        return False
    print(f"✓ Found {len(os.listdir('./docs'))} file(s) in ./docs")
    
    # Test imports
    print("\nLoading dependencies...")
    try:
        from langchain_anthropic import ChatAnthropic
        from langchain_community.vectorstores import Chroma
        from langchain_community.embeddings import HuggingFaceEmbeddings
        print("✓ All imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    # Test embedding model (downloads on first run)
    print("\nLoading embedding model (first run downloads ~90MB)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )
    test_embedding = embeddings.embed_query("test")
    print(f"✓ Embeddings working (dim={len(test_embedding)})")
    
    # Test document loading
    print("\nLoading documents...")
    from loader import load_documents, chunk_documents
    docs = load_documents("./docs")
    if not docs:
        print("❌ No documents loaded")
        return False
    
    chunks = chunk_documents(docs)
    print(f"✓ Loaded {len(docs)} doc(s) → {len(chunks)} chunks")
    
    # Create vector store
    print("\nCreating vector store...")
    from retriever import create_vectorstore
    vectorstore = create_vectorstore(chunks)
    print("✓ Vector store ready")
    
    # Test retrieval
    print("\nTesting retrieval...")
    results = vectorstore.similarity_search("valuation features", k=2)
    print(f"✓ Retrieved {len(results)} results")
    
    # Test Claude connection
    print("\nTesting Claude connection...")
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=api_key,
        max_tokens=100
    )
    response = llm.invoke("Say 'Connection successful!' in exactly 3 words.")
    print(f"✓ Claude responded: {response.content[:50]}...")
    
    # Full RAG test
    print("\nRunning full RAG query...")
    from chain import create_rag_chain
    chain = create_rag_chain(vectorstore=vectorstore)
    answer = chain.invoke("What are the 5 core features of the Valuation Module?")
    print(f"\n{'='*60}")
    print("Q: What are the 5 core features of the Valuation Module?")
    print(f"{'='*60}")
    print(f"\nA: {answer[:500]}...")
    
    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED - Knowledge base is ready!")
    print("="*60)
    print("\nNext steps:")
    print("  • Run: python cli.py chat")
    print("  • Or:  python cli.py ask 'your question'")
    return True


if __name__ == "__main__":
    main()
