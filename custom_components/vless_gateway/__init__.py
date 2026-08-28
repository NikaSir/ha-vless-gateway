"""VLESS Gateway panel integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .panel import async_register_panel, async_unregister_panel

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Register the integration-owned VLESS Gateway panel."""
    try:
        await async_register_panel(hass)
    except (OSError, RuntimeError, ValueError) as err:
        _LOGGER.error("Cannot register VLESS Gateway panel: %s", err)
        return False
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unregister the panel when the config entry unloads."""
    async_unregister_panel(hass)
    return True
