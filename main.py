"""AI Observability & Cost Intelligence Platform – FastAPI Application Entry Point."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.observability import router as obs_router
from app.core.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s – %(message)s")

app = FastAPI(
    title="AI Observability & Cost Intelligence Platform",
    description="Real-time LLM monitoring platform with token cost tracking, latency analytics, hallucination detection, response drift alerting, and multi-model performance comparison.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(obs_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "service": "AI Observability & Cost Intelligence Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "capabilities": [
            "Real-time token cost tracking (GPT-4, Claude, Mistral)",
            "Latency monitoring with P95 percentile analytics",
            "Hallucination detection via judge-LLM",
            "Response drift detection for production models",
            "Configurable cost & latency alerting",
            "Multi-model performance comparison dashboard",
        ],
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
