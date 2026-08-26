# Specialized Panel Compliance Audit

**Audit target:** NIKAS Specialized Panel UI Standard v1.5
**Audited main:** `795484c99d8779665822ac3edc255882b592b469`
**Policy:** audit only; no runtime exists to rewrite in this PR.

## Summary

This repository is intentionally a bootstrap. README states that the Home Assistant integration will be introduced only after the gateway management API is defined and verified. Therefore the synchronized standard and approved repository identity are present, while every runtime-specific item remains a GAP rather than an unverified PASS.

## Compliance

| Requirement | Result | Evidence / required correction |
|---|---|---|
| Standard is synchronized and non-contradictory | PASS | `docs/NIKAS_SPECIALIZED_PANEL_UI_STANDARD.md` contains v1.5 and points to the canonical source. |
| Integration implementation and HACS package | GAP | No `custom_components/<domain>`, `manifest.json` or `hacs.json` exists. Define the verified API/domain first, then add the supported custom Integration package and align README. |
| Specialized panel route/registration | GAP | No `panel.json`, panel registration or frontend entry exists. |
| Single viewport, native scroll at 100%, >100 axis-limited pan | GAP | No runtime to verify. Implement directly to v1.5; do not copy the superseded always-transform-pan pattern. |
| Header exact UPS shell | GAP | No runtime. Implement fixed 62/60px Header, 52/1fr/52 (48 narrow), 44×44 plaques, radius 16/border/card/shadow, icons 25, menu primary-text, Refresh primary, title 21 and subtitle 12. |
| Permanent HA menu left / internal parent navigation | GAP | No runtime. Future Header must always emit composed/bubbling `hass-toggle-menu`; Back belongs in content. |
| Bottom Bar exact UPS shell | GAP | No runtime. Future panel must use fixed full-width safe-area bar, 52px minimum tabs, `ha-icon` 28px, 12/700 labels, ~11% active primary background. |
| Mandatory iPhone acceptance | GAP | No panel build exists to test. |
| Approved source brand asset exists | PASS | The selected theme-neutral square alpha mark is preserved at `assets/icon.png`. |
| Integration icon packaged through supported path | GAP | No integration package exists yet. When the verified `vless_gateway` domain is implemented, copy the approved mark to `custom_components/vless_gateway/brand/icon.png`; do not create a fictitious package only to claim compliance. |
| Repository visual identity | PASS | README displays `assets/icon.png`; the same square asset is suitable for repository avatar/social-preview configuration. |

## Contradiction prevention for first implementation

- Do not set `native_scroll: false` or unconditional `one_pointer_pan: true`.
- Do not put Back or gateway commands in the permanent left Header rail.
- Do not use text glyphs for Header/Bottom icons.
- Do not claim a brand is integrated when the mandatory packaged `custom_components/<domain>/brand/icon.png` is absent.
- Keep API verification and domain UI semantics separate from shell compliance.

## Future phone acceptance

Before enabling the panel for users, test a long Diagnostics view and every tab on iPhone against the full mandatory acceptance list in the standard.


<!-- v1.6-adoption -->
## v1.6 adoption delta — 2026-08-26

This bootstrap has no panel runtime, so runtime requirements remain GAP rather than assumed PASS.

- **Indicator policy:** **NOT ENABLED.** A future VLESS panel may add the two-level indicator only after a separate explicit requirement defines the factual local/cloud/reserve path.
- Future runtime must implement stable DOM point updates, stationary fixed chrome, sole Work Viewport scroll ownership and the LIDER typography scale directly from v1.6.
- Repository identity `assets/icon.png` is present.
- Packaged `custom_components/<domain>/brand/icon.png` remains a GAP until the Home Assistant integration package is introduced.
