"""Flight Agent - Specialized agent for flight search and comparison."""

import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from app.multi_agent.tools.shared_tools import search_flights


def create_flight_agent(enable_langfuse: bool = True):
    """Create a specialized flight agent.
    
    This agent is an expert in:
    - Searching and comparing flights
    - Filtering by price, airline, schedules
    - Providing flight recommendations
    
    Args:
        enable_langfuse: If True, enables Langfuse tracing if configured.
    
    Returns:
        A LangChain agent configured for flight-related tasks.
    """
    llm = ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.3,  # Lower temperature for more consistent flight search
    )
    
    tools = [search_flights]
    
    prompt = """Flight search expert. Use search_flights. Return: airline, price, departure/arrival, duration. Use max_price when user has a budget. Compare options briefly."""
    
    agent = create_agent(llm, tools, system_prompt=prompt)
    
    if enable_langfuse:
        from app.legacy_agent.main import _get_langfuse_handler
        agent._langfuse_handler = _get_langfuse_handler()
    
    return agent
