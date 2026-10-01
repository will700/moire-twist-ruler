"""Draw the two README schematics:

  docs/img/moire_regions.svg   what the regions of a reconstructed twisted bilayer are
                               (parallel and antiparallel, stacking names after
                               Van Winkle et al. 2023, Fig. 1f, g)
  docs/img/how_to_measure.svg  how to read the moire period L (right and wrong measurements)

  python tools/make_measure_diagram.py
"""
import math, os

L = 58.0                     # period in drawing units
H = L * math.sqrt(3) / 2
MXC, XMC, WALL, NODE, MMC = "#d6e2ec", "#a9bfd3", "#2b3a48", "#e07a1f", "#7b5bb5"
HEXC = "#cfdcc8"
GOOD, BAD, INK, MUTED, EDGE = "#11806a", "#c43d3d", "#1d2329", "#4d5964", "#d5dbe1"
MONO = 'font-family="DejaVu Sans Mono, Menlo, monospace"'
SANS = 'font-family="DejaVu Sans, Helvetica, Arial, sans-serif"'
HERE = os.path.dirname(os.path.abspath(__file__))


def node(o, i, j, m=((1, 0), (0, 1))):
    x, y = i * L + j * L / 2, j * H
    return (o[0] + m[0][0] * x + m[0][1] * y, o[1] + m[1][0] * x + m[1][1] * y)


def pts(ps):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)


def network(o, m=((1, 0), (0, 1)), dots=True):
    out = []
    for j in range(-1, 7):
        for i in range(-7, 11):
            a, b, c, d = node(o, i, j, m), node(o, i + 1, j, m), node(o, i, j + 1, m), node(o, i + 1, j + 1, m)
            out.append(f'<polygon points="{pts([a, b, c])}" fill="{MXC}" stroke="{WALL}" stroke-width="1.3"/>')
            out.append(f'<polygon points="{pts([b, d, c])}" fill="{XMC}" stroke="{WALL}" stroke-width="1.3"/>')
    if dots:
        for j in range(-1, 8):
            for i in range(-7, 12):
                x, y = node(o, i, j, m)
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{NODE}"/>')
    return out


def hexes(o, with_sites=True):
    """Antiparallel, strongly reconstructed: XMMX hexagons on the moire lattice, XX and MM
    at alternate corners (each corner set is itself a triangular lattice of period L)."""
    r = L / math.sqrt(3); out, xx, mm = [], set(), set()
    for j in range(-1, 7):
        for i in range(-6, 10):
            cx, cy = node(o, i, j)
            hx = [(cx + r * math.cos(math.pi / 6 + q * math.pi / 3), cy + r * math.sin(math.pi / 6 + q * math.pi / 3)) for q in range(6)]
            out.append(f'<polygon points="{pts(hx)}" fill="{HEXC}" stroke="{WALL}" stroke-width="1.3"/>')
            for q, (x, y) in enumerate(hx):
                (xx if q % 2 == 0 else mm).add((round(x, 1), round(y, 1)))
    if with_sites:
        out += [f'<circle cx="{x}" cy="{y}" r="3.4" fill="{NODE}"/>' for x, y in sorted(xx)]
        out += [f'<rect x="{x - 3}" y="{y - 3}" width="6" height="6" fill="{MMC}" transform="rotate(45 {x} {y})"/>' for x, y in sorted(mm)]
    return out, r


def arrow(p, q, col, both=True, w=2.6):
    mk = "g" if col == GOOD else ("b" if col == BAD else "k")
    s = f' marker-start="url(#{mk})"' if both else ""
    return f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="round" marker-end="url(#{mk})"{s}/>'


def label(x, y, t, col, anchor="middle", size=12):
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{col}" text-anchor="{anchor}" font-size="{size}" font-weight="700" {MONO} '
            f'stroke="#fff" stroke-width="3.5" paint-order="stroke" stroke-linejoin="round">{t}</text>')


def wrap(text, width, size):
    per = max(10, int(width / (size * 0.55)))
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > per:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + ([cur] if cur else [])


