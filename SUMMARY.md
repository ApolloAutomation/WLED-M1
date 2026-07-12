# SUMMARY: Apollo M-1 migration to upstream WLED (through session 3)

Updated 2026-07-12, session 3. Canonical repo: ApolloAutomation/WLED-M1, branch
m1-wled-update, pushed. Nothing has touched hardware in any session; the split
between hardware-verified and build-verified is exact and appears below.

## The audit numbers first (TASK.md asked for before and after)

Delta against the v16.0.1 base tag:

| | files | insertions | deletions |
|---|---|---|---|
| Before (session 2 end) | 29 | 1163 | 2 |
| After (session 3), total | 36 | 2327 | 2 |
| After, CODE ONLY | 11 | 209 | 2 |
| Before, CODE ONLY | 11 | 212 | 2 |

Reading those honestly:
- The code delta was already small and got slightly smaller (212 to 209) while
  ABSORBING the session-3 additions (AP password, product string comments). The
  audit deleted every duplicated line: [env:apollo_m1] no longer restates the
  pinout define, the five aux pin defines, the five I2S mic defines, or the four
  flag-group references; it now expands the parent env's build_flags and unflags
  only the inherited release name (the exact pattern upstream main uses for the
  waveshare env).
- The TOTAL delta grew because TASK.md itself demands documentation files:
  M1_FACTS.md (committed per instructions), FACT_CHALLENGES.md, WIKI_TRIAGE.md
  (13-page triage), the D0-D12 QA checklist, and three wiki page rewrites. Docs,
  not firmware. The firmware surface that fights future upstream rebases is the
  209-line code column: 36 lines in wled00/cfg.cpp, 2 one-line patches (wled.cpp
  mDNS prefix, wled.h AP SSID), 3 lines in const.h, a 29-line env, and the
  apollo/ factory-image tooling.

## What the firmware now does (build-verified, values read from inside the built artifact)

Factory boot, zero configuration: HUB75 Half Scan (type 65), one 64x64 panel,
chain length 1 (reads as 1 in the UI), 2D matrix 1x 64x64, brightness limiter off,
Solid warm orange at brightness 128 on the full-panel segment, server description
"Apollo M-1", mDNS apollo-led-matrix-xxxxxx, setup AP "Apollo M-1-xxxxxx" password
wled1234, AudioReactive compiled/disabled with Generic I2S SD 10 WS 12 SCK 11 sync
Off, ver 16.0.1, release Apollo_M-1, product Apollo M-1.

Verification method (Phase C, per TASK.md "not by reading source"): unpacked the
LittleFS image out of M-1_full_install.bin and read cfg.json (type 65, pin
[64,64,1,1,1], mpc 1, 64x64, maxpwr 0, name Apollo M-1); confirmed identity strings
present in firmware.bin and "Apollo LED Matrix" absent; GIF decoder confirmed
present in the binary (three wiki example pages depend on it). Build: SUCCESS,
zero macro-redefinition warnings, 1,250,144 bytes = 39.7 percent of the 3 MB OTA
slot. Partition table byte-identical to shipped WLED-MM units.

OTA from WLED-MM: the WLED_MM_HUB75_MIGRATION shim rewrites old type-101/103 bus
entries to the 16.x layout on first read, so upgraded customers keep a working
display and their settings. Full-erase install restores all factory defaults.

## What the adversarial verification changed (FACT_CHALLENGES.md)

- FACT 1 (half scan) and FACT 3 (M-1 = upstream MOONHUB board) survived attack,
  with byte-identical pinout confirmed again from pristine v16.0.1.
- FACT 2: code correct, prose imprecise. Pristine upstream first boot creates ZERO
  buses (dead display), not a wrong-sized one; and chain survives sanitization
  (only the two 64s were mangled). Migration notes amended.
- FACT 4: the upstream ABL fear is DISPROVEN. Upstream ABL is structurally
  digital-bus-only (isDigital() gates every loop; BusHub75Matrix carries no
  milliamp state). The planned second upstream PR is cancelled: nothing to patch.
  maxpwr=0 stays as defense-in-depth and to keep the UI checkbox reading off.
- DEFAULT_LED_COUNT was silently ineffective all along (unguarded #define in
  const.h beats any -D). Replaced with the guarded PIXEL_COUNTS. Found by reading
  the full build log rather than trusting exit codes.

## Justin's decisions: applied or queued

- D1 AP password wled1234: APPLIED (and logged: OTA-upgraded units keep their old
  open-AP config; only full-erase units get the password).
- D2 unique names: already implemented, 6 MAC hex chars, confirmed.
- D3 AudioReactive enabled-by-default: OPEN as instructed; QA item D9 collects the
  measurements (rev4 no-mic CPU/heap/refresh/current) that produce the
  recommendation.
- D4 server description Apollo M-1: APPLIED (env + factory cfg.json + artifact
  re-verified).
