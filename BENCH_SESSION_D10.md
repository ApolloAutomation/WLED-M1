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
### STEP 2 SUPERSEDED 2026-07-12 SESSION 2 PART 2 - SEE BELOW. Correct 2D
### config is ONE 256x64 panel (exactly like WLED-MM), enabled by the
### Panel uint16 fix. "Four 64s" produces a panel-major ledmap that the
### HUB75 bus renders scrambled (glass-proven, photo-decoded).
1. LED settings (UI or API): HUB75 (Half Scan), Panel 64x64, No. of Panels 4,
   rows x cols = 1 x 4. Save, REBOOT. (Slots = pin [64,64,4,1,4].)
2. [SUPERSEDED - DO NOT USE] 2D Configuration: FOUR panels of 64x64 at X
   offsets 0/64/128/192, Y 0. (Old rationale: per-panel dims were 8-bit.
   That was the actual BUG, now fixed - dims widened to uint16.)
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

### 2x2 groundwork (Justin wants 2x2) - HOST SIM DONE, path looks viable
- The build compiles the LEGACY ESP32-VirtualMatrixPanel-I2S-DMA.h (seen in
  build warnings), not the _T template header.
- HOST SIMULATION (scratchpad virtual_sim.py, full port of getCoords incl.
  FOUR_SCAN): 1x4 TOP_RIGHT_DOWN is IDENTITY over the entire 256x64 canvas.
  PROVEN. The pre-bypass staircase CANNOT have come from this math with a
  type-65 bus. Revised suspect for the historic scramble: type-66 (QS)
  residue during that test - QS reshapes mxconfig to 128x32 AND applies
  FOUR_SCAN_64PX_HIGH, whose remap = per-64px x-displacement + 8/16-row
  y-swizzle = exactly the observed staircase + dashes. (Same night the flash
  was later found holding type 66 "WRONG, revert to 65".) The direct-drive
  bypass stays: fewer layers, field-proven architecture.
- 2x2 SIM RESULT (rows=2, cols=2, canvas 128x128): mapping is BIJECTIVE.
  Canvas top row -> chain panels 2,3 upright; canvas bottom row -> panels
  1,0 x-reversed AND y-inverted (= physically mounted 180 deg rotated).
  Cabling for customers: controller into BOTTOM-RIGHT panel, chain runs left
  along the bottom row (both bottom panels upside down), then up to top-left,
  then right along the top row. Config: pins [64,64,4,2,2], 2D four 64x64
  panels at (0,0)(64,0)(0,64)(64,64), canvas 128x128.
  Decent odds 2x2 works as-is on a cleanly-typed 65 bus; bench-verify with
  the F-probe segments before content tests.
- Upstream lib quirks found by inspection (four-scan path, QS-only, report
  to mrfaptastic lib): (1) FOUR_SCAN_64PX_HIGH y-swizzle line has a C
  precedence bug - '(y & 0b11000) ^ 0b11000 + (y & 0b11100111)' parses as
  'a ^ (b + c)', braces missing around the XOR; (2) un-braced else with two
  indented statements right below it (32PX branch) - works but lies.
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
5. Virtual-path 1xN scramble: host-sim PROVES legacy getCoords is identity
   for 1xN/type-65; historic staircase re-attributed to QS(66) residue +
   FOUR_SCAN remap. Downgraded from upstream bug to config-trap documentation
   (plus the two four-scan lib quirks below).
6. HUB75 _ledBuffer PREFER_DRAM starves heap at chain sizes -> watchdog
   destroys segments (PREFER_PSRAM fixes; watchdog itself is also worth an
   upstream conversation - it silently eats user config).
7. getLastActiveSegmentId size_t underflow: mainseg POST on empty strip =
   LoadProhibited panic (one-line fix, clean repro, backtrace on file).

## SESSION 2, PART 2 (2026-07-12 ~23:00): JUSTIN'S PHOTOS DECODE THE LAST SCRAMBLE

