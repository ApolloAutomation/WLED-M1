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

## ADDENDUM (late session, after direct-drive bypass build 36ea8972 + factory reflash)

### THE WORKING CHAIN RECIPE on this firmware (customer-facing, wiki-ready)
1. LED settings (UI or API): HUB75 (Half Scan), Panel 64x64, No. of Panels 4,
   rows x cols = 1 x 4. Save, REBOOT. (Slots = pin [64,64,4,1,4].)
2. 2D Configuration: FOUR panels of 64x64 at X offsets 0/64/128/192, Y 0.
   NEVER one 256x64 panel: per-panel dims are 8-bit upstream (255 max, field
   goes red). WLED-MM's cure was "one 256x64 panel"; the upstream equivalent
   is four 64s. KEY MIGRATION DOC ITEM for chaining customers.
3. TRAP: the 2D settings page saves WHATEVER layout it currently shows. If it
   shows a stale 1-panel 64x64 layout and the user hits Save, the canvas
   collapses to 64x64 and content tiles 4x squashed on the 256 bus (photo in
   chat; identical intermediate state existed on MM). Re-push 4-panel matrix.

### Verified on glass tonight (direct-drive path, all four panels)
- Solid fills: perfect across the chain, cold-boot stable.
- DNA (2D fx): ONE wide helix across all four panels per Justin - mapping is
  substantially CORRECT. (Scrolling text = his definitive test, pending below.)
- Rainbow "per-panel" report RESOLVED as 1D-expansion semantics, not a bug:
  m12=0 fine hue rows, m12=1 row-bars (vertical, north-south). Justin confirms
  rainbow was never horizontal on MM either. Consider default m12 choice for
  factory presets only; no code change.
- 2D settings preview labels hardware panels 3|2|1|0 RIGHT to LEFT (panel 0 =
  first chained = controller end = far right). Reading-order verdict comes
  from scrolling text.
- fps: 28-30 solid, ~15 on heavy 2D at 256x64. Heap ~23K free steady.
- LED memory gauge: 180224/196608 B = 91 percent, UI warns stability/lag.
  PRIME SUSPECT for the scrolling-text wedge (render loop hung + WiFi drop,
  watchdog off). LEVER READY: -D MAX_LED_MEMORY=(256*1024) or similar in
  apollo_m1 (S3+PSRAM afford it; default 192K in const.h). Not yet applied.
- Power: Justin states the rig runs full white on 4 panels fine (power module
  in line). Ladder measurement optional.

### Device state at addendum time
Factory b6 image (has factory presets + pixelpaint) + WiFi reprovisioned +
chain-4 config live (256x64, count 16384). Justin's "mypaint" saved on device.
Production artifacts + Desktop bundle already at b6 (single-panel customers
unaffected; chain fixes included).

### Next actions queue
1. Scrolling text across 256x64 (definitive mapping + reading-order + the
   hang repro). If it wedges: power-cycle, apply MAX_LED_MEMORY bump, rebuild
   dbg+prod, OTA, retest.
2. Lock config; have Justin walk the UI once to confirm both pages now show
   the four-panel truth (and Save is then harmless).
3. WiFi-under-load test; optional current readings.
4. Wiki multiple-panels rewrite from the recipe above + LED-memory warning
   note + 1D-expansion explainer. QA_CHECKLIST D10 results block.
5. 2x2 wish (Justin): needs the virtual path (rows=2) which is still the
   scrambled one - future session; direct path only covers 1xN today.
6. Upstream findings list now: >= MAX_LEDS boundary, cfg total=0 div-by-zero,
   2D width cap 255 (should be 256+), virtual-path 1xN geometry scramble
   (repro'd, bypassed in fork), tight MAX_LED_MEMORY for HS chains.

### FINAL late-night status (context handoff point)
- WORKING on the 4x1 chain (256x64, direct drive): solid fills, DNA and organic
  2D effects (one wide helix confirmed by Justin), rainbow (1D semantics),
  Pixel Paint content once canvas is right. Cold-boot stable. This is a USABLE
  display state; DNA left running.
- NOT WORKING: Scrolling Text on 256x64 = STATIC shredded letter fragments in
  two horizontal bands, does not animate. Engine keeps running (fps ~32), no
  alloc error on the WLED_DEBUG console (capture was silent; early-boot capture
  gap does not apply here - this was live). Suspects for next session, in
  order: (1) effect/segment data ceiling for 256-wide text (find 16.x name of
  the segment-data cap; the LED-memory gauge already reads 91 percent red),
  (2) high-frequency content revealing a residual row/subrow interleave that
  organic effects hide - decisive probe: STATIC single letter drawn via
  segment i-ranges at known coords, compare glass vs canvas, (3) the earlier
  multi-seg/dark-glass wedge - possibly same root.
- Earlier bold-edge test in direct mode showed "panels off": likely the same
  text-class failure (thin static content), NOT power - solid frames work.
- Next-session order: static-letter probe -> find+raise segment-data and
  MAX_LED_MEMORY ceilings in apollo_m1 -> retest text -> if interleave
  persists, swap HUB75 lib to WLED-MM's softhack007 fork (field-proven with
  these panels) and retest -> then WiFi-under-load, wiki chaining rewrite,
  QA_CHECKLIST D10 block, upstream findings report.

## SESSION 2 ADDENDUM (2026-07-12 late night): TEXT BUG KILLED - it was heap, not mapping

### Correction to "device state" above
The unit was running the FACTORY B6 image, not apollo_m1_dbg (proof: panic
dump ELF sha 5f0470d5... == .pio/build/apollo_m1/firmware.bin app descriptor;
/json/info lacked the WLED_DEBUG-only maxalloc field). That is why the last
session's console capture was "silent": b6 has no WLED_DEBUG and no CDC
console. ALSO: plain `cat` on /dev/cu.usbmodem1101 only ever shows ROM boot +
panic text (USB-Serial-JTAG); HWCDC app output needs DTR asserted - use
scratchpad serial_logger.py pattern (pyserial, ser.dtr=True). With the real
dbg build + DTR the console works and streams "Slow strip 31/23" pacing lines.

### Root cause of the Scrolling Text freeze (and the WiFi drop, and more)
- BusHub75Matrix allocates a 48KB shadow buffer (16384 px * CRGB) with
  BFRALLOC_PREFER_DRAM (bus_manager.cpp ~1053). At bus-init heap is still
  large, so it lands in DRAM, leaving ~23K free / <14K contiguous at 256x64.
- wled.cpp:185-211 heap watchdog needs MIN_HEAP_SIZE (15K) CONTIGUOUS heap:
  after 15 consecutive low seconds it purges segments and forces ALL segments
  to FX_MODE_STATIC (= text freezes mid-frame as "static shredded fragments",
  engine keeps rendering at ~30fps); at 30s it resets segments; at 45s it
  DESTROYS AND RE-CREATES the strip and sets forceReconnect (= the WiFi drop).
  Reproduced tonight WITHOUT text: 7 static solid segments were nuked to
  seg:[] + error:8 within ~90s on the old firmware.
