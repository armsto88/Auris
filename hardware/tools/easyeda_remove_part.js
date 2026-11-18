// Auris: delete one part and the net-name wire stubs on its pins from the open schematic page, so the
// capture script can place it again (e.g. with a new device) without clearing the page.
// Set PAGE (LTE, POWER, AUDIO or MCU), TARGET (designator) and EXPECTED (the part's netlist rows that
// are not NC, i.e. its stub wires). Nothing is deleted unless the open page and the stub count match.
// Then run that sheet's hardware/easyeda/capture-<sheet>.js: it skips the parts already on the page
// and places only the missing ones, in a box below the existing blocks. Used 2026-11-18 for U301 and
// U401 on EasyEDA Pro 4.1.105, where clearing and re-capturing a whole page failed.
(async () => {
  const PAGE = "SET_ME", TARGET = "SET_ME", EXPECTED = -1;
  if (PAGE === "SET_ME" || TARGET === "SET_ME" || EXPECTED < 0) throw new Error("set PAGE, TARGET and EXPECTED first: nothing deleted");
  const page = await eda.dmt_Schematic.getCurrentSchematicPageInfo();
  if (String(page && page.name) !== PAGE) throw new Error("open page is " + (page && page.name) + ", not " + PAGE + ": nothing deleted");
  const comps = ((await eda.sch_PrimitiveComponent.getAll()) || []).filter((c) => c.getState_ComponentType() === "part" && String(c.getState_Designator()) === TARGET);
  if (comps.length !== 1) throw new Error(comps.length + " parts named " + TARGET + ": nothing deleted");
  const comp = comps[0];
  const pins = (await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(comp.getState_PrimitiveId())) || [];
  const key = (x, y) => Math.round(x * 10) + "," + Math.round(y * 10);
  const pts = new Set(pins.map((p) => key(p.getState_X(), p.getState_Y())));
  const wires = (await eda.sch_PrimitiveWire.getAll()) || [];
  const hit = [];
  for (const w of wires) {
    const line = w.getState_Line();
    const flat = Array.isArray(line[0]) ? [].concat(...line) : line;
    for (let i = 0; i + 1 < flat.length; i += 2) if (pts.has(key(flat[i], flat[i + 1]))) { hit.push(w); break; }
  }
  const info = TARGET + " (" + (comp.getState_SupplierId ? comp.getState_SupplierId() : "?") + "): " + pins.length + " pins, " + hit.length + " stub wires";
  if (hit.length !== EXPECTED) throw new Error(info + ", expected " + EXPECTED + ": nothing deleted");
  const w = await eda.sch_PrimitiveWire.delete(hit.map((x) => x.getState_PrimitiveId()));
  const c = await eda.sch_PrimitiveComponent.delete([comp.getState_PrimitiveId()]);
  eda.sys_MessageBox.showInformationMessage(info + "; deleted wires " + w + ", part " + c, "Auris remove");
})().catch((e) => eda.sys_MessageBox.showInformationMessage("remove stopped: " + ((e && e.message) || e), "Auris remove"));
