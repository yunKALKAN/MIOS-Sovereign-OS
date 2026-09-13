"""
MUCIZEWORK WEB4 Core Orchestrator — API Contract v1 (Frozen)
Port: 5002

Endpoints:
    GET  /api/v1/health
    GET  /api/v1/graph
    GET  /api/v1/radar
    GET  /api/v1/funding/{wallet}
    POST /api/v1/flow
    POST /api/v1/hash/sha256
    POST /api/v1/sign/verify
"""

import sys
import os
import uuid
import hashlib
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, Blueprint, jsonify, request, g
from wallet_cluster.cluster import WalletCluster
from radar.radar import Radar
from funding.trace import FundingTrace
from signature.engine import SignatureEngine

API_VERSION = "1.0"

app = Flask(__name__)

cluster = WalletCluster()
radar = Radar()
funding = FundingTrace()
sig = SignatureEngine()

v1 = Blueprint("v1", __name__, url_prefix="/api/v1")


# =========================
# MIDDLEWARE
# =========================


@app.before_request
def before_request_handler():
    g.request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex)


@app.after_request
def after_request_handler(response):
    response.headers["X-Request-ID"] = g.request_id
    response.headers["X-API-Version"] = API_VERSION
    return response


# =========================
# ERROR HANDLERS
# =========================

ERROR_MAP = {
    400: "INVALID_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "VALIDATION_FAILED",
    429: "RATE_LIMITED",
    500: "INTERNAL_ERROR",
}


def error_response(status_code, message=None):
    code = ERROR_MAP.get(status_code, "UNKNOWN_ERROR")
    body = {
        "error": {
            "code": code,
            "status": status_code,
            "message": message or code,
            "request_id": getattr(g, "request_id", None),
        }
    }
    return jsonify(body), status_code


@app.errorhandler(400)
def handle_400(e):
    return error_response(400, str(e))


@app.errorhandler(404)
def handle_404(e):
    return error_response(404, "Kaynak bulunamadi")


@app.errorhandler(422)
def handle_422(e):
    return error_response(422, str(e))


@app.errorhandler(500)
def handle_500(e):
    return error_response(500, "Sunucu hatasi")


# =========================
# HEALTH (enhanced)
# =========================


@v1.route("/health")
def health():
    subsystems = {
        "graph_engine": _check_graph(),
        "radar_engine": _check_radar(),
        "funding_engine": _check_funding(),
        "signature_engine": _check_signature(),
        "database": _check_db(),
    }
    all_ok = all(s["status"] == "ok" for s in subsystems.values())
    return jsonify(
        {
            "status": "online" if all_ok else "degraded",
            "engine": "WEB4_BLACK_MUCIZEWORK",
            "version": API_VERSION,
            "subsystems": subsystems,
            "timestamp": time.time(),
        }
    )


def _check_graph():
    try:
        data = cluster.graph()
        return {"status": "ok", "nodes": len(data.get("nodes", {}))}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _check_radar():
    try:
        radar.scan()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _check_funding():
    try:
        funding.trace()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _check_signature():
    try:
        sig.sha256("test")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _check_db():
    db_path = os.path.join(os.path.dirname(__file__), "..", "storage", "db", "db.json")
    if os.path.exists(db_path):
        return {"status": "ok"}
    return {"status": "error", "detail": "db.json not found"}


# =========================
# GRAPH
# =========================


@v1.route("/graph")
def graph():
    return jsonify(cluster.graph())


# =========================
# RADAR
# =========================


@v1.route("/radar")
def get_radar():
    return jsonify(radar.scan())


# =========================
# FUNDING (with wallet path param)
# =========================


@v1.route("/funding/<wallet>")
def get_funding(wallet):
    data = funding.trace(wallet=wallet)
    return jsonify(data)


@v1.route("/funding")
def get_funding_all():
    data = funding.trace()
    return jsonify(data)


# =========================
# FLOW
# =========================


@v1.route("/flow", methods=["POST"])
def flow():
    data = request.json
    if not data:
        return error_response(400, "Request body bos veya gecersiz JSON")
    required = ["from", "to", "amount"]
    missing = [f for f in required if f not in data]
    if missing:
        return error_response(422, f"Eksik alanlar: {', '.join(missing)}")
    return jsonify({"status": "flow_added", "data": data, "request_id": g.request_id})


# =========================
# HASH (SHA256)
# =========================


@v1.route("/hash/sha256", methods=["POST"])
def hash_sha256():
    data = request.json
    if not data or "input" not in data:
        return error_response(422, "Eksik alan: input")
    raw = data["input"]
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return jsonify({"hash": digest, "algorithm": "sha256", "input_length": len(raw)})


# =========================
# SIGN / VERIFY
# =========================


@v1.route("/sign/verify", methods=["POST"])
def sign_verify():
    data = request.json
    if not data:
        return error_response(400, "Request body bos veya gecersiz JSON")
    required = ["wallet", "message", "signature"]
    missing = [f for f in required if f not in data]
    if missing:
        return error_response(422, f"Eksik alanlar: {', '.join(missing)}")
    result = sig.verify(data["wallet"], data["message"], data["signature"])
    return jsonify(
        {
            "valid": result["valid"],
            "hash": result["hash"],
            "wallet": data["wallet"],
        }
    )


# =========================
# REGISTER BLUEPRINT
# =========================

app.register_blueprint(v1)


if __name__ == "__main__":
    print("WEB4 MUCIZEWORK ENGINE STARTED — API Contract v1")
    print("PORT: 5002")
    print("DOCS: http://127.0.0.1:5002/api/v1/health")
    app.run(port=5002, debug=False)
