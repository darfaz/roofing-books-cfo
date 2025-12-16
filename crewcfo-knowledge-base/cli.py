#!/usr/bin/env python3
"""
Interactive CLI for CrewCFO Knowledge Base.
"""
import os
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from dotenv import load_dotenv

from chain import create_rag_chain, query
from retriever import get_or_create_vectorstore

load_dotenv()

app = typer.Typer(help="CrewCFO Knowledge Base CLI")
console = Console()


@app.command()
def chat(
    rebuild: bool = typer.Option(False, "--rebuild", "-r", help="Rebuild vector store from docs"),
    docs_dir: str = typer.Option("./docs", "--docs", "-d", help="Documents directory"),
    k: int = typer.Option(6, "--k", help="Number of documents to retrieve"),
):
    """
    Interactive chat with the CrewCFO knowledge base.
    """
    console.print(Panel.fit(
        "[bold blue]CrewCFO Knowledge Base[/bold blue]\n"
        "Ask questions about valuation modules, Spec-OS, and more.\n"
        "Type 'exit' or 'quit' to leave. Type 'help' for commands.",
        title="Welcome"
    ))
    
    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print("[red]Error: ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key.[/red]")
        raise typer.Exit(1)
    
    # Initialize
    with console.status("[bold green]Loading knowledge base..."):
        vectorstore = get_or_create_vectorstore(
            docs_dir=docs_dir,
            force_rebuild=rebuild
        )
        chain = create_rag_chain(vectorstore=vectorstore, k=k)
    
    console.print("[green]✓ Ready![/green]\n")
    
    # Chat loop
    while True:
        try:
            question = Prompt.ask("[bold cyan]You[/bold cyan]")
            
            if question.lower() in ("exit", "quit", "q"):
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            if question.lower() == "help":
                console.print(Panel(
                    "• Type your question and press Enter\n"
                    "• 'rebuild' - Rebuild the vector store\n"
                    "• 'sources' - Show last retrieved sources\n"
                    "• 'exit/quit/q' - Exit the CLI",
                    title="Commands"
                ))
                continue
            
            if question.lower() == "rebuild":
                with console.status("[bold green]Rebuilding vector store..."):
                    vectorstore = get_or_create_vectorstore(
                        docs_dir=docs_dir,
                        force_rebuild=True
                    )
                    chain = create_rag_chain(vectorstore=vectorstore, k=k)
                console.print("[green]✓ Rebuilt![/green]")
                continue
            
            if not question.strip():
                continue
            
            # Query
            with console.status("[bold green]Thinking..."):
                answer = chain.invoke(question)
            
            console.print("\n[bold green]Claude:[/bold green]")
            console.print(Markdown(answer))
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question to ask"),
    docs_dir: str = typer.Option("./docs", "--docs", "-d", help="Documents directory"),
    k: int = typer.Option(6, "--k", help="Number of documents to retrieve"),
):
    """
    Ask a single question (non-interactive).
    """
    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print("[red]Error: ANTHROPIC_API_KEY not set[/red]")
        raise typer.Exit(1)
    
    with console.status("[bold green]Loading..."):
        vectorstore = get_or_create_vectorstore(docs_dir=docs_dir)
        chain = create_rag_chain(vectorstore=vectorstore, k=k)
    
    answer = chain.invoke(question)
    console.print(Markdown(answer))


@app.command()
def ingest(
    docs_dir: str = typer.Option("./docs", "--docs", "-d", help="Documents directory"),
    chunk_size: int = typer.Option(1000, "--chunk-size", help="Chunk size"),
    chunk_overlap: int = typer.Option(200, "--overlap", help="Chunk overlap"),
):
    """
    Ingest documents and build/rebuild the vector store.
    """
    console.print(f"[bold]Ingesting documents from {docs_dir}...[/bold]")
    
    vectorstore = get_or_create_vectorstore(
        docs_dir=docs_dir,
        force_rebuild=True,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    
    count = vectorstore._collection.count()
    console.print(f"[green]✓ Ingested {count} chunks into vector store[/green]")


@app.command()
def search(
    query_text: str = typer.Argument(..., help="Search query"),
    docs_dir: str = typer.Option("./docs", "--docs", "-d", help="Documents directory"),
    k: int = typer.Option(4, "--k", help="Number of results"),
):
    """
    Search the knowledge base without LLM (retrieval only).
    """
    vectorstore = get_or_create_vectorstore(docs_dir=docs_dir)
    results = vectorstore.similarity_search(query_text, k=k)
    
    for i, doc in enumerate(results):
        source = doc.metadata.get("filename", "unknown")
        console.print(Panel(
            doc.page_content[:500] + "...",
            title=f"[{i+1}] {source}",
            border_style="blue"
        ))


if __name__ == "__main__":
    app()
