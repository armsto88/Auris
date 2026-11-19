// Auris rev A layout, phase 3: board outline with the ESP32 antenna notch, and MH1 moved.
// Owner decision 2026-11-19: notch 35 x 6 mm at the top-left so U401's antenna is in free air
// (Espressif ESP32-S3 HW design guide Fig. 26); MH1 moves from (4, 101) to (40, 101) mm.
// Outline (mm, origin bottom-left): 80 x 105 with 2 mm outer corner radii, the notch's outer
// corners 1 mm and 0.5 mm, its inner corner 1 mm (a router cannot cut a sharp inner corner).
// Arcs are drawn as short straight segments (<= 0.01 mm from the true arc).
// Safe to re-run. The document is NOT saved.
// Run: __aurisStart("pcb-phase3-outline.js", { titleRe: /^Auris phase 3 outline/, timeoutMs: 120000 })
(async () => {
  const PCB_UUID = "1171ec2ee0a2c106";
  const MIL = 1 / 0.0254;
  const W = 80, H = 105, NX = 35, NY = 99;
  const MH1 = [40, 101];
  const out = [];
  const add = (s) => out.push(s);
  const r2 = (v) => Math.round(v * 100) / 100;

  // corner arc from angle a0 to a1 (degrees) around (cx, cy), radius r
  const arc = (cx, cy, r, a0, a1, n = 8) => {
    const pts = [];
    for (let i = 0; i <= n; i++) {
      const a = ((a0 + ((a1 - a0) * i) / n) * Math.PI) / 180;
      pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]);
    }
    return pts;
  };
  const pts = [
    ...arc(2, 2, 2, 180, 270),            // bottom-left  (0,2) -> (2,0)
    ...arc(W - 2, 2, 2, 270, 360),        // bottom-right (78,0) -> (80,2)
    ...arc(W - 2, H - 2, 2, 0, 90),       // top-right    (80,103) -> (78,105)
    ...arc(NX + 1, H - 1, 1, 90, 180),    // notch outer  (36,105) -> (35,104)
    ...arc(NX - 1, NY + 1, 1, 0, -90),    // notch inner  (35,100) -> (34,99), fillet left by the router
    ...arc(0.5, NY - 0.5, 0.5, 90, 180),  // notch left   (0.5,99) -> (0,98.5)
  ];
  pts.push(pts[0]);
  const src = [];
  pts.forEach(([x, y], i) => { src.push(x * MIL, y * MIL); if (i === 0) src.push("L"); });

  await eda.dmt_EditorControl.openDocument(PCB_UUID);
  await new Promise((r) => setTimeout(r, 1500));

  // 1. Outline: replace the polyline(s) on the Board Outline layer
  const lines11 = (await eda.pcb_PrimitivePolyline.getAll()).filter((p) => p.getState_Layer() === 11);
  const poly = eda.pcb_MathPolygon.createPolygon(src);
  if (!poly) throw new Error("createPolygon returned nothing for the notched outline");
  const created = await eda.pcb_PrimitivePolyline.create("", 11, poly, 10, false);
  if (!created) throw new Error("outline not created; old outline left in place");
  const id = created.getState_PrimitiveId();
  const b = await eda.pcb_Primitive.getPrimitivesBBox([id]);
  add(`new outline ${id}: ${pts.length} points; bbox X ${r2(b.minX / MIL)}..${r2(b.maxX / MIL)} Y ${r2(b.minY / MIL)}..${r2(b.maxY / MIL)} mm (want 0..80, 0..105 plus half the 0.25 mm line)`);
  const ok = Math.abs(b.minX / MIL) < 0.3 && Math.abs(b.maxX / MIL - W) < 0.3 && Math.abs(b.minY / MIL) < 0.3 && Math.abs(b.maxY / MIL - H) < 0.3;
  if (!ok) {
    add(`bbox wrong, deleting the new outline -> ${await eda.pcb_PrimitivePolyline.delete([id])}; old outline kept`);
  } else if (lines11.length) {
    add(`deleted old outline(s) ${lines11.map((p) => p.getState_PrimitiveId()).join(",")} -> ${await eda.pcb_PrimitivePolyline.delete(lines11.map((p) => p.getState_PrimitiveId()))}`);
  }

  // 2. MH1
  const mh1 = (await eda.pcb_PrimitivePad.getAll()).find((p) => p.getState_PadNumber() === "MH1");
  if (!mh1) add("MH1 not found");
  else {
    const m = await eda.pcb_PrimitivePad.modify(mh1.getState_PrimitiveId(), { x: MH1[0] * MIL, y: MH1[1] * MIL });
    const p = (await eda.pcb_PrimitivePad.getAll()).find((q) => q.getState_PadNumber() === "MH1");
    add(`MH1 modify -> ${!!m}; now at (${r2(p.getState_X() / MIL)}, ${r2(p.getState_Y() / MIL)}) mm, hole ${JSON.stringify(p.getState_Hole())}`);
  }

  out.forEach((l, i) => { try { eda.sys_ToastMessage.showMessage(`AURIS ${String(i).padStart(2, "0")} ${l}`, undefined, 300); } catch (_) { /* no toast */ } });
  eda.sys_Dialog.showInformationMessage(out.join("\n"), "Auris phase 3 outline");
})().catch((e) => eda.sys_Dialog.showInformationMessage("Auris phase 3 outline stopped: " + ((e && e.stack) || e), "Auris phase 3 outline"));
