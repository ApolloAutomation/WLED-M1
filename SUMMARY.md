# SUMMARY: Apollo M-1 migration to upstream WLED (through the D10 bench sessions)

Updated 2026-07-15. Canonical repo: ApolloAutomation/WLED-M1, branch
m1-wled-update. THREE live hardware campaigns are complete: the first live
session (2026-07-12, OTA + factory-install QA), the D10 bench sessions
(2026-07-12/13, panel chains; BENCH_SESSION_D10.md), and the AP-mode
first-run session (2026-07-14/15, BENCH_SESSION_AP.md).

CORRECTION TO THE EARLIER SHIP-READY CLAIM: the 2026-07-13 contamination
check tested AP mode only as a provisioning step, never as a destination.
Justin's real first-run walk found the gap; D20 made AP a first-class
mode; a dedicated session root-caused every symptom (device bugs fixed:
offline Pixel Paint, crippled AP radio, modem sleep, static short text,
one-bar Sound Bars; client-side causes proven: Android cellular routing,
captive mini-browser, app file-chooser MIME bug) and added the
connectivity-probe answers (D22) plus the on-panel setup tour (D23).
A permanent AP walkthrough gate now lives in QA_CHECKLIST.md. SHIP-READY
was RE-ASSERTED 2026-07-16 for bundle b8 (commit f654b57b): fresh-flash
gate + full AP walkthrough passed on the final artifact, which ships the
D24 static setup card and the D26 clean AP SSID.

## The audit numbers first (TASK.md asked for before and after)

Delta against the v16.0.1 base tag:

| | files | insertions | deletions |
|---|---|---|---|
| Session 3 end, total | 36 | 2327 | 2 |
| After D10 sessions, total | 56 | 3410 | 14 |
| After D10 sessions, wled00 + platformio.ini only | 10 | 168 | 14 |

Reading those honestly:
- The wled00+env code surface (the part that fights upstream rebases) is 168
  added lines across 10 files: cfg.cpp 42, image_loader.cpp 60 (GIF PSRAM
  cache + fast 2D draw), platformio.ini 33 (env), bus_manager.cpp 19 (chain
  direct-drive + PSRAM shadow buffer), FX_2Dfcn.cpp 9 (256 cap + ledmap
  fallback), FX.h 6 (Panel uint16 + guard), FX_fcn.cpp 6 (underflow fix),
  const.h 3, one-liners in wled.cpp/wled.h. Six of those changes are
  customer-facing bug fixes found on hardware; each has a repro in
  BENCH_SESSION_D10.md and an upstream writeup in apollo/UPSTREAM_FINDINGS.md.
- The TOTAL delta growth is documentation and factory assets: the bench
  narrative, the findings report, the multiple-panels wiki rewrite, QA
  results, and the animated dog GIF + presets in apollo/fs/.

## What the firmware now does (hardware-verified on a factory-erased unit)

Factory boot, zero configuration: HUB75 Half Scan (type 65), one 64x64 panel,
2D matrix 1x 64x64, brightness limiter off, and the ANIMATED APOLLO DOG
(D19) greeting at brightness 128 - a 64x64 GIF on Apollo blue 0x4379AA that
blinks, flicks its ears, and sniffs on a mostly-idle 3.9 s loop, played by
the built-in Image effect from factory preset 4. Server description
"Apollo M-1", mDNS apollo-led-matrix-xxxxxx, OPEN setup AP "Apollo M-1"
(D16, join-and-play), AudioReactive ON (D15, Generic I2S SD 10 WS 12 SCK 11,
sync off), factory presets: 1 Scrolling Text, 2 Apollo Blue, 3 Sound Bars,
4 Apollo Dog. PixelForge + Pixel Paint on board. ver 16.0.1, release
Apollo_M-1, product Apollo M-1. Single panel runs 43 fps with ~154K free
heap.

Panel chains (new, D10): up to FOUR panels per unit, verified on glass in
both 1x4 (256x64) and 2x2 (128x128) arrangements - solid fills, 2D effects,
scrolling text across all seams, and GIF playback. Customer recipe (wiki
rewrite apollo/wiki-rewrites/multiple-panels.md): bus pins
[64,64,4,rows,cols], 2D config = ONE canvas-sized panel, reboot after
changes; 2x2 bottom row mounts rotated 180 with the controller into the
bottom-right panel. Four panels is the hard ceiling (DMA framebuffer DRAM,
refresh physics, power); bigger walls = multiple synced M-1s.

