from unittest.mock import AsyncMock
import pytest
from custom_components.vless_gateway.api import GatewayError
from custom_components.vless_gateway.coordinator import GatewayCoordinator


@pytest.mark.asyncio
async def test_refresh_failure_keeps_last_good_but_marks_unavailable(hass):
    client = AsyncMock()
    first = {
        "status": {
            "state": "healthy",
            "freshness": {"available": True, "age_seconds": 1, "stale": False},
            "data": {"mode": "auto"},
        }
    }
    client.async_refresh.return_value = first
    coordinator = GatewayCoordinator(hass, None, client)
    await coordinator.async_refresh()
    assert coordinator.last_update_success
    assert coordinator.data == first
    client.async_refresh.side_effect = GatewayError("Gateway unavailable")
    await coordinator.async_refresh()
    assert not coordinator.last_update_success
    assert coordinator.data["status"]["data"] == first["status"]["data"]
    assert coordinator.data["status"]["freshness"]["stale"] is True
    assert first["status"]["freshness"]["stale"] is False
    client.async_get.assert_not_awaited()
