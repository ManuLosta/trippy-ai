import os
from typing import Optional
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langfuse.langchain  import CallbackHandler
import pandas as pd
import requests
from dotenv import load_dotenv
load_dotenv()


def search_flights(destination: str, max_price: Optional[float] = None) -> str:
    """Search for flights to a specific destination from Buenos Aires.

    Args:
        destination: The destination city
        max_price: Optional maximum price filter in USD

    Returns:
        String with available flights information
    """
    try:
        df = pd.read_csv('data/flights.csv')
        flights = df[df['destination'].str.contains(destination, case=False, na=False)]

        if max_price:
            flights = flights[flights['price_usd'] <= max_price]

        if flights.empty:
            return f"No flights found to {destination}"

        result = f"Found {len(flights)} flights to {destination}:\n"
        for _, flight in flights.iterrows():
            result += f"- {flight['airline']} {flight['flight_number']}: ${flight['price_usd']} "
            result += f"({flight['departure_time']} - {flight['arrival_time']}, {flight['duration_hours']}h)\n"

        return result
    except Exception as e:
        return f"Error searching flights: {str(e)}"



def search_activities(city: str, category: Optional[str] = None) -> str:
    """Search for activities and attractions in a specific city.

    Args:
        city: The city name
        category: Optional category filter (cultura, aventura, gastronomia, etc.)

    Returns:
        String with available activities information
    """
    try:
        df = pd.read_csv('data/activities.csv')
        activities = df[df['city'].str.contains(city, case=False, na=False)]

        if category:
            activities = activities[activities['category'].str.contains(category, case=False, na=False)]

        if activities.empty:
            return f"No activities found in {city}"

        result = f"Found {len(activities)} activities in {city}:\n"
        for _, activity in activities.iterrows():
            cost_str = f"${activity['cost_usd']}" if activity['cost_usd'] > 0 else "Free"
            result += f"- {activity['activity_name']}: {cost_str} "
            result += f"({activity['category']}, ideal weather: {activity['ideal_weather']})\n"
            result += f"  {activity['description']}\n"

        return result
    except Exception as e:
        return f"Error searching activities: {str(e)}"


def get_weather(city: str, days: int = 5) -> str:
    """Get weather forecast for a city using Open-Meteo API to plan daily activities.

    Args:
        city: The city name
        days: Number of days to forecast (default: 5)

    Returns:
        String with daily weather forecast for activity planning
    """
    try:
        # City coordinates mapping (simplified for demo)
        city_coords = {
            'madrid': (40.4168, -3.7038),
            'new york': (40.7128, -74.0060),
            'miami': (25.7617, -80.1918),
            'santiago': (-33.4489, -70.6693),
            'lima': (-12.0464, -77.0428),
            'rio de janeiro': (-22.9068, -43.1729),
            'paris': (48.8566, 2.3522),
            'barcelona': (41.3851, 2.1734),
            'rome': (41.9028, 12.4964),
            'london': (51.5074, -0.1278)
        }

        city_lower = city.lower()
        if city_lower not in city_coords:
            return f"Weather data not available for {city}"

        lat, lon = city_coords[city_lower]

        # Open-Meteo API call for forecast
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum&timezone=auto&forecast_days={days}"
        response = requests.get(url)
        data = response.json()

        if 'daily' in data:
            daily = data['daily']
            dates = daily['time']
            max_temps = daily['temperature_2m_max']
            min_temps = daily['temperature_2m_min']
            weather_codes = daily['weather_code']
            precipitation = daily.get('precipitation_sum', [0] * len(dates))

            # Map weather codes to conditions and activity recommendations
            weather_conditions = {
                0: ("sunny", "Perfect for outdoor activities, sightseeing, and walking tours"),
                1: ("mostly sunny", "Great for outdoor activities and sightseeing"),
                2: ("partly cloudy", "Good for outdoor activities, some cloud cover"),
                3: ("cloudy", "Suitable for indoor activities and museums"),
                45: ("foggy", "Be careful with outdoor activities, reduced visibility"),
                48: ("foggy", "Be careful with outdoor activities, reduced visibility"),
                51: ("light rain", "Indoor activities recommended, bring umbrella"),
                53: ("light rain", "Indoor activities recommended, bring umbrella"),
                55: ("moderate rain", "Indoor activities recommended, avoid outdoor plans"),
                61: ("rain", "Indoor activities recommended, avoid outdoor plans"),
                63: ("rain", "Indoor activities recommended, avoid outdoor plans"),
                65: ("heavy rain", "Indoor activities only, avoid outdoor plans"),
                71: ("snow", "Indoor activities recommended, winter conditions"),
                73: ("snow", "Indoor activities recommended, winter conditions"),
                75: ("heavy snow", "Indoor activities only, winter conditions"),
                77: ("snow grains", "Indoor activities recommended, winter conditions"),
                80: ("rain showers", "Indoor activities recommended, bring umbrella"),
                81: ("rain showers", "Indoor activities recommended, bring umbrella"),
                82: ("heavy rain showers", "Indoor activities only, avoid outdoor plans"),
                85: ("snow showers", "Indoor activities recommended, winter conditions"),
                86: ("heavy snow showers", "Indoor activities only, winter conditions"),
                95: ("thunderstorm", "Indoor activities only, avoid outdoor plans"),
                96: ("thunderstorm with hail", "Indoor activities only, avoid outdoor plans"),
                99: ("thunderstorm with heavy hail", "Indoor activities only, avoid outdoor plans")
            }

            result = f"{days}-Day Weather Forecast for {city.title()}:\n\n"

            for i in range(len(dates)):
                date = dates[i]
                max_temp = max_temps[i]
                min_temp = min_temps[i]
                weather_code = weather_codes[i]
                precip = precipitation[i] if i < len(precipitation) else 0

                condition, activity_advice = weather_conditions.get(weather_code, ("unknown", "Check weather conditions before planning"))

                # Format date nicely
                from datetime import datetime
                try:
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%A, %B %d")
                except:
                    formatted_date = date

                result += f"{formatted_date}:\n"
                result += f"   Temperature: {min_temp}°C - {max_temp}°C\n"
                result += f"   Weather: {condition}\n"
                if precip > 0:
                    result += f"   Precipitation: {precip}mm\n"
                result += f"   Activity Advice: {activity_advice}\n\n"

            return result
        else:
            return f"Weather forecast not available for {city}"

    except Exception as e:
        return f"Error getting weather forecast: {str(e)}"



