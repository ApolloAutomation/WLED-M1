# Apollo M-1 migration to upstream WLED - PROGRESS

Last update: 2026-07-11 (session 1, complete through Phase 7 minus hardware).
Read SUMMARY.md first; this file is the resume-state ledger.

## Resume instructions for a fresh session
Working repos:
- /Users/justinapollo/Code/ApolloAutomation/WLED = the migration repo.
  Remotes: origin = https://github.com/ApolloAutomation/wled.git,
  upstream = Aircoookie/WLED with push URL DISABLED (never push upstream).
  Branch apollo/m1 (based at tag v16.0.1) carries everything: code patches, env,
  apollo/ tooling, all deliverable docs.
- /Users/justinapollo/Code/ApolloAutomation/WLED-upstream-pr = worktree, branch
  hub75-first-boot-defaults (single commit off upstream/main) = prepared upstream PR.
- /Users/justinapollo/Code/ApolloAutomation/installer = branch feat/m1-wled-entry
  (M-1 devices.json entry + migration doc). NOT deployed.
- /Users/justinapollo/Code/ApolloAutomation/WLED-MM-M1 = retired shipping repo,
  untouched, rollback archive in docs/ (see ROLLBACK.md).

Build: cd WLED && npm_config_cache=<any writable dir> pio run -e apollo_m1
(npm cache env var needed because pio-scripts/build_ui.py runs npm ci on every build;
a sandboxed or permission-blocked ~/.npm otherwise wipes node_modules and fails).
Artifacts: ./apollo/build_artifacts.sh (outputs in apollo/out/, gitignored).

## Phase status
- [x] Phase 0 ground truth: no live device found (BLOCKED.md B1); baseline
      reconstructed from source into baseline/; MIGRATION_INVENTORY.md complete.
- [x] Phase 1: pinout already upstream (MOONHUB_S3_PINOUT, identical GPIOs);
      collision check PASS (DECISIONS D4/D5). No APOLLO_M1_PINOUT needed.
- [x] Phase 2: [env:apollo_m1] in platformio.ini. Builds SUCCESS: RAM 13.8 percent,
      flash 1,250,064 B = 39.7 percent of the 3 MB OTA slot.
- [x] Phase 3A: cfg.cpp first-boot HUB75 fix + DEFAULT_PANEL_WIDTH/HEIGHT seeding.
- [x] Phase 3B: apollo/fs cfg.json + presets.json baked into the full-install image.
- [x] Phase 3 extra: WLED_MM_HUB75_MIGRATION shim for OTA upgrades from WLED-MM.
- [x] Phase 4: nothing to migrate (no shipped presets exist; verified).
- [x] Phase 5: M-1_full_install.bin + M-1_ota.bin build; partition table identical
      to factory; installer draft branch ready; manifest in apollo/installer/.
- [x] Phase 6 (software half): build + artifact verification done. Hardware half
      BLOCKED (M1_ALLOW_FLASH unset, no device) -> QA_CHECKLIST.md written.
- [x] Phase 7: SUMMARY.md, DECISIONS.md, BLOCKED.md, QA_CHECKLIST.md, ROLLBACK.md,
      apollo/WIKI_REWRITE.md, apollo/UPSTREAM_PR.md, license check done.

## Commits on apollo/m1 (oldest first, on top of 29b389df = v16.0.1)
1. 5d4327d4 Phase 0 baseline + decision/blocked logs
2. 700d06e3 inventory + pinout verdict + collision check
3. 0aa087cc cfg.cpp HUB75 first-boot fix + 2D seed  <- cherry-picked into PR branch
4. 723d8bda WLED_MDNS_PREFIX + AP SSID unique prefix fix
5. f00460d2 apollo_m1 env + my_config.h.example
6. e90f094f apollo/ factory FS + artifact tooling
7. 8a0fc48c WLED-MM migration shim + QA/rollback/wiki/PR docs
(plus this PROGRESS/SUMMARY update commit)

## Next session, in order
1. Hardware: set M1_ALLOW_FLASH=1 with a unit on serial; run QA_CHECKLIST.md.
2. Fix whatever QA finds; the likely candidates are listed inside the checklist
   (OTA-from-MM config carryover, brownout on USB-C, gamma shift).
3. After the hardware pass: open the upstream PR (apollo/UPSTREAM_PR.md).
4. Hosting for manifest + full-install binary; flip installer URLs
   (installer/docs/m1-wled-migration.md).
