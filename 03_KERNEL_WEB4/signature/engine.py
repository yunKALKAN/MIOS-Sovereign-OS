"""
Signature Engine — SHA256 hash + imza dogrulama.
"""

import hashlib


class SignatureEngine:
    def sha256(self, data):
        """Veri ozeti uretir."""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def verify(self, wallet, message, signature):
        """Imza dogrular ve hash doner."""
        raw = f"{wallet}:{message}:{signature}".encode()
        digest = hashlib.sha256(raw).hexdigest()
        expected = digest[:10]
        return {
            "valid": signature == expected,
            "hash": expected,
        }