def card(x, y, w, img_h, eyebrow, lead, body, art, k):
    """A card like the README page: eyebrow, picture, bold lead sentence, explanation."""
    pad, size, lh = 14, 13, 19
    lead_l, body_l = wrap(lead, w - 2 * pad, size), wrap(body, w - 2 * pad, size)
    th = 36 + img_h + 14 + lh * (len(lead_l) + len(body_l)) + 16
    out = [f'<g transform="translate({x},{y})">',
           f'<rect x="0.5" y="0.5" width="{w - 1}" height="{th - 1}" rx="8" fill="#fff" stroke="{EDGE}"/>',
           f'<text x="{pad}" y="26" fill="{GOOD}" font-size="11.5" font-weight="700" letter-spacing="1" {MONO}>{eyebrow}</text>',
           f'<g transform="translate({pad},36)"><clipPath id="c{k}"><rect width="{w - 2 * pad}" height="{img_h}" rx="3"/></clipPath>',
           f'<g clip-path="url(#c{k})"><rect width="{w - 2 * pad}" height="{img_h}" fill="#fff"/>', *art, "</g></g>"]
    ty = 36 + img_h + 14 + 13
    for t in lead_l:
        out.append(f'<text x="{pad}" y="{ty}" fill="{INK}" font-size="{size}" font-weight="700" {SANS}>{t}</text>'); ty += lh
    for t in body_l:
        out.append(f'<text x="{pad}" y="{ty}" fill="{MUTED}" font-size="{size}" {SANS}>{t}</text>'); ty += lh
    out.append("</g>")
    return out, th


def legend(items, y=0):
    out, x = [], 0
    for kind, col, text in items:
        if kind == "box":
            out.append(f'<rect x="{x}" y="{y - 11}" width="14" height="14" rx="2" fill="{col}" stroke="{WALL}" stroke-width="1"/>'); x += 20
        elif kind == "dot":
            out.append(f'<circle cx="{x + 6}" cy="{y - 4}" r="4.5" fill="{col}"/>'); x += 16
        elif kind == "dia":
            out.append(f'<rect x="{x + 2}" y="{y - 8}" width="8" height="8" fill="{col}" transform="rotate(45 {x + 6} {y - 4})"/>'); x += 16
        elif kind == "line":
            out.append(f'<line x1="{x}" y1="{y - 4}" x2="{x + 14}" y2="{y - 4}" stroke="{col}" stroke-width="2.6"/>'); x += 20
        out.append(f'<text x="{x}" y="{y}" fill="{MUTED}" font-size="12.5" {SANS}>{text}</text>')
        x += int(len(text) * 7.3) + 22
    return out


def svg(path, body, w, h):
    doc = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-12 -12 {w + 24} {h + 24}" width="{w + 24}" height="{h + 24}">',
           f'<rect x="-12" y="-12" width="{w + 24}" height="{h + 24}" fill="#f6f7f8"/>', "<defs>",
           *[f'<marker id="{m}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
             for m, c in (("g", GOOD), ("b", BAD), ("k", INK))],
           "</defs>", *body, "</svg>"]
    dst = os.path.normpath(os.path.join(HERE, "..", "docs", "img", path))
    open(dst, "w").write("\n".join(doc) + "\n")
    print("wrote", dst)


# ---------------------------------------------------------------- moire_regions.svg
CW, IH = 520, 290
O = (-10, 20)
out = legend([("box", MXC, "MX domain (AB)"), ("box", XMC, "XM domain (BA)"), ("line", WALL, "SP domain wall"),
              ("dot", NODE, "MMXX node (AA)"), ("box", HEXC, "XMMX domain (2H)"), ("dot", NODE, "XX node"), ("dia", MMC, "MM site")], y=4)

art = network(O)
n0 = node(O, 4, 2); t1 = (node(O, 2, 1)[0] + L / 2, node(O, 2, 1)[1] + H / 3); t2 = (node(O, 5, 2)[0] + L, node(O, 5, 2)[1] + 2 * H / 3)
w0 = ((node(O, 6, 3)[0] + node(O, 7, 3)[0]) / 2, node(O, 6, 3)[1])
art += [label(t1[0], t1[1] + 5, "MX", INK), label(t2[0], t2[1] + 5, "XM", INK),
        f'<circle cx="{n0[0]:.1f}" cy="{n0[1]:.1f}" r="8" fill="none" stroke="{INK}" stroke-width="2"/>',
        label(n0[0] + 12, n0[1] - 12, "MMXX (AA) node", INK, "start"),
        f'<circle cx="{w0[0]:.1f}" cy="{w0[1]:.1f}" r="6" fill="none" stroke="{INK}" stroke-width="2"/>',
        label(w0[0], w0[1] + 24, "SP wall", INK)]
