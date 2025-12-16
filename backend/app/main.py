import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain.messages import HumanMessage
from app.multi_agent import create_supervisor_agent, invoke_with_langfuse

if __name__ == "__main__":
    agent = create_supervisor_agent()
    
    query = "Quiero viajar a Madrid por 3 días esta semana desde Buenos Aires. Necesito vuelos disponibles, actividades culturales, el pronóstico del clima, y un itinerario optimizado. Tengo un límite de 50000 dolares para el viaje."
    
    print("=" * 80)
    print("Multi-Agent Travel Planning System")
    print("=" * 80)
    print(f"\nQuery: {query}\n")
    
    response = invoke_with_langfuse(
        agent,
        {"messages": [HumanMessage(content=query)]}
    )
    
    messages = response.get("messages", [])
    if messages:
        last_message = messages[-1]
        if hasattr(last_message, 'content'):
            print("Response:")
            print("-" * 80)
            print(last_message.content)
            print("-" * 80)
    else:
        print("Response:", response)