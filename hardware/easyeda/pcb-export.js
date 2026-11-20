// Auris: save the open PCB and download the whole project as AURIS_<date>.epro2 (lands in
// ~/Downloads without a dialog). PCB counterpart of hardware/tools/easyeda_export.js (no BOM: that
// call needs a schematic page active). Run: __aurisRun(code, { titleRe: /^Auris export/ })
(async () => {
  const day = new Date().toISOString().slice(0, 10);
  const out = [];
  try { out.push(`saved PCB: ${await eda.pcb_Document.save()} (false means EasyEDA had already saved)`); } catch (e) { out.push(`save failed: ${(e && e.message) || e}`); }
  const f = await eda.sys_FileManager.getProjectFile(`AURIS_${day}`, undefined, ".epro2");
  if (!f) throw new Error("getProjectFile returned nothing");
  await eda.sys_FileSystem.saveFile(f, `AURIS_${day}.epro2`);
  out.push(`project: AURIS_${day}.epro2, ${f.size} bytes`);
  eda.sys_Dialog.showInformationMessage(out.join("\n"), "Auris export");
})().catch((e) => eda.sys_Dialog.showInformationMessage(`export stopped: ${(e && e.message) || e}`, "Auris export"));
