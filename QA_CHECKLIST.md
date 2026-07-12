# M-1 hardware QA checklist (WLED 16.0.1 migration, TASK.md Phase D order)

Status: NOT RUN. No hardware was available in any session so far (M1_ALLOW_FLASH
unset, no unit on serial, no live unit on the network). Everything below is for
Trevor or a hardware-enabled session. Results go inline under each item; replace
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
- [ ] Dump is exactly 16,777,216 bytes. PENDING
- [ ] JSON captures committed; dump stored outside git, path noted here. PENDING

## D1. Diff live capture against the reconstructed baseline
- [ ] Compare baseline/live/cfg.json to baseline/README.md expectations (MM defaults:
      type 101 or wiki-configured 103, maxpwr 1500 or 0, SERVERNAME Apollo M-1,
      open AP, release "mdev_release" per DECISIONS D10). Every mismatch is an
      assumption we got wrong; list them ALL here before flashing anything. PENDING

## D2. OTA path FIRST (highest risk, touches existing customers)
With the unit still on WLED-MM and its real cfg.json intact:
- [ ] Upload M-1_ota.bin via the WLED update page. PENDING
- [ ] Panel still lights at 64x64 (not dark, not a 32x32 quadrant). PENDING
- [ ] /json/cfg shows the migration shim result: bus type 65, pin [64,64,c,1,c]
      (from old type 103; a unit that was still on the never-configured type-101
      32x32 default will correctly come up 32x32; that case is full-install
      territory, record which case this unit was). PENDING
- [ ] cfg.json got re-saved in 16.x format (vid updated). PENDING
- [ ] Settings, mDNS name, WiFi survived. Note: AP config also survives, so an
      MM-upgraded unit keeps its open AP (DECISIONS A3); maxpwr carries over
      likewise (ABL cannot affect the HUB75 bus either way, FACT_CHALLENGES
      FACT 4, but the UI checkbox may read on if the old config had 1500). PENDING
- [ ] If it fails: restore the D0 dump (esptool write_flash 0 m1_factory_16mb.bin),
      fix, repeat. Do not proceed until this passes. PENDING

## D3. Full-install path
- [ ] esptool erase_flash, write M-1_full_install.bin at 0x0, power on with a 64x64
      panel, ZERO configuration. PENDING
- [ ] Verify every Apollo delta item via /json/cfg and /json/info:
      type 65, pin [64,64,1,1,1], len 4096, chain READS as 1 in LED Preferences,
      2D matrix mpc 1 panel 64x64, maxpwr 0 (limiter unchecked in UI),
      name Apollo M-1, mDNS apollo-led-matrix-xxxxxx, AP Apollo M-1-xxxxxx with
      password wled1234, AudioReactive Generic I2S SD 10 WS 12 SCK 11 sync Off
      and disabled, ver 16.0.1, release Apollo_M-1, product Apollo M-1. PENDING
- [ ] Filesystem-erase resilience: button hold 10 s (FS format), reboot; all values
      above must return via the compile-time defaults path (this exercises the
      cfg.cpp patches instead of the shipped cfg.json). PENDING

## D4. The real acceptance test: visible light
- [ ] Factory unit, powered on, unconfigured: VISIBLE LIGHT across the full 64x64
      panel within a few seconds (factory default is Solid warm orange at
      brightness 128, DECISIONS D14). Photograph it. If the panel is dark, that is
      a release blocker regardless of what /json/cfg says. PENDING

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

## D9. AudioReactive (also resolves Trevor's D3)
- [ ] Rev6 with mic addon: enable in Usermods (should be ONE toggle, no pin entry),
      reboot, audio effect responds to sound, sync Off. PENDING
- [ ] Rev4 / no mic, usermod force-enabled: measure CPU load, free heap, panel
      refresh, current draw versus disabled. No crash, display unaffected. Record
      numbers, then recommend the enabled-by-default answer for D3. PENDING

## D10. Four-panel chain at 256x64
- [ ] Chain 4 panels, set LED Preferences pins to [64,64,4,1,4] and 2D config to
      four panels in a row. Full 256x64 lights, effects span correctly, note the
      frame rate and any color banding (driver reduces bit depth at this size). PENDING

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
- [ ] A GIF renders via the image playback path (GIF decoder is confirmed present
      in the built binary; three wiki example pages depend on it). Compare colors
      against an MM unit; 16.x gamma differs. PENDING
- [ ] WizMote pairs using the stock build (ESP-NOW is compiled in upstream; the FAQ
      currently claims a special build is needed and should be corrected if this
      passes). PENDING
- [ ] Pixelforge (Pixel Magic successor) pushes a 64x64 image correctly. PENDING
- [ ] The installer still offers the ESPHome firmware path for the M-1 wherever it
      is published today; the WLED entry must not hide it. PENDING
