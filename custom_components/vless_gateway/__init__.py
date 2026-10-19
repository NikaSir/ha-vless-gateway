"""VLESS Gateway panel integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import entity_registry as er

from .panel import async_register_panel, async_unregister_panel
from .api import GatewayClient
from .coordinator import GatewayCoordinator
from .const import DOMAIN
from .roles import SENSOR_ROLES, BINARY_ROLES

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]


def _entity_roles(hass, entry):
    roles = {}
    prefix = f"{entry.entry_id}_"
    for entity in er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id):
        if entity.platform == DOMAIN and entity.unique_id.startswith(prefix):
            role = entity.unique_id[len(prefix) :]
            if role in SENSOR_ROLES or role in BINARY_ROLES:
                roles[role] = entity.entity_id
    return roles


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Register the integration-owned VLESS Gateway panel."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    # Existing scaffold entries retain their panel until explicitly reconfigured.
    if not entry.data.get("base_url") or not entry.data.get("api_token"):
        await async_register_panel(hass)
        return True
    client = GatewayClient(
        entry.data["base_url"],
        entry.data["api_token"],
        async_get_clientsession(hass),
        allow_http=entry.data.get("allow_http", False),
    )
    coordinator = GatewayCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    domain_data[entry.entry_id] = coordinator

    async def registry_changed(event):
        await async_register_panel(hass, _entity_roles(hass, entry))

    entry.async_on_unload(
        hass.bus.async_listen(er.EVENT_ENTITY_REGISTRY_UPDATED, registry_changed)
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_register_panel(hass, _entity_roles(hass, entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unregister the panel when the config entry unloads."""
    if entry.entry_id in hass.data.get(DOMAIN, {}):
        if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
            return False
        hass.data[DOMAIN].pop(entry.entry_id, None)
    async_unregister_panel(hass)
    return True


async def async_migrate_entry(hass, entry):
    if entry.version > 2:
        return False
    if entry.version < 2:
        hass.config_entries.async_update_entry(entry, version=2)
    return True
