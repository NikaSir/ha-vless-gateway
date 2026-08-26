# Specialized Panel Compliance Audit

**Audit target:** NikaS Specialized Panel UI Standard v1.5
**Audited main:** `795484c99d8779665822ac3edc255882b592b469`
**Policy:** audit only; no runtime exists to rewrite in this PR.

## Summary

This repository is intentionally a bootstrap. README states that the Home Assistant integration will be introduced only after the gateway management API is defined and verified. Therefore the synchronized standard is present, but every runtime-specific item remains a GAP rather than an unverified PASS.

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
| Approved source brand asset exists | GAP | No icon/logo/light/dark source exists. Do not invent a brand; obtain an approved gateway/integration source asset. |
| Integration icon packaged through supported path | GAP | Domain is not yet implemented. After domain approval, add the mandatory HACS asset at `custom_components/<domain>/brand/icon.png`; add dark/logo variants when required. |
| Repository visual identity | GAP | README has no logo/hero and GitHub social preview/avatar is not represented. After asset approval, add a README visual and configure repository social preview. |

## Contradiction prevention for first implementation

- Do not set `native_scroll: false` or unconditional `one_pointer_pan: true`.
- Do not put Back or gateway commands in the permanent left Header rail.
- Do not use text glyphs for Header/Bottom icons.
- Do not claim a brand is integrated when the mandatory packaged `custom_components/<domain>/brand/icon.png` is absent.
- Keep API verification and domain UI semantics separate from shell compliance.

## Future phone acceptance

Before enabling the panel for users, test a long Diagnostics view and every tab on iPhone against the full mandatory acceptance list in the standard.
