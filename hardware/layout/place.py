#!/usr/bin/env python3
"""Auris rev A placement planner (phase 3).

Reads the parts and their footprints from an EasyEDA export, puts the anchor parts where this file
says, places every other part greedily as close as possible to the pads it connects to (and to the
part named in its BOM / netlist note, e.g. "At U102 pin 8"), checks the result, renders a PNG and
writes the EasyEDA script that moves the parts.

    python3 hardware/layout/place.py hardware/2026-11-19/AURIS_2026-11-19_phase2.epro2 pass1
    python3 hardware/layout/place.py --check hardware/2026-11-19/AURIS_2026-11-19_place1.epro2 pass1

Writes hardware/layout/placement-<tag>.csv and .png, and hardware/easyeda/pcb-phase3-place.js.
Coordinates: mm, board frame (origin bottom-left, Y up); angles counter-clockwise, degrees.
"""
import csv, math, os, re, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "hardware", "tools"))
from pcb_board import load_board, SHEETS  # noqa: E402

# ------------------------------------------------------------------ board (owner decisions)
W, H = 80.0, 105.0
NOTCH = (0.0, 99.0, 35.0, 105.0)       # ESP32 antenna cut-out, top-left (owner 2026-11-19)
HOLES = [(4.0, 4.0), (76.0, 4.0), (40.0, 101.0), (76.0, 101.0)]   # MH3, MH4, MH1 (moved), MH2
HOLE_KEEP = 3.6                         # half-size of the square kept clear for an M3 head + washer
EDGE = 0.3                              # parts (pads and body) stay this far inside the edge
GAP = 0.15                              # minimum margin (pass 1 used this for every part)
GAP_IC, GAP_CONN, GAP_PASSIVE = 0.8, 0.5, 0.35   # pass 2: room for fan-out, vias and traces


def gap_of(p):
    """Margin around a part: ICs and multi-pin parts get fan-out room, passives less."""
    if p.des.startswith(("J", "BT", "SW")):
        return GAP_CONN
    return GAP_IC if len(p.fp.pads) >= 5 else GAP_PASSIVE
U301_RING = 3.0                         # Quectel: >= 3 mm from U301 to other parts
GND_NETS = {"GND"}

# ------------------------------------------------------------------ anchors: x, y, angle
ANCHORS = {
    "U401": (13.5, 88.61, 0),        # pass 4: body 4.5..22.5 x 79.5..105; antenna strip y 99..105 over the notch, 3V3/EN caps in the strip at x 2-3
    # J401 and J402 are used from above since SC-001/SC-002 (2026-11-19): no edge needed
    "J401": (4.5, 73.0, 90),         # vertical USB-C just below the module, near its USB pins
    "J402": (9.0, 56.0, 90),         # flip-top microSD below J401, contact row facing the module and the SD parts
    "J301": (8.325, 39.5, 270),      # SIM, slot at the left edge (shell pad 8 copper 0.5 mm in)
    "J101": (14.0, 3.45, 0),         # mic 1, bottom edge (mount pads 0.5 mm in)
    "J102": (28.0, 3.45, 0),         # mic 2 option, bottom edge
    "J201": (50.0, 3.6, 0),          # panel inputs, bottom edge
    "J202": (61.0, 3.6, 0),
    "J203": (74.875, 40.0, 90),      # battery, right edge (mount pads 0.5 mm in)
    "U203": (30.0, 52.0, 0),         # TMP390 over the battery pack (now under the board; pack assumed centred, x 20-60, y 25-95), clear of converters and charger
    "BT201": (40.0, 41.0, 0),        # RTC coin cell in the centre, away from the charger and converters
    "U102": (22.0, 20.0, 90),        # PCM1863: analog end (pins 1-8, 27-30) down toward J101, digital end up
    "U301": (62.5, 85.5, 0),         # LTE module, top-right; pad 35 (RF) top-right
    "J302": (77.4, 91.0, 0),         # u.FL to the LTE antenna on the right wall
}
POGO = ["TP401", "TP402", "TP403", "TP413", "TP414", "TP415"]     # 2.54 mm pogo row
POGO_AT = (26.0, 80.5, 0.0, 2.54)                                 # x, first y, angle, pitch (up)

