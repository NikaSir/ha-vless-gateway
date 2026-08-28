# Update and publication policy

## Source of truth

- `main` is the canonical source branch.
- This repository does not publish GitHub Releases or attach generated archives through the Releases API.
- Reviewed pull requests and committed source are the delivery record.
- Automatic release tags are not used; an integration version does not by itself require a Git tag.

## Version lineage

Integration and UI versions are explicit numeric `X.Y.Z` values. Version `0.1.0` identifies the first installable read-only panel scaffold; it does not claim that the separate gateway management API is implemented.

The integration manifest, panel metadata, production bundle cache key and visible `UI vX.Y.Z` line must remain coherent for every accepted update.

## Publication gate

Before an accepted update is merged into `main`:

1. Repository checks are green.
2. Functional tests for the affected integration behavior are complete.
3. `CHANGELOG.md` is updated.
4. No gateway credentials, private keys, tokens or private diagnostics are present in tracked files or generated assets.
5. The accepted implementation remains traceable to the reviewed pull request and merged commit; no GitHub Release or automatic release tag is created.
