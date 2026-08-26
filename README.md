# VLESS Gateway for Home Assistant

<p align="center">
  <img src="assets/icon.png" width="180" alt="VLESS Gateway repository icon">
</p>

Reserved Home Assistant integration repository for the separate **VLESS Gateway** project.

## Scope boundary

This repository currently contains the reviewed integration boundary and specialized-panel readiness contracts only. Configuration, entities, commands/services, diagnostics and HACS packaging will be added after the gateway API is defined and verified.

The gateway operating system, routing/VLESS implementation, provisioning scripts, and network appliance configuration belong in **`NikaSir/vless-gateway`** and must not be duplicated here.

## Status

Repository bootstrap is complete; integration implementation will be introduced when the gateway management contract/API is defined and verified.

There is no installable Home Assistant integration, registered panel route or HACS package yet. The future panel must implement **NikaS Specialized Panel UI Standard v1.6** directly; the current compliance audit is in `docs/NIKAS_SPECIALIZED_PANEL_COMPLIANCE.md` and the machine-readable decision is in `docs/SPECIALIZED_PANEL_READINESS.json`.

The optional common connection/freshness indicator is not enabled for VLESS Gateway. It may be added only by an explicit repository-specific request after real transport semantics exist. The first runtime must also mount a stationary Header and Bottom Bar around one zoom viewport, use stable point-patched DOM without polling/tab flicker, and keep meaningful text within 12–25px.

The approved square gateway mark is stored at `assets/icon.png` and is the canonical repository visual. When the verified Home Assistant integration package is introduced, this same mark must be packaged at `custom_components/vless_gateway/brand/icon.png`; an empty or fictitious integration skeleton must not be created only to host an icon.

## Repository policy

- Default branch: `main`.
- GitHub Releases are not used; bootstrap changes are delivered as reviewed source commits/PRs.
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
