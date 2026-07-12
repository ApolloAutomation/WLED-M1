# SUMMARY: Apollo M-1 migration to upstream WLED

Date: 2026-07-11. Session was build-only (no hardware reachable, M1_ALLOW_FLASH
unset). Everything below is committed on branch apollo/m1 of the local clone at
/Users/justinapollo/Code/ApolloAutomation/WLED unless noted.

## What you asked for versus what was found

1. The 32x32 bug has a concrete root cause. The shipping WLED-MM build compiles
   DEFAULT_LED_TYPE=101, and in WLED-MM type 101 IS the 32x32 HUB75 panel (64x64 is
   103). Factory units default to the wrong panel size by definition, ABL defaults
   to 1500 mA, and no 2D matrix is seeded. The wiki page exists to hand-fix all of
   that.
2. Upstream had no v16.1 tag as of today. Work is pinned at v16.0.1, the newest
   release (contains the Seengreat pinout PR the task referenced). Rebasing to a
   future 16.1 should be trivial; the delta is small.
3. The planned APOLLO_M1_PINOUT upstream PR is unnecessary. Upstream 16.0.1 already
   contains the M-1 pinout (MOONHUB_S3_PINOUT, byte-identical GPIOs) and even a
   matching board env (esp32s3dev_16MB_opi_hub75) with the M-1 aux pins and I2S mic
   pins. The MoonModules HUB75 work was upstreamed. What upstream was missing is a
   working zero-config first boot for HUB75, and that is the PR prepared instead.
4. There are no shipped presets. Phase 4 index-mapping was not applicable (verified
   repo-wide: WLED-MM-M1 ships no presets.json or cfg.json anywhere).
5. Pin collision check passed: HUB75 {1,4,5,6,7,8,9,13,16,18,21,38,47,48} vs I2S
   {10,11,12} vs button 0, relay 15: disjoint.

## Deliverables

Firmware (branch apollo/m1, 7 commits on top of v16.0.1):
- [env:apollo_m1] in platformio.ini: extends the upstream T7-S3 HUB75 env; Apollo
  identity, 64x64 first-boot defaults, ABL off, CDC_ON_BOOT=0, mic pins, unique AP
  SSID and mDNS hostname per unit.
- cfg.cpp first-boot fix (HUB75 slots not sanitized as GPIOs) + optional
  DEFAULT_PANEL_WIDTH/HEIGHT 2D seeding. This is the erase-proof fix.
- WLED_MM_HUB75_MIGRATION: OTA from WLED-MM keeps the display working by rewriting
  the old type-101/103 bus entry to the 16.x layout on first read.
- WLED_MDNS_PREFIX define + AP SSID unique-suffix fix (uses WLED_AP_SSID, not brand).
- apollo/fs/cfg.json + presets.json factory filesystem content.
- apollo/build_artifacts.sh producing:
  - M-1_full_install.bin (16,711,680 bytes, flash at 0x0 after full erase, includes
    LittleFS with factory config)
  - M-1_ota.bin (1,250,064 bytes = 39 percent of the 3 MB OTA slot, filesystem
    untouched)
- Build verified: pio run -e apollo_m1 SUCCESS. RAM 13.8 percent, flash 39.7 percent.
  Identity strings confirmed present in the binary; LittleFS image verified to
  contain cfg.json and presets.json.
- Partition table: byte-identical to the WLED-MM factory table (same CSV file), so
  OTA is safe and field filesystems stay at 0x610000.

Upstream PR (prepared, NOT opened):
- Branch hub75-first-boot-defaults, single commit 42c58077 off upstream/main, in
  worktree /Users/justinapollo/Code/ApolloAutomation/WLED-upstream-pr.
- PR description: apollo/UPSTREAM_PR.md. Needs the hardware pass before opening.

Installer (draft branch, NOT deployed):
- ApolloAutomation/installer branch feat/m1-wled-entry: M-1 added to devices.json
  pointing at the currently live WLED-MM manifests (registry validator passes);
  docs/m1-wled-migration.md documents the switch to the 16.0.1 manifest
  (apollo/installer/manifest.json, chipFamily ESP32-S3, full-erase flow) once
  hosting exists. Image asset images/m-1.jpg still needed.

Docs: MIGRATION_INVENTORY.md, DECISIONS.md, BLOCKED.md, PROGRESS.md, QA_CHECKLIST.md,
ROLLBACK.md, apollo/WIKI_REWRITE.md, baseline/.

## License (EUPL-1.2)
Compliant as set up: the fork is public, the LICENSE file is unchanged, all Apollo
modifications are committed publicly on the fork, WLED attribution and brand remain
(brand string stays WLED; Apollo identity lives in product/release/server strings).
Ship the source link (github.com/ApolloAutomation/wled) anywhere the firmware is
distributed, including install.apolloautomation.com, to keep the source-availability
obligation visibly satisfied. WLED is a project of the Open Home Foundation
ecosystem's wider community; no trademark issues introduced (we did not rebrand).

## Decisions you need to review (details in DECISIONS.md)
- A1/A6: mDNS is apollo-led-matrix-xxxxxx (6 MAC hex chars, not the wiki's literal
  name, and 6 chars rather than the task's 4) to avoid collisions.
- A2: AP SSID is Apollo M-1-xxxxxx (unique per unit).
- A3: the AP stays OPEN (matches the shipping build). Deliberate security posture
  decision to confirm.
- A4: server description compiles as "Apollo LED Matrix" (wiki value), not the old
  compiled "Apollo M-1".
- A7: AudioReactive ships compiled but disabled, matching WLED-MM shipping behavior;
  rev4 boards have no microphone. Flip is one define if you want it on by default.
- A5: work is on local branch apollo/m1; your GitHub fork only has main (the
  "add m1 to wled" branch was never pushed).

## Follow-ups for you
- Hardware QA: run QA_CHECKLIST.md top to bottom on rev4 and rev6 units, including
  the OTA-from-MM case and the 4-panel chain. Nothing has touched hardware yet.
- Open the upstream PR after the hardware pass (apollo/UPSTREAM_PR.md).
- Set up hosting for the 16.0.1 manifest + M-1_full_install.bin (GitHub Pages on the
  fork or install site storage), then flip the installer URLs per
  docs/m1-wled-migration.md.
- Copy that will become wrong and needs an edit pass when 16.0.1 ships:
  - wiki.apolloautomation.com/products/m1/introduction/ says "Pre-flashed with WLED"
    (fine) but also "use the Pixel Magic tool"; needs the Pixelforge rename.
  - wiki M-1 settings page: replace with apollo/WIKI_REWRITE.md.
  - wiki M-1 flashing guide and any page linking WLED-MM-M1 GitHub Pages.
  - Shopify M-1 product listing: check for WLED-MM, WLED_MM, Pixel Magic mentions.
  - PixelMagicTool repo README if Pixelforge replaces it.
  - Any support macros or printed inserts referencing the settings wiki page.
- OTA password remains WLED's default (wledota), same as the MM build. Decide if a
  per-unit or Apollo-specific OTA password should ship (my_config mechanism exists
  for bench builds; a fleet decision is a product call).
- The MM build had the brownout detector disabled; the 16.0.1 build does not. If
  soak tests brown out on USB-C, revisit (QA item 11).
- WLED-MM-M1 repo: leave as archive (rollback path documented in ROLLBACK.md).

## Repo safety (your original concern)
The local WLED clone now has origin = ApolloAutomation/wled and upstream =
Aircoookie/WLED with its push URL set to an invalid string, so pushing to the real
WLED repository fails by construction. Nothing was pushed anywhere during this
session except as noted in PROGRESS.md.
