# BENCH SESSION: D10 four-panel chain (2026-07-12, live, Justin at the bench)

Resume file. If context is lost, read this top to bottom, then PROGRESS.md.
Single-operator rule is in force: no agents may touch the serial port or device HTTP.

## Hardware truth (from Justin, overrides TASK.md where they conflict)
- FOUR panels chained to the M-1, SAME MODEL as the M-1's own panel (half scan).
- Physical arrangement: one horizontal row (1x4), CONTROLLER ON THE FAR RIGHT.
- IMPORTANT CORRECTION: TASK.md said the 4-chain was never tested; Justin says a
  4x1 setup worked VERY WELL on shipping WLED-MM (chain length + 2D settings only).
  Hardware, cabling, and panels are PROVEN GOOD. All tonight's artifacts are
  upstream-16 firmware bugs in the chain path.
- WLED-MM drove chains DIRECTLY on the DMA display (no virtual layer, types
  101-104 plain). Upstream 16.0.1 wraps any rows/cols chain in VirtualMatrixPanel
  (CHAIN_TOP_RIGHT_DOWN hardcoded, bus_manager.cpp ~1056-1068). Prime suspect.
- Justin also wants 2x2 support eventually ("told it was a WLED limitation" -
  it is not: the lib supports rows x cols grids; same code path once 1x4 works).

## Device state RIGHT NOW
- Unit 192.168.20.99 (apollo-led-matrix-2f5f7c, USB /dev/cu.usbmodem1101).
- Running the BENCH DEBUG build (env apollo_m1_dbg from gitignored
  platformio_override.ini: extends apollo_m1 + ARDUINO_USB_CDC_ON_BOOT=1 +
  WLED_DEBUG; console works over USB; Improv-serial provisioning works - WiFi
  was provisioned over USB with it).
- Config on flash at last check: bus type 66 (QS - WRONG, revert to 65),
  pin [64,64,4,1,4], len 16384, matrix mpc 4 (4x 64x64 in a row, canvas 256x64).
- FS was wiped mid-session (crash-loop recovery), so factory presets/pixelpaint
  are gone from the unit; WiFi re-provisioned via Improv. Fine for bench.
- The demo unit's original WLED-MM dump is safe: baseline/live/m1_factory_16mb.bin.

## Confirmed bugs found tonight (all reproduced, all in QA notes)
1. MAX_LEDS boundary: 4x 64x64 = exactly 16384 = S3 MAX_LEDS, driver guard uses
   >= so exactly-four-panels was rejected. FIXED: -D MAX_LEDS=16388 in apollo_m1.
2. Divide-by-zero boot loop: cfg.cpp maMax fallback divides by "total" which can
   be saved as 0 (save during bus teardown); ArduinoJson | evaluates the fallback
   even when maxpwr exists. Customer-reachable. FIXED: guarded (total > 0).
   Recovery if hit: erase FS region 0x610000 len 0x9E0000 (esptool erase_region).
3. 2D width cap: setUpMatrix rejected Segment::maxWidth > 255; a 4-panel chain is
   exactly 256 wide (and max coordinate index 255 fits 8-bit anyway).
   FIXED: cap moved to > 256 (FX_2Dfcn.cpp), M-1 4x1 = 256x64 now configures.
4. Ledmap alloc: 16384-pixel map needs 32KB contiguous internal RAM; added a
   PSRAM fallback in FX_2Dfcn.cpp + FX_fcn.cpp (insurance; primary alloc worked
   once bug 3 was fixed; heap ~23KB free at 256x64, tight).
