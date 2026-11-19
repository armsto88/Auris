#!/usr/bin/env python3
"""Auris PCB model read from an EasyEDA Pro .epro2 export, for placement planning and checks.

Units: mm, board coordinates (Cartesian, Y up, origin at the board's bottom-left corner as set
in phase 1). EasyEDA stores mil; footprint pad coordinates are in the footprint frame, and a pad
on the board is at component (x, y) + R(angle) * (pad x, pad y), angle counter-clockwise in
degrees (checked against the editor in phase 3; see hardware/layout/easyeda-pcb-api.md).

    from pcb_board import load_board
    b = load_board("hardware/2026-11-19/AURIS_2026-11-19_phase2.epro2")
    b.parts["U301"].extent()   # local (x0, y0, x1, y1) of body outline and pads, mm
"""
import csv, json, math, os, re, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from easyeda_check import read_epru  # noqa: E402

MIL = 0.0254
BODY_LAYER = 48          # Component Shape Layer: the footprint's body outline
# Bodies (mm, footprint frame) for footprints that have no body outline on layer 48, so parts
# are not placed under them. TF-030: JLC gives 13.1 x 13.8 mm; centred, rounded up to 14 mm.
BODY_OVERRIDE = {"CONN-SMD_TF-030": [(-6.55, -7.0), (6.55, 7.0)]}
SHEETS = ["audio-frontend", "power", "lte", "mcu"]


def path_points(path):
    """Points of an EasyEDA polygon source (mil): handles L, ARC/CARC (end points), R, CIRCLE, C."""
    if isinstance(path, str):
        try:
            path = json.loads(path)
        except ValueError:
            return []
    pts, i, n = [], 0, len(path)
    if n and isinstance(path[0], list):            # complex polygon: list of sources
        for p in path:
            pts += path_points(p)
        return pts
    while i < n:
        t = path[i]
        if t == "R" and i + 6 < n + 1:
            x, y, w, h = path[i + 1:i + 5]
            pts += [(x, y), (x + w, y - h), (x + w, y), (x, y - h)]
            i += 7
        elif t == "CIRCLE":
            cx, cy, r = path[i + 1:i + 4]
            pts += [(cx - r, cy - r), (cx + r, cy + r)]
            i += 4
        elif t in ("ARC", "CARC"):
            pts.append((path[i + 2], path[i + 3]))  # angle, end x, end y
            i += 4
        elif t in ("L", "C"):
            i += 1
        elif isinstance(t, (int, float)) and i + 1 < n and isinstance(path[i + 1], (int, float)):
            pts.append((t, path[i + 1]))
            i += 2
        else:
            i += 1
    return pts


class Pad:
    def __init__(self, b):
        dp = b.get("defaultPad") or {}
        self.num = str(b["num"])
        self.x, self.y = b["centerX"] * MIL, b["centerY"] * MIL
        self.shape = dp.get("padType")
        w, h = dp.get("width", 0) * MIL, dp.get("height", 0) * MIL
        if (round(b.get("padAngle") or 0) % 180) == 90:
            w, h = h, w
        self.w, self.h = w, h
        self.layer = b.get("layerId")
        self.hole = b.get("hole")


class Footprint:
    def __init__(self, uuid, name, recs):
        self.uuid, self.name = uuid, name
        self.pads = [Pad(b) for h, b in recs if h["type"] == "PAD"]
        body = []
        for h, b in recs:
            if h["type"] in ("POLY", "FILL") and str(b.get("layerId")) == str(BODY_LAYER):
                body += [(x * MIL, y * MIL) for x, y in path_points(b.get("path"))]
        self.body = body or list(BODY_OVERRIDE.get(name, []))

    def extent(self, margin=0.0):
        xs, ys = [], []
        for x, y in self.body:
            xs.append(x); ys.append(y)
        for p in self.pads:
            xs += [p.x - p.w / 2, p.x + p.w / 2]; ys += [p.y - p.h / 2, p.y + p.h / 2]
        if not xs:
            return (-0.5 - margin, -0.5 - margin, 0.5 + margin, 0.5 + margin)
        return (min(xs) - margin, min(ys) - margin, max(xs) + margin, max(ys) + margin)


def rot(x, y, angle):
    a = math.radians(angle)
    c, s = round(math.cos(a), 12), round(math.sin(a), 12)
    return x * c - y * s, x * s + y * c


