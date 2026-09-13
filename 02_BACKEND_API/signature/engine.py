import hashlib


class SignatureEngine:
    def verify(self, wallet, message, signature):
        raw = f"{wallet}:{message}:{signature}".encode()
        return hashlib.sha256(raw).hexdigest()[:10]
