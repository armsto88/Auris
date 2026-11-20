// Auris: delete every via and every track on the copper layers (1, 2, 15, 16) so a routing script can be
// re-run from a clean board. Pours, regions, parts and pads are untouched. Not saved.
// Run: __aurisRun(code, { titleRe: /^Auris clear/ })
(async () => {
  const out = [];
  const vias = await eda.pcb_PrimitiveVia.getAll();
  const vids = vias.map((v) => v.getState_PrimitiveId());
  out.push(`vias: ${vids.length} -> ${vids.length ? await eda.pcb_PrimitiveVia.delete(vids) : "none"}`);
  let n = 0;
  for (const layer of [1, 2, 15, 16]) {
    const lines = await eda.pcb_PrimitiveLine.getAll(undefined, layer);   // getAll(net, layer, lock)
    const ids = lines.map((l) => l.getState_PrimitiveId());
    if (ids.length) { await eda.pcb_PrimitiveLine.delete(ids); n += ids.length; }
  }
  out.push(`copper lines deleted: ${n}`);
  try { const r = await eda.pcb_PrimitivePour.rebuildAllCopperRegions(); out.push(`pours rebuilt: ${Array.isArray(r) ? r.length : r}`); } catch (e) { out.push("rebuild: " + ((e && e.message) || e)); }
  eda.sys_Dialog.showInformationMessage(out.join("\n"), "Auris clear routing");
})().catch((e) => eda.sys_Dialog.showInformationMessage("Auris clear routing stopped: " + ((e && e.stack) || e), "Auris clear routing"));
