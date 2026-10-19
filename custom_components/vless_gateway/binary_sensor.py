"""Connectivity observations; absent data is never represented as false."""

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .roles import BINARY_ROLES, role_value


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        GatewayBinarySensor(coordinator, entry, role, name)
        for role, name in BINARY_ROLES.items()
    )


class GatewayBinarySensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator, entry, role, name):
        super().__init__(coordinator, context=role)
        self.role = role
        self._attr_unique_id = f"{entry.entry_id}_{role}"
        self._attr_name = name
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.entry_id)}}

    @property
    def available(self):
        return super().available and type(self.is_on) is bool

    @property
    def is_on(self):
        value = role_value(self.coordinator.data or {}, self.role)
        return value if type(value) is bool else None

    @property
    def extra_state_attributes(self):
        return {"role": self.role, "api_schema_version": "1"}
