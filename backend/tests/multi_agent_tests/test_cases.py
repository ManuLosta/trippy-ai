"""Test cases for the multi-agent system.

Includes original test cases for comparison and new test cases
that require advanced multi-agent functionality.
"""

from typing import List
from dataclasses import dataclass


@dataclass
class TestCase:
    id: str
    description: str
    user_query: str
    expected_tools: List[str]
    expected_content: List[str]
    requires_multi_agent: bool = False  # True if this test requires multi-agent coordination


# Original test cases (for comparison)
ORIGINAL_TEST_CASES = [
    TestCase(
        id="TC-001",
        description="Guía completa de viaje con vuelos, actividades y clima",
        user_query="Quiero viajar a Madrid por 3 días. Busca vuelos disponibles, actividades culturales en la ciudad y el pronóstico del clima para planificar qué hacer cada día.",
        expected_tools=["search_flights", "search_activities", "get_weather"],
        expected_content=["Madrid", "vuelo", "actividad", "clima", "pronóstico", "cultural"],
        requires_multi_agent=False,
    ),
    
    TestCase(
        id="TC-002",
        description="Planificación de viaje con presupuesto y conversión de moneda",
        user_query="Necesito planificar un viaje a Barcelona. Busca vuelos, actividades gastronómicas y convierte los precios totales a pesos argentinos para saber cuánto me costará el viaje.",
        expected_tools=["search_flights", "search_activities", "convert_usd_to_ars"],
        expected_content=["Barcelona", "vuelo", "actividad", "gastronomía", "pesos", "ARS"],
        requires_multi_agent=False,
    ),
    
    TestCase(
        id="TC-003",
        description="Guía completa de viaje con todas las herramientas",
        user_query="Ayúdame a planificar un viaje a París. Necesito: vuelos disponibles desde Buenos Aires, actividades de cultura y arte, el pronóstico del tiempo para los próximos 5 días, y todos los costos convertidos a pesos argentinos para armar mi presupuesto.",
        expected_tools=["search_flights", "search_activities", "get_weather", "convert_usd_to_ars"],
        expected_content=["París", "vuelo", "actividad", "cultura", "clima", "pronóstico", "pesos", "ARS"],
        requires_multi_agent=False,
    ),
]


# New test cases requiring multi-agent coordination
MULTI_AGENT_TEST_CASES = [
    TestCase(
        id="TC-MA-001",
        description="Planificación completa con itinerario optimizado",
        user_query="Quiero viajar a Madrid por 4 días. Necesito: vuelos disponibles, actividades culturales y gastronómicas, el pronóstico del clima, y un itinerario diario optimizado que considere el clima y la ubicación de las actividades.",
        expected_tools=["flight_agent", "activity_agent", "weather_agent"],
        expected_content=["Madrid", "itinerario", "día", "optimizado", "clima"],
        requires_multi_agent=True,
    ),
    
    TestCase(
        id="TC-MA-002",
        description="Recomendaciones personalizadas con optimización de presupuesto",
        user_query="Tengo un presupuesto de $2000 USD para un viaje a Barcelona de 5 días. Necesito recomendaciones personalizadas de actividades que se ajusten a mi presupuesto, y que optimices cómo distribuir el dinero entre vuelos, actividades, comida y otros gastos.",
        expected_tools=["flight_agent", "activity_agent", "budget_agent"],
        expected_content=["Barcelona", "presupuesto", "recomendaciones", "optimizado", "distribución"],
        requires_multi_agent=True,
    ),
    
    TestCase(
        id="TC-MA-003",
        description="Planificación completa con múltiples agentes coordinados",
        user_query="Planifica un viaje completo a París por 3 días. Busca vuelos económicos (máximo $800), encuentra actividades culturales y gastronómicas, obtén el pronóstico del clima, crea un itinerario diario optimizado, y dame recomendaciones personalizadas considerando que prefiero actividades culturales y tengo un presupuesto limitado.",
        expected_tools=["flight_agent", "activity_agent", "weather_agent", "budget_agent"],
        expected_content=["París", "vuelo", "actividad", "itinerario", "recomendaciones", "presupuesto"],
        requires_multi_agent=True,
    ),
    
    TestCase(
        id="TC-MA-004",
        description="Itinerario con consideración de clima y preferencias",
        user_query="Voy a viajar a New York por 5 días. Quiero un itinerario diario que considere: actividades de cultura y aventura, el pronóstico del clima para cada día (para planificar actividades al aire libre en días soleados), y que optimice la ruta para minimizar desplazamientos.",
        expected_tools=["activity_agent", "weather_agent"],
        expected_content=["New York", "itinerario", "día", "clima", "optimizado", "ruta"],
        requires_multi_agent=True,
    ),
    
    TestCase(
        id="TC-MA-005",
        description="Recomendaciones con ranking y análisis de valor",
        user_query="Estoy planeando un viaje a Roma. Dame las mejores recomendaciones de actividades considerando: prefiero cultura y gastronomía, tengo un presupuesto de $500 para actividades, y quiero saber cuáles ofrecen mejor relación calidad-precio. También convierte todo a pesos argentinos.",
        expected_tools=["activity_agent", "budget_agent"],
        expected_content=["Roma", "recomendaciones", "ranking", "presupuesto", "valor", "pesos"],
        requires_multi_agent=True,
    ),
    
    TestCase(
        id="TC-MA-006",
        description="Planificación multi-criterio compleja",
        user_query="Necesito planificar un viaje a Londres de 6 días con estas restricciones: presupuesto total de $3000 USD, prefiero actividades culturales y gastronómicas, quiero un itinerario que considere el clima, y necesito que optimices el presupuesto entre vuelos, actividades, comida y otros gastos. Convierte todos los costos a pesos argentinos.",
        expected_tools=["flight_agent", "activity_agent", "weather_agent", "budget_agent"],
        expected_content=["Londres", "presupuesto", "itinerario", "optimizado", "clima", "pesos"],
        requires_multi_agent=True,
    ),
    
    TestCase(
        id="TC-MA-007",
        description="Comparación y selección de opciones",
        user_query="Compara opciones de vuelos a Miami, encuentra actividades de aventura y playa, y dame recomendaciones personalizadas considerando que tengo 4 días y quiero maximizar actividades al aire libre según el clima.",
        expected_tools=["flight_agent", "activity_agent", "weather_agent"],
        expected_content=["Miami", "vuelo", "actividad", "recomendaciones", "clima"],
        requires_multi_agent=True,
    ),
]


# All test cases combined
ALL_TEST_CASES = ORIGINAL_TEST_CASES + MULTI_AGENT_TEST_CASES

# Dictionary for quick lookup by ID
TEST_CASES_BY_ID = {tc.id: tc for tc in ALL_TEST_CASES}
