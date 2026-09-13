"""
Clustering Engine — Wallet sınıflandırma (AJAN / MZC / MYK).
"""

CLUSTERS = {
    "AJAN": {"type": "execution"},
    "MZC": {"type": "asset"},
    "MYK": {"type": "treasury"},
}


def classify(wallet):
    return CLUSTERS.get(wallet, {"type": "unknown"})


if __name__ == "__main__":
    print("CLUSTER ENGINE ACTIVE")
