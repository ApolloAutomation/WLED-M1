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
