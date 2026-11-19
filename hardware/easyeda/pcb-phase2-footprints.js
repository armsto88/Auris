// Auris rev A layout, phase 2: footprint fixes (layout-only: pad numbers and nets unchanged).
// Targets and sources: hardware/layout/README.md "Footprint fixes". The PCB keeps only pad-to-net
// links (PAD_NET) and takes pad geometry from the project-library footprints, so the project
// footprints are edited in place. On 4.1.105 lib_Footprint.updateDocumentSource() only accepts the
// footprint editor's full document source: each footprint is opened with openInEditor(), read with
// sys_FileManager.getDocumentSource(), written with updateDocumentSource() and closed again.
// Switching editor tabs closes the Run Script window, so the report also goes out as toasts.
//
// For each footprint every targeted pad must match either the expected current values (then it
// is changed) or the target values (already done); otherwise that footprint is not written.
// Units: mil, footprint frame as stored (same frame as the README's coordinates). Safe to re-run.
// The document is NOT saved.
//
// Run through the page driver: __aurisStart("pcb-phase2-footprints.js", { titleRe: /^Auris phase 2/, timeoutMs: 240000 })
(async () => {
  const PCB_UUID = "1171ec2ee0a2c106";
  const LIB = "3ba79283056140b08e7552182142ce8a";   // project library = project uuid
  const mm = (v) => v / 0.0254;
  const near = (a, b, tol = 0.15) => Math.abs(a - b) <= tol;
  const sgn = (v) => (v < 0 ? -1 : 1);
  const out = [];
  const add = (s) => out.push(s);
  const msg = (e) => String((e && e.message) || e).slice(0, 200);
  const r3 = (v) => Math.round(v * 0.0254 * 1000) / 1000;  // mil -> mm, 3 places

  // Each fix: which pads, a test for the current geometry, a test for the target, and the change.
  const OUTER = (b) => near(Math.abs(b.centerX), mm(7.1), 1) || near(Math.abs(b.centerY), mm(8.05), 1);
  const FIXES = [
    { fp: "f658649acb3d06f3", label: "U301 LGA-109 outer ring 1.0 x 0.6", parts: ["U301"], count: 48,
      pick: (n) => (n >= 1 && n <= 44) || (n >= 95 && n <= 98),
      was: (b) => OUTER(b) && b.defaultPad.padType === "RECT" && near(b.defaultPad.width, 39.37) && near(b.defaultPad.height, 27.559),
      is: (b) => OUTER(b) && near(b.defaultPad.width, 39.37) && near(b.defaultPad.height, mm(0.6)),
      apply: (b) => { b.defaultPad.height = mm(0.6); },
      also: (pads) => { const bad = pads.filter((b) => !(Number(b.num) <= 44 || (Number(b.num) >= 95 && Number(b.num) <= 98)) && OUTER(b)); return bad.length ? `pads ${bad.map((b) => b.num).join(",")} on the outer ring but not targeted` : ""; } },
    { fp: "62743fff779509b1", label: "X1SON-2 TI DPY0002A 0.3 x 0.5 at +-0.35", parts: ["D101", "D102", "D402"], count: 2,
      pick: (n) => n === 1 || n === 2,
      was: (b) => near(b.defaultPad.width, 23.622) && near(b.defaultPad.height, 23.622) && near(Math.abs(b.centerX), mm(0.5), 0.5),
      is: (b) => near(b.defaultPad.width, mm(0.3)) && near(b.defaultPad.height, mm(0.5)) && near(Math.abs(b.centerX), mm(0.35), 0.5),
      apply: (b) => { b.defaultPad.width = mm(0.3); b.defaultPad.height = mm(0.5); b.centerX = sgn(b.centerX) * mm(0.35); } },
    { fp: "58d60b454650b3eb", label: "R1812 Littelfuse 1.78 x 3.15 at +-2.615", parts: ["F201"], count: 2,
      pick: (n) => n === 1 || n === 2,
      was: (b) => near(b.defaultPad.width, 50.493) && near(b.defaultPad.height, 136.063) && near(Math.abs(b.centerX), mm(2.141), 0.5),
      is: (b) => near(b.defaultPad.width, mm(1.78)) && near(b.defaultPad.height, mm(3.15)) && near(Math.abs(b.centerX), mm(2.615), 0.5),
      apply: (b) => { b.defaultPad.width = mm(1.78); b.defaultPad.height = mm(3.15); b.centerX = sgn(b.centerX) * mm(2.615); } },
    { fp: "e2877e89ae510885", label: "F1812 Littelfuse 1.78 x 3.15 at +-2.615", parts: ["F202"], count: 2,
      pick: (n) => n === 1 || n === 2,
      was: (b) => near(b.defaultPad.width, 55.381) && near(b.defaultPad.height, 137.764) && near(Math.abs(b.centerX), mm(1.853), 0.5),
      is: (b) => near(b.defaultPad.width, mm(1.78)) && near(b.defaultPad.height, mm(3.15)) && near(Math.abs(b.centerX), mm(2.615), 0.5),
      apply: (b) => { b.defaultPad.width = mm(1.78); b.defaultPad.height = mm(3.15); b.centerX = sgn(b.centerX) * mm(2.615); } },
    { fp: "8d48bcf63d31ff15", label: "C207 FP-V size B: 2.56 x 1.1 at +-1.78 (gap 1.0)", parts: ["C207"], count: 2,
      pick: (n) => n === 1 || n === 2,
      was: (b) => near(b.defaultPad.width, 110.236) && near(b.defaultPad.height, 43.307) && near(Math.abs(b.centerX), mm(1.661), 0.5),
      is: (b) => near(b.defaultPad.width, mm(2.56)) && near(b.defaultPad.height, 43.307) && near(Math.abs(b.centerX), mm(1.78), 0.5),
      apply: (b) => { b.defaultPad.width = mm(2.56); b.centerX = sgn(b.centerX) * mm(1.78); } },
    { fp: "dd045926244beccb", label: "Test-Point (a) 1.0 mm round", parts: ["TP*"], count: 1,
      pick: (n) => n === 1,
      was: (b) => b.defaultPad.padType === "ELLIPSE" && near(b.defaultPad.width, 19.685) && near(b.defaultPad.height, 19.685),
      is: (b) => b.defaultPad.padType === "ELLIPSE" && near(b.defaultPad.width, mm(1)) && near(b.defaultPad.height, mm(1)),
      apply: (b) => { b.defaultPad.width = mm(1); b.defaultPad.height = mm(1); } },
    { fp: "df56496f1e7ffd22", label: "Test-Point (b) 1.0 mm round", parts: ["TP*"], count: 1,
      pick: (n) => n === 1,
      was: (b) => b.defaultPad.padType === "ELLIPSE" && near(b.defaultPad.width, 19.685) && near(b.defaultPad.height, 19.685),
      is: (b) => b.defaultPad.padType === "ELLIPSE" && near(b.defaultPad.width, mm(1)) && near(b.defaultPad.height, mm(1)),
      apply: (b) => { b.defaultPad.width = mm(1); b.defaultPad.height = mm(1); } },
    { fp: "4046b9745dfa4000", label: "J401 shell: pads 3/4 copper 1.8 slot 1.4; pads 1/2 to y +1.87", parts: ["J401"], count: 4,
      pick: (n) => n >= 1 && n <= 4,
      was: (b) => (Number(b.num) <= 2
        ? near(b.defaultPad.height, 82.677) && b.hole && near(b.hole.width, 66.929) && near(b.centerY, mm(1.77), 0.5)
        : near(b.defaultPad.height, 62.992) && b.hole && near(b.hole.width, 47.244) && near(b.centerY, mm(-2.41), 0.5)),
      is: (b) => (Number(b.num) <= 2
        ? near(b.defaultPad.height, 82.677) && b.hole && near(b.hole.width, 66.929) && near(b.centerY, mm(1.87), 0.5)
        : near(b.defaultPad.height, mm(1.8)) && b.hole && near(b.hole.width, mm(1.4)) && near(b.centerY, mm(-2.41), 0.5)),
      apply: (b) => { if (Number(b.num) <= 2) b.centerY = mm(1.87); else { b.defaultPad.height = mm(1.8); b.hole.width = mm(1.4); } } },
    // Added in phase 3 after SC-002 (J402 is now the Hanbo TF-030): the library footprint has the
    // contact row 0.10 mm right of the drawing and the upper cover pads 0.10 mm high. Hanbo TF-030
    // drawing (recommended PCB layout): #08 at -4.50, #01 at +3.20 from the cover-pad centreline;
    // upper cover pads' bottom edge 5.45 above the contacts' bottom edge (centre +5.70 from the contacts).
    { fp: "e0ed2a6d9b179b77", label: "J402 TF-030 per Hanbo drawing: contacts 0.10 left, pads 9/11 at y +4.10", parts: ["J402"], count: 10,
      pick: (n) => (n >= 1 && n <= 9) || n === 11,
      was: (b) => (Number(b.num) <= 8 ? near(b.centerX, mm(3.30 - 1.10 * (Number(b.num) - 1)), 0.5) && near(b.centerY, mm(-1.60), 0.5)
        : near(b.centerY, mm(4.20), 0.5) && near(Math.abs(b.centerX), mm(6.88), 0.5)),
      is: (b) => (Number(b.num) <= 8 ? near(b.centerX, mm(3.20 - 1.10 * (Number(b.num) - 1)), 0.5) && near(b.centerY, mm(-1.60), 0.5)
        : near(b.centerY, mm(4.10), 0.5) && near(Math.abs(b.centerX), mm(6.88), 0.5)),
      apply: (b) => { if (Number(b.num) <= 8) b.centerX = mm(3.20 - 1.10 * (Number(b.num) - 1)); else b.centerY = mm(4.10); } },
  ];

  // The pad lines are "{head}||{body}|"; only PAD bodies are re-serialised
  const parse = (src) => src.split("\n").map((line) => {
    const i = line.indexOf("||");
    if (i < 0) return { line };
    let head; try { head = JSON.parse(line.slice(0, i)); } catch (_) { return { line }; }
    if (!head || head.type !== "PAD") return { line };
    const bodyText = line.slice(i + 2).replace(/\|$/, "");
    return { line, head, headText: line.slice(0, i), body: JSON.parse(bodyText) };
  });

  await eda.dmt_EditorControl.openDocument(PCB_UUID);
  await new Promise((r) => setTimeout(r, 1500));

  add("== 1. Footprints");
  const written = [];
  for (const f of FIXES) {
    try {
      const tab = await eda.lib_Footprint.openInEditor(f.fp, LIB);
      await new Promise((r) => setTimeout(r, 2500));
      let src;
      try { src = await eda.sys_FileManager.getDocumentSource(); } finally { /* tab closed below */ }
      const close = async () => { if (tab) try { await eda.dmt_EditorControl.closeDocument(tab); } catch (_) { /* leave it */ } };
      // The editor's DOCHEAD says docType "PCB" (the footprint editor is a PCB canvas); its uuid must be this footprint
      let dh = null;
      try { const first = (src || "").split("\n")[0]; dh = JSON.parse(first.slice(first.indexOf("||") + 2).replace(/\|$/, "")); } catch (_) { dh = null; }
      if (!dh || dh.uuid !== f.fp || !["PCB", "FOOTPRINT"].includes(dh.docType)) { add(`${f.label}: editor source is not this footprint (${dh && dh.docType} ${dh && dh.uuid}), NOT WRITTEN`); await close(); continue; }
      const rows = parse(src);
      const pads = rows.filter((r) => r.body).map((r) => r.body);
      const target = rows.filter((r) => r.body && f.pick(Number(r.body.num)));
      const problems = [];
      if (target.length !== f.count) problems.push(`${target.length} target pads, expected ${f.count}`);
      let todo = 0, done = 0;
      for (const r of target) {
        if (f.is(r.body)) done++;
        else if (f.was(r.body)) todo++;
        else problems.push(`pad ${r.body.num} matches neither old nor new: ${JSON.stringify(r.body.defaultPad)} c(${r3(r.body.centerX)},${r3(r.body.centerY)}) hole ${JSON.stringify(r.body.hole)}`);
      }
      const extra = f.also ? f.also(pads) : "";
      if (extra) problems.push(extra);
      if (problems.length) { add(`${f.label}: NOT WRITTEN: ${problems.slice(0, 3).join("; ")}`); await close(); continue; }
      if (!todo) { add(`${f.label}: already done (${done} pads)`); await close(); continue; }
      for (const r of target) if (!f.is(r.body)) { f.apply(r.body); r.line = r.headText + "||" + JSON.stringify(r.body) + "|"; }
      const next = rows.map((r) => r.line).join("\n");
      const ok = await eda.lib_Footprint.updateDocumentSource(f.fp, LIB, next);
      // read back
      const back = parse((await eda.lib_Footprint.getDocumentSource(f.fp, LIB)) || "").filter((r) => r.body && f.pick(Number(r.body.num)));
      const good = back.filter((r) => f.is(r.body)).length;
      add(`${f.label}: changed ${todo}, already ${done}; updateDocumentSource -> ${ok}; read back ${good}/${f.count} at target`);
      const s = back[0] && back[0].body;
      if (s) add(`  e.g. pad ${s.num}: ${s.defaultPad.padType} ${r3(s.defaultPad.width)} x ${r3(s.defaultPad.height)} mm at (${r3(s.centerX)}, ${r3(s.centerY)})${s.hole ? " slot " + r3(s.hole.width) + " x " + r3(s.hole.height) : ""}`);
      await close();
      if (ok && good === f.count) written.push(f);
    } catch (e) { add(`${f.label}: ERROR ${msg(e)}`); }
  }

  // 2. Does the open PCB show the new geometry?
  await eda.dmt_EditorControl.openDocument(PCB_UUID);
  await new Promise((r) => setTimeout(r, 2500));
  add("== 2. PCB pads after the change");
  const comps = await eda.pcb_PrimitiveComponent.getAll();
  const byDes = (d) => comps.find((c) => { try { return c.getState_Designator() === d; } catch (_) { return false; } });
  for (const [d, nums] of [["U301", ["1", "35", "45", "95"]], ["D101", ["1"]], ["F201", ["1"]], ["F202", ["1"]], ["C207", ["1"]], ["TP101", ["1"]], ["J401", ["A1", "17"]], ["J402", ["1", "8", "9", "10"]]]) {
    const c = byDes(d);
    if (!c) { add(`${d}: not found`); continue; }
    try {
      const pins = await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(c.getState_PrimitiveId());
      const cx = c.getState_X(), cy = c.getState_Y();
      add(`${d}: ` + nums.map((n) => { const p = pins.find((q) => q.getState_PadNumber() === n); if (!p) return `${n}?`; const s = p.getState_Pad(); const h = p.getState_Hole(); return `${n} ${JSON.stringify(s.map((v) => (typeof v === "number" ? r3(v) : v)))}${h ? " hole " + JSON.stringify(h.map((v) => (typeof v === "number" ? r3(v) : v))) : ""} at (${r3(p.getState_X() - cx)}, ${r3(p.getState_Y() - cy)}) ${p.getState_Net()}`; }).join(" | "));
    } catch (e) { add(`${d}: ERROR ${msg(e)}`); }
  }

  out.forEach((l, i) => { try { eda.sys_ToastMessage.showMessage(`AURIS ${String(i).padStart(2, "0")} ${l}`, undefined, 300); } catch (_) { /* no toast */ } });
  eda.sys_Dialog.showInformationMessage(out.join("\n"), "Auris phase 2");
})().catch((e) => eda.sys_Dialog.showInformationMessage("Auris phase 2 stopped: " + ((e && e.stack) || e), "Auris phase 2"));