def convert_usd_to_ars(amount_usd: float) -> str:
    """Convert USD amount to Argentine Pesos using current exchange rate.

    Args:
        amount_usd: Amount in USD to convert

    Returns:
        String with conversion result
    """
    try:
        # Using ExchangeRate-API (free tier)
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url)
        data = response.json()

        if 'rates' in data and 'ARS' in data['rates']:
            rate = data['rates']['ARS']
            amount_ars = amount_usd * rate
            return f"${amount_usd:.2f} USD = ${amount_ars:.2f} ARS (rate: {rate:.2f})"
        else:
            # Fallback rate if API fails
            fallback_rate = 1000  # Approximate rate
            amount_ars = amount_usd * fallback_rate
            return f"${amount_usd:.2f} USD = ${amount_ars:.2f} ARS (approximate rate: {fallback_rate})"

    except Exception as e:
        # Fallback rate if API fails
        fallback_rate = 1000
        amount_ars = amount_usd * fallback_rate
        return f"${amount_usd:.2f} USD = ${amount_ars:.2f} ARS (approximate rate: {fallback_rate})"



def _get_langfuse_handler():
    """Create and return a Langfuse callback handler if credentials are configured.
    
    The CallbackHandler automatically reads credentials from environment variables:
    - LANGFUSE_SECRET_KEY
    - LANGFUSE_PUBLIC_KEY
    - LANGFUSE_HOST (optional, defaults to https://cloud.langfuse.com)
    """
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    
    if not secret_key or not public_key:
        return None
    
    try:
        # CallbackHandler automatically reads from environment variables
        return CallbackHandler()
    except Exception as e:
        print(f"Warning: Failed to initialize Langfuse callback handler: {e}")
        return None


def create_legacy_agent(enable_langfuse: bool = True):
    """Create a legacy agent with optional Langfuse tracing.
    
    Args:
        enable_langfuse: If True, enables Langfuse tracing if credentials are configured.
                        Defaults to True.
    
    Returns:
        A LangChain agent configured with the LLM and tools.
    """
    llm = ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
    )

    tools = [search_flights, search_activities, get_weather, convert_usd_to_ars]

    agent = create_agent(llm, tools)
    
    # Store langfuse handler for later use
    if enable_langfuse:
        agent._langfuse_handler = _get_langfuse_handler()
    
    return agent


def invoke_with_langfuse(agent, input_data):
    """Invoke the agent with Langfuse tracing if available.
    
    Args:
        agent: The agent returned by create_legacy_agent
        input_data: Input data (dict with "messages" key for LangChain agents)
    
    Returns:
        Agent response
    """
    langfuse_handler = getattr(agent, '_langfuse_handler', None)
    
    if langfuse_handler:
        # Use LangChain's RunnableConfig to pass callbacks
        from langchain_core.runnables import RunnableConfig
        config = RunnableConfig(callbacks=[langfuse_handler])
        return agent.invoke(input_data, config=config)
    else:
        return agent.invoke(input_data)