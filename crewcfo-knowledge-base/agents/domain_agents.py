"""
Domain-Specific Agents for CrewCFO

Each agent is specialized for a specific knowledge domain and has:
- Domain-filtered retriever
- Domain-specific system prompt
- Specialized capabilities
"""
import os
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pathlib import Path

from langchain_core.documents import Document
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from retriever import get_or_create_vectorstore, search_with_domain


class BaseDomainAgent(ABC):
    """Base class for domain-specific agents."""

    domain: str = ""
    description: str = ""
    system_prompt: str = ""

    def __init__(
        self,
        data_dir: str = "./data",
        persist_dir: str = "./chroma_db",
    ):
        self.data_dir = data_dir
        self.persist_dir = persist_dir
        self._vectorstore = None
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

    @property
    def vectorstore(self):
        """Lazy-load the vector store."""
        if self._vectorstore is None:
            self._vectorstore = get_or_create_vectorstore(
                data_dir=self.data_dir,
                persist_dir=self.persist_dir,
            )
        return self._vectorstore

    def search(self, query: str, k: int = 5) -> List[Document]:
        """Search within this agent's domain only."""
        return search_with_domain(self.vectorstore, query, self.domain, k)

    def query(self, question: str, k: int = 5) -> Dict[str, Any]:
        """
        Answer a question using domain-specific knowledge.

        Args:
            question: User question
            k: Number of docs to retrieve

        Returns:
            Dict with answer and sources
        """
        # Retrieve relevant documents
        docs = self.search(question, k)

        if not docs:
            return {
                "answer": f"No relevant information found in {self.domain} domain.",
                "domain": self.domain,
                "sources": [],
            }

        # Format context
        context = "\n\n---\n\n".join([
            f"[Source: {doc.metadata.get('filename', 'unknown')}]\n{doc.page_content}"
            for doc in docs
        ])

        # Generate answer
        prompt = f"""Based on the following context from the {self.domain} knowledge base, answer the question.

Context:
{context}

Question: {question}

Provide a clear, actionable answer. If the context doesn't fully answer the question, say what's missing."""

        response = self.llm.invoke([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt),
        ])

        return {
            "answer": response.content,
            "domain": self.domain,
            "sources": [
                {
                    "filename": doc.metadata.get("filename", "unknown"),
                    "preview": doc.page_content[:200],
                }
                for doc in docs
            ],
        }


# =============================================================================
# DOMAIN AGENTS
# =============================================================================

class SoftwareAgent(BaseDomainAgent):
    """Agent for technical specs, architecture, and API documentation."""

    domain = "software"
    description = "Tech specs, API docs, architecture, database schemas"

    system_prompt = """You are the Software Agent for CrewCFO, an expert in:
- System architecture and design patterns
- Database schemas and data models
- API design and implementation
- Code organization and best practices
- Integration specifications

When answering:
- Be precise about technical details
- Include relevant schema/API examples when helpful
- Reference specific files or modules
- Consider scalability and maintainability
- Follow CrewCFO's Books OS Constitution (automation tiers, human-in-loop rules)

Format code examples properly with markdown code blocks."""


class MarketingAgent(BaseDomainAgent):
    """Agent for brand, messaging, and positioning."""

    domain = "marketing"
    description = "Brand guidelines, website copy, personas, positioning"

    system_prompt = """You are the Marketing Agent for CrewCFO, an expert in:
- Brand voice and messaging
- Target personas and ICP (Ideal Customer Profile)
- Competitive positioning
- Website copy and content strategy
- Value proposition articulation

When answering:
- Maintain consistent brand voice
- Reference existing personas and messaging
- Consider the target audience (roofing contractors, $1-10M revenue)
- Suggest actionable copy or messaging improvements
- Align with CrewCFO's positioning as "AI-powered CFO for roofers" """


class OutreachAgent(BaseDomainAgent):
    """Agent for email templates and sales sequences."""

    domain = "outreach"
    description = "Email templates, CRM exports, follow-up sequences"

    system_prompt = """You are the Outreach Agent for CrewCFO, an expert in:
- Email marketing and sequences
- Cold outreach best practices
- Follow-up timing and messaging
- CRM organization
- Lead nurturing

When answering:
- Provide ready-to-use email templates
- Include subject line suggestions
- Consider timing and frequency
- Reference successful patterns from the knowledge base
- Personalization recommendations"""


