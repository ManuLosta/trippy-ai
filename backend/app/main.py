import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.multi_agent import create_supervisor_agent, invoke_with_langfuse

load_dotenv()


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=10000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=100)


class ChatResponse(BaseModel):
    message: str


def _to_langchain_messages(messages: list[ChatMessage]):
    converted = []
    for message in messages:
        content = message.content.strip()
        if not content:
            continue
        if message.role == "user":
            converted.append(HumanMessage(content=content))
        else:
            converted.append(AIMessage(content=content))
    return converted


def _extract_content(content: object) -> str:
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        fragments = []
        for item in content:
            if isinstance(item, str):
                fragments.append(item.strip())
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    fragments.append(text.strip())
        return "\n".join(fragment for fragment in fragments if fragment).strip()

    return str(content).strip()


def _allowed_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or ["*"]


@lru_cache(maxsize=1)
def _get_supervisor_agent():
    return create_supervisor_agent()


app = FastAPI(title="Trippy AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def healthcheck():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    messages = _to_langchain_messages(payload.messages)
    if not messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")
    if not isinstance(messages[-1], HumanMessage):
        raise HTTPException(status_code=400, detail="last message must be from user")

    try:
        response = invoke_with_langfuse(_get_supervisor_agent(), {"messages": messages})
    except Exception:
        raise HTTPException(status_code=500, detail="failed to generate travel plan")

    result_messages = response.get("messages", [])
    if not result_messages:
        raise HTTPException(status_code=500, detail="agent returned an empty response")

    content = _extract_content(getattr(result_messages[-1], "content", ""))
    if not content:
        raise HTTPException(status_code=500, detail="agent returned invalid content")

    return ChatResponse(message=content)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
    )
