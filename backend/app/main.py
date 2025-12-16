from legacy_agent import create_legacy_agent, invoke_with_langfuse
from langchain.messages import HumanMessage

agent = create_legacy_agent()

response = invoke_with_langfuse(
    agent, 
    {"messages": [HumanMessage(content="Quiero viajar a Madrid por 3 días. Busca vuelos disponibles, actividades culturales en la ciudad y el pronóstico del clima para planificar qué hacer cada día.")]}
)

print(response)