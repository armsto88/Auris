#!/usr/bin/env python3
"""Phase 4c: the power loops, the battery path and the RF feed as explicit copper.

    python3 hardware/layout/phase4_power.py <export .epro2> --from fanout

Writes hardware/easyeda/pcb-phase4-power.js and hardware/layout/routes/power.json (the fan-out state
plus everything added here, so the router starts from it). All numbers in mm, board frame.

What it adds, for the owner to review in the editor (handover phase 4: switching loops, battery
path and RF are owner-reviewed):
- L1 pours above the top-side GND pour: EasyEDA's pour order is unique per layer and the LOWER number
  wins (found 2026-11-20: pours created under a GND pour of order 1 never filled), so the script
  re-creates the GND L1 pour last with priority 99 that join the pads of one net inside a
  rectangle; EasyEDA keeps clearance from every foreign pad by itself: VMODEM and VBAT_SW at
  U207, VBAT_SW and 3V3 at U206, SOLAR_IN and CHG_SW in the charger, RAW_BAT along the battery
  path, VBAT_M under the modem's capacitor array, VMODEM at R301;
- explicit wide tracks: U207's inductor nodes M_L1/M_L2 (0.8 mm, the class minimum, because the
  pins are 0.25 mm at 0.5 mm pitch), BAT_CONN and BAT_FUSED (1.0 mm), the VBAT_M stub onto U301's
  pads 42/43 (1.2 mm);
- the 50 ohm feed: U301 pad 35 -> R310 -> J302 as 0.30 mm tracks (RF_50 rule: 0.30 fixed, 0.20
  mm gap to the L1 ground pour) with a GND via fence 0.85 mm either side at 0.9 mm pitch;
- via arrays: 4 GND thermal vias in U207's exposed pad, 4 VMODEM vias from the output pour to the
  L3 strip and 3 at R301's end of the strip.
"""
import json, math, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "hardware", "tools")); sys.path.insert(0, HERE)
from pcb_board import load_board  # noqa: E402
import router  # noqa: E402
from router import Router, cells, L1, VIA_DIA  # noqa: E402

POURS = [   # name, net, (x0, y0, x1, y1), priority
    ("VMODEM out", "VMODEM", (44.8, 62.9, 63.4, 70.3), 2),
    ("VMODEM out b", "VMODEM", (51.0, 60.4, 63.4, 63.0), 2),
    ("VMODEM top", "VMODEM", (51.6, 98.8, 54.7, 102.0), 2),
    ("VBAT_SW in", "VBAT_SW", (41.4, 52.6, 48.0, 62.2), 2),     # stops before U207 pins 12-14 so they keep an exit
    ("VBAT_SW bridge", "VBAT_SW", (50.6, 50.6, 60.2, 53.9), 2),
    ("VBAT_SW U206", "VBAT_SW", (34.9, 74.6, 38.7, 76.4), 2),     # leaves the strip under the pins for BB_L1/BB_L2
    ("3V3 out", "3V3", (29.9, 73.6, 34.0, 80.2), 2),
    ("SOLAR_IN a", "SOLAR_IN", (44.2, 15.4, 50.9, 33.7), 2),
    ("SOLAR_IN b", "SOLAR_IN", (48.4, 31.4, 54.5, 36.7), 2),
    ("CHG_SW", "CHG_SW", (54.2, 18.4, 62.7, 28.1), 2),
    ("RAW_BAT bat", "RAW_BAT", (60.4, 44.4, 70.2, 54.2), 2),
    ("RAW_BAT neck", "RAW_BAT", (61.0, 39.0, 65.5, 45.0), 2),
    ("RAW_BAT charger", "RAW_BAT", (52.6, 31.4, 68.6, 39.6), 2),
    ("VBAT_M top", "VBAT_M", (54.1, 94.9, 64.4, 101.6), 2),
]
TRACKS = [  # net, [(x, y), ...], width
    ("M_L1", [(42.37, 60.92), (46.45, 60.93)], 0.8),
    ("M_L2", [(42.37, 64.62), (45.2, 64.62), (45.95, 63.85), (46.45, 63.85)], 0.8),
    ("BAT_CONN", [(71.95, 39.0), (67.57, 38.6)], 1.0),
    ("BAT_FUSED", [(67.57, 43.45), (67.63, 45.55)], 1.0),
    ("VBAT_M", [(59.2, 95.3), (59.2, 93.55)], 0.5),     # one stub per pad, ending on the pad centre (EasyEDA joins by end points)
    ("VBAT_M", [(60.3, 95.3), (60.3, 93.55)], 0.5),
    ("ANT_MAIN", [(69.6, 92.1), (74.25, 91.6)], 0.3),
    ("ANT_FEED", [(74.25, 90.74), (74.9, 90.24), (77.4, 90.24)], 0.3),   # along y 90.24: J302's GND pads start at y 90.66
]
THERMAL_VIAS = [("GND", x, 62.4) for x in (46.3, 47.2, 48.1, 49.1)]      # U207 exposed pad, 4.4 x 1.58 mm, GND
VIA_GROUPS = [  # net, rect to search, number of vias wanted
    ("VMODEM", (54.0, 63.3, 62.6, 69.8), 4),
    ("VMODEM", (51.8, 99.0, 54.5, 101.8), 3),
]
FENCE_OFF, FENCE_PITCH = 0.85, 0.9


