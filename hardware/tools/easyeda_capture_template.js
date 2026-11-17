// Auris schematic capture: __SHEET__ sheet (__NPARTS__ parts, __NROWS__ pin connections).
// Generated __DATE__ by hardware/tools/easyeda_capture.py from __SOURCES__.
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
//  2. __TEMPLATE_STEP__
//  3. Advanced > Run Script (EasyEDA Pro v2: Settings > Extensions > Standalone
//     Script). Paste this whole file and run it. A dialog reports the result.
// Running it again skips designators already on the page, so after fixing an
// error you can run it again without getting duplicates.

(async () => {
  const SHEET = __SHEET_JSON__;
  // d: designator, lcsc: LCSC code ("" = copy a template part), fit: false = not fitted,
  // block: block in build_guide.py, pins: [pin number, pin name, net] from the netlist
  const PARTS = __PARTS_JSON__;
  const BLOCKS = __BLOCKS_JSON__;
  const TEMPLATE_PREFIXES = __PREFIX_JSON__;
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
