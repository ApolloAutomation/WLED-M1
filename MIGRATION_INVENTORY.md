# MIGRATION_INVENTORY

Every Apollo customization in the shipping WLED-MM build, its current value, and where
it lands in upstream WLED v16.0.1. Compiled 2026-07-11 from source (no live device was
reachable; see BLOCKED.md B1).

Repos:
- MM = /Users/justinapollo/Code/ApolloAutomation/WLED-MM-M1 (branch mdev, shipping)
- UP = /Users/justinapollo/Code/ApolloAutomation/WLED (upstream, tag v16.0.1, branch apollo/m1)

The entire Apollo delta over netmindz/WLED-MM (merge-base 315f147d) is one file,
platformio_override.ini, plus shipped binaries in docs/. Everything below documents the
effective state that file produces.

## Headline bug root cause
MM env sets `-D DEFAULT_LED_TYPE=101` (platformio_override.ini:16). In WLED-MM,
HUB75 type 101 = 32x32 panel (MM bus_manager.cpp:681-714: 101=32x32, 102=64x32,
103=64x64, ...). The shipping firmware's factory default is literally a 32x32 HUB75
bus. 64x64 would have been type 103. On top of that, MM never seeds a 2D matrix
config (isMatrix defaults false) and ABL defaults on at 1500 mA (MM const.h:458).
This is why the wiki settings page exists.

## Acceptance table mapping

| Acceptance item | Shipping MM reality | WLED 16.0.1 target |
|---|---|---|
| Server description "Apollo LED Matrix" | Compiled SERVERNAME "Apollo M-1" (platformio_override.ini:20); wiki has users change it manually | `-D SERVERNAME='"Apollo LED Matrix"'` -> serverDescription (UP wled00/wled.h:426-430) |
| mDNS apollo-led-matrix | Factory default is wled-XXXXXX (MM wled.cpp:763); wiki has users set apollo-led-matrix manually | New WLED_MDNS_PREFIX define + patched fallback in UP wled00/wled.cpp:536 -> apollo-led-matrix-XXXXXX (unique suffix, DECISIONS A1) |
| LED type Hub75Matrix 64x64 | Type 101 = 32x32 (the bug) | TYPE_HUB75MATRIX_HS = 65 (UP const.h:358) with pins[0..1] = 64,64. Bus "pins" for HUB75 are config params {panelW, panelH, chain, rows, cols} (UP bus_manager.cpp:798-811, bus_manager.h:174). Env: `-D DATA_PINS=64,64,1,1,1`, LED_TYPES=TYPE_HUB75MATRIX_HS (from [hub75] group) + cfg.cpp first-boot fix (see below) |
| Chain length 1 | bc.pins[0] in MM semantics; default 0/1 | pins[2] = 1 in DATA_PINS. Upstream clamps chain 1..4 (bus_manager.cpp:828) - matches the 4-panel chain product limit |
| ABL off | ON at 1500 mA (MM const.h:458); wiki has users uncheck it | `-D ABL_MILLIAMPS_DEFAULT=0` (0 = disabled, UP const.h:595-603) |
| 2D 64x64 Basic | Not set at factory; wiki manual step | No upstream compile defines exist for 2D defaults (only WLED_MAX_PANELS, const.h:166). Adding DEFAULT_PANEL_WIDTH/HEIGHT seed in cfg.cpp matrix section (fresh-install only) + shipped cfg.json |
| AudioReactive Generic I2S | SR_DMTYPE=1 (platformio_override.ini:34) | Same define upstream (audio_reactive.cpp:771-776, default already 1) |
| AR pins SD 10 / WS 12 / SCK 11 | I2S_SDPIN=10 I2S_WSPIN=12 I2S_CKPIN=11 MCLK=-1 | Identical defines already present in upstream env esp32s3dev_16MB_opi_hub75 (platformio.ini:891) |
| AR sync Off | audioSyncEnabled=0 default | Same default upstream (audio_reactive.cpp:77) |
| AP SSID/pass match MM build | "Apollo M-1" / "" (open AP) | `-D WLED_AP_SSID='"Apollo M-1"'`, `-D WLED_AP_PASS='""'` + WLED_AP_SSID_UNIQUE (deviation per task, DECISIONS A2). Open-AP behavior identical (WiFi.softAP with empty pass) |

## Pin map (verified byte-identical MM vs upstream)

