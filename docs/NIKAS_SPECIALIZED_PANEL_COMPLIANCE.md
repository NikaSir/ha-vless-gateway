# Specialized Panel Compliance Audit

**Audit target:** NikaS Specialized Panel UI Standard v1.8 and Navigation Contract v1.0
**Audited main:** `1748dbfa3c3e32eaf2cbfc3c4ee094ab2d1cf43b`
**Repository state:** bootstrap only; no integration or specialized-panel runtime exists

## Summary

VLESS Gateway does not yet ship a Home Assistant integration, HACS package, panel route or frontend. Runtime requirements therefore remain an explicit **GAP** rather than being reported as unverified passes. The v1.8 UI and navigation contracts, approved repository identity and automated readiness checks are present now; the first real implementation must satisfy them directly.

## Compliance

| Requirement | Result | Evidence / required correction |
|---|---|---|
| Standard synchronized and non-contradictory | PASS | The canonical v1.8 UI standard and Navigation Contract v1.0 are pinned by checksum and supersede older shell guidance. |
| Machine-readable readiness decision | PASS | `docs/SPECIALIZED_PANEL_READINESS.json` records that integration/panel runtime are absent and prevents false runtime claims. |
| Integration implementation and HACS package | DEFERRED | No `custom_components/vless_gateway`, manifest or `hacs.json` exists. Define and verify the gateway management API before adding the package. |
| Specialized panel route and production entry | DEFERRED | No panel registration, route, web component or frontend bundle exists. |
| Fixed shell and sole scroll owner | DEFERRED | Future runtime must keep Header/selector/Bottom Bar outside one Work Viewport; the outer page must not scroll. |
| Scale and scroll contract | DEFERRED | Future runtime must implement 75–200% focal pinch, 97–103% snap, stationary two-finger reset, native vertical scroll at 100% and bounded overflow-axis pan only above 100%. |
| Stable DOM / no polling or tab flicker | DEFERRED | Future runtime must mount shell/views once, point-patch telemetry and preserve Header, viewport, images, tabs and Bottom Bar identities. |
| UPS Header geometry | DEFERRED | Future Header: 52/1fr/52 rails (48 narrow), matching 44×44 radius-16 plaques, 25px icons, 23/14 title/subtitle and 21/13 narrow. |
| Native HA menu, title return and Refresh | DEFERRED | Left control must be `mdi:menu`; the centered two-line title plaque returns to the captured NikaS base route without `history.back()`; optional Refresh uses a matching plaque. |
| Bottom Tab Bar | DEFERRED | Future bar must be fixed, full-width and safe-area aware, with MDI `ha-icon` 28px, 12/700 labels and primary-colour active tint. |
| Optional common indicator | PASS | Explicitly **disabled**. It may be introduced only by a future repository-specific request; no transport/freshness semantics are invented during bootstrap. |
| Typography | DEFERRED | Future meaningful text range is 12–25px; 9–10px is limited to redundant non-interactive schematic annotations. |
| Repository identity | PASS | README displays the approved 512×512 alpha PNG at `assets/icon.png`; CI validates it. |
| Packaged integration icon | DEFERRED | No integration package exists. When the verified domain is implemented, the approved mark must ship as `custom_components/vless_gateway/brand/icon.png`; do not create a fictitious package only to host it. |
| Mandatory iPhone acceptance | DEFERRED | Required after the first panel build and before user enablement. |

## Contradiction prevention for first implementation

- Do not claim runtime compliance while `runtime_present` is false.
- Do not use unconditional one-finger pan, native horizontal scroll, nested zoom wrappers or permanent zoom controls.
- Do not put Back, gateway commands or text-glyph icons in permanent navigation rails.
- Do not rebuild `shadowRoot` on Home Assistant polling or tab changes.
- Do not introduce the common connection/freshness indicator without an explicit VLESS-specific request.
- Do not use meaningful text below 12px or above 25px.
- Do not claim an integration icon until a real supported integration package exists.

## Future phone acceptance

Before enabling a real panel, complete every v1.8 iPhone check, including source-route return from all three base panels, long Diagnostics scrolling, fixed Header/Bottom Bar during inertia and boundary pull, bounded pan, pinch stability, more-info safety, ten tab switches without a blank frame and repeated polling during upward scroll.
