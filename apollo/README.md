# Apollo M-1 build and release files

This directory holds everything Apollo-specific that is not part of the WLED source
tree itself.

## Contents
- fs/cfg.json - known-good factory configuration. Mirrors the compile-time defaults of
  the apollo_m1 environment: one HUB75 half-scan bus (type 65) as a single 64x64 panel,
  chain length 1, 2D matrix 1x 64x64, brightness limiter off, server description
  "Apollo LED Matrix". Keys follow wled00/cfg.cpp serializeConfig() for WLED 16.0.1.
  Fields deliberately omitted (mDNS name, AP settings, usermod settings) fall back to
  the compile-time defaults, which include the per-unit unique hostname and AP SSID.
- fs/presets.json - empty preset file, identical to what the firmware creates itself.
  The M-1 has never shipped presets (verified against the WLED-MM source), so there is
  nothing to migrate.
- build_artifacts.sh - builds the two release artifacts (see below).
- out/ - build products (gitignored).

## Artifacts
- M-1_full_install.bin - complete 16MB-image content merged at offset 0x0: bootloader,
  partition table, otadata, application, and a LittleFS image containing the factory
  cfg.json and presets.json. Flash after a full erase. This is the factory and
  recovery path; it wipes user settings on purpose and guarantees the 64x64 defaults.
- M-1_ota.bin - application only, for the WLED OTA update page (Config, Security and
  Updates, Manual OTA). Does not touch the filesystem, so customer settings and
  presets survive.

Both artifacts come from the same apollo_m1 PlatformIO environment. Partition layout
is tools/WLED_ESP32_16MB_9MB_FS.csv, byte-identical to the table already on shipped
M-1 units running WLED-MM, so OTA from WLED-MM 14.5.1 is safe: app slots match
(0x10000 and 0x310000, 3 MB each) and the filesystem stays at 0x610000.

## Why both a config image and compile-time defaults
The compile-time defaults (DATA_PINS, DEFAULT_PANEL_WIDTH/HEIGHT, cfg.cpp first-boot
fix) make the firmware come up correctly even if a customer erases or corrupts the
filesystem. The cfg.json in the LittleFS image makes the very first boot skip the
default-seeding code path entirely and doubles as documentation of the intended
factory state. Either one alone satisfies the acceptance table; shipping both means
no single regression can bring back the 32x32 problem.
