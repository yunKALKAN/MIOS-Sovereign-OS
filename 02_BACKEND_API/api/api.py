"""
MUCIZEWORK WEB4 Core Orchestrator — Final One-Block System
Port: 5002
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, jsonify, request
from wallet_cluster.cluster import WalletCluster
from radar.radar import Radar
from funding.trace import FundingTrace
from signature.engine import SignatureEngine

app = Flask(__name__)

cluster = WalletCluster()
radar = Radar()
funding = FundingTrace()
sig = SignatureEngine()


@app.route("/health")
def health():
    return jsonify({"status": "online", "engine": "WEB4_BLACK_MUCIZEWORK"})


@app.route("/graph")
def graph():
    return jsonify(cluster.graph())


@app.route("/radar")
def get_radar():
    return jsonify(radar.scan())


@app.route("/funding")
def get_funding():
    return jsonify(funding.trace())


@app.route("/flow", methods=["POST"])
def flow():
    data = request.json
    return jsonify({"status": "flow_added", "data": data})


@app.route("/sign", methods=["POST"])
def sign():
    d = request.json
    h = sig.verify(d.get("wallet"), d.get("message"), d.get("signature"))
    return jsonify({"verify_hash": h})


if __name__ == "__main__":
    print("WEB4 MUCIZEWORK ENGINE STARTED")
    print("PORT: 5002")
    app.run(port=5002, debug=False)
