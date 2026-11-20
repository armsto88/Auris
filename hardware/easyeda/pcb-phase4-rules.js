// Auris phase 4 rule changes (owner decisions 2026-11-20): PWR_3A minimum track 0.8 -> 0.3 mm, PWR_1A
// minimum 0.3 -> 0.25 mm (branches to 0402 pads and the 0.3 mm pins of U206), and the two USB
// differential-pair definitions removed (R405/R406 sit apart; USB full speed does not need the pair rule).
// Edits the PCB's current rule configuration in place, as pcb-phase1-rules.js did. Not saved.
// Run: __aurisRun(code, { titleRe: /^Auris rules/ })
(async () => {
  const out = [];
  const clone = (o) => JSON.parse(JSON.stringify(o));
  const cfg = clone((await eda.pcb_Drc.getCurrentRuleConfiguration()).config);
  const T = cfg.Physics.Track;
  const setMin = (name, v) => { if (!T[name]) { out.push(`${name}: no such track rule`); return; } for (const k of Object.keys(T[name].form.data)) T[name].form.data[k] = Object.assign({}, T[name].form.data[k], { minValue: v }); out.push(`${name} minValue -> ${v}`); };
  setMin("PWR_3A", 0.3);
  setMin("PWR_1A", 0.25);
  out.push(`overwriteCurrentRuleConfiguration -> ${await eda.pcb_Drc.overwriteCurrentRuleConfiguration(cfg)}`);
  const cur = (await eda.pcb_Drc.getCurrentRuleConfiguration()).config.Physics.Track;
  for (const n of ["PWR_3A", "PWR_1A"]) out.push(`${n} now: ${JSON.stringify(cur[n].form.data["1"])}`);
  for (const pr of ["USB", "ESP_USB"]) {
    try { out.push(`deleteDifferentialPair(${pr}) -> ${await eda.pcb_Drc.deleteDifferentialPair(pr)}`); } catch (e) { out.push(`${pr}: ${(e && e.message) || e}`); }
  }
  try { out.push(`pairs left: ${JSON.stringify(await eda.pcb_Drc.getAllDifferentialPairs()).slice(0, 200)}`); } catch (e) { out.push("pairs: " + e); }
  eda.sys_Dialog.showInformationMessage(out.join("\n"), "Auris rules");
})().catch((e) => eda.sys_Dialog.showInformationMessage("Auris rules stopped: " + ((e && e.stack) || e), "Auris rules"));
