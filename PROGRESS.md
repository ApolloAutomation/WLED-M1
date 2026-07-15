# Apollo M-1 migration - PROGRESS

Last update: 2026-07-15, after the AP-mode first-run session (D20-D23,
BENCH_SESSION_AP.md) and its post-gate fixes. Read SUMMARY.md first. This
file is the resume ledger for a fresh session. Bench narratives:
BENCH_SESSION_D10.md (chains), BENCH_SESSION_AP.md (AP mode + first-run).

## AP session outcome (2026-07-14/15) - see BENCH_SESSION_AP.md for detail
- D20: AP mode is a first-class operating mode (binding, Justin). Permanent
  AP walkthrough gate added to QA_CHECKLIST.md.
- Fixed on hardware, all verified over the hotspot: offline Pixel Paint
  (CDN->on-device libs), AP radio power (txpwr 78) + modem sleep (initAP,
  +1 line), Scrolling Text force-scroll (check3, 2 lines) with right-to-left
  direction, presets normalized (Sound Bars ONE-bar defect -> 16 bands,
  glass-verified), frozen-segment thaw on effect change (json.cpp, the
  pixel-paint black-screen trap), D22 connectivity-probe answers (works
  with mobile data ON), D23 first-boot signpost tour (dog / STEP 1 join
  hotspot / STEP 2 scan next QR code / inverted QR / NO CAMERA? fallback),
  10 tour iterations approved on glass.
- Client-side causes proven (not device bugs): Android cellular routing
  around no-internet APs, captive mini-browser limitations, WLED Android
  app file-chooser MIME bug (source-level proof, apollo/WLED_APP_BUG.md).
- Firmware code surface vs v16.0.1 now ~180/-16 lines across 12 files
  (was 168/-14); upstream findings ledger at 12 items
  (apollo/UPSTREAM_FINDINGS.md); three PR-ready patches (AP sleep,
  force-scroll, freeze-thaw) prepared, unopened.
- Test unit (6d0a40) left factory-fresh with the final tour running.
- Bench tooling preserved: apollo/bench/ (serial logger with clean-reset
  attach, AP probe template).

## Canonical locations
- THIS repo: /Users/justinapollo/Code/ApolloAutomation/WLED-M1 = clone of
  ApolloAutomation/WLED-M1 (public GitHub fork of wled/WLED). Branch m1-wled-update
  = all work, PUSHED through 32cda73d. Branch hub75-first-boot-defaults = prepared
  upstream PR, single commit, PUSHED. Never push to main. Never force push.
- Old clone /Users/justinapollo/Code/ApolloAutomation/WLED: retired source of the
  recovered work (branches apollo/m1, hub75-first-boot-defaults; its linked
  worktree ../WLED-upstream-pr belongs to it). Read-only; upstream push disabled in
  its git config. Safe to archive once pushed branches are confirmed.
- /Users/justinapollo/Code/ApolloAutomation/WLED-MM-M1: shipping WLED-MM repo,
  untouched, rollback archive in docs/ (ROLLBACK.md). Also served as the oracle
  for the D10 fps investigation (see BENCH_SESSION_D10.md "60fps answer").
- /Users/justinapollo/Code/ApolloAutomation/installer: branch feat/m1-wled-entry
  PUSHED; apply apollo/installer-fixup.patch from this repo before merging.

## Build recipe (works on this Mac)
    cd /Users/justinapollo/Code/ApolloAutomation/WLED-M1
    export npm_config_cache=<any writable dir>   # sandbox blocks ~/.npm; pio runs npm ci itself
    pio run -e apollo_m1
    ./apollo/build_artifacts.sh --skip-pio       # M-1_full_install.bin + M-1_ota.bin in apollo/out/
Check full build logs for redefinition warnings; exit codes hide them (see
DECISIONS D13 for the DEFAULT_LED_COUNT lesson). Do NOT re-add speed/-O2
flags without re-running the virgin-boot gate (see 2d00934f: -O2 boot-looped
a factory-fresh unit while every OTA boot worked).

## State by phase (session-3 TASK.md numbering)
- [x] Phase A HARD GATE: 9 commits recovered from the old clone, proven,
      consolidated onto m1-wled-update (DECISIONS D11), M1_FACTS.md committed,
      branches + installer branch pushed, fork confirmed public.
- [x] AUDIT: env rewritten to inherit (DECISIONS D12); DEFAULT_LED_COUNT trap
      fixed (D13). Post-D10 firmware-code surface vs v16.0.1: 10 files,
      +168/-14 (SUMMARY has the honest table).
- [x] Justin's decisions: D1 superseded by D16 (open AP), D2 confirmed,
      D3 closed by D15 (AR on), D4 applied, D5 one PR stands,
      D14 superseded by D19 (animated dog first boot), D16-D19 applied.
- [x] Fact verification: FACT_CHALLENGES.md. F1/F3 confirmed, F2 prose
      corrected, F4 disproven -> ABL patch cancelled.