def fence_points(tracks):
    pts = []
    for net, path, w in tracks:
        if net not in ("ANT_MAIN", "ANT_FEED"):
            continue
        for (x0, y0), (x1, y1) in zip(path, path[1:]):
            L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L
            nx, ny = -uy, ux
            n = max(1, int(L / FENCE_PITCH))
            for k in range(n + 1):
                t = k / n
                px, py = x0 + t * (x1 - x0), y0 + t * (y1 - y0)
                for sgn in (1, -1):
                    pts.append((px + sgn * FENCE_OFF * nx, py + sgn * FENCE_OFF * ny))
    return pts


def pick_vias(r, net, rect, n, min_sep=1.0):
    allowed, own, via_ok = r.fields(net)
    x0, y0, x1, y1 = rect
    m = np.zeros_like(via_ok); m[cells(y0):cells(y1) + 1, cells(x0):cells(x1) + 1] = True
    cand = np.argwhere(via_ok & m)
    # prefer spots far from foreign copper: use the distance transform of the foreign mask on L1
    from scipy import ndimage
    foreign = (r.ras.occ[L1] != 0) & (r.ras.occ[L1] != r.idx[net])
    dist = ndimage.distance_transform_edt(~foreign)
    order = sorted(cand, key=lambda c: -dist[c[0], c[1]])
    chosen = []
    for j, i in order:
        x, y = i * router.CELL, j * router.CELL
        if all(math.hypot(x - cx, y - cy) >= min_sep for cx, cy in chosen):
            chosen.append((x, y))
            r.add_via(net, x, y)
            if len(chosen) >= n:
                break
    return chosen


