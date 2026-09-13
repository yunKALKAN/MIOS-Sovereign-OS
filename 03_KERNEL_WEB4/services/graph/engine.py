"""Graph Service — Wallet cluster graph management."""


class GraphService:
    def __init__(self):
        self._nodes = {
            "AJAN": {"role": "execution", "balance": 0},
            "MZC": {"role": "asset", "balance": 162.99},
            "MYK": {"role": "treasury", "balance": 12025.88},
        }
        self._edges = [
            {"from": "external", "to": "MZC", "amount": 162.99},
            {"from": "MZC", "to": "MYK", "amount": 162.99},
        ]

    def get_graph(self) -> dict:
        return {"nodes": self._nodes, "edges": self._edges}

    def is_healthy(self) -> bool:
        return len(self._nodes) > 0
