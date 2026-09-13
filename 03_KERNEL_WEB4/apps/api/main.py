"""
MUCIZEWORK WEB4 Core Orchestrator — API Contract v1 (Frozen)
Framework: FastAPI
Port: 5002

Endpoints:
    GET  /api/v1/health
    GET  /api/v1/graph
    GET  /api/v1/radar
    GET  /api/v1/funding/{wallet}
    GET  /api/v1/funding
    POST /api/v1/flow
    POST /api/v1/hash/sha256
    POST /api/v1/sign/verify

Observability:
    GET  /health/live
    GET  /health/ready
    GET  /metrics
"""

import hashlib
import os
import sys
import time
import uuid

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

# Ensure project root is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from packages.models.envelope import Envelope
from packages.models.requests import FlowRequest, HashRequest, SignVerifyRequest
from packages.shared.config import get_settings
from packages.shared.logger import get_logger
from services.funding.engine import FundingService
from services.graph.engine import GraphService
from services.radar.engine import RadarService
from services.signature.engine import SignatureService

settings = get_settings()
logger = get_logger("web4.api")

app = FastAPI(
    title="MUCIZEWORK WEB4 API",
    version=settings.api_version,
    description="Web4 Blockchain Intelligence Engine — API Contract v1 (Frozen)",
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Service instances (Dependency Injection ready) ---

graph_service = GraphService()
radar_service = RadarService()
funding_service = FundingService()
signature_service = SignatureService()


# =========================
# MIDDLEWARE
# =========================


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex)
    trace_id = request.headers.get("X-Trace-ID", uuid.uuid4().hex[:16])
    request.state.request_id = request_id
    request.state.trace_id = trace_id

    start = time.time()
    response: Response = await call_next(request)
    latency_ms = round((time.time() - start) * 1000, 2)

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Trace-ID"] = trace_id
    response.headers["X-API-Version"] = settings.api_version

    logger.info(
        "%s %s %s %.1fms",
        request.method,
        request.url.path,
        response.status_code,
        latency_ms,
        extra={
            "request_id": request_id,
            "trace_id": trace_id,
            "latency_ms": latency_ms,
            "status": response.status_code,
        },
    )
    return response


# =========================
# ERROR HANDLERS
# =========================


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    rid = getattr(request.state, "request_id", None)
    tid = getattr(request.state, "trace_id", None)
    envelope = Envelope.fail("NOT_FOUND", 404, "Kaynak bulunamadi", rid, tid)
    return JSONResponse(status_code=404, content=envelope.model_dump())


@app.exception_handler(422)
async def validation_handler(request: Request, exc):
    rid = getattr(request.state, "request_id", None)
    tid = getattr(request.state, "trace_id", None)
    envelope = Envelope.fail("VALIDATION_FAILED", 422, str(exc), rid, tid)
    return JSONResponse(status_code=422, content=envelope.model_dump())


@app.exception_handler(500)
async def internal_handler(request: Request, exc):
    rid = getattr(request.state, "request_id", None)
    tid = getattr(request.state, "trace_id", None)
    envelope = Envelope.fail("INTERNAL_ERROR", 500, "Sunucu hatasi", rid, tid)
    return JSONResponse(status_code=500, content=envelope.model_dump())


# =========================
# OBSERVABILITY
# =========================


@app.get("/health/live", tags=["observability"])
async def health_live():
    return {"status": "alive"}


@app.get("/health/ready", tags=["observability"])
async def health_ready():
    checks = {
        "graph": graph_service.is_healthy(),
        "radar": radar_service.is_healthy(),
        "funding": funding_service.is_healthy(),
        "signature": signature_service.is_healthy(),
    }
    ready = all(checks.values())
    return {"status": "ready" if ready else "not_ready", "checks": checks}


@app.get("/metrics", tags=["observability"])
async def metrics():
    return {
        "uptime": time.time(),
        "engine": settings.engine_name,
        "mode": settings.engine_mode,
        "api_version": settings.api_version,
    }


# =========================
# API v1 — CONTRACT (FROZEN)
# =========================

# --- HEALTH ---


