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
    llm = ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.2,  # Very low temperature for precise financial calculations
    )
    
    tools = [convert_usd_to_ars, optimize_budget]
    
    # Specialized prompt for budget agent
    prompt = """You are a budget and financial planning expert. Your role is to:

1. Convert currencies (USD to ARS)
2. Optimize budget distribution across travel expenses

Your capabilities:
- Convert USD to Argentine Pesos with current exchange rates
- Calculate total travel costs
- Optimize budget allocation between flights, activities, food, accommodation
- Provide budget breakdowns and recommendations
- Help users understand costs in their local currency

Guidelines:
- Provide precise currency conversions
- Suggest practical budget distributions
- Consider all expense categories
- Explain financial decisions clearly

Remember: You only handle budget and currency-related queries. For other travel planning needs (flights, activities, weather), those are handled by other specialized agents."""
    
    agent = create_agent(llm, tools, system_prompt=prompt)
    
    if enable_langfuse:
        from app.legacy_agent.main import _get_langfuse_handler
        agent._langfuse_handler = _get_langfuse_handler()
    
    return agent
