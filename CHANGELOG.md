# Changelog

All notable project changes are recorded here.

## [Unreleased]

### Added

- Initial GitHub repository bootstrap and integration boundary documentation.
- Contract-first Home Assistant custom component under `custom_components/vless_gateway`.
- UI configuration flow for local gateway API URL and optional bearer token.
- DataUpdateCoordinator polling the documented `GET /api/v1/status` endpoint every 30 seconds.
- Tunnel connectivity binary sensor.
- Active route, uptime, tunnel latency, RX bytes, and TX bytes sensors.
- Manual `Refresh now` button.
- Russian entity/config-flow translations and HACS metadata.
- Management API v1 contract in `docs/API_CONTRACT.md`.
