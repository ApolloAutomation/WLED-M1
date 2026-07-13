# Draft replacement: /products/m1/setup/m1-multiple-panels/

Editor note (not part of the page): rewritten 2026-07-12 from the D10 bench session.
The old page's guidance predates firmware 16.0.1 and the chain fixes. Everything
below was verified on glass on a four-panel rig (photos in the QA record). Requires
an M-1 build that includes the D10 chain fixes (any build after b6; check the
firmware date on the info page). Grid layouts (2x2) are not yet supported on this
page's firmware - do not fold the old grid speculation back in.

---

## Driving multiple panels with the M-1

The M-1 can drive a chain of up to four 64x64 panels (a 256x64 display) using the
same HUB75 connector that feeds its built-in panel. You need:

- Panels that match the M-1's own: 64x64, half-scan (1/32). Panels sold as
  "indoor P2.5/P3 64x64" usually qualify; quarter-scan "outdoor" panels do not.
- A 5V supply sized for the whole chain. Four panels showing bright content can
  draw over 12A; do not power a chain from USB.
- HUB75 ribbon cables between panels.

### Cabling

Connect the M-1 to the panel on the **right end** of the row (as you face the
screens), then chain each panel's output to the input of the panel on its left.
With this orientation, text and images read naturally with no extra settings. All
panels mount right side up.

### Settings (two steps, one reboot each)

1. **LED Preferences**: set the HUB75 output to Half Scan, panel size 64x64,
   number of panels 4, arrangement 1 row x 4 columns. Save and let the unit
   reboot.
2. **2D Configuration**: set **one panel of 256x64** at offset 0,0 - not four
   64x64 panels. The single wide panel is what tells the effects engine to treat
   the chain as one continuous canvas. Save and reboot again.

After the second reboot the full 256x64 display works: solid colors, 2D effects,
scrolling text, and Pixel Paint content all span the four panels continuously.

### If the picture looks wrong

- **Content repeats on every panel, or thin lines break into short dashes**: the
  2D Configuration lists four separate panels. Change it to one 256x64 panel and
  reboot.
- **One panel's worth of content is tiled and squashed across the chain**: the 2D
  Configuration still shows the single-panel 64x64 layout. Set one 256x64 panel
  and reboot.
- **The 2D page will not accept 256 in the width field**: the firmware predates
  the chain fixes. Update from the installer, then set the 2D layout.
- **Nothing shows after changing settings**: power-cycle the unit. The display
  driver cannot reconfigure itself live; every LED or 2D settings change needs a
  reboot to take effect cleanly.

### Good to know

- The LED memory gauge on the LED Preferences page reads high with four panels.
  That is expected on current firmware and does not cause instability.
- Frame rate at 256x64 is about 30 fps for most content and about 15 fps for the
  heaviest 2D effects, compared to 44 fps on the single built-in panel.
- Chains longer than four panels and grid arrangements (for example 2x2) are not
  supported yet. The 2x2 layout is under active work.
