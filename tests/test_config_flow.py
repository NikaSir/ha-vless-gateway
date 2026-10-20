from unittest.mock import AsyncMock, patch
import pytest
from homeassistant.config_entries import SOURCE_USER
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry
from custom_components.vless_gateway.api import GatewayAuthError


@pytest.mark.asyncio
async def test_flow_validates_connection_and_stores_token_only_in_entry(hass):
    with (
        patch(
            "custom_components.vless_gateway.config_flow.GatewayClient.async_refresh",
            new_callable=AsyncMock,
            return_value={},
        ),
        patch(
            "custom_components.vless_gateway.async_setup_entry",
            new_callable=AsyncMock,
            return_value=True,
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            "vless_gateway", context={"source": SOURCE_USER}
        )
        assert result["type"] == FlowResultType.FORM
        data = {
            "base_url": "http://192.168.10.5:9080",
            "api_token": "test-only-token",
            "allow_http": True,
        }
        result = await hass.config_entries.flow.async_configure(result["flow_id"], data)
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"]["api_token"] == "test-only-token"
        assert "options" not in result or "api_token" not in result["options"]


@pytest.mark.asyncio
async def test_duplicate_and_auth_failure(hass):
    with patch(
        "custom_components.vless_gateway.config_flow.GatewayClient.async_refresh",
        new_callable=AsyncMock,
        side_effect=GatewayAuthError("safe"),
    ):
        result = await hass.config_entries.flow.async_init(
            "vless_gateway", context={"source": SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "base_url": "https://gateway.example",
                "api_token": "test-only-token",
                "allow_http": False,
            },
        )
        assert result["errors"] == {"base": "invalid_auth"}
    entry = MockConfigEntry(domain="vless_gateway", unique_id="vless_gateway", data={})
    entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        "vless_gateway", context={"source": SOURCE_USER}
    )
    assert result["type"] == FlowResultType.ABORT
