# Upstream PR draft (prepared, NOT opened)

Branch: hub75-first-boot-defaults (single commit 42c58077 off upstream main c7d41a8e,
pushed to ApolloAutomation/WLED-M1). Target: Aircoookie/WLED main.

Note on scope: the original plan was an APOLLO_M1_PINOUT bus_manager.cpp block, but
the Apollo M-1 pinout already exists upstream as MOONHUB_S3_PINOUT with identical
GPIOs, so there is nothing to add there. The genuinely missing piece for the M-1 (and
for every fixed-geometry HUB75 product) is a working zero-configuration first boot.
That is what this PR fixes.

## Suggested PR title
Fix HUB75 first-boot defaults: honor config slots, seed default 2D panel

## Suggested PR description

### What this does
Makes it possible for a HUB75 build to boot into a working, correctly sized panel on
a completely fresh filesystem, with no user configuration.

Two changes in wled00/cfg.cpp, both no-ops for existing configs:

1. Skip GPIO sanitization for HUB75 bus types in the first-boot default-bus path.
   For HUB75, the five pin slots carry config values (panel width, panel height,
   chain length, grid rows, grid cols), not GPIOs. The sanitize loop treated a panel
   width of 64 as an invalid GPIO and rewrote it, so the default bus never came up
   usable. validatePinsAndTypes() already has this exact carve-out for the
   compile-time assert; this applies the same rule at runtime.

2. Optional DEFAULT_PANEL_WIDTH / DEFAULT_PANEL_HEIGHT defines. When both are set,
   a fresh install (no LED config present at all) seeds strip.panel with one panel of
   that size and sets isMatrix, so the 2D layout matches the default bus. Without the
   defines, behavior is unchanged. Once any LED config exists, the seed never runs.

Also adds a comment in the [hub75] common section documenting the pattern:

    -D DATA_PINS=64,64,1,1,1
    -D DEFAULT_PANEL_WIDTH=64 -D DEFAULT_PANEL_HEIGHT=64

### Why
Vendors shipping fixed-geometry HUB75 products need first boot to light the panel at
native size. Today a fresh device boots with no bus at all (or, if DATA_PINS is set,
with mangled values), which reads as dead hardware to end users. This was noted in
66069245, which removed the then-broken LED_TYPES=65 + DATA_PINS=64,64,1 sample lines;
those lines were also missing the two grid slots (HUB75 uses 5), which is part of why
they never worked. With this fix the pattern works and is documented.

We (Apollo Automation) ship the M-1, a 64x64 HUB75 matrix on the MOONHUB_S3_PINOUT /
esp32s3dev_16MB_opi_hub75 target, and this is the only change we need on top of
mainline to boot it zero-config.

### Testing
- Compiles clean on an esp32s3dev_16MB_opi_hub75-based env with
  LED_TYPES=TYPE_HUB75MATRIX_HS, DATA_PINS=64,64,1,1,1,
  DEFAULT_PANEL_WIDTH/HEIGHT=64 (and without the new defines).
- Code-path analysis: seed only runs when hw.led.ins is absent AND both defines are
  set; the sanitize skip mirrors the existing validatePinsAndTypes() carve-out.
- IMPORTANT before opening: run the hardware pass on an M-1 (factory erase, flash,
  confirm /json/cfg shows type 65 with pins [64,64,1,1,1] and a lit 64x64 panel).
  This session was build-only; do not submit the PR with untested claims.

## How to open it later
The branch is already pushed to ApolloAutomation/WLED-M1, which GitHub knows as a
fork of wled/WLED, so the PR can be opened directly from
ApolloAutomation/WLED-M1:hub75-first-boot-defaults against wled/WLED main. Do not
open it from automation; a maintainer conversation about define naming
(DEFAULT_PANEL_* vs WLED_*) is likely and worth having a human in the loop for.
