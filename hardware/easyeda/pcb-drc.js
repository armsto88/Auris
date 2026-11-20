// Auris: run the PCB DRC and summarise the violations by rule and error type (nothing is changed).
// Run: __aurisRun(code, { titleRe: /^Auris DRC/, timeoutMs: 120000 })
(async () => {
  const groups = await eda.pcb_Drc.check(false, false, true);
  const count = {};
  let total = 0;
  const walk = (g) => {
    for (const item of (g && g.list) || []) {
      if (item.errorType !== undefined) {
        total++;
        const k = `${item.errorType} / ${item.ruleName || "-"} / ${(item.obj1 && item.obj1.typeName) || "-"}`;
        count[k] = (count[k] || 0) + 1;
      } else walk(item);
    }
  };
  for (const g of groups || []) walk(g);
  const res = await eda.pcb_Drc.getDrcResult();
  const lines = [`DRC: ${total} violations; result state ${res && res.state}, totalCount ${res && res.totalCount}`];
  for (const [k, v] of Object.entries(count).sort((a, b) => b[1] - a[1]).slice(0, 15)) lines.push(`${v} x ${k}`);
  eda.sys_Dialog.showInformationMessage(lines.join("\n"), "Auris DRC");
})().catch((e) => eda.sys_Dialog.showInformationMessage(`DRC stopped: ${(e && e.message) || e}`, "Auris DRC"));
