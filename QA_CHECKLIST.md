# M-1 hardware QA checklist (WLED 16.0.1 migration, TASK.md Phase D order)

Status: NOT RUN. No hardware was available in any session so far (M1_ALLOW_FLASH
unset, no unit on serial, no live unit on the network). Everything below is for
Justin or a hardware-enabled session. Results go inline under each item; replace
"PENDING" with what actually happened.

Artifacts: apollo/out/M-1_full_install.bin and M-1_ota.bin, rebuilt via
apollo/build_artifacts.sh. Expected identity: ver 16.0.1, release Apollo_M-1,
product Apollo M-1, name Apollo M-1.

RULES (from TASK.md, non-negotiable):
- ONE operator only. Never two agents or two terminals talking to one unit.
- The order below is mandatory. D0 before anything writes to the device. D2 (OTA)
  before D3 (full install), because D2 needs the unit still on its factory WLED-MM
  state and D3 destroys that state.
- The D0 flash dump is one-shot and irreplaceable. Nothing may erase or flash the
  unit until the dump is verified at exactly 16,777,216 bytes.
- Use the panel fault decoder (M1_FACTS.md appendix, or
  apollo/wiki-rewrites/troubleshooting-panel-faults.md) instead of guessing.

## D0. Capture the field unit BEFORE touching it (one-shot)
    mkdir -p baseline/live
    curl -s http://$M1_IP/json/info    > baseline/live/json_info.json
    curl -s http://$M1_IP/json/state   > baseline/live/json_state.json
    curl -s http://$M1_IP/json/cfg     > baseline/live/json_cfg.json
    curl -s http://$M1_IP/presets.json > baseline/live/presets.json
    curl -s http://$M1_IP/cfg.json     > baseline/live/cfg.json
    esptool.py --port <port> read_flash 0 0x1000000 baseline/live/m1_factory_16mb.bin
- [x] DONE 2026-07-12. Dump is exactly 16,777,216 bytes, taken as 16x1MB chunks over
      the S3 native USB-Serial/JTAG (/dev/cu.usbmodem1101; single 16MB reads abort
      with serial-stream corruption on this port, chunking works). Verified: image
      magic 0xE9 at 0x0, partition table at 0x8000, littlefs superblock at 0x610000,
      plus a 64KB spot re-read compared byte-identical. SHA-256
      84706b9df02f690b34d06060c7308b038a06d929967b1f2001ec9baf4c55b60d.
      Stored at baseline/live/m1_factory_16mb.bin (gitignored, NOT in git).
- [x] Captures committed: cfg.json (WiFi SSID value redacted for the public repo)
      and presets.json, both extracted FROM THE DUMP's littlefs (the unit was not
      reachable over HTTP; filesystem extraction replaces the curl captures and is
      strictly more authoritative). 37 customer GIFs also present, kept locally
      (baseline/live/gifs/, gitignored). wsec.json exists on the unit and was
      deliberately NOT extracted into git; the dump preserves it.
      HTTP captures (/json/info etc.) still to do once the unit is on the LAN.

## D1. Diff live capture against the reconstructed baseline
- [x] DONE 2026-07-12, from the dump's cfg.json. This unit is Justin's demo unit,
      not factory-fresh. Findings, none blocking:
      1. Bus: type 103 (MM Hub75 64x64) with pin [1] = chain 1, len 4096. Matches
         the wiki-configured state; the OTA shim's 103 -> 65 mapping is the exact
         case this unit exercises.
      2. SURPRISE: 2D matrix config says FOUR panels (256x64, mpc 4, mph 4) over a
         single-panel bus. Leftover from a chaining experiment; a real-world messy
         config. Post-OTA behavior on this mismatch must be observed and recorded,
         and judged against what the unit shows on MM today, not against perfection.
      3. mdns "wled-2f5f7c" (factory MAC default; the wiki rename was never done),
         name "Apollo M-1" (matches D4), ap.ssid "Apollo M-1".
      4. AudioReactive: enabled=true, Generic I2S, pins [10,12,11] - a mic-equipped
         unit, and the pins match the acceptance table exactly.
      5. maxpwr 1500 (ABL never unchecked on this unit; harmless for HUB75, FACT 4).
      6. Boot preset 23 of 32 presets (GIF-heavy, MM effect indices; post-OTA some
         presets will select different effects because 16.x renumbered - expected,
         reversible via dump restore).
      7. um config for Autosave/Animartrix/AutoPlaylist present; those usermods do
         not exist in the 16.0.1 build, their config blocks become inert.
      8. FALSE ALARM investigated and cleared: the FS superblock carries
         name_max=255 while every toolchain sdkconfig says 64. Resolution:
         esp_littlefs leaves lfs name_max at the littlefs default (255) for both
         format and mount regardless of CONFIG_LITTLEFS_OBJ_NAME_LEN; the unit
         itself (built with a 64-config toolchain) created and mounts this FS.
         Only the HOST mklittlefs tool refuses it. OTA mount is compatible; our
         mklittlefs-built factory image (superblock 64) is also compatible.

