from unittest.mock import AsyncMock, patch
import pytest
from homeassistant.components import frontend
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry
from custom_components.vless_gateway.api import GatewayClient


@pytest.mark.asyncio
async def test_real_platforms_register_roles_without_guessing_entity_ids(hass):
    entry = MockConfigEntry(
        domain="vless_gateway",
        unique_id="vless_gateway",
        version=2,
        data={
            "base_url": "https://gateway.example",
            "api_token": "test-only-token",
            "allow_http": False,
        },
    )
    entry.add_to_hass(hass)
    payload = {
        "status": {
            "schema_version": "1",
            "state": "healthy",
            "freshness": {"available": True, "age_seconds": 1, "stale": False},
            "data": {
                "state": "healthy",
                "mode": "auto",
                "active_route": {"available": True, "value": "de"},
            },
        }
    }
    with patch.object(
        GatewayClient, "async_refresh", new_callable=AsyncMock, return_value=payload
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        registry = er.async_get(hass)
        entities = [
            e for e in registry.entities.values() if e.config_entry_id == entry.entry_id
        ]
        assert len(entities) == 19
        assert any(e.unique_id.endswith("_active_route") for e in entities)
        panel = hass.data[frontend.DATA_PANELS]["dashboard-vless-gateway"]
        assert set(panel.config["entity_roles"].values()) == {
            e.entity_id for e in entities
        }
        assert all(
            "test-only-token" not in str(hass.states.get(e.entity_id).attributes)
            for e in entities
        )
        assert await hass.config_entries.async_unload(entry.entry_id)
