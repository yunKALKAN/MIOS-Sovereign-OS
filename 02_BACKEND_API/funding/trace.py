import time


class FundingTrace:
    def trace(self):
        return {
            "sources": ["external", "CEX", "bridge"],
            "flows": [
                {"from": "external", "to": "MZC", "amount": 162.99},
                {"from": "MZC", "to": "MYK", "amount": 162.99},
            ],
            "confidence": 0.87,
            "timestamp": time.time(),
        }
