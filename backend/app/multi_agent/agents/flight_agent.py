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
    
    # Specialized prompt for flight agent
    prompt = """You are a flight search expert. Your role is to help users find and compare flights.

Your capabilities:
- Search for flights to specific destinations
- Filter flights by price, airline, or schedule preferences
- Compare different flight options
- Provide recommendations based on user preferences (price, duration, schedule)

When searching for flights:
- Always provide clear, structured information
- Include key details: airline, flight number, price, departure/arrival times, duration
- If the user mentions a budget constraint, use the max_price parameter
- Be helpful in comparing options and making recommendations

Remember: You only handle flight-related queries. For other travel planning needs (activities, weather, budget conversion), those are handled by other specialized agents."""
    
    agent = create_agent(llm, tools, system_prompt=prompt)
    
    if enable_langfuse:
        from app.legacy_agent.main import _get_langfuse_handler
        agent._langfuse_handler = _get_langfuse_handler()
    
    return agent
