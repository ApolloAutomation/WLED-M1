#!/usr/bin/env python3
"""Generate static first-boot setup card variants for the Apollo M-1 (64x64).
Feedback-driven redesign: ONE static page, QR smaller (2px modules), the
address in text below, join instruction on top, no 'hotspot' wording.
Variants cover the QR scannability test matrix: polarity, ECC, layout.
"""
from PIL import Image
import qrcode

W = H = 64
BLACK = (0, 0, 0)
AMBER = (255, 170, 0)
SKY = (77, 166, 255)
WHITE = (255, 255, 255)

# Variable-width 5-tall caps font (rows as bit strings, 1 = lit)
F5 = {
    'A': ["010", "101", "111", "101", "101"],
    'F': ["111", "100", "110", "100", "100"],
    'I': ["1", "1", "1", "1", "1"],
    'J': ["111", "001", "001", "101", "010"],
    'L': ["100", "100", "100", "100", "111"],
    'M': ["10001", "11011", "10101", "10001", "10001"],
    'N': ["1001", "1101", "1011", "1001", "1001"],
    'O': ["010", "101", "101", "101", "010"],
    'P': ["110", "101", "110", "100", "100"],
    'W': ["10001", "10001", "10101", "11011", "10001"],
    '-': ["000", "000", "111", "000", "000"],
    ':': ["0", "1", "0", "1", "0"],
    '1': ["01", "11", "01", "01", "01"],
    ' ': ["00", "00", "00", "00", "00"],
}
# 7-tall digit font for the address line
F7 = {
    '4': ["0011", "0101", "1001", "1111", "0001", "0001", "0001"],
    '3': ["1110", "0001", "0001", "0110", "0001", "0001", "1110"],
    '2': ["0110", "1001", "0001", "0010", "0100", "1000", "1111"],
    '1': ["01", "11", "01", "01", "01", "01", "01"],
    '.': ["0", "0", "0", "0", "0", "0", "1"],
    'H': ["1001", "1001", "1001", "1111", "1001", "1001", "1001"],
    'T': ["111", "010", "010", "010", "010", "010", "010"],
    'P': ["110", "101", "101", "110", "100", "100", "100"],
    '/': ["001", "001", "010", "010", "010", "100", "100"],
    ':': ["0", "0", "1", "0", "1", "0", "0"],
}

def text_width(s, font):
    return sum(len(font[c][0]) for c in s) + (len(s) - 1)

def draw_text(px, s, font, y, color, x=None, colors=None):
    if x is None:
        x = (W - text_width(s, font)) // 2
    for i, ch in enumerate(s):
        g = font[ch]
        col = colors[i] if colors else color
        for ry, row in enumerate(g):
            for rx, bit in enumerate(row):
                if bit == '1':
                    px[x + rx, y + ry] = col
        x += len(g[0]) + 1
    return x

import qrcode.constants as qc

def build_matrix(ecc):
    q = qrcode.QRCode(version=1, error_correction=ecc, box_size=1, border=0)
    q.add_data("HTTP://4.3.2.1")
    q.make(fit=False)
    return q.get_matrix()  # list of rows of bool, 21x21

def render_qr(px, matrix, box, ox, oy, inverted):
    n = len(matrix)
    for my in range(n):
        for mx in range(n):
            dark = matrix[my][mx]
            lit = dark if inverted else (not dark)
            color = WHITE if lit else BLACK
            for dy in range(box):
                for dx in range(box):
                    px[ox + mx * box + dx, oy + my * box + dy] = color

def card_L1(ecc, inverted, fname):
    """One top line JOIN:APOLLO M-1, 42px QR, 4.3.2.1 below. 4px quiet zones."""
    im = Image.new("RGB", (W, H), BLACK)
    px = im.load()
    s = "JOIN:APOLLO M-1"
    cols = [AMBER] * 5 + [SKY] * 10
    draw_text(px, s, F5, 0, None, colors=cols)
    m = build_matrix(ecc)
    qs = 21 * 2
    ox, oy = (W - qs) // 2, 9
    if not inverted:
        # standard polarity needs a LIT quiet zone box
        for y in range(oy - 4, oy + qs + 4):
            for x in range(ox - 4, ox + qs + 4):
                px[x, y] = WHITE
    render_qr(px, m, 2, ox, oy, inverted)
    draw_text(px, "4.3.2.1", F7, 56, WHITE)
    im.save(fname)

