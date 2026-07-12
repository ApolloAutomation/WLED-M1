# M1_FACTS.md

Established facts for the Apollo M-1 WLED migration, verified against source.

HOW TO USE THIS FILE:
Do not re-derive anything below. If you have contrary evidence, do not silently act on it:
write your evidence to FACT_CHALLENGES.md and escalate to the orchestrator.
If you are a subagent, these facts were pasted into your brief because subagents run in
clean context windows and do not inherit CLAUDE.md or the parent's context.

---

## Hardware

- Apollo M-1 LED Matrix. Controller: ESP32-S3, 16MB flash, 8MB octal PSRAM.
- Panel: 64x64 HUB75, P2.5, 4096 pixels. USB-C or WAGO 5V 3A input.
- Pinout is identical to the MoonHub board. Confirmed by Justin.
- Two PCB revisions in the field: rev4 (no microphone) and rev6+ (optional mic addon).
- ESP32-S3 supports HUB75 and audioreactive simultaneously with no known restrictions.

---

## FACT 1: the panel is HALF SCAN. It is not quarter scan.

Evidence, from MoonModules/WLED-MM `wled00/bus_manager.cpp`:

    types 101-104 = plain panels (32x32, 64x32, 64x64, 128x64). No VirtualMatrixPanel.
    types 105-108 = VirtualMatrixPanel + setPhysicalPanelScanRate(FOUR_SCAN_*). Quarter scan.

The Apollo wiki instructs users to select "Hub75Matrix 64x64", which is type 103: plain, no
VirtualMatrixPanel, no four-scan remap. Quarter-scan 64x64 is a separate type (107) which the
wiki does not use. The product ships and works on 103.

Therefore the panel is half scan. Upstream equivalent: TYPE_HUB75MATRIX_HS = 65.

Confirm on hardware anyway. A wrong scan rate does not look dim or slightly off. It looks like
interleaved horizontal bands or a doubled image. Do not switch to QS without a photograph
proving HS is wrong.

---

## FACT 2: upstream does NOT encode panel size in the LED type. WLED-MM did.

`wled00/const.h`:

    TYPE_HUB75MATRIX_HS = 65   // Half Scan
    TYPE_HUB75MATRIX_QS = 66   // Quarter Scan

`wled00/bus_manager.cpp`, BusHub75Matrix constructor:

    panelWidth  = bc.pins[0];
    panelHeight = bc.pins[1];
    chainLength = bc.pins[2];         // clamped to 1..4
    mxconfig.clkphase = bc.reversed;  // the "Reversed" checkbox is HUB75 clock phase

The type is ALREADY correct upstream via `-D LED_TYPES=TYPE_HUB75MATRIX_HS` in the [hub75]
flag group. The 32x32 bug is that the default bus comes up with the wrong panel
width/height/chain and with no 2D matrix configured. THAT is what must default to 64 / 64 / 1.

A prior session diagnosed this as a DEFAULT_LED_TYPE problem. That was correct for WLED-MM and
WRONG for upstream. Re-audit anything built on that assumption.

---

## FACT 3: the M-1 is already a supported upstream board.

Upstream `platformio.ini` ships `[env:esp32s3dev_16MB_opi_hub75]`, commented "MOONHUB HUB75
adapter board (lilygo T7-S3 with 16MB flash and octal PSRAM)":

    extends = env:esp32s3dev_8MB_opi
    board = lilygo-t7-s3
    board_build.partitions = ${esp32.extreme_partitions}   ; tools/WLED_ESP32_16MB_9MB_FS.csv
    -D MOONHUB_S3_PINOUT
       gpio { 1, 5, 6, 7, 13, 9, 16, 48, 47, 21, 38, 8, 4, 18 }
       = R1, G1, B1, R2, G2, B2, A, B, C, D, E, LAT, OE, CLK
    -D SR_DMTYPE=1 -D I2S_SDPIN=10 -D I2S_CKPIN=11 -D I2S_WSPIN=12 -D MCLK_PIN=-1
       = Generic I2S, SD 10, SCK 11, WS 12. EXACTLY the Apollo wiki mic settings, already baked.
    -D LEDPIN=14 -D BTNPIN=0 -D RLYPIN=15 -D IRPIN=-1 -D AUDIOPIN=-1
    inherits ${hub75.build_flags} and ${hub75.s3_build_flags}

`[env:apollo_m1]` MUST extend this env. Do not reimplement board, PSRAM, partitions, pinout, or
mic pins. Gotcha: build_unflags the inherited WLED_RELEASE_NAME before redefining it. See the
waveshare env for the pattern.

Cross-check: the E line (GPIO 38) must be landed on the M-1 panel connector. If E is unused, the
panel is 1/16 scan and FACT 1 is wrong. Escalate immediately if so.

---

## FACT 4: UNRESOLVED. The brightness limiter may be a second cause of "panel looks broken".

WLED-MM `const.h` has:

    #define EXCLUDE_FROM_ABL(t)  ( IS_VIRTUAL(t) || ( (t) >= (TYPE_HUB75MATRIX) && (t) < (TYPE_HUB75MATRIX + 10)))
    // WLEDMM do not apply auto-brightness-limiter on these bus types

MM never applies the auto brightness limiter to HUB75 buses. Upstream 16.0.1 appears to have NO
such exemption; BusHub75Matrix inherits `_milliAmpsPerLed` and `_milliAmpsMax` like any other bus.

If upstream's ABL applies its per-LED milliamp math to a 4096-pixel HUB75 bus, it will compute a
fictional power draw and clamp global brightness hard, producing a dim or near-black panel
independent of the 32x32 bug. A self-exemption may exist via the `_milliAmpsPerLed == 255`
sentinel. NOT CONFIRMED.

Verify in source AND on hardware by toggling ABL. If confirmed, prepare a second upstream PR
exempting HUB75 from the ABL, matching MM. Prepare it. Do not open it.

---

## Prior work (find it, do not recreate it)

- 9 commits on branch `apollo/m1`, +1163/-2, based on upstream v16.0.1. There is no v16.1 tag.
- Branch `hub75-first-boot-defaults`: prepared upstream PR, single commit, unopened.
- Branch `feat/m1-wled-entry` in a separate clone of ApolloAutomation/installer.
- None of it has ever been pushed.
- Fork is ApolloAutomation/wled-m1. Note the name. A prior session guessed "wled".

---

## Appendix: panel fault decoder

Use this instead of guessing when the panel looks wrong. Also belongs on the Apollo wiki
troubleshooting page.

    Interleaved horizontal bands, doubled image   -> wrong scan rate (HS vs QS)
    Only a quadrant lit, rest black               -> wrong panel width/height
    Image repeated or horizontally stretched      -> wrong chain length
    Whole panel dim or near black                 -> ABL applied, or default brightness too low
    Panel dark, or colors washed out and pastel   -> wrong shift register driver chip
    Ghosting or smearing at high brightness       -> needs WLED_HUB75_MAX_BRIGHTNESS below 255
    Colors bleed sideways, vertical tearing       -> clock phase (the "Reversed" checkbox)
    Went black right after a settings change      -> S3 requires a reboot to apply HUB75 changes

Shift register driver options in bus_manager.cpp: FM6124, ICN2038S, FM6126A, MBI5124, DP3246.
Upstream documents `-D WLED_HUB75_MAX_BRIGHTNESS=239` as the ghosting fix.