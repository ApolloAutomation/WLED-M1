# M-1 hardware QA checklist (WLED 16.0.1 migration)

Hardware was not available this session (M1_ALLOW_FLASH unset), so none of this has
run yet. Every item below must pass on real hardware before release. Artifacts:
apollo/out/M-1_full_install.bin and apollo/out/M-1_ota.bin (rebuild with
apollo/build_artifacts.sh).

## 1. Factory-fresh first boot (the headline test)
- esptool --chip esp32s3 erase_flash, then write M-1_full_install.bin at 0x0.
- Power on with a 64x64 panel attached. NO configuration of any kind.
- The FULL 64x64 panel lights (Solid orange, brightness 128). Not a 32x32 quadrant,
  not garbage rows, correct orientation.
- Join the AP (see item 2), open http://4.3.2.1, then check via the AP or after WiFi
  setup:
  - /json/info: name "Apollo LED Matrix", ver 16.0.1, release Apollo_M-1,
    product Apollo M-1, brand WLED
  - /json/cfg: hw.led.ins[0].type = 65, pin = [64,64,1,1,1], len 4096
  - /json/cfg: hw.led.matrix.mpc = 1, panels[0] w=64 h=64
  - /json/cfg: hw.led.maxpwr = 0 (ABL off; also check the LED settings page shows the
    limiter unchecked)
  - AudioReactive usermod settings page: type Generic I2S, SD 10, WS 12, SCK 11,
    sync mode Off, enabled unchecked
- Diff /json/cfg against baseline/ expectations (baseline/README.md) and explain any
  difference.
- Reboot twice; settings persist; panel still correct.

## 2. Identity and collisions
- AP SSID is "Apollo M-1-xxxxxx" (last 6 MAC hex chars), OPEN (no password).
- mDNS hostname is apollo-led-matrix-xxxxxx.local and resolves.
- Two M-1 units on the same network at once: no mDNS collision, both reachable.

## 3. Filesystem-erase resilience (compile-time defaults path)
- On a flashed unit: erase ONLY the filesystem region (0x610000, size 0x9E0000) or
  hold the boot button 10 s (factory reset formats the FS), then reboot.
- Unit must come back as a 64x64 matrix with all acceptance values (this exercises
  the cfg.cpp first-boot patch instead of the shipped cfg.json).

## 4. Power
- Full-white Solid at brightness 255 on USB-C 3A: no brownout, no visible dimming
  collapse, supply stays within its rating. Record actual current draw.
- Same check on WAGO 5V input.
- Because ABL is off, confirm the recommended supply guidance in the wiki matches
  reality on a full 64x64 white screen.

## 5. AudioReactive
- Rev6 with microphone addon: enable AudioReactive in Usermod settings (no pin entry
  should be needed), reboot, run an audio-reactive effect, confirm response to sound.
- Rev4 (no microphone): usermod stays disabled by default; enabling it anyway must
  not crash or corrupt the display (effects fall back to silence/noise); disabling it
  again restores normal operation.

## 6. Panel chaining
- 4 panels chained: LED settings, set pins to [64,64,4,1,4] (panelW, panelH, chain,
  grid rows 1, grid cols 4) and 2D matrix to 4 panels 256x64 wide.
- Full 256x64 lights correctly, effects run across the whole span, frame rate usable
  and WiFi stays responsive.
- Color depth note: at 256x64 the driver reduces bit depth; check for visible banding
  and record it.

## 7. OTA from WLED-MM (field upgrade path)
- On a unit running WLED-MM 14.5.1 WITH customer-like config (custom name, WiFi,
  a preset, 64x64 configured per the old wiki page):
  - Config, Security and Updates, Manual OTA, upload M-1_ota.bin.
  - Unit reboots into 16.0.1; WiFi credentials, name, presets survive; display still
    64x64 and correct.
  - The build includes WLED_MM_HUB75_MIGRATION: the WLED-MM cfg.json HUB75 bus entry
    (type 101/103, chain in pin[0]) must be rewritten on first boot to type 65 with
    slots [w,h,chain,1,chain], and cfg.json re-saved in 16.x format. Verify
    /json/cfg after the OTA shows type 65 and the panel is correct. A unit that was
    still on the OLD 32x32 default (type 101, never configured) will come up as
    32x32 after OTA because that genuinely was its stored config; that case needs the
    full install (or one settings save), not the OTA.
  - Note: hw.led.maxpwr carries over from the old config. A unit where the wiki step
    "uncheck ABL" was never done will still have ABL at 1500 mA after OTA; that is
    intentional (customer config preserved), but record it.
- OTA back from 16.0.1 to the archived WLED-MM binary (rollback path, see
  ROLLBACK.md): unit boots and works.

## 8. Home Assistant
- Fresh 16.0.1 unit joins WiFi; HA discovers it via the native WLED integration
  (zeroconf _wled._tcp) with the name Apollo LED Matrix.
- Entities: light entity present, effect list populated with the 16.0.1 effect set,
  brightness/color/effect control works.
- A unit that was previously in HA under WLED-MM and got OTA-updated keeps its device
  entry (same MAC) and entities keep working; note any entity-id churn.

## 9. Image tooling (Pixelforge, replacing Pixel Magic)
- Push a 64x64 image from the Pixelforge workflow to the device and confirm it
  renders correctly on 16.0.1.
- Note: WLED 16.x changed color handling and gamma versus WLED-MM 14.5.x. Compare a
  known image side by side on an MM unit and a 16.0.1 unit; colors may shift. Record
  whether Pixelforge output needs a gamma adjustment.

## 10. Visual regression
- Run a representative set of effects (Solid, a palette effect, a 2D effect, an
  audio effect on rev6) side by side against a WLED-MM unit. The 16.x gamma change
  means colors will not match exactly; flag anything that looks wrong rather than
  merely different.

## 11. Long soak
- 24 h on a looping playlist at brightness 128: no reboot (check /json/info uptime),
  no heap exhaustion (json/info freeheap stable), panel artifact-free. Note: the
  16.0.1 build does not disable the brownout detector (the MM build did); if soak
  shows spurious brownout resets on USB-C power, revisit DECISIONS and consider
  WLED brownout mitigation before release.
