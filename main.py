#!/usr/bin/env python3
"""Sum up 18 November 2026 world news in one image.

make.fun bounty news-image-20261118.
Python 3.13, standard library only, no network, deterministic.
Writes a 1024x1024 PNG newspaper front page to /output/entry.png
(or output/entry.png when /output does not exist).

The news facts are embedded (researched 18 Nov 2026):
- Xi Jinping and Vladimir Putin met in Shenzhen ahead of trilateral
  talks with Donald Trump.
- US strikes on a missile site on Iran's Qeshm Island; Iran launched
  drones at Bahrain and Kuwait.
- Ukraine hit the Kerch (Crimea) Bridge; one arch collapsed into the strait.
- Democrat Mary Peltola beat Dan Sullivan in Alaska; Democrats 56-44 Senate.
- Ebola in DR Congo: about 3 in 4 children under 5 infected do not survive.
- US loses measles-free status after 26 years; 5,400+ cases, 10 deaths.
- Russian An-12 military plane crashed near Kemerovo, Siberia: 19 dead.
- Gaza: cold kills in displacement tents; ceasefire at risk.
- Markets fell: S&P 500 -1.03%, DAX -2.08%, gold USD 3,775, Brent USD 91.55.
- Waymo suspended driverless rides on US highways.
Rendering is a pure-Python rasteriser with an embedded 5x7 bitmap font,
so the program needs no external files, fonts or packages.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# --- colours ---
WHITE = (255, 255, 255)
PAPER = (252, 250, 244)
BLACK = (18, 18, 18)
GREY = (90, 90, 90)
LIGHT = (230, 228, 220)
RED = (178, 34, 34)
NAVY = (22, 48, 88)
GOLD = (201, 162, 39)
SKY = (173, 205, 230)
SEA = (46, 92, 128)
GREEN = (46, 110, 70)

# --- 5x7 bitmap font: each glyph is 7 strings of 5 chars, # = on ---
def _g(s):
    return [row.replace(".", "0").replace("#", "1") for row in s.split("|")]

FONT = {}
_upper = {
 "A": "01110|10001|10001|11111|10001|10001|10001",
 "B": "11110|10001|10001|11110|10001|10001|11110",
 "C": "01110|10001|10000|10000|10000|10001|01110",
 "D": "11110|10001|10001|10001|10001|10001|11110",
 "E": "11111|10000|10000|11110|10000|10000|11111",
 "F": "11111|10000|10000|11110|10000|10000|10000",
 "G": "01110|10001|10000|10111|10001|10001|01111",
 "H": "10001|10001|10001|11111|10001|10001|10001",
 "I": "01110|00100|00100|00100|00100|00100|01110",
 "J": "00111|00010|00010|00010|00010|10010|01100",
 "K": "10001|10010|10100|11000|10100|10010|10001",
 "L": "10000|10000|10000|10000|10000|10000|11111",
 "M": "10001|11011|10101|10101|10001|10001|10001",
 "N": "10001|11001|10101|10011|10001|10001|10001",
 "O": "01110|10001|10001|10001|10001|10001|01110",
 "P": "11110|10001|10001|11110|10000|10000|10000",
 "Q": "01110|10001|10001|10001|10101|10010|01101",
 "R": "11110|10001|10001|11110|10100|10010|10001",
 "S": "01111|10000|10000|01110|00001|00001|11110",
 "T": "11111|00100|00100|00100|00100|00100|00100",
 "U": "10001|10001|10001|10001|10001|10001|01110",
 "V": "10001|10001|10001|10001|10001|01010|00100",
 "W": "10001|10001|10001|10101|10101|11011|10001",
 "X": "10001|10001|01010|00100|01010|10001|10001",
 "Y": "10001|10001|01010|00100|00100|00100|00100",
 "Z": "11111|00001|00010|00100|01000|10000|11111",
}
_lower = {
 "a": "00000|00000|01110|00001|01111|10001|01111",
 "b": "10000|10000|11110|10001|10001|10001|11110",
 "c": "00000|00000|01110|10000|10000|10001|01110",
 "d": "00001|00001|01111|10001|10001|10001|01111",
 "e": "00000|00000|01110|10001|11111|10000|01110",
 "f": "00110|01001|01000|11110|01000|01000|01000",
 "g": "00000|01111|10001|10001|01111|00001|01110",
 "h": "10000|10000|11110|10001|10001|10001|10001",
 "i": "00100|00000|01100|00100|00100|00100|01110",
 "j": "00010|00000|00110|00010|00010|10010|01100",
 "k": "10000|10000|10010|10100|11000|10100|10010",
 "l": "01100|00100|00100|00100|00100|00100|01110",
 "m": "00000|00000|11010|10101|10101|10101|10101",
 "n": "00000|00000|11110|10001|10001|10001|10001",
 "o": "00000|00000|01110|10001|10001|10001|01110",
 "p": "00000|11110|10001|10001|11110|10000|10000",
 "q": "00000|00000|01111|10001|10001|01111|00001",
 "r": "00000|00000|10110|11001|10000|10000|10000",
 "s": "00000|00000|01111|10000|01110|00001|11110",
 "t": "01000|01000|11100|01000|01000|01001|00110",
 "u": "00000|00000|10001|10001|10001|10011|01101",
 "v": "00000|00000|10001|10001|10001|01010|00100",
 "w": "00000|00000|10001|10101|10101|10101|01010",
 "x": "00000|00000|10001|01010|00100|01010|10001",
 "y": "00000|00000|10001|10001|01111|00001|01110",
 "z": "00000|00000|11111|00010|00100|01000|11111",
}
_digits = {
 "0": "01110|10001|10011|10101|11001|10001|01110",
 "1": "00100|01100|00100|00100|00100|00100|01110",
 "2": "01110|10001|00001|00110|01000|10000|11111",
 "3": "11111|00010|00100|00010|00001|10001|01110",
 "4": "00010|00110|01010|10010|11111|00010|00010",
 "5": "11111|10000|11110|00001|00001|10001|01110",
 "6": "00110|01000|10000|11110|10001|10001|01110",
 "7": "11111|00001|00010|00100|01000|01000|01000",
 "8": "01110|10001|10001|01110|10001|10001|01110",
 "9": "01110|10001|10001|01111|00001|00010|01100",
}
_punct = {
 " ": "00000|00000|00000|00000|00000|00000|00000",
 ".": "00000|00000|00000|00000|00000|01100|01100",
 ",": "00000|00000|00000|00000|01100|00100|01000",
 ":": "00000|01100|01100|00000|01100|01100|00000",
 ";": "00000|01100|01100|00000|01100|00100|01000",
 "'": "00100|00100|01000|00000|00000|00000|00000",
 '"': "01010|01010|00000|00000|00000|00000|00000",
 "-": "00000|00000|00000|01110|00000|00000|00000",
 "(": "00010|00100|01000|01000|01000|00100|00010",
 ")": "01000|00100|00010|00010|00010|00100|01000",
 "?": "01110|10001|00001|00110|00100|00000|00100",
 "!": "00100|00100|00100|00100|00100|00000|00100",
 "/": "00001|00010|00010|00100|01000|01000|10000",
 "+": "00000|00100|00100|01110|00100|00100|00000",
 "=": "00000|00000|11111|00000|11111|00000|00000",
 "$": "00100|01111|10100|01110|00101|11110|00100",
 "%": "11001|11010|00010|00100|01000|01011|10011",
}
for _d in (_upper, _lower, _digits, _punct):
    for _k, _v in _d.items():
        FONT[_k] = _g(_v)

# --- canvas ---
canvas = bytearray(PAPER * W * H)

def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        canvas[i], canvas[i + 1], canvas[i + 2] = c

def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, c)

def hline(x, y, w, c):
    rect(x, y, w, 1, c)

def vline(x, y, h, c):
    rect(x, y, 1, h, c)

def circle(cx, cy, r, c, fill=True):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = (xx - cx) ** 2 + (yy - cy) ** 2
            if fill and d <= r * r:
                px(xx, yy, c)
            elif not fill and abs(d - r * r) <= r:
                px(xx, yy, c)

def line(x0, y0, x1, y1, c):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        px(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)

def text(x, y, s, scale, c):
    """Draw text, return width in px. scale = pixel size of one font dot."""
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for r, row in enumerate(glyph):
            for col, bit in enumerate(row):
                if bit == "1":
                    rect(cx + col * scale, y + r * scale, scale, scale, c)
        cx += 6 * scale
    return cx - x

def text_w(s, scale):
    return len(s) * 6 * scale

def wrap(s, max_w, scale):
    words = s.split(" ")
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if text_w(t, scale) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

def para(x, y, s, max_w, scale, c, lh=None):
    lh = lh or (9 * scale)
    for ln in wrap(s, max_w, scale):
        text(x, y, ln, scale, c)
        y += lh
    return y

def kicker(x, y, s, c=RED):
    return text(x, y, s, 2, c)

def headline(x, y, s, max_w, scale=3):
    yy = y
    for ln in wrap(s, max_w, scale):
        text(x, yy, ln, scale, BLACK)
        yy += 10 * scale
    return yy

# --- illustrations (one per story, drawn, no photos) ---
def ill_summit(x, y, w, h):
    rect(x, y, w, h, SKY)
    circle(x + w - 70, y + 34, 22, GOLD)
    # skyline
    for i, bh in enumerate((50, 80, 65, 95, 70, 85, 55)):
        bx = x + 14 + i * 52
        rect(bx, y + h - 40 - bh, 40, bh + 40, NAVY)
        for wy in range(y + h - 34 - bh, y + h - 44, 14):
            for wx in range(bx + 6, bx + 34, 12):
                rect(wx, wy, 5, 6, GOLD)
    # ground
    rect(x, y + h - 40, w, 40, (60, 60, 60))
    # three flags on poles
    flags = [(RED, None), (WHITE, (180, 40, 40)), (NAVY, None)]
    for i, (c1, c2) in enumerate(flags):
        fx = x + 30 + i * 62
        vline(fx, y + h - 110, 70, BLACK)
        rect(fx, y + h - 110, 44, 26, c1)
        if c2:
            rect(fx, y + h - 110, 44, 9, c2)
            rect(fx, y + h - 92, 44, 8, WHITE)
        else:
            # stars / stripes hint
            for sx in range(fx + 5, fx + 40, 10):
                rect(sx, y + h - 106, 3, 3, WHITE)

def ill_gulf(x, y, w, h):
    rect(x, y, w, h, (28, 38, 58))
    circle(x + w - 60, y + 30, 20, (230, 230, 220))
    rect(x, y + h // 2, w, h // 2, SEA)
    for wx in range(x + 10, x + w - 10, 34):
        hline(wx, y + h // 2 + 18 + (wx % 3) * 8, 20, (120, 170, 210))
    # drone silhouette
    cx, cy = x + w // 3, y + 46
    rect(cx - 26, cy - 4, 52, 8, BLACK)
    rect(cx - 8, cy - 14, 16, 10, BLACK)
    circle(cx - 28, cy, 7, BLACK)
    circle(cx + 28, cy, 7, BLACK)
    # flare / smoke
    circle(x + 2 * w // 3, y + h - 52, 26, (220, 120, 40))
    circle(x + 2 * w // 3, y + h - 66, 16, (240, 180, 60))

def ill_bridge(x, y, w, h):
    rect(x, y, w, h, SKY)
    rect(x, y + h - 52, w, 52, SEA)
    # bridge deck left and right, middle arch fallen
    rect(x, y + 78, w // 2 - 30, 10, (90, 90, 90))
    rect(x + w // 2 + 30, y + 78, w // 2 - 30, 10, (90, 90, 90))
    # fallen arch in water, tilted
    line(x + w // 2 - 28, y + 82, x + w // 2 + 10, y + h - 30, (70, 70, 70))
    line(x + w // 2 + 28, y + 82, x + w // 2 - 6, y + h - 26, (70, 70, 70))
    for px_ in range(x + 12, x + w - 12, 22):
        vline(px_, y + 48, 30, (110, 110, 110))
    circle(x + 40, y + 30, 16, GOLD)

def ill_senate(x, y, w, h):
    rect(x, y, w, h, (238, 236, 228))
    # capitol dome
    rect(x + w // 2 - 70, y + h - 46, 140, 46, WHITE)
    circle(x + w // 2, y + h - 62, 34, WHITE)
    rect(x + w // 2 - 4, y + h - 106, 8, 18, BLACK)
    for cx in range(x + w // 2 - 56, x + w // 2 + 60, 20):
        rect(cx, y + h - 38, 8, 26, NAVY)
    rect(x, y + h - 12, w, 12, GREEN)

def ill_ebola(x, y, w, h):
    rect(x, y, w, h, (245, 225, 225))
    cx, cy = x + w // 2, y + h // 2
    for a in range(0, 360, 30):
        import math
        dx = int(34 * math.cos(math.radians(a)))
        dy = int(34 * math.sin(math.radians(a)))
        line(cx, cy, cx + dx, cy + dy, RED)
        circle(cx + dx, cy + dy, 4, RED)
    circle(cx, cy, 26, RED)
    circle(cx - 8, cy - 6, 6, (255, 180, 180))
    circle(cx + 9, cy + 7, 5, (255, 180, 180))

def ill_health(x, y, w, h):
    # small icons row: plane, mask/virus, tent, car — used in IN BRIEF
    rect(x, y, w, h, PAPER)

def draw_plane(x, y, s, c):
    rect(x, y + s // 2, s, s // 6, c)
    rect(x + s // 3, y, s // 6, s, c)
    line(x, y + s, x + s, y + s // 3, c)

def draw_tent(x, y, s, c):
    line(x, y + s, x + s // 2, y, c)
    line(x + s // 2, y, x + s, y + s, c)
    hline(x, y + s, s, c)

def draw_car(x, y, s, c):
    rect(x, y + s // 2, s, s // 3, c)
    rect(x + s // 4, y + s // 6, s // 2, s // 3, c)
    circle(x + s // 4, y + s - 4, 5, BLACK)
    circle(x + 3 * s // 4, y + s - 4, 5, BLACK)

# --- page layout ---
rect(0, 0, W, H, PAPER)
# top rules
hline(24, 18, W - 48, BLACK)
hline(24, 22, W - 48, BLACK)

# masthead
title = "THE WORLD TODAY"
tw = text_w(title, 5)
text((W - tw) // 2, 36, title, 5, BLACK)
hline(24, 92, W - 48, RED)
hline(24, 96, W - 48, RED)
sub = "WEDNESDAY, 18 NOVEMBER 2026  |  NO. 18  |  PAGE 1"
text((W - text_w(sub, 2)) // 2, 108, sub, 2, BLACK)
hline(24, 128, W - 48, BLACK)

# LEAD (left, 620 wide)
lx, lw = 24, 620
kicker(lx, 142, "SUMMIT EVE  -  SHENZHEN")
y = headline(lx, 162, "XI AND PUTIN MEET BEFORE TRUMP TALKS", lw, 3)
ill_summit(lx, y + 8, lw, 150)
y = y + 8 + 150 + 12
y = para(lx, y,
    "Xi Jinping and Vladimir Putin met in Shenzhen ahead of a trilateral "
    "summit with Donald Trump. The two leaders pledged to defend a "
    "multipolar world and denounced protectionism and Western sanctions.",
    lw, 2, BLACK)
y = para(lx, y + 4,
    "Xi called for open trade at the APEC gathering. Europe fears Ukraine "
    "could be discussed without Kyiv.",
    lw, 2, GREY)

# RIGHT column (x 668, 332 wide)
rx, rw = 668, 332
kicker(rx, 142, "UNITED STATES  -  SENATE 56-44")
y2 = headline(rx, 162, "PELTOLA WINS ALASKA AS DEMOCRATS TAKE SENATE", rw, 2)
ill_senate(rx, y2 + 8, rw, 100)
y2 = y2 + 8 + 100 + 10
y2 = para(rx, y2,
    "Democrat Mary Peltola beat Republican Dan Sullivan in Alaska. "
    "Democrats will hold 56 seats to 44 for Republicans.",
    rw, 2, BLACK)
hline(rx, y2 + 8, rw, BLACK)
kicker(rx, y2 + 18, "HEALTH  -  DR CONGO")
y2 = headline(rx, y2 + 36, "EBOLA HITS CHILDREN HARDEST", rw, 2)
ill_ebola(rx, y2 + 4, 90, 54)
y2 = para(rx, y2 + 4 + 54 + 6,
    "Nearly 3 in 4 children under 5 infected with Ebola do not survive.",
    rw, 2, BLACK)

# MIDDLE ROW, y ~ 640
my = 640
hline(24, my, W - 48, BLACK)
# Gulf, left
kicker(lx, my + 12, "MIDDLE EAST  -  GULF ON ALERT")
y3 = headline(lx, my + 32, "US STRIKES QESHM AS IRAN HITS BAHRAIN AND KUWAIT", 480, 2)
ill_gulf(lx, y3 + 6, 480, 88)
y3 = para(lx, y3 + 6 + 88 + 8,
    "US jets struck a missile site on Iran's Qeshm Island. Iran then "
    "launched drones at Bahrain and Kuwait, which say they repelled them.",
    480, 2, BLACK)
# Bridge, right of middle
bx, bw = 528, 472
kicker(bx, my + 12, "UKRAINE  -  KERCH BRIDGE")
y4 = headline(bx, my + 32, "BRIDGE PARTLY COLLAPSES IN UKRAINE ATTACK", bw, 2)
ill_bridge(bx, y4 + 6, bw, 88)
y4 = para(bx, y4 + 6 + 88 + 8,
    "Ukrainian drones and missiles partly destroyed the bridge to Crimea. "
    "One arch fell into the strait. Zelenskyy called it unprecedented.",
    bw, 2, BLACK)

# BOTTOM STRIP
by = 880
hline(24, by, W - 48, BLACK)
kicker(24, by + 10, "IN BRIEF")
# icons + briefs in one line each, two columns
briefs = [
    ("PLANE CRASH: 19 dead as a Russian An-12 crashes in Siberia.",
     "MEASLES: US loses measles-free status. 5,400 cases, 10 deaths."),
    ("GAZA COLD: Cold kills in displacement tents.",
     "WAYMO: Driverless rides suspended on US highways."),
]
yy = by + 32
for left_b, right_b in briefs:
    para(24, yy, left_b, 470, 1, BLACK, lh=16)
    para(528, yy, right_b, 472, 1, BLACK, lh=16)
    yy += 20
# markets line
hline(24, 972, W - 48, LIGHT)
text(24, 984, "MARKETS: SP 500 -1.03%  DAX -2.08%  GOLD USD 3,775  BRENT USD 91.55",
     1, GREY)

# --- PNG writer (stdlib zlib) ---
def chunk(kind, data):
    c = struct.pack(">I", len(data)) + kind + data
    return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

def write_png(path):
    raw = b"".join(b"\x00" + bytes(canvas[y * W * 3:(y + 1) * W * 3])
                   for y in range(H))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

def main():
    out = "/output/entry.png" if os.path.isdir("/output") else "output/entry.png"
    if "OUTPUT_PATH" in os.environ:
        out = os.environ["OUTPUT_PATH"]
    n = write_png(out)
    print(f"wrote {out} {W}x{H} {n} bytes")

if __name__ == "__main__":
    main()
