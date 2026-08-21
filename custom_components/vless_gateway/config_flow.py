"""Config flow for VLESS Gateway."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import VlessGatewayApi, VlessGatewayApiError, VlessGatewayAuthError
from .const import CONF_BASE_URL, CONF_TOKEN, DEFAULT_NAME, DOMAIN


async def _validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    api = VlessGatewayApi(
        async_get_clientsession(hass),
        data[CONF_BASE_URL],
        data.get(CONF_TOKEN, ""),
    )
    status = await api.async_get_status()
    gateway = status.get("gateway", {}) if isinstance(status.get("gateway"), dict) else {}
    return {
        "title": gateway.get("name") or DEFAULT_NAME,
        "unique_id": gateway.get("id") or data[CONF_BASE_URL].rstrip("/"),
    }


class VlessGatewayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for VLESS Gateway."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await _validate_input(self.hass, user_input)
            except VlessGatewayAuthError:
                errors["base"] = "invalid_auth"
            except VlessGatewayApiError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(str(info["unique_id"]))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=str(info["title"]), data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL): str,
                vol.Optional(CONF_TOKEN, default=""): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