### What the glass showed (probe frame photo, 23:03)
F repeated on ALL FOUR panels (squashed), red x=100 line repeated on all four
at local x=36, the 256-wide green y=40 line FOLDED into four 64px rows
stacked 16px apart on the leftmost panel, white (250,60) dot at leftmost
panel bottom. Every element fits ONE mapping exactly:
   glass = customMappingTable is PANEL-MAJOR, HUB75 bus blit is ROW-MAJOR.

### Root cause (source-proven)
- setUpMatrix (FX_2Dfcn.cpp ~107-120) numbers pixels consecutively PER PANEL:
  four 64x64 panels in a row -> table[y*256+x] = (x/64)*4096 + y*64 + x%64.
- BusHub75Matrix show() blits strip index i -> (i%256, i/256): ROW-MAJOR.
- The ONLY 2D config whose ledmap is identity (matching the bus) is ONE
  256x64 panel - EXACTLY WLED-MM's documented cure. It was impossible on
  upstream because Panel.width/height are uint8_t (256 wraps to 0, bounds
  error kills the matrix). THAT is the real "8-bit panel dims" issue; the
  red UI field was just its shadow.
- FIX: FX.h Panel width/height -> uint16_t. One 256x64 panel now configures,
  survives cfg round-trip (verified in raw /cfg.json), ledmap is identity.
- This ALSO re-explains the ENTIRE historic pre-bypass scramble: "staircase
  stepping down 16px per 64px of x, 16px dashes every 64px, mirrored" is the
  panel-major signature (it lives ABOVE the bus layer, so it hit virtual and
  direct modes identically; the direct-drive bypass never actually fixed it -
  organic DNA just hid it, and the QS-residue theory from part 1 is retired).
  The virtual layer was innocent all along (host-sim already proved identity).

### New recipe (wiki-ready, replaces the superseded step 2)
1. LED prefs: HUB75 HS, pins [64,64,4,1,4]. Save, reboot.
2. 2D config: ONE panel, 256x64, offsets 0,0 (via API/cfg.json; the settings
   UI number field may still visually clamp at 255 - JS only, note for wiki
   or a later UI tweak).
3. Reboot after any matrix/bus change (S3 cannot re-init HUB75 live).
If text/content is MIRRORED on glass: set the single panel's "r" (rightStart)
flag true instead of re-cabling - no code change needed.

### Verified tonight on the new config (engine side)
fx 122 stable, fps 30-31, heap flat 72104/64500, serial clean, 45s+ soak.
GLASS VERDICT PENDING JUSTIN: text should now read as ONE continuous line
scrolling right-to-left across all four panels, no bands, no repeats.
Old split-text video frame archived (scratchpad video_frame1.png): four
glyph fragments spaced exactly 64px = one per panel + folded band = the
panel-major signature, kept for the upstream report.

### Upstream findings ledger: item 8 (and 5 rewritten again)
5. (final form) Historic 1xN "virtual-path scramble" = panel-major ledmap vs
   row-major HUB75 bus, NOT the virtual layer (host-sim: identity; glass
   photos + source: panel-major). Direct-drive bypass kept for simplicity
   but was never the fix.
8. Panel.width/height uint8_t forbids >255 panels, blocking the only correct
   2D config for HUB75 chains (one WxH panel). Widen to uint16_t. Combined
   with 5: either HUB75 bus should translate panel-major indices, or docs
   must mandate the one-big-panel 2D config for HUB75 chains.

### Device state at end of part 2
apollo_m1_dbg + uint16-panel fix OTA'd; flash cfg: bus 65 [64,64,4,1,4],
matrix mpc1 ONE 256x64 panel, same-subnet true. Scrolling Text left running.
Prod artifacts rebuilt AFTER this fix (see git log). FS untouched.

