// Auris rev A layout, phase 1b: design rules, net classes, differential pairs.
// Values: hardware/layout/README.md "Net classes" and "Current-carrying nets"; widths from
// hardware/layout/impedance.py (to be confirmed in JLC's calculator). Net names checked against
// the sheet netlists 2026-11-19.
//
// Edits this PCB's current rule configuration in place (no account-level rule set is saved): adds
// named Track rules per class and a 0.2 mm Safe Spacing rule (max of JLC's table and 0.2 mm), sets
// the default track and pair rules, then assigns the class rules through the net-rule table. If the
// rules do not take, the classes are pointed back at "default". Safe to re-run.
// The document is NOT saved.
//
// Run through the page driver: __aurisStart("pcb-phase1-rules.js", { titleRe: /^Auris phase 1b/, timeoutMs: 180000 })
(async () => {
  const PCB_UUID = "1171ec2ee0a2c106";
  const CLR = "CLR_0.2";
  const DEFAULT_TRACK = 0.2;        // mm
  const DEFAULT_TT_SPACING = 0.152; // mm track-to-track (JLC's table has 0.102); README default 0.15
  const CLASSES = {
    RF_50:  { nets: ["ANT_MAIN", "ANT_FEED"], color: { r: 230, g: 60, b: 60, alpha: 1 }, track: [0.30, 0.30, 0.30], clr: true },
    USB_90: { nets: ["ESP_USB_DP", "ESP_USB_DN", "USB_DP", "USB_DN"], color: { r: 60, g: 120, b: 230, alpha: 1 }, track: [0.25, 0.20, 0.30], clr: false },
    PWR_3A: { nets: ["BAT_CONN", "BAT_FUSED", "RAW_BAT", "VBAT_SW", "VMODEM", "VBAT_M", "M_L1", "M_L2"], color: { r: 230, g: 140, b: 30, alpha: 1 }, track: [1.5, 0.8, 10], clr: true },
    PWR_1A: { nets: ["3V3", "BB_L1", "BB_L2", "PANEL_IN", "PANEL_FUSED", "SOLAR_IN", "CHG_SW_RAW", "CHG_SW", "CHARGE_SENSE"], color: { r: 200, g: 190, b: 40, alpha: 1 }, track: [0.5, 0.3, 5], clr: true },
  };   // track: [default, min, max] mm
  const PAIRS = [["USB", "USB_DP", "USB_DN"], ["ESP_USB", "ESP_USB_DP", "ESP_USB_DN"]];
  const out = [];
  const add = (s) => out.push(s);
  const msg = (e) => String((e && e.message) || e).slice(0, 200);
  const json = (v, n) => { try { return JSON.stringify(v).slice(0, n); } catch (e) { return "(not JSON)"; } };
  const clone = (v) => JSON.parse(JSON.stringify(v));

  await eda.dmt_EditorControl.openDocument(PCB_UUID);
  await new Promise((r) => setTimeout(r, 1500));
  const info = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  if (!info || info.uuid !== PCB_UUID) throw new Error("PCB not the current document: " + json(info, 200));

  const netNames = new Set(await eda.pcb_Net.getAllNetsName());
  const missing = Object.values(CLASSES).flatMap((c) => c.nets).filter((n) => !netNames.has(n));
  if (missing.length) throw new Error("nets not on the PCB: " + missing.join(", "));

  // 1. Rule configuration. The PCB's current configuration has its own format (per-layer "data" /
  // "tables" blocks); the named templates from getRuleConfiguration() use a flat "form"/"table" and
  // overwriteCurrentRuleConfiguration() ignores them (returns undefined, nothing changes; 4.1.105).
  // So the current configuration (JLC's 2-layer capability, stricter than the multilayer one) is
  // edited in place. Its name stays "JLCPCB Capability(Two Layers Board)".
  add("== 1. Rule configuration");
  const cfg = clone((await eda.pcb_Drc.getCurrentRuleConfiguration()).config);
  const defKey = (o) => Object.keys(o).find((k) => o[k].isSetDefault);
  const T = cfg.Physics.Track;
  const tDef = defKey(T);
  const setData = (form, v) => { for (const k of Object.keys(form.data)) form.data[k] = Object.assign({}, form.data[k], v); };
  setData(T[tDef].form, { defaultValue: DEFAULT_TRACK });
  for (const [name, c] of Object.entries(CLASSES)) {
    T[name] = clone(T[tDef]);
    T[name].editName = name; T[name].isSetDefault = false;
    setData(T[name].form, { defaultValue: c.track[0], minValue: c.track[1], maxValue: c.track[2] });
  }
  const S = cfg.Spacing["Safe Spacing"];
  const sDef = defKey(S);
  for (const t of Object.values(S[sDef].tables)) t.content[0][0] = Math.max(t.content[0][0], DEFAULT_TT_SPACING);
  S[CLR] = clone(S[sDef]);
  S[CLR].editName = CLR; S[CLR].isSetDefault = false;
  for (const t of Object.values(S[CLR].tables)) t.content = t.content.map((row) => row.map((v) => (typeof v === "number" ? Math.max(v, 0.2) : v)));
  // The only pairs are the two USB pairs, so the default pair rule takes the USB_90 geometry
  const DP = cfg.Physics["Differential Pair"];
  const dDef = DP[defKey(DP)];
  setData(dDef.form.strokeWidthTables, { defaultValue: 0.25, minValue: 0.2, maxValue: 0.3 });
  setData(dDef.form.diffPairSpacingTables, { defaultValue: 0.15, minValue: 0.127 });
  add(`overwriteCurrentRuleConfiguration -> ${await eda.pcb_Drc.overwriteCurrentRuleConfiguration(cfg)}`);
  const cur = await eda.pcb_Drc.getCurrentRuleConfiguration();
  const cT = cur.config.Physics.Track, cS = cur.config.Spacing["Safe Spacing"], cD = cur.config.Physics["Differential Pair"];
  add(`current name ${cur.name}; Track ${json(Object.keys(cT), 200)}; Safe Spacing ${json(Object.keys(cS), 200)}`);
  for (const k of Object.keys(cT)) add(`  track ${k}: ${json(cT[k].form.data, 120)}`);
  if (cS[CLR]) add(`  ${CLR} first rows ${json(Object.values(cS[CLR].tables)[0].content.slice(0, 3), 120)}; default track-track ${json(Object.values(cS[sDef].tables)[0].content[0], 40)}`);
  add(`  pair rule: ${json(cD[defKey(cD)].form, 300)}`);
  const ruleOk = Object.keys(CLASSES).every((k) => cT[k]) && !!cS[CLR];
  if (!ruleOk) add("  RULES NOT WRITTEN: class rows will be set to default");

  // 2. Net classes and differential pairs
  add("== 2. Net classes and pairs");
  const haveClasses = (await eda.pcb_Drc.getAllNetClasses()) || [];
  add(`  existing classes: ${json(haveClasses, 200)}`);
  // createNetClass takes alpha on a 0-255 scale (alpha 1 came back as 1/255); a class made with the
  // wrong alpha is deleted and made again
  for (const [name, c] of Object.entries(CLASSES)) {
    const have = haveClasses.find((x) => x && x.name === name);
    if (have && have.color && have.color.alpha > 0.5) { add(`  ${name}: exists`); continue; }
    if (have) add(`  ${name}: transparent colour, deleteNetClass -> ${await eda.pcb_Drc.deleteNetClass(name)}`);
    try { add(`  createNetClass ${name} (${c.nets.length}) -> ${await eda.pcb_Drc.createNetClass(name, c.nets, Object.assign({}, c.color, { alpha: 255 }))}`); } catch (e) { add(`  ${name} ERROR ${msg(e)}`); }
  }
  const havePairs = (await eda.pcb_Drc.getAllDifferentialPairs()) || [];
  for (const [name, p, n] of PAIRS) {
    if (havePairs.some((x) => x && (x.name === name || x.differentialPairName === name))) { add(`  pair ${name}: exists`); continue; }
    try { add(`  createDifferentialPair ${name} -> ${await eda.pcb_Drc.createDifferentialPair(name, p, n)}`); } catch (e) { add(`  pair ${name} ERROR ${msg(e)}`); }
  }
  add(`  classes now ${json(await eda.pcb_Drc.getAllNetClasses(), 400)}`);
  add(`  pairs now ${json(await eda.pcb_Drc.getAllDifferentialPairs(), 300)}`);

  // 3. Net rules
  add("== 3. Net rules");
  const nr = await eda.pcb_Drc.getNetRules();
  const types = {};
  for (const e of nr) types[e.type] = (types[e.type] || 0) + 1;
  add(`  ${nr.length} entries by type ${json(types, 200)}`);
  // After createNetClass, member nets move into the class entry's "sub" list; the class row and
  // each member row get the class rules
  const other = nr.filter((e) => e.type !== "net");
  if (other.length && other[0].sub) add(`  first class member entry: ${json(other[0].sub[0], 300)}`);
  const classOf = {};
  for (const [name, c] of Object.entries(CLASSES)) for (const n of c.nets) classOf[n] = name;
  let set = 0;
  const apply = (e, cls) => { e.Track = ruleOk ? cls : "default"; e["Safe Spacing"] = ruleOk && CLASSES[cls].clr ? CLR : "default"; set++; };
  for (const e of nr) {
    if (e.type === "net" && classOf[e.name]) apply(e, classOf[e.name]);
    if (e.type === "netClass" && CLASSES[e.name]) {
      apply(e, e.name);
      for (const s of e.sub || []) if (s && classOf[s.name]) apply(s, classOf[s.name]);
    }
  }
  add(`  entries changed ${set}; overwriteNetRules -> ${await eda.pcb_Drc.overwriteNetRules(nr)}`);
  const nr2 = await eda.pcb_Drc.getNetRules();
  const flat = nr2.flatMap((e) => [e, ...(e.sub || [])]);
  for (const n of ["ANT_FEED", "USB_DP", "VBAT_SW", "3V3", "GND"]) {
    const e = flat.find((x) => x.type === "net" && x.name === n);
    add(`  ${n}: Track ${e && e.Track}, Safe Spacing ${e && e["Safe Spacing"]}`);
  }
  for (const e of nr2.filter((x) => x.type !== "net")) add(`  ${e.type} ${e.name}: Track ${e.Track}, Safe Spacing ${e["Safe Spacing"]}, ${(e.sub || []).length} members`);
  add(`  classes ${json((await eda.pcb_Drc.getAllNetClasses()).map((c) => c.name + ":" + c.color.alpha), 200)}`);

  eda.sys_Dialog.showInformationMessage(out.join("\n"), "Auris phase 1b");
})().catch((e) => eda.sys_Dialog.showInformationMessage("Auris phase 1b stopped: " + ((e && e.stack) || e), "Auris phase 1b"));
