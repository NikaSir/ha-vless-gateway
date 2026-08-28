# Update and publication policy

## Source of truth

- `main` is the canonical source branch.
- This repository does not publish GitHub Releases or attach generated archives through the Releases API.
- Reviewed pull requests and committed source are the delivery record during bootstrap.
- Automatic release tags are not used; a future internal integration version does not by itself require a Git tag.

## Version lineage

Existing project version history, once implementation begins, must be preserved during GitHub migration. Repository bootstrap is not a functional update.

Before HACS publication, the integration manifest version format must be validated against current Home Assistant/HACS requirements. Until that validation is complete, no synthetic version number is introduced by this repository scaffold.

## Publication gate

Before an accepted update is merged into `main`:

1. Repository checks are green.
2. Functional tests for the affected integration behavior are complete.
3. `CHANGELOG.md` is updated.
4. No gateway credentials, private keys, tokens or private diagnostics are present in tracked files or generated assets.
5. The accepted implementation remains traceable to the reviewed pull request and merged commit; no GitHub Release or automatic release tag is created.
