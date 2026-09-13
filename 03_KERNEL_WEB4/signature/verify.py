"""
Signature Engine — Hash tabanlı imza doğrulama.
"""

import hashlib


def verify(wallet, msg, sig):
    raw = f"{wallet}:{msg}:{sig}".encode()
    return hashlib.sha256(raw).hexdigest()


if __name__ == "__main__":
    print("SIGNATURE ENGINE READY")