Performance envelope at 16384 px, measured and documented: ~30 fps text and
most content, ~17 fps heavy 2D, ~18 fps typical pixel-art GIFs, ~8 fps
worst-case full-frame GIFs. The "MM hit 60 fps" question was answered with a
full code trace (MM's write-through pixel pipeline vs upstream 16.x's
per-pixel compositor); two portable "fixes" (-O2 build flags, 4-bit panel
depth) were tested on hardware and rejected with measurements. True parity
is post-launch engineering (UPSTREAM_FINDINGS.md).

OTA from WLED-MM: the WLED_MM_HUB75_MIGRATION shim rewrites old type-101/103
bus entries on first read; hardware-proven in the first live session. NOTE:
OTA does not touch the filesystem, so existing units get firmware fixes but
not the dog/presets - those arrive via full install.

## The contamination check (Justin's Tier-1 ship gate): PASS, and it earned it

2026-07-13, on the demo unit: full chip erase, flash M-1_full_install.bin,
virgin first boot. Verified: animated dog appears with zero configuration,
customer AP flow works end-to-end (WiFi provisioned from a phone), exact
single-panel factory defaults, all four presets cycle (including
AudioReactive Sound Bars), tool pages serve, zero residue from the chain
sessions, zero panics, 43 fps / 154K heap matching the pre-chain baseline.

The check's FIRST run caught a genuine shipping blocker: the -O2 speed
flags (adopted from WLED-MM for fps parity) crash-looped the virgin boot
800+ times - while every OTA boot onto existing config all night had been
flawless. Bisected on hardware, fixed by dropping the flags (they had
measured zero LED benefit), re-flashed, re-verified. Lesson, now written
into QA_CHECKLIST.md: OTA-boot testing can never substitute for the
virgin-boot gate.

## Justin's decisions ledger (DECISIONS.md)

D1 AP password: superseded by D16 (open setup hotspot, join-and-play).
D2 unique names: applied. D3 AudioReactive: closed by D15, defaults ON.
D4 Apollo M-1 identity: applied. D5 one upstream PR stands, ABL PR
cancelled (FACT 4). D14 solid welcome color: superseded by D19.
D16 open AP, D17 factory presets + image tools, D18 PixelForge-only,
D19 animated dog first boot: all applied and hardware-verified.

## Hardware-verified versus build-verified

HARDWARE-VERIFIED (both live campaigns; results in QA_CHECKLIST.md,
BENCH_SESSION_D10.md, baseline/live/):
- D0/D1 dump + diff, D2 OTA from shipping MM, D3 factory install (twice -
  the second time as the contamination check on the final artifact),
  D4 visible light, D8 WiFi under load (256x64: 0% loss, 9.7 ms avg),
  D9 rev6 half, D10 four-panel chain in BOTH arrangements on glass.
- Six firmware fixes, each reproduced then re-verified fixed on hardware.
- GIF playback on single panel, 1x4, and 2x2; PixelForge/Pixel Paint pages
  serving on all configs.

STILL PENDING ON HARDWARE (parts or instruments needed): filesystem-erase
resilience via the 10 s button, current draw at full white (D5), ghosting
(D6), driver chip identification (D7), rev4 no-mic measurements (D9 second
half), Home Assistant discovery click-through (D11), dump-restore rollback
drill (D12).

## For Justin

1. Artifacts in apollo/out/ are final at the AP-session HEAD (dog tour,
   all fixes; also copied to ~/Downloads with sha256 sums). Pick the
   tester-bundle number (well past b6) and distribute. The AP walkthrough
   gate (QA_CHECKLIST) is the standing re-certification ritual for any
   future artifact.
2. Publish the wiki rewrites (apollo/wiki-rewrites/): matrix-settings,
   microphone-addon, panel-faults, and the NEW multiple-panels page (1x4 +
   2x2 recipes, size limits, GIF how-to). Also the older triage items:
   wrong-product pinout table, FAQ WizMote answer, PixelForge naming.
3. Installer: apply apollo/installer-fixup.patch to feat/m1-wled-entry, host
   manifest + M-1_full_install.bin, flip the URLs. This becomes the customer
   flash path (ESP Web Tools); until then, esptool erase-flash + write_flash
   0x0 (commands in the multiple-panels/reflash docs and PROGRESS.md).
4. Open the upstream PR (apollo/UPSTREAM_PR.md) and file the findings
   (apollo/UPSTREAM_FINDINGS.md: 8 WLED items, 2 of them remote-crash class
   and already fixed in this fork, + 3 HUB75-lib observations).
5. Remaining QA when parts allow: D5/D6/D7, D9 rev4, D11, D12, FS-reset
   button (QA_CHECKLIST.md).
6. EUPL-1.2: fork is public, LICENSE intact; put the source link wherever
   binaries are distributed.
7. Old clones: WLED (retired) can be archived; WLED-MM-M1 stays as rollback
   archive AND as the performance oracle for the post-launch fps work.
