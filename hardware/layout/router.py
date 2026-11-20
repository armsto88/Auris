#!/usr/bin/env python3
"""Auris rev A grid router (phase 4): fan-out vias for the plane nets and A* routing of signal nets
on L1 (top) and L4 (bottom), emitted as an EasyEDA Pro script.

    python3 hardware/layout/router.py fanout <export .epro2> <tag>
    python3 hardware/layout/router.py route  <export .epro2> <tag> [net ...]

State: hardware/layout/routes/<tag>.json holds every track and via this tool has made (mm), so the
next step starts from it (pass --from <tag>). Output: hardware/easyeda/pcb-phase4-<tag>.js, which
creates the tracks and vias through pcb_PrimitiveLine.create / pcb_PrimitiveVia.create (mil).

Model: 0.1 mm cells; obstacles are drawn at true size per layer (pads, tracks, vias, keep-outs,
board edge); a Euclidean distance transform then gives, for the net being routed, the cells whose
track centre keeps clearance + half-width from every foreign copper. Through-hole pads and vias
block every layer. L2 (solid GND) and L3 (power pours) are never routed.
"""
import heapq, json, math, os, sys
from collections import defaultdict

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "hardware", "tools")); sys.path.insert(0, HERE)
from pcb_board import load_board, rot  # noqa: E402
import place  # noqa: E402

CELL = 0.05                                  # mm per cell (0.1 wasted too much clearance at 0.5 mm-pitch pins)
W, H = place.W, place.H
NX, NY = int(round(W / CELL)) + 1, int(round(H / CELL)) + 1
L1, L4 = 1, 2                                # EasyEDA layer ids used for routing
LAYERS = (L1, L4)
CLEAR = 0.20                                 # clearance to foreign copper (rules: 0.152 default, 0.2 for the power/RF classes)
EDGE = 0.50                                  # copper to board edge
VIA_DRILL, VIA_DIA = 0.30, 0.60
VIA_HOLE_GAP = 0.60                          # hole edge to hole edge between vias (rule: other spacing, hole-hole)
WIDTH = {"RF_50": 0.30, "USB_90": 0.25, "PWR_3A": 1.50, "PWR_1A": 0.50, "default": 0.20}
MIN_WIDTH = {"PWR_3A": 0.30, "PWR_1A": 0.25}          # the track rules' minimum per class (owner 2026-11-20: 0.8/0.3 lowered for the small pads)
CLASS = {}
for n in ("ANT_MAIN", "ANT_FEED"):
    CLASS[n] = "RF_50"
for n in ("ESP_USB_DP", "ESP_USB_DN", "USB_DP", "USB_DN"):
    CLASS[n] = "USB_90"
for n in ("BAT_CONN", "BAT_FUSED", "RAW_BAT", "VBAT_SW", "VMODEM", "VBAT_M", "M_L1", "M_L2"):
    CLASS[n] = "PWR_3A"
for n in ("3V3", "BB_L1", "BB_L2", "PANEL_IN", "PANEL_FUSED", "SOLAR_IN", "CHG_SW_RAW", "CHG_SW", "CHARGE_SENSE"):
    CLASS[n] = "PWR_1A"
# plane nets: pads get a via to the plane; L3 pours only exist inside these rectangles (phase4_planes.py)
PLANES = {"GND": None, "3V3": (1.0, 57.0, 44.0, H - 0.5), "VMODEM": (44.5, 53.5, 63.5, 102.0)}
VMODEM_STRIP = (50.5, 70.5, 61.5, 102.0)     # the upper part of the VMODEM pour is only this strip
# routed right after the escape stubs, before fan-out: the converters' inductor and feedback nodes at 0.5 mm-pitch pins.
# BB_L1/BB_L2 at 0.25 mm: a 0.3 mm track cannot leave U206's 0.3 mm pins with 0.2 mm clearance (PWR_1A minimum is 0.3: rule exception for the owner)
EARLY = [("BB_L1", 0.25), ("BB_L2", 0.25), ("FB_3V3", 0.20), ("FB_M", 0.20), ("M_PS", 0.20)]
POUR_RECTS = []     # filled from phase4_power.POURS when the escape step runs (pins inside their own pour need no stub)
KEEPOUT, NONET = -1, -2


def width_of(net):
    return WIDTH.get(CLASS.get(net, "default"), WIDTH["default"])


def cells(v):
    return int(round(v / CELL))


def rcells(v):
    """Cells needed so that copper edges (half a cell beyond a cell centre) keep the distance v."""
    return int(math.ceil((v + CELL / 2) / CELL))


class Raster:
    """Owner map per layer: 0 free, KEEPOUT, NONET (pad without net), or net index + 1."""

    def __init__(self):
        self.occ = {l: np.zeros((NY, NX), dtype=np.int32) for l in LAYERS}
        self.pour = {l: np.zeros((NY, NX), dtype=np.int32) for l in LAYERS}  # pour copper by net: soft for other nets (the pour yields)

    def rect(self, layer, x0, y0, x1, y1, owner):
        i0, i1 = max(0, cells(x0)), min(NX - 1, cells(x1))
        j0, j1 = max(0, cells(y0)), min(NY - 1, cells(y1))
        if i1 >= i0 and j1 >= j0:
            self.occ[layer][j0:j1 + 1, i0:i1 + 1] = owner

    def disc(self, layer, cx, cy, r, owner):
        i0, i1 = max(0, cells(cx - r)), min(NX - 1, cells(cx + r))
        j0, j1 = max(0, cells(cy - r)), min(NY - 1, cells(cy + r))
        if i1 < i0 or j1 < j0:
            return
        ii, jj = np.meshgrid(np.arange(i0, i1 + 1), np.arange(j0, j1 + 1))
        m = (ii * CELL - cx) ** 2 + (jj * CELL - cy) ** 2 <= r * r
        sub = self.occ[layer][j0:j1 + 1, i0:i1 + 1]
        sub[m] = owner

    def segment(self, layer, x0, y0, x1, y1, w, owner):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / (CELL * 0.5)) + 1)
        for k in range(n):
            t = k / (n - 1)
            self.disc(layer, x0 + t * (x1 - x0), y0 + t * (y1 - y0), w / 2, owner)


