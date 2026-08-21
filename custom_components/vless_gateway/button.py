"""Buttons for VLESS Gateway."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import VlessGatewayConfigEntry
from .entity import VlessGatewayEntity


async def async_setup_entry(hass: HomeAssistant, entry: VlessGatewayConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    gateway = coordinator.data.get("gateway", {})
    gateway_id = str(gateway.get("id") or entry.entry_id)
    gateway_name = str(gateway.get("name") or entry.title)
    async_add_entities([VlessGatewayRefreshButton(coordinator, gateway_id, gateway_name)])


class VlessGatewayRefreshButton(VlessGatewayEntity, ButtonEntity):
    """Request an immediate coordinator refresh."""

    _attr_translation_key = "refresh"

    def __init__(self, coordinator, gateway_id: str, gateway_name: str) -> None:
        super().__init__(coordinator, gateway_id, gateway_name)
        self._attr_unique_id = f"{gateway_id}_refresh"

    async def async_press(self) -> None:
        await self.coordinator.async_request_refresh()
