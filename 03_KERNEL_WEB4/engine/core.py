"""
MUCIZEWORK Engine Core — Graph state, event logging, DB yönetimi.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

STORAGE_DIR = Path(__file__).resolve().parent.parent / "storage"


class MucizeEngine:
    """Merkezi motor: graph state, events ve db yönetimi."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or (
            Path(__file__).resolve().parent.parent / "core" / "config.json"
        )
        self.config = self._load_json(self.config_path)
        self.graph_path = STORAGE_DIR / "graph" / "graph_state.json"
        self.events_path = STORAGE_DIR / "logs" / "events.json"
        self.db_path = STORAGE_DIR / "db" / "db.json"
        self.state_path = STORAGE_DIR / "state"

        self.graph = self._load_json(self.graph_path)
        self.events: list[dict[str, Any]] = self._load_json(self.events_path)
        self.db = self._load_json(self.db_path)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_json(path: Path) -> Any:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    @staticmethod
    def _save_json(path: Path, data: Any) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False, default=str)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        return {
            "engine": self.config.get("engine"),
            "version": self.config.get("version"),
            "mode": self.config.get("mode"),
            "status": self.config.get("status"),
            "graph_nodes": len(self.graph.get("nodes", {})),
            "graph_edges": len(self.graph.get("edges", [])),
            "event_count": len(self.events),
            "timestamp": self._now(),
        }

    # ------------------------------------------------------------------
    # Graph operations
    # ------------------------------------------------------------------

    def get_graph(self) -> dict[str, Any]:
        return self.graph

    def add_node(self, node_id: str, data: dict[str, Any]) -> dict[str, Any]:
        self.graph["nodes"][node_id] = {
            "data": data,
            "created": self._now(),
        }
        self.graph["updated"] = self._now()
        self._save_json(self.graph_path, self.graph)
        self._log_event("NODE_ADDED", {"node_id": node_id})
        return self.graph["nodes"][node_id]

    def remove_node(self, node_id: str) -> bool:
        if node_id not in self.graph["nodes"]:
            return False
        del self.graph["nodes"][node_id]
        self.graph["edges"] = [
            e
            for e in self.graph["edges"]
            if e.get("source") != node_id and e.get("target") != node_id
        ]
        self.graph["updated"] = self._now()
        self._save_json(self.graph_path, self.graph)
        self._log_event("NODE_REMOVED", {"node_id": node_id})
        return True

    def add_edge(self, source: str, target: str, weight: float = 1.0) -> dict[str, Any]:
        edge = {
            "source": source,
            "target": target,
            "weight": weight,
            "created": self._now(),
        }
        self.graph["edges"].append(edge)
        self.graph["updated"] = self._now()
        self._save_json(self.graph_path, self.graph)
        self._log_event("EDGE_ADDED", {"source": source, "target": target})
        return edge

    # ------------------------------------------------------------------
    # Event log
    # ------------------------------------------------------------------

    def _log_event(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        event = {
            "type": event_type,
            "payload": payload,
            "timestamp": self._now(),
        }
        self.events.append(event)
        self._save_json(self.events_path, self.events)
        return event

    def get_events(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.events[-limit:]

    def log_custom_event(
        self, event_type: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        return self._log_event(event_type, payload)

    # ------------------------------------------------------------------
    # DB operations (wallets, flows, positions)
    # ------------------------------------------------------------------

    def get_db(self) -> dict[str, Any]:
        return self.db

    def add_wallet(self, wallet_id: str, data: dict[str, Any]) -> dict[str, Any]:
        self.db["wallets"][wallet_id] = {
            "data": data,
            "added": self._now(),
        }
        self._save_json(self.db_path, self.db)
        self._log_event("WALLET_ADDED", {"wallet_id": wallet_id})
        return self.db["wallets"][wallet_id]

    def add_flow(self, flow: dict[str, Any]) -> dict[str, Any]:
        record = {**flow, "recorded": self._now()}
        self.db["flows"].append(record)
        self._save_json(self.db_path, self.db)
        self._log_event("FLOW_RECORDED", {"flow": flow})
        return record

    def add_position(self, position: dict[str, Any]) -> dict[str, Any]:
        record = {**position, "recorded": self._now()}
        self.db["positions"].append(record)
        self._save_json(self.db_path, self.db)
        self._log_event("POSITION_ADDED", {"position": position})
        return record
