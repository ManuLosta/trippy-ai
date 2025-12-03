from langchain_google_genai import ChatGoogleGenerativeAI
from agent.main import search_flights, search_activities, get_weather, convert_usd_to_ars
from langchain.agents import create_agent 
from langchain.messages import HumanMessage
import os
from dotenv import load_dotenv
load_dotenv()

def create_travel_agent():
    """Create the travel agent with LangGraph using create_react_agent."""

    # Initialize Google Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # Define tools
    tools = [search_flights, search_activities, get_weather, convert_usd_to_ars]

    # Create the agent using the recommended pattern
    agent = create_agent(llm, tools)

    return agent


agent = create_travel_agent()
user_message = "Quiero viajar a Madrid por 3 días. Busca vuelos disponibles, actividades culturales y el pronóstico del clima para planificar qué hacer cada día. También convierte los costos a pesos argentinos."
response = agent.invoke({"messages": [HumanMessage(content=user_message)]})
for message in response["messages"]:
    if hasattr(message, 'content') and message.content:
        print(message.content)