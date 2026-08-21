# VLESS Gateway for Home Assistant

Custom Home Assistant integration for monitoring the separate **VLESS Gateway** project.

## Scope boundary

This repository contains only the Home Assistant integration: configuration, entities, commands/services, diagnostics, tests, documentation, HACS packaging, and releases.

The gateway operating system, routing/VLESS implementation, provisioning scripts, and network appliance configuration belong in **`NikaSir/vless-gateway`** and must not be duplicated here.

## Status

Initial contract-first integration baseline is implemented on the development branch. It uses only the documented local management API and does not inspect gateway internals over SSH.

Current entities:

- binary sensor: tunnel connectivity;
- sensors: active route, gateway uptime, tunnel latency, received bytes, transmitted bytes;
- button: immediate Home Assistant refresh.

Control operations such as restart, failover, tunnel reset, policy switching, and software update are intentionally deferred until their API semantics are explicitly defined and verified.

## Management API

The integration consumes `GET /api/v1/status`. The normative contract is documented in [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md).

## Installation target

The custom component lives in:

```text
custom_components/vless_gateway/
```

HACS metadata is provided through `hacs.json`.

## Repository policy

- Default branch: `main`.
- No gateway credentials, private keys, UUIDs, access tokens, or production network secrets may be committed.
- The integration must depend on a documented gateway interface rather than undocumented host internals.
- Shared contribution/security defaults are inherited from `NikaSir/.github` unless overridden here.
