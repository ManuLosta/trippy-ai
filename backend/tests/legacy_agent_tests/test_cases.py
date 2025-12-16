from typing import List
from dataclasses import dataclass


@dataclass
class TestCase:
    id: str
    description: str
    user_query: str
    expected_tools: List[str]
    expected_content: List[str]


TEST_CASES = [
    TestCase(
        id="TC-001",
        description="Guía completa de viaje con vuelos, actividades y clima",
        user_query="Quiero viajar a Madrid por 3 días. Busca vuelos disponibles, actividades culturales en la ciudad y el pronóstico del clima para planificar qué hacer cada día.",
        expected_tools=["search_flights", "search_activities", "get_weather"],
        expected_content=["Madrid", "vuelo", "actividad", "clima", "pronóstico", "cultural"]
    ),
    
    TestCase(
        id="TC-002",
        description="Planificación de viaje con presupuesto y conversión de moneda",
        user_query="Necesito planificar un viaje a Barcelona. Busca vuelos, actividades gastronómicas y convierte los precios totales a pesos argentinos para saber cuánto me costará el viaje.",
        expected_tools=["search_flights", "search_activities", "convert_usd_to_ars"],
        expected_content=["Barcelona", "vuelo", "actividad", "gastronomía", "pesos", "ARS"]
    ),
    
    TestCase(
        id="TC-003",
        description="Guía completa de viaje con todas las herramientas",
        user_query="Ayúdame a planificar un viaje a París. Necesito: vuelos disponibles desde Buenos Aires, actividades de cultura y arte, el pronóstico del tiempo para los próximos 5 días, y todos los costos convertidos a pesos argentinos para armar mi presupuesto.",
        expected_tools=["search_flights", "search_activities", "get_weather", "convert_usd_to_ars"],
        expected_content=["París", "vuelo", "actividad", "cultura", "clima", "pronóstico", "pesos", "ARS"]
    ),
]


TEST_CASES_BY_ID = {tc.id: tc for tc in TEST_CASES}
