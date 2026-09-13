"""
MIGE OS API

Copyright © 2026 Mucize Platform. All Rights Reserved.
Proprietary commercial software.
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
import json
import time
import logging
import uuid
from datetime import datetime
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Metadata
API_VERSION = "1.0.0"
API_TITLE = "MIGE OS Evidence API"
SCHEMA_VERSION = "1.0.0"
BUILD_TIME = datetime.utcnow().isoformat()
GIT_COMMIT = "unknown"

# Startup time
STARTUP_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info(f"API starting up - version: {API_VERSION}, commit: {GIT_COMMIT}")
    yield
    logger.info("API shutting down")


app = FastAPI(
    title=API_TITLE,
    description="MUCIZECHAİN Evidence Compilation API - Production",
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware)


# Correlation ID Middleware
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """Correlation ID middleware for distributed tracing"""
    correlation_id = request.headers.get("X-Correlation-ID")
    
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
    
    request.state.correlation_id = correlation_id
    
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    
    return response


# Error Model
class ErrorResponse(BaseModel):
    """Standard error response model"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    correlation_id: str = Field(..., description="Correlation ID for tracing")
    details: Dict = Field(default_factory=dict, description="Additional error details")


# Request/Response Models
class EvidenceRequest(BaseModel):
    """Evidence derleme isteği modeli"""
    raw_data: Dict = Field(..., description="Raw evidence data")
    handler_type: str = Field(..., description="Handler type (e.g., SOLANA, ETHEREUM)")
    blockchain: str = Field(..., description="Blockchain name")
    source: str = Field(..., description="Data source")


class EvidenceResponse(BaseModel):
    """Evidence derleme yanıtı modeli"""
    success: bool = Field(..., description="Compilation success status")
    evidence_id: Optional[str] = Field(None, description="Generated evidence ID")
    error: Optional[str] = Field(None, description="Error message if failed")
    compilation_time: Optional[float] = Field(None, description="Compilation duration in seconds")


class HandlerInfo(BaseModel):
    """Handler information model"""
    type: str
    status: str
    supported_formats: List[str]


class HandlersResponse(BaseModel):
    """Handlers list response model"""
    handlers: List[HandlerInfo]


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    version: str
    git_commit: str
    build_time: str
    uptime: float
    schema_version: str


class VersionResponse(BaseModel):
    """Version information response model"""
    version: str
    commit: str
    tag: str


# Root endpoint
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "name": "MIGE OS API",
        "version": API_VERSION,
        "status": "running"
    }


# Health endpoint
@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint with detailed information"""
    uptime = time.time() - STARTUP_TIME
    return HealthResponse(
        status="healthy",
        version=API_VERSION,
        git_commit=GIT_COMMIT,
        build_time=BUILD_TIME,
        uptime=uptime,
        schema_version=SCHEMA_VERSION
    )


# Readiness endpoint
@app.get("/ready")
async def ready():
    """Readiness check endpoint"""
    # TODO: Check dependencies (database, external services)
    return {"status": "ready"}


# Liveness endpoint
@app.get("/live")
async def live():
    """Liveness check endpoint"""
    return {"status": "alive"}


# Version endpoint
@app.get("/version", response_model=VersionResponse)
async def version():
    """Version information endpoint"""
    return VersionResponse(
        version=API_VERSION,
        commit=GIT_COMMIT,
        tag="v1.0.0-foundation"
    )


# Evidence compilation endpoint
@app.post("/api/v1/evidence/compile", response_model=EvidenceResponse)
async def compile_evidence(request: EvidenceRequest, http_request: Request):
    """
    Evidence derleme endpoint'i
    
    Ham veriyi alır, Evidence Compiler ile derler.
    """
    correlation_id = http_request.state.correlation_id
    
    start_time = time.time()
    
    logger.info(f"Evidence compilation started - correlation_id: {correlation_id}, handler_type: {request.handler_type}, blockchain: {request.blockchain}")
    
    try:
        # TODO: Evidence Compiler entegrasyonu
        # Şimdilik mock implementation
        
        # Simüle edilmiş derleme süresi
        compilation_time = time.time() - start_time
        
        # Simüle edilmiş evidence ID
        import hashlib
        evidence_id = hashlib.sha256(
            json.dumps(request.raw_data, sort_keys=True).encode()
        ).hexdigest()[:32]
        
        logger.info(f"Evidence compilation completed - correlation_id: {correlation_id}, evidence_id: {evidence_id}, compilation_time: {compilation_time}")
        
        return EvidenceResponse(
            success=True,
            evidence_id=evidence_id,
            compilation_time=compilation_time
        )
        
    except Exception as e:
        logger.error(f"Evidence compilation failed - correlation_id: {correlation_id}, error: {str(e)}")
        
        return EvidenceResponse(
            success=False,
            error=str(e)
        )


# Handlers list endpoint
@app.get("/api/v1/registry/handlers", response_model=HandlersResponse)
async def list_handlers(http_request: Request):
    """Kayıtlı handler'leri listeler"""
    correlation_id = http_request.state.correlation_id
    
    logger.info(f"Listing handlers - correlation_id: {correlation_id}")
    
    # TODO: Handler Registry entegrasyonu
    return HandlersResponse(
        handlers=[
            HandlerInfo(
                type="SOLANA",
                status="available",
                supported_formats=["json", "base64"]
            ),
            HandlerInfo(
                type="ETHEREUM",
                status="available",
                supported_formats=["json", "hex"]
            )
        ]
    )


# Blockchains list endpoint
@app.get("/api/v1/registry/blockchains")
async def list_blockchains(http_request: Request):
    """Desteklenen blockchain'leri listeler"""
    correlation_id = http_request.state.correlation_id
    
    logger.info(f"Listing blockchains - correlation_id: {correlation_id}")
    
    return {
        "blockchains": [
            "ETHEREUM",
            "SOLANA",
            "BNB_CHAIN",
            "POLYGON",
            "ARBITRUM",
            "OPTIMISM",
            "AVALANCHE",
            "BASE"
        ]
    }


# Metrics endpoint (Prometheus format placeholder)
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # TODO: Implement actual Prometheus metrics
    return {
        "# HELP mige_os_api_requests_total Total number of API requests",
        "# TYPE mige_os_api_requests_total counter",
        "mige_os_api_requests_total 0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )