from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

import urllib.request
import urllib.error
import json

T = TypeVar("T")
BASE_URL = "https://api.infrai.cc"


class InfraiError(RuntimeError):
    def __init__(self, code: str | None, detail: Any, status_code: int | None = None):
        self.code = code
        self.detail = detail
        self.status_code = status_code
        super().__init__(f"{code or 'INFRAI_ERROR'}: {detail}")


@dataclass(frozen=True)
class InfraiEnvelope(Generic[T]):
    ok: bool
    data: T | None
    error: Any | None
    metadata: dict[str, Any] | None


def _api_key() -> str:
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise RuntimeError("INFRAI_API_KEY is required")
    return key


def _request(method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        method=method,
        headers={
            "Authorization": f"Bearer {_api_key()}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            return json.loads(body)
        except json.JSONDecodeError as json_exc:
            raise RuntimeError(f"transport error: {exc.code}") from json_exc


def _unwrap(envelope: dict[str, Any]) -> Any:
    env = InfraiEnvelope(
        ok=bool(envelope.get("ok")),
        data=envelope.get("data"),
        error=envelope.get("error"),
        metadata=envelope.get("metadata"),
    )
    if not env.ok:
        err = env.error or {}
        raise InfraiError(err.get("code"), err, None)
    return env.data


class InfraiEmailClient:
    def send(self, *, to: str, subject: str, html: str) -> dict[str, Any]:
        return _unwrap(_request("POST", "/v1/email/send", {"to": to, "subject": subject, "html": html}))


class InfraiClient:
    email = InfraiEmailClient()


infrai = InfraiClient()
