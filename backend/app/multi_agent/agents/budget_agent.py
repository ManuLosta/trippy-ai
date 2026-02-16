"""Budget Agent - Specialized agent for currency conversion and budget management."""

import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from app.multi_agent.tools.shared_tools import convert_usd_to_ars
from app.multi_agent.tools.recommendation_tools import optimize_budget


def create_budget_agent(enable_langfuse: bool = True):
    """Create a specialized budget agent.
    
    This agent is an expert in:
    - Currency conversion (USD to ARS)
    - Budget optimization and distribution
    - Cost analysis for travel planning
    
    Args:
        enable_langfuse: If True, enables Langfuse tracing if configured.
    
    Returns:
        A LangChain agent configured for budget-related tasks.
    """
    # Use fast model when set (budget is mostly tool calls: convert + optimize)
    model = os.getenv("OPENROUTER_FAST_MODEL") or os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
    llm = ChatOpenAI(
        model=model,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.2,
    )
    
    tools = [convert_usd_to_ars, optimize_budget]
    
    prompt = """Budget expert. Use convert_usd_to_ars for USD→ARS; use optimize_budget for allocation. Give precise numbers and a clear breakdown (flights, activities, food, accommodation)."""
    
    agent = create_agent(llm, tools, system_prompt=prompt)
    
    if enable_langfuse:
        from app.legacy_agent.main import _get_langfuse_handler
        agent._langfuse_handler = _get_langfuse_handler()
    
    return agent
