# Apollo M-1 migration - PROGRESS

Last update: 2026-07-12, session 3 complete (all phases except hardware).
Read SUMMARY.md first. This file is the resume ledger for a fresh session.

## Canonical locations
- THIS repo: /Users/justinapollo/Code/ApolloAutomation/WLED-M1 = clone of
  ApolloAutomation/WLED-M1 (public GitHub fork of wled/WLED). Branch m1-wled-update
  = all work, PUSHED. Branch hub75-first-boot-defaults = prepared upstream PR,
  single commit, PUSHED. Never push to main. Never force push.
- Old clone /Users/justinapollo/Code/ApolloAutomation/WLED: retired source of the
  recovered work (branches apollo/m1, hub75-first-boot-defaults; its linked
  worktree ../WLED-upstream-pr belongs to it). Read-only; upstream push disabled in
  its git config. Safe to archive once pushed branches are confirmed.
- /Users/justinapollo/Code/ApolloAutomation/WLED-MM-M1: shipping WLED-MM repo,
  untouched, rollback archive in docs/ (ROLLBACK.md).
- /Users/justinapollo/Code/ApolloAutomation/installer: branch feat/m1-wled-entry
  PUSHED; apply apollo/installer-fixup.patch from this repo before merging.

## Build recipe (works on this Mac)
    cd /Users/justinapollo/Code/ApolloAutomation/WLED-M1
    export npm_config_cache=<any writable dir>   # sandbox blocks ~/.npm; pio runs npm ci itself
    pio run -e apollo_m1
    ./apollo/build_artifacts.sh --skip-pio       # M-1_full_install.bin + M-1_ota.bin in apollo/out/
Check full build logs for redefinition warnings; exit codes hide them (see
DECISIONS D13 for the DEFAULT_LED_COUNT lesson).

## State by phase (session-3 TASK.md numbering)
- [x] Phase A HARD GATE: 9 commits recovered from the old clone, proven (count 9
      against v16.0.1, diffstat +1163/-2, subjects printed), consolidated onto
      m1-wled-update via pointer move (DECISIONS D11), M1_FACTS.md committed,
      both branches + installer branch pushed, fork confirmed public.
- [x] AUDIT: env rewritten to inherit (DECISIONS D12); code delta 212 -> 209
      lines while absorbing D1/D4; docs grew per TASK.md deliverables (SUMMARY
      has the honest table). DEFAULT_LED_COUNT trap fixed (D13).
- [x] Trevor's decisions: D1 wled1234 APPLIED, D2 confirmed, D3 OPEN (QA D9),
      D4 Apollo M-1 APPLIED, D5 one PR stands / ABL PR cancelled.
- [x] Fact verification: FACT_CHALLENGES.md written. F1 confirmed, F2 prose
      corrected, F3 confirmed (unflag pattern validated against PIO source),
      F4 upstream half disproven -> no ABL patch needed anywhere.
- [x] Phase B wiki triage: WIKI_TRIAGE.md (13 pages; matrix-settings 11/13 fixed
      as default). Rewrites in apollo/wiki-rewrites/ (matrix-settings,
      microphone-addon, new panel-faults page with the fault decoder).
- [x] Phase C: clean build in THIS clone, SUCCESS, 1,250,144 B / 39.7 percent of
      OTA slot, zero warnings. Acceptance verified from inside the artifact
      (unpacked LittleFS cfg.json + binary strings + GIF decoder present).
      v16.1 tag still does not exist upstream (rechecked 2026-07-12).
- [~] Phase D hardware (live session 2026-07-12, Trevor authorizing and observing):
      D0/D1/D2/D3/D4 PASS, D9 rev6-half PASS. 13/13 acceptance rows verified over
      HTTP on a factory-fresh boot; both OTA cycles clean; Apollo blue (D14) and
      AR-on (D15) decided live and shipped. Remaining: D3 FS-reset resilience,
      D5-D8, D9 rev4 half, D10-D12 (parts/instruments). See QA_CHECKLIST.md.
- [x] Phase E wrap-up: this file, SUMMARY.md, QA_CHECKLIST.md, WIKI_TRIAGE.md,
      FACT_CHALLENGES.md, wiki rewrites, installer patch, UPSTREAM_PR.md.

## Next session, in order
1. Hardware QA per QA_CHECKLIST.md (single operator, D0 first, order mandatory).
2. Resolve Trevor's D3 (AudioReactive default) from the D9 measurements.
3. Open the upstream PR after D2-D4 pass.
4. Hosting + installer URL flip + wiki updates per SUMMARY "For Trevor".
