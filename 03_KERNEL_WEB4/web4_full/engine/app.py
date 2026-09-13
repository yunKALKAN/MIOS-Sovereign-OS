"""
MUCIZEWORK WEB4 FULL STACK ENGINE
Solana ED25519 wallet auth, JWT session, graph entegrasyonu.
Port: 5080
"""

from flask import Flask, request, jsonify
import json
import time
import os
import jwt
import secrets
import base58
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "db.json")
SECRET = "MUCIZEWORK_SECRET_KEY"


# =========================
# DB HELPERS
# =========================
def load_db():
    if not os.path.exists(DB_PATH):
        return {"users": {}, "sessions": {}, "graph": {"nodes": {}, "edges": []}}
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(db):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


# =========================
# REAL SIGNATURE VERIFY (SOLANA ED25519)
# =========================
def verify_signature(pubkey, message, signature):
    try:
        vk = VerifyKey(base58.b58decode(pubkey))
        vk.verify(message.encode("utf-8"), base58.b58decode(signature))
        return True
    except BadSignatureError:
        return False
    except Exception:
        return False


# =========================
# CHALLENGE (NONCE)
# =========================
@app.route("/challenge/<wallet>")
def challenge(wallet):
    nonce = secrets.token_hex(16)
    message = f"MUCIZEWORK WEB4 LOGIN {wallet} {nonce}"

    db = load_db()
    db["users"][wallet] = {
        "nonce": nonce,
        "message": message,
    }
    save_db(db)

    return jsonify(
        {
            "wallet": wallet,
            "nonce": nonce,
            "message": message,
        }
    )


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    wallet = data.get("wallet")
    message = data.get("message")
    signature = data.get("signature")

    db = load_db()

    if wallet not in db["users"]:
        return jsonify({"status": "no_challenge"}), 400

    ok = verify_signature(wallet, message, signature)

    if not ok:
        return jsonify({"status": "invalid_signature"}), 403

    token = jwt.encode(
        {
            "wallet": wallet,
            "time": time.time(),
        },
        SECRET,
        algorithm="HS256",
    )

    db["sessions"][token] = {
        "wallet": wallet,
        "time": time.time(),
    }
    save_db(db)

    return jsonify(
        {
            "status": "logged_in",
            "token": token,
        }
    )


# =========================
# SESSION VERIFY
# =========================
@app.route("/session/<token>")
def session(token):
    db = load_db()
    return jsonify(db["sessions"].get(token, {"status": "invalid"}))


# =========================
# GRAPH INTEGRATION
# =========================
@app.route("/graph")
def graph():
    db = load_db()
    return jsonify(db["graph"])


@app.route("/graph/add", methods=["POST"])
def add_graph():
    data = request.json
    db = load_db()

    db["graph"]["edges"].append(data)
    save_db(db)

    return jsonify({"status": "edge_added"})


# =========================
# STATUS
# =========================
@app.route("/status")
def status():
    return jsonify(
        {
            "status": "online",
            "engine": "MUCIZEWORK_WEB4_FULL_STACK",
        }
    )


if __name__ == "__main__":
    print("WEB4 FULL STACK ACTIVE")
    print("PORT: 5080")
    app.run(port=5080, debug=False)
