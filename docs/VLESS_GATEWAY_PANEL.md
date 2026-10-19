# VLESS Gateway read-only panel

## Ownership

- Home Assistant integration and panel: `NikaSir/ha-vless-gateway`.
- Gateway OS, provisioning, routing, VLESS/Xray/sing-box, systemd and firewall: `NikaSir/vless-gateway`.
- Panel route: `/dashboard-vless-gateway`.
- Base-panel fallback: `/dashboard-infrastructure/overview`.

The Home Assistant repository must not duplicate gateway configuration or store UUIDs, private keys, access tokens, server addresses or production network secrets.

## Current scope

UI and integration version `1.0.0-beta001` consume gateway API v1 through a shared HA coordinator. The host-bound NikaS UI v2.2 / Shell v2.1 composition and existing navigation are retained. Real-device and phone acceptance remain required.

Views:

1. `overview` — current state, intended traffic topology and primary telemetry;
2. `routes` — route/mode/bypass visibility;
3. `traffic` — live rates, volume and connection count;
4. `diagnostics` — raw entity state, timestamps and all attributes.

## Entity-role contract

Live cards are bound only through `panel.config.entity_roles`. An absent role renders `Нет данных`; a configured entity missing from `hass.states` renders `Источник недоступен`. The scaffold never searches for a name-shaped entity ID.

Roles backed by the API v1 consumer:

| View | Role |
|---|---|
| Overview | `gateway_status`, `lan_status`, `tunnel_status`, `vless_server_status`, `internet_status`, `active_route`, `latency`, `uptime` |
| Routes | `active_route`, `routing_mode`, `bypass_rules`, `last_route_change`, `default_route`, `dns_route`, `tunnel_status` |
| Traffic | `download_rate`, `upload_rate`, `routed_traffic`, `active_connections`, `traffic_today`, `traffic_month`, `latency` |

Diagnostics combines:

- every valid entity ID explicitly assigned to a role;
- every entity whose Home Assistant entity-registry `platform` is `vless_gateway`.

## Write policy

The panel is read-only and contains no `hass.callService()` calls. Route switching, service restart, configuration reload and other commands remain excluded until all of the following exist:

- documented gateway API and authentication model;
- explicit Home Assistant services owned by the integration;
- target availability checks and fail-closed behavior;
- confirmation UI for every state-changing action;
- factual success/failure acknowledgement from the gateway.

## Frontend build

```bash
node scripts/build-frontend-bundle.mjs
node scripts/build-frontend-bundle.mjs --check
node --check custom_components/vless_gateway/frontend/vless-gateway-panel.js
```

The production module is a single autonomous bundle. The vendored Shell v2.1 source kit and the other files under `frontend/src` are build inputs only and are never imported at runtime.
