# GitHub release draft (staged, NOT published)

Answers the tester ask: bin as a release on our repo instead of Google Drive.
Publish only on Justin's explicit go, after the b8 gates pass. Research
verdict behind the hosting split (2026-07-15, sourced in the session
scratchpad and summarized in BENCH_SESSION_POSTB7.md): GitHub release assets
send NO CORS headers, so ESP Web Tools cannot fetch them; jsDelivr cannot
serve release assets and caps near 20MB anyway. Therefore DUAL-PUBLISH:

1. RELEASE ASSETS on ApolloAutomation/WLED-M1 for human downloads
   (stable link: releases/latest/download/M-1_full_install.bin).
2. WEB FLASHER files (manifest.json + both bins) served same-origin with the
   installer page (GitHub Pages tree of the installer site). Manifest is
   prepared at apollo/installer/manifest.json; parts[].path resolves
   relative to the manifest URL, so keep bins beside it. Do NOT point the
   manifest at release-asset URLs, do NOT add a CORS proxy.

Tag convention: m1-b<N> (matches internal bundle numbers, never collides
with upstream v* tags). Tag the exact commit the bundle was built from.
The sha256 sums Justin distributed are the arbiter of which bytes ship.

If the release ships bundle b8, substitute b8/commit throughout; the text
below is written for b8 with placeholders.

## Title

    Apollo M-1 firmware, bundle b8

## Body (paste-ready)

```markdown
# Apollo M-1 firmware, bundle b8

Firmware for the Apollo M-1 LED matrix (ESP32-S3, 16 MB flash, 64x64 HUB75).
This is Apollo's build of upstream [WLED](https://github.com/wled/WLED)
v16.0.1 with M-1 hardware support, factory defaults, and hardware-verified
fixes. Complete source for this exact build: this repository, branch
`m1-wled-update`, tag `m1-b8`. License: EUPL-1.2.

## Which file do I flash?

| File | Use it when | How |
|---|---|---|
| `M-1_full_install.bin` | New unit, misbehaving unit, or upgrading from WLED-MM and you want the full factory experience | Serial flash at offset `0x0` after a FULL chip erase |
| `M-1_ota.bin` | Unit already runs M-1 16.0.1 firmware and you just want the update | WLED web UI: Config, Security & Updates, Manual OTA |

`M-1_full_install.bin` is the complete 16 MB image: bootloader, partition
table, app, and the factory filesystem (Apollo dog, factory presets, the
first-boot setup screen). `M-1_ota.bin` updates the app only; OTA never
touches the filesystem, so the factory content arrives only via the full
install.

## Serial flash (full install)

    esptool.py --chip esp32s3 --port <YOUR_PORT> erase_flash
    esptool.py --chip esp32s3 --port <YOUR_PORT> write_flash 0x0 M-1_full_install.bin

`<YOUR_PORT>` is e.g. `/dev/cu.usbmodem...` on macOS or `COM5` on Windows.
The full erase is mandatory: it clears old config and guarantees the factory
first-boot experience. Prefer no command line? Use the Apollo web installer
(Chrome or Edge, USB cable).

## First boot

Power on with the panel attached. While the unit is unconfigured the panel
shows the setup screen: join the open "Apollo M-1-xxxxxx" WiFi, then scan
the QR code or browse to http://4.3.2.1. Factory presets: 1 Scrolling Text,
2 Apollo Blue, 3 Sound Bars, 4 Apollo Dog. AudioReactive is on by default.
No account, no cloud, nothing leaves your home.

## What is in bundle b8

<UPDATE AFTER b8 IS CUT; b7 list plus:>
- First-boot setup redesigned as a single static page (QR + address text),
  per tester feedback
- <QR scannability changes per the glass matrix results>

Everything through the AP-mode first-run session:
- AP mode is a first-class mode: full radio power, no modem sleep, phones
  keep the hotspot usable with mobile data on
- Pixel Paint fully offline over the hotspot (no CDN)
- Frozen-segment thaw on effect change (fixes the paint-then-black trap)
- Scrolling Text: short text scrolls reliably, right-to-left
- Sound Bars: true 16-band spectrum
- Panel chains up to four panels (1x4 and 2x2 verified on hardware) with
  the chain stability fixes
- GIF playback improvements (PSRAM cache, direct 2D draw)
- OTA migration shim for units coming from WLED-MM

## Checksums (sha256)

    <FILL FROM shasum -a 256 apollo/out/*.bin AT RELEASE TIME>

## Source and license

Derivative of WLED, distributed under EUPL-1.2. Complete corresponding
source: https://github.com/ApolloAutomation/WLED-M1 (branch m1-wled-update,
tag m1-b8).
```

## Commands (STAGED, do not run without Justin's go)

```bash
# 1. Verify the bins are the gated b8 bytes
shasum -a 256 apollo/out/M-1_full_install.bin apollo/out/M-1_ota.bin

# 2. Save the body above (with real sums) to /tmp/release-notes-m1-b8.md

# 3. Create tag + release with assets
gh release create m1-b8 \
  --repo ApolloAutomation/WLED-M1 \
  --target <b8 commit sha> \
  --title "Apollo M-1 firmware, bundle b8" \
  --notes-file /tmp/release-notes-m1-b8.md \
  --latest \
  apollo/out/M-1_full_install.bin apollo/out/M-1_ota.bin
```

Flag notes: use --prerelease instead of --latest if b8 is tester-only
(mutually exclusive). Do not attach intermediate artifacts (littlefs.bin).
Release assets are for human downloads; the web flasher fetches its copies
same-origin per the hosting split above.
