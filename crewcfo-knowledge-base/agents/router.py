"""
Query Router for CrewCFO Multi-Agent System

The Router analyzes user queries and routes them to the appropriate agent(s).
It can also orchestrate multi-domain queries that require input from multiple agents.
"""
import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from .librarian import Librarian
from .domain_agents import get_agent, list_agents, AGENT_REGISTRY


ROUTER_SYSTEM_PROMPT = """You are the Query Router for CrewCFO's multi-agent knowledge system.

Your job is to analyze user queries and determine which specialized agent(s) should handle them.

Available agents:
- software: Tech specs, architecture, API, database schemas
- marketing: Brand, messaging, website copy, personas
- outreach: Email templates, CRM, follow-up sequences
- valuation: M&A, exit strategy, valuation multiples, drivers
- accounting: QBO, bookkeeping, chart of accounts
- sales: Proposals, pricing, objection handling
- roofing_industry: Market research, benchmarks, trends
- librarian: Cross-domain search, knowledge management

Routing rules:
1. For specific domain questions, route to that domain's agent
2. For cross-domain questions, return multiple agents
3. For knowledge management (find docs, organize), route to librarian
4. For unclear queries, ask for clarification

Respond ONLY with valid JSON in this format:
{"agents": ["primary_agent", "optional_secondary"], "reasoning": "brief explanation"}"""


