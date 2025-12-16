# Trippy AI - Sistema Multiagente para Planificación de Viajes

Sistema de planificación de viajes basado en agentes de IA que utiliza una arquitectura multiagente para proporcionar asistencia completa en la planificación de viajes.

## Arquitectura del Sistema

### Patrón: Tool Calling (Supervisor + Agentes Especializados)

El sistema utiliza un **Supervisor Agent** que coordina múltiples agentes especializados, cada uno enfocado en un dominio específico:

```
Usuario
  ↓
Supervisor Agent (Coordina)
  ↓
├── Flight Agent (Vuelos)
├── Activity Agent (Actividades + Itinerarios + Recomendaciones)
├── Weather Agent (Clima)
└── Budget Agent (Presupuesto + Optimización)
```

### Agentes Especializados (4 Agentes)

1. **Flight Agent**: Búsqueda y comparación de vuelos, filtrado por precio, aerolínea, horarios
2. **Activity Agent**: Búsqueda de actividades, planificación de itinerarios, optimización de rutas, recomendaciones personalizadas
3. **Weather Agent**: Pronóstico detallado con recomendaciones de actividades según clima
4. **Budget Agent**: Conversión de monedas, optimización de distribución de presupuesto

### Ventajas del Sistema Simplificado

- **Eficiencia**: Menos agentes = menos llamadas al LLM = menos problemas de RPM limits
- **Especialización**: Cada agente maneja un dominio completo de funcionalidad
- **Agentes robustos**: Agentes más capaces con múltiples herramientas relacionadas
- **Mantenibilidad**: Código más organizado y más fácil de mantener
- **Performance**: Mejor uso de tokens con menos overhead de coordinación
- **Observabilidad**: Trazabilidad completa con Langfuse integrado

## Instalación

### Requisitos

