"""Factual read-only gateway sensors."""

from datetime import datetime

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import UnitOfDataRate, UnitOfInformation, UnitOfTime
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, INTEGRATION_VERSION
from .roles import SENSOR_ROLES, role_value


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        GatewaySensor(coordinator, entry, role, name)
        for role, name in SENSOR_ROLES.items()
    )


class GatewaySensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, role, name):
        super().__init__(coordinator, context=role)
        self.role = role
        self._attr_unique_id = f"{entry.entry_id}_{role}"
        self._attr_name = name
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "NanoPi R5S VLESS Gateway",
            "manufacturer": "NikaS",
            "model": "NanoPi R5S LTS",
            "sw_version": INTEGRATION_VERSION,
        }
        if role in ("download_rate", "upload_rate"):
            self._attr_device_class = SensorDeviceClass.DATA_RATE
            self._attr_native_unit_of_measurement = UnitOfDataRate.BYTES_PER_SECOND
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif role in ("routed_traffic", "traffic_today", "traffic_month"):
            self._attr_device_class = SensorDeviceClass.DATA_SIZE
            self._attr_native_unit_of_measurement = UnitOfInformation.BYTES
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        elif role == "uptime":
            self._attr_device_class = SensorDeviceClass.DURATION
            self._attr_native_unit_of_measurement = UnitOfTime.SECONDS
        elif role == "latency":
            self._attr_native_unit_of_measurement = UnitOfTime.MILLISECONDS
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif role == "last_route_change":
            self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def available(self):
        return super().available and self.native_value is not None

    @property
    def native_value(self):
        value = role_value(self.coordinator.data or {}, self.role)
        if self.role == "last_route_change" and value is not None:
            try:
                result = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return result if result.tzinfo else None
            except (ValueError, AttributeError):
                return None
        return value

    @property
    def extra_state_attributes(self):
        return {"role": self.role, "api_schema_version": "1"}
