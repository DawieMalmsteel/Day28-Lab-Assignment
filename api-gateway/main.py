# api-gateway/main.py
from __future__ import annotations

import os
import time

import httpx
from fastapi import FastAPI
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="AI Platform API Gateway")
Instrumentator().instrument(app).expose(app)

VLLM_URL = os.environ.get("VLLM_URL", "").rstrip("/")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333").rstrip("/")
MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    embedding: list[float] = Field(default_factory=lambda: [0.0] * 384)


async def _search_context(embedding: list[float]) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.post(
                f"{QDRANT_URL}/collections/documents/points/search",
                json={"vector": embedding, "limit": 3},
            )
            resp.raise_for_status()
            return resp.json().get("result", [])
    except Exception:
        return []


async def _call_llm(prompt: str) -> tuple[str, str]:
    if not VLLM_URL:
        return (
            "[fallback] VLLM_URL chưa được cấu hình. Đây là phản hồi mặc định để kiểm tra pipeline.",
            "fallback/mock",
        )

    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            resp = await client.post(
                f"{VLLM_URL}/v1/chat/completions",
                json={
                    "model": MODEL_NAME,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            resp.raise_for_status()
            result = resp.json()
            return (
                result.get("choices", [{}])[0].get("message", {}).get("content", "No answer"),
                result.get("model", MODEL_NAME),
            )
    except Exception:
        return (
            "[fallback] Không gọi được vLLM (timeout/network). Hệ thống vẫn hoạt động ở chế độ degraded.",
            "fallback/degraded",
        )


@app.post("/api/v1/chat")
async def chat(body: ChatRequest):
    start = time.time()
    context = await _search_context(body.embedding)
    prompt = f"Context: {context}\n\nQuery: {body.query}"
    answer, model = await _call_llm(prompt)

    return {
        "answer": answer,
        "latency_ms": round((time.time() - start) * 1000, 2),
        "model": model,
    }


@app.get("/health")
def health():
    return {"status": "ok"}
