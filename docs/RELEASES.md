# Release policy

## Source of truth

- `main` is the canonical source branch.
- This repository does not publish GitHub Releases or attach generated archives through the Releases API.
- Reviewed pull requests and committed source are the delivery record during bootstrap.
- A future source tag, if needed for a verified HACS integration, must point to the exact reviewed commit; it does not authorize creating a GitHub Release.

## Version lineage

Existing project version history, once implementation begins, must be preserved during GitHub migration. Repository bootstrap is not a functional release.

Before HACS publication, the tag format and integration manifest version format must be validated against current Home Assistant/HACS requirements. Until that validation is complete, no synthetic version number is introduced by this repository scaffold.

## Release gate

Before a release:

1. Repository checks are green.
2. Functional tests for the affected integration behavior are complete.
3. `CHANGELOG.md` is updated.
4. No gateway credentials, private keys, tokens, or private diagnostics are present in tracked files or release artifacts.
5. Any required source tag points to the exact reviewed commit; no GitHub Release is created.

Published tags are treated as immutable.
