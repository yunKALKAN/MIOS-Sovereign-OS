"""
Integration tests — API Contract v1.
Her endpoint icin en az bir basarili ve bir hata senaryosu.
"""

import sys
import os
import json
import importlib.util

# Load api/api.py directly to avoid conflict with root api.py
_api_path = os.path.join(os.path.dirname(__file__), "..", "api", "api.py")
_spec = importlib.util.spec_from_file_location("api_v1", os.path.abspath(_api_path))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
app = _mod.app


def client():
    app.config["TESTING"] = True
    return app.test_client()


# =========================
# HEALTH
# =========================


def test_health_success():
    c = client()
    r = c.get("/api/v1/health")
    assert r.status_code == 200
    d = r.get_json()
    assert d["engine"] == "WEB4_BLACK_MUCIZEWORK"
    assert d["status"] in ("online", "degraded")
    assert d["version"] == "1.0"
    assert "subsystems" in d
    for name in (
        "graph_engine",
        "radar_engine",
        "funding_engine",
        "signature_engine",
        "database",
    ):
        assert name in d["subsystems"], f"Missing subsystem: {name}"
    assert "timestamp" in d
    print("PASS: test_health_success")


def test_health_headers():
    c = client()
    r = c.get("/api/v1/health")
    assert "X-Request-ID" in r.headers
    assert r.headers["X-API-Version"] == "1.0"
    print("PASS: test_health_headers")


def test_health_custom_request_id():
    c = client()
    r = c.get("/api/v1/health", headers={"X-Request-ID": "custom-123"})
    assert r.headers["X-Request-ID"] == "custom-123"
    print("PASS: test_health_custom_request_id")


# =========================
# GRAPH
# =========================


def test_graph_success():
    c = client()
    r = c.get("/api/v1/graph")
    assert r.status_code == 200
    d = r.get_json()
    assert "nodes" in d
    assert "edges" in d
    assert len(d["nodes"]) == 3
    assert "AJAN" in d["nodes"]
    assert "MZC" in d["nodes"]
    assert "MYK" in d["nodes"]
    print("PASS: test_graph_success")


# =========================
# RADAR
# =========================


def test_radar_success():
    c = client()
    r = c.get("/api/v1/radar")
    assert r.status_code == 200
    d = r.get_json()
    assert d["signal"] == "ACCUMULATION"
    assert d["smart_money_inflow"] - d["outflow"] == d["net"]
    print("PASS: test_radar_success")


# =========================
# FUNDING
# =========================


def test_funding_all():
    c = client()
    r = c.get("/api/v1/funding")
    assert r.status_code == 200
    d = r.get_json()
    assert d["confidence"] == 0.87
    assert "sources" in d
    assert d["wallet"] is None
    print("PASS: test_funding_all")


def test_funding_wallet():
    c = client()
    r = c.get("/api/v1/funding/MZC")
    assert r.status_code == 200
    d = r.get_json()
    assert d["wallet"] == "MZC"
    assert len(d["flows"]) > 0
    for f in d["flows"]:
        assert f["from"] == "MZC" or f["to"] == "MZC"
    print("PASS: test_funding_wallet")


def test_funding_unknown_wallet():
    c = client()
    r = c.get("/api/v1/funding/UNKNOWN")
    assert r.status_code == 200
    d = r.get_json()
    assert d["wallet"] == "UNKNOWN"
    assert len(d["flows"]) == 0
    print("PASS: test_funding_unknown_wallet")


# =========================
# FLOW
# =========================


def test_flow_success():
    c = client()
    r = c.post(
        "/api/v1/flow",
        data=json.dumps({"from": "A", "to": "B", "amount": 100}),
        content_type="application/json",
    )
    assert r.status_code == 200
    d = r.get_json()
    assert d["status"] == "flow_added"
    assert d["data"]["amount"] == 100
    assert "request_id" in d
    print("PASS: test_flow_success")


def test_flow_missing_fields():
    c = client()
    r = c.post(
        "/api/v1/flow", data=json.dumps({"from": "A"}), content_type="application/json"
    )
    assert r.status_code == 422
    d = r.get_json()
    assert d["error"]["code"] == "VALIDATION_FAILED"
    assert "to" in d["error"]["message"]
    assert "amount" in d["error"]["message"]
    print("PASS: test_flow_missing_fields")