c1, h1 = card(0, 24, CW, IH, "PARALLEL, NEAR 0 DEG (3R-LIKE)",
              "Triangles of two stackings, nodes where the walls meet.",
              "In MX and XM (often written AB and BA) the metal atoms (M) of one layer sit over the chalcogen atoms (X) of the "
              "other; the two are mirror versions of each other. They have the lowest stacking energy, so they grow into "
              "triangular domains as the layers relax. The domains meet along domain walls of saddle-point (SP) stacking. Three "
              "walls cross at an MMXX node (often written AA): metal over metal and chalcogen over chalcogen, the highest "
              "energy, squeezed to a point. The nodes form the moire lattice: L is node to node.", art, 0)

hx, r = hexes((30, 20))
cc = node((30, 20), 3, 2); vx = (cc[0] + r * math.cos(math.pi / 6), cc[1] + r * math.sin(math.pi / 6))
vm = (cc[0] + r * math.cos(math.pi / 2), cc[1] + r * math.sin(math.pi / 2))
c2c = node((30, 20), 4, 2)
hx += [label(cc[0], cc[1] - 8, "XMMX", INK),
       f'<circle cx="{vx[0]:.1f}" cy="{vx[1]:.1f}" r="8" fill="none" stroke="{INK}" stroke-width="2"/>', label(vx[0] + 12, vx[1] + 4, "XX node", INK, "start"),
       f'<circle cx="{vm[0]:.1f}" cy="{vm[1]:.1f}" r="8" fill="none" stroke="{INK}" stroke-width="2"/>', label(vm[0], vm[1] + 24, "MM", INK),
       arrow(node((30, 20), 1, 0), node((30, 20), 3, 0), GOOD), label(node((30, 20), 2, 0)[0], node((30, 20), 2, 0)[1] - 10, "2L", GOOD)]
c3, h2 = card(CW + 16, 24, CW, IH, "ANTIPARALLEL, NEAR 60 DEG (2H-LIKE)",
              "Hexagons of one stacking, nodes at alternate corners.",
              "XMMX is the 2H stacking: every metal sits over a chalcogen of the other layer. It has the lowest energy and grows "
              "into hexagonal domains. XX (chalcogen over chalcogen) has the highest energy and shrinks to points at alternate "
              "hexagon corners: these are the nodes. MM (metal over metal) sits at the other corners; it is only a little above "
              "XMMX in energy, so it stays as small regions at larger twist and shrinks as the twist falls. L is hexagon centre "
              "to centre (XX node to XX node), not the hexagon edge (L/√3).", hx, 1)
hh = 24 + max(h1, h2)
out += c1 + c3 + [f'<text x="0" y="{hh + 22}" fill="{MUTED}" font-size="11.5" {SANS}>Schematic, strongly reconstructed. Stacking names and '
                  f'energies as in Van Winkle et al., Nat. Commun. 14, 2989 (2023), Fig. 1f, g: M = metal, X = chalcogen, SP = saddle point.</text>']
svg("moire_regions.svg", out, 2 * CW + 16, hh + 30)

# ---------------------------------------------------------------- how_to_measure.svg
CW, IH = 340, 230
O = (-6, 20)
out = legend([("box", MXC, "MX (AB) domain"), ("box", XMC, "XM (BA) domain"), ("dot", NODE, "MMXX (AA) node, wall junction"),
              ("line", GOOD, "correct measurement"), ("line", BAD, "common mistake")], y=4)
cards = []

c = node(O, 2, 2)
art = network(O) + [arrow(c, node(O, 3, 2), GOOD, False), arrow(c, node(O, 2, 1), GOOD, False), arrow(c, node(O, 1, 2), GOOD, False),
                    f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="7.5" fill="none" stroke="{GOOD}" stroke-width="2.4"/>',
                    label(c[0] + 26, c[1] - 8, "L", GOOD), label(c[0] + 18, c[1] - 30, "L", GOOD, "start"), label(c[0] - 26, c[1] - 8, "L", GOOD)]
cards.append(("DEFINITION", "L is one node to the next node along a wall.",
              "From any AA node, walls run out in six directions (three lines). Following any wall to the next node is exactly "
              "one moire period L.", art))

art = network(O, dots=False)
for j in range(0, 5):
    for i in range(-3, 7):
        x, y = node(O, i, j)
        if 6 < x < CW - 34 and 6 < y < IH - 6:
            art.append(f'<circle cx="{x + 1.2:.1f}" cy="{y - 0.8:.1f}" r="3.8" fill="#ffd23f" stroke="{INK}" stroke-width="0.8"/>')
cards.append(("BEST: CLICK NODES", "Click every node you can see.",
              "Neighbouring nodes are joined into triangular moire cells, so there is nothing to count. Each cell gives its own "
              "three sides, twist and heterostrain, and the image takes the median cell.", art))