HUB75 via MOONHUB_S3_PINOUT, GPIO order {R1,G1,B1,R2,G2,B2,A,B,C,D,E,LAT,OE,CLK}:
{1, 5, 6, 7, 13, 9, 16, 48, 47, 21, 38, 8, 4, 18}
- MM: wled00/bus_manager.cpp:749-753
- UP: wled00/bus_manager.cpp:887-890 (SAME GPIOs, SAME define name - the MoonModules
  HUB75 support was upstreamed before v16.0.1)

Aux pins (both repos): LEDPIN=14, BTNPIN=0 (boot button: toggle/AP reset/factory
reset), RLYPIN=15 (panel power rail, active high), IRPIN=-1, AUDIOPIN=-1.
I2S mic: SD=10, SCK/BCLK=11, WS=12, MCLK off.

Collision check (Phase 1): HUB75 set {1,4,5,6,7,8,9,13,16,18,21,38,47,48} vs
I2S {10,11,12} vs button {0} vs relay {15} vs LEDPIN {14}: all disjoint. NO COLLISIONS.
GPIO 14 note: LEDPIN=14 is a dummy to keep the default WS2812 path off HUB75 pins; the
HUB75 bus does not use it. Upstream chose the same values.

E pin (GPIO38) is wired: 64-row 1/32-scan panels supported. Driver chip: library
default shift register (no FM6126A); FM6124 only forced for quarter-scan outdoor
types, not used by the M-1.

## Build environment

| Item | MM shipping | Upstream 16.0.1 target |
|---|---|---|
| env | esp32S3_16MB_PSRAM_M_HUB75 (platformio_override.ini, extends esp32S3_8MB_PSRAM_M) | NEW [env:apollo_m1] extends env:esp32s3dev_16MB_opi_hub75 (platformio.ini:881-893) which is the same physical target: board lilygo-t7-s3, qio_opi, 16MB |
| board | lilygo-t7-s3 | lilygo-t7-s3 (boards/lilygo-t7-s3.json: qio_opi, 16MB, ARDUINO_USB_MODE=1) |
| PSRAM | qio_opi = 16MB QIO flash + 8MB OPI PSRAM (ESP32-S3-WROOM-1-N16R8) VERIFIED from board json + override | same (inherited) |
| partitions | tools/WLED_ESP32_16MB_9MB_FS.csv (esp32.extreme_partitions) | SAME FILE, byte-identical: nvs 0x9000/0x5000, otadata 0xe000/0x2000, app0 0x10000/0x300000, app1 0x310000/0x300000, spiffs(LittleFS) 0x610000/0x9E0000, coredump 64K. OTA-compatible; FS offset unchanged so field configs survive |
| max app size | 0x300000 = 3,145,728 B per OTA slot | same |
| HUB75 lib | softhack007/ESP32-HUB75-MatrixPanel-DMA_sh7#fix_dangling_pointer (branch pin, v3.0.12-era) | mrfaptastic/ESP32-HUB75-MatrixPanel-DMA #f17fb7fe = v3.0.14 (commit-pinned, platformio.ini:809) |
| USB | ARDUINO_USB_MODE=1, CDC_ON_BOOT=0 (external USB-serial chip) | must KEEP CDC_ON_BOOT=0 (unflag the =1 from hub75.s3_build_flags) |
| watchdog | WLED_WATCHDOG_TIMEOUT=0, brownout detector disabled | WLED_WATCHDOG_TIMEOUT=0 inherited from hub75.s3_build_flags; WLED_DISABLE_BROWNOUT_DET was an MM define - dropped (upstream has no such flag; brownout stays enabled unless problems surface in QA) |

## Usermods / features

