# Apollo WLED-M1: rules for AI agents and contributors

This repository is Apollo Automation's M-1 firmware: upstream WLED (16.0.x release line)
plus the M-1 changes. WLED's coding conventions are in AGENTS.md (inherited from upstream).
The Apollo rules below take precedence over anything inherited from upstream.

## Never touch upstream WLED

- Never push to, open pull requests or issues against, or comment on wled/WLED (formerly
  Aircoookie/WLED), MoonModules/WLED-MM or netmindz/WLED-MM. Nothing goes upstream.
- This repository is a GitHub fork of wled/WLED, so the GitHub web UI and the gh CLI lean
  toward the parent repository. Every gh command that writes (pr create, issue create,
  release, api with POST/PATCH/DELETE) must pass `-R ApolloAutomation/WLED-M1`.
- The upstream PR drafts in apollo/UPSTREAM_*.md and the upstream PR plans in older session
  notes were WITHDRAWN on 2026-10-22. Do not act on them.
- AGENTS.md says pull requests target upstream's `main`. Here, pull requests target this
  repository's product branch (see Branches below).
- Local clones keep upstream as a fetch-only remote named `wled` (not `upstream`, which gh
  would prefer over origin) with its push URL disabled, and fetch upstream tags into
  `refs/remotes/wled-tags/` so `git push --tags` can never publish them.

## Taking upstream changes

- Merge an upstream release tag (for example v16.0.2) on a sync branch, then open a PR into
  the product branch. Never merge upstream `main` (17.0.0-dev on ESP-IDF 5; a 17.x move is
  its own port project).
- Never rebase or force-push published branches. Never run `git push --tags`; push only the
  new `m1-bN` tag.

## Branches

- `main`: the M-1 product branch (since 2026-10-22: WLED v16.0.1 + M-1 work, tag m1-b8)
  and the default branch. Changes go through pull requests; deletion and force-push are
  blocked. The install page deploys from it.
- `m1-wled-update`: the former product branch, frozen read-only at 30e8a0ed (the commit
  `main` took over) so old links and docs that name it still resolve. Do not use it.
- `archive/main-upstream-snapshot-2026-07` and `archive/main-before-product-2026-10-22`:
  the previous `main` (an upstream 17.0.0-dev snapshot plus the install-page workflow),
  frozen and kept for reference.

## Shipping: keep the install page and the flash script working

- The web installer (install.apolloautomation.com/#/m-1) reads
  https://apolloautomation.github.io/WLED-M1/manifest.json. The site is deployed by
  .github/workflows/apollo-pages.yml from `main`, by manual run:
  `gh workflow run apollo-pages.yml -R ApolloAutomation/WLED-M1 --ref main`.
  It copies apollo/installer/manifest.json and the `M-1_full_install.bin` asset of the
  release marked Latest. The github-pages environment only accepts `main`, so the
  release-published trigger does not deploy.
- ApolloAutomation/FlashScripts M-1/flash-prod.sh pins the release asset URL and its
  SHA-256. A new release bumps PINNED_URL, PINNED_SHA256 and PINNED_VERSION in the same
  change, then the Pages site is redeployed and both downloads are hash-checked.
- Never delete or replace a published release asset. Renaming this repository or making it
  private breaks the Pages URL and the flash script's unauthenticated download; move those
  consumers first.
- Each shipped release is archived (binaries, source bundle, libraries, toolchain, debug
  symbols) in the company Google Drive under Apollo Firmware Vault/M-1/<tag>.
- Build with env `apollo_m1` (its libraries are pinned in platformio.ini; keep them pinned).
  Firmware changes need the virgin-boot gate, the QA_CHECKLIST.md D13 AP walkthrough and an
  OTA gate before release.
- Releases follow apollo/RELEASE_CHECKLIST.md: push the m1-bN tag first, then
  `gh release create --verify-tag` (without it gh tags the default branch). Release
  immutability is on, and m1-* tags cannot be moved or deleted.