- Python >= 3.13
- Cuenta en [OpenRouter](https://openrouter.ai) y API key
- Variables de entorno configuradas (ver sección de Variables de Entorno)

### Instalación de Dependencias

```bash
# Usando uv (recomendado)
uv sync

# O usando pip
pip install -r requirements.txt
```

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto backend con:

```env
# OpenRouter Configuration (Required)
OPENROUTER_API_KEY=tu_api_key_de_openrouter
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet  # Opcional, modelo por defecto

# Langfuse Configuration (Opcional - para observabilidad)
LANGFUSE_SECRET_KEY=tu_secret_key
LANGFUSE_PUBLIC_KEY=tu_public_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

#### Modelos Disponibles en OpenRouter

Puedes usar cualquier modelo disponible en [OpenRouter](https://openrouter.ai/models):

- `anthropic/claude-3.5-sonnet` (recomendado, por defecto)
- `anthropic/claude-3-opus` (más potente)
- `openai/gpt-4-turbo`
- `openai/gpt-4o`
- `google/gemini-pro-1.5`
- `meta-llama/llama-3.1-70b-instruct`
- Y muchos más...

Para obtener tu API key de OpenRouter, visita: https://openrouter.ai/keys

## Uso

### Uso Básico del Sistema Multiagente

```python
from app.multi_agent import create_supervisor_agent, invoke_with_langfuse
from langchain.messages import HumanMessage

# Crear el supervisor agent
agent = create_supervisor_agent()

# Hacer una consulta
response = invoke_with_langfuse(
    agent,
    {"messages": [HumanMessage(content="Quiero viajar a Madrid por 3 días. Necesito vuelos, actividades y un itinerario optimizado.")]}
)

print(response)
```

### Comparación con el Agente Legacy

El sistema incluye un agente legacy (monolítico) para comparación:

```python
from app.legacy_agent import create_legacy_agent, invoke_with_langfuse

# Agente legacy
legacy_agent = create_legacy_agent()
response = invoke_with_langfuse(
    legacy_agent,
    {"messages": [HumanMessage(content="...")]}
)
```

## Tests y Evaluación

### Ejecutar Tests de Comparación

El sistema incluye un test runner que compara ambos sistemas (legacy y multi-agent):

```bash
# Ejecutar todos los tests
python -m tests.multi_agent_tests.test_runner

# Ejecutar un test específico
python -m tests.multi_agent_tests.test_runner --test-id TC-MA-001

# Ejecutar solo legacy agent
python -m tests.multi_agent_tests.test_runner --legacy-only

# Ejecutar solo multi-agent
python -m tests.multi_agent_tests.test_runner --multi-only
```

### Casos de Prueba

El sistema incluye:

- **Casos originales** (TC-001 a TC-003): Para comparación con el sistema legacy
- **Casos multiagente** (TC-MA-001 a TC-MA-007): Que requieren coordinación entre múltiples agentes

### Métricas de Comparación

El test runner genera métricas comparativas:

- Tasa de éxito (tests pasados)
- Tiempo de ejecución promedio
- Herramientas/agentes utilizados
- Calidad de respuestas

## Estructura del Proyecto

```
backend/
├── app/
│   ├── legacy_agent/          # Agente original (para comparación)
│   │   ├── __init__.py
│   │   └── main.py
│   ├── multi_agent/           # Sistema multiagente
│   │   ├── __init__.py
│   │   ├── supervisor.py     # Supervisor agent
│   │   ├── agents/           # Agentes especializados
│   │   │   ├── flight_agent.py
│   │   │   ├── activity_agent.py
│   │   │   ├── weather_agent.py
│   │   │   ├── budget_agent.py
│   │   │   ├── itinerary_agent.py
│   │   │   └── recommendation_agent.py
│   │   └── tools/            # Herramientas compartidas
│   │       ├── shared_tools.py
│   │       ├── itinerary_tools.py
│   │       └── recommendation_tools.py
│   └── main.py
├── tests/
│   ├── legacy_agent_tests/    # Tests del agente legacy
│   └── multi_agent_tests/     # Tests del sistema multiagente
│       ├── test_cases.py
│       └── test_runner.py
├── data/                      # Datos (vuelos, actividades)
│   ├── flights.csv
│   └── activities.csv
└── README.md
```

## Observabilidad con Langfuse

El sistema está integrado con [Langfuse](https://cloud.langfuse.com) para observabilidad y trazabilidad:

- Trazado de todas las llamadas al supervisor
- Trazado de llamadas a cada agente especializado
- Métricas de performance por agente
- Análisis de uso de tokens y costos

Para habilitar Langfuse, configura las variables de entorno correspondientes.

## Nuevas Funcionalidades

### 1. Planificación de Itinerarios

El **Itinerary Agent** crea itinerarios diarios optimizados considerando:
- Ubicación geográfica de actividades
- Condiciones climáticas
- Preferencias del usuario
- Balance de costos

### 2. Recomendaciones Personalizadas

El **Recommendation Agent** proporciona:
- Análisis de preferencias del usuario
- Ranking de actividades y vuelos
- Sugerencias basadas en presupuesto y tiempo disponible
- Optimización de presupuesto

### 3. Optimización Multi-criterio

El sistema coordina múltiples agentes para:
- Balance entre costo y calidad
- Optimización de tiempo de viaje
- Consideración de restricciones (presupuesto, fechas, preferencias)

## Desarrollo

### Agregar una Nueva Herramienta

1. Crear la función de herramienta en el módulo apropiado:
   - `app/multi_agent/tools/shared_tools.py` - herramientas básicas
   - `app/multi_agent/tools/itinerary_tools.py` - herramientas de itinerario
   - `app/multi_agent/tools/recommendation_tools.py` - herramientas de recomendación
2. Importarla en el agente apropiado
3. Agregarla a la lista de `tools` del agente
4. Actualizar el prompt del agente para documentar la nueva capacidad

### Agregar un Nuevo Agente

1. Crear el archivo del agente en `app/multi_agent/agents/`
2. Implementar `create_<agent_name>_agent()` con:
   - LLM configurado con OpenRouter
   - Herramientas específicas del dominio
   - Prompt especializado claro
3. Agregar el agente al supervisor en `app/multi_agent/supervisor.py`:
   - Crear función `call_<agent_name>_agent()` con decorador `@tool`
   - Agregar a la lista de `tools` del supervisor
   - Actualizar el prompt del supervisor

## Resultados y Comparación

### Mejoras del Sistema Simplificado (4 Agentes)

- **Eficiencia mejorada**: Reducción de 6 a 4 agentes = menos llamadas al LLM
- **Mejor coordinación**: Agentes más capaces que manejan dominios completos
- **Nuevas capacidades**: Itinerarios optimizados, recomendaciones personalizadas, optimización de presupuesto
- **Menos problemas de RPM**: Menos agentes = menos requests = evita rate limits
- **Mejor coherencia**: Actividades, itinerarios y recomendaciones manejados por un solo agente

### Arquitectura Optimizada

- **Activity Agent expandido**: Maneja búsqueda de actividades + creación de itinerarios + recomendaciones
- **Budget Agent expandido**: Maneja conversión de moneda + optimización de presupuesto
- **Agentes simplificados**: Flight y Weather mantienen su foco específico

## Contribuciones

Este proyecto fue desarrollado como trabajo final para la materia de Agentes de IA.

## Licencia

[Especificar licencia si aplica]