# ------------------------------------------------------------------ block regions (x0, y0, x1, y1)
ANT_KEEP = (22.5, 95.5, 39.0, 99.0)     # no parts just below the antenna cut-out
REGIONS = {
    "m_module": [(19.5, 64, 40, 95.5), (0, 76, 20, 79.5)],
    "m_test": [(19.5, 54, 44, 95.5)],
    "m_sd": [(17, 46, 38, 79)],
    "m_usb": [(7, 64, 22, 79.5)],
    "m_led": [(14, 37, 30, 50)],
    "l_sim": [(14, 33, 34, 50)],
    "l_pins": [(40, 62, 80, 99)],
    "l_ant": [(72.5, 72, 80, 98)],
    "l_supply": [(42, 58, 80, 77)],
    "l_ctrl": [(34, 56, 54, 98)],
    "l_test": [(32, 52, 56, 98)],
    "p_battery": [(52, 30, 80, 54)],
    "p_temp": [(18, 42, 44, 62)],
    "p_modem": [(44, 46, 80, 76)],
    "p_charger": [(34, 10, 70, 38)],
    "p_solar": [(34, 0, 74, 20)],
    "p_3v3": [(20, 52, 46, 80)],
    "p_rtc": [(18, 30, 58, 62)],
    "p_latch": [(18, 30, 58, 62)],
    "p_test": [(18, 10, 80, 64)],
    "mic": [(0, 0, 47, 37)], "mic2": [(0, 0, 47, 37)], "presupply": [(0, 0, 47, 37)],
    "preamp": [(0, 0, 47, 37)], "direct": [(0, 0, 47, 37)], "adc": [(0, 0, 47, 37)],
    "clockio": [(0, 0, 47, 37)], "power": [(0, 0, 47, 37)], "test": [(0, 0, 47, 37)],
}
ORDER = ["m_module", "m_test", "m_sd", "m_usb", "m_led", "l_sim", "l_pins", "l_ant", "l_supply", "l_ctrl",
         "l_test", "p_battery", "p_modem", "p_temp", "p_charger", "p_solar", "p_3v3", "p_rtc", "p_latch",
         "p_test", "adc", "direct", "clockio", "power", "preamp", "presupply", "mic", "mic2", "test"]
# parts placed in another block's region than their schematic block
REGION_OF = {"SW201": "m_led", "Q210": "p_battery", "R228": "p_battery"}
EDGE_OK = {"U401", "J301", "J101", "J102", "J201", "J202", "J203", "J302"}


# ------------------------------------------------------------------ geometry helpers
def overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def inside_board(r, allow_notch=False):
    if r[0] < EDGE or r[1] < EDGE or r[2] > W - EDGE or r[3] > H - EDGE:
        return False
    return allow_notch or not overlap(r, NOTCH)


def dist_to_rect(x, y, r):
    dx = max(r[0] - x, 0, x - r[2]); dy = max(r[1] - y, 0, y - r[3])
    return math.hypot(dx, dy)


