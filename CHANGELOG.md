# Changelog

All notable project changes are recorded here.

## [Unreleased]

### Changed

- Bump the integration to `0.1.1`, prefix the Home Assistant/HACS name with `NikaS`
  and republish the approved local brand icon.
- Ship a standards-compliant 256×256 `icon.png` plus 512×512 `icon@2x.png`.

### Added

- Installable panel-only `vless_gateway` custom integration version `0.1.0`.
- Autonomous VLESS Gateway UI `0.1.0` at `/dashboard-vless-gateway`.
- Read-only `Обзор`, `Маршруты`, `Трафик` and `Диагн.` views.
- Declarative entity-role boundary and registry-backed raw Diagnostics without guessed entity IDs.
- Deterministic frontend build and runtime/data-truth contract tests.
- Packaged approved gateway mark at `custom_components/vless_gateway/brand/icon.png`.

### Changed

- Promoted the repository from readiness-only bootstrap to an installable panel scaffold.
- Keeps all state-changing commands disabled until the gateway API and fail-closed write contract are verified.
- Keeps the optional common connection/freshness indicator disabled until explicitly requested for verified transport semantics.