## D2. OTA path FIRST (highest risk, touches existing customers)
RESULT 2026-07-12: PASS on the real demo unit at 192.168.20.99.
- [x] Live pre-OTA HTTP baseline captured first (baseline/live/json_*.json).
      On-hardware confirmations of two source-derived predictions: /json/info
      reported release "mdev_release" (DECISIONS D10, the self-cancelled release
      name) and product "MoonModules"; the running MM firmware presented the
      fictional 4-panel 256x64 matrix (leds.count 16384) over the 1-panel bus.
- [x] M-1_ota.bin uploaded through the OLD firmware's /update endpoint ("Update
      successful!"). Unit back on WiFi within seconds of reboot.
- [x] Filesystem MOUNTED, nothing wiped: fs usage identical before/after
      (3960/10354 KB), WiFi + all settings + presets.json + 37 GIF files intact.
      The name_max false alarm (D1 item 8) is hereby hardware-proven safe.
- [x] Migration shim verified in /json/cfg: ins[0] became type 65,
      pin [64,64,1,1,1], len 4096; cfg re-saved in 16.x format (vid 2605010).
      /json/info: ver 16.0.1, release Apollo_M-1, repo ApolloAutomation/WLED-M1.
- [x] mDNS name kept (wled-2f5f7c - saved value survives, unique-prefix logic only
      applies to fresh units, as designed). AudioReactive survived enabled with
      pins [10,12,11], type Generic I2S.
- [x] EXPECTED CASUALTY, recorded: the pre-existing fictional 4-panel matrix was
      dropped by upstream's 2D bounds check (256x64 canvas > 4096-px bus) and the
      unit fell back to 1D. This config was already broken on MM; a correctly
      configured customer unit (1 panel 64x64 = 4096 px) passes the bounds check
      and keeps 2D. Fix applied via JSON API (matrix mpc 1, one 64x64 panel) +
      reboot; unit then reported 64x64 matrix, full-panel segment 0-64/0-64,
      46 fps, playlist cycling presets.
- [x] VISUAL (Justin): full 64x64 panel animating, content sensible. Preset
      effects may differ from MM (16.x renumbering) - accepted, dump restores.
- [x] maxpwr 1500 carried over from the old config as predicted (customer config
      preserved; ABL cannot affect the HUB75 bus, FACT_CHALLENGES FACT 4). The
      migrated BUS entry got maxpwr 0 from the shim path.

## D3. Full-install path
RESULT 2026-07-12: PASS.
- [x] erase_flash (7.9 s) + write_flash 0x0 M-1_full_install.bin (41.5 s, hash
      verified by esptool) over the S3 native USB port. Powered with the 64x64
      panel, zero configuration.
- [x] Acceptance table verified live over HTTP, 13 of 13 rows (capture committed
      as baseline/live/factory_boot_json_cfg.json / _info.json): type 65,
      pin [64,64,1,1,1], len 4096 (chain reads as 1), matrix 1x 64x64, maxpwr 0,
      name Apollo M-1, mdns apollo-led-matrix-2f5f7c (resolved over real mDNS),
      AP "Apollo M-1-2f5f7c" pskl 8 (wled1234, no longer open), AR Generic I2S
      pins [10,12,11] sync 0, ver 16.0.1, release Apollo_M-1.
