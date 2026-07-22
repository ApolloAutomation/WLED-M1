#!/usr/bin/env python3
"""Port of the legacy VirtualMatrixPanel::getCoords (CHAIN_TOP_RIGHT_DOWN
branch) from the vendored ESP32-VirtualMatrixPanel-I2S-DMA.h, as configured
by BusHub75Matrix for multi-row HUB75 chains (rebuilt 2026-07-16 after the
D10 sim died with its scratchpad; committed this time).
Prints which CHAIN PANEL displays which canvas quadrant and its orientation.
Config: rows=2 cols=2 panel 64x64 -> virtual 128x128, DMA chain 256x64.
"""
ROWS, COLS, PW, PH = 2, 2, 64, 64
VX, VY = COLS * PW, ROWS * PH      # 128 x 128 virtual canvas
DMARESX = PW * ROWS * COLS          # 256 wide physical chain

def get_coords(vx, vy):             # rotation 0, CHAIN_TOP_RIGHT_DOWN
    row = vy // PH
    if row % 2 == 1:                # "upside down panel" branch
        x = DMARESX - vx - (row * VX)
        y = PH - 1 - (vy % PH)
    else:
        x = ((ROWS - (row + 1)) * VX) + vx
        y = vy % PH
    return x, y

def chain_panel(dma_x):
    return dma_x // PW + 1          # 1-indexed position from the controller

quads = {"canvas TOP-LEFT": (16, 16), "canvas TOP-RIGHT": (112, 16),
         "canvas BOT-LEFT": (16, 112), "canvas BOT-RIGHT": (112, 112)}
print(f"{'canvas quadrant':>18} -> chain panel, orientation")
for name, (cx, cy) in quads.items():
    x0, y0 = get_coords(cx, cy)
    xr, yr = get_coords(cx + 1, cy)   # +x direction on canvas
    xd, yd = get_coords(cx, cy + 1)   # +y direction on canvas
    upright = (xr - x0, yr - y0) == (1, 0) and (xd - x0, yd - y0) == (0, 1)
    rot180 = (xr - x0, yr - y0) == (-1, 0) and (xd - x0, yd - y0) == (0, -1)
    o = "UPRIGHT" if upright else ("ROTATED 180" if rot180 else "OTHER")
    print(f"{name:>18} -> chain panel {chain_panel(x0)}, {o}")
# sanity: bijective?
seen = set()
for vy in range(VY):
    for vx in range(VX):
        c = get_coords(vx, vy)
        assert 0 <= c[1] < PH, c
        seen.add(c)
print("mapped DMA x range:", min(s[0] for s in seen), "-", max(s[0] for s in seen),
      "| unique cells:", len(seen), "of", VX * VY)
