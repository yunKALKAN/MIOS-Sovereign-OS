"""Funding Service — Fund source analysis."""

import time
from typing import Optional


class FundingService:
    def __init__(self):
        self._flows = [
            {"from": "external", "to": "MZC", "amount": 162.99},
            {"from": "MZC", "to": "MYK", "amount": 162.99},
        ]

    def trace(self, wallet: Optional[str] = None) -> dict:
        flows = self._flows
        if wallet:
            flows = [f for f in self._flows if f["to"] == wallet or f["from"] == wallet]
        return {
            "wallet": wallet,
            "sources": ["external", "CEX", "bridge"],
            "flows": flows,
            "confidence": 0.87,
            "timestamp": time.time(),
        }

    def is_healthy(self) -> bool:
        return True
