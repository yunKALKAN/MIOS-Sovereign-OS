"""
MUCIZEWORK MASTER API — v4.0 BLACK
Port: 5002  |  Endpoints: /status, /graph, /events, /db
"""

import os
from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from engine import MucizeEngine

load_dotenv()

MZC_MODE = os.getenv("MZC_MODE", "BLACK")
MZC_PORT = int(os.getenv("MZC_PORT", "5002"))

app = FastAPI(
    title="MUCIZEWORK MASTER ENGINE",
    version="4.0",
    description="Merkezi motor API — graph, event ve veri yönetimi",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = MucizeEngine()


# =========================
# Pydantic request models
# =========================

class NodeInput(BaseModel):
    node_id: str
    data: dict[str, Any]


class EdgeInput(BaseModel):
    source: str
    target: str
    weight: float = 1.0


class EventInput(BaseModel):
    event_type: str
    payload: dict[str, Any]


class WalletInput(BaseModel):
    wallet_id: str
    data: dict[str, Any]


class FlowInput(BaseModel):
    source: str
    target: str
    amount: float
    token: str = "MZC"


class PositionInput(BaseModel):
    protocol: str
    asset: str
    amount: float
    chain: str = "ethereum"


# =========================
# Status
# =========================

@app.get("/status")
async def get_status():
    return engine.status()


# =========================
# Graph endpoints
# =========================

@app.get("/graph")
async def get_graph():
    return engine.get_graph()


@app.post("/graph/node")
async def add_node(body: NodeInput):
    node = engine.add_node(body.node_id, body.data)
    return {"ok": True, "node": node}


@app.delete("/graph/node/{node_id}")
async def remove_node(node_id: str):
    removed = engine.remove_node(node_id)
    if not removed:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' bulunamadi")
    return {"ok": True, "removed": node_id}


@app.post("/graph/edge")
async def add_edge(body: EdgeInput):
    edge = engine.add_edge(body.source, body.target, body.weight)
    return {"ok": True, "edge": edge}


# =========================
# Events
# =========================

@app.get("/events")
async def get_events(limit: int = Query(default=50, ge=1, le=500)):
    return engine.get_events(limit=limit)


@app.post("/events")
async def post_event(body: EventInput):
    event = engine.log_custom_event(body.event_type, body.payload)
    return {"ok": True, "event": event}


# =========================
# DB endpoints
# =========================

@app.get("/db")
async def get_db():
    return engine.get_db()


@app.post("/db/wallet")
async def add_wallet(body: WalletInput):
    wallet = engine.add_wallet(body.wallet_id, body.data)
    return {"ok": True, "wallet": wallet}


@app.post("/db/flow")
async def add_flow(body: FlowInput):
    flow = engine.add_flow(body.model_dump())
    return {"ok": True, "flow": flow}


@app.post("/db/position")
async def add_position(body: PositionInput):
    position = engine.add_position(body.model_dump())
    return {"ok": True, "position": position}


# =========================
# Health
# =========================

@app.get("/health")
async def health():
    return {"status": "alive", "mode": MZC_MODE, "port": MZC_PORT}


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=MZC_PORT, reload=True)
