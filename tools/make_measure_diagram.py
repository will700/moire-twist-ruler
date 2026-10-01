"""Draw docs/img/how_to_measure.svg: schematic of how to read the moire period L from a
reconstructed twisted-bilayer domain network (right and wrong measurements).

  python tools/make_measure_diagram.py
"""
import math, os

L = 58.0                     # period in drawing units
H = L * math.sqrt(3) / 2
PW, PH = 330, 250            # panel size
COLS, ROWS = 3, 2
AB, BA, WALL, NODE = "#d6e2ec", "#a9bfd3", "#2b3a48", "#e07a1f"
GOOD, BAD, INK, MUTED = "#11806a", "#c43d3d", "#1d2329", "#5d6873"
FONT = "font-family=\"DejaVu Sans Mono, Menlo, monospace\""


def node(o, i, j, m=((1, 0), (0, 1))):
    x, y = i * L + j * L / 2, j * H
    return (o[0] + m[0][0] * x + m[0][1] * y, o[1] + m[1][0] * x + m[1][1] * y)


def pts(ps):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)


def network(o, m=((1, 0), (0, 1)), dots=True):
    out = []
    for j in range(-1, 6):
        for i in range(-6, 9):
            a, b, c, d = node(o, i, j, m), node(o, i + 1, j, m), node(o, i, j + 1, m), node(o, i + 1, j + 1, m)
            out.append(f'<polygon points="{pts([a, b, c])}" fill="{AB}" stroke="{WALL}" stroke-width="1.3"/>')
            out.append(f'<polygon points="{pts([b, d, c])}" fill="{BA}" stroke="{WALL}" stroke-width="1.3"/>')
    if dots:
        for j in range(-1, 7):
            for i in range(-6, 10):
                x, y = node(o, i, j, m)
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{NODE}"/>')
    return out


def arrow(p, q, col, both=True, w=2.6):
    mk = "g" if col == GOOD else "b"
    s = f' marker-start="url(#{mk})"' if both else ""
    return f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="round" marker-end="url(#{mk})"{s}/>'


def label(x, y, t, col, anchor="middle", size=12):
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{col}" text-anchor="{anchor}" font-size="{size}" font-weight="600" {FONT} '
            f'stroke="#fff" stroke-width="3.5" paint-order="stroke" stroke-linejoin="round">{t}</text>')