| Feature | MM shipping | 16.0.1 target |
|---|---|---|
| AudioReactive | Compiled (USERMOD_AUDIOREACTIVE via MM build_flags_S), runtime DISABLED by default (audio_reactive.h:1190-1194; no SR_ENABLE_DEFAULT) | Compiled via custom_usermods = audioreactive (inherited through env chain); runtime disabled by default (no UM_AUDIOREACTIVE_ENABLE). Mic pins/type preconfigured by defines. Matches MM behavior; see DECISIONS A7 |
| Auto Playlist | Compiled (USERMOD_AUTO_PLAYLIST) | Not carried over (no evidence of runtime use; MM-specific). Log: available upstream? 16.x has usermods/ dir - NOT added. Follow-up if wanted |
| ARTIFX | Compiled (MM-exclusive) | Does not exist upstream. Dropped |
| Animartrix | Compiled (netmindz/animartrix pin; GPL-limbo lib) | Exists upstream as usermod but NOT added (licensing + not in acceptance spec). Dropped; effects covered by upstream FX set |
| Auto Save | Compiled (USERMOD_AUTO_SAVE) | Not carried over (not in acceptance spec; can be added later via custom_usermods) |
| MQTT | Compiled, runtime disabled | Same upstream (compiled by default, mqttEnabled=false) |
| HA discovery | None in firmware (MM removed MQTT discovery; HA uses native WLED integration via mDNS _wled._tcp) | Identical upstream. No action needed. HA entity behavior verified via integration, not firmware |
| Alexa/Loxone | Accidentally compiled IN (MM override replaced parent build_flags that disabled them); runtime off | Upstream compiles Alexa/etc by default, runtime off. No action |
| IR | Code compiled, IRPIN=-1 inert | Same approach (IRPIN=-1) |
| UDP sync | Ports 21324/65506; receive bri/col/fx ON, send OFF | Same upstream defaults |
| NTP/TZ | Disabled / UTC | Same upstream defaults |
| Gamma/CIE | NO_CIE1931 (driver gamma off) | Same flag in [hub75] group. Note 16.x global gamma changes: QA visual pass required |

## Identity / versioning

| Item | MM shipping | 16.0.1 target |
|---|---|---|
| versionString | "14.5.1-dev" (package.json via set_version.py) | "16.0.1" (package.json via set_metadata.py). Real version bump for OTA sanity |
| releaseString | BUG: "mdev_release" - the env unflags its own WLED_RELEASE_NAME=Apollo_M-1 (platformio_override.ini:8 vs 19), so shipped units do NOT report Apollo_M-1 | -D WLED_RELEASE_NAME=\"Apollo_M-1\" (no self-unflag) |
| brand / product | WLED / (MM has no product string) | WLED_BRAND stays "WLED" (community-first; UI unchanged); -D WLED_PRODUCT_NAME='"Apollo M-1"' -> /json/info product field identifies the Apollo build |
| OTA password | default "wledota" (not overridden) | unchanged; flag for review (SUMMARY follow-ups) |

## Presets / playlists / boot behavior
- NO presets.json or cfg.json is shipped or baked anywhere in the MM repo (repo-wide
  search; firmware creates empty {"0":{}} on first boot). Boot preset = 0, turnOnAtBoot
  = true, effect Solid, palette Default, color orange 0xFFAA00, brightness 128.
- Phase 4 conclusion: there are no shipped presets to migrate. Index-mapping work is
  not applicable. Upstream 16.0.1 first boot is also Solid/orange/128. The gamma
  difference (16.x color handling) still needs the QA visual pass.

## Rollback archive (already in git)
WLED-MM-M1/docs/: merged-firmware.bin (25.7.14.1), 14.5.1/Apollo_M-1_Firmware_14.5.1.bin
(25.8.19.1, rev4), Rev6_14.5.1/Apollo_M-1_Rev6_14.5.1.bin (25.10.9.1, rev6, latest
shipping) + their ESP Web Tools manifests + bootloader/partitions/boot_app0 parts.

## Gaps upstream needed for zero-config first boot (Phase 3 patches)
1. cfg.cpp default-bus loop (cfg.cpp:285-327) treats HUB75's 5 config slots as GPIOs
   and mangles them (values like 64 fail isPinOk). validatePinsAndTypes already has the
   HUB75 carve-out (cfg.cpp:29-37); the runtime loop does not. Fix: skip GPIO
   sanitization for Bus::isHub75 types. (This is why upstream main commit 66069245
   removed LED_TYPES=65 from hub75 envs - first boot was broken. Our fix re-enables it;
   prime upstream PR candidate.)
2. No compile-time 2D matrix defaults exist. Add DEFAULT_PANEL_WIDTH/HEIGHT seeding in
   the cfg.cpp matrix section, fresh-install only (guarded by ins.isNull() && fromFS).
3. mDNS fallback prefix "wled-" hardcoded (wled.cpp:536). Add WLED_MDNS_PREFIX.
4. WLED_AP_SSID_UNIQUE prefixes with WLED_BRAND, not WLED_AP_SSID (wled.h:1028-1042).
   Patch to use WLED_AP_SSID so the unique AP keeps the Apollo M-1 name.
