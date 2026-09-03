# Specialized Panel Compliance Audit

**Audit target:** NikaS Specialized Panel UI Standard v2.2, Navigation Contract v1.2 and Shell v2.1

**Repository state:** installable VLESS Gateway panel scaffold

**Runtime version:** integration `0.1.2`, UI `0.1.1`

## Summary

The repository now contains an installable panel-only Home Assistant integration and an autonomous frontend scaffold. The panel is intentionally read-only until the separate gateway project exposes a reviewed management/telemetry API. It never guesses entity IDs: overview, route and traffic values use only `panel.config.entity_roles`, while Diagnostics additionally reads entities whose Home Assistant registry platform is `vless_gateway`.

Automated contract checks can verify the implementation shape. Real iPhone portrait, cold-load, restart and Home Assistant Cloud acceptance remain required before runtime compliance is claimed.

## Compliance

| Requirement | Result | Evidence / remaining work |
|---|---|---|
| Standard synchronized and non-contradictory | PASS | Canonical v2.2 UI standard and Navigation Contract v1.2 remain pinned by checksum. |
| Installable integration and HACS package | PASS | `custom_components/vless_gateway`, config flow, manifest, translations and `hacs.json` are present. |
| Specialized panel route | PASS | The integration registers `/dashboard-vless-gateway`, owned by `vless_gateway`, with `/dashboard-infrastructure/overview` as safe fallback. |
| Autonomous production bundle | PASS | One deterministic `vless-gateway-panel.js` is built from local sources; runtime imports and historical bundle chains are absent. |
| Data truth and command safety | PASS | No fixed entity IDs are shipped. Missing, `unknown` and `unavailable` states are explicit. The UI contains no Home Assistant service calls. |
| Fixed shell and sole scroll owner | PASS | The vendored Shell v2.1 binds to `ha-panel`; Header and Bottom Tab Bar remain outside one viewport, and the capture-phase boundary guard prevents outer-page scrolling. |
| Scale and scroll contract | PASS | The gesture controller implements 75–200% focal pinch, 97–103% snap, stationary two-finger reset, native vertical scroll at 100% and bounded pan only above 100%. |
| Stable DOM / no polling or tab flicker | PASS | The shell mounts once. Visited tab subtrees are cached and hidden/inert; current-view values are reconciled without replacing fixed chrome. |
| Header geometry | PASS | Canonical 60px Shell v2.1 Header with 52/1fr/52 rails (48 narrow), matching 44×44 plaques, 25px icons and 23/14 typography (21/13 narrow). |
| Native HA menu, title return and Refresh | PASS | Left rail dispatches `hass-toggle-menu`; the centered LIDER-style title captures and returns to the originating base route; Refresh only reloads safe registry metadata. |
| Bottom Tab Bar | PASS | Fixed full-width safe-area-aware four-tab bar with 26px MDI icons, 12/700 labels and primary active tint. |
| Optional common connection indicator | PASS | Explicitly disabled. It remains opt-in after real transport/freshness semantics are known. |
| Typography | PASS | Meaningful panel text stays within 12–25px. |
| Repository and packaged identity | PASS | The approved 512×512 alpha PNG is used in README and packaged at `custom_components/vless_gateway/brand/icon.png`. |
| Mandatory real-device acceptance | PENDING | Test on iPhone Pro Max portrait after the branch is installed in Home Assistant. |

## Scaffold content

- **Обзор:** factual Hero, intended LAN → Gateway → VLESS server → Internet topology and primary metrics.
- **Маршруты:** active route, routing mode, bypass state and network-contour placeholders.
- **Трафик:** receive/transmit rates, routed traffic, connection count and counters.
- **Диагн.:** integration identity plus raw state, timestamps and all attributes of involved entities.

## Acceptance still required

Before enabling the panel as operational, verify on the real phone:

1. cold load on LAN and Home Assistant Cloud/Nabu Casa;
2. full Home Assistant restart followed by repeated panel opens;
3. source-aware return from all applicable base panels;
4. fixed Header and Bottom Tab Bar during long Diagnostics scrolling and boundary pull;
5. focal pinch, bounded enlarged pan, 97–103% snap and stationary two-finger reset;
6. long-press `more-info` without accidental activation during pinch;
7. at least ten tab switches and repeated Home Assistant state updates without blank frames.
