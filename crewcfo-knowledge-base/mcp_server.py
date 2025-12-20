#!/usr/bin/env python3
"""
MCP Server for CrewCFO Knowledge Base

This server exposes the CrewCFO knowledge base as MCP tools that can be
used directly from Claude Code.

Installation:
    1. Add to ~/.claude/claude_desktop_config.json:
       {
         "mcpServers": {
           "crewcfo-knowledge": {
             "command": "python",
             "args": ["/path/to/mcp_server.py"],
             "env": {
               "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
             }
           }
         }
       }

    2. Restart Claude Code

Tools provided:
    - search_knowledge: Search the CrewCFO knowledge base
    - ask_agent: Route a query to specialized agents
    - list_domains: List knowledge domains and stats
    - ingest_content: Add new knowledge
    - get_stats: Get knowledge base statistics
"""
import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

# Try to import MCP SDK
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    from mcp.server.stdio import stdio_server
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("MCP SDK not installed. Run: pip install mcp", file=sys.stderr)

from agents.librarian import Librarian
from agents.router import Router
from agents.domain_agents import list_agents
from loader import DOMAIN_CONFIG, get_domain_stats


# =============================================================================
# MCP SERVER
# =============================================================================

if HAS_MCP:

    # Initialize server
    server = Server("crewcfo-knowledge")

    # Lazy-loaded components
    _librarian: Optional[Librarian] = None
    _router: Optional[Router] = None

    def get_librarian() -> Librarian:
        global _librarian
        if _librarian is None:
            _librarian = Librarian()
        return _librarian

    def get_router() -> Router:
        global _router
        if _router is None:
            _router = Router()
        return _router

    # =========================================================================
    # TOOLS
    # =========================================================================

    @server.list_tools()
    async def list_tools():
        """List available tools."""
        return [
            Tool(
                name="search_knowledge",
                description="Search the CrewCFO knowledge base. Optionally filter by domain.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "domain": {
                            "type": "string",
                            "description": "Optional domain filter: software, marketing, outreach, valuation, accounting, sales, roofing_industry",
                            "enum": list(DOMAIN_CONFIG.keys())
                        },
                        "k": {
                            "type": "integer",
                            "description": "Number of results (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="ask_agent",
                description="Route a question to the appropriate specialized agent for a detailed answer.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The question to ask"
                        },
                        "agent": {
                            "type": "string",
                            "description": "Specific agent to use (optional, auto-routes if not specified)",
                            "enum": ["auto", "librarian", "software", "marketing", "outreach", "valuation", "accounting", "sales", "roofing_industry"]
                        }
                    },
                    "required": ["question"]
                }
            ),
            Tool(
                name="list_domains",
                description="List all knowledge domains with descriptions and document counts.",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="ingest_content",
                description="Add new content to the knowledge base. Auto-classifies to appropriate domain.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The content to add"
                        },
                        "title": {
                            "type": "string",
                            "description": "Title for the content"
                        },
                        "domain": {
                            "type": "string",
                            "description": "Target domain (optional, auto-classifies if not specified)",
                            "enum": list(DOMAIN_CONFIG.keys())
                        }
                    },
                    "required": ["content", "title"]
                }
            ),
            Tool(
                name="get_stats",
                description="Get statistics about the knowledge base.",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="classify_content",
                description="Classify content into the most appropriate domain without adding it.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The content to classify"
                        }
                    },
                    "required": ["content"]
                }
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        """Handle tool calls."""

        if name == "search_knowledge":
            query = arguments.get("query", "")
            domain = arguments.get("domain")
            k = arguments.get("k", 5)

            librarian = get_librarian()
            results = librarian.search(query, domain=domain, k=k)

            if not results:
                return [TextContent(
                    type="text",
                    text=f"No results found for: {query}"
                )]

            # Format results
            formatted = []
            for i, doc in enumerate(results, 1):
                domain = doc.metadata.get("domain", "unknown")
                filename = doc.metadata.get("filename", "unknown")
                preview = doc.page_content[:300]
                formatted.append(f"**[{i}] [{domain}] {filename}**\n{preview}...")

            return [TextContent(
                type="text",
                text="\n\n---\n\n".join(formatted)
            )]

        elif name == "ask_agent":
            question = arguments.get("question", "")
            agent = arguments.get("agent", "auto")

            router = get_router()

            if agent == "auto":
                result = router.query(question)
            else:
                result = router.query(question, auto_route=False, agents=[agent])

            # Format response
            routing = result.get("routing", {})
            responses = result.get("responses", [])

            output = f"**Routed to:** {', '.join(routing.get('agents', []))}\n"
            output += f"*{routing.get('reasoning', '')}*\n\n"

            for resp in responses:
                if "error" in resp:
                    output += f"**{resp['agent'].upper()}:** Error - {resp['error']}\n"
                else:
                    output += f"**{resp['agent'].upper()}:**\n{resp['answer']}\n\n"
                    if resp.get("sources"):
                        output += "Sources:\n"
                        for s in resp["sources"][:3]:
                            output += f"- {s.get('filename', 'unknown')}\n"

            return [TextContent(type="text", text=output)]

        elif name == "list_domains":
            stats = get_domain_stats()

            output = "## CrewCFO Knowledge Domains\n\n"
            for domain, config in DOMAIN_CONFIG.items():
                count = stats.get(domain, 0)
                desc = config.get("description", "")
                output += f"- **{domain}** ({count} files): {desc}\n"

            output += "\n## Available Agents\n\n"
            for name, desc in list_agents().items():
                output += f"- **{name}**: {desc}\n"

            return [TextContent(type="text", text=output)]

        elif name == "ingest_content":
            content = arguments.get("content", "")
            title = arguments.get("title", "Untitled")
            domain = arguments.get("domain")

            librarian = get_librarian()
            result = librarian.ingest_text(content, title, domain)

            if result.get("success"):
                return [TextContent(
                    type="text",
                    text=f"✅ Added to **{result['domain']}**: {result['file']}\n*{result['reasoning']}*"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Failed: {result.get('error', 'Unknown error')}"
                )]

        elif name == "get_stats":
            librarian = get_librarian()
            stats = librarian.get_stats()

            output = "## Knowledge Base Statistics\n\n"
            output += f"**Total Files:** {stats['total_files']}\n"
            output += f"**Total Chunks:** {stats['total_chunks']}\n\n"

            output += "### Files by Domain\n"
            for domain, count in sorted(stats["files_by_domain"].items()):
                output += f"- {domain}: {count}\n"

            output += "\n### Chunks by Domain\n"
            for domain, count in sorted(stats["chunks_by_domain"].items()):
                output += f"- {domain}: {count}\n"

            return [TextContent(type="text", text=output)]

        elif name == "classify_content":
            content = arguments.get("content", "")

            librarian = get_librarian()
            domain, reasoning = librarian.classify_content(content)

            return [TextContent(
                type="text",
                text=f"**Classification:** {domain}\n**Reasoning:** {reasoning}"
            )]

        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]


# =============================================================================
# MAIN
# =============================================================================

async def main():
    """Run the MCP server."""
    if not HAS_MCP:
        print("MCP SDK not installed. Install with: pip install mcp")
        sys.exit(1)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing MCP server components...")

        # Test librarian
        librarian = Librarian()
        stats = librarian.get_stats()
        print(f"✓ Librarian loaded: {stats['total_files']} files, {stats['total_chunks']} chunks")

        # Test router
        router = Router()
        routing = router.route("What are the valuation multiples?")
        print(f"✓ Router working: routes to {routing['agents']}")

        print("\n✅ All components working!")
        print("\nTo use with Claude Code, add this to ~/.claude/claude_desktop_config.json:")
        print(json.dumps({
            "mcpServers": {
                "crewcfo-knowledge": {
                    "command": "python",
                    "args": [str(Path(__file__).absolute())],
                    "env": {
                        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
                    }
                }
            }
        }, indent=2))

    else:
        asyncio.run(main())
