"""VLESS Gateway integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import VlessGatewayApi
from .const import CONF_BASE_URL, CONF_TOKEN, PLATFORMS
from .coordinator import VlessGatewayCoordinator


type VlessGatewayConfigEntry = ConfigEntry[VlessGatewayCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: VlessGatewayConfigEntry) -> bool:
    """Set up VLESS Gateway from a config entry."""
    api = VlessGatewayApi(
        async_get_clientsession(hass),
        entry.data[CONF_BASE_URL],
        entry.data.get(CONF_TOKEN, ""),
    )
    coordinator = VlessGatewayCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: VlessGatewayConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
