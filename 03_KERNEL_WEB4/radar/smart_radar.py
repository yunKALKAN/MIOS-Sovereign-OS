"""
Smart Money Radar — Büyük hacimli akışları tespit eder.
"""


class Radar:
    def __init__(self):
        self.signals = []

    def feed(self, flow):
        if flow.get("amount", 0) > 100000:
            self.signals.append({"type": "smart_money", "flow": flow})

    def get(self):
        return self.signals


radar = Radar()