art = network(O) + [arrow(node(O, 0, 1), node(O, 4, 1), GOOD), label(node(O, 2, 1)[0], node(O, 2, 1)[1] - 9, "D1 = 4L", GOOD),
                    arrow(node(O, 1, 0), node(O, 1, 3), GOOD), label(node(O, 1, 2)[0] - 16, node(O, 1, 2)[1] + 20, "D2 = 3L", GOOD, "end"),
                    arrow(node(O, 5, 0), node(O, 2, 3), GOOD), label(node(O, 4, 2)[0] - 8, node(O, 4, 2)[1] + 26, "D3 = 3L", GOOD, "end")]
cards.append(("IN PRACTICE: LINES", "Same measurement, spread over several periods.",
              "Pick two AA nodes several periods apart on one wall line, measure D, divide by N = (nodes on the line) - 1. A 1 px "
              "pick error is then divided by N. Repeat along all three wall directions. Here D1/4, D2/3 and D3/3 all give L.", art))

n = node(O, 1, 1)
c1_, c2_ = (n[0] + L / 2, n[1] + H / 3), (n[0] + L, n[1] + 2 * H / 3)
top = node(O, 4, 0); mid = ((node(O, 3, 1)[0] + node(O, 4, 1)[0]) / 2, node(O, 3, 1)[1])
art = network(O) + [arrow(c1_, c2_, BAD), label(c1_[0] - 6, c1_[1] - 4, "L/√3", BAD, "end"),
                    arrow(top, mid, BAD), label(top[0] + 8, top[1] + 30, "0.87L", BAD, "start")]
cards.append(("COMMON MISTAKES", "Not domain centres or triangle heights.",
              "A domain centre to the neighbouring centre is L/√3, which reads the twist 1.73x too high (the MX and XM domains "
              "can look alike, so the nearest blobs are this pair). The triangle height is 0.87 L (1.15x too high); a "
              "second-order fringe is L/2 (2x).", art))

M = ((1.13, 0), (0, 0.93)); O2 = (-4, 18)
art = network(O2, M) + [arrow(node(O2, 0, 1, M), node(O2, 3, 1, M), GOOD), label(node(O2, 1.5, 1, M)[0], node(O2, 1, 1, M)[1] - 9, "1.13 L", GOOD),
                        arrow(node(O2, 0, 2, M), node(O2, 0, 0, M), GOOD), label(node(O2, 0, 1, M)[0] + 30, node(O2, 0, 1, M)[1] + 40, "0.98 L", GOOD, "start"),
                        arrow(node(O2, 4, 0, M), node(O2, 2, 2, M), GOOD), label(node(O2, 3, 1, M)[0] + 12, node(O2, 3, 1, M)[1] + 30, "0.98 L", GOOD, "start")]
cards.append(("HETEROSTRAIN", "Unequal periods mean heterostrain.",
              "If L1, L2 and L3 differ by more than a few percent, the pure-twist formula on their mean reads the twist wrong. "
              "Click nodes solves twist and heterostrain together for every cell.", art))

O3 = (20, 20); art, r = hexes(O3)
art += [arrow(node(O3, 0, 2), node(O3, 4, 2), GOOD), label(node(O3, 2, 2)[0], node(O3, 2, 2)[1] - 10, "4L centre to centre", GOOD)]
cc = node(O3, 1, 3); v1 = (cc[0] + r * math.cos(math.pi / 6), cc[1] + r * math.sin(math.pi / 6)); v2 = (cc[0], cc[1] + r)
art += [arrow(v2, v1, BAD), label(v1[0] + 8, v1[1] + 22, "edge = L/√3", BAD, "start")]
cards.append(("NEAR 60 DEG (ANTIPARALLEL)", "Measure hexagon centre to centre.",
              "Here the XMMX domains are hexagons and the nodes sit at their corners. L is the centre-to-centre spacing (the "
              "same as XX node to XX node), not the hexagon edge, which is L/√3.", art))

heights = []
for k, (eb, lead, body, art) in enumerate(cards):
    heights.append(card(0, 0, CW, IH, eb, lead, body, art, 10 + k)[1])
rows = [max(heights[0:3]), max(heights[3:6])]
y = 24
for row in range(2):
    for col in range(3):
        k = row * 3 + col; eb, lead, body, art = cards[k]
        out += card(col * (CW + 14), y, CW, IH, eb, lead, body, art, 10 + k)[0]
    y += rows[row] + 14
svg("how_to_measure.svg", out, 3 * CW + 28, y - 14)