def test_flow_empty_body():
    c = client()
    r = c.post("/api/v1/flow", content_type="application/json")
    assert r.status_code == 400
    d = r.get_json()
    assert d["error"]["code"] == "INVALID_REQUEST"
    print("PASS: test_flow_empty_body")


# =========================
# HASH / SHA256
# =========================


def test_hash_success():
    c = client()
    r = c.post(
        "/api/v1/hash/sha256",
        data=json.dumps({"input": "hello"}),
        content_type="application/json",
    )
    assert r.status_code == 200
    d = r.get_json()
    assert d["algorithm"] == "sha256"
    assert len(d["hash"]) == 64
    assert d["input_length"] == 5
    print("PASS: test_hash_success")


def test_hash_deterministic():
    c = client()
    r1 = c.post(
        "/api/v1/hash/sha256",
        data=json.dumps({"input": "test"}),
        content_type="application/json",
    )
    r2 = c.post(
        "/api/v1/hash/sha256",
        data=json.dumps({"input": "test"}),
        content_type="application/json",
    )
    assert r1.get_json()["hash"] == r2.get_json()["hash"]
    print("PASS: test_hash_deterministic")


def test_hash_different_inputs():
    c = client()
    r1 = c.post(
        "/api/v1/hash/sha256",
        data=json.dumps({"input": "a"}),
        content_type="application/json",
    )
    r2 = c.post(
        "/api/v1/hash/sha256",
        data=json.dumps({"input": "b"}),
        content_type="application/json",
    )
    assert r1.get_json()["hash"] != r2.get_json()["hash"]
    print("PASS: test_hash_different_inputs")


def test_hash_missing_input():
    c = client()
    r = c.post(
        "/api/v1/hash/sha256",
        data=json.dumps({"data": "x"}),
        content_type="application/json",
    )
    assert r.status_code == 422
    d = r.get_json()
    assert d["error"]["code"] == "VALIDATION_FAILED"
    print("PASS: test_hash_missing_input")


# =========================
# SIGN / VERIFY
# =========================


def test_sign_verify_success():
    c = client()
    r = c.post(
        "/api/v1/sign/verify",
        data=json.dumps({"wallet": "W", "message": "M", "signature": "S"}),
        content_type="application/json",
    )
    assert r.status_code == 200
    d = r.get_json()
    assert "valid" in d
    assert "hash" in d
    assert d["wallet"] == "W"
    assert isinstance(d["valid"], bool)
    assert len(d["hash"]) == 10
    print("PASS: test_sign_verify_success")


def test_sign_verify_different_hashes():
    c = client()
    r1 = c.post(
        "/api/v1/sign/verify",
        data=json.dumps({"wallet": "A", "message": "m1", "signature": "s1"}),
        content_type="application/json",
    )
    r2 = c.post(
        "/api/v1/sign/verify",
        data=json.dumps({"wallet": "B", "message": "m2", "signature": "s2"}),
        content_type="application/json",
    )
    assert r1.get_json()["hash"] != r2.get_json()["hash"]
    print("PASS: test_sign_verify_different_hashes")


def test_sign_verify_missing_fields():
    c = client()
    r = c.post(
        "/api/v1/sign/verify",
        data=json.dumps({"wallet": "W"}),
        content_type="application/json",
    )
    assert r.status_code == 422
    d = r.get_json()
    assert d["error"]["code"] == "VALIDATION_FAILED"
    print("PASS: test_sign_verify_missing_fields")


# =========================
# 404 ERROR FORMAT
# =========================


def test_404_error_format():
    c = client()
    r = c.get("/api/v1/nonexistent")
    assert r.status_code == 404
    d = r.get_json()
    assert d["error"]["code"] == "NOT_FOUND"
    assert d["error"]["status"] == 404
    assert "request_id" in d["error"]
    print("PASS: test_404_error_format")


# =========================
# RUN ALL
# =========================

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"FAIL: {t.__name__} — {e}")
            failed += 1
    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed, {passed+failed} total")
    if failed > 0:
        sys.exit(1)
