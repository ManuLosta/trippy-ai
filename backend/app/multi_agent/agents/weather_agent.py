"""Weather Agent - Specialized agent for weather forecasts and activity planning."""

import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from app.multi_agent.tools.shared_tools import get_weather


def create_weather_agent(enable_langfuse: bool = True):
    """Create a specialized weather agent.
    
    This agent is an expert in:
    - Providing detailed weather forecasts
    - Recommending activities based on weather conditions
    - Planning daily activities according to weather
    
    Args:
        enable_langfuse: If True, enables Langfuse tracing if configured.
    
    Returns:
        A LangChain agent configured for weather-related tasks.
    """
    llm = ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.3,  # Lower temperature for factual weather information
    )
    
    tools = [get_weather]
    
    # Specialized prompt for weather agent
    prompt = """You are a weather and activity planning expert. Your role is to provide weather forecasts and help users plan activities based on weather conditions.

Your capabilities:
- Get detailed weather forecasts for cities
- Provide activity recommendations based on weather conditions
- Help plan daily itineraries considering weather
- Explain how weather affects different types of activities

When providing weather information:
- Always include temperature ranges, weather conditions, and precipitation
- Provide specific activity advice based on weather (e.g., "indoor activities recommended" for rain)
- If the user mentions a specific number of days, use that for the forecast
- Help users understand which activities are suitable for the forecasted weather

Remember: You only handle weather-related queries. For other travel planning needs (flights, activities, budget conversion), those are handled by other specialized agents."""
    
    agent = create_agent(llm, tools, system_prompt=prompt)
    
    if enable_langfuse:
        from app.legacy_agent.main import _get_langfuse_handler
        agent._langfuse_handler = _get_langfuse_handler()
    
    return agent
