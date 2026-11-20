// Auris: run the PCB DRC and summarise the violations by rule and error type (nothing is changed).
// Run: __aurisRun(code, { titleRe: /^Auris DRC/, timeoutMs: 120000 })
(async () => {
  const groups = await eda.pcb_Drc.check(false, false, true);
  const count = {};
  const details = [];
  let rawFirst = null;
  let total = 0;
  const MIL = 0.0254;
  const walk = (g) => {
    for (const item of (g && g.list) || []) {
      if (item.errorType !== undefined) {
        total++;
        const k = `${item.errorType} / ${item.ruleName || "-"} / ${(item.obj1 && item.obj1.typeName) || "-"}`;
        count[k] = (count[k] || 0) + 1;
        if (!/Connection/.test(String(item.errorType)) && !rawFirst) rawFirst = JSON.stringify(item).slice(0, 700);
        if ((!/Connection/.test(String(item.errorType)) || /Via|Track/.test(String((item.obj1 || {}).typeName))) && details.length < 80) {
          const ed = item.errData || (item.explanation && item.explanation.errData) || {};
          const p = ed.position || {};
          const o1 = item.obj1 || {}, o2 = (item.errData && item.errData.obj2) || item.obj2 || {};
          // errData.position is in units of 10 mil (checked 2026-11-20 against a known via)
          details.push(`${item.errorType}|${item.ruleName}|${item.net || ""}|${o1.typeName || ""} ${o1.suffix || ""}|${o2.typeName || ""} ${o2.suffix || ""}|(${(p.x * 0.254).toFixed(2)}, ${(p.y * 0.254).toFixed(2)}) mm`);
        }
      } else walk(item);
    }
  };
  for (const g of groups || []) walk(g);
  const res = await eda.pcb_Drc.getDrcResult();
  const lines = [`DRC: ${total} violations; result state ${res && res.state}, totalCount ${res && res.totalCount}`];
  for (const [k, v] of Object.entries(count).sort((a, b) => b[1] - a[1]).slice(0, 15)) lines.push(`${v} x ${k}`);
  for (const d of details) lines.push(d);

  eda.sys_Dialog.showInformationMessage(lines.join("\n"), "Auris DRC");
})().catch((e) => eda.sys_Dialog.showInformationMessage(`DRC stopped: ${(e && e.message) || e}`, "Auris DRC"));
