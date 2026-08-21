# VLESS Gateway management API contract v1

This document defines the boundary consumed by the Home Assistant integration. The integration must not depend on SSH, systemd, routing-table scraping, sing-box/Xray files, or other gateway implementation details.

## Transport

- Local HTTP or HTTPS endpoint reachable from Home Assistant.
- Base URL is configured by the user, for example `http://192.168.1.50:8787`.
- Optional bearer-token authentication: `Authorization: Bearer <token>`.
- JSON responses encoded as UTF-8.

## `GET /api/v1/status`

Returns one atomic status snapshot.

```json
{
  "api_version": "1",
  "gateway": {
    "id": "vless-gateway-01",
    "name": "VLESS Gateway",
    "uptime_seconds": 123456
  },
  "tunnel": {
    "connected": true,
    "latency_ms": 42,
    "rx_bytes": 123456789,
    "tx_bytes": 987654321
  },
  "routing": {
    "active_route": "vless"
  }
}
```

### Required semantics

- `gateway.id`: stable identifier that does not change across reboot or IP change.
- `gateway.name`: human-readable gateway name.
- `gateway.uptime_seconds`: gateway OS/service uptime represented in seconds.
- `tunnel.connected`: factual tunnel connectivity state. It must not be inferred only from process existence.
- `tunnel.latency_ms`: current or most recent valid tunnel health-check latency in milliseconds; `null` when unavailable.
- `tunnel.rx_bytes` / `tx_bytes`: monotonically increasing counters for tunnel traffic for the current counter epoch.
- `routing.active_route`: factual currently selected route, initially `vless`, `direct`, or another documented future value.

## HTTP status handling

- `200`: valid status response.
- `401` / `403`: authentication rejected.
- Other status codes: temporary API failure unless explicitly added to a later contract revision.

## Compatibility

Fields may be added in API v1 without breaking clients. Existing field meaning must not change. Breaking changes require a new API major version.

## Control endpoints

No control endpoints are part of the initial contract. Restart, failover, tunnel reset, policy changes, and software update operations will be added only after their safety and idempotency semantics are defined and verified on the gateway project.