class Router:
    """Routes queries to appropriate agents."""

    def __init__(
        self,
        data_dir: str = "./data",
        persist_dir: str = "./chroma_db",
    ):
        self.data_dir = data_dir
        self.persist_dir = persist_dir
        self._llm = None
        self._librarian = None
        self._agents = {}

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
                max_tokens=1024,
            )
        return self._llm

    @property
    def librarian(self):
        """Get or create the librarian agent."""
        if self._librarian is None:
            self._librarian = Librarian(
                data_dir=self.data_dir,
                persist_dir=self.persist_dir,
            )
        return self._librarian

    def get_agent(self, domain: str):
        """Get or create a domain agent."""
        if domain not in self._agents:
            if domain == "librarian":
                self._agents[domain] = self.librarian
            else:
                self._agents[domain] = get_agent(
                    domain,
                    data_dir=self.data_dir,
                    persist_dir=self.persist_dir,
                )
        return self._agents[domain]

    def route(self, query: str) -> Dict[str, Any]:
        """
        Analyze a query and determine which agent(s) should handle it.

        Args:
            query: User query

        Returns:
            Dict with agents list and reasoning
        """
        prompt = f"""Analyze this query and determine which agent(s) should handle it.

Query: "{query}"

Remember to respond ONLY with JSON: {{"agents": ["agent1"], "reasoning": "why"}}"""

        response = self.llm.invoke([
            SystemMessage(content=ROUTER_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])

        try:
            text = response.content
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                result = json.loads(text[start:end])
                # Validate agents exist
                valid_agents = list(AGENT_REGISTRY.keys()) + ["librarian"]
                result["agents"] = [
                    a for a in result.get("agents", [])
                    if a in valid_agents
                ]
                if not result["agents"]:
                    result["agents"] = ["librarian"]
                return result
        except (json.JSONDecodeError, KeyError):
            pass

        return {"agents": ["librarian"], "reasoning": "Could not determine routing"}

    def query(
        self,
        question: str,
        auto_route: bool = True,
        agents: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Query the knowledge base with automatic agent routing.

        Args:
            question: User question
            auto_route: Whether to auto-detect agents (default True)
            agents: Manual list of agents to use (overrides auto_route)

        Returns:
            Combined response from all relevant agents
        """
        # Determine which agents to use
        if agents:
            target_agents = agents
            routing = {"agents": agents, "reasoning": "Manual routing"}
        elif auto_route:
            routing = self.route(question)
            target_agents = routing["agents"]
        else:
            target_agents = ["librarian"]
            routing = {"agents": ["librarian"], "reasoning": "Default to librarian"}

        # Query each agent
        responses = []
        for agent_name in target_agents:
            try:
                agent = self.get_agent(agent_name)

                if agent_name == "librarian":
                    # Librarian uses search directly
                    docs = agent.search(question, k=5)
                    response = {
                        "agent": "librarian",
                        "answer": f"Found {len(docs)} relevant documents.",
                        "sources": [
                            {
                                "domain": d.metadata.get("domain", "?"),
                                "filename": d.metadata.get("filename", "?"),
                                "preview": d.page_content[:200],
                            }
                            for d in docs
                        ],
                    }
                else:
                    result = agent.query(question)
                    response = {
                        "agent": agent_name,
                        "answer": result["answer"],
                        "sources": result["sources"],
                    }

                responses.append(response)

            except Exception as e:
                responses.append({
                    "agent": agent_name,
                    "error": str(e),
                })

        return {
            "routing": routing,
            "responses": responses,
        }

    def multi_query(
        self,
        question: str,
        domains: List[str],
    ) -> Dict[str, Any]:
        """
        Query multiple domains in parallel and combine results.

        Args:
            question: User question
            domains: List of domains to query

        Returns:
            Combined response
        """
        return self.query(question, auto_route=False, agents=domains)

    def ask(self, question: str) -> str:
        """
        Simple interface - returns just the answer text.

        Args:
            question: User question

        Returns:
            Combined answer string
        """
        result = self.query(question)

        answers = []
        for resp in result["responses"]:
            if "answer" in resp:
                agent = resp["agent"].upper()
                answers.append(f"**[{agent}]**\n{resp['answer']}")

        return "\n\n---\n\n".join(answers) if answers else "No answer found."


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def route_query(
    query: str,
    data_dir: str = "./data",
    persist_dir: str = "./chroma_db",
) -> Dict[str, Any]:
    """
    Convenience function to route and execute a query.

    Args:
        query: User query
        data_dir: Path to data directory
        persist_dir: Path to vector store

    Returns:
        Query result
    """
    router = Router(data_dir=data_dir, persist_dir=persist_dir)
    return router.query(query)


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel

    load_dotenv()
    console = Console()

    if len(sys.argv) < 2:
        console.print(Panel.fit(
            "[bold]CrewCFO Multi-Agent Router[/bold]\n\n"
            "Usage: python router.py <query>\n"
            "       python router.py --chat (interactive mode)\n\n"
            "[dim]Available agents:[/dim]",
            title="Help"
        ))
        for name, desc in list_agents().items():
            console.print(f"  [cyan]{name:20}[/cyan] {desc}")
        console.print(f"  [cyan]{'librarian':20}[/cyan] Cross-domain search, knowledge management")
        sys.exit(0)

    router = Router()

    if sys.argv[1] == "--chat":
        # Interactive mode
        console.print(Panel.fit(
            "[bold blue]CrewCFO Multi-Agent System[/bold blue]\n"
            "Ask questions and I'll route them to the right agent.\n\n"
            "[dim]Type 'exit' to quit, 'agents' to list agents[/dim]",
            title="Welcome"
        ))

        while True:
            try:
                query = console.input("\n[bold cyan]You:[/bold cyan] ").strip()

                if not query:
                    continue

                if query.lower() in ("exit", "quit", "q"):
                    console.print("[yellow]Goodbye![/yellow]")
                    break

                if query.lower() == "agents":
                    for name, desc in list_agents().items():
                        console.print(f"  [cyan]{name:20}[/cyan] {desc}")
                    continue

                # Route and execute
                with console.status("[bold green]Thinking..."):
                    result = router.query(query)

                # Show routing decision
                routing = result["routing"]
                agents = ", ".join(routing["agents"])
                console.print(f"\n[dim]Routed to: {agents}[/dim]")
                console.print(f"[dim]Reason: {routing['reasoning']}[/dim]\n")

                # Show responses
                for resp in result["responses"]:
                    if "error" in resp:
                        console.print(f"[red]{resp['agent']}: {resp['error']}[/red]")
                    else:
                        console.print(f"[bold green]{resp['agent'].upper()}:[/bold green]")
                        console.print(Markdown(resp["answer"]))

                        if resp.get("sources"):
                            console.print("\n[dim]Sources:[/dim]")
                            for s in resp["sources"][:3]:
                                if "filename" in s:
                                    console.print(f"  [dim]- {s['filename']}[/dim]")
                                elif "domain" in s:
                                    console.print(f"  [dim]- [{s['domain']}] {s['filename']}[/dim]")

            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

    else:
        # Single query mode
        query = " ".join(sys.argv[1:])
        console.print(f"\n[bold]Query:[/bold] {query}\n")

        with console.status("[bold green]Routing and querying..."):
            result = router.query(query)

        # Show routing
        routing = result["routing"]
        console.print(f"[cyan]Routed to:[/cyan] {', '.join(routing['agents'])}")
        console.print(f"[dim]{routing['reasoning']}[/dim]\n")

        # Show responses
        for resp in result["responses"]:
            if "error" in resp:
                console.print(f"[red]{resp['agent']}: {resp['error']}[/red]")
            else:
                console.print(Panel(
                    Markdown(resp["answer"]),
                    title=f"[bold]{resp['agent'].upper()}[/bold]",
                ))
