"""Signature Service — SHA256 hash + signature verification."""

import hashlib


class SignatureService:
    def sha256(self, data: str) -> str:
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def verify(self, wallet: str, message: str, signature: str) -> dict:
        raw = f"{wallet}:{message}:{signature}".encode()
        digest = hashlib.sha256(raw).hexdigest()
        expected = digest[:10]
        return {"valid": signature == expected, "hash": expected}

    def is_healthy(self) -> bool:
        return True