5. UNSOLVED - THE CURRENT BUG: with type 65 (HS) chain 4 + 256x64 matrix, canvas
   geometry is scrambled on glass. Edge test (RED at canvas x0 vertical, WHITE
   x255 vertical, GREEN y0 horizontal, YELLOW y63 horizontal) rendered as:
   staircase of horizontal segments stepping DOWN ~16 px per 64 px of x, short
   16-px vertical dashes repeating every 64 px, panel order MIRRORED (canvas
   left appears at physical far right - consistent with controller cabled to the
   rightmost panel and CHAIN_TOP_RIGHT_DOWN). Photos in the chat log.
   - QS (type 66) test: different mangling, not the fix (panels are HS). Revert.
   - The 16-px periodicity looks scan-ish BUT panels are proven HS single, and
     the same chain worked on MM without the virtual layer -> suspect upstream's
     VirtualMatrixPanel usage: WHICH CLASS/API does bus_manager instantiate?
     The lib ships BOTH the legacy ESP32-VirtualMatrixPanel-I2S-DMA.h (ctor:
     disp, rows, cols, resX, resY, chainType - getCoords derivation for 1x4
     TOP_RIGHT_DOWN is IDENTITY, should have worked) AND a NEW template API
     ESP32-HUB75-VirtualMatrixPanel_T.hpp (calcPhysicalToElectricalCoords with
     pixel_base / scan-rate handling). NEXT STEP: check which header
     bus_manager.cpp actually includes/instantiates and whether the ctor
     arguments are interpreted per the OLD API while compiling the NEW one.
     Also verify what virtualDisp->width() returned (console said 256 - OK).
   - MM comparison is the oracle: MM bus_manager.cpp (WLED-MM-M1 repo) drove
     display directly with x=pix%width, y=pix/width on mx_width=64,chain=4.
     If needed, bypass option: for _rows*_cols==chain with rows==1, skip
     VirtualMatrixPanel entirely and draw direct like MM (upstream-shaped fix).

## Working method notes (hard-won)
- Config saves are DEFERRED; poll the RAW FILE http://IP/cfg.json (NOT /json/cfg,
  which serializes RAM) before rebooting, or the save races the reboot.
- Any /json/cfg POST triggers a save of CURRENT RAM - posting ota.same-subnet
  toggles around an OTA can wipe not-yet-persisted parts (matrix!) from flash.
  Order: get matrix+bus onto flash LAST, verify raw file, then reboot.
- Live bus re-init on S3 HUB75 tears down and half-applies: ALWAYS reboot after
  bus/matrix changes; expect one full boot before judging.
- OTA cross-subnet: unflag ota.same-subnet first, restore after.
- Serial console: HWCDC on /dev/cu.usbmodem1101; capture with a background cat
  loop; early boot lines are lost to re-enumeration (use live console for
  runtime events instead). addr2line for panics:
  ~/.platformio/packages/toolchain-xtensa-esp32s3/bin/xtensa-esp32s3-elf-addr2line
  -pfiaC -e .pio/build/apollo_m1_dbg/firmware.elf <addrs>
- 16MB flash reads over this port fail as one piece; use 16x 1MB chunks.

## Still to do in D10 after the mapping bug is fixed
1. Revert bus to type 65 + matrix mpc4 (canvas 256x64), verify edge test CLEAN:
   red left edge (or right if mirrored - document which), white opposite,
   green top, yellow bottom, continuous across seams.
2. Panel-order question: with controller on far right, canvas-left lands on the
   far-right panel (mirrored). Decide: document cabling direction for customers
   OR flip panel x-offsets in the 2D layout (panels listed right-to-left) -
   test which gives correct reading order.
3. Scrolling text across 256x64 (the real-content test).
4. White ladder 25/50/100 percent with Justin's meter (power module status
   still UNCONFIRMED - ASK before bright tests; USB alone cannot power 4 panels).
5. fps/heap/psram table 64x64 vs 256x64 (baseline: 44fps/150168/8264615;
   chain HS: 30fps/23-56K/8.16-8.17MB depending on state).
6. WiFi under load at 256x64 (idle baseline: 0 percent loss, 6.0ms avg).
7. 2x2 experiment if time: pins [64,64,4,2,2], matrix 4 panels at
   (0,0)(64,0)(0,64)(64,64), canvas 128x128. Physical serpentine caveat.
8. THE CONTAMINATION CHECK (Justin's Tier-1): factory-erase, flash
   apollo/out/M-1_full_install.bin (REBUILD FIRST from current source - it
   carries tonight's fixes), verify single-panel 64x64 defaults untouched.
9. Rebuild production artifacts + tester bundle (b6) with tonight's fixes;
   update QA_CHECKLIST D10 section, FACT_CHALLENGES (TASK.md premise corrections:
   4x1 was field-proven on MM; horizontal-only claim needs revision - grids are
   supported by the lib), DECISIONS (MAX_LEDS, 256 cap, div0, psram fallback),
   wiki multiple-panels rewrite, upstream findings list (now 4+ items).

## Uncommitted work reminder
platformio_override.ini (bench env) is GITIGNORED by design - its contents are
documented above. Everything else from tonight is committed after each fix; if
this file exists but fixes are missing from git log, check the working tree.
