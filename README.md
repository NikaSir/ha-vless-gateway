# VLESS Gateway for Home Assistant

Custom Home Assistant integration for monitoring and controlling the separate **VLESS Gateway** project.

## Scope boundary

This repository contains only the Home Assistant integration: configuration, entities, commands/services, diagnostics, tests, documentation, HACS packaging, and releases.

The gateway operating system, routing/VLESS implementation, provisioning scripts, and network appliance configuration belong in **`NikaSir/vless-gateway`** and must not be duplicated here.

## Status

Repository bootstrap is complete; integration implementation will be introduced when the gateway management contract/API is defined and verified.

## Repository policy

- Default branch: `main`.
- No gateway credentials, private keys, UUIDs, access tokens, or production network secrets may be committed.
- The integration must depend on a documented gateway interface rather than undocumented host internals.
- Shared contribution/security defaults are inherited from `NikaSir/.github` unless overridden here.

## Target layout

```text
custom_components/vless_gateway/
docs/
.github/workflows/
hacs.json
```