def main():
    src = sys.argv[1]
    frm = sys.argv[sys.argv.index("--from") + 1] if "--from" in sys.argv else "fanout"
    board = load_board(src, ROOT)
    routes = os.path.join(HERE, "routes")
    state = json.load(open(os.path.join(routes, f"{frm}.json")))
    r = Router(board, state)
    n_l, n_v = len(r.lines), len(r.vias)
    for net, path, w in TRACKS:
        for (x0, y0), (x1, y1) in zip(path, path[1:]):
            r.add_line(net, L1, x0, y0, x1, y1, w)
    for net, x, y in THERMAL_VIAS:
        r.add_via(net, x, y)
    report = []
    for net, rect, n in VIA_GROUPS:
        got = pick_vias(r, net, rect, n)
        report.append(f"{net} vias in {rect}: {len(got)} of {n} at " + " ".join(f"({x:.1f},{y:.1f})" for x, y in got))
    # RF via fence: GND vias where the board allows them
    allowed, own, via_ok = r.fields("GND")
    fence = 0
    for x, y in fence_points(TRACKS):
        i, j = cells(x), cells(y)
        if 0 <= i < router.NX and 0 <= j < router.NY and via_ok[j, i]:
            r.add_via("GND", x, y); fence += 1
            allowed, own, via_ok = r.fields("GND")
    report.append(f"RF fence: {fence} GND vias of {len(fence_points(TRACKS))} candidates")
    # pours go into the state so the router treats them as copper
    r.pours = [(name, net, rect, prio) for name, net, rect, prio in POURS]
    st = r.state(); st["pours"] = [[name, net, list(rect), prio] for name, net, rect, prio in POURS]
    json.dump(st, open(os.path.join(routes, "power.json"), "w"))
    new_lines, new_vias = r.lines[n_l:], r.vias[n_v:]
    js_path = os.path.join(ROOT, "hardware", "easyeda", "pcb-phase4-power.js")
    write_js(js_path, new_lines, new_vias)
    router.render(r, os.path.join(routes, "power.png"), title="Auris routing: fan-out + power copper (pours drawn as rectangles)", pours=POURS)
    print("\n".join(report))
    print(f"power: +{len(new_lines)} lines, +{len(new_vias)} vias, {len(POURS)} L1 pours; wrote routes/power.json, routes/power.png, {os.path.relpath(js_path, ROOT)}")


def write_js(path, lines, vias):
    MIL = 1 / 0.0254
    rows_l = [[n, l, round(x0 * MIL, 2), round(y0 * MIL, 2), round(x1 * MIL, 2), round(y1 * MIL, 2), round(w * MIL, 3)] for n, l, x0, y0, x1, y1, w in lines]
    rows_v = [[n, round(x * MIL, 2), round(y * MIL, 2)] for n, x, y in vias]
    rows_p = [[name, net, 1, ["R", round(x0 * MIL, 2), round(y1 * MIL, 2), round((x1 - x0) * MIL, 2), round((y1 - y0) * MIL, 2), 0, 0], prio] for name, net, (x0, y0, x1, y1), prio in POURS]
    js = TEMPLATE.replace("__LINES__", router.json_rows(rows_l)).replace("__VIAS__", router.json_rows(rows_v)).replace("__POURS__", router.json_rows(rows_p))
    js = js.replace("__DRILL__", str(round(router.VIA_DRILL * MIL, 2))).replace("__DIA__", str(round(VIA_DIA * MIL, 2)))
    open(path, "w").write(js)


