// Auris: empty the open schematic page before a re-capture (keeps the page frame).
// Set EXPECT to the page's name (LTE, POWER, AUDIO or MCU). If another page is open, nothing is deleted.
// Run it through Advanced > Run Script or the page driver (hardware/tools/easyeda_page_driver.js),
// then run that sheet's hardware/easyeda/capture-<sheet>.js.
(async () => {
  const EXPECT = "SET_ME";
  const page = await eda.dmt_Schematic.getCurrentSchematicPageInfo();
  if (EXPECT === "SET_ME") throw new Error("set EXPECT to the page name first: nothing deleted");
  if (String(page.name) !== EXPECT) throw new Error(`open page is ${page.name}, not ${EXPECT}: nothing deleted`);
  const out = [];
  const ids = (l) => l.map((p) => p.getState_PrimitiveId());
  const parts = ((await eda.sch_PrimitiveComponent.getAll()) || []).filter((c) => c.getState_ComponentType() === "part");
  const wires = (await eda.sch_PrimitiveWire.getAll()) || [];
  const rects = (await eda.sch_PrimitiveRectangle.getAll()) || [];
  const texts = (await eda.sch_PrimitiveText.getAll()) || [];
  for (const [api, list, what] of [[eda.sch_PrimitiveWire, wires, "wires"], [eda.sch_PrimitiveComponent, parts, "parts"], [eda.sch_PrimitiveRectangle, rects, "boxes"], [eda.sch_PrimitiveText, texts, "texts"]]) {
    if (list.length) out.push(`deleted ${list.length} ${what}: ${await api.delete(ids(list))}`);
  }
  const left = ((await eda.sch_PrimitiveComponent.getAll()) || []).map((c) => c.getState_ComponentType());
  out.push(`left on ${page.name}: ${left.join(", ")}`);
  eda.sys_MessageBox.showInformationMessage(out.join("\n"), "Auris clear page");
})().catch((e) => eda.sys_MessageBox.showInformationMessage(`clear stopped: ${(e && e.message) || e}`, "Auris clear page"));
