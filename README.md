# VLESS Gateway for Home Assistant

<p align="center">
  <img src="assets/icon.png" width="180" alt="VLESS Gateway repository icon">
</p>

Read-only API v1 integration and panel for the separate **VLESS Gateway** project on NanoPi R5S.

## Status

- Integration version: `1.0.0-beta001`.
- Panel UI version: `1.0.0-beta001`.
- Home Assistant route: `/dashboard-vless-gateway`.
- Parent route: `/home/overview`.
- Views: **Обзор**, **Маршруты**, **Трафик**, **Диагн.**
- Commands: disabled until the gateway API and safe write contract are verified.

The scaffold is intentionally honest when no telemetry exists: it renders `Нет данных`, preserves the complete application shell and never invents Home Assistant entity IDs. The optional common connection/freshness indicator is not enabled for VLESS Gateway and remains a separate product decision.

## Scope boundary

This repository owns:

- the Home Assistant custom integration package;
- the specialized panel and its autonomous frontend bundle;
- entity-role and diagnostics presentation contracts;
- HACS metadata, tests and panel documentation.

The NanoPi OS, routing/VLESS implementation, sing-box, procd and firewall belong in **`NikaSir/vless-gateway`** and must not be duplicated here.

No gateway credentials, private keys, UUIDs, access tokens, server addresses or production network secrets may be committed.

## Panel composition

The panel follows **NikaS Specialized Panel UI Standard v2.2**, **Navigation Contract v1.2** and host-bound **Shell v2.1**:

- fixed Home Assistant menu Header with the current S8 OMNI title/return geometry;
- one gesture-driven work viewport;
- fixed full-width safe-area-aware Bottom Tab Bar;
- host-bound sizing without `100dvh`, fixed-position takeover or Home Assistant outer-page scrolling;
- 75–200% focal pinch, 97–103% snap and two-finger double-tap reset;
- native vertical scrolling at 100%, bounded one-finger pan only above 100%;
- stable shell DOM and lazy persistent tab subtrees;
- meaningful typography within 12–25px;
- long press on factual entity-backed content opens native Home Assistant `more-info`.

See [`docs/VLESS_GATEWAY_PANEL.md`](docs/VLESS_GATEWAY_PANEL.md) for the reserved entity roles and write-safety boundary.

## Installation after merge

1. Add `https://github.com/NikaSir/ha-vless-gateway` to HACS as a custom **Integration** repository.
2. Install **VLESS Gateway** and restart Home Assistant.
3. Open **Settings → Devices & services → Add integration → VLESS Gateway**.
4. Enter the management URL and independent read-only API token, then open `/dashboard-vless-gateway`.

HTTPS is preferred. HTTP requires explicit consent for a literal private management IP. Tokens stay in the HA config entry and never enter panel config, entity attributes or browser assets. Existing empty scaffold entries retain the panel and can be connected through Reconfigure.

One coordinator polls status/routes/traffic/system/health every 15 seconds. Nineteen sensor/binary-sensor roles bind through actual HA registry IDs. Stale/unavailable values are unavailable; a factual zero remains zero. There are no write entities/services. The header shows full UI and integration versions.

## Development checks

```bash
node scripts/build-frontend-bundle.mjs --check
node --check custom_components/vless_gateway/frontend/vless-gateway-panel.js
node tests/shell_v2_harness.mjs
python -m unittest discover -s tests -v
python -m pytest -q tests/test_coordinator.py tests/test_config_flow.py tests/test_setup.py
python scripts/check_nikas_ui_standard.py
```

## Repository policy

Runtime tests use Python 3.14, Home Assistant 2026.10.0 and requirements.test.txt. The gateway contract source is recorded in tests/fixtures/api_v1/SOURCE.json. Actual device, soak and phone acceptance remain required.

- Default branch: `main`.
- GitHub Releases and automatic release tags are not used.
- Frontend history belongs in reviewed commits and merged pull requests, not runtime import chains.
- Shared contribution/security defaults are inherited from `NikaSir/.github` unless overridden here.
