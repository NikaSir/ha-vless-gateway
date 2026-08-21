"""Local API client for VLESS Gateway."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import API_STATUS_PATH


class VlessGatewayApiError(Exception):
    """Base API error."""


class VlessGatewayAuthError(VlessGatewayApiError):
    """Authentication failed."""


@dataclass(slots=True)
class VlessGatewayApi:
    """Small client for the documented gateway management API."""

    session: ClientSession
    base_url: str
    token: str

    async def async_get_status(self) -> dict[str, Any]:
        """Return normalized gateway status payload."""
        url = f"{self.base_url.rstrip('/')}{API_STATUS_PATH}"
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        try:
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status in (401, 403):
                    raise VlessGatewayAuthError("Gateway rejected credentials")
                if response.status != 200:
                    raise VlessGatewayApiError(f"Gateway returned HTTP {response.status}")
                payload = await response.json()
        except (ClientError, TimeoutError, ValueError) as err:
            raise VlessGatewayApiError(str(err)) from err

        if not isinstance(payload, dict):
            raise VlessGatewayApiError("Gateway status response is not an object")
        return payload