- MAX_SEGMENT_DATA (FX.h, the 16.x segment-data ceiling name) is COMPILED OUT
  on PSRAM builds (#ifndef BOARD_HAS_PSRAM in FX_fcn.cpp) - raising it is a
  no-op for the M-1. The ceiling that matters is MAX_LED_MEMORY: if the bus
  memory estimate exceeds it (+1K) at re-init the bus is built as a
  PLACEHOLDER = dark panels (FX_fcn.cpp ~1264). We sat at 180224/197632.
- BONUS CRASH FOUND (repro + backtrace): WS2812FX::getLastActiveSegmentId
  does `for (size_t i = _segments.size() - 1; ...)` - with ZERO segments
  (i.e., right after the watchdog nuke) the unsigned wraps and any
  /json/state POST containing "mainseg" (the web UI sends it!) LoadProhibited-
  panics the device. Watchdog nuke -> next UI click -> reboot. Likely the old
  "multi-seg/dark-glass wedge" and maybe the earlier crash-loop too.

### Fixes applied (all in m1-wled-update)
1. bus_manager.cpp: _ledBuffer BFRALLOC_PREFER_DRAM -> BFRALLOC_PREFER_PSRAM.
   The allocator heuristic keeps small (single-panel) buffers in DRAM, spills
   big chain buffers to PSRAM. Result on glass build: freeheap 23K -> 72K,
   contiguous 64.5K (4.5x the watchdog line).
2. FX_fcn.cpp: getLastActiveSegmentId underflow guard (loop from size()).
3. platformio.ini apollo_m1: -D MAX_LED_MEMORY=262144 (placeholder-drop margin).

### Verified after OTA of the real dbg build
- 160s soak, 7 static segments: nsegs stable, error none, heap flat 71860.
- Scrolling Text 256x64 (43-char string, forced horizontal): 2min+, fx stays
  122, heap flat, fps 30-31, console clean (only "Slow strip" pacing lines).
  GLASS VERDICT PENDING JUSTIN (readability, direction, seams).
- WiFi under load during text: 40/40 pings, 0.0% loss, avg 9.7ms.
- mainseg POST on populated strip: fine (fix in build; empty-strip case now safe).

### NEW TRAP (cost us the matrix config tonight - recovered)
After ANY watchdog strip-nuke, the RAM config is DEGRADED (matrix gone from
RAM). ANY /json/cfg POST then saves that degraded state to flash - tonight an
innocent {"ota":{"same-subnet":false}} unflag-for-OTA wiped hw.led.matrix
from flash (bus line survives; it is a different path). RULE: before ANY
/json/cfg POST, check /json/state has nsegs>0 AND /json/info leds.matrix
exists; if not, REBOOT FIRST. Recovery: re-push the matrix block (four 64x64
panels at x 0/64/128/192, mpc 4), poll raw /cfg.json, reboot.

### 2x2 groundwork (Justin wants 2x2; virtual path still suspect)
- The build compiles the LEGACY ESP32-VirtualMatrixPanel-I2S-DMA.h (seen in
  build warnings), not the _T template header.
- getCoords for 1x4 TOP_RIGHT_DOWN is mathematically IDENTITY (row 0 even
  branch), yet glass showed the 16-px staircase pre-bypass - paradox not yet
  resolved; suspects: Adafruit_GFX _width bounds check (non-NO_GFX branch),
  rotation state. FOUR_SCAN remap is QS-only, not the HS culprit.
- NEXT STEP (desk-safe): extract getCoords into a host-side simulation, run
  1x4 + 2x2 cases, find the discrepancy BEFORE touching device config.
- 2x2 physical caveat: legacy chain math assumes row-2 panels are mounted
  180 degrees ROTATED (serpentine). Customer doc item.
- S3 cannot teardown the HUB75 driver at runtime (cleanup() sets
  ERR_REBOOT_NEEDED, deleting display crashes) - the "always reboot after bus
  changes" rule is structural, not superstition.

### Device state at end of session 2
- Firmware: apollo_m1_dbg WITH tonight's 3 fixes, OTA'd (first build that is
  actually the dbg env on this unit). Factory b6 on-disk artifacts are STALE
  (pre-fix) until rebuilt.
- Config on flash: verified via raw /cfg.json - bus type 65 pin [64,64,4,1,4]
  len 16384, matrix mpc4 four panels x 0/64/128/192, ota.same-subnet TRUE
  (restored after the OTA dance).
- Scrolling Text left RUNNING on glass for Justin's verdict ("APOLLO M-1 FOUR
  PANEL CHAIN TEST 0123456789", amber, sx=140).
- FS: factory b6 presets + Justin's "mypaint" still on the unit (OTA does not
  touch FS).

### Upstream findings ledger (for the report, now 7)
1. MAX_LEDS boundary uses >= (exactly-4-panel chains rejected).
2. cfg.cpp maMax div-by-zero boot loop (total saved as 0).
3. 2D width cap rejects exactly-256 (should be > 256).
4. Ledmap 32KB alloc needs PSRAM fallback at 16K pixels.
5. Virtual-path 1xN geometry scramble (bypassed in fork; host-sim pending).
6. HUB75 _ledBuffer PREFER_DRAM starves heap at chain sizes -> watchdog
   destroys segments (PREFER_PSRAM fixes; watchdog itself is also worth an
   upstream conversation - it silently eats user config).
7. getLastActiveSegmentId size_t underflow: mainseg POST on empty strip =
   LoadProhibited panic (one-line fix, clean repro, backtrace on file).