class Grid:
    """Placed rectangles in 5 mm buckets."""
    def __init__(self):
        self.cells = defaultdict(list)

    def add(self, r, tag):
        for i in range(int(r[0] // 5), int(r[2] // 5) + 1):
            for j in range(int(r[1] // 5), int(r[3] // 5) + 1):
                self.cells[(i, j)].append((r, tag))

    def hits(self, r):
        out = set()
        for i in range(int(r[0] // 5), int(r[2] // 5) + 1):
            for j in range(int(r[1] // 5), int(r[3] // 5) + 1):
                for rr, tag in self.cells.get((i, j), ()):
                    if overlap(r, rr):
                        out.add(tag)
        return out


# ------------------------------------------------------------------ notes: "At U102 pin 8"
def note_targets(board):
    """des -> [(ref, pad nums)] from BOM notes and netlist notes, kept only where ref shares a net."""
    pin_net = {}
    notes = defaultdict(str)
    for sheet in SHEETS:
        f = os.path.join(ROOT, "hardware", sheet, f"{sheet}-netlist.csv")
        for r in csv.DictReader(open(f)):
            pin_net[(r["designator"], r["pin"])] = r["net"]
            pin_net[(r["designator"], r["pin_name"])] = r["net"]
            if r.get("notes"):
                notes[r["designator"]] += " " + r["notes"]
    # BOM rows: a single-part row counts whole; in a shared row only clauses naming this part count
    for sheet in SHEETS:
        f = os.path.join(ROOT, "hardware", sheet, f"{sheet}-bom.csv")
        for r in csv.DictReader(open(f)):
            ds = [x for x in re.split(r"[,\s]+", r.get("designators", "")) if x]
            text = r.get("notes", "") or ""
            for d in ds:
                if len(ds) == 1:
                    notes[d] += " " + text
                else:
                    notes[d] += " " + " ".join(c for c in re.split(r"[;.]", text) if re.search(rf"\b{d}\b", c))
    rx = re.compile(r"\b[Aa]t ((?:U|J|Q|Y|L|D)\d{3})(?:\s+pins?\s+([\d/]+)|\s+([A-Z][A-Z0-9_]{1,8})\b)?")
    out = {}
    for d, text in notes.items():
        if d not in board.parts:
            continue
        mine = {n for n in board.parts[d].nets.values() if n not in GND_NETS}
        tg = []
        for m in rx.finditer(text):
            ref, pins, pname = m.group(1), m.group(2), m.group(3)
            if ref not in board.parts or ref == d:
                continue
            refp = board.parts[ref]
            shared = {n for n in refp.nets.values() if n in mine}
            if not shared:
                continue
            want = set()
            if pins:
                want = {pin_net.get((ref, p)) for p in pins.split("/")} & shared
            elif pname:
                want = {pin_net.get((ref, pname))} & shared
            want = want or shared
            pads = [num for num, n in refp.nets.items() if n in want]
            if pads:
                tg.append((ref, pads))
        if tg:
            out[d] = tg
    return out


# ------------------------------------------------------------------ planner
def plan(board):
    place = {}            # des -> (x, y, angle)
    grid = Grid()
    targets = note_targets(board)
    padpos = {}           # (des, num) -> (x, y) for placed parts

    def commit(d, x, y, a):
        p = board.parts[d]
        place[d] = (x, y, a)
        grid.add(p.extent(gap_of(p), x, y, a), d)
        for pad in p.fp.pads:
            padpos[(d, pad.num)] = p.pad_xy(pad, x, y, a)

    # fixed keep-outs
    for i, (hx, hy) in enumerate(HOLES):
        grid.add((hx - HOLE_KEEP, hy - HOLE_KEEP, hx + HOLE_KEEP, hy + HOLE_KEEP), f"HOLE{i}")
    grid.add(ANT_KEEP, "ANT_KEEP")
    for d, (x, y, a) in ANCHORS.items():
        commit(d, x, y, a)
    u = board.parts["U301"]
    x0, y0, x1, y1 = u.extent(0, *ANCHORS["U301"])
    grid.add((x0 - U301_RING, y0 - U301_RING, x1 + U301_RING, y1 + U301_RING), "U301_RING")
    px, py, pa, pitch = POGO_AT
    for i, d in enumerate(POGO):
        commit(d, px, py + i * pitch, pa)

    def score(p, x, y, a):
        s = 0.0
        for pad in p.fp.pads:
            n = p.nets.get(pad.num)
            if not n or n in GND_NETS:
                continue
            others = [padpos[k] for k in board.net_pads[n] if k in padpos and k[0] != p.des]
            if not others:
                continue
            qx, qy = p.pad_xy(pad, x, y, a)
            s += min(math.hypot(qx - ox, qy - oy) for ox, oy in others)
        for ref, pads in targets.get(p.des, []):
            if ref not in place:
                continue
            tpts = [padpos[(ref, n)] for n in pads if (ref, n) in padpos]
            mine = [p.pad_xy(pad, x, y, a) for pad in p.fp.pads if p.nets.get(pad.num) in {board.parts[ref].nets.get(n) for n in pads}]
            if tpts and mine:
                s += 4 * min(math.hypot(mx - tx, my - ty) for mx, my in mine for tx, ty in tpts)
        return s

    def ideal(p, regs):
        pts = []
        for ref, pads in targets.get(p.des, []):
            pts += [padpos[(ref, n)] for n in pads if (ref, n) in padpos] * 3
        for pad in p.fp.pads:
            n = p.nets.get(pad.num)
            if n and n not in GND_NETS:
                pts += [padpos[k] for k in board.net_pads[n] if k in padpos and k[0] != p.des][:6]
        if pts:
            return sum(q[0] for q in pts) / len(pts), sum(q[1] for q in pts) / len(pts)
        r = regs[0]
        return (r[0] + r[2]) / 2, (r[1] + r[3]) / 2

    soft = []

    def place_one(d, regs):
        p = board.parts[d]
        cx, cy = ideal(p, regs)
        for hard in (True, False):
            best, found_r = None, None
            r, step = 0.0, 0.25
            while r <= 60:
                pts = [(cx, cy)] if r == 0 else ring(cx, cy, r, step)
                for x, y in pts:
                    for a in (0, 90, 180, 270):
                        ext = p.extent(gap_of(p), x, y, a)
                        if hard and not any(rg[0] <= ext[0] and rg[1] <= ext[1] and ext[2] <= rg[2] and ext[3] <= rg[3] for rg in regs):
                            continue
                        if not inside_board(ext) or grid.hits(ext):
                            continue
                        pen = 0 if hard else min(dist_to_rect(x, y, rg) for rg in regs)
                        s = score(p, x, y, a) + 6 * pen + 0.05 * r
                        if best is None or s < best[0]:
                            best = (s, x, y, a)
                            found_r = found_r if found_r is not None else r
                if found_r is not None and r >= found_r + 1.5:
                    break
                r += step
                if r > 6:
                    step = 0.5
            if best is not None:
                break
            soft.append(d)
        if best is None:
            raise SystemExit(f"no room for {d}")
        commit(d, round(best[1], 3), round(best[2], 3), best[3])

    for blk in ORDER:
        todo = [d for d, p in board.parts.items() if p.block == blk and d not in place]
        while todo:
            def key(d):
                p = board.parts[d]
                linked = sum(1 for pad in p.fp.pads for k in board.net_pads.get(p.nets.get(pad.num), [])
                             if p.nets.get(pad.num) not in GND_NETS and k in padpos)
                x0, y0, x1, y1 = p.fp.extent()
                return (len(p.fp.pads) >= 6, linked > 0, linked, (x1 - x0) * (y1 - y0))
            todo.sort(key=key, reverse=True)
            d = todo.pop(0)
            regs = REGIONS.get(REGION_OF.get(d, blk), [(0, 0, W, H)])
            place_one(d, regs)
    missing = set(board.parts) - set(place)
    if missing:
        raise SystemExit(f"not placed: {sorted(missing)}")
    if soft:
        print(f"placed outside their block region (region full): {soft}")
    return place, targets


def ring(cx, cy, r, step):
    n = max(8, int(2 * math.pi * r / step))
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


# ------------------------------------------------------------------ checks
def check(board, place, targets):
    out = []
    rects = {d: board.parts[d].extent(0, *place[d]) for d in place}
    names = sorted(rects)
    over = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if overlap(rects[a], rects[b]):
                over.append(f"{a}/{b}")
    out.append(f"overlapping parts (body+pads, no margin): {len(over)} {' '.join(over[:20])}")
    area = sum((r[2] - r[0]) * (r[3] - r[1]) for r in rects.values())
    out.append(f"parts cover {area:.0f} mm2 = {100 * area / (W * H - (NOTCH[2] - NOTCH[0]) * (NOTCH[3] - NOTCH[1])):.0f}% of the board (body+pads)")
    gaps = []
    for i, a in enumerate(names):
        ra = rects[a]
        best = 99
        for b in names:
            if b == a:
                continue
            g = dist_box(ra, rects[b])
            if g < best:
                best = g
        gaps.append(best)
    gaps.sort()
    out.append(f"gap to the nearest part: min {gaps[0]:.2f}, 10th percentile {gaps[len(gaps) // 10]:.2f}, median {gaps[len(gaps) // 2]:.2f} mm")
    outside = [d for d, r in rects.items() if d not in EDGE_OK and not inside_board(r)]
    out.append(f"outside the outline or in the notch: {outside}")
    # copper to the board edge (the notch counts as edge); DRC wants >= ~0.3 mm, aim for 0.5
    near_edge = []
    for d, (x, y, a) in place.items():
        p = board.parts[d]
        for q in p.fp.pads:
            cx, cy = p.pad_xy(q, x, y, a)
            w, h = (q.w, q.h) if a % 180 == 0 else (q.h, q.w)
            e = min(cx - w / 2, cy - h / 2, W - (cx + w / 2), H - (cy + h / 2))
            if cx - w / 2 < NOTCH[2] and cy + h / 2 > NOTCH[1] - 0.5:
                e = min(e, NOTCH[1] - (cy + h / 2))
            if e < 0.45:
                near_edge.append(f"{d}.{q.num} {e:.2f}")
    out.append(f"pad copper within 0.45 mm of the edge: {near_edge}")
    holes = [d for d, r in rects.items() for hx, hy in HOLES
             if overlap(r, (hx - HOLE_KEEP, hy - HOLE_KEEP, hx + HOLE_KEEP, hy + HOLE_KEEP))]
    out.append(f"in a mounting-hole keep-out: {holes}")
    x0, y0, x1, y1 = rects["U301"]
    ring_r = (x0 - U301_RING, y0 - U301_RING, x1 + U301_RING, y1 + U301_RING)
    near = [d for d, r in rects.items() if d != "U301" and overlap(r, ring_r)]
    out.append(f"within 3 mm of U301: {near}")
    ux = ANCHORS["U401"][0]
    ant = (ux - 9.0, 99.0, ux + 9.0, 105.0)   # the antenna strip, 18 mm wide, over the notch
    close = [f"{d} {dist_box(rects[d], ant):.1f}" for d in rects if d != "U401" and dist_box(rects[d], ant) < 10]
    out.append(f"parts within 10 mm of the antenna strip: {close}")
    # note targets: distance from the part's pad on the shared net to the target pad
    far = []
    for d, tg in targets.items():
        p = board.parts[d]
        for ref, pads in tg:
            rp = board.parts[ref]
            nets = {rp.nets.get(n) for n in pads}
            mine = [p.pad_xy(pad, *place[d]) for pad in p.fp.pads if p.nets.get(pad.num) in nets]
            tp = [rp.pad_xy(pad, *place[ref]) for pad in rp.fp.pads if pad.num in pads]
            if mine and tp:
                dd = min(math.hypot(a[0] - b[0], a[1] - b[1]) for a in mine for b in tp)
                far.append((dd, d, ref))
    far.sort(reverse=True)
    out.append(f"note targets: {len(far)}; farthest " + ", ".join(f"{d}->{ref} {dd:.1f} mm" for dd, d, ref in far[:12]))
    return out, far


def dist_box(a, b):
    dx = max(b[0] - a[2], 0, a[0] - b[2]); dy = max(b[1] - a[3], 0, a[1] - b[3])
    return math.hypot(dx, dy)


# ------------------------------------------------------------------ outputs
COLORS = {"audio-frontend": "#2a9d8f", "power": "#e76f51", "lte": "#6a4c93", "mcu": "#277da1"}


def sheet_of(blk):
    if blk.startswith("p_"):
        return "power"
    if blk.startswith("l_"):
        return "lte"
    if blk.startswith("m_"):
        return "mcu"
    return "audio-frontend"


def render(board, place, path, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Polygon, Circle
    fig, ax = plt.subplots(figsize=(9, 11.6), dpi=130)
    outline = [(0, 0), (W, 0), (W, H), (NOTCH[2], H), (NOTCH[2], NOTCH[1]), (0, NOTCH[1])]
    ax.add_patch(Polygon(outline, closed=True, fc="#f4f1e8", ec="#333", lw=1.2))
    ax.add_patch(Rectangle((1.5, 99), 18, 6, fc="none", ec="#277da1", lw=0.8, ls="--"))
    ax.text(10.5, 102, "antenna (in the notch)", ha="center", va="center", fontsize=6, color="#277da1")
    for hx, hy in HOLES:
        ax.add_patch(Circle((hx, hy), 1.6, fc="white", ec="#333", lw=0.8))
        ax.add_patch(Circle((hx, hy), HOLE_KEEP, fc="none", ec="#999", lw=0.5, ls=":"))
    u = board.parts["U301"]
    x0, y0, x1, y1 = u.extent(0, *place["U301"])
    ax.add_patch(Rectangle((x0 - U301_RING, y0 - U301_RING), x1 - x0 + 2 * U301_RING, y1 - y0 + 2 * U301_RING,
                           fc="none", ec="#6a4c93", lw=0.6, ls=":"))
    for d, (x, y, a) in place.items():
        p = board.parts[d]
        r = p.extent(0, x, y, a)
        col = COLORS[sheet_of(p.block)]
        ax.add_patch(Rectangle((r[0], r[1]), r[2] - r[0], r[3] - r[1], fc=col, alpha=0.18 if p.fit else 0.06,
                               ec=col, lw=0.5, ls="-" if p.fit else "--"))
        for pad in p.fp.pads:
            qx, qy = p.pad_xy(pad, x, y, a)
            w, h = (pad.w, pad.h) if a % 180 == 0 else (pad.h, pad.w)
            ax.add_patch(Rectangle((qx - w / 2, qy - h / 2), w, h, fc="#c9a227", ec="none", alpha=0.8))
        big = (r[2] - r[0]) * (r[3] - r[1]) > 12
        ax.text((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, d, ha="center", va="center",
                fontsize=5.5 if big else 3.2, color="#111")
    for sheet, col in COLORS.items():
        ax.plot([], [], color=col, lw=6, alpha=0.5, label=sheet)
    ax.legend(loc="upper right", bbox_to_anchor=(1.0, -0.03), ncol=4, fontsize=7, frameon=False)
    ax.set_xlim(-2, W + 2); ax.set_ylim(-2, H + 2); ax.set_aspect("equal")
    ax.set_xticks(range(0, 81, 10)); ax.set_yticks(range(0, 106, 10)); ax.tick_params(labelsize=6)
    ax.grid(True, lw=0.2, color="#bbb")
    ax.set_title(title, fontsize=9)
    fig.tight_layout()
    fig.savefig(path)


def write_csv(board, place, path):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["designator", "block", "x_mm", "y_mm", "angle", "fit"])
        for d in sorted(place, key=lambda s: (re.sub(r"\d", "", s), int(re.sub(r"\D", "", s) or 0))):
            x, y, a = place[d]
            p = board.parts[d]
            w.writerow([d, p.block, f"{x:.3f}", f"{y:.3f}", a, "Y" if p.fit else "N"])


def write_js(board, place, path, tag):
    MIL = 1 / 0.0254
    rows = [[d, round(x * MIL, 2), round(y * MIL, 2), a] for d, (x, y, a) in sorted(place.items())]
    probe = []
    for d, num in (("U301", "35"), ("J401", "A1B12"), ("U401", "1"), ("U102", "1"), ("J203", "1"), ("J402", "1")):
        p = board.parts.get(d)
        pad = next((q for q in p.fp.pads if q.num == num), None) if p else None
        if pad and d in place:
            px, py = p.pad_xy(pad, *place[d])
            probe.append([d, num, round(px * MIL, 1), round(py * MIL, 1)])
    js = TEMPLATE.replace("__TAG__", tag).replace("__ROWS__", json_rows(rows)).replace("__PROBE__", json_rows(probe))
    open(path, "w").write(js)


def json_rows(rows):
    import json
    return "[\n" + ",\n".join("    " + json.dumps(r) for r in rows) + "\n  ]"


TEMPLATE = r"""// Auris rev A layout, phase 3: move every part to its planned place (generated by
// hardware/layout/place.py, placement __TAG__; do not edit by hand).
// x, y in mil (board origin bottom-left), angle counter-clockwise in degrees. Also checks a few
// pads against the planner's prediction, which confirms the rotation convention.
// The document is NOT saved. Run: __aurisStart("pcb-phase3-place.js", { titleRe: /^Auris phase 3/, timeoutMs: 600000 })
(async () => {
  const PCB_UUID = "1171ec2ee0a2c106";
  const ROWS = __ROWS__;
  const PROBE = __PROBE__;
  const out = [];
  await eda.dmt_EditorControl.openDocument(PCB_UUID);
  await new Promise((r) => setTimeout(r, 1500));
  const comps = await eda.pcb_PrimitiveComponent.getAll();
  const byDes = {};
  for (const c of comps) { try { byDes[c.getState_Designator()] = c; } catch (_) { /* skip */ } }
  let group;
  try { group = await eda.pcb_Document.beginCommandGroup("Auris placement __TAG__"); } catch (_) { group = null; }
  let moved = 0, failed = [];
  for (const [d, x, y, a] of ROWS) {
    const c = byDes[d];
    if (!c) { failed.push(d + ":missing"); continue; }
    try {
      const r = await eda.pcb_PrimitiveComponent.modify(c.getState_PrimitiveId(), { x, y, rotation: a });
      if (r) moved++; else failed.push(d + ":false");
    } catch (e) { failed.push(d + ":" + String((e && e.message) || e).slice(0, 60)); }
  }
  if (group && group.groupId) { try { await eda.pcb_Document.commitCommandGroup(group.groupId); } catch (_) { /* ignore */ } }
  out.push(`moved ${moved} of ${ROWS.length}; failed ${failed.length} ${failed.slice(0, 10).join(" ")}`);
  const after = await eda.pcb_PrimitiveComponent.getAll();
  const byDes2 = {};
  for (const c of after) { try { byDes2[c.getState_Designator()] = c; } catch (_) { /* skip */ } }
  for (const [d, num, px, py] of PROBE) {
    const c = byDes2[d];
    if (!c) continue;
    const pins = await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(c.getState_PrimitiveId());
    const p = pins.find((q) => q.getState_PadNumber() === num);
    if (p) out.push(`${d} pad ${num}: planned (${px}, ${py}) actual (${Math.round(p.getState_X() * 10) / 10}, ${Math.round(p.getState_Y() * 10) / 10}) part at (${Math.round(c.getState_X())}, ${Math.round(c.getState_Y())}) rot ${c.getState_Rotation()}`);
  }
  out.forEach((l, i) => { try { eda.sys_ToastMessage.showMessage(`AURIS ${String(i).padStart(2, "0")} ${l}`, undefined, 300); } catch (_) { /* no toast */ } });
  eda.sys_Dialog.showInformationMessage(out.join("\n"), "Auris phase 3");
})().catch((e) => eda.sys_Dialog.showInformationMessage("Auris phase 3 stopped: " + ((e && e.stack) || e), "Auris phase 3"));
"""


def check_export(src, tag):
    """Check the placement as exported from EasyEDA against placement-<tag>.csv and render it."""
    board = load_board(src, ROOT)
    place = {d: (p.x, p.y, p.angle) for d, p in board.parts.items()}
    planned = {r["designator"]: r for r in csv.DictReader(open(os.path.join(HERE, f"placement-{tag}.csv")))}
    dev = []
    for d, (x, y, a) in place.items():
        r = planned.get(d)
        if not r:
            dev.append((99, d, "not in plan")); continue
        e = math.hypot(x - float(r["x_mm"]), y - float(r["y_mm"]))
        if e > 0.01 or int(float(r["angle"])) % 360 != int(a) % 360:
            dev.append((e, d, f"{x:.3f},{y:.3f},{a} vs plan {r['x_mm']},{r['y_mm']},{r['angle']}"))
    print(f"exported vs plan: {len(place)} parts, {len(dev)} differ" + (f": {sorted(dev, reverse=True)[:5]}" if dev else ""))
    lines, _ = check(board, place, note_targets(board))
    print("\n".join(lines))
    render(board, place, os.path.join(HERE, f"placement-{tag}.png"),
           f"Auris rev A placement {tag}, as exported from EasyEDA (top view, mm)")
    print(f"rendered placement-{tag}.png from {os.path.basename(src)}")


def main():
    if sys.argv[1] == "--check":
        return check_export(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "pass1")
    src, tag = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "pass1")
    board = load_board(src, ROOT)
    place, targets = plan(board)
    lines, _ = check(board, place, targets)
    print("\n".join(lines))
    write_csv(board, place, os.path.join(HERE, f"placement-{tag}.csv"))
    render(board, place, os.path.join(HERE, f"placement-{tag}.png"), f"Auris rev A placement {tag} (top view, mm)")
    write_js(board, place, os.path.join(ROOT, "hardware", "easyeda", "pcb-phase3-place.js"), tag)
    print(f"wrote placement-{tag}.csv/.png and hardware/easyeda/pcb-phase3-place.js")


if __name__ == "__main__":
    main()
