// Auris rev A layout, phase 1a: 4 copper layers, board outline, mounting holes.
// Decisions: hardware/layout/README.md (80 x 105 mm portrait, 2 mm corner radii, 4x M3 holes
// 3.2 mm unplated 4 mm in from each corner). API notes: hardware/layout/easyeda-pcb-api.md.
//
// The board sits at X 0..80 mm, Y 0..105 mm (origin = bottom-left corner), above the area where
// Update PCB dropped the parts (all at negative Y). Positions are Cartesian (Y up) in mil; the
// outline rectangle ["R", x, y, w, h, rot, round] takes its top-left corner, so (0, H).
// Safe to re-run: steps already done are skipped. All writes go into one command group (one undo).
// The document is NOT saved; check the report, then save.
//
// Run through the page driver: __aurisStart("pcb-phase1-board.js", { titleRe: /^Auris phase 1a/, timeoutMs: 180000 })
(async () => {
  const PCB_UUID = "1171ec2ee0a2c106";
  const MIL = 1 / 0.0254;                // mil per mm
  const W = 80 * MIL, H = 105 * MIL, R = 2 * MIL;
  const HOLE = 3.2 * MIL, HOLE_IN = 4 * MIL;
  const OUTLINE_LAYER = 11, MULTI_LAYER = 12;
  const r2 = (v) => Math.round(v * 100) / 100;
  const out = [];
  const add = (s) => out.push(s);
  const msg = (e) => String((e && e.message) || e).slice(0, 200);
  const json = (v, n) => { try { return JSON.stringify(v).slice(0, n); } catch (e) { return "(not JSON)"; } };
  const st = (p, k) => { try { return p["getState_" + k](); } catch (e) { return "ERR"; } };

  await eda.dmt_EditorControl.openDocument(PCB_UUID);
  await new Promise((r) => setTimeout(r, 1500));
  const info = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  if (!info || info.uuid !== PCB_UUID) throw new Error("PCB not the current document: " + json(info, 200));

  let group;
  try { group = await eda.pcb_Document.beginCommandGroup("Auris phase 1a"); add(`command group ${json(group, 80)}`); }
  catch (e) { add(`beginCommandGroup failed (${msg(e)}); continuing without`); }

  // 1. Copper layers
  add("== 1. Copper layers");
  const n0 = await eda.pcb_Layer.getTheNumberOfCopperLayers();
  if (n0 !== 4) add(`setTheNumberOfCopperLayers(4) from ${n0} -> ${await eda.pcb_Layer.setTheNumberOfCopperLayers(4)}`);
  else add("already 4 layers");
  const layers = await eda.pcb_Layer.getAllLayers();
  add(`now ${await eda.pcb_Layer.getTheNumberOfCopperLayers()}; ` + layers.filter((l) => l.type === "SIGNAL" && l.layerStatus).map((l) => `${l.id}:${l.name}`).join(", "));

  // 2. Stack-up EasyEDA assigned (compare with JLC04161H-7628 in the README)
  add("== 2. Stack-up");
  try {
    const s = await eda.pcb_Layer.getStackup();
    add(`unit ${s.unit} total ${r2(s.totalThickness)}: ` + s.layers.filter((l) => l.kind !== "other" || l.thickness).map((l) => `${l.layerType}/${l.material || "-"}/t${r2(l.thickness)}/er${l.permittivity}`).join(" | "));
  } catch (e) { add(`getStackup ERROR ${msg(e)}`); }

  // 3. Board outline
  add("== 3. Outline");
  // An existing outline is kept only if its bounding box is the board (10 mil line width allowed)
  const near = (a, b) => Math.abs(a - b) < 10;
  const lines11 = (await eda.pcb_PrimitivePolyline.getAll()).filter((p) => st(p, "Layer") === OUTLINE_LAYER);
  let outline;
  for (const p of lines11) {
    const id = st(p, "PrimitiveId");
    const b = await eda.pcb_Primitive.getPrimitivesBBox([id]);
    if (b && near(b.minX, 0) && near(b.maxX, W) && near(b.minY, 0) && near(b.maxY, H) && !outline) { outline = p; add(`outline already present and in place: ${id}`); }
    else add(`deleting misplaced outline ${id} (bbox Y ${b && r2(b.minY)}..${b && r2(b.maxY)}) -> ${await eda.pcb_PrimitivePolyline.delete([id])}`);
  }
  if (!outline) {
    // In the PCB, ["R", x, y, w, h, rot, round] has (x, y) as the top-left corner in Cartesian
    // coordinates and extends down (to y - h); found 2026-11-19, the type file's "SVG" note misleads.
    const poly = eda.pcb_MathPolygon.createPolygon(["R", 0, H, W, H, 0, R]);
    if (!poly) throw new Error("createPolygon returned nothing for the outline");
    outline = await eda.pcb_PrimitivePolyline.create("", OUTLINE_LAYER, poly, 10, false);
    add(`created: ${outline ? st(outline, "PrimitiveId") : "FAILED (undefined)"}`);
  }
  if (outline) {
    const id = st(outline, "PrimitiveId");
    try { const b = await eda.pcb_Primitive.getPrimitivesBBox([id]); add(`bbox X ${r2(b.minX)}..${r2(b.maxX)} Y ${r2(b.minY)}..${r2(b.maxY)} mil (want X 0..${r2(W)} Y 0..${r2(H)}, line width adds ~5)`); }
    catch (e) { add(`bbox ERROR ${msg(e)}`); }
    try { add(`source ${json(st(outline, "Polygon") && st(outline, "Polygon").getSource ? st(outline, "Polygon").getSource() : st(outline, "Polygon"), 200)}`); } catch (e) { add(`source ERROR ${msg(e)}`); }
  }

  // 4. Mounting holes: unplated, no copper ring (pad = hole), no net
  add("== 4. Mounting holes");
  const centres = [
    ["MH1", HOLE_IN, H - HOLE_IN], ["MH2", W - HOLE_IN, H - HOLE_IN],
    ["MH3", HOLE_IN, HOLE_IN], ["MH4", W - HOLE_IN, HOLE_IN],
  ];
  const freePads = (await eda.pcb_PrimitivePad.getAll()).filter((p) => /^MH\d$/.test(String(st(p, "PadNumber"))));
  for (const [num, x, y] of centres) {
    const have = freePads.find((p) => st(p, "PadNumber") === num);
    let p = have;
    if (!have) {
      try {
        p = await eda.pcb_PrimitivePad.create(MULTI_LAYER, num, x, y, 0, ["ELLIPSE", HOLE, HOLE], "", ["ROUND", HOLE], 0, 0, 0, false, 0);
      } catch (e) { add(`${num} create ERROR ${msg(e)}`); continue; }
    }
    add(p ? `${num} ${have ? "present" : "created"}: X ${r2(st(p, "X"))} Y ${r2(st(p, "Y"))} pad ${json(st(p, "Pad"), 60)} hole ${json(st(p, "Hole"), 60)} plated ${st(p, "Metallization")} layer ${st(p, "Layer")}`
           : `${num} create FAILED (undefined)`);
  }

  if (group && group.groupId) { try { add(`commitCommandGroup -> ${await eda.pcb_Document.commitCommandGroup(group.groupId)}`); } catch (e) { add(`commit ERROR ${msg(e)}`); } }

  // 5. Read-only: rule structure needed for the net classes (phase 1b)
  add("== 5. Rules (read only)");
  try {
    const ml = await eda.pcb_Drc.getRuleConfiguration("JLCPCB Capability(Multiple Layers Board)");
    const c = (ml && ml.config) || ml;
    add(`ML top keys ${json(Object.keys(ml || {}), 100)}`);
    add(`ML Physics.Track: ${json(c.Physics && c.Physics.Track, 900)}`);
    add(`ML Physics.Via Size: ${json(c.Physics && c.Physics["Via Size"], 600)}`);
    add(`ML Physics.Differential Pair: ${json(c.Physics && c.Physics["Differential Pair"], 600)}`);
    const ss = c.Spacing && c.Spacing["Safe Spacing"];
    add(`ML Safe Spacing keys ${json(Object.keys(ss || {}), 200)}; first: ${json(ss && ss[Object.keys(ss)[0]], 700)}`);
    add(`ML Plane: ${json(c.Plane, 500)}`);
  } catch (e) { add(`rules ERROR ${msg(e)}`); }
  try { add(`net classes now: ${json(await eda.pcb_Drc.getAllNetClasses(), 200)}`); } catch (e) { add(`classes ERROR ${msg(e)}`); }

  eda.sys_Dialog.showInformationMessage(out.join("\n"), "Auris phase 1a");
})().catch((e) => eda.sys_Dialog.showInformationMessage("Auris phase 1a stopped: " + ((e && e.stack) || e), "Auris phase 1a"));
