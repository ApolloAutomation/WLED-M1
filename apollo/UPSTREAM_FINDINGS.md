# Upstream findings from the D10 four-panel chain sessions (2026-07-12)

Everything below was found while bringing a 4x 64x64 HUB75 chain (256x64,
ESP32-S3, PSRAM) up on WLED 16.0.1. Each item has a repro on record in
BENCH_SESSION_D10.md and a fix (or bypass) on the m1-wled-update branch.
Ordered by customer impact. Items 1-3 and 5-8 are candidates for upstream
issues/PRs; item 4 is insurance we would defend but not push hard.

## 1. HUB75 shadow buffer starves internal heap on chains -> watchdog destroys user state
`BusHub75Matrix` allocates its per-pixel shadow buffer (`_len * sizeof(CRGB)`,
48KB at 16384 px) with `BFRALLOC_PREFER_DRAM`. At bus-init heap is plentiful,
so the buffer lands in DRAM; combined with the DMA framebuffer this leaves
~23KB free / <14KB contiguous. The wled.cpp heap watchdog (15KB contiguous
floor) then fires its 15/30/45s ladder: forces every segment to
FX_MODE_STATIC (running effects freeze mid-frame), then resets segments,
then destroys and re-creates the strip and forces a WiFi reconnect. To the
user this presents as "effect froze, WiFi dropped, my segments vanished" -
with no error anywhere, because production builds compile the debug prints
out. Fix: allocate the shadow buffer `BFRALLOC_PREFER_PSRAM`; the allocator
heuristic keeps small (single-panel) buffers in DRAM and spills chain-sized
ones to PSRAM. Result on hardware: 23K -> 72K free, watchdog silent.
Fixed in fork: bus_manager.cpp (m1-wled-update). Suggest same one-flag
change upstream. A separate conversation: the watchdog silently eating user
segments (and, via the next item, corrupting saved config) deserves an
error surface of its own.

## 2. getLastActiveSegmentId underflows on an empty segment list -> remote-triggerable panic
`for (size_t i = _segments.size() - 1; i > 0; i--)` wraps to SIZE_MAX when
the vector is empty (exactly the state the watchdog's strip re-create
leaves behind). The next `/json/state` POST containing `"mainseg"` - which
the stock web UI sends routinely - calls `setMainSegmentId` ->
`getLastActiveSegmentId` -> wild `isActive()` read -> LoadProhibited panic
and reboot. Clean repro + decoded backtrace on file. One-line fix in fork
(FX_fcn.cpp): iterate from `size()` with `i > 1`, index `i-1`.

