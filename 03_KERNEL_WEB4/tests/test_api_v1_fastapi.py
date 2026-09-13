"""
Integration tests — API Contract v1 (FastAPI).
Her endpoint icin en az bir basarili ve bir hata senaryosu.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


# =========================
# OBSERVABILITY
# =========================


def test_health_live():
    r = client.get("/health/live")
    assert r.status_code == 200
    assert r.json()["status"] == "alive"


def test_health_ready():
    r = client.get("/health/ready")
    assert r.status_code == 200
    assert r.json()["status"] in ("ready", "not_ready")


def test_metrics():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "engine" in r.json()


# =========================
# HEALTH
# =========================


def test_health_success():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    d = r.json()
    assert d["success"] is True
    data = d["data"]
    assert data["engine"] == "WEB4_BLACK_MUCIZEWORK"
    assert data["status"] in ("online", "degraded")
    assert data["version"] == "1.0"
    assert "subsystems" in data
    for name in (
        "graph_engine",
        "radar_engine",
        "funding_engine",
        "signature_engine",
        "database",
    ):
        assert name in data["subsystems"], f"Missing subsystem: {name}"
    assert "timestamp" in data


def test_health_headers():
    r = client.get("/api/v1/health")
    assert "X-Request-ID" in r.headers
    assert "X-Trace-ID" in r.headers
    assert r.headers["X-API-Version"] == "1.0"


def test_health_custom_request_id():
    r = client.get("/api/v1/health", headers={"X-Request-ID": "custom-123"})
    assert r.headers["X-Request-ID"] == "custom-123"


def test_health_envelope():
    r = client.get("/api/v1/health")
    d = r.json()
    assert "success" in d
    assert "request_id" in d
    assert "trace_id" in d
    assert "timestamp" in d
    assert "data" in d


# =========================
# GRAPH
# =========================


def test_graph_success():
    r = client.get("/api/v1/graph")
    assert r.status_code == 200
    d = r.json()
    assert d["success"] is True
    data = d["data"]
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) == 3
    assert "AJAN" in data["nodes"]
    assert "MZC" in data["nodes"]
    assert "MYK" in data["nodes"]


# =========================
# RADAR
# =========================


def test_radar_success():
    r = client.get("/api/v1/radar")
    assert r.status_code == 200
    d = r.json()
    assert d["success"] is True
    data = d["data"]
    assert data["signal"] == "ACCUMULATION"
    assert data["smart_money_inflow"] - data["outflow"] == data["net"]


# =========================
# FUNDING
# =========================


def test_funding_all():
    r = client.get("/api/v1/funding")
    assert r.status_code == 200
    d = r.json()
    assert d["success"] is True
    data = d["data"]
    assert data["confidence"] == 0.87
    assert "sources" in data
    assert data["wallet"] is None


def test_funding_wallet():
    r = client.get("/api/v1/funding/MZC")
    assert r.status_code == 200
    d = r.json()
    assert d["success"] is True
    data = d["data"]
    assert data["wallet"] == "MZC"
    assert len(data["flows"]) > 0
    for f in data["flows"]:
        assert f["from"] == "MZC" or f["to"] == "MZC"


def test_funding_unknown_wallet():
    r = client.get("/api/v1/funding/UNKNOWN")
    assert r.status_code == 200
    d = r.json()
    assert d["success"] is True
    data = d["data"]
    assert data["wallet"] == "UNKNOWN"
    assert len(data["flows"]) == 0


# =========================
# FLOW
# =========================


def test_flow_success():
    r = client.post("/api/v1/flow", json={"from": "A", "to": "B", "amount": 100})
    assert r.status_code == 200
    d = r.json()
    assert d["success"] is True
    data = d["data"]
    assert data["status"] == "flow_added"
    assert data["data"]["amount"] == 100


def test_flow_missing_fields():
    r = client.post("/api/v1/flow", json={"from": "A"})
    assert r.status_code == 422


def test_flow_empty_body():
    r = client.post("/api/v1/flow")
    assert r.status_code == 422


# =========================
# HASH / SHA256
# =========================


def test_hash_success():
    r = client.post("/api/v1/hash/sha256", json={"input": "hello"})
    assert r.status_code == 200
    d = r.json()
    assert d["success"] is True
    data = d["data"]
    assert data["algorithm"] == "sha256"
    assert len(data["hash"]) == 64
    assert data["input_length"] == 5


def test_hash_deterministic():
    r1 = client.post("/api/v1/hash/sha256", json={"input": "test"})
    r2 = client.post("/api/v1/hash/sha256", json={"input": "test"})
    assert r1.json()["data"]["hash"] == r2.json()["data"]["hash"]


def test_hash_different_inputs():
    r1 = client.post("/api/v1/hash/sha256", json={"input": "a"})
    r2 = client.post("/api/v1/hash/sha256", json={"input": "b"})
    assert r1.json()["data"]["hash"] != r2.json()["data"]["hash"]


def test_hash_missing_input():
    r = client.post("/api/v1/hash/sha256", json={"data": "x"})
    assert r.status_code == 422


# =========================
# SIGN / VERIFY
# =========================


def test_sign_verify_success():
    r = client.post(
        "/api/v1/sign/verify", json={"wallet": "W", "message": "M", "signature": "S"}
    )
    assert r.status_code == 200
    d = r.json()
    assert d["success"] is True
    data = d["data"]
    assert "valid" in data
    assert "hash" in data
    assert data["wallet"] == "W"
    assert isinstance(data["valid"], bool)
    assert len(data["hash"]) == 10


def test_sign_verify_different_hashes():
    r1 = client.post(
        "/api/v1/sign/verify", json={"wallet": "A", "message": "m1", "signature": "s1"}
    )
    r2 = client.post(
        "/api/v1/sign/verify", json={"wallet": "B", "message": "m2", "signature": "s2"}
    )
    assert r1.json()["data"]["hash"] != r2.json()["data"]["hash"]


def test_sign_verify_missing_fields():
    r = client.post("/api/v1/sign/verify", json={"wallet": "W"})
    assert r.status_code == 422


# =========================
# 404 ERROR FORMAT
# =========================


def test_404_error_format():
    r = client.get("/api/v1/nonexistent")
    assert r.status_code == 404
    d = r.json()
    assert d["success"] is False
    assert d["error"]["code"] == "NOT_FOUND"
    assert d["error"]["status"] == 404