- [x] mDNS/AP unique suffix matched the MAC-derived prediction (2f5f7c) exactly.
- [ ] Filesystem-erase resilience (10 s button hold; exercises the cfg.cpp
      compile-default path instead of the shipped cfg.json). STILL PENDING.

## D4. The real acceptance test: visible light
RESULT 2026-07-12: PASS.
- [x] Factory-fresh boot lit the FULL 64x64 panel within seconds, zero
      configuration (Justin confirmed visually; the shipping WLED-MM firmware
      would have shown a 32x32 quadrant here). Initially the warm orange default;
      Justin chose Apollo blue live and DECISIONS D14 was answered: the factory
      welcome color is now 0x4379AA, verified after OTA as boot segment color
      [67,121,170] with effect Solid at brightness 128.

## D-extra. Findings from the live session (2026-07-12)
- OTA CROSS-SUBNET GATE (support-relevant): upstream 16.x rejects /update from a
  different subnet by default (HTTP 401 "Client is not on local subnet",
  otaSameSubnet, cfg key ota."same-subnet"). WLED-MM had no such gate, which is
  why the MM-side OTA worked cross-subnet and the 16.0.1-side one required
  temporarily clearing the flag (restored to true afterward). Customers on
  split-band/VLAN networks (like this site: 5G and 2.4G are different subnets)
  will hit this when updating from a browser on another subnet. Add to the wiki
  troubleshooting page and FAQ.
- AudioReactive default flipped ON live (Justin's D3 decision, DECISIONS D15):
  -D UM_AUDIOREACTIVE_ENABLE now in the env, artifacts rebuilt. This unit also
  set enabled=true via API since its cfg predated the new default.
- Both live decisions (blue, AR on) rode an app-only OTA onto the factory unit
  with settings intact: second successful OTA cycle on 16.0.1 (first was
  MM -> 16.0.1; this one 16.0.1 -> 16.0.1).

## D5. Current draw, limiter off
- [ ] Full white, brightness 255, stock 3A USB-C supply: measure amps. No brownout,
      no flicker, no supply shutdown. Repeat on the WAGO 5V input. PENDING
- [ ] If it browns out: cap default brightness (briS) and log in DECISIONS; also
      revisit DECISIONS D14 brightness choice. Note the MM build disabled the
      brownout detector and this build does not; spurious brownout resets under
      load would show here. PENDING

## D6. Ghosting
- [ ] Full white at 255: look for ghosting/smearing. If present, add
      -D WLED_HUB75_MAX_BRIGHTNESS=239 (upstream-documented fix) and rebuild. PENDING

## D7. Driver chip
- [ ] If the panel is dark or colors look pastel with everything else correct:
      identify the panel's shift register IC (FM6124/ICN2038S/FM6126A/MBI5124/
      DP3246 options in bus_manager.cpp) and set it explicitly. Record the IC
      actually fitted to current production panels here. PENDING

## D8. WiFi under load
- [ ] Heavy effect running: test WiFi throughput and stability (S3_LCD_DIV_NUM=20
      is inherited as the mitigation). Record ping loss and UI responsiveness. PENDING

