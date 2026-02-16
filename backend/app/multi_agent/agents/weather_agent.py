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
    # Use fast model when set (weather is simple: one tool, minimal reasoning)
    model = os.getenv("OPENROUTER_FAST_MODEL") or os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
    llm = ChatOpenAI(
        model=model,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.2,
    )
    
    tools = [get_weather]
    
    prompt = """Weather expert. Use get_weather. Return temps, conditions, precipitation. Use the number of days the user asks for. Give brief activity advice (e.g. indoor if rain)."""
    
    agent = create_agent(llm, tools, system_prompt=prompt)
    
    if enable_langfuse:
        from app.legacy_agent.main import _get_langfuse_handler
        agent._langfuse_handler = _get_langfuse_handler()
    
    return agent