TEMPLATE = r"""// Auris rev A layout, phase 4c: power loops, battery path and RF feed (generated by
// hardware/layout/phase4_power.py; do not edit by hand). mil, board origin bottom-left, layer 1 = top.
// Idempotent for the pours (earlier pours of the same names are replaced). The document is NOT saved.
// Run: __aurisStart("pcb-phase4-power.js", { titleRe: /^Auris phase 4c/ })
(async () => {
  const PCB_UUID = "1171ec2ee0a2c106";
  const LINES = __LINES__;
  const VIAS = __VIAS__;
  const POURS = __POURS__;
  const out = [];
  const msg = (e) => String((e && e.message) || e).slice(0, 80);
  await eda.dmt_EditorControl.openDocument(PCB_UUID);
  await new Promise((r) => setTimeout(r, 1500));
  // EasyEDA upper-cases pour names and appends a digit to duplicates ("VMODEM OUT1"): match on that
  const names = new Set(POURS.map((p) => p[0].toUpperCase()));
  const mine = (n) => { n = String(n || "").toUpperCase(); return names.has(n) || names.has(n.replace(/\d+$/, "")); };
  try {
    const old = (await eda.pcb_PrimitivePour.getAll()).filter((p) => mine(p.getState_PourName && p.getState_PourName()));
    if (old.length) out.push(`replaced ${old.length} earlier pours: ${await eda.pcb_PrimitivePour.delete(old.map((p) => p.getState_PrimitiveId()))}`);
  } catch (e) { out.push("cleanup: " + msg(e)); }
  let group = null;
  try { group = await eda.pcb_Document.beginCommandGroup("Auris phase 4c power"); } catch (_) { group = null; }
  let nl = 0, nv = 0, np = 0; const errs = [];
  for (const [net, x, y] of VIAS) {
    try { const v = await eda.pcb_PrimitiveVia.create(net, x, y, __DRILL__, __DIA__, 0, null, null, false); if (v) nv++; else errs.push(`via ${net}: ${v}`); }
    catch (e) { errs.push(`via ${net} ${x},${y}: ${msg(e)}`); }
  }
  for (const [net, layer, x0, y0, x1, y1, w] of LINES) {
    try { const l = await eda.pcb_PrimitiveLine.create(net, layer, x0, y0, x1, y1, w, false); if (l) nl++; else errs.push(`line ${net}: ${l}`); }
    catch (e) { errs.push(`line ${net} ${x0},${y0}: ${msg(e)}`); }
  }
  for (const [name, net, layer, src, prio] of POURS) {
    try {
      const poly = eda.pcb_MathPolygon.createPolygon(src);
      const p = await eda.pcb_PrimitivePour.create(net, layer, poly, "solid", false, name, prio, 4, false);
      if (p) np++; else errs.push(`pour ${name}: ${p}`);
    } catch (e) { errs.push(`pour ${name}: ${msg(e)}`); }
  }
  // The pour "order" is unique per layer and a lower number wins; EasyEDA renumbers what the API asks for.
  // Re-create the top-side GND pour last with a large priority so every power pour sits above it.
  try {
    const gnd = (await eda.pcb_PrimitivePour.getAll()).filter((p) => String(p.getState_PourName && p.getState_PourName()).toUpperCase() === "GND L1");
    if (gnd.length) await eda.pcb_PrimitivePour.delete(gnd.map((p) => p.getState_PrimitiveId()));
    const poly = eda.pcb_MathPolygon.createPolygon(["R", 0, 4133.86, 3149.61, 4133.86, 0, 0]);
    const g = await eda.pcb_PrimitivePour.create("GND", 1, poly, "solid", false, "GND L1", 99, 4, false);
    out.push(`GND L1 pour re-created below the power pours: ${!!g} (priority now ${g && g.getState_PourPriority ? g.getState_PourPriority() : "?"})`);
  } catch (e) { out.push("GND L1 re-create: " + msg(e)); }
  let rebuilt = "?";
  try { const r = await eda.pcb_PrimitivePour.rebuildAllCopperRegions(); rebuilt = Array.isArray(r) ? r.length : String(r); } catch (e) { rebuilt = "ERR " + msg(e); }
  if (group && group.groupId) { try { await eda.pcb_Document.commitCommandGroup(group.groupId); } catch (_) { /* ignore */ } }
  try {
    const all = await eda.pcb_PrimitivePour.getAll();
    out.push("L1 pour orders: " + all.filter((p) => p.getState_Layer() === 1).map((p) => `${p.getState_PourName()}=${p.getState_PourPriority()}`).join(", "));
  } catch (e) { out.push("orders: " + msg(e)); }
  out.unshift(`vias ${nv} of ${VIAS.length}; lines ${nl} of ${LINES.length}; pours ${np} of ${POURS.length}; errors ${errs.length} ${errs.slice(0, 6).join(" | ")}; poured areas: ${rebuilt}`);
  eda.sys_Dialog.showInformationMessage(out.join("\n"), "Auris phase 4c power");
})().catch((e) => eda.sys_Dialog.showInformationMessage("Auris phase 4c power stopped: " + ((e && e.stack) || e), "Auris phase 4c power"));
"""

if __name__ == "__main__":
    main()