## D9. AudioReactive (also resolves Justin's D3)
- [x] REV6 HALF: PASS 2026-07-12. Mic-equipped unit, zero manual configuration
      (enabled by default per DECISIONS D15, pins baked): GEQ effect visibly
      reacts to live sound (Justin's clap test). Sync mode 0 (off) confirmed in
      /json/cfg. Better than the one-toggle goal: it is now a zero-toggle flow.
- [ ] Rev4 / no mic with the usermod force-enabled: measure CPU load, free heap,
      panel refresh, current draw versus disabled. No crash, display unaffected.
      Needs a rev4 board; still the open half of this item. PENDING

## D10. Four-panel chain at 256x64
- [x] PASS 2026-07-12/13 (live bench, Justin + assistant; full narrative in
      BENCH_SESSION_D10.md). Recipe that works: LED prefs pins [64,64,4,1,4]
      type 65 (HS), 2D config ONE 256x64 panel at 0,0 (REVISED session 2
      part 2: the four-64s layout produces a panel-major ledmap the HUB75
      bus renders scrambled - glass photos decoded it; Panel dims widened
      to uint16 to allow 256), save, reboot.
      Verified on glass: solid fills, DNA and organic 2D effects span all four
      panels continuously across seams. fps ~30 solid/text, ~15 heavy 2D.
      Six firmware bugs found and fixed to get here (MAX_LEDS >= boundary,
      cfg div-by-zero boot loop, 2D width cap 255->256, ledmap PSRAM fallback,
      HUB75 _ledBuffer DRAM starvation, getLastActiveSegmentId underflow crash)
      plus MAX_LED_MEMORY raised 192K->256K; see DECISIONS + BENCH file.
- [x] Scrolling Text regression root-caused and fixed same session: 48KB HUB75
      shadow buffer in DRAM left ~23K free heap; the wled.cpp low-heap watchdog
      (needs 15K contiguous) force-reset segments after 15/30/45s, freezing text
      mid-frame ("static shredded fragments") and dropping WiFi. After moving
      the buffer to PSRAM: 72K free / 64K contiguous, 160s multi-segment soak
      clean, text ran 2min+ with zero heap movement, fx stable at 122.
      GLASS PASS 2026-07-12 23:31 (Justin, photo + video): "APOLLO M-1 FOUR
      PANEL CHAIN" renders as one continuous readable line across all four
      panels, correct orientation (no mirror flag needed with this cabling:
      controller far right), seams invisible, scroll smooth. D10 definitive
      test CLOSED.
- [x] WiFi under load at 256x64 while Scrolling Text renders: 40/40 pings,
      0.0% loss, 9.7ms avg (idle baseline 6.0ms). PASS.
- [ ] 2x2 grid (Justin wants it): needs the virtual path; legacy
      ESP32-VirtualMatrixPanel-I2S-DMA.h confirmed as the compiled header.
      Plan: host-side simulation of getCoords first (desk-safe), then bench.
      Physical caveat: row-2 panels must be mounted 180 degrees rotated. PENDING
- [ ] Contamination check (Justin's Tier-1): factory-erase, flash rebuilt
      M-1_full_install.bin, verify single-panel 64x64 defaults untouched. PENDING

## D11. Home Assistant
- [ ] Native WLED integration discovers the fresh unit (zeroconf), entity name
      Apollo M-1, effect list populated (16.0.1 effect set), controls work, no
      integration errors in the Home Assistant log. PENDING
- [ ] A unit previously in Home Assistant under WLED-MM, after OTA: device entry
      survives (same MAC), entities keep working; note any entity id churn. PENDING

## D12. Rollback
- [ ] Restore baseline/live/m1_factory_16mb.bin with esptool write_flash 0, confirm
      the unit returns to its exact original shipping state (panel, settings,
      version strings match the D0 capture). PENDING

## Additional checks folded in from the wiki triage
- [x] PASS 2026-07-12 (Justin, from his PC against the b2+ firmware): GIFs upload
      and play via the built-in /pxmagic.htm on the device. Pre-fix builds (b1)
      404 these pages. CORRECTED SAME DAY: the working tool is PixelForge
      (/pixelforge.htm), BUILT INTO upstream 16.0.1 and self-contained; the
      phone greying was the WLED Android app's file-chooser bug all along
      (proof: same page works in Firefox on the same Samsung Fold7; bug report
      drafted in apollo/WLED_APP_BUG.md, workaround = phone browser). Per
      Justin, the legacy pxmagic/pixart pages are old and outdated and are NOT
      shipped (removed again in b5); PixelForge + the pre-installed Pixel Paint
      module are the supported image/paint path. Wiki editor: point GIF and
      example pages at http://<device>/pixelforge.htm. Side-by-side gamma
      comparison against an MM unit still worthwhile.
- [ ] WizMote pairs using the stock build (ESP-NOW is compiled in upstream; the FAQ
      currently claims a special build is needed and should be corrected if this
      passes). PENDING
- [x] Covered by the item above: PixelForge pushes images and GIFs correctly
      on 16.0.1 (PC browser and Android Firefox verified).
- [ ] The installer still offers the ESPHome firmware path for the M-1 wherever it
      is published today; the WLED entry must not hide it. PENDING
