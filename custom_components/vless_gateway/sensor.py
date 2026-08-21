"""Sensors for VLESS Gateway."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorDeviceClass
from homeassistant.const import UnitOfInformation, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import VlessGatewayConfigEntry
from .entity import VlessGatewayEntity


@dataclass(frozen=True, kw_only=True)
class VlessGatewaySensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]


def _nested(data: dict[str, Any], section: str, key: str) -> Any:
    block = data.get(section)
    return block.get(key) if isinstance(block, dict) else None


SENSORS = (
    VlessGatewaySensorDescription(key="active_route", translation_key="active_route", value_fn=lambda d: _nested(d, "routing", "active_route")),
    VlessGatewaySensorDescription(key="uptime", translation_key="uptime", device_class=SensorDeviceClass.DURATION, native_unit_of_measurement=UnitOfTime.SECONDS, value_fn=lambda d: _nested(d, "gateway", "uptime_seconds")),
    VlessGatewaySensorDescription(key="latency", translation_key="latency", native_unit_of_measurement="ms", value_fn=lambda d: _nested(d, "tunnel", "latency_ms")),
    VlessGatewaySensorDescription(key="rx_bytes", translation_key="rx_bytes", native_unit_of_measurement=UnitOfInformation.BYTES, value_fn=lambda d: _nested(d, "tunnel", "rx_bytes")),
    VlessGatewaySensorDescription(key="tx_bytes", translation_key="tx_bytes", native_unit_of_measurement=UnitOfInformation.BYTES, value_fn=lambda d: _nested(d, "tunnel", "tx_bytes")),
)


async def async_setup_entry(hass: HomeAssistant, entry: VlessGatewayConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    gateway = coordinator.data.get("gateway", {})
    gateway_id = str(gateway.get("id") or entry.entry_id)
    gateway_name = str(gateway.get("name") or entry.title)
    async_add_entities(VlessGatewaySensor(coordinator, gateway_id, gateway_name, description) for description in SENSORS)


class VlessGatewaySensor(VlessGatewayEntity, SensorEntity):
    entity_description: VlessGatewaySensorDescription

    def __init__(self, coordinator, gateway_id: str, gateway_name: str, description: VlessGatewaySensorDescription) -> None:
        super().__init__(coordinator, gateway_id, gateway_name)
        self.entity_description = description
        self._attr_unique_id = f"{gateway_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data)
