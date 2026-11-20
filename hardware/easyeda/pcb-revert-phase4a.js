// Auris: revert the board to the phase 4a state (owner decision 2026-11-20, "I will route myself"):
// every via and copper track goes, and the top-side power pours of phase 4c. The GND pours (L1, L2, L4),
// the L3 3V3/VMODEM pours, the keep-out regions and the rule changes stay. Not saved (pcb-export.js saves).
// Run: __aurisRun(code, { titleRe: /^Auris revert/ })
(async () => {
  const out = [];
  const POWER_POURS = new Set(["3V3 OUT", "CHG_SW", "RAW_BAT BAT", "RAW_BAT CHARGER", "RAW_BAT NECK", "SOLAR_IN A", "SOLAR_IN B", "VBAT_M TOP", "VBAT_SW BRIDGE", "VBAT_SW IN", "VBAT_SW U206", "VMODEM OUT", "VMODEM OUT B", "VMODEM TOP"]);
  const mine = (n) => { n = String(n || "").toUpperCase(); return POWER_POURS.has(n) || POWER_POURS.has(n.replace(/\d+$/, "")); };
  const vias = await eda.pcb_PrimitiveVia.getAll();
  const vids = vias.map((v) => v.getState_PrimitiveId());
  out.push(`vias deleted: ${vids.length} -> ${vids.length ? await eda.pcb_PrimitiveVia.delete(vids) : "none"}`);
  let n = 0;
  for (const layer of [1, 2, 15, 16]) {
    const lines = await eda.pcb_PrimitiveLine.getAll(undefined, layer);
    const ids = lines.map((l) => l.getState_PrimitiveId());
    if (ids.length) { await eda.pcb_PrimitiveLine.delete(ids); n += ids.length; }
  }
  out.push(`copper lines deleted: ${n}`);
  const pours = await eda.pcb_PrimitivePour.getAll();
  const gone = pours.filter((p) => mine(p.getState_PourName && p.getState_PourName()));
  if (gone.length) out.push(`power pours deleted: ${gone.length} -> ${await eda.pcb_PrimitivePour.delete(gone.map((p) => p.getState_PrimitiveId()))}`);
  const left = await eda.pcb_PrimitivePour.getAll();
  out.push("pours left: " + left.map((p) => `${p.getState_PourName()} (L${p.getState_Layer()})`).join(", "));
  try { const r = await eda.pcb_PrimitivePour.rebuildAllCopperRegions(); out.push(`pours rebuilt: ${Array.isArray(r) ? r.length : r}`); } catch (e) { out.push("rebuild: " + ((e && e.message) || e)); }
  const regions = await eda.pcb_PrimitiveRegion.getAll();
  out.push(`regions kept: ${regions.length}`);
  eda.sys_Dialog.showInformationMessage(out.join("\n"), "Auris revert");
})().catch((e) => eda.sys_Dialog.showInformationMessage("Auris revert stopped: " + ((e && e.stack) || e), "Auris revert"));
