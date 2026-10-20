"""Config flow for VLESS Gateway."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol

from .const import DOMAIN
from .api import (
    GatewayClient,
    GatewayError,
    GatewayAuthError,
    GatewaySchemaError,
    normalize_base_url,
)


class VlessGatewayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Create the single panel scaffold entry."""

    VERSION = 2

    async def _validate(self, values):
        data = dict(values)
        data["base_url"] = normalize_base_url(
            data["base_url"], allow_http=data.get("allow_http", False)
        )
        client = GatewayClient(
            data["base_url"],
            data["api_token"],
            async_get_clientsession(self.hass),
            allow_http=data.get("allow_http", False),
        )
        await client.async_refresh()
        return data

    async def _form(self, step_id, user_input=None, entry=None):
        errors = {}
        if user_input is not None:
            try:
                data = await self._validate(user_input)
            except GatewayAuthError:
                errors["base"] = "invalid_auth"
            except GatewaySchemaError:
                errors["base"] = "unsupported_schema"
            except GatewayError:
                errors["base"] = "cannot_connect"
            else:
                if entry is not None:
                    return self.async_update_reload_and_abort(entry, data_updates=data)
                return self.async_create_entry(title="VLESS Gateway", data=data)
        return self.async_show_form(
            step_id=step_id,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "base_url",
                        default=(entry.data.get("base_url", "") if entry else ""),
                    ): str,
                    vol.Required("api_token"): str,
                    vol.Optional(
                        "allow_http",
                        default=(
                            entry.data.get("allow_http", False) if entry else False
                        ),
                    ): bool,
                }
            ),
            errors=errors,
        )

    async def async_step_user(self, user_input=None):
        """Create the local panel entry."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return await self._form("user", user_input)

    async def async_step_reconfigure(self, user_input=None):
        return await self._form(
            "reconfigure", user_input, self._get_reconfigure_entry()
        )

    async def async_step_reauth(self, entry_data):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        return await self._form("reauth_confirm", user_input, self._get_reauth_entry())
