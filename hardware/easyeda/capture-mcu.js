// Auris schematic capture: mcu sheet (32 parts, 126 pin connections).
// Generated 2026-11-17 by hardware/tools/easyeda_capture.py from mcu/mcu-netlist.csv and mcu-bom.csv.
// Don't edit this file: change the CSVs, then run the generator again.
//
// What it does: places every part of the sheet on the open schematic page by its
// LCSC code, grouped by the blocks in hardware/tools/build_guide.py, each in a box
// with the heading the block has in the hardware guide. It sets each
// designator and BOM flag, then gives every pin a short wire carrying its net
// name. Pins marked NC get a no-connect flag. Parts are not wired to each other:
// connections come from the net names, so move things around freely afterwards.
//
// To run it in EasyEDA Pro:
//  1. Open the Auris project and an empty schematic page for this sheet.
//  2. Place one template part per kind on the page, keeping its default
//     designator: a test pad (any test-point part from the library) for
//     TP401, TP402, TP403. These parts have no LCSC code, so the script
//     copies the template's library part. It leaves the template where it is,
//     so delete it afterwards.
//  3. Advanced > Run Script (EasyEDA Pro v2: Settings > Extensions > Standalone
//     Script). Paste this whole file and run it. A dialog reports the result.
// Running it again skips designators already on the page, so after fixing an
// error you can run it again without getting duplicates.

