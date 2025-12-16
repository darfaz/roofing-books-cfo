"""
RAG chain for CrewCFO knowledge base using Claude.
"""
import os
from typing import Optional

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import Chroma

from retriever import get_or_create_vectorstore, get_retriever

load_dotenv()

# CrewCFO-specific system prompt
SYSTEM_PROMPT = """You are an expert assistant for CrewCFO, an AI-powered bookkeeping and fractional CFO platform for roofing contractors.

You have access to the following knowledge base documents about:
- Valuation Intelligence Module (Features A-E: Real-time Valuation Engine, Value Driver Scoring, Scenario Simulator, Exit Readiness/Deal Room, Roadmap Agent)
- Spec-OS modules (Torch/Marketing, Takeoff/Operations, Ridgeline/Strategy)
- Books OS Constitution and automation tiers
- Roofing industry financial metrics and benchmarks

When answering questions:
1. Reference specific features, schemas, or module names from the knowledge base
2. Use concrete examples from the roofing contractor domain
3. If discussing implementation, mention relevant data dependencies and automation tiers
4. For valuation questions, reference the Matador tier model (Below Avg / Avg / Above Avg multiples)

Context from knowledge base:
{context}

Answer the question based on the context above. If you don't have enough information, say so clearly."""

USER_PROMPT = """Question: {question}

Provide a detailed, actionable answer based on the CrewCFO documentation."""


def format_docs(docs):
    """Format retrieved documents for context."""
    formatted = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get("filename", "unknown")
        formatted.append(f"[Source {i+1}: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(formatted)


def create_rag_chain(
    vectorstore: Optional[Chroma] = None,
    model_name: str = None,
    temperature: float = 0.1,
    k: int = 6,
):
    """
    Create a RAG chain with Claude and the knowledge base.
    
    Args:
        vectorstore: Optional pre-loaded vector store
        model_name: Claude model to use
        temperature: Model temperature (lower = more focused)
        k: Number of documents to retrieve
        
    Returns:
        Runnable RAG chain
    """
    # Load environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in environment")
    
    model_name = model_name or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    
    # Initialize components
    if vectorstore is None:
        vectorstore = get_or_create_vectorstore()
    
    retriever = get_retriever(vectorstore, k=k)
    
    llm = ChatAnthropic(
        model=model_name,
        temperature=temperature,
        api_key=api_key,
        max_tokens=4096,
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", USER_PROMPT),
    ])
    
    # Build chain
    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain


def query(question: str, chain=None, **kwargs) -> str:
    """
    Query the knowledge base.
    
    Args:
        question: User question
        chain: Optional pre-built chain
        **kwargs: Additional args for create_rag_chain
        
    Returns:
        Answer string
    """
    if chain is None:
        chain = create_rag_chain(**kwargs)
    
    return chain.invoke(question)


# Convenience function for direct use
def ask(question: str) -> str:
    """Simple query interface."""
    return query(question)


if __name__ == "__main__":
    # Test the chain
    test_questions = [
        "What are the 5 core features of the Valuation Intelligence Module?",
        "How does the Value Driver Scoring Engine work?",
        "What schema tables are needed for valuation_snapshots?",
    ]
    
    print("Initializing RAG chain...")
    chain = create_rag_chain()
    
    for q in test_questions:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        print(f"{'='*60}")
        answer = chain.invoke(q)
        print(f"\nA: {answer}")