class Router:
    def __init__(self, board, state=None, with_pours=True):
        self.b = board
        self.nets = sorted(board.net_pads)
        self.idx = {n: i + 1 for i, n in enumerate(self.nets)}
        self.lines = []      # (net, layer, x0, y0, x1, y1, width)
        self.vias = []       # (net, x, y)
        self.ras = Raster()
        self.novia = np.zeros((NY, NX), dtype=bool)   # cells too close to an existing via for another via (hole-to-hole)
        self.pads = defaultdict(list)   # net -> [(layer or None for TH, x, y, w, h)]
        self._base()
        self.pours = []      # (name, net, (x0, y0, x1, y1), priority) on L1
        self.pending_pours = []
        self.escapes = []    # indices into self.lines of the escape stubs (dropped after routing if nothing uses them)
        if state:
            for l in state.get("lines", []):
                self.add_line(*l)
            for v in state.get("vias", []):
                self.add_via(*v)
            self.escapes = list(state.get("escapes", []))
            self.pending_pours = [(name, net, tuple(rect), prio) for name, net, rect, prio in state.get("pours", [])]
            if with_pours:
                for pp in self.pending_pours:
                    self.add_pour(*pp)
                self.pending_pours = []

    # ---------------------------------------------------------------- static obstacles
    def _base(self):
        R = self.ras
        for l in LAYERS:                                       # board edge and the notch
            R.rect(l, -1, -1, W + 1, EDGE, KEEPOUT); R.rect(l, -1, H - EDGE, W + 1, H + 1, KEEPOUT)
            R.rect(l, -1, -1, EDGE, H + 1, KEEPOUT); R.rect(l, W - EDGE, -1, W + 1, H + 1, KEEPOUT)
            nx0, ny0, nx1, ny1 = place.NOTCH
            R.rect(l, nx0 - 1, ny0 - EDGE, nx1 + EDGE, ny1 + 1, KEEPOUT)
            for hx, hy in place.HOLES:                        # M3 heads: no copper of any kind (phase 4a regions)
                R.disc(l, hx, hy, 3.6, KEEPOUT)
        for d, p in self.b.parts.items():
            for hx, hy, hr in getattr(p.fp, "npth", []):          # unplated holes: no copper on any layer around them
                dx, dy = rot(hx, hy, p.angle)
                for l in LAYERS:
                    R.disc(l, p.x + dx, p.y + dy, hr + 0.25, KEEPOUT)
            for q in p.fp.pads:
                net = p.nets.get(q.num)
                owner = self.idx[net] if net else NONET
                x, y = p.pad_xy(q, p.x, p.y, p.angle)
                if q.off != (0.0, 0.0):                       # polygon pad: raster its bounding box, not the pad centre
                    ox, oy = rot(q.off[0], q.off[1], p.angle); x, y = x + ox, y + oy
                w, h = (q.w, q.h) if p.angle % 180 == 0 else (q.h, q.w)
                th = q.layer == 12 or (q.hole and (q.hole.get("width") or 0) > 0)
                for l in (LAYERS if th else (L1,)):
                    R.rect(l, x - w / 2, y - h / 2, x + w / 2, y + h / 2, owner)
                if net:
                    self.pads[net].append((None if th else L1, x, y, w, h))

    # ---------------------------------------------------------------- dynamic copper
    def add_line(self, net, layer, x0, y0, x1, y1, w):
        self.lines.append((net, layer, x0, y0, x1, y1, w))
        self.ras.segment(layer, x0, y0, x1, y1, w, self.idx[net])

    def add_pour(self, name, net, rect, prio):
        """A pour rectangle counts as the net's copper where no foreign copper is nearby (the pour keeps
        clearance from foreign pads by itself); elsewhere in the rectangle nothing is drawn."""
        self.pours.append((name, net, rect, prio))
        x0, y0, x1, y1 = rect
        occ = self.ras.occ[L1]
        i0, i1 = max(0, cells(x0)), min(NX - 1, cells(x1)); j0, j1 = max(0, cells(y0)), min(NY - 1, cells(y1))
        sub = self.ras.pour[L1][j0:j1 + 1, i0:i1 + 1]
        foreign = (occ != 0) & (occ != self.idx[net])
        dist = ndimage.distance_transform_edt(~foreign)[j0:j1 + 1, i0:i1 + 1]
        fill = (occ[j0:j1 + 1, i0:i1 + 1] == 0) & (dist > rcells(CLEAR + 0.3))    # copper surely there: > 0.5 mm from anything foreign
        sub[fill] = self.idx[net]

    def add_via(self, net, x, y):
        self.vias.append((net, x, y))
        for l in LAYERS:
            self.ras.disc(l, x, y, VIA_DIA / 2, self.idx[net])
        r = VIA_HOLE_GAP + VIA_DRILL
        i0, i1 = max(0, cells(x - r)), min(NX - 1, cells(x + r)); j0, j1 = max(0, cells(y - r)), min(NY - 1, cells(y + r))
        ii, jj = np.meshgrid(np.arange(i0, i1 + 1), np.arange(j0, j1 + 1))
        self.novia[j0:j1 + 1, i0:i1 + 1] |= (ii * CELL - x) ** 2 + (jj * CELL - y) ** 2 <= r * r

    # ---------------------------------------------------------------- per-net fields
    def fields(self, net, width=None):
        """allowed[layer] (bool, track centre may be here), own[layer] (bool, own copper), via_ok (bool)."""
        k, w = self.idx[net], (width or width_of(net))
        r_track = rcells(CLEAR + w / 2)           # obstacles are drawn on cell centres; copper edges reach half a cell beyond
        r_via = rcells(CLEAR + VIA_DIA / 2)
        allowed, own, via_ok = {}, {}, np.ones((NY, NX), dtype=bool)
        self.penalty = {}
        for l in LAYERS:
            occ = self.ras.occ[l]; pour = self.ras.pour[l]
            foreign = (occ != 0) & (occ != k)
            dist = ndimage.distance_transform_edt(~foreign)
            allowed[l] = dist > r_track
            own[l] = (occ == k) | (pour == k)
            self.penalty[l] = (pour != 0) & (pour != k)         # crossing a foreign pour: allowed, costed (the pour yields with clearance)
            via_ok &= dist > r_via
        via_ok &= ~self.novia
        own_via = np.zeros((NY, NX), dtype=bool)              # an own via is a free layer change
        for vn, vx, vy in self.vias:
            if vn == net:
                own_via[cells(vy), cells(vx)] = True
        via_ok |= own_via
        self.own_via = own_via
        for layer, x, y, pw, ph in self.pads[net]:          # entry zone: along the pad's centre line and 0.25 mm beyond its long ends,
            if layer is None:                                # laterally only as far as the track stays inside the pad copper
                continue
            if abs(pw - ph) < 0.05:
                hx, hy = max(0.0, (pw - w) / 2), max(0.0, (ph - w) / 2)
            elif pw < ph:
                hx, hy = max(0.0, (pw - w) / 2), ph / 2 + 0.25
            else:
                hx, hy = pw / 2 + 0.25, max(0.0, (ph - w) / 2)
            i0, i1 = max(0, cells(x - hx)), min(NX - 1, cells(x + hx))
            j0, j1 = max(0, cells(y - hy)), min(NY - 1, cells(y + hy))
            allowed[L1][j0:j1 + 1, i0:i1 + 1] = True
        # no via inside or touching an own SMD pad (no via-in-pad)
        for layer, x, y, pw, ph in self.pads[net]:
            if layer is None:
                continue
            m = VIA_DIA / 2 + 0.10
            i0, i1 = max(0, cells(x - pw / 2 - m)), min(NX - 1, cells(x + pw / 2 + m))
            j0, j1 = max(0, cells(y - ph / 2 - m)), min(NY - 1, cells(y + ph / 2 + m))
            via_ok[j0:j1 + 1, i0:i1 + 1] = False
        return allowed, own, via_ok

    # ---------------------------------------------------------------- A*
    def astar(self, allowed, goal, start, via_ok=None, via_cost=None, max_nodes=12_000_000, weight=1.25):
        """start: (layer, i, j); goal[layer]: bool array. Returns [(layer, i, j), ...] or None.
        Array-based (numpy g/parent per layer) with a weighted heuristic: the dict version ran out of its
        node budget on 60 mm nets at the 0.05 mm grid (2026-11-20)."""
        gmask = np.zeros((NY, NX), dtype=bool)
        for l in LAYERS:
            gmask |= goal[l]
        if not gmask.any():
            return None
        hdist = (ndimage.distance_transform_edt(~gmask) * 10.0 * weight).astype(np.float32)   # 10 per straight cell
        if via_cost is None:
            via_cost = int(1.5 / CELL * 10)                       # a via costs as much as 1.5 mm of track
        li = {l: k for k, l in enumerate(LAYERS)}
        al = np.stack([allowed[l] for l in LAYERS])
        gl = np.stack([goal[l] for l in LAYERS])
        G = np.full((len(LAYERS), NY, NX), np.inf, dtype=np.float32)
        PAR = np.full((len(LAYERS), NY, NX), -1, dtype=np.int64)
        pen = getattr(self, "penalty", None)
        PEN = np.stack([pen[l] for l in LAYERS]) if pen is not None else None
        sl, si, sj = start
        s0 = li[sl]
        G[s0, sj, si] = 0.0
        NN = NY * NX
        pq = [(float(hdist[sj, si]), 0.0, (s0 * NY + sj) * NX + si)]
        seen = 0
        steps = ((1, 0, 10), (-1, 0, 10), (0, 1, 10), (0, -1, 10), (1, 1, 14), (1, -1, 14), (-1, 1, 14), (-1, -1, 14))
        while pq:
            f, gc, k = heapq.heappop(pq)
            l, rem = divmod(k, NN); j, i = divmod(rem, NX)
            if gc > G[l, j, i]:
                continue
            if gl[l, j, i]:
                path = []
                while k >= 0:
                    l2, rem2 = divmod(k, NN); j2, i2 = divmod(rem2, NX)
                    path.append((LAYERS[l2], i2, j2)); k = int(PAR[l2, j2, i2])
                return path[::-1]
            seen += 1
            if seen > max_nodes:
                return None
            a = al[l]
            for di, dj, c in steps:
                ni, nj = i + di, j + dj
                if ni < 0 or nj < 0 or ni >= NX or nj >= NY or not a[nj, ni]:
                    continue
                if c == 14 and not (a[j, ni] and a[nj, i]):     # no squeezing diagonally between obstacles
                    continue
                ng = gc + (c * 5 if PEN is not None and PEN[l, nj, ni] else c)
                if ng < G[l, nj, ni]:
                    G[l, nj, ni] = ng; PAR[l, nj, ni] = k
                    heapq.heappush(pq, (ng + hdist[nj, ni], ng, (l * NY + nj) * NX + ni))
            if via_ok is not None and via_ok[j, i]:
                for ol in range(len(LAYERS)):
                    if ol == l or not al[ol, j, i]:
                        continue
                    ng = gc + via_cost
                    if ng < G[ol, j, i]:
                        G[ol, j, i] = ng; PAR[ol, j, i] = k
                        heapq.heappush(pq, (ng + hdist[j, i], ng, (ol * NY + j) * NX + i))
        return None

    # ---------------------------------------------------------------- path -> copper
    def snap_end(self, net, path):
        """EasyEDA joins tracks by their end points: move the last point onto the centre of the own pad,
        the centreline of the own track or the own via that the route lands on."""
        l, i, j = path[-1]
        x, y = i * CELL, j * CELL
        for layer, px, py, pw, ph in self.pads[net]:
            if (layer is None or layer == l) and abs(x - px) <= pw / 2 + 0.05 and abs(y - py) <= ph / 2 + 0.05:
                return path + [(l, cells(px), cells(py))] if (cells(px), cells(py)) != (i, j) else path, (px, py)
        for vn, vx, vy in self.vias:
            if vn == net and math.hypot(x - vx, y - vy) <= VIA_DIA / 2 + 0.05:
                return path, (vx, vy)
        best = None
        for n2, l2, x0, y0, x1, y1, w2 in self.lines:
            if n2 != net or l2 != l:
                continue
            dx, dy = x1 - x0, y1 - y0; L2 = dx * dx + dy * dy
            t = 0 if L2 == 0 else max(0, min(1, ((x - x0) * dx + (y - y0) * dy) / L2))
            qx, qy = x0 + t * dx, y0 + t * dy
            d = math.hypot(x - qx, y - qy)
            if d <= w2 / 2 + 0.05 and (best is None or d < best[0]):
                best = (d, qx, qy)
        return path, (best[1], best[2]) if best else None

    def commit_path(self, net, path, w, allowed=None, tail=None):
        """Split the cell path into straight segments and vias; register them. tail: exact (x, y) the last
        segment must end on (a pad centre or a track centreline), appended as its own short segment."""
        segs, vias = [], []
        run = [path[0]]
        for a, b in zip(path, path[1:]):
            if a[0] != b[0]:                       # layer change: via at this cell
                if len(run) > 1:
                    segs += self._segments(self._simplify(run, allowed))
                vias.append((a[1], a[2]))
                run = [b]
            else:
                run.append(b)
        if len(run) > 1:
            segs += self._segments(self._simplify(run, allowed))
        for (l, i0, j0, i1, j1) in segs:
            self.add_line(net, l, i0 * CELL, j0 * CELL, i1 * CELL, j1 * CELL, w)
        if tail is not None:
            ex, ey = path[-1][1] * CELL, path[-1][2] * CELL
            if math.hypot(tail[0] - ex, tail[1] - ey) > 0.005:
                self.add_line(net, path[-1][0], ex, ey, tail[0], tail[1], w)
        for i, j in vias:
            if any(vn == net and abs(vx - i * CELL) < 0.15 and abs(vy - j * CELL) < 0.15 for vn, vx, vy in self.vias):
                continue                                   # reused an existing own via
            self.add_via(net, i * CELL, j * CELL)
        return len(segs), len(vias)

    @staticmethod
    def _simplify(run, allowed):
        """Greedy string-pulling: replace cell chains by the longest straight lines whose samples stay in allowed cells."""
        if allowed is None or len(run) < 3:
            return run
        l = run[0][0]; al = allowed[l]
        pts = [(c[1], c[2]) for c in run]
        out = [run[0]]; a = 0
        while a < len(pts) - 1:
            b = len(pts) - 1
            while b > a + 1:
                (x0, y0), (x1, y1) = pts[a], pts[b]
                n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
                ok = True
                for k in range(1, n):
                    t = k / n; xi, yi = x0 + t * (x1 - x0), y0 + t * (y1 - y0)
                    i, j = int(round(xi)), int(round(yi))
                    if not al[j, i]:
                        ok = False; break
                    # both cells straddled by the line must be free (no squeezing between obstacles)
                    if abs(xi - i) > 0.3 and abs(yi - j) > 0.3:
                        if not (al[j, i + (1 if xi > i else -1)] and al[j + (1 if yi > j else -1), i]):
                            ok = False; break
                if ok:
                    break
                b -= 1
            out.append(run[b]); a = b
        return out

    @staticmethod
    def _segments(run):
        out = []
        l = run[0][0]
        s = run[0]; prev = run[0]; d = None
        for c in run[1:]:
            dx, dy = c[1] - prev[1], c[2] - prev[2]
            g = math.gcd(abs(dx), abs(dy)) or 1
            nd = (dx // g, dy // g)
            if d is not None and nd != d:
                out.append((l, s[1], s[2], prev[1], prev[2])); s = prev
            d = nd; prev = c
        out.append((l, s[1], s[2], prev[1], prev[2]))
        return [o for o in out if (o[1], o[2]) != (o[3], o[4])]

    # ---------------------------------------------------------------- jobs
    def fanout(self, nets, radius=4.0):
        """One via per pad of each plane net (shared when an own via/track is nearer)."""
        report = []
        for net in nets:
            if net not in self.pads:
                continue
            rect = PLANES.get(net)
            allowed, own, via_ok = self.fields(net)
            if rect:                                   # the via must land inside the L3 pour
                m = np.zeros((NY, NX), dtype=bool)
                x0, y0, x1, y1 = rect
                m[cells(y0) + cells(0.3):cells(y1) - cells(0.3), cells(x0) + cells(0.3):cells(x1) - cells(0.3)] = True
                if net == "VMODEM":                    # the pour is an L: lower block plus the strip
                    sx0, sy0, sx1, sy1 = VMODEM_STRIP
                    m2 = np.zeros((NY, NX), dtype=bool)
                    m2[cells(53.5) + cells(0.3):cells(71.0), cells(44.5) + cells(0.3):cells(63.5) - cells(0.3)] = True
                    m2[cells(sy0):cells(sy1) - cells(0.3), cells(sx0) + cells(0.3):cells(sx1) - cells(0.3)] = True
                    m = m2
                via_ok &= m
            w_stub = max(0.20, MIN_WIDTH.get(CLASS.get(net), 0.20))   # the stub only carries this pad's share
            done = fail = shared = 0
            for layer, x, y, pw, ph in sorted(self.pads[net], key=lambda t: (t[2], t[1])):
                if layer is None:
                    continue                           # through-hole pads reach the planes already
                si, sj = cells(x), cells(y)
                w = w_stub
                centre = (si, sj)
                if not allowed[L1][sj, si]:
                    # pad centre blocked by the clearance of a foreign pad (fine pitch): start from the free
                    # cell nearest the centre, which lies outward along the pad's long axis
                    R_ = cells(1.4)
                    i0, j0 = max(0, si - R_), max(0, sj - R_)
                    cand = np.argwhere(allowed[L1][j0:sj + R_ + 1, i0:si + R_ + 1])
                    if len(cand) == 0:
                        fail += 1; report.append(f"{net}: pad at ({x:.2f},{y:.2f}) has no free cell around it"); continue
                    cj, ci = min(cand, key=lambda c: (c[0] + j0 - sj) ** 2 + (c[1] + i0 - si) ** 2)
                    si, sj = ci + i0, cj + j0
                # goal: an own via/track already nearby, or any via-able cell within the radius
                goal = {}
                near = np.zeros((NY, NX), dtype=bool)
                near[max(0, sj - cells(radius)):sj + cells(radius), max(0, si - cells(radius)):si + cells(radius)] = True
                goal[L1] = (via_ok | own[L1]) & near & ~self._padmask(net)
                goal[L4] = np.zeros((NY, NX), dtype=bool)
                path = self.astar(allowed, goal, (L1, si, sj), via_ok=None, max_nodes=250000)
                if path is None:
                    fail += 1; report.append(f"{net}: no via spot within {radius} mm of pad ({x:.2f},{y:.2f})"); continue
                end = path[-1]
                if own[L1][end[2], end[1]] and not via_ok[end[2], end[1]]:
                    shared += 1
                if (path[0][1], path[0][2]) != centre:          # fine pitch: the stub starts at the pad centre
                    self.add_line(net, L1, centre[0] * CELL, centre[1] * CELL, path[0][1] * CELL, path[0][2] * CELL, w)
                ns, _ = self.commit_path(net, path, w, allowed)
                if not own[L1][end[2], end[1]] or via_ok[end[2], end[1]]:
                    if not any(abs(vx - end[1] * CELL) < 0.05 and abs(vy - end[2] * CELL) < 0.05 for vn, vx, vy in self.vias):
                        self.add_via(net, end[1] * CELL, end[2] * CELL)
                done += 1
                allowed, own, via_ok = self.fields(net)      # refresh: the new via and stub are obstacles for the next pad
                if rect:
                    via_ok &= m
            report.append(f"{net}: {done} pads fanned out ({shared} to existing own copper), {fail} failed")
        return report

    VIA_ESCAPE = {"U401"}                                # pins escape to a via under the part's body

    def escape(self, parts, radius=2.5):
        """For every pad of the listed parts whose net is routable, add a short stub from the pad centre to the
        nearest clearly free cell, so later nets start outside the pin field and keep their exit corridor."""
        report = []
        for des in parts:
            p = self.b.parts.get(des)
            if not p:
                continue
            done = fail = 0
            for q in p.fp.pads:
                net = p.nets.get(q.num)
                if not net or net in PLANES or len(self.b.net_pads.get(net, [])) < 2:
                    continue
                if CLASS.get(net) in ("PWR_1A", "PWR_3A", "RF_50") or net in {n_ for n_, _ in EARLY}:
                    continue
                x, y = p.pad_xy(q, p.x, p.y, p.angle)
                if any(x0 + 0.1 <= x <= x1 - 0.1 and y0 + 0.1 <= y <= y1 - 0.1 for name, pnet, (x0, y0, x1, y1), prio in POUR_RECTS if pnet == net):
                    continue                                   # the pour joins this pin
                w = max(0.20, MIN_WIDTH.get(CLASS.get(net), 0.20))   # the class minimum (0.8 mm cannot leave a 0.25 mm pin: skipped below)
                if w > 0.3 and min(q.w, q.h) < 0.5:
                    continue
                allowed, own, via_ok = self.fields(net, width=w)
                occ = self.ras.occ[L1]; k = self.idx[net]
                foreign = (occ != 0) & (occ != k)
                dist = ndimage.distance_transform_edt(~foreign)
                si, sj = cells(x), cells(y)
                near = np.zeros((NY, NX), dtype=bool)
                near[max(0, sj - cells(radius)):sj + cells(radius), max(0, si - cells(radius)):si + cells(radius)] = True
                if des in self.VIA_ESCAPE:
                    bx0, by0, bx1, by1 = p.extent(0, p.x, p.y, p.angle)
                    body = np.zeros((NY, NX), dtype=bool)
                    body[cells(by0 + 0.6):cells(by1 - 0.6), cells(bx0 + 0.6):cells(bx1 - 0.6)] = True
                    goal = {L1: via_ok & near & body & ~self._padmask(net), L4: np.zeros((NY, NX), dtype=bool)}
                else:
                    goal = {L1: allowed[L1] & near & (dist > rcells(CLEAR + w / 2) + cells(0.25)) & ~self._padmask(net), L4: np.zeros((NY, NX), dtype=bool)}
                path = self.astar(allowed, goal, (L1, si, sj), via_ok=None, max_nodes=160000)
                if path is None or len(path) < 2:
                    fail += 1; continue
                n0 = len(self.lines)
                self.commit_path(net, path, w, allowed); done += 1
                if des in self.VIA_ESCAPE:
                    end = path[-1]; self.add_via(net, end[1] * CELL, end[2] * CELL)
                else:
                    self.escapes += list(range(n0, len(self.lines)))
            report.append(f"{des}: {done} pins escaped, {fail} without room")
        return report

    def _padmask(self, net):
        m = np.zeros((NY, NX), dtype=bool)
        for layer, x, y, pw, ph in self.pads[net]:
            i0, i1 = max(0, cells(x - pw / 2)), min(NX - 1, cells(x + pw / 2))
            j0, j1 = max(0, cells(y - ph / 2)), min(NY - 1, cells(y + ph / 2))
            m[j0:j1 + 1, i0:i1 + 1] = True
        return m

    def route_net(self, net, layers_allowed=LAYERS, width=None, max_nodes=12_000_000):
        """Connect every pad of the net: nearest-first spanning tree. The tree is the copper island that holds the
        first pad (own tracks, vias, pours, pads, labelled on the union of both layers); every other pad is
        routed to that island, so a pin's lone escape stub or via is never mistaken for the tree."""
        pads = self.pads.get(net, [])
        if len(pads) < 2:
            return f"{net}: {len(pads)} pad"
        w = width or width_of(net)
        order = sorted(pads, key=lambda t: (t[2], t[1]))
        own_rects = [rect for name, pnet, rect, prio in self.pours if pnet == net]
        def in_own_pour(pad):
            layer, x, y, pw, ph = pad
            return any(x0 + 0.1 <= x <= x1 - 0.1 and y0 + 0.1 <= y <= y1 - 0.1 for x0, y0, x1, y1 in own_rects)
        pre = [pd for pd in order if in_own_pour(pd)]
        first = (pre or order)[0]
        padmask = self._padmask(net)

        def restrict(allowed):
            if layers_allowed != LAYERS:
                for l in LAYERS:
                    if l not in layers_allowed:
                        allowed[l][:] = False
            return allowed

        def islands(own):
            lab, _n = ndimage.label(own[L1] | own[L4] | padmask)
            labs = {int(lab[cells(first[2]), cells(first[1])])} | {int(lab[cells(pd[2]), cells(pd[1])]) for pd in pre}
            labs.discard(0)
            return lab, labs

        allowed, own, via_ok = self.fields(net, width=w); w_cur = w; restrict(allowed)
        lab, tree_labels = islands(own)
        connected = 1
        remaining = [pd for pd in order if pd != first]
        done_pre = [pd for pd in remaining if int(lab[cells(pd[2]), cells(pd[1])]) in tree_labels]
        connected += len(done_pre)
        remaining = [pd for pd in remaining if pd not in done_pre]
        fails = []
        while remaining:
            tree_m = np.isin(lab, list(tree_labels))
            tj, ti = np.nonzero(tree_m)
            best, bi = None, -1
            for k, (layer, x, y, pw, ph) in enumerate(remaining):
                d = np.min((ti * CELL - x) ** 2 + (tj * CELL - y) ** 2) if len(ti) else 0
                if best is None or d < best:
                    best, bi = d, k
            layer, x, y, pw, ph = remaining.pop(bi)
            w_pad = w if layer is None else min(w, max(0.20, round(min(pw, ph) - 0.15, 2)))
            if w_pad != w_cur:
                allowed, own, via_ok = self.fields(net, width=w_pad); w_cur = w_pad; restrict(allowed)
            cur = np.zeros((NY, NX), dtype=bool)
            self._mark_pad(cur, (layer, x, y, pw + 0.6, ph + 0.6))
            def goals(allowed_, own_):
                g = {L1: tree_m & own_[L1] & allowed_[L1] & ~cur, L4: tree_m & own_[L4] & allowed_[L4] & ~cur}
                for pd in [first] + pre + done_pre:                 # tree pads count even where clearance bites
                    m = np.zeros((NY, NX), dtype=bool); self._mark_pad(m, pd); g[L1] |= m & allowed_[L1] & ~cur
                return g
            start = (L1, cells(x), cells(y))
            path = self.astar(allowed, goals(allowed, own), start, via_ok=via_ok if len(layers_allowed) > 1 else None, max_nodes=max_nodes)
            w_used = w_pad
            if path is None and MIN_WIDTH.get(CLASS.get(net), 0.2) < w_pad:
                w_used = MIN_WIDTH.get(CLASS.get(net), 0.2)
                allowed2, own2, via_ok2 = self.fields(net, width=w_used); restrict(allowed2)
                path = self.astar(allowed2, goals(allowed2, own2), start, via_ok=via_ok2 if len(layers_allowed) > 1 else None, max_nodes=max_nodes)
                if path is not None:
                    allowed = allowed2
            if path is None:
                fails.append(f"({x:.1f},{y:.1f})")
                continue
            path, tail = self.snap_end(net, path)
            self.commit_path(net, path, w_used, allowed, tail=tail)
            connected += 1
            allowed, own, via_ok = self.fields(net, width=w); w_cur = w; restrict(allowed)
            lab, tree_labels = islands(own)
            joined_now = [pd for pd in remaining if int(lab[cells(pd[2]), cells(pd[1])]) in tree_labels]
            connected += len(joined_now); done_pre += joined_now
            remaining = [pd for pd in remaining if pd not in joined_now]
        return f"{net}: {connected}/{len(pads)} pads connected" + (f", failed at {' '.join(fails)}" if fails else "")

    @staticmethod
    def _mark_pad(mask, pad):
        layer, x, y, pw, ph = pad
        i0, i1 = max(0, cells(x - pw / 2)), min(NX - 1, cells(x + pw / 2))
        j0, j1 = max(0, cells(y - ph / 2)), min(NY - 1, cells(y + ph / 2))
        mask[j0:j1 + 1, i0:i1 + 1] = True

    # ---------------------------------------------------------------- output
    def state(self):
        return {"lines": [list(l) for l in self.lines], "vias": [list(v) for v in self.vias],
                "pours": [[name, net, list(rect), prio] for name, net, rect, prio in self.pours], "escapes": list(self.escapes)}

    def drop_unused_escapes(self):
        """Remove escape stubs that no later track or via of their net touches (they would be dangling copper)."""
        used = set()
        esc = set(self.escapes)
        by_net = defaultdict(list)
        for idx, (net, l, x0, y0, x1, y1, w) in enumerate(self.lines):
            if idx not in esc:
                by_net[net].append((x0, y0, x1, y1, w))
        vias_by_net = defaultdict(list)
        for net, x, y in self.vias:
            vias_by_net[net].append((x, y))
        def near_seg(px, py, seg, tol):
            x0, y0, x1, y1, w = seg
            dx, dy = x1 - x0, y1 - y0; L2 = dx * dx + dy * dy
            t = 0 if L2 == 0 else max(0, min(1, ((px - x0) * dx + (py - y0) * dy) / L2))
            return math.hypot(px - (x0 + t * dx), py - (y0 + t * dy)) <= tol
        groups = defaultdict(list)          # stubs of one pad form a chain: group by net and first point
        for idx in sorted(esc):
            net, l, x0, y0, x1, y1, w = self.lines[idx]
            groups[(net, round(x0, 2), round(y0, 2))].append(idx)
        drop = []
        for key, idxs in groups.items():
            net = key[0]
            chain = [self.lines[i] for i in idxs]
            touched = False
            for (_, l, x0, y0, x1, y1, w) in chain:
                for (ax0, ay0, ax1, ay1, aw) in by_net[net]:
                    for (ex, ey) in ((ax0, ay0), (ax1, ay1)):
                        if near_seg(ex, ey, (x0, y0, x1, y1, w), w / 2 + aw / 2 + 0.02):
                            touched = True; break
                    if touched:
                        break
                if not touched:
                    for (vx, vy) in vias_by_net[net]:
                        if near_seg(vx, vy, (x0, y0, x1, y1, w), VIA_DIA / 2 + w / 2 + 0.02):
                            touched = True; break
                if touched:
                    break
            if not touched:
                drop += idxs
        keep = [l for i, l in enumerate(self.lines) if i not in set(drop)]
        self.lines = keep
        self.escapes = []
        return len(drop)

    def write_js(self, path, tag, lines, vias):
        MIL = 1 / 0.0254
        rows_l = [[n, l, round(x0 * MIL, 2), round(y0 * MIL, 2), round(x1 * MIL, 2), round(y1 * MIL, 2), round(w * MIL, 3)] for n, l, x0, y0, x1, y1, w in lines]
        rows_v = [[n, round(x * MIL, 2), round(y * MIL, 2)] for n, x, y in vias]
        js = TEMPLATE.replace("__TAG__", tag).replace("__LINES__", json_rows(rows_l)).replace("__VIAS__", json_rows(rows_v))
        js = js.replace("__DRILL__", str(round(VIA_DRILL * MIL, 2))).replace("__DIA__", str(round(VIA_DIA * MIL, 2)))
        open(path, "w").write(js)


def json_rows(rows):
    return "[\n" + ",\n".join("    " + json.dumps(r) for r in rows) + "\n  ]"


TEMPLATE = r"""// Auris rev A layout, phase 4 __TAG__: tracks and vias generated by hardware/layout/router.py
// (do not edit by hand). Coordinates in mil, board origin bottom-left; layers 1 top, 2 bottom.
// The document is NOT saved. Run: __aurisStart("pcb-phase4-__TAG__.js", { titleRe: /^Auris phase 4/ })
(async () => {
  const PCB_UUID = "1171ec2ee0a2c106";
  const LINES = __LINES__;
  const VIAS = __VIAS__;
  const out = [];
  const msg = (e) => String((e && e.message) || e).slice(0, 80);
  await eda.dmt_EditorControl.openDocument(PCB_UUID);
  await new Promise((r) => setTimeout(r, 1500));
  let group = null;
  try { group = await eda.pcb_Document.beginCommandGroup("Auris phase 4 __TAG__"); } catch (_) { group = null; }
  let nl = 0, nv = 0; const errs = [];
  for (const [net, x, y] of VIAS) {
    try { const v = await eda.pcb_PrimitiveVia.create(net, x, y, __DRILL__, __DIA__, 0, null, null, false); if (v) nv++; else errs.push(`via ${net} ${x},${y}: ${v}`); }
    catch (e) { errs.push(`via ${net} ${x},${y}: ${msg(e)}`); }
  }
  for (const [net, layer, x0, y0, x1, y1, w] of LINES) {
    try { const l = await eda.pcb_PrimitiveLine.create(net, layer, x0, y0, x1, y1, w, false); if (l) nl++; else errs.push(`line ${net}: ${l}`); }
    catch (e) { errs.push(`line ${net} ${x0},${y0}: ${msg(e)}`); }
  }
  let rebuilt = "?";
  try { const r = await eda.pcb_PrimitivePour.rebuildAllCopperRegions(); rebuilt = Array.isArray(r) ? r.length : String(r); } catch (e) { rebuilt = "ERR " + msg(e); }
  if (group && group.groupId) { try { await eda.pcb_Document.commitCommandGroup(group.groupId); } catch (_) { /* ignore */ } }
  out.push(`vias ${nv} of ${VIAS.length}; lines ${nl} of ${LINES.length}; errors ${errs.length} ${errs.slice(0, 6).join(" | ")}; pours rebuilt: ${rebuilt}`);
  eda.sys_Dialog.showInformationMessage(out.join("\n"), "Auris phase 4 __TAG__");
})().catch((e) => eda.sys_Dialog.showInformationMessage("Auris phase 4 __TAG__ stopped: " + ((e && e.stack) || e), "Auris phase 4 __TAG__"));
"""


def render(router, path, window=None, title="", pours=None):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle
    x0, y0, x1, y1 = window or (0, 0, W, H)
    fig, ax = plt.subplots(figsize=((x1 - x0) * 0.4, (y1 - y0) * 0.4), dpi=100)
    b = router.b
    for d, p in b.parts.items():
        e = p.extent(0, p.x, p.y, p.angle)
        if e[2] < x0 or e[0] > x1 or e[3] < y0 or e[1] > y1:
            continue
        ax.add_patch(Rectangle((e[0], e[1]), e[2] - e[0], e[3] - e[1], fill=False, lw=0.4, color="gray"))
        for q in p.fp.pads:
            px, py = p.pad_xy(q, p.x, p.y, p.angle)
            w, h = (q.w, q.h) if p.angle % 180 == 0 else (q.h, q.w)
            ax.add_patch(Rectangle((px - w / 2, py - h / 2), w, h, color="goldenrod", alpha=0.7, lw=0))
        ax.text((e[0] + e[2]) / 2, (e[1] + e[3]) / 2, d, fontsize=4, ha="center", va="center", color="k")
    for name, net, (px0, py0, px1, py1), prio in (pours or getattr(router, "pours", [])):
        ax.add_patch(Rectangle((px0, py0), px1 - px0, py1 - py0, fill=True, alpha=0.12, color="purple", lw=0.5))
        ax.text(px0 + 0.3, py1 - 0.6, name, fontsize=5, color="purple")
    for n, l, ax0, ay0, ax1, ay1, w in router.lines:
        ax.plot([ax0, ax1], [ay0, ay1], color="red" if l == L1 else "blue", lw=max(0.5, w * 4), alpha=0.8, solid_capstyle="round")
    for n, vx, vy in router.vias:
        ax.add_patch(Circle((vx, vy), VIA_DIA / 2, color="green", alpha=0.8))
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.set_title(title, fontsize=8)
    ax.grid(True, lw=0.2, alpha=0.4)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def main():
    mode, src, tag = sys.argv[1:4]
    extra = sys.argv[4:]
    frm = None
    if "--from" in extra:
        k = extra.index("--from"); frm = extra[k + 1]; extra = extra[:k] + extra[k + 2:]
    board = load_board(src, ROOT)
    routes_dir = os.path.join(HERE, "routes"); os.makedirs(routes_dir, exist_ok=True)
    state = json.load(open(os.path.join(routes_dir, f"{frm}.json"))) if frm else None
    r = Router(board, state, with_pours=(mode != "route"))
    n_lines0, n_vias0 = len(r.lines), len(r.vias)
    if mode == "escape":
        try:
            import phase4_power
            POUR_RECTS[:] = [(n_, net_, tuple(rect_), pr_) for n_, net_, rect_, pr_ in phase4_power.POURS]
        except Exception as e:  # noqa: BLE001
            print("pour rectangles not loaded:", e)
        parts = extra or ["U102", "U401", "U301", "U302", "U201", "U206", "U207", "U103", "U104", "U105", "U203", "U204", "U205", "U208"]
        for line in r.escape(parts):
            print(line)
        # the tightest nets go in before the fan-out vias take the space around their pins
        for net, w in EARLY:
            print("early:", r.route_net(net, layers_allowed=(L1,), width=w))
    elif mode == "fanout":
        # 3V3 first (fewer options), then GND. VMODEM's pads sit in U207's output loop at 0.7 mm gaps, too
        # tight for 0.2 mm stubs with 0.2 mm clearance: that loop is joined by an L1 pour (phase 4c) instead.
        nets = extra or ["3V3", "GND"]
        for line in r.fanout(nets):
            print(line)
    elif mode == "route":
        # options: --l1 (top layer only), --width W, --batch FILE (one net per line, "#" comments; "L1" or "w=0.5" after the name)
        layers, width = LAYERS, None
        if "--l1" in extra:
            layers = (L1,); extra.remove("--l1")
        if "--width" in extra:
            k = extra.index("--width"); width = float(extra[k + 1]); extra = extra[:k] + extra[k + 2:]
        jobs = []
        if "--batch" in extra:
            k = extra.index("--batch")
            for line in open(extra[k + 1]):
                line = line.split("#")[0].strip()
                if not line:
                    continue
                toks = line.split()
                jl, jw = layers, width
                for t in toks[1:]:
                    if t == "L1":
                        jl = (L1,)
                    elif t.startswith("w="):
                        jw = float(t[2:])
                jobs.append((toks[0], jl, jw))
            extra = extra[:k] + extra[k + 2:]
        jobs += [(n, layers, width) for n in extra]
        import time
        done = 0
        if r.pending_pours:
            # nets with a pad inside a pour rectangle (other than the pour's net) go first, without the pours
            inside = set()
            for name, pnet, (x0, y0, x1, y1), prio in r.pending_pours:
                for net2, plist in r.pads.items():
                    if net2 == pnet or net2 in PLANES:
                        continue
                    if any(x0 - 0.5 <= x <= x1 + 0.5 and y0 - 0.5 <= y <= y1 + 0.5 for layer, x, y, pw, ph in plist):
                        inside.add(net2)
            first = [j for j in jobs if j[0] in inside]; rest = [j for j in jobs if j[0] not in inside]
            print(f"local nets routed before the pours: {len(first)}: {' '.join(j[0] for j in first)}", flush=True)
            jobs = first + [None] + rest
        for job in jobs:
            if job is None:
                for pp in r.pending_pours:
                    r.add_pour(*pp)
                r.pending_pours = []
                print("pours now counted as copper", flush=True)
                continue
            net, jl, jw = job
            t0 = time.time()
            # a top-layer-only attempt gets a small budget: if it cannot be done there, the two-layer retry follows
            line = r.route_net(net, layers_allowed=jl, width=jw, max_nodes=(1_500_000 if jl != LAYERS else 12_000_000))
            if "failed" in line and jl != LAYERS:
                line += " | retry on both layers: " + r.route_net(net, layers_allowed=LAYERS, width=jw)
            print(f"{line}  [{time.time() - t0:.0f} s]", flush=True)
            done += 1
            if done % 10 == 0:          # checkpoint: state and script so far
                json.dump(r.state(), open(os.path.join(routes_dir, f"{tag}.json"), "w"))
                r.write_js(os.path.join(ROOT, "hardware", "easyeda", f"pcb-phase4-{tag}.js"), tag, r.lines[n_lines0:], r.vias[n_vias0:])
    else:
        sys.exit("mode: escape | fanout | route")
    if mode == "route" and r.escapes:
        esc_before = [r.lines[i] for i in r.escapes]
        dropped = r.drop_unused_escapes()
        survivors = [l for l in esc_before if l in r.lines]
        esc_vias = [tuple(v) for v in json.load(open(os.path.join(routes_dir, "escape.json"))).get("vias", [])]   # the via escapes (U401)
        r.write_js(os.path.join(ROOT, "hardware", "easyeda", "pcb-phase4-escape.js"), "escape", survivors, esc_vias)
        print(f"escape stubs: {len(esc_before)} made, {dropped} unused dropped, {len(survivors)} kept (pcb-phase4-escape.js rewritten)")
        n_lines0 -= dropped                     # the new-lines slice shifts with the removed stubs
    json.dump(r.state(), open(os.path.join(routes_dir, f"{tag}.json"), "w"))
    new_lines, new_vias = r.lines[n_lines0:], r.vias[n_vias0:]
    js = os.path.join(ROOT, "hardware", "easyeda", f"pcb-phase4-{tag}.js")
    r.write_js(js, tag, new_lines, new_vias)
    render(r, os.path.join(routes_dir, f"{tag}.png"), title=f"Auris routing {tag}")
    print(f"{tag}: +{len(new_lines)} lines, +{len(new_vias)} vias (total {len(r.lines)} / {len(r.vias)}); wrote routes/{tag}.json, routes/{tag}.png, {os.path.relpath(js, ROOT)}")


if __name__ == "__main__":
    main()
