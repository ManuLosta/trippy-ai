# Trippy AI

Planificador de viajes con IA usando una arquitectura de agentes especializados.

Este repositorio tiene dos partes:

- `backend/`: API FastAPI + sistema multiagente (LangChain/LangGraph + OpenRouter).
- `web/`: frontend React + Vite para conversar con el asistente de viajes.

## Arquitectura (simple)

```text
Usuario (web)
   -> POST /api/chat
      -> Supervisor Agent
         -> flight_agent (vuelos)
         -> activity_agent (actividades + itinerario + recomendaciones)
         -> weather_agent (clima)
         -> budget_agent (presupuesto + conversion USD/ARS)
      -> respuesta unificada
   -> UI muestra respuesta y guarda historial local
```

## Requisitos

- Python `>=3.13`
- [uv](https://docs.astral.sh/uv/) (recomendado para backend)
- Node.js `>=20`
- `pnpm` (para frontend)
- API key de [OpenRouter](https://openrouter.ai/keys)

## Inicio rapido

### 1) Configurar backend

```bash
cd backend
uv sync
```

Crear `backend/.env`:

```env
OPENROUTER_API_KEY=tu_api_key
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Opcional (modelo mas rapido para enrutamiento/supervisor)
OPENROUTER_FAST_MODEL=openai/gpt-4o-mini

# Opcional (observabilidad)
LANGFUSE_SECRET_KEY=
LANGFUSE_PUBLIC_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com

# Opcional (API)
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
HOST=0.0.0.0
PORT=8000
RELOAD=true
```

Levantar API:

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Healthcheck:

```bash
curl http://127.0.0.1:8000/api/health
```

### 2) Configurar frontend

En otra terminal:

```bash
cd web
pnpm install
pnpm dev
```

Abrir:

- `http://127.0.0.1:5173`

Notas:

- En desarrollo, Vite proxyea `/api` a `http://127.0.0.1:8000`.
- Si queres apuntar a otra API, define `VITE_API_BASE_URL` (por ejemplo `http://127.0.0.1:8000/api`).

## Como funciona

1. Escribis un mensaje en el chat web.
2. El frontend manda el historial de mensajes a `POST /api/chat`.
3. FastAPI valida el payload y ejecuta el supervisor.
4. El supervisor llama solo a los agentes necesarios.
5. Cada agente usa herramientas:
   - vuelos/actividades desde CSV locales en `backend/data/`
   - clima desde Open-Meteo
   - conversion USD/ARS desde ExchangeRate API
6. El backend devuelve un texto final con el plan de viaje.
7. El frontend muestra la respuesta y guarda conversaciones en `localStorage`.

## API

### `GET /api/health`

Respuesta:

```json
{ "status": "ok" }
```

### `POST /api/chat`

Request:

```json
{
  "messages": [
    { "role": "user", "content": "Quiero viajar a Madrid 3 dias." }
  ]
}
```

Response:

```json
{
  "message": "Plan de viaje generado..."
}
```

## Tests

Importante: ejecutar siempre desde `backend/` para que los paths de datos sean correctos.

### Legacy agent

```bash
cd backend
uv run python -m tests.legacy_agent_tests.test_runner
uv run python -m tests.legacy_agent_tests.test_runner --test-id TC-001
```

### Comparacion legacy vs multi-agent

```bash
cd backend
uv run python -m tests.multi_agent_tests.test_runner
uv run python -m tests.multi_agent_tests.test_runner --test-id TC-MA-001
```

Casos disponibles:

- Legacy/originales: `TC-001` a `TC-003`
- Multi-agent: `TC-MA-001` a `TC-MA-007`

## Benchmarking (basado en tests actuales)

El benchmark ya esta incorporado en `tests.multi_agent_tests.test_runner`:

- mide `execution_time` por caso y por sistema (legacy vs multi-agent)
- calcula porcentaje de exito por suite
- muestra diferencia de tiempo absoluta y porcentual entre ambos sistemas

Criterio de exito actual por test:

- usa las tools/agentes esperados
- incluye al menos ~60% del contenido esperado (`expected_content`)

Benchmark rapido de un caso (comparativo):

```bash
cd backend
uv run python -m tests.multi_agent_tests.test_runner --test-id TC-MA-003
```

Multiples corridas para reducir ruido:

```bash
cd backend
for i in {1..5}; do
  uv run python -m tests.multi_agent_tests.test_runner --test-id TC-MA-003
done
```

## Estructura del repo

```text
trippy-ai/
├── README.md
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── legacy_agent/
│   │   └── multi_agent/
│   ├── data/
│   └── tests/
└── web/
    └── src/
```

## Problemas comunes

- `failed to generate travel plan`: revisar `OPENROUTER_API_KEY` y modelo configurado.
- Error de CORS: ajustar `ALLOWED_ORIGINS` en `backend/.env`.
- Respuestas sin vuelos/actividades: validar que el destino exista en los CSV de `backend/data/`.