@app.get("/api/v1/health", tags=["health"])
async def health(request: Request):
    subsystems = {
        "graph_engine": _check_service(graph_service, "graph"),
        "radar_engine": _check_service(radar_service, "radar"),
        "funding_engine": _check_service(funding_service, "funding"),
        "signature_engine": _check_service(signature_service, "signature"),
        "database": _check_db(),
        "rpc_connection": _check_rpc(),
        "queue_system": {"status": "ok", "detail": "not_configured"},
    }
    all_ok = all(s["status"] == "ok" for s in subsystems.values())
    data = {
        "status": "online" if all_ok else "degraded",
        "engine": settings.engine_name,
        "version": settings.api_version,
        "mode": settings.engine_mode,
        "subsystems": subsystems,
        "timestamp": time.time(),
    }
    envelope = Envelope.ok(data, request.state.request_id, request.state.trace_id)
    return envelope.model_dump()


def _check_service(service, name: str) -> dict:
    try:
        return {"status": "ok" if service.is_healthy() else "error"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _check_db() -> dict:
    db_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "storage", "db", "db.json"
    )
    if os.path.exists(db_path):
        return {"status": "ok"}
    return {"status": "error", "detail": "db.json not found"}


def _check_rpc() -> dict:
    if settings.rpc_url:
        return {"status": "ok", "url": settings.rpc_url[:30] + "..."}
    return {"status": "error", "detail": "RPC URL not configured"}


# --- GRAPH ---


@app.get("/api/v1/graph", tags=["graph"])
async def graph(request: Request):
    data = graph_service.get_graph()
    envelope = Envelope.ok(data, request.state.request_id, request.state.trace_id)
    return envelope.model_dump()


# --- RADAR ---


@app.get("/api/v1/radar", tags=["radar"])
async def radar(request: Request):
    data = radar_service.scan()
    envelope = Envelope.ok(data, request.state.request_id, request.state.trace_id)
    return envelope.model_dump()


# --- FUNDING ---


@app.get("/api/v1/funding/{wallet}", tags=["funding"])
async def funding_wallet(request: Request, wallet: str):
    data = funding_service.trace(wallet=wallet)
    envelope = Envelope.ok(data, request.state.request_id, request.state.trace_id)
    return envelope.model_dump()


@app.get("/api/v1/funding", tags=["funding"])
async def funding_all(request: Request):
    data = funding_service.trace()
    envelope = Envelope.ok(data, request.state.request_id, request.state.trace_id)
    return envelope.model_dump()


# --- FLOW ---


@app.post("/api/v1/flow", tags=["flow"])
async def flow(request: Request, body: FlowRequest):
    data = {
        "status": "flow_added",
        "data": {"from": body.from_wallet, "to": body.to, "amount": body.amount},
        "request_id": request.state.request_id,
    }
    envelope = Envelope.ok(data, request.state.request_id, request.state.trace_id)
    return envelope.model_dump()


# --- HASH / SHA256 ---


@app.post("/api/v1/hash/sha256", tags=["signature"])
async def hash_sha256(request: Request, body: HashRequest):
    digest = hashlib.sha256(body.input.encode("utf-8")).hexdigest()
    data = {"hash": digest, "algorithm": "sha256", "input_length": len(body.input)}
    envelope = Envelope.ok(data, request.state.request_id, request.state.trace_id)
    return envelope.model_dump()


# --- SIGN / VERIFY ---


@app.post("/api/v1/sign/verify", tags=["signature"])
async def sign_verify(request: Request, body: SignVerifyRequest):
    result = signature_service.verify(body.wallet, body.message, body.signature)
    data = {"valid": result["valid"], "hash": result["hash"], "wallet": body.wallet}
    envelope = Envelope.ok(data, request.state.request_id, request.state.trace_id)
    return envelope.model_dump()


# =========================
# ENTRYPOINT
# =========================

if __name__ == "__main__":
    import uvicorn

    print("WEB4 MUCIZEWORK ENGINE STARTED — API Contract v1")
    print(f"PORT: {settings.port}")
    print(f"DOCS: http://127.0.0.1:{settings.port}/docs")
    host = os.environ.get("MZC_HOST", "0.0.0.0")  # nosec B104
    uvicorn.run(app, host=host, port=settings.port)
