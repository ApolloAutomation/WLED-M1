# M-1 firmware release checklist (bundle m1-bN)

Every step, in order. The install page and the FlashScripts flash script both serve
`M-1_full_install.bin` from the release, so a release is not done until both are
re-pointed and hash-checked. Nothing in this process touches upstream WLED.

## 1. Scope and branch
- Work on a branch off the product branch (see CLAUDE.md, Branches) and merge by PR.
- Upstream changes come only from an upstream release tag. A cherry-pick from upstream
  (for example a security fix before the next tag exists) is an explicit, recorded
  exception: use `git cherry-pick -x` so the upstream commit is named.
- If apollo/fs changes, the first-boot look changes too: update FlashScripts LED_PASS text
  (step 7) and the customer docs.

## 2. Gates (on hardware, with the exact build you will ship)
- Virgin-boot gate (factory-erased unit, full install).
- QA_CHECKLIST.md D13 AP walkthrough.
- OTA gate: previous bundle (m1-bN-1) to this build through the WLED update page, with
  settings and presets surviving. When WLED-MM units are still in the field, also repeat
  QA_CHECKLIST.md D2 (WLED-MM 14.5.1 to this build).

## 3. Build the artifacts
- Clean tree at the commit you gated: `git status` shows nothing to commit.
- `apollo/build_artifacts.sh`. On Apple silicon without Rosetta, mklittlefs cannot run:
  if apollo/fs is unchanged since the last release, pass
  `--littlefs <last release's littlefs.bin>` (in the firmware vault).
- Keep everything in apollo/out: both binaries, littlefs.bin, firmware.elf, firmware.map,
  bootloader.bin, partitions.bin, BUILD_INFO.txt, SHA256SUMS.txt.

## 4. Tag (push the tag BEFORE creating the release)
```
git tag -a m1-bN -m "Apollo M-1 firmware bundle bN (gated YYYY-MM-DD)" <gated commit>
git push origin refs/tags/m1-bN                       # never `git push --tags`
git ls-remote origin 'refs/tags/m1-bN^{}'             # must print <gated commit>
```
`m1-*` tags cannot be moved or deleted once pushed (repo ruleset), so check the commit first.

## 5. GitHub release (immutable once published)
```
gh release create m1-bN -R ApolloAutomation/WLED-M1 --verify-tag \
  --title "Apollo M-1 firmware, bundle bN" --notes-file <notes.md> \
  apollo/out/M-1_full_install.bin apollo/out/M-1_ota.bin
gh release view m1-bN -R ApolloAutomation/WLED-M1 --json assets --jq '.assets[] | .name + " " + .digest'
```
- `--verify-tag` stops gh from tagging the default branch when the tag is missing.
- The asset digests must equal the two lines in apollo/out/SHA256SUMS.txt.
- Release immutability is on: assets cannot be replaced after publishing. A bad release
  gets a new tag (m1-bN+1); the tag name cannot be reused.
- Publishing starts an "apollo-pages" run that fails on the github-pages branch policy.
  That red run is expected; deploy in step 6.

## 6. Install page (install.apolloautomation.com/#/m-1)
```
gh workflow run apollo-pages.yml -R ApolloAutomation/WLED-M1 --ref main
```
- It copies apollo/installer/manifest.json from `main` and `M-1_full_install.bin` from the
  release marked Latest. If the WLED base version changed, update the manifest "version"
  and the installer's devices.json label first.
- After the run succeeds (allow up to 10 minutes of CDN cache):
  `curl -sL https://apolloautomation.github.io/WLED-M1/M-1_full_install.bin | shasum -a 256`
  must equal the new full-install hash.

## 7. FlashScripts (ApolloAutomation/FlashScripts, M-1/flash-prod.sh)
- In one PR: PINNED_URL (new tag), PINNED_SHA256, PINNED_VERSION, and LED_PASS /
  LED_PASS_SHORT if the first-boot look changed.
- Verify: `curl -sL <PINNED_URL> | shasum -a 256` equals PINNED_SHA256.

## 8. Firmware vault
- Company Google Drive, Apollo Firmware Vault/M-1/m1-bN: everything from apollo/out, the
  release notes, and `git bundle create WLED-M1-all.bundle --all`.
- `shasum -a 256 -c SHA256SUMS.txt` inside the Drive folder.

## 9. Final check
- Install page: manifest returns 200 and the bin hash is the new one.
- FlashScripts PINNED_URL hash is the new one.
- WLED-MM-M1 manifests still return 200 (the installer still offers them).
- Customer docs and wiki match what the unit now does.