(async () => {
  const SHEET = "mcu";
  // d: designator, lcsc: LCSC code ("" = copy a template part), fit: false = not fitted,
  // block: block in build_guide.py, pins: [pin number, pin name, net] from the netlist
  const PARTS = [
    {"d": "U401", "lcsc": "C2913202", "fit": true, "pins": [["1", "GND", "GND"], ["2", "3V3", "3V3"], ["3", "EN", "ESP_EN"], ["4", "IO4", "AUD_INT_MCU"], ["5", "IO5", "MIC1_DC_SENSE"], ["6", "IO6", "PREAMP_EN"], ["7", "IO7", "AUDIO_EN"], ["8", "IO15", "AUD_BCK"], ["9", "IO16", "AUD_LRCK"], ["10", "IO17", "AUD_DOUT"], ["11", "IO18", "AUD_SDA"], ["12", "IO8", "AUD_SCL"], ["13", "IO19", "ESP_USB_DN"], ["14", "IO20", "ESP_USB_DP"], ["15", "IO3", "USB_VSENSE"], ["16", "IO46", "NC"], ["17", "IO9", "AUD_MCLK"], ["18", "IO10", "PWR_HOLD"], ["19", "IO11", "MODEM_EN"], ["20", "IO12", "MODEM_PG"], ["21", "IO13", "SYS_SDA"], ["22", "IO14", "SYS_SCL"], ["23", "IO21", "LTE_PWRKEY"], ["24", "IO47", "SD_CLK"], ["25", "IO48", "SD_CMD"], ["26", "IO45", "SD_PWR_EN"], ["27", "IO0", "ESP_BOOT"], ["28", "IO35", "NC"], ["29", "IO36", "NC"], ["30", "IO37", "NC"], ["31", "IO38", "LTE_STATUS"], ["32", "IO39", "LTE_TX"], ["33", "IO40", "LTE_RX"], ["34", "IO41", "LTE_RTS"], ["35", "IO42", "LTE_CTS"], ["36", "RXD0", "SD_D0"], ["37", "TXD0", "STATUS_LED"], ["38", "IO2", "SOLAR_ADC"], ["39", "IO1", "BATT_ADC"], ["40", "GND", "GND"], ["41", "EPAD", "GND"]], "block": "m_module"},
    {"d": "C401", "lcsc": "C45783", "fit": true, "pins": [["1", "1", "3V3"], ["2", "2", "GND"]], "block": "m_module"},
    {"d": "C402", "lcsc": "C1525", "fit": true, "pins": [["1", "1", "3V3"], ["2", "2", "GND"]], "block": "m_module"},
    {"d": "R401", "lcsc": "C25744", "fit": true, "pins": [["1", "1", "3V3"], ["2", "2", "ESP_EN"]], "block": "m_module"},
    {"d": "C403", "lcsc": "C15849", "fit": true, "pins": [["1", "1", "ESP_EN"], ["2", "2", "GND"]], "block": "m_module"},
    {"d": "R402", "lcsc": "C25741", "fit": true, "pins": [["1", "1", "SD_PWR_EN"], ["2", "2", "GND"]], "block": "m_module"},
    {"d": "J401", "lcsc": "C2894897", "fit": true, "pins": [["A1", "GND", "GND"], ["A4", "VBUS", "VBUS"], ["A5", "CC1", "USB_CC1"], ["A6", "DP1", "USB_DP"], ["A7", "DN1", "USB_DN"], ["A8", "SBU1", "NC"], ["A9", "VBUS", "VBUS"], ["A12", "GND", "GND"], ["B1", "GND", "GND"], ["B4", "VBUS", "VBUS"], ["B5", "CC2", "USB_CC2"], ["B6", "DP2", "USB_DP"], ["B7", "DN2", "USB_DN"], ["B8", "SBU2", "NC"], ["B9", "VBUS", "VBUS"], ["B12", "GND", "GND"]], "block": "m_usb"},
    {"d": "D401", "lcsc": "C13612", "fit": true, "pins": [["1", "IO1", "USB_DP"], ["2", "REF1", "GND"], ["3", "IO2", "USB_DN"], ["4", "IO3", "USB_CC1"], ["5", "REF2", "VBUS"], ["6", "IO4", "USB_CC2"]], "block": "m_usb"},
    {"d": "R403", "lcsc": "C25905", "fit": true, "pins": [["1", "1", "USB_CC1"], ["2", "2", "GND"]], "block": "m_usb"},
    {"d": "R404", "lcsc": "C25905", "fit": true, "pins": [["1", "1", "USB_CC2"], ["2", "2", "GND"]], "block": "m_usb"},
    {"d": "R405", "lcsc": "C17168", "fit": true, "pins": [["1", "1", "USB_DP"], ["2", "2", "ESP_USB_DP"]], "block": "m_usb"},
    {"d": "R406", "lcsc": "C17168", "fit": true, "pins": [["1", "1", "USB_DN"], ["2", "2", "ESP_USB_DN"]], "block": "m_usb"},
    {"d": "R407", "lcsc": "C25756", "fit": false, "pins": [["1", "1", "VBUS"], ["2", "2", "USB_VSENSE"]], "block": "m_usb"},
    {"d": "R408", "lcsc": "C2909337", "fit": false, "pins": [["1", "1", "USB_VSENSE"], ["2", "2", "GND"]], "block": "m_usb"},
    {"d": "J402", "lcsc": "C393941", "fit": true, "pins": [["1", "DAT2", "SD_D2"], ["2", "CD/DAT3", "SD_D3"], ["3", "CMD", "SD_CMD"], ["4", "VDD", "SD_VDD"], ["5", "CLK", "SD_CLK"], ["6", "VSS", "GND"], ["7", "DAT0", "SD_D0"], ["8", "DAT1", "SD_D1"]], "block": "m_sd"},
    {"d": "R409", "lcsc": "C25744", "fit": true, "pins": [["1", "1", "SD_VDD"], ["2", "2", "SD_CMD"]], "block": "m_sd"},
    {"d": "R410", "lcsc": "C25744", "fit": true, "pins": [["1", "1", "SD_VDD"], ["2", "2", "SD_D0"]], "block": "m_sd"},
    {"d": "R411", "lcsc": "C25744", "fit": true, "pins": [["1", "1", "SD_VDD"], ["2", "2", "SD_D1"]], "block": "m_sd"},
    {"d": "R412", "lcsc": "C25744", "fit": true, "pins": [["1", "1", "SD_VDD"], ["2", "2", "SD_D2"]], "block": "m_sd"},
    {"d": "R413", "lcsc": "C25744", "fit": true, "pins": [["1", "1", "SD_VDD"], ["2", "2", "SD_D3"]], "block": "m_sd"},
    {"d": "Q401", "lcsc": "C15127", "fit": true, "pins": [["1", "G", "SD_PSW_G"], ["2", "S", "3V3"], ["3", "D", "SD_VDD"]], "block": "m_sd"},
    {"d": "Q402", "lcsc": "C8545", "fit": true, "pins": [["1", "G", "SD_PWR_EN"], ["2", "S", "GND"], ["3", "D", "SD_PSW_DRV"]], "block": "m_sd"},
    {"d": "R414", "lcsc": "C25741", "fit": true, "pins": [["1", "1", "3V3"], ["2", "2", "SD_PSW_G"]], "block": "m_sd"},
    {"d": "R415", "lcsc": "C25744", "fit": true, "pins": [["1", "1", "SD_PSW_G"], ["2", "2", "SD_PSW_DRV"]], "block": "m_sd"},
    {"d": "C406", "lcsc": "C1525", "fit": true, "pins": [["1", "1", "3V3"], ["2", "2", "SD_PSW_G"]], "block": "m_sd"},
    {"d": "C404", "lcsc": "C19702", "fit": true, "pins": [["1", "1", "SD_VDD"], ["2", "2", "GND"]], "block": "m_sd"},
    {"d": "C405", "lcsc": "C1525", "fit": true, "pins": [["1", "1", "SD_VDD"], ["2", "2", "GND"]], "block": "m_sd"},
    {"d": "LED401", "lcsc": "C12624", "fit": true, "pins": [["A", "A", "LED401_A"], ["K", "K", "GND"]], "block": "m_led"},
    {"d": "R416", "lcsc": "C25879", "fit": true, "pins": [["1", "1", "STATUS_LED"], ["2", "2", "LED401_A"]], "block": "m_led"},
    {"d": "TP401", "lcsc": "", "fit": true, "pins": [["1", "TP", "ESP_BOOT"]], "block": "m_test", "prefix": "TP"},
    {"d": "TP402", "lcsc": "", "fit": true, "pins": [["1", "TP", "ESP_EN"]], "block": "m_test", "prefix": "TP"},
    {"d": "TP403", "lcsc": "", "fit": true, "pins": [["1", "TP", "GND"]], "block": "m_test", "prefix": "TP"},
  ];
  const BLOCKS = [["m_module", "ESP32-S3 module"], ["m_usb", "USB-C service port"], ["m_sd", "microSD card and card supply"], ["m_led", "Status LED"], ["m_test", "Test points"]];
  const TEMPLATE_PREFIXES = ["TP"];
  const NC = "NC";

  const CFG = {
    grid: 5,          // schematic coordinates are in 10 mil units
    stub: 30,         // shortest wire stub from a pin
    charW: 6,         // estimated width of one net-name character
    padX: 30,         // room around each part for its pins' wires
    padY: 40,         // room above and below each part for designator and value text
    blockW: 900,      // width a block packs its parts into before starting a new row
    blockGap: 150,    // space between blocks
    pageW: 3200,      // width before blocks wrap to a new row
    titleH: 60,       // band at the top of each block box for its heading
    headingY: 40,     // heading baseline below the top of the box
    headingSize: 20,  // heading font size, bold
    headingCharW: 13, // estimated width of one heading character
    boxLine: 2,       // block box line width (1-10)
    down: 1,          // direction rows advance in: +1 = y grows downwards, as in EasyEDA Pro 3.2 (checked on the AURIS project)
    origin: [0, 0],   // top left corner of the first block
  };

  const sch = eda.sch_PrimitiveComponent;
  const errors = [], warnings = [];
  let nParts = 0, nCells = 0, nWires = 0, nNC = 0;
  const log = (m) => console.log(`[auris ${SHEET}] ${m}`);
  const toast = (m) => { log(m); try { eda.sys_ToastMessage.showMessage(m); } catch (_) { /* no toast in this version */ } };
  const snap = (v) => Math.round(v / CFG.grid) * CFG.grid;
  const msg = (e) => (e && e.message) || String(e);
  const tryCall = async (fn) => { try { return await fn(); } catch (_) { return undefined; } };
  let decorError = null;   // boxes and headings are drawing only: report the first failure once
  const decor = async (fn) => {
    try { if ((await fn()) === undefined) decorError = decorError || "EasyEDA returned nothing"; }
    catch (e) { decorError = decorError || msg(e); }
  };
  async function call(what, fn) {
    try {
      const r = await fn();
      if (r === undefined || r === false) errors.push(`${what}: EasyEDA returned nothing`);
      return r;
    } catch (e) {
      errors.push(`${what}: ${msg(e)}`);
      return undefined;
    }
  }

  // ---- what is on the page already ----------------------------------------
  const wanted = new Set(PARTS.map((p) => p.d));
  const present = new Set();
  const templates = {};
  let farthest = null;   // the existing sheet part farthest along CFG.down
  for (const c of (await tryCall(() => sch.getAll())) || []) {
    const des = c.getState_Designator && c.getState_Designator();
    if (!des) continue;
    if (wanted.has(des)) {
      present.add(des);
      const y = c.getState_Y();
      if (farthest === null || (y - farthest) * CFG.down > 0) farthest = y;
      continue;
    }
    for (const pre of TEMPLATE_PREFIXES) {
      if (!templates[pre] && new RegExp(`^${pre}\\d*\\??$`).test(des)) templates[pre] = c;
    }
  }

  // ---- library parts --------------------------------------------------------
  const devices = new Map();
  const notFound = new Map();   // LCSC code -> designators
  const fromTemplate = new Map();   // template designator -> designators copied from it
  async function deviceFor(part) {
    if (!part.lcsc) {
      const t = templates[part.prefix];
      if (!t) {
        errors.push(`${part.d}: no LCSC code, and no ${part.prefix} template part on the page to copy`);
        return undefined;
      }
      const td = t.getState_Designator();
      fromTemplate.set(td, [...(fromTemplate.get(td) || []), part.d]);
      return t.getState_Component();
    }
    if (!devices.has(part.lcsc)) {
      let dev;
      try { dev = await eda.lib_Device.getByLcscIds(part.lcsc); } catch (e) { dev = undefined; }
      devices.set(part.lcsc, dev);
    }
    const dev = devices.get(part.lcsc);
    if (!dev) notFound.set(part.lcsc, [...(notFound.get(part.lcsc) || []), part.d]);
    return dev;
  }

  // ---- pins -----------------------------------------------------------------
  const pinInfo = (p) => ({
    obj: p,
    num: String(p.getState_PinNumber()),
    name: String(p.getState_PinName() ?? ""),
    x: p.getState_X(),
    y: p.getState_Y(),
    rot: (((p.getState_Rotation() || 0) % 360) + 360) % 360,
  });
  const pinsOf = async (comp) =>
    ((await tryCall(() => sch.getAllPinsByPrimitiveId(comp.getState_PrimitiveId()))) || []).map(pinInfo);

  // Match netlist rows to symbol pins: by number first, then by pin name. A name shared by
  // several symbol pins (four GND pins on a USB-C socket) is only used when every netlist row
  // with that name is on the same net, so it does not matter which pin each row gets.
  function match(part, cells) {
    const pins = cells.flatMap((cell, i) => cell.pins.map((p) => Object.assign(p, { cell: i })));
    const byNum = new Map();
    for (const p of pins) if (!byNum.has(p.num)) byNum.set(p.num, p);
    const used = new Set(), links = [], missing = [], byName = [];
    for (const [num, name, net] of part.pins) {
      let p = byNum.get(num);
      if (!p || used.has(p)) {
        const c = pins.filter((q) => !used.has(q) && (q.name === name || q.name === num || q.num === name));
        const oneNet = part.pins.filter((r) => r[1] === name).every((r) => r[2] === net);
        p = c.length === 1 || (c.length > 1 && oneNet) ? c[0] : undefined;
        if (p) byName.push(`${num} as symbol pin ${p.num}`);
      }
      if (!p) { missing.push(name && name !== num ? `${num} (${name})` : num); continue; }
      used.add(p);
      links.push({ cell: p.cell, num: p.num, name: p.name, net, pin: p });
    }
    const extra = pins.filter((p) => !used.has(p)).map((p) => p.num);
    return { links, missing, extra, byName };
  }

  // A wire stub leaves each pin away from the middle of the symbol.
  function outward(p, cx, cy) {
    if (p.rot === 0 || p.rot === 180) return [Math.sign(p.x - cx) || (p.rot === 0 ? -1 : 1), 0];
    return [0, Math.sign(p.y - cy) || (p.rot === 90 ? -1 : 1)];
  }
  const stubLen = (net) => (net === NC ? 0 : Math.ceil(Math.max(CFG.stub, CFG.charW * net.length + 10) / 10) * 10);

  // Box around a symbol's pins and their stubs, relative to the symbol origin.
  function cellBox(cell, links) {
    const ox = cell.comp.getState_X(), oy = cell.comp.getState_Y();
    const ps = cell.pins;
    if (!ps.length) return { l: -40, r: 40, lo: -40, hi: 40 };
    const xs = ps.map((p) => p.x), ys = ps.map((p) => p.y);
    let minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
    const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2;
    for (const l of links) {
      [l.ux, l.uy] = outward(l.pin, cx, cy);
      const len = stubLen(l.net);
      minX = Math.min(minX, l.pin.x + l.ux * len); maxX = Math.max(maxX, l.pin.x + l.ux * len);
      minY = Math.min(minY, l.pin.y + l.uy * len); maxY = Math.max(maxY, l.pin.y + l.uy * len);
    }
    return { l: minX - CFG.padX - ox, r: maxX + CFG.padX - ox, lo: minY - CFG.padY - oy, hi: maxY + CFG.padY - oy };
  }

  // ---- place one part (all of its symbol parts) at a staging spot ----------
  const STAGE = [CFG.origin[0] - 4000, CFG.origin[1]];
  async function stagePart(part) {
    const dev = await deviceFor(part);
    if (!dev) return undefined;
    const first = await call(`${part.d}: place`, () => sch.create(dev, STAGE[0], STAGE[1], undefined, 0, false, part.fit, true));
    if (!first) return undefined;
    const cells = [{ comp: first, pins: await pinsOf(first) }];
    let res = match(part, cells);
    // Multi-part symbols (e.g. a dual op-amp) are named NAME.1, NAME.2, ...: add parts until every pin is found.
    const m = String((first.getState_SubPartName && first.getState_SubPartName()) || "").match(/^(.*)\.(\d+)$/);
    for (let k = m ? Number(m[2]) + 1 : 0; m && res.missing.length && k <= 16; k++) {
      const c = await tryCall(() => sch.create(dev, STAGE[0], STAGE[1] + CFG.down * 600 * cells.length, `${m[1]}.${k}`, 0, false, part.fit, true));
      if (!c) break;
      cells.push({ comp: c, pins: await pinsOf(c) });
      res = match(part, cells);
    }
    const tag = part.lcsc ? `${part.d} (${part.lcsc})` : part.d;
    if (res.missing.length) errors.push(`${tag}: netlist pins not on the EasyEDA symbol: ${res.missing.join(", ")}`);
    if (res.extra.length) warnings.push(`${tag}: symbol pins not in the netlist, left unconnected: ${res.extra.join(", ")}`);
    if (res.byName.length) warnings.push(`${tag}: matched by pin name: ${res.byName.join(", ")}`);
    return { cells, links: res.links };
  }

  // ---- move a staged symbol into place and wire its pins -------------------
  async function finishCell(part, cell, i, links, ox, oy) {
    const id = cell.comp.getState_PrimitiveId();
    const moved = await call(`${part.d}: move and set designator`, () =>
      sch.modify(id, { x: ox, y: oy, designator: part.d, addIntoBom: part.fit, addIntoPcb: true }));
    if (!moved) return;
    nCells++;
    const pins = await pinsOf(cell.comp);
    for (const l of links.filter((l) => l.cell === i)) {
      const p = pins.find((q) => q.num === l.num && q.name === l.name);
      if (!p) { errors.push(`${part.d} pin ${l.num}: not found after moving the part`); continue; }
      if (l.net === NC) {
        try { p.obj.setState_NoConnected(true); await p.obj.done(); nNC++; }
        catch (e) { warnings.push(`${part.d} pin ${l.num}: could not set the no-connect flag (${msg(e)})`); }
        continue;
      }
      const len = stubLen(l.net);
      const ex = p.x + l.ux * len, ey = p.y + l.uy * len;
      // Start the wire at its left (or lower) end, where EasyEDA anchors the net name.
      const line = l.ux < 0 || l.uy < 0 ? [ex, ey, p.x, p.y] : [p.x, p.y, ex, ey];
      const w = await call(`${part.d} pin ${l.num} to ${l.net}`, () => eda.sch_PrimitiveWire.create(line, l.net));
      if (w) nWires++;
    }
  }

  // ---- lay out block by block ----------------------------------------------
  const page = { x: CFG.origin[0], y: farthest === null ? CFG.origin[1] : farthest + CFG.down * 800, rowH: 0 };
  for (const [block, title] of BLOCKS) {
    const parts = PARTS.filter((p) => p.block === block && !present.has(p.d));
    if (!parts.length) continue;
    if (page.x > CFG.origin[0] && page.x + CFG.blockW > CFG.origin[0] + CFG.pageW) {
      page.x = CFG.origin[0];
      page.y += CFG.down * (page.rowH + CFG.blockGap);
      page.rowH = 0;
    }
    const bx = page.x, by = page.y;
    const heading = PARTS.some((p) => p.block === block && present.has(p.d)) ? `${title} (continued)` : title;
    toast(`Auris ${SHEET}: placing ${heading} (${parts.length} parts)`);
    let rx = bx, ry = by + CFG.down * CFG.titleH, rowH = 0, width = 0;
    for (const part of parts) {
      const staged = await stagePart(part);
      if (!staged) continue;
      nParts++;
      for (const [i, cell] of staged.cells.entries()) {
        const box = cellBox(cell, staged.links.filter((l) => l.cell === i));
        const w = box.r - box.l, h = box.hi - box.lo;
        if (rx > bx && rx + w > bx + CFG.blockW) {
          rx = bx;
          ry += CFG.down * rowH;
          rowH = 0;
        }
        const top = CFG.down < 0 ? box.hi : box.lo;
        await finishCell(part, cell, i, staged.links, snap(rx - box.l), snap(ry - top));
        rx += w;
        rowH = Math.max(rowH, h);
        width = Math.max(width, rx - bx);
      }
    }
    // Box the block with its heading inside the top edge, as the hardware guide shows it.
    // The box's top left corner is (bx, by) and it extends right and in the CFG.down direction.
    const boxW = snap(Math.max(width, heading.length * CFG.headingCharW + 2 * CFG.padX));
    const boxH = snap(Math.abs(ry - by) + rowH);
    await decor(() => eda.sch_PrimitiveRectangle.create(bx, by, boxW, boxH, 0, 0, null, "none", CFG.boxLine));
    await decor(() => eda.sch_PrimitiveText.create(bx + CFG.padX, by + CFG.down * CFG.headingY, heading, 0, null, null, CFG.headingSize, true));
    page.x = bx + boxW + CFG.blockGap;
    page.rowH = Math.max(page.rowH, boxH);
  }

  // ---- report ---------------------------------------------------------------
  for (const [code, ds] of notFound) errors.unshift(`${code} not found in the EasyEDA library, not placed: ${ds.join(", ")}`);
  if (decorError) warnings.push(`Some block boxes or headings were not drawn: ${decorError}`);
  for (const [td, ds] of fromTemplate) {
    warnings.push(`${ds.join(", ")}: copied from template ${td}, so check value and footprint. Delete ${td} when done.`);
  }
  const head = [`${SHEET} sheet: placed ${nParts} parts (${nCells} symbols), ${nWires} net wires, ${nNC} no-connect flags.`];
  if (present.size) head.push(`Skipped ${present.size} parts already on the page.`);
  const show = (title, list, max) =>
    list.length ? ["", `${title} (${list.length}):`, ...list.slice(0, max), ...(list.length > max ? [`...and ${list.length - max} more in the browser console`] : [])] : [];
  const report = [...head, ...show("Errors", errors, 25), ...show("Warnings", warnings, 10)].join("\n");
  log([...head, ...show("Errors", errors, 1e9), ...show("Warnings", warnings, 1e9)].join("\n"));
  try { eda.sys_Dialog.showInformationMessage(report, `Auris capture: ${SHEET}`); } catch (_) { toast(head[0]); }
})().catch((e) => {
  const m = `Auris capture stopped: ${(e && e.stack) || e}`;
  console.error(m);
  try { eda.sys_Dialog.showInformationMessage(m, "Auris capture"); } catch (_) { /* console only */ }
});