## 3. 2D multi-panel ledmap is panel-major; the HUB75 bus renders row-major -> geometry scramble
`setUpMatrix()` numbers pixels consecutively per panel (panel 0's WxH
pixels first, then panel 1's...). `BusHub75Matrix` maps the strip index
back to coordinates as `(i % width, i / width)` - row-major over the whole
canvas. Configure a HUB75 chain as N separate panels in the 2D page and
every non-uniform frame shreds deterministically: thin horizontal lines
fold into N stacked rows on the first panel, vertical lines repeat once per
panel, glyphs slice into per-panel fragments. (Photo-decoded on hardware;
the signature also retroactively explains this fork's earlier "virtual
layer scramble" - the virtual remap was proven identity by simulation and
was never at fault.) The only 2D layout whose mapping is identity - and
therefore correct - is ONE canvas-sized panel, which is also what WLED-MM
documented for chains. That leads directly to item 4's blocker: it was
impossible to configure. Options for upstream: translate panel-major
indices in the HUB75 bus, or document one-big-panel as the required 2D
config for HUB75 (now that item 4 makes it possible).

## 4. Panel.width/height are uint8_t -> a 256-wide panel wraps to 0 and kills the matrix
The struct fields cap per-panel dimensions at 255. A 4x64 chain needs a
256-wide single panel (see item 3), which silently becomes width 0 through
the cfg round-trip and fails the 2D bounds check, disabling the matrix.
Fixed in fork (FX.h): widen to uint16_t; cost is 4 bytes per configured
panel. The settings-page number field still visually flags >255 (JS only);
cfg.json/API accepts it.

## 5. MAX_LEDS boundary check uses >= : exactly-MAX chains rejected
4x 64x64 = 16384 = the S3 MAX_LEDS value, and the HUB75 driver guard
`if (_len >= MAX_LEDS)` rejects it. Off-by-one; a chain that IS the maximum
should work. Fork carries MAX_LEDS=16388 as a product-level pad (mirrors
WLED-MM); the upstream-shaped fix is `>`.

## 6. cfg.cpp ABL fallback divides by a total that can be saved as zero -> boot loop
The per-bus current fallback divides by `total` (sum of bus lengths), which
a save during bus teardown can legitimately persist as 0; ArduinoJson's `|`
operator evaluates the fallback expression even when the primary key
exists. Result: divide-by-zero panic on every boot = permanent boot loop
with user data intact but unreachable. Customer-reachable (any save racing
a bus re-init). Fixed in fork (guard `total > 0`); recovery documented
(erase FS region). Worth an upstream PR on its own.

## 7. setUpMatrix 2D width cap rejects exactly-256 canvases
The bounds check refused `Segment::maxWidth > 255`; a 4-panel chain is
exactly 256 wide and the maximum coordinate index (255) still fits 8-bit
storage everywhere it matters. Fixed in fork: cap moved to `> 256`
(FX_2Dfcn.cpp).

## 8. 16K-pixel ledmap needs a PSRAM fallback
`customMappingTable` for 16384 pixels is a 32KB contiguous allocation from
internal RAM, requested after the display driver has taken its buffers.
Fork adds a `p_malloc` fallback rather than silently dropping the whole 2D
configuration (FX_2Dfcn.cpp, FX_fcn.cpp).

## Library-side observations (ESP32-HUB75-MatrixPanel-DMA, not WLED)
- Legacy `ESP32-VirtualMatrixPanel-I2S-DMA.h` FOUR_SCAN_64PX_HIGH y-swizzle
  has a C precedence bug: `(y & 0b11000) ^ 0b11000 + (y & 0b11100111)`
  parses as `a ^ (b + c)`; the XOR needs braces. Affects quarter-scan
  64px-high panels only.
- Same file, FOUR_SCAN_32PX branch: un-braced `else` followed by two
  indented statements - the second executes unconditionally. Behavior is
  (accidentally) correct; the indentation is a trap for maintainers.
- On ESP32-S3 the driver cannot be deleted/re-created at runtime (DMA
  teardown crashes); WLED's bus cleanup already works around it with
  ERR_REBOOT_NEEDED. Documenting this in the lib would help downstreams.

## Additions from the AP-mode session (2026-07-14/15)

## 9. AP mode never disables WiFi modem sleep on unconfigured units
WiFi.setSleep(!noWifiSleep) is only called inside the WLED_WIFI_CONFIGURED
branch of initConnection(); a factory-fresh unit serving its setup AP keeps
the Arduino default power-save, a classic source of softAP latency/loss.
One-line fix in initAP() after setTxPower (in fork; PR-ready).

## 10. Scrolling Text: fitting text cannot scroll horizontally
mode_2Dscrollingtext centers-and-holds when totalTextWidth <= cols; check3
(Reverse) is dead code in that branch. A customer typing a short word sees
a static display. Fork change (2 lines, PR-ready): check3 also forces
horizontal scrolling for fitting text (standard right-to-left direction;
reverse still applies to overflowing text). PixelForge's text preview also
hardcoded left-to-right for any o3 - fixed to mirror the effect.

## 11. For discussion rather than a patch: captive portal vs modern phones
The AP session documented (with phone-side evidence) how the stock captive
implementation interacts with Android: the 302-on-probe marks the network
captive, the auto-popup opens Android's crippled mini-browser (no file
chooser), and typed URLs in real browsers route over cellular because the
WiFi never validates - 4.3.2.1 being a real routable Level3 address makes
this fail hard. The fork answers generate_204/hotspot-detect/connecttest
probes as if online (204/Success), which makes real browsers work with
mobile data on at the cost of the auto-popup; an on-panel QR closes the
discovery gap. Also noted: core 2.0.18 DNSServer answers AAAA/HTTPS(65)
queries with malformed A records, and the welcome page's /json/net
triggers all-channel STA scans that pull the softAP radio off-channel.

## 12. Frozen segments silently ignore effect changes (live-paint trap)
The per-pixel JSON API ("i" arrays - used by Pixel Paint and similar
tools) sets seg.freeze=true by design. Selecting a new effect afterwards
calls setMode() but leaves freeze set, so the effect never runs and the
panel keeps the frozen canvas - a black screen if the user cleared their
drawing. Nothing in the main UI hints at the frozen state. Fork fix
(json.cpp, PR-ready): an effect change clears freeze unless the same
message explicitly sets frz. Repro'd live; PixelForge only escapes the
trap because its GIF player sends frz:false explicitly.
