"""Activity Agent - Specialized agent for activity search, itineraries, and recommendations."""

import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from app.multi_agent.tools.shared_tools import search_activities
from app.multi_agent.tools.itinerary_tools import plan_itinerary, optimize_route
from app.multi_agent.tools.recommendation_tools import get_recommendations


def create_activity_agent(enable_langfuse: bool = True):
    """Create a specialized activity agent.
    
    This agent is an expert in:
    - Searching for activities and attractions
    - Creating optimized day-by-day travel itineraries
    - Optimizing routes and activity order
    - Providing personalized recommendations based on preferences and budget
    
    Args:
        enable_langfuse: If True, enables Langfuse tracing if configured.
    
    Returns:
        A LangChain agent configured for activity-related tasks.
    """
    llm = ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.5,  # Slightly higher for more creative recommendations
    )
    
    tools = [search_activities, plan_itinerary, optimize_route, get_recommendations]
    
    # Specialized prompt for activity agent
    prompt = """You are an activity, itinerary, and recommendation expert. Your role is to:

1. Search for activities and attractions in cities
2. Create optimized day-by-day travel itineraries
3. Optimize routes and activity order
4. Provide personalized recommendations based on preferences and budget

Your capabilities:
- Search activities by category (culture, adventure, gastronomy, etc.)
- Plan detailed itineraries considering location, weather, and preferences
- Optimize activity routes to minimize travel time
- Rank and recommend activities based on user preferences
- Consider budget constraints in recommendations

Guidelines:
- Provide comprehensive activity information
- Create practical, well-organized itineraries
- Consider weather conditions when planning
- Balance free and paid activities
- Optimize for user preferences and constraints

Remember: You only handle activity-related queries, itineraries, and recommendations. For other travel planning needs (flights, weather, budget conversion), those are handled by other specialized agents."""
    
    agent = create_agent(llm, tools, system_prompt=prompt)
    
    if enable_langfuse:
        from app.legacy_agent.main import _get_langfuse_handler
        agent._langfuse_handler = _get_langfuse_handler()
    
    return agent
