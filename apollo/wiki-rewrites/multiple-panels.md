# Draft replacement: /products/m1/setup/m1-multiple-panels/

Editor note (not part of the page): rewritten 2026-07-12 from the D10 bench session;
2x2 grid section added 2026-07-13 after it passed on glass (probe + seam-straddling
scrolling text + GIF playback, photos in the QA record). Everything below was
verified on hardware. Requires an M-1 build that includes the D10 chain fixes
(any build after b6; check the firmware date on the info page).

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
- Frame rate at 16,384 pixels (either 256x64 or 128x128) is about 30 fps for
  most content and about 15 fps for the heaviest 2D effects, compared to 44 fps
  on the single built-in panel.
- GIF playback speed depends on how much of the image changes per frame:
  typical pixel-art animations (a sprite moving on a steady background) run
  15-25 fps; worst-case GIFs where every pixel changes every frame (plasma,
  full-screen noise) run about 8 fps. The panels themselves are refreshed by
  hardware at all times, so lower rates mean slower motion, never flicker.
- Chains longer than four panels are not supported.

## 2x2 grid (128x128 square display)

The same four panels can be arranged as a square instead of a row. The pixel
count is identical; only the arrangement and two settings change.

### Physical arrangement (facing the screens)

The chain order does not change - the same cables stay in the same ports. Take
the row and stack it:

- **Top row, mounted upright**: the 3rd panel from the controller goes top-left,
  the 4th (last) panel goes top-right.
- **Bottom row, each rotated 180 degrees in place** (spin it like a steering
  wheel - do not flip it face-to-back): the 2nd panel goes bottom-left, the 1st
  panel (the one cabled to the controller) goes bottom-right.

The cable path ends up as a serpentine: controller into the bottom-right panel,
along the bottom row, up, then along the top row. The bottom panels are upside
down on purpose - the firmware knows and draws them correctly.

### Settings (two steps, one reboot each)

1. **LED Preferences**: HUB75 Half Scan, panel size 64x64, number of panels 4,
   arrangement **2 rows x 2 columns**. Save, reboot.
2. **2D Configuration**: **one panel of 128x128** at offset 0,0. Save, reboot.

Text, effects, and images now treat the square as one 128x128 canvas. Content
crosses all four seams cleanly, including letters that straddle the horizontal
middle.

### Playing a GIF across the grid

1. Upload a GIF to the device filesystem (PixelForge at `http://<device>/pixelforge.htm`,
   or `http://<device>/edit`). A GIF sized 128x128 plays pixel-perfect; other
   sizes are scaled.
2. Set the segment name to the exact filename (for example `plasma.gif`).
3. Select the **Image** effect.
4. To keep it: save the state as a preset. To start it at power-on, set that
   preset as the boot preset in LED Preferences.
