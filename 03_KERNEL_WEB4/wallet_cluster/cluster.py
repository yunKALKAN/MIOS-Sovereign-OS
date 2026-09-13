class WalletCluster:
    def __init__(self):
        self.nodes = {
            "AJAN": {"role": "execution", "balance": 0},
            "MZC": {"role": "asset", "balance": 162.99},
            "MYK": {"role": "treasury", "balance": 12025.88},
        }
        self.edges = [
            {"from": "external", "to": "MZC", "amount": 162.99},
            {"from": "MZC", "to": "MYK", "amount": 162.99},
        ]

    def graph(self):
        return {"nodes": self.nodes, "edges": self.edges}