class Part:
    def __init__(self, des, cid, fp, x, y, angle, layer):
        self.des, self.id, self.fp = des, cid, fp
        self.x, self.y, self.angle, self.layer = x, y, angle, layer
        self.nets = {}          # pad num -> net
        self.fit = True
        self.block = None
        self.note = ""

    def extent(self, margin=0.0, x=None, y=None, angle=None):
        """Board-frame axis-aligned box for the part at (x, y, angle) (defaults: current)."""
        x = self.x if x is None else x
        y = self.y if y is None else y
        angle = self.angle if angle is None else angle
        x0, y0, x1, y1 = self.fp.extent(margin)
        cs = [rot(cx, cy, angle) for cx, cy in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
        return (x + min(c[0] for c in cs), y + min(c[1] for c in cs), x + max(c[0] for c in cs), y + max(c[1] for c in cs))

    def pad_xy(self, pad, x=None, y=None, angle=None):
        x = self.x if x is None else x
        y = self.y if y is None else y
        angle = self.angle if angle is None else angle
        dx, dy = rot(pad.x, pad.y, angle)
        return x + dx, y + dy


class Board:
    def __init__(self):
        self.parts = {}
        self.outline = None      # (x0, y0, x1, y1) mm
        self.holes = []          # (x, y, d) mm
        self.net_pads = defaultdict(list)   # net -> [(des, pad num)]

    def pads_on(self, net):
        return self.net_pads.get(net, [])


def _footprint_of_device(docs):
    """Device uuid -> footprint uuid, for parts without a Footprint attribute (the test pads)."""
    out = {}
    for d in docs:
        if d["type"] != "DEVICE":
            continue
        for h, b in d["recs"]:
            if not isinstance(b, dict):
                continue
            for k in ("footprint", "Footprint"):
                v = b.get(k) if k in b else (b.get("value") if b.get("key") == k else None)
                if isinstance(v, dict):
                    v = v.get("uuid")
                if isinstance(v, str) and re.fullmatch(r"[0-9a-f]{16}", v):
                    out[d["uuid"]] = v
    return out


def load_board(path, root=None):
    root = root or os.path.dirname(os.path.dirname(HERE))
    docs = read_epru(path)
    fps = {}
    for d in docs:
        if d["type"] == "FOOTPRINT":
            meta = [b for h, b in d["recs"] if h["type"] == "META"]
            fps[d["uuid"]] = Footprint(d["uuid"], meta[0].get("title") if meta else d["uuid"], d["recs"])
    dev_fp = _footprint_of_device(docs)
    tp_fp = next((u for u, f in fps.items() if f.name.startswith("Test-Point")), None)
    pcb = [d for d in docs if d["type"] == "PCB"][0]
    comps, attrs = {}, defaultdict(dict)
    for h, b in pcb["recs"]:
        if h["type"] == "COMPONENT":
            comps[h["id"]] = b
        elif h["type"] == "ATTR" and b.get("parentId"):
            attrs[b["parentId"]][b.get("key")] = b.get("value")
    board = Board()
    for cid, c in comps.items():
        a = attrs.get(cid, {})
        des = a.get("Designator")
        fpu = a.get("Footprint") or dev_fp.get(a.get("Device")) or (tp_fp if str(des).startswith("TP") else None)
        if not des or fpu not in fps:
            raise SystemExit(f"{path}: component {cid} ({des}) has no footprint I can resolve")
        board.parts[des] = Part(des, cid, fps[fpu], c["x"] * MIL, c["y"] * MIL, c.get("angle") or 0, c.get("layerId"))
    by_id = {p.id: p for p in board.parts.values()}
    for h, b in pcb["recs"]:
        if h["type"] == "PAD_NET":
            _, cid, num, _ = json.loads(h["id"])
            p = by_id.get(cid)
            if p and b.get("padNet"):
                p.nets[str(num)] = b["padNet"]
                board.net_pads[b["padNet"]].append((p.des, str(num)))
    # outline and holes (free primitives)
    for h, b in pcb["recs"]:
        if h["type"] == "PRIMITIVE":
            pass
    # fit / notes / blocks from the repo
    for sheet in SHEETS:
        bom = os.path.join(root, "hardware", sheet, f"{sheet}-bom.csv")
        if os.path.exists(bom):
            for r in csv.DictReader(open(bom)):
                for des in re.split(r"[,\s]+", r.get("designators", "")):
                    if des in board.parts:
                        board.parts[des].fit = r.get("fit", "Y").strip().upper() != "N"
                        board.parts[des].note = r.get("notes", "")
    try:
        from easyeda_capture import load_blocks
        for k, ds in load_blocks().items():
            for des in ds:
                if des in board.parts:
                    board.parts[des].block = k
    except Exception as e:  # noqa: BLE001
        print(f"blocks not loaded: {e}", file=sys.stderr)
    return board


if __name__ == "__main__":
    b = load_board(sys.argv[1])
    print(f"{len(b.parts)} parts, {len(b.net_pads)} nets")