def panel(k, title, sub, body):
    cx, cy = (k % COLS) * (PW + 14), (k // COLS) * (PH + 60)
    clip = f"c{k}"
    return [f'<g transform="translate({cx},{cy})">',
            f'<clipPath id="{clip}"><rect x="0" y="0" width="{PW}" height="{PH}" rx="6"/></clipPath>',
            f'<g clip-path="url(#{clip})"><rect width="{PW}" height="{PH}" fill="#fff"/>', *body, "</g>",
            f'<rect x="0.5" y="0.5" width="{PW - 1}" height="{PH - 1}" rx="6" fill="none" stroke="#cfd6dc"/>',
            f'<text x="2" y="{PH + 20}" fill="{INK}" font-size="13.5" font-weight="700" {FONT}>{title}</text>',
            f'<text x="2" y="{PH + 39}" fill="{MUTED}" font-size="11.5" {FONT}>{sub}</text>', "</g>"]


O = (14, 26)
out = []

# 1 definition
c = node(O, 2, 2)
b = network(O) + [arrow(c, node(O, 3, 2), GOOD, False), arrow(c, node(O, 2, 1), GOOD, False), arrow(c, node(O, 1, 2), GOOD, False),
                  f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="7.5" fill="none" stroke="{GOOD}" stroke-width="2.4"/>',
                  label(c[0] + 24, c[1] - 8, "L", GOOD), label(c[0] + 18, c[1] - 30, "L", GOOD, "start"), label(c[0] - 24, c[1] - 8, "L", GOOD)]
out += panel(0, "1. L = node to next node", "AA node (wall junction) to its neighbour", b)

# 2 click every node: the cells between them are measured one by one
b = network(O, dots=False)
for j in range(0, 5):
    for i in range(-3, 7):
        x, y = node(O, i, j)
        if 8 < x < PW - 8 and 8 < y < PH - 8:
            b.append(f'<circle cx="{x + 1.2:.1f}" cy="{y - 0.8:.1f}" r="3.6" fill="#ffd23f" stroke="{INK}" stroke-width="0.8"/>')
out += panel(1, "2. Best: click every node", "cells between nodes: local twist + strain", b)

# 3 lines over several periods, three directions
b = network(O) + [arrow(node(O, 0, 1), node(O, 4, 1), GOOD), label(node(O, 2, 1)[0], node(O, 2, 1)[1] - 9, "4L", GOOD),
                  arrow(node(O, 1, 0), node(O, 1, 3), GOOD), label(node(O, 1, 2)[0] - 14, node(O, 1, 2)[1] + 22, "3L", GOOD, "end"),
                  arrow(node(O, 5, 0), node(O, 2, 3), GOOD), label(node(O, 4, 2)[0] - 4, node(O, 4, 2)[1] + 24, "3L", GOOD, "end")]
out += panel(2, "3. Lines: span several periods", "N = nodes on the line - 1, all 3 directions", b)

# 4 mistakes
n = node(O, 1, 1)
c1, c2 = (n[0] + L / 2, n[1] + H / 3), (n[0] + L, n[1] + 2 * H / 3)
top = node(O, 4, 0); mid = ((node(O, 3, 1)[0] + node(O, 4, 1)[0]) / 2, node(O, 3, 1)[1])
b = network(O) + [arrow(c1, c2, BAD), label(c1[0] - 6, c1[1] - 4, "L/√3", BAD, "end"),
                  arrow(top, mid, BAD), label(top[0] + 8, top[1] + 30, "0.87L", BAD, "start")]
out += panel(3, "4. Not: centres or heights", "centre to centre = 0.58 L (theta x1.73)", b)

# 5 heterostrain
M = ((1.13, 0), (0, 0.93))
O2 = (10, 24)
b = network(O2, M) + [arrow(node(O2, 0, 1, M), node(O2, 3, 1, M), GOOD), label(node(O2, 1.5, 1, M)[0], node(O2, 1, 1, M)[1] - 9, "1.13 L", GOOD),
                       arrow(node(O2, 0, 2, M), node(O2, 0, 0, M), GOOD), label(node(O2, 0, 1, M)[0] + 30, node(O2, 0, 1, M)[1] + 40, "0.98 L", GOOD, "start"),
                       arrow(node(O2, 4, 0, M), node(O2, 2, 2, M), GOOD), label(node(O2, 3, 1, M)[0] + 12, node(O2, 3, 1, M)[1] + 30, "0.98 L", GOOD, "start")]
out += panel(4, "5. Unequal periods = heterostrain", "L1, L2, L3 differ by > 5 %", b)

# 6 AP hexagons
O3 = (30, 30); r = L / math.sqrt(3); b = []
for j in range(-1, 6):
    for i in range(-5, 8):
        cx, cy = node(O3, i, j)
        hx = [(cx + r * math.cos(math.pi / 6 + q * math.pi / 3), cy + r * math.sin(math.pi / 6 + q * math.pi / 3)) for q in range(6)]
        b.append(f'<polygon points="{pts(hx)}" fill="{AB}" stroke="{WALL}" stroke-width="1.3"/>')
        b.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3" fill="{NODE}"/>')
b += [arrow(node(O3, 0, 1), node(O3, 4, 1), GOOD), label(node(O3, 2, 1)[0], node(O3, 2, 1)[1] - 10, "4L centre to centre", GOOD)]
cc = node(O3, 1, 3); v1 = (cc[0] + r * math.cos(math.pi / 6), cc[1] + r * math.sin(math.pi / 6)); v2 = (cc[0], cc[1] + r)
b += [arrow(v2, v1, BAD), label(v1[0] + 8, v1[1] + 22, "edge = L/√3", BAD, "start")]
out += panel(5, "6. Near 60 deg (AP): hexagons", "L = hexagon centre to centre", b)

W, Ht = COLS * PW + (COLS - 1) * 14, ROWS * (PH + 60)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-8 -8 {W + 16} {Ht + 8}" width="{W + 16}" height="{Ht + 8}">',
       f'<rect x="-8" y="-8" width="{W + 16}" height="{Ht + 8}" fill="#fff"/>',
       "<defs>",
       f'<marker id="g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{GOOD}"/></marker>',
       f'<marker id="b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{BAD}"/></marker>',
       "</defs>", *out, "</svg>"]
dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "img", "how_to_measure.svg")
open(dst, "w").write("\n".join(svg) + "\n")
print("wrote", os.path.normpath(dst))
