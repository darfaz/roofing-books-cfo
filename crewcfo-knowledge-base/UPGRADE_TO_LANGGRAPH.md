# Upgrade to LangGraph Agent

This guide shows how to upgrade from simple RAG to a LangGraph agent that can:
- Search docs AND take actions
- Generate schemas, specs, and task breakdowns
- Maintain conversation state across turns

## Requirements Addition

Add to `requirements.txt`:
```
langgraph==0.2.60
```

## Agent Implementation

Create `agent.py`:

```python
"""
LangGraph agent for CrewCFO planning and spec generation.
"""
import os
import json
from typing import Annotated, TypedDict, List
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from retriever import get_or_create_vectorstore

load_dotenv()

# State definition
class AgentState(TypedDict):
    messages: Annotated[List, add_messages]


# Tools
@tool
def search_knowledge_base(query: str) -> str:
    """Search the CrewCFO knowledge base for relevant documentation.
    Use this to find information about valuation modules, Spec-OS, schemas, etc.
    """
    vectorstore = get_or_create_vectorstore()
    results = vectorstore.similarity_search(query, k=4)
    
    formatted = []
    for i, doc in enumerate(results):
        source = doc.metadata.get("filename", "unknown")
        formatted.append(f"[{source}]\n{doc.page_content}")
    
    return "\n\n---\n\n".join(formatted)


@tool
def generate_database_schema(table_name: str, description: str, columns: List[str]) -> str:
    """Generate a PostgreSQL schema definition for a CrewCFO table.
    
    Args:
        table_name: Name of the table (e.g., 'valuation_snapshots')
        description: What this table stores
        columns: List of column definitions (e.g., ['tenant_id UUID NOT NULL', 'created_at TIMESTAMPTZ'])
    """
    columns_sql = ",\n  ".join(columns)
    schema = f'''-- {description}
CREATE TABLE {table_name} (
  {columns_sql}
);

-- Indexes
CREATE INDEX idx_{table_name}_tenant ON {table_name}(tenant_id);
'''
    return schema


@tool  
def generate_epic_breakdown(
    epic_name: str,
    description: str,
    tasks: List[str],
    estimated_hours: int
) -> str:
    """Generate an Epic/Story breakdown in speckit format.
    
    Args:
        epic_name: Name of the epic (e.g., 'Valuation Engine v1')
        description: What this epic delivers
        tasks: List of task descriptions
        estimated_hours: Total estimated hours
    """
    task_lines = "\n".join([f"  - [ ] {task}" for task in tasks])
    
    return f'''## Epic: {epic_name}

**Description:** {description}

**Estimated Hours:** {estimated_hours}

**Tasks:**
{task_lines}

**Acceptance Criteria:**
- [ ] All tasks completed and tested
- [ ] Documentation updated
- [ ] Code reviewed and merged
'''


@tool
def generate_spec_file(
    feature_name: str,
    purpose: str,
    inputs: List[str],
    outputs: List[str],
    automation_tier: str
) -> str:
    """Generate a feature specification in YAML format.
    
    Args:
        feature_name: Name of the feature
        purpose: What it does
        inputs: List of required inputs
        outputs: List of outputs produced
        automation_tier: 'rules', 'ml', 'llm', or 'hybrid'
    """
    inputs_yaml = "\n".join([f"    - {i}" for i in inputs])
    outputs_yaml = "\n".join([f"    - {o}" for o in outputs])
    
    return f'''# {feature_name} Specification

feature:
  name: {feature_name}
  purpose: {purpose}
  automation_tier: {automation_tier}
  
  inputs:
{inputs_yaml}
  
  outputs:
{outputs_yaml}
  
  human_in_loop:
    threshold: 0.80
    escalation: "Flag for review if confidence < 80%"
'''


# Build the agent
def create_agent():
    """Create LangGraph agent with tools."""
    
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        max_tokens=4096
    )
    
    tools = [
        search_knowledge_base,
        generate_database_schema,
        generate_epic_breakdown,
        generate_spec_file
    ]
    
    llm_with_tools = llm.bind_tools(tools)
    
    # System message
    system = SystemMessage(content="""You are an expert technical architect for CrewCFO, 
an AI-powered bookkeeping and CFO platform for roofing contractors.

You have access to tools to:
1. search_knowledge_base - Find information in project documentation
2. generate_database_schema - Create PostgreSQL schema definitions
3. generate_epic_breakdown - Create Epic/Story breakdowns
4. generate_spec_file - Create feature specifications

When asked about implementation:
1. First search the knowledge base for context
2. Then use appropriate tools to generate artifacts
3. Reference specific features (A-E) and automation tiers from the docs

Always ground your responses in the CrewCFO documentation.""")
    
    def call_model(state: AgentState):
        messages = [system] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: AgentState):
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END
    
    # Build graph
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))
    
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")
    
    # Add memory for conversation persistence
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)


# Usage
def chat_with_agent():
    """Interactive chat with the agent."""
    agent = create_agent()
    config = {"configurable": {"thread_id": "crewcfo-planning"}}
    
    print("CrewCFO Planning Agent")
    print("Type 'exit' to quit\n")
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            break
        
        response = agent.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config
        )
        
        # Get the last AI message
        for msg in reversed(response["messages"]):
            if isinstance(msg, AIMessage) and msg.content:
                print(f"\nAgent: {msg.content}\n")
                break


if __name__ == "__main__":
    chat_with_agent()
```

## Example Interactions

```
You: What schema do I need for the Value Driver Scoring Engine?

Agent: [searches knowledge base, then generates schema]
Based on the documentation, here's the schema for driver scoring:

CREATE TABLE driver_scores (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  as_of_date DATE NOT NULL,
  driver_key VARCHAR(50) NOT NULL,
  score DECIMAL(5,2) CHECK (score >= 0 AND score <= 100),
  evidence_refs JSONB,
  computed_by VARCHAR(20),
  confidence DECIMAL(3,2),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
...
```

```
You: Create an epic breakdown for implementing Feature B

Agent: [generates epic]
## Epic: Value Driver Scoring Engine v1

**Description:** Implement scoring system across 6 Matador-style drivers...

**Tasks:**
- [ ] Define driver_scores schema and migrations
- [ ] Implement financial records quality scorer
- [ ] Build management independence proxy metrics
...
```

## Running the Agent

```bash
# Install langgraph
pip install langgraph

# Run interactive
python agent.py
```

## Key Differences from RAG

| RAG | LangGraph Agent |
|-----|-----------------|
| Search + answer | Search + reason + act |
| Single turn | Multi-turn with memory |
| Text output only | Can generate schemas, specs, code |
| Fixed retrieval | Dynamic tool selection |
