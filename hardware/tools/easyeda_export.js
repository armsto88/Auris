// Auris: download the open EasyEDA Pro project as .epro2 and its whole-project BOM as .csv.
// Both land in the browser's download folder (~/Downloads) without a dialog (checked 2026-11-17).
// The BOM has EasyEDA's LCSC and JLCPCB stock and price columns. Move the .epro2 to hardware/<date>/.
(async () => {
  const EXPORT_PROJECT = true, EXPORT_BOM = true;
  const day = new Date().toISOString().slice(0, 10);
  const out = [];
  try { out.push(`saved open page: ${await eda.sch_Document.save()}`); } catch (e) { out.push(`save failed: ${(e && e.message) || e}`); }
  if (EXPORT_PROJECT) {
    const f = await eda.sys_FileManager.getProjectFile(`AURIS_${day}`, undefined, ".epro2");
    if (!f) throw new Error("getProjectFile returned nothing");
    await eda.sys_FileSystem.saveFile(f, `AURIS_${day}.epro2`);
    out.push(`project: AURIS_${day}.epro2, ${f.size} bytes`);
  }
  if (EXPORT_BOM) {
    const f = await eda.sch_ManufactureData.getBomFile(`AURIS_BOM_${day}`, "csv");
    if (!f) throw new Error("getBomFile returned nothing");
    await eda.sys_FileSystem.saveFile(f, `AURIS_BOM_${day}.csv`);
    out.push(`BOM: AURIS_BOM_${day}.csv, ${f.size} bytes`);
  }
  eda.sys_MessageBox.showInformationMessage(out.join("\n"), "Auris export");
})().catch((e) => eda.sys_MessageBox.showInformationMessage(`export stopped: ${(e && e.message) || e}`, "Auris export"));
