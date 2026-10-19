"""Bounded read-only gateway API; no Home Assistant dependency or raw error bodies."""

from __future__ import annotations

import asyncio
from datetime import datetime
import ipaddress
import json
from urllib.parse import urlsplit, urlunsplit

import aiohttp

ENDPOINTS = ("status", "routes", "traffic", "system", "health")
MAX_RESPONSE = 1 << 20


class GatewayError(Exception):
    """Safe connection or protocol error."""


class GatewayAuthError(GatewayError):
    """Gateway rejected the independent API token."""


class GatewaySchemaError(GatewayError):
    """Unsupported or malformed API schema."""


def normalize_base_url(value: str, *, allow_http: bool = False) -> str:
    try:
        u = urlsplit(value.strip())
        port = u.port
        if (
            u.scheme not in ("http", "https")
            or not u.hostname
            or u.username is not None
            or u.password is not None
            or u.query
            or u.fragment
            or u.path not in ("", "/")
        ):
            raise ValueError
        if port is not None and not 1 <= port <= 65535:
            raise ValueError
        if u.scheme == "http" and (
            not allow_http or not ipaddress.ip_address(u.hostname).is_private
        ):
            raise ValueError
        return urlunsplit((u.scheme, u.netloc.lower(), "", "", ""))
    except (ValueError, TypeError, AttributeError):
        raise GatewayError("Invalid or untrusted management URL") from None


def validate_envelope(value):
    if not isinstance(value, dict) or value.get("schema_version") != "1":
        raise GatewaySchemaError("Unsupported gateway schema")
    if value.get("state") not in (
        "healthy",
        "starting",
        "degraded_fail_open",
        "control_error",
    ) or not isinstance(value.get("data"), dict):
        raise GatewaySchemaError("Invalid gateway response")
    try:
        stamp = datetime.fromisoformat(value["generated_at"].replace("Z", "+00:00"))
        if stamp.tzinfo is None or not isinstance(value["gateway_version"], str):
            raise ValueError
        f = value["freshness"]
        if (
            not isinstance(f, dict)
            or type(f.get("stale")) is not bool
            or type(f.get("available")) is not bool
        ):
            raise ValueError
        if f["available"] and (
            type(f.get("age_seconds")) not in (int, float) or f["age_seconds"] < 0
        ):
            raise ValueError
    except (KeyError, TypeError, ValueError, AttributeError):
        raise GatewaySchemaError("Invalid gateway metadata") from None
    return value


class GatewayClient:
    def __init__(self, base_url, token, session, *, allow_http=False):
        self.base_url = normalize_base_url(base_url, allow_http=allow_http)
        if not isinstance(token, str) or not token or "\n" in token or "\r" in token:
            raise GatewayError("Invalid API token")
        self._token = token
        self._session = session

    async def async_get(self, endpoint):
        if endpoint not in (*ENDPOINTS, "diagnostics"):
            raise GatewayError("Unsupported read-only endpoint")
        try:
            async with self._session.get(
                self.base_url + "/api/v1/" + endpoint,
                headers={"Authorization": "Bearer " + self._token},
                timeout=aiohttp.ClientTimeout(total=5),
                allow_redirects=False,
            ) as response:
                if response.status == 401:
                    raise GatewayAuthError("Gateway authentication failed")
                if response.status != 200:
                    raise GatewayError("Gateway request failed")
                chunks = bytearray()
                async for chunk in response.content.iter_chunked(65536):
                    chunks.extend(chunk)
                    if len(chunks) > MAX_RESPONSE:
                        raise GatewaySchemaError("Gateway response too large")
                try:
                    return validate_envelope(json.loads(chunks))
                except (ValueError, UnicodeError):
                    raise GatewaySchemaError("Gateway response is not JSON") from None
        except GatewayError:
            raise
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
            raise GatewayError("Gateway unavailable") from None

    async def async_refresh(self):
        values = await asyncio.gather(
            *(self.async_get(endpoint) for endpoint in ENDPOINTS)
        )
        return dict(zip(ENDPOINTS, values, strict=True))