def card_L2(ecc, fname):
    """Two top lines JOIN WIFI / APOLLO M-1, tighter quiet zones (2-3px)."""
    im = Image.new("RGB", (W, H), BLACK)
    px = im.load()
    draw_text(px, "JOIN WIFI", F5, 0, AMBER)
    draw_text(px, "APOLLO M-1", F5, 6, SKY)
    m = build_matrix(ecc)
    render_qr(px, m, 2, (W - 42) // 2, 14, True)
    draw_text(px, "4.3.2.1", F7, 57, WHITE)
    im.save(fname)

import sys
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
card_L1(qc.ERROR_CORRECT_M, True, f"{OUT}/cardA_invM.gif")
card_L1(qc.ERROR_CORRECT_Q, True, f"{OUT}/cardA_invQ.gif")
card_L1(qc.ERROR_CORRECT_M, False, f"{OUT}/cardA_stdM.gif")
card_L2(qc.ERROR_CORRECT_M, f"{OUT}/cardB_invM.gif")

# enlarged previews
for n in ["cardA_invM", "cardA_invQ", "cardA_stdM", "cardB_invM"]:
    Image.open(f"{OUT}/{n}.gif").convert("RGB").resize((256, 256), Image.NEAREST).save(f"{OUT}/view_{n}.png")
print("done")

# --- cardB2: Justin's pick (two-line header) with step numbers (2026-07-15) ---
# "1 JOIN WIFI / APOLLO M-1" then QR, then "2 SCAN  4.3.2.1".
F5.update({
    'S': ["011", "100", "010", "001", "110"],
    'C': ["011", "100", "100", "100", "011"],
    'R': ["110", "101", "110", "101", "101"],
    '2': ["110", "001", "010", "100", "111"],
    '3': ["110", "001", "010", "001", "110"],
    '4': ["101", "101", "111", "001", "001"],
    '.': ["0", "0", "0", "0", "1"],
})

def draw_mixed(px, parts, font, y):
    """parts = [(text, color), ...] rendered as one centered line."""
    s = "".join(t for t, _ in parts)
    x = (W - text_width(s, font)) // 2
    for t, col in parts:
        for ch in t:
            g = font[ch]
            for ry, row in enumerate(g):
                for rx, bit in enumerate(row):
                    if bit == '1':
                        px[x + rx, y + ry] = col
            x += len(g[0]) + 1

def card_B2(ecc, polarity, fname):
    """polarity: 'inv' (light modules on black) or 'std' (dark modules on lit box)."""
    im = Image.new("RGB", (W, H), BLACK)
    px = im.load()
    draw_mixed(px, [("1 ", WHITE), ("JOIN WIFI", AMBER)], F5, 0)
    draw_text(px, "APOLLO M-1", F5, 6, SKY)
    m = build_matrix(ecc)
    if polarity == 'std':
        for y in range(12, 58):
            for x in range(9, 55):
                px[x, y] = WHITE
        render_qr(px, m, 2, 11, 14, False)
    else:
        render_qr(px, m, 2, (W - 42) // 2, 14, True)
    draw_mixed(px, [("2 ", WHITE), ("SCAN", AMBER), (" OR ", WHITE), ("4.3.2.1", SKY)], F5, 58)
    im.save(fname)

def qr_std_full(fname):
    """Diagnostic arm: standard polarity, full lit field, 4-module quiet, no text."""
    im = Image.new("RGB", (W, H), WHITE)
    px = im.load()
    m = build_matrix(qc.ERROR_CORRECT_Q)
    render_qr(px, m, 2, 11, 11, False)
    im.save(fname)

if __name__ == "__main__":
    card_B2(qc.ERROR_CORRECT_M, 'inv', f"{OUT}/cardB2_invM.gif")
    card_B2(qc.ERROR_CORRECT_Q, 'inv', f"{OUT}/cardB2_invQ.gif")
    card_B2(qc.ERROR_CORRECT_M, 'std', f"{OUT}/cardB2_stdM.gif")
    qr_std_full(f"{OUT}/qr_std_full.gif")
    for n in ["cardB2_invM", "cardB2_invQ", "cardB2_stdM", "qr_std_full"]:
        Image.open(f"{OUT}/{n}.gif").convert("RGB").resize((256, 256), Image.NEAREST).save(f"{OUT}/view_{n}.png")
    print("cardB2 set done")

# --- cardB3 (round 3): dimmed text to protect the quiet zone + module color arms ---
def dim(c, f=0.4):
    return tuple(int(v * f) for v in c)

def card_B3(ecc, module_color, fname):
    """cardB2 layout, instruction text at 40% so it stops eating the QR quiet
    zone, QR modules in a chosen color (white or amber tested on glass)."""
    im = Image.new("RGB", (W, H), BLACK)
    px = im.load()
    draw_mixed(px, [("1 ", dim(WHITE)), ("JOIN WIFI", dim(AMBER))], F5, 0)
    draw_text(px, "APOLLO M-1", F5, 6, dim(SKY))
    m = build_matrix(ecc)
    for my in range(21):
        for mx in range(21):
            color = module_color if m[my][mx] else BLACK
            for dy in range(2):
                for dx in range(2):
                    px[11 + mx*2 + dx, 14 + my*2 + dy] = color
    draw_mixed(px, [("2 ", dim(WHITE)), ("SCAN", dim(AMBER)), (" OR ", dim(WHITE)), ("4.3.2.1", dim(SKY))], F5, 58)
    im.save(fname)

# --- cardB4 (FINAL, 2026-07-16): Justin's wording "or go to 4.3.2.1" ---
# One-line top (1 JOIN APOLLO M-1), glass-proven QR geometry (inverted 2px,
# ECC Q, 3px top / 2px bottom dark gaps, dim text), two bottom rows.
F5.update({
    'G': ["0110", "1000", "1011", "1001", "0110"],
    'T': ["111", "010", "010", "010", "010"],
})

def card_B4(fname):
    im = Image.new("RGB", (W, H), BLACK)
    px = im.load()
    draw_mixed(px, [("1 ", dim(WHITE)), ("JOIN", dim(AMBER)), (" ", dim(WHITE)), ("APOLLO M-1", dim(SKY))], F5, 0)
    m = build_matrix(qc.ERROR_CORRECT_Q)
    for my in range(21):
        for mx in range(21):
            color = WHITE if m[my][mx] else BLACK
            for dy in range(2):
                for dx in range(2):
                    px[11 + mx*2 + dx, 8 + my*2 + dy] = color
    draw_mixed(px, [("2 ", dim(WHITE)), ("SCAN", dim(AMBER)), (" OR", dim(WHITE))], F5, 52)
    draw_mixed(px, [("GO TO ", dim(AMBER)), ("4.3.2.1", dim(SKY))], F5, 58)
    im.save(fname)

# --- cardB5 (2026-07-16): Justin's step copy, thin word-spaces to fit ---
F5['~'] = ["0"]  # thin space (1px + spacing)
F5['E'] = ["111", "100", "110", "100", "111"]

def card_B5(fname):
    """1 JOIN APOLLO WIFI / QR / 2 SCAN OR / GO TO 4.3.2.1 (all dim but QR)."""
    im = Image.new("RGB", (W, H), BLACK)
    px = im.load()
    draw_mixed(px, [("1~", dim(WHITE)), ("JOIN~", dim(AMBER)), ("APOLLO~WIFI", dim(SKY))], F5, 0)
    m = build_matrix(qc.ERROR_CORRECT_Q)
    for my in range(21):
        for mx in range(21):
            color = WHITE if m[my][mx] else BLACK
            for dy in range(2):
                for dx in range(2):
                    px[11 + mx*2 + dx, 8 + my*2 + dy] = color
    draw_mixed(px, [("2 ", dim(WHITE)), ("SCAN", dim(AMBER)), (" OR", dim(WHITE))], F5, 52)
    draw_mixed(px, [("GO TO ", dim(AMBER)), ("4.3.2.1", dim(SKY))], F5, 58)
    im.save(fname)

# --- cardB6 (2026-07-16): 1px-module QR proven reliable on glass -> full copy
# STEP 1 / JOIN APOLLO WIFI / QR 21px huge quiet zone / STEP 2 SCAN /
# OR GO TO / 4.3.2.1 (big font). QR full white; text dim 0.4 (proven).
def card_B6(fname):
    im = Image.new("RGB", (W, H), BLACK)
    px = im.load()
    draw_mixed(px, [("STEP ", dim(AMBER)), ("1", dim(WHITE))], F5, 0)
    draw_mixed(px, [("JOIN APOLLO WIFI", dim(SKY))], F5, 6)
    m = build_matrix(qc.ERROR_CORRECT_Q)
    for my in range(21):
        for mx in range(21):
            if m[my][mx]:
                px[21 + mx, 17 + my] = WHITE
    draw_mixed(px, [("STEP ", dim(AMBER)), ("2", dim(WHITE)), (" SCAN", dim(AMBER))], F5, 44)
    draw_mixed(px, [("OR GO TO", dim(WHITE))], F5, 50)
    draw_text(px, "4.3.2.1", F7, 56, dim(SKY, 0.55))
    im.save(fname)

# --- cardB7 (2026-07-16): Justin's revised copy, small address font ---
F5.update({
    'H': ["101", "101", "111", "101", "101"],
    'B': ["110", "101", "110", "101", "110"],
})

def card_B7(fname):
    """STEP 1 / JOIN APOLLO / WIFI HOTSPOT / QR 21px / STEP 2 SCAN OR /
    OPEN BROWSER TO / 4.3.2.1 (small font). 4px vertical quiet zones."""
    im = Image.new("RGB", (W, H), BLACK)
    px = im.load()
    draw_mixed(px, [("STEP ", dim(AMBER)), ("1", dim(WHITE))], F5, 0)
    draw_mixed(px, [("JOIN APOLLO", dim(SKY))], F5, 6)
    draw_mixed(px, [("WIFI HOTSPOT", dim(SKY))], F5, 12)
    m = build_matrix(qc.ERROR_CORRECT_Q)
    for my in range(21):
        for mx in range(21):
            if m[my][mx]:
                px[21 + mx, 21 + my] = WHITE
    draw_mixed(px, [("STEP ", dim(AMBER)), ("2", dim(WHITE)), (" SCAN OR", dim(AMBER))], F5, 46)
    draw_mixed(px, [("OPEN BROWSER TO", dim(WHITE))], F5, 52)
    draw_mixed(px, [("4.3.2.1", dim(SKY, 0.55))], F5, 58)
    im.save(fname)

# --- cardB8 (2026-07-16): order-of-operations revision - QR moves BELOW the
# steps so nobody scans before joining; SSID shown as APOLLO M-1; THEN SCAN.
def card_B8(fname):
    im = Image.new("RGB", (W, H), BLACK)
    px = im.load()
    draw_mixed(px, [("STEP ", dim(AMBER)), ("1", dim(WHITE))], F5, 0)
    draw_mixed(px, [("JOIN APOLLO M-1", dim(SKY))], F5, 6)
    draw_mixed(px, [("WIFI HOTSPOT", dim(SKY))], F5, 12)
    draw_mixed(px, [("STEP ", dim(AMBER)), ("2", dim(WHITE)), (" THEN SCAN", dim(AMBER))], F5, 18)
    draw_mixed(px, [("OR OPEN BROWSER", dim(WHITE))], F5, 24)
    draw_mixed(px, [("TO ", dim(WHITE)), ("4.3.2.1", dim(SKY, 0.55))], F5, 30)
    m = build_matrix(qc.ERROR_CORRECT_Q)
    for my in range(21):
        for mx in range(21):
            if m[my][mx]:
                px[21 + mx, 40 + my] = WHITE
    im.save(fname)

# --- cardB9 (2026-07-16): STEP 2 / SCAN QR BELOW / OR GO TO 4.3.2.1 ---
F5['Q'] = ["0110", "1001", "1001", "1010", "0101"]

def card_B9(fname):
    im = Image.new("RGB", (W, H), BLACK)
    px = im.load()
    draw_mixed(px, [("STEP ", dim(AMBER)), ("1", dim(WHITE))], F5, 0)
    draw_mixed(px, [("JOIN APOLLO M-1", dim(SKY))], F5, 6)
    draw_mixed(px, [("WIFI HOTSPOT", dim(SKY))], F5, 12)
    draw_mixed(px, [("STEP ", dim(AMBER)), ("2", dim(WHITE))], F5, 18)
    draw_mixed(px, [("SCAN QR BELOW", dim(AMBER))], F5, 24)
    draw_mixed(px, [("OR GO TO ", dim(WHITE)), ("4.3.2.1", dim(SKY, 0.55))], F5, 30)
    m = build_matrix(qc.ERROR_CORRECT_Q)
    for my in range(21):
        for mx in range(21):
            if m[my][mx]:
                px[21 + mx, 40 + my] = WHITE
    im.save(fname)