- [x] Phase B wiki triage: WIKI_TRIAGE.md. Rewrites in apollo/wiki-rewrites/:
      matrix-settings, microphone-addon, panel-faults, and (new, D10 sessions)
      multiple-panels with the verified 1x4 + 2x2 recipes and size limits.
- [x] Phase C: clean builds throughout; artifacts final at 32cda73d
      (1,250,528 B app / 39% of OTA slot; full install 16 MB with animated
      dog + presets embedded, byte-verified).
- [x] Phase D hardware, first live session (2026-07-12): D0/D1/D2/D3/D4 PASS,
      D9 rev6-half PASS, both OTA cycles clean, D14/D15 decided live.
- [x] Phase D hardware, D10 bench sessions (2026-07-12/13, full narrative in
      BENCH_SESSION_D10.md):
      * D10 4-panel chain PASS on glass: 1x4 (256x64) and 2x2 (128x128),
        scrolling text/effects/GIFs across seams. Recipe: one canvas-sized
        2D panel (panel-major ledmap mismatch found and documented).
      * Six firmware fixes shipped: MAX_LEDS >= boundary, cfg div-by-zero
        boot loop, 2D width cap 256, ledmap PSRAM fallback, HUB75 shadow
        buffer PSRAM (heap watchdog fix), getLastActiveSegmentId underflow
        panic. Plus MAX_LED_MEMORY 192K->256K, Panel dims uint16, GIF PSRAM
        file cache + direct-XY draw.
      * D8 WiFi under load PASS at 256x64 (0% loss, 9.7 ms avg).
      * fps envelope documented: text 31 / DNA 17 / sparse GIF 18 /
        full-frame GIF 8 at 16384 px; 43 fps single panel. MM-60fps question
        answered (write-through pipeline vs 16.x compositor; -O2 and 4-bit
        depth both tested and rejected with measurements).
      * CONTAMINATION CHECK PASS (2026-07-13) on the shipping artifact -
        after catching a real blocker: -O2 crash-looped the virgin boot
        (fixed by dropping the flags, 2d00934f). Virgin boot verified:
        animated dog first impression (D19), customer AP flow, exact
        single-panel defaults, all 4 factory presets, no chain residue.
- [x] Phase E wrap-up: all ledger docs current; NEW: BENCH_SESSION_D10.md
      (bench narrative + traps), apollo/UPSTREAM_FINDINGS.md (8 WLED items +
      3 HUB75-lib observations), apollo/wiki-rewrites/multiple-panels.md.

## Remaining work, in order
1. Business tail (Justin): publish wiki rewrites (multiple-panels is new),
   pick the tester-bundle number (artifacts are well past b6), hosting +
   installer URL flip (apollo/installer-fixup.patch first), open the upstream
   PR (apollo/UPSTREAM_PR.md), file the upstream findings
   (apollo/UPSTREAM_FINDINGS.md).
2. Remaining hardware QA (parts/instruments): D3 FS-reset button resilience,
   D5 current draw, D6 ghosting, D7 driver chip id, D9 rev4 no-mic half,
   D11 HA discovery click-through, D12 dump-restore drill (QA_CHECKLIST.md).
3. Demo/test units: Justin's demo unit currently runs the shipping factory
   image + his WiFi (post-contamination-check). Restore-from-dump option
   still available (ROLLBACK.md; doubles as D12).
4. Future engineering (post-launch, evidence in UPSTREAM_FINDINGS.md +
   BENCH_SESSION_D10.md): GIF/effects fps parity with MM = 16.x compositor
   fast path or softhack007 HUB75 lib swap; -O2 virgin-boot crash root cause
   (dynarray post-link script suspicion).

## Bundle b7 (2026-07-15, commit c10ac303): first named bundle since b6; carries all D10 + AP session fixes, the first-boot tour, and the freeze-thaw fix. Distributed to Justin with sha256 sums.

## Post-b7 session (2026-07-15 afternoon, BENCH_SESSION_POSTB7.md)
Tester feedback drove a first-boot redesign: ONE static setup card (FS-only,
preset 9 swap, zero firmware delta). QR scannability investigated on glass
across 3 rounds + web research: inverted 2px + on-panel quiet zone + bri 220
is the best possible on bare P2.5 and still intermittent in lit rooms (dot
fill factor is the physical limit; research's standard-polarity prediction
refuted on glass, brightness prediction confirmed). OPEN: ship card with
best-effort QR vs text-only (D24 pending, recommendation text-only or
de-emphasized QR). Business tail: three upstream PR texts verified and
finalized (apollo/UPSTREAM_PRS_READY.md), GitHub release drafted
(apollo/RELEASE_DRAFT.md, publish approved once b8 gates pass, hosting =
dual-publish because release assets still have no CORS), installer fixup
applied and pushed. Old-Android captive popup explained (vendor probe
paths hit the 302 catch-all; OnePlus 9-ish on b7 confirms; no action).
Test unit 2f5e50 runs b7 + QR-test presets; demo unit has a USB
power/cable mystery pending. b8 waits on the D24 card decision, then the
single virgin + AP walkthrough gate (Justin approved gating once on b8).
