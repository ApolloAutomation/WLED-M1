# Baseline (Phase 0 ground truth)

Captured 2026-07-11.

## Live device capture: NOT POSSIBLE (see BLOCKED.md)
No live M-1 running WLED-MM was reachable:
- mDNS browse for _wled._tcp: no responders
- http probes: apollo-led-matrix.local, wled-apollo.local: no response
- Home Assistant WLED integration: one entry, host 192.168.20.30, state setup_retry
  ("Error occurred while communicating with WLED device"). Its entities are named
  "The Belle Permanent Lights", i.e. not an M-1 matrix. See ha-wled-integration.json.
- Full sweep of local subnet 192.168.1.0/24 port 80 /json/info: only a Pi-hole answered
  (network-scan-192.168.1.0-24.txt).

Therefore the baseline is reconstructed from the authoritative sources that produce a
factory-fresh device state:
1. platformio_override_wledmm.ini - the complete shipping build config (the entire
   Apollo delta over netmindz/WLED-MM lives in this one file).
2. shipped-manifests/ - ESP Web Tools manifests for the three shipped builds:
   - root merged-firmware.bin, version 25.7.14.1
   - 14.5.1 (rev4), version 25.8.19.1
   - Rev6_14.5.1, version 25.10.9.1 (latest shipping)
   Shipped binaries themselves stay archived in WLED-MM-M1/docs/ (rollback path).
3. wiki-m1-matrix-settings.md - the manual configuration the wiki requires today,
   which doubles as the acceptance spec.
4. mm-source-defaults.md - runtime defaults extracted from WLED-MM source
   (written after the Phase 0 inventory workflow completes).

## Key shipping facts (from platformio_override_wledmm.ini)
- env esp32S3_16MB_PSRAM_M_HUB75, board lilygo-t7-s3
- board_build.arduino.memory_type = qio_opi (16MB QIO flash + 8MB OPI PSRAM, matches
  ESP32-S3-WROOM-1-N16R8), flash_mode qio
- DEFAULT_LED_TYPE=101, MOONHUB_S3_PINOUT (HUB75 pin map)
- I2S digital mic: SR_DMTYPE=1 (Generic I2S), SD=GPIO10, SCK=GPIO11, WS=GPIO12, MCLK off
- LEDPIN=14, BTNPIN=0, RLYPIN=15, IRPIN=-1, AUDIOPIN=-1 (chosen to avoid HUB75 pins)
- AP: SSID "Apollo M-1", password EMPTY (open AP)
- SERVERNAME "Apollo M-1" (note: wiki acceptance value is "Apollo LED Matrix", set
  manually today; see DECISIONS.md)
- partitions: esp32.extreme_partitions, 16MB flash
- USB: ARDUINO_USB_MODE=1, CDC_ON_BOOT=0 (external USB-serial chip)
