"""HMAC-signed opaque token used to round-trip server-only fields (such as the
reference translation `sentence_target`) through the client without exposing
them in the response payload.

The token is intentionally stateless: it carries the signed JSON payload, so no
DB or cache is required. Tokens carry an `iat` timestamp and are rejected after
`max_age_seconds`.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any


class InvalidPromptToken(Exception):
    pass


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


class PromptTokenService:
    """Sign and verify small JSON payloads with HMAC-SHA256."""

    def __init__(self, secret_key: str, max_age_seconds: int = 3600):
        self._key = secret_key.encode("utf-8")
        self._max_age = max_age_seconds

    def sign(self, payload: dict[str, Any]) -> str:
        body = dict(payload)
        body["iat"] = int(time.time())
        body_bytes = json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8")
        sig = hmac.new(self._key, body_bytes, hashlib.sha256).digest()
        return f"{_b64encode(body_bytes)}.{_b64encode(sig)}"

    def verify(self, token: str) -> dict[str, Any]:
        try:
            body_b64, sig_b64 = token.split(".", 1)
            body_bytes = _b64decode(body_b64)
            sig = _b64decode(sig_b64)
        except Exception as exc:
            raise InvalidPromptToken("Malformed token") from exc

        expected = hmac.new(self._key, body_bytes, hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected):
            raise InvalidPromptToken("Bad signature")

        try:
            payload = json.loads(body_bytes.decode("utf-8"))
        except Exception as exc:
            raise InvalidPromptToken("Bad payload") from exc

        iat = payload.get("iat")
        if not isinstance(iat, int) or (time.time() - iat) > self._max_age:
            raise InvalidPromptToken("Token expired")

        return payload
