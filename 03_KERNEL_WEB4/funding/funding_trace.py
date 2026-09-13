"""
Funding Trace Engine — Fon akışı kayıt ve izleme.
Port: 5003
"""

from flask import Flask, request, jsonify
import time

app = Flask(__name__)

flows = []


@app.route("/flow", methods=["POST"])
def flow():
    data = request.json
    flows.append(
        {
            "from": data["from"],
            "to": data["to"],
            "amount": data["amount"],
            "ts": time.time(),
        }
    )
    return jsonify({"status": "flow_added", "total": len(flows)})


@app.route("/trace")
def trace():
    return jsonify({"flows": flows})


@app.route("/status")
def status():
    return jsonify({"status": "online", "module": "funding_trace"})


if __name__ == "__main__":
    app.run(port=5003, debug=False)
