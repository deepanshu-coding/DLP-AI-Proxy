from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.metrics import router as metrics_router
from app.api.scan import router as scan_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(
    title="Confidential Data Protection Proxy",
    description=(
        "A production-quality proxy service that inspects all incoming content "
        "before forwarding it to a downstream LLM, preventing confidential "
        "information leakage via Regex, Keyword, and (future) SLM detection."
    ),
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

app.include_router(scan_router, tags=["Scanning"])
app.include_router(metrics_router, tags=["Observability"])


@app.get("/health", tags=["Health"])
async def health() -> dict:
    return {"status": "ok"}
