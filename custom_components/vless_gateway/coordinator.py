"""One read-only polling coordinator for every gateway entity."""

from datetime import timedelta
from copy import deepcopy
import logging

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import GatewayAuthError, GatewayError

_LOGGER = logging.getLogger(__name__)


class GatewayCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, client):
        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name="VLESS Gateway",
            update_interval=timedelta(seconds=15),
        )

    async def _async_update_data(self):
        try:
            return await self.client.async_refresh()
        except GatewayAuthError:
            self._mark_stale()
            raise ConfigEntryAuthFailed("Gateway authentication failed") from None
        except GatewayError:
            self._mark_stale()
            raise UpdateFailed("Gateway unavailable or incompatible") from None

    def _mark_stale(self):
        if self.data:
            self.data = deepcopy(self.data)
            for envelope in self.data.values():
                envelope.setdefault("freshness", {})["stale"] = True

    async def async_diagnostic_snapshot(self):
        """Fetched only by an explicit diagnostics request, never periodic polling."""
        return await self.client.async_get("diagnostics")
