"""Binary sensors for VLESS Gateway."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import VlessGatewayConfigEntry
from .entity import VlessGatewayEntity


async def async_setup_entry(hass: HomeAssistant, entry: VlessGatewayConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    gateway = coordinator.data.get("gateway", {})
    gateway_id = str(gateway.get("id") or entry.entry_id)
    gateway_name = str(gateway.get("name") or entry.title)
    async_add_entities([VlessGatewayTunnelConnected(coordinator, gateway_id, gateway_name)])


class VlessGatewayTunnelConnected(VlessGatewayEntity, BinarySensorEntity):
    """Expose VLESS tunnel connectivity."""

    _attr_translation_key = "tunnel_connected"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator, gateway_id: str, gateway_name: str) -> None:
        super().__init__(coordinator, gateway_id, gateway_name)
        self._attr_unique_id = f"{gateway_id}_tunnel_connected"

    @property
    def is_on(self) -> bool | None:
        tunnel = self.coordinator.data.get("tunnel")
        if not isinstance(tunnel, dict) or "connected" not in tunnel:
            return None
        return bool(tunnel["connected"])
