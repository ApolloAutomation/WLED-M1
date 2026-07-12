# Apollo M-1 migration to upstream WLED - PROGRESS

Last update: 2026-07-11 (session 1)

## Resume instructions for a fresh session
Working repos:
- /Users/justinapollo/Code/ApolloAutomation/WLED = upstream WLED clone.
  Remotes: origin = https://github.com/ApolloAutomation/wled.git (push target),
  upstream = Aircoookie/WLED with push URL DISABLED (safety: never push upstream).
  Branch apollo/m1 created at tag v16.0.1 (commit 29b389df). All migration work lands here.
- /Users/justinapollo/Code/ApolloAutomation/WLED-MM-M1 = shipping WLED-MM fork (branch mdev).
  READ ONLY reference. Apollo delta over netmindz/WLED-MM merge-base 315f147d is:
  platformio_override.ini (the whole firmware config), docs/ (shipped binaries + ESP Web
  Tools manifests = rollback archive), CI workflow removal.
- /Users/justinapollo/Code/ApolloAutomation/WLED-MM = plain netmindz/WLED-MM clone (reference).

## Environment facts
- gh CLI not installed. pio and esptool.py available.
- M1_IP unset, M1_ALLOW_FLASH unset -> no hardware flashing this session.
- No live M-1 found yet: HA WLED integration points at 192.168.20.30 (state setup_retry,
  unreachable, device is "The Belle Permanent Lights", not an M-1). mDNS browse for
  _wled._tcp found nothing. Subnet sweep of 192.168.1.0/24 was run (see baseline/).
- Upstream has NO v16.1 tag as of 2026-07-11. Latest release tag is v16.0.1 -> pinned there.
  (Task text said "16.1"; logged in DECISIONS.md.)

## Ground truth from platformio_override.ini (shipping MM build)
- env esp32S3_16MB_PSRAM_M_HUB75 extends esp32S3_8MB_PSRAM_M
- board lilygo-t7-s3, memory_type qio_opi (16MB QIO flash + OPI PSRAM, N16R8), flash_mode qio
- DEFAULT_LED_TYPE=101 (MM HUB75 bus type), MOONHUB_S3_PINOUT
- I2S mic: SR_DMTYPE=1, I2S_SDPIN=10, I2S_CKPIN=11, I2S_WSPIN=12, MCLK_PIN=-1
- LEDPIN=14 BTNPIN=0 RLYPIN=15 IRPIN=-1 AUDIOPIN=-1
- WLED_AP_SSID "Apollo M-1", WLED_AP_PASS "" (OPEN AP)
- SERVERNAME "Apollo M-1", WLED_RELEASE_NAME Apollo_M-1
- partitions: esp32.extreme_partitions, 16MB flash
- ARDUINO_USB_MODE=1, CDC_ON_BOOT=0 (external Serial-to-USB chip)

## Phase status
- [x] Repo safety: upstream push disabled, origin -> ApolloAutomation/wled
- [~] Phase 0 IN PROGRESS: inventory workflow launched (MM pinout, partitions, effective
      flags, upstream recon, MM defaults). Baseline from live device NOT possible (no
      device reachable); reconstructing from source + shipped manifests instead.
- [ ] Phase 1 pinout block
- [ ] Phase 2 apollo_m1 env
- [ ] Phase 3 defaults fix (A compile-time, B FS image)
- [ ] Phase 4 presets (likely trivial: no shipped presets found so far, TBC)
- [ ] Phase 5 artifacts
- [ ] Phase 6 verify (build only, no flash)
- [ ] Phase 7 deliverables

## Notes
- ApolloAutomation/wled fork on GitHub has ONLY branch main (c7d41a8e). The user's
  "add m1 to wled" branch was not pushed there. Work proceeds on local apollo/m1.
- User's earlier experiment lives untracked in WLED clone as platform_override.ini
  (misnamed, PlatformIO ignores it). Left in place as reference.
- Shipped versions: docs/manifest.json 25.7.14.1 (merged), 14.5.1 build 25.8.19.1,
  Rev6_14.5.1 build 25.10.9.1 (latest shipping).
