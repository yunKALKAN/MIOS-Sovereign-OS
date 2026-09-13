"""
MIGE OS API Tests

Copyright © 2026 Mucize Platform. All Rights Reserved.
"""

import pytest
from fastapi.testclient import TestClient
from api import app


client = TestClient(app)


def test_root():
    """Root endpoint test"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "MIGE OS API"
    assert data["version"] == "1.0.0"


def test_health():
    """Health check test"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "git_commit" in data
    assert "build_time" in data
    assert "uptime" in data
    assert "schema_version" in data


def test_ready():
    """Readiness check test"""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_live():
    """Liveness check test"""
    response = client.get("/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


def test_version():
    """Version endpoint test"""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0.0"
    assert data["tag"] == "v1.0.0-foundation"
    assert "commit" in data


def test_evidence_compile():
    """Evidence compilation test"""
    request_data = {
        "raw_data": {"tx": "abc123"},
        "handler_type": "SOLANA",
        "blockchain": "SOLANA",
        "source": "rpc"
    }
    
    response = client.post("/api/v1/evidence/compile", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "evidence_id" in data
    assert "compilation_time" in data


def test_list_handlers():
    """Handlers list test"""
    response = client.get("/api/v1/registry/handlers")
    assert response.status_code == 200
    data = response.json()
    assert "handlers" in data
    assert len(data["handlers"]) > 0


def test_list_blockchains():
    """Blockchains list test"""
    response = client.get("/api/v1/registry/blockchains")
    assert response.status_code == 200
    data = response.json()
    assert "blockchains" in data
    assert len(data["blockchains"]) > 0


def test_metrics():
    """Metrics endpoint test"""
    response = client.get("/metrics")
    assert response.status_code == 200


def test_correlation_id():
    """Correlation ID middleware test"""
    response = client.get("/health")
    assert "X-Correlation-ID" in response.headers