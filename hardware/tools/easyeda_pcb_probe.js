// Auris: read-only probe of EasyEDA Pro's PCB scripting API before the rev A layout (handover
// phase 0). It opens the PCB document, lists what each pcb_* class offers (method names and, where
// the source shows them, parameter names), and calls only getters, getAll() and DRC. Nothing on the
// board is created, moved, modified or deleted, and the document is not saved. DRC changes nothing
// in the design; it may add markers to EasyEDA's DRC panel.
//
// Run through the page driver (hardware/tools/easyeda_page_driver.js):
//   __aurisStart("easyeda_pcb_probe.js", { titleRe: /^Auris probe/, timeoutMs: 300000 })
// then poll __aurisJobResult. The same report goes to the browser console, one "[Auris probe]" line
// per row, in case the dialog is cut short.
(async () => {
  const PCB_UUID = "1171ec2ee0a2c106";
  const RUN_DRC = true;
  const SAMPLE_PARTS = ["U301", "U401", "J402", "C207"];
  const out = [];
  const add = (s) => { out.push(s); try { console.log("[Auris probe] " + s); } catch (_) { /* no console */ } };
  const sleep = (ms) => new Promise((r) => (typeof setTimeout === "function" ? setTimeout(r, ms) : r()));
  const msg = (e) => String((e && e.message) || e).slice(0, 200);
  const json = (v, n) => { try { return JSON.stringify(v).slice(0, n); } catch (e) { return "(not JSON: " + msg(e) + ")"; } };
  const brief = (v) => {
    if (v === undefined) return "undefined";
    if (v === null) return "null";
    if (Array.isArray(v)) return `array(${v.length})`;
    if (typeof v === "object") { const k = Object.keys(v); return `{${k.slice(0, 15).join(",")}${k.length > 15 ? ",..." : ""}}`; }
    return String(v).slice(0, 120);
  };
  // detail > 0 adds a JSON excerpt of that many characters
  const call = async (label, f, detail = 0) => {
    try {
      const v = await f();
      add(`${label} -> ${brief(v)}${detail && v && typeof v === "object" ? " " + json(v, detail) : ""}`);
      return v;
    } catch (e) { add(`${label} -> ERROR ${msg(e)}`); return undefined; }
  };
  const methods = (o) => {
    const s = new Set();
    for (let p = o; p && p !== Object.prototype; p = Object.getPrototypeOf(p))
      for (const k of Object.getOwnPropertyNames(p)) {
        if (k === "constructor") continue;
        try { if (typeof o[k] === "function") s.add(k); } catch (_) { /* getter threw */ }
      }
    return [...s].sort();
  };
  const params = (f) => {
    try {
      const m = /^[^(]*\(([^)]*)\)/.exec(Function.prototype.toString.call(f));
      return m ? m[1].replace(/\s+/g, "") : "len" + f.length;
    } catch (_) { return "len" + f.length; }
  };
  const sig = (o, m) => `${m}(${params(o[m])})`;

  // 1. What the API offers
  const keys = new Set();
  for (let p = eda; p && p !== Object.prototype; p = Object.getPrototypeOf(p)) for (const k of Object.getOwnPropertyNames(p)) keys.add(k);
  for (const k in eda) keys.add(k);
  const names = [...keys].filter((k) => k !== "constructor").sort();
  const pcbClasses = names.filter((k) => /^pcb_/.test(k));
  add(`== 1. API: ${names.length} eda members`);
  for (const pre of ["pcb_", "dmt_", "lib_", "sys_"]) add(`${pre}*: ${names.filter((k) => k.startsWith(pre)).join(" ")}`);
  for (const c of ["sys_Environment"]) if (eda[c]) for (const m of methods(eda[c])) if (/version/i.test(m)) await call(`${c}.${m}()`, () => eda[c][m]());

  // 2. Open the PCB (switches the editor tab only)
  add("== 2. PCB document");
  await call("dmt_EditorControl.openDocument(PCB)", () => eda.dmt_EditorControl.openDocument(PCB_UUID));
  await sleep(2000);
  if (eda.dmt_SelectControl) await call("dmt_SelectControl.getCurrentDocumentInfo()", () => eda.dmt_SelectControl.getCurrentDocumentInfo(), 300);

  // 3. Signatures of every pcb_* class, plus the document and library classes layout needs
  add("== 3. Signatures");
  for (const c of [...pcbClasses, "dmt_Pcb", "dmt_Board", "lib_Footprint", "sys_FileManager"]) {
    const o = eda[c];
    add(o ? `${c}: ${methods(o).map((m) => sig(o, m)).join(" ")}` : `${c}: missing`);
  }

  // 4. Zero-argument getters on the classes that describe the board (layers, rules, nets, document)
  add("== 4. Getters");
  const SAFE = ["dmt_Pcb", "dmt_Board", "pcb_Document", "pcb_Layer", "pcb_Drc", "pcb_Net"];
  const DENY = /file|export|download|manufactur|image|render|screenshot|gerber|import|save|navigate|zoom|select|highlight|open|close|create|modify|delete|set|add|remove|update|check|run|place|lock|convert|move|clear/i;
  for (const c of SAFE) {
    const o = eda[c];
    if (!o) { add(`${c}: missing`); continue; }
    for (const m of methods(o)) {
      if (!/^(get|is|has)/.test(m) || DENY.test(m.replace(/^(get|is|has)/, ""))) continue;
      if (o[m].length !== 0) { add(`${c}.${sig(o, m)}: needs arguments, not called`); continue; }
      await call(`${c}.${m}()`, () => o[m](), 600);
    }
  }

  // 5. Every primitive class: count by layer, and what a primitive object offers
  add("== 5. Primitives");
  let comps = [];
  for (const c of pcbClasses.filter((k) => /^pcb_Primitive/.test(k))) {
    const o = eda[c];
    if (typeof o.getAll !== "function") { add(`${c}: no getAll`); continue; }
    const all = await call(`${c}.getAll()`, () => o.getAll());
    if (!Array.isArray(all) || !all.length) continue;
    if (c === "pcb_PrimitiveComponent") comps = all;
    const byLayer = {};
    for (const p of all) {
      let l; try { l = typeof p.getState_Layer === "function" ? p.getState_Layer() : "?"; } catch (_) { l = "err"; }
      byLayer[l] = (byLayer[l] || 0) + 1;
    }
    add(`  ${c} by layer: ${json(byLayer, 300)}`);
    add(`  ${c} object methods: ${methods(all[0]).join(" ")}`);
  }

  // 6. Components: positions, a few sample parts in full, and their pads
  add("== 6. Components");
  const st = (p, k) => { try { return typeof p["getState_" + k] === "function" ? p["getState_" + k]() : undefined; } catch (e) { return "ERR " + msg(e); } };
  if (comps.length) {
    const xs = comps.map((p) => Number(st(p, "X"))), ys = comps.map((p) => Number(st(p, "Y")));
    add(`count ${comps.length}; X ${Math.min(...xs)} .. ${Math.max(...xs)}; Y ${Math.min(...ys)} .. ${Math.max(...ys)} (units as returned)`);
    const rots = new Set(comps.map((p) => st(p, "Rotation"))), lays = new Set(comps.map((p) => st(p, "Layer")));
    add(`rotations ${[...rots].join(",")}; layers ${[...lays].join(",")}`);
    for (const d of SAMPLE_PARTS) {
      const p = comps.find((q) => String(st(q, "Designator")) === d);
      if (!p) { add(`${d}: not found by getState_Designator`); continue; }
      const vals = {};
      for (const m of methods(p).filter((k) => /^getState_/.test(k))) vals[m.slice(9)] = st(p, m.slice(9));
      add(`${d}: ${json(vals, 700)}`);
      const id = st(p, "PrimitiveId");
      const pc = eda.pcb_PrimitiveComponent;
      if (pc && typeof pc.getAllPinsByPrimitiveId === "function") {
        const pads = await call(`  ${d} getAllPinsByPrimitiveId`, () => pc.getAllPinsByPrimitiveId(id));
        if (Array.isArray(pads) && pads.length) {
          add(`  pad methods: ${methods(pads[0]).filter((k) => /^getState_/.test(k)).map((k) => k.slice(9)).join(" ")}`);
          const pv = {};
          for (const m of methods(pads[0]).filter((k) => /^getState_/.test(k))) pv[m.slice(9)] = st(pads[0], m.slice(9));
          add(`  first pad: ${json(pv, 500)}`);
        }
      }
    }
  }

  // 7. Board-outline helper (pure geometry, no primitive is created)
  add("== 7. Outline helpers");
  if (eda.pcb_MathPolygon && typeof eda.pcb_MathPolygon.createPolygon === "function") {
    const poly = await call("pcb_MathPolygon.createPolygon(R 0 0 100 70)", () => eda.pcb_MathPolygon.createPolygon(["R", 0, 0, 100, 70, 0]));
    if (poly) add(`  polygon methods: ${methods(poly).join(" ")}`);
  } else add("pcb_MathPolygon.createPolygon: missing");

  // 8. DRC
  add("== 8. DRC");
  const drc = eda.pcb_Drc;
  if (RUN_DRC && drc && typeof drc.check === "function") {
    add(`signature: ${sig(drc, "check")}`);
    const t0 = Date.now();
    const r = await call("pcb_Drc.check(false, false, true)", () => drc.check(false, false, true), 300);
    add(`took ${Date.now() - t0} ms`);
    if (Array.isArray(r) && r.length) {
      add(`first item: ${json(r[0], 600)}`);
      const keyOf = (e) => (e && (e.errorType || e.type || e.ruleName || e.name || e.title)) || "?";
      const groups = {};
      for (const e of r) { const k = String(keyOf(e)).slice(0, 60); groups[k] = (groups[k] || 0) + 1; }
      add(`groups: ${json(groups, 800)}`);
    }
  } else add("pcb_Drc.check: not run (missing or RUN_DRC false)");

  const text = out.join("\n");
  for (const box of [eda.sys_Dialog, eda.sys_MessageBox]) {
    try { if (box && typeof box.showInformationMessage === "function") { box.showInformationMessage(text, "Auris probe"); return; } }
    catch (_) { /* try the next one */ }
  }
})().catch((e) => {
  const m = "Auris probe stopped: " + ((e && e.stack) || e);
  try { console.error(m); } catch (_) { /* no console */ }
  (eda.sys_Dialog || eda.sys_MessageBox).showInformationMessage(m, "Auris probe");
});
