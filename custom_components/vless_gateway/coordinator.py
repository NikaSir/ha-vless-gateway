"""Data coordinator for VLESS Gateway."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import VlessGatewayApi, VlessGatewayApiError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN


class VlessGatewayCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll the gateway management API."""

    def __init__(self, hass: HomeAssistant, api: VlessGatewayApi) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.api.async_get_status()
        except VlessGatewayApiError as err:
            raise UpdateFailed(str(err)) from err