### GLASS PASS (2026-07-12 23:31, Justin's photo + video)
"APOLLO M-1 FOUR PANEL CHAIN" = ONE continuous readable line across all four
panels, correct reading order with the controller cabled far right (no
mirror/rightStart flag needed), clean seams, smooth scroll. THE D10
DEFINITIVE TEST IS CLOSED. The historic "panel order MIRRORED" observation
retires with the panel-major scramble that produced it. Reading-order doc
answer for the wiki: cable the controller to the RIGHT end of the row (as
the M-1 demo rig is built) and text reads naturally; no 2D flags needed.

## SESSION 2, PART 3 (2026-07-12 23:35+): 2x2 GRID EXPERIMENT
- Config applied and verified on flash: pins [64,64,4,2,2], 2D ONE 128x128
  panel (mpc1). Boot clean: canvas 128x128, virtual path active, fps 30,
  heap 72K/63K - the uint16-panel + one-panel-ledmap recipe carries over.
- Quadrant probe (4 corner boxes + F + center cross) on the STILL-1x4 row:
  Justin's 23:44 photo matches the host-sim prediction on every element,
  including the split cross halves at the 1/2 and 3/4 seams. The legacy
  VirtualMatrixPanel serpentine math is CORRECT on hardware.
- Physical re-rack instructions issued: top row = chain panels 2,3 upright;
  bottom row = panels 1,0 rotated 180; cabling unchanged (controller into
  bottom-right). Awaiting on-glass grid verdict, then 128x128 text.

### 2x2 GLASS PASS (2026-07-13 ~00:00, Justin's photos)
- Re-racked grid: quadrant boxes upright in all four corners, F readable,
  center cross joined -> serpentine mapping correct on glass.
- Scrolling text on 128x128: letters cross the horizontal mid-seam INTACT
  (top half on upright panels, bottom half on 180-rotated panels) and the
  vertical seam cleanly. 31 fps, heap flat. 2x2 GRID WORKS.
- GIF playback: generated 48-frame seamless-loop 128x128 rainbow plasma
  (scratchpad plasma.gif, 762KB), uploaded to FS via /upload, played with
  the Image effect (fx 53, segment name = filename). Fills all four panels,
  seams invisible. Effective ~7 fps (CPU-bound LZW decode + 16K px/frame
  pipeline) - GIF-path optimization is a known follow-up, NOT a regression
  (chain fps unchanged before/after the PSRAM fix: 28-30 then, 30-31 now).
- Saved: preset 4 "Plasma 2x2" (factory presets 1-3 untouched). 2x2 config
  on flash (pins [64,64,4,2,2], 2D one 128x128 panel).
- Wiki: multiple-panels.md now includes the full 2x2 recipe + GIF how-to.

### GIF-path optimization + performance model (2026-07-13 ~00:30)
- image_loader.cpp changes: (1) whole GIF file cached in PSRAM at open when
  room allows (kills per-frame LittleFS streaming; falls back to streaming),
  (2) exact-fit 2D GIFs draw via setPixelColorXY instead of the 1D-index
  expansion. Guarded for non-PSRAM builds (p_malloc aliases).
- Honest measurements on 128x128 (debug console "Slow strip/effects" lines):
  full-frame-change GIF (plasma) 7 -> 8 fps; effect stage 47ms, downstream
  blend+bus+DMA-pack 66ms. Sparse-change GIF (bounce.gif, ~300 px/frame):
  18 fps. Text ~31 fps (sparse). Conclusion: throughput scales with CHANGED
  pixels/frame through the 16.x per-pixel blend pipeline; that pipeline has
  no single-opaque-segment fast path (verified in blendSegment source) -
  that is the real upstream optimization target, out of bench scope.
- FS now holds plasma.gif (762KB, worst-case demo) and bounce.gif (7KB,
  sparse demo). Preset 4 "Plasma 2x2" restored as live state.
- Tool pages verified serving on the 2x2 config: /pixelforge.htm 200,
  /pixelpaint.htm 200, /edit 200. Scrolling Text glass-verified on both
  chain setups. Pixel Paint caveat: paints the LIVE canvas; presets painted
  on a different canvas (old "mypaint") need repainting after geometry
  changes.