- D5 PRs prepared, not opened: one PR stands (hub75-first-boot-defaults, single
  commit, pushed to the fork; description in apollo/UPSTREAM_PR.md); the ABL PR
  is cancelled per FACT 4.
- D14 (new): boot visual proposal for you: keep Solid orange 128 (option a,
  recommended, zero risk) or ship a preset with a gentle 2D effect (option b).
  Decide after seeing option (a) on hardware in QA D4.

## Wiki triage (WIKI_TRIAGE.md, the real definition of done)

13 pages, one agent per page. Scorecard: matrix-settings lands 11 of 13 steps in
FIXED AS DEFAULT; the two leftovers are the flash itself and the rev6 microphone
enable, both of which belong to other pages. Getting-started drops 8 steps.
FAQ drops 6 (including the WizMote "special firmware" answer: ESP-NOW ships in the
standard upstream build). Rewrites ready in apollo/wiki-rewrites/ for
matrix-settings, microphone-addon, and a new panel-fault troubleshooting page
containing the fault decoder.

Genuine findings out of the triage:
- The published pinout page's table appears to be for the wrong product (header
  says "LED-1 PCB") and lists mic pins SD 16 / WS 6 / SCK 7, contradicting both
  the firmware and the matrix-settings page (SD 10 / WS 12 / SCK 11). Needs a
  wiki fix regardless of this migration.
- Three example pages depend on GIF playback: decoder confirmed present in the
  16.0.1 artifact; visual QA still required (gamma).
- The reflash page's install path is WLED-only and references a Discord CDN
  binary and a third-party flasher; it should point at the installer, and the
  ESPHome option must stay visible (QA item added).

## Hardware-verified versus build-verified

HARDWARE-VERIFIED (live session 2026-07-12, Justin's mic-equipped demo unit,
results and captures in QA_CHECKLIST.md and baseline/live/):
- D0/D1: 16 MB dump taken and integrity-proven before any write; unit state
  diffed (wiki-configured type 103; release "mdev_release" bug confirmed live).
- D2 OTA from shipping WLED-MM: PASS. Filesystem mounted, WiFi/settings/presets/
  GIFs survived, migration shim produced type 65 pin [64,64,1,1,1]. The
  pre-existing fictional 4-panel matrix was dropped by upstream's bounds check
  (already broken on MM; corrected via API).
- D3 factory install: PASS, 13 of 13 acceptance rows over HTTP on a zero-config
  boot; unique mDNS hostname and AP name matched the MAC-derived prediction.
- D4 visible light: PASS. Full 64x64 lit within seconds, no configuration.
- D9 rev6 half: PASS. AudioReactive works with zero touches (GEQ reacts to
  claps); sync off.
- Two OTA cycles total (MM to 16.0.1, then 16.0.1 to 16.0.1 carrying the live
  decisions below).
- Live decisions taken by Justin during the session: factory welcome color is
  Apollo blue 0x4379AA (D14), AudioReactive defaults ON (D15/D3), both shipped
  and verified on the unit.
- New support-relevant finding: 16.x rejects cross-subnet OTA by default
  (otaSameSubnet); WLED-MM did not. Documented for the wiki.

STILL PENDING ON HARDWARE (parts or instruments needed): filesystem-erase
resilience via the 10 s button (exercises the compile-default path), current
draw at full white (D5), ghosting (D6), driver chip identification (D7), WiFi
under load (D8), rev4 no-mic measurements (D9 second half), 4-panel chain
(D10), Home Assistant discovery click-through (D11), dump-restore rollback
drill (D12).

## For Justin

1. Run QA_CHECKLIST.md with a unit on serial and M1_ALLOW_FLASH=1. D0 first.
2. After D2-D4 pass: open the upstream PR from
   ApolloAutomation/WLED-M1:hub75-first-boot-defaults (apollo/UPSTREAM_PR.md).
3. Installer: apply apollo/installer-fixup.patch to the feat/m1-wled-entry branch
   (corrects the fork name a prior session wrote), set up hosting for
   apollo/installer/manifest.json + M-1_full_install.bin, then flip the URLs.
4. Wiki, when firmware ships: replace matrix-settings and microphone pages with
   apollo/wiki-rewrites/, add the panel-faults page, fix the wrong-product pinout
   table, update the FAQ per WIKI_TRIAGE (AP name "Apollo M-1-xxxxxx", WizMote,
   reflash path), and rename Pixel Magic references to Pixelforge on the
   introduction and example pages.
5. EUPL-1.2: ApolloAutomation/WLED-M1 is public, LICENSE intact, all changes
   public. Put the source link wherever binaries are distributed.
6. Old clones: /Users/justinapollo/Code/ApolloAutomation/WLED (retired, has the
   original branches, push-blocked to upstream) can be archived or deleted once
   you confirm the pushed branches; WLED-MM-M1 stays as the rollback archive
   (ROLLBACK.md).
