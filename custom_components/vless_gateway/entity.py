"""Base entity for VLESS Gateway."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import VlessGatewayCoordinator


class VlessGatewayEntity(CoordinatorEntity[VlessGatewayCoordinator]):
    """Base coordinator entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: VlessGatewayCoordinator, gateway_id: str, gateway_name: str) -> None:
        super().__init__(coordinator)
        self._gateway_id = gateway_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, gateway_id)},
            name=gateway_name,
            manufacturer="NikaSir",
            model="VLESS Gateway",
        )
