"""Explicit, allow-listed diagnostic export without configuration-entry secrets."""

from .api import GatewayError
from .const import DOMAIN, INTEGRATION_VERSION, PANEL_UI_VERSION


async def async_get_config_entry_diagnostics(hass, entry):
    result = {
        "integration_version": INTEGRATION_VERSION,
        "ui_version": PANEL_UI_VERSION,
        "schema_version": "1",
    }
    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if coordinator is None:
        return {**result, "available": False}
    try:
        response = await coordinator.async_diagnostic_snapshot()
        return {
            **result,
            "available": True,
            "gateway_state": response["state"],
            "last_update_success": coordinator.last_update_success,
        }
    except GatewayError:
        return {**result, "available": False, "error": "gateway_unavailable"}
