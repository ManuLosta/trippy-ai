"""Supervisor Agent - Coordinates specialized agents using Tool Calling pattern."""

import os
from typing import Annotated
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from app.multi_agent.agents.flight_agent import create_flight_agent
from app.multi_agent.agents.activity_agent import create_activity_agent
from app.multi_agent.agents.weather_agent import create_weather_agent
from app.multi_agent.agents.budget_agent import create_budget_agent

from app.legacy_agent.main import _get_langfuse_handler


# Initialize specialized agents (lazy initialization)
_flight_agent = None
_activity_agent = None
_weather_agent = None
_budget_agent = None


def _get_flight_agent():
    """Lazy initialization of flight agent."""
    global _flight_agent
    if _flight_agent is None:
        _flight_agent = create_flight_agent()
    return _flight_agent


def _get_activity_agent():
    """Lazy initialization of activity agent."""
    global _activity_agent
    if _activity_agent is None:
        _activity_agent = create_activity_agent()
    return _activity_agent


def _get_weather_agent():
    """Lazy initialization of weather agent."""
    global _weather_agent
    if _weather_agent is None:
        _weather_agent = create_weather_agent()
    return _weather_agent


def _get_budget_agent():
    """Lazy initialization of budget agent."""
    global _budget_agent
    if _budget_agent is None:
        _budget_agent = create_budget_agent()
    return _budget_agent


@tool(
    "flight_agent",
    description="""Use this agent when the user needs to:
- Search for flights to a destination
- Compare flight options
- Filter flights by price, airline, or schedule
- Get flight recommendations

This agent specializes in finding and comparing flights from Buenos Aires to various destinations."""
)
def call_flight_agent(query: str) -> str:
    """Call the flight agent to handle flight-related queries."""
    try:
        agent = _get_flight_agent()
        result = agent.invoke({
            "messages": [HumanMessage(content=query)]
        })
        # Extract the final message content
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, 'content'):
                return str(last_message.content)
        return str(result)
    except Exception as e:
        return f"Error in flight agent: {str(e)}"


@tool(
    "activity_agent",
    description="""Use this agent when the user needs to:
- Search for activities and attractions in a city
- Find activities by category (culture, adventure, gastronomy, etc.)
- Get activity recommendations
- Learn about things to do in a destination

This agent specializes in discovering and recommending activities and attractions."""
)
def call_activity_agent(query: str) -> str:
    """Call the activity agent to handle activity-related queries."""
    try:
        agent = _get_activity_agent()
        result = agent.invoke({
            "messages": [HumanMessage(content=query)]
        })
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, 'content'):
                return str(last_message.content)
        return str(result)
    except Exception as e:
        return f"Error in activity agent: {str(e)}"


@tool(
    "weather_agent",
    description="""Use this agent when the user needs to:
- Get weather forecasts for a city
- Plan activities based on weather conditions
- Understand how weather affects travel plans
- Get daily weather information for trip planning

This agent specializes in weather forecasts and weather-based activity planning."""
)
def call_weather_agent(query: str) -> str:
    """Call the weather agent to handle weather-related queries."""
    try:
        agent = _get_weather_agent()
        result = agent.invoke({
            "messages": [HumanMessage(content=query)]
        })
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, 'content'):
                return str(last_message.content)
        return str(result)
    except Exception as e:
        return f"Error in weather agent: {str(e)}"


@tool(
    "budget_agent",
    description="""Use this agent when the user needs to:
- Convert currencies (USD to ARS)
- Calculate travel costs
- Understand budget in different currencies
- Get budget-related information

This agent specializes in currency conversion and budget calculations."""
)
def call_budget_agent(query: str) -> str:
    """Call the budget agent to handle budget-related queries."""
    try:
        agent = _get_budget_agent()
        result = agent.invoke({
            "messages": [HumanMessage(content=query)]
        })
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, 'content'):
                return str(last_message.content)
        return str(result)
    except Exception as e:
        return f"Error in budget agent: {str(e)}"




# Use a small/fast model for routing to save tokens and latency (optional)
_SUPERVISOR_MODEL = os.getenv("OPENROUTER_FAST_MODEL") or os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")


def create_supervisor_agent(enable_langfuse: bool = True):
    """Create the supervisor agent that coordinates all specialized agents.
    
    The supervisor uses the Tool Calling pattern, where each specialized agent
    is exposed as a tool that the supervisor can invoke when needed.
    Uses OPENROUTER_FAST_MODEL when set (e.g. openai/gpt-4o-mini) to reduce tokens and latency.
    
    Args:
        enable_langfuse: If True, enables Langfuse tracing if configured.
    
    Returns:
        A LangChain agent configured as the supervisor.
    """
    llm = ChatOpenAI(
        model=_SUPERVISOR_MODEL,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.2,  # Low for consistent routing
    )
    
    # All specialized agents as tools
    tools = [
        call_flight_agent,
        call_activity_agent,
        call_weather_agent,
        call_budget_agent,
    ]
    
    prompt = """Travel planning coordinator. You route to the right agent(s):
- flight_agent: search/compare flights, filter by price or schedule
- activity_agent: activities, itineraries, recommendations, route optimization
- weather_agent: forecasts, plan by weather
- budget_agent: USD↔ARS conversion, budget allocation

Call only agents needed (single query → one agent when possible). Synthesize results clearly."""
    
    agent = create_agent(llm, tools, system_prompt=prompt)
    
    if enable_langfuse:
        agent._langfuse_handler = _get_langfuse_handler()
    
    return agent


def invoke_with_langfuse(agent, input_data):
    """Invoke the supervisor agent with Langfuse tracing if available.
    
    Args:
        agent: The supervisor agent returned by create_supervisor_agent
        input_data: Input data (dict with "messages" key for LangChain agents)
    
    Returns:
        Agent response
    """
    langfuse_handler = getattr(agent, '_langfuse_handler', None)
    
    if langfuse_handler:
        config = RunnableConfig(callbacks=[langfuse_handler])
        return agent.invoke(input_data, config=config)
    else:
        return agent.invoke(input_data)