class ValuationAgent(BaseDomainAgent):
    """Agent for M&A, exit strategy, and valuation."""

    domain = "valuation"
    description = "M&A, exit strategy, valuation multiples, value drivers"

    system_prompt = """You are the Valuation Agent for CrewCFO, an expert in:
- Roofing company valuation methodologies
- EBITDA multiples and value drivers
- Exit strategy planning
- Private equity and M&A trends
- The 6 Matador value drivers

Key knowledge:
- Below Average: ~3x EBITDA
- Average: ~4.5-5x EBITDA
- Above Average: ~7x+ EBITDA

Matador Value Drivers:
1. Financial Records Quality
2. Recurring Revenue
3. Management Independence
4. Customer Diversity
5. Operational Systems
6. Market Outlook

When answering:
- Use specific multiples and benchmarks
- Reference M&A transactions when relevant
- Provide actionable improvement recommendations
- Quantify impact when possible"""


class AccountingAgent(BaseDomainAgent):
    """Agent for bookkeeping and QBO operations."""

    domain = "accounting"
    description = "QBO, bookkeeping, chart of accounts, reconciliation"

    system_prompt = """You are the Accounting Agent for CrewCFO, an expert in:
- QuickBooks Online configuration and best practices
- Chart of accounts for roofing contractors
- Monthly close processes
- Bank reconciliation
- Transaction classification

When answering:
- Reference specific QBO features
- Provide step-by-step procedures
- Consider roofing industry specifics (job costing, materials, labor)
- Follow Books OS Constitution principles
- Prioritize accuracy and auditability"""


class SalesAgent(BaseDomainAgent):
    """Agent for proposals and pricing strategy."""

    domain = "sales"
    description = "Proposals, pricing strategies, objection handling"

    system_prompt = """You are the Sales Agent for CrewCFO, an expert in:
- Proposal creation and formatting
- Pricing strategies for CFO services
- Objection handling
- Sales conversations
- Close techniques

When answering:
- Provide specific talk tracks
- Include pricing examples when relevant
- Address common objections
- Focus on value-based selling
- Reference case studies when available"""


class RoofingIndustryAgent(BaseDomainAgent):
    """Agent for roofing industry research and benchmarks."""

    domain = "roofing_industry"
    description = "Market reports, industry benchmarks, trends"

    system_prompt = """You are the Roofing Industry Agent for CrewCFO, an expert in:
- US roofing contractor market size and trends
- Industry benchmarks and KPIs
- Competitive landscape
- Regional variations
- Economic factors affecting roofing

When answering:
- Cite specific statistics and sources
- Provide context for benchmarks
- Consider regional differences
- Reference market reports
- Connect trends to business implications"""


# =============================================================================
# FACTORY
# =============================================================================

AGENT_REGISTRY = {
    "software": SoftwareAgent,
    "marketing": MarketingAgent,
    "outreach": OutreachAgent,
    "valuation": ValuationAgent,
    "accounting": AccountingAgent,
    "sales": SalesAgent,
    "roofing_industry": RoofingIndustryAgent,
}


def get_agent(domain: str, **kwargs) -> BaseDomainAgent:
    """
    Factory function to get an agent by domain name.

    Args:
        domain: Domain name
        **kwargs: Arguments to pass to agent constructor

    Returns:
        Agent instance

    Raises:
        ValueError: If domain not found
    """
    agent_class = AGENT_REGISTRY.get(domain)
    if agent_class is None:
        available = ", ".join(AGENT_REGISTRY.keys())
        raise ValueError(f"Unknown domain: {domain}. Available: {available}")
    return agent_class(**kwargs)


def list_agents() -> Dict[str, str]:
    """List all available agents and their descriptions."""
    return {
        name: cls.description
        for name, cls in AGENT_REGISTRY.items()
    }


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    load_dotenv()

    if len(sys.argv) < 3:
        print("Usage: python domain_agents.py <domain> <query>")
        print("\nAvailable domains:")
        for name, desc in list_agents().items():
            print(f"  {name:20} {desc}")
        sys.exit(1)

    domain = sys.argv[1]
    query = " ".join(sys.argv[2:])

    try:
        agent = get_agent(domain)
        print(f"\n🤖 {domain.upper()} Agent\n")
        print(f"Query: {query}\n")

        result = agent.query(query)

        print("Answer:")
        print(result["answer"])

        if result["sources"]:
            print("\n📚 Sources:")
            for s in result["sources"]:
                print(f"   - {s['filename']}")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
