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
    padX: 20,         // room left and right of each part (its pin wires are counted separately)
    padY: 20,         // room above and below each part for designator and value text
    blockGap: 40,     // space between blocks
    blockAspect: 1.4, // width / height each block's parts are packed towards
    pageAspect: 1.414,// width / height the blocks are packed towards: an A-series sheet, landscape
    orderBonus: 0.03, // another packing order must save this much (3 %) to beat the netlist / guide order
    shuffles: 300,    // extra block orders tried when packing the page (fixed seed, so repeatable)
    titleH: 50,       // band at the top of each block box for its heading
    headingY: 35,     // heading baseline below the top of the box
    headingSize: 20,  // heading font size, bold
    headingCharW: 13, // estimated width of one heading character
    boxLine: 2,       // block box line width (1-10)
    down: -1,         // direction rows advance in: in EasyEDA Pro 3.2 the API's y grows UP the screen, so -1 lays blocks out downwards (checked on the AURIS project 2026-11-17)
    border: 6,        // mm kept clear inside the page frame's edge (its zone band is 2.54 mm)
    titleBlock: [182, 51], // mm, the title block in the frame's bottom right corner; null if it is hidden
    // Library parts for parts without an LCSC code when no template part is on the page:
    // TP = the test point picked for LTE on 2026-11-17 (BOM asks for a 1.0 mm pad: check the footprint);
    // C = a 0402 capacitor (untuned RF parts: value is set later).
    templateDefaults: { TP: { name: "Test-Point", footprint: "Test-Point-0.5mm" }, C: { lcsc: "C1525" } },
    timeout: 20000,   // ms to wait for one EasyEDA call before reporting it as an error instead of hanging
  };

  const sch = eda.sch_PrimitiveComponent;
  const errors = [], warnings = [];
  let nParts = 0, nCells = 0, nWires = 0, nNC = 0;
  const log = (m) => console.log(`[auris ${SHEET}] ${m}`);
  const toast = (m) => { log(m); try { eda.sys_ToastMessage.showMessage(m); } catch (_) { /* no toast in this version */ } };
  const snap = (v) => Math.round(v / CFG.grid) * CFG.grid;
  const msg = (e) => (e && e.message) || String(e);
  // Some EasyEDA calls never settle (sch.create with an unknown device does that), so every call
  // races a timer: a call that hangs becomes an error in the report instead of stopping the run.
  const TIMEOUT = Symbol("timeout");
  const within = (p) => Promise.race([Promise.resolve(p), new Promise((r) => setTimeout(() => r(TIMEOUT), CFG.timeout))]);
  const noAnswer = `EasyEDA did not answer within ${CFG.timeout / 1000} s`;
  const tryCall = async (fn) => { try { const r = await within(fn()); return r === TIMEOUT ? undefined : r; } catch (_) { return undefined; } };
  let decorError = null;   // boxes and headings are drawing only: report the first failure once
  const decor = async (fn) => {
    try {
      const r = await within(fn());
      if (r === undefined || r === TIMEOUT) decorError = decorError || (r === TIMEOUT ? noAnswer : "EasyEDA returned nothing");
    } catch (e) { decorError = decorError || msg(e); }
  };
  async function call(what, fn) {
    try {
      const r = await within(fn());
      if (r === TIMEOUT) { errors.push(`${what}: ${noAnswer}`); return undefined; }
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
  // The page frame is a "sheet" component at (0, 0), its bottom left corner: it grows up and to
  // the right when the page size changes. Its Width and Height properties (10 mil units) follow
  // the page size; its "Page Size" property and symbol name do not (they stay "A4").
  const SHEETS = [["A4", 297, 210], ["A3", 420, 297], ["A2", 594, 420], ["A1", 841, 594], ["A0", 1189, 841]];
  let page = null;   // {w, h, titleBlock}
  for (const c of (await tryCall(() => sch.getAll())) || []) {
    if (c.getState_ComponentType && c.getState_ComponentType() === "sheet") {
      const o = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
      const w = Number(o.Width), h = Number(o.Height);
      if (w > 0 && h > 0) page = { w, h, titleBlock: String(o["Title Block"] ?? "1") !== "0" };
      continue;
    }
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
  const fromTemplate = new Map();   // source label -> designators placed from it
  const templateLost = new Map();   // source label -> [why, designators not placed]
  const sourceDevices = new Map();   // source label -> its library device, or null
  // Parts without an LCSC code are placed as a library device found by LCSC code, or else by exact
  // name (preferring the given footprint). The source is a template part on the page if there is
  // one (its getState_Component() names its copy in the project, not the library device, and
  // sch.create() never returns for it), otherwise the default in CFG.templateDefaults.
  // EasyEDA Pro 4.1 cannot place a system-library device whose copy in the project library is out
  // of date ("Create project component failed"; sch.create() never returns, and the next few
  // creates fail too). So a device the project already holds is placed from the project's copy,
  // which is also the version the parts on the other pages use; only new devices come from the
  // system library.
  let projectLib;
  async function projectCopy(dev) {
    if (!dev || !dev.name) return null;
    if (projectLib === undefined) projectLib = (await tryCall(() => eda.lib_LibrariesList.getProjectLibraryUuid())) || null;
    if (!projectLib) return null;
    const found = (await tryCall(() => eda.lib_Device.search(dev.name, projectLib))) || [];
    return (Array.isArray(found) ? found : [found]).find((d) => d && d.name === dev.name) || null;
  }
  async function sourceDevice(label, { lcsc = "", name = "", footprint = "" }) {
    if (sourceDevices.has(label)) return sourceDevices.get(label);
    let dev = null, why = "";
    if (/^C\d+$/.test(lcsc)) dev = (await tryCall(() => eda.lib_Device.getByLcscIds(lcsc))) || null;
    if (!dev) {
      const found = name ? (await tryCall(() => eda.lib_Device.search(name))) || [] : [];
      const named = (Array.isArray(found) ? found : [found]).filter((d) => d && d.name === name);
      const sameFp = named.filter((d) => footprint && d.footprintName === footprint);
      dev = sameFp.length === 1 ? sameFp[0] : named.length === 1 ? named[0] : null;
      if (!dev) why = `its library device was not found (${lcsc ? `LCSC ${lcsc}, ` : ""}${named.length} library devices named "${name}")`;
    }
    if (dev) dev = (await projectCopy(dev)) || dev;
    sourceDevices.set(label, dev);
    if (!dev) templateLost.set(label, [why, []]);
    return dev;
  }
  async function deviceFor(part) {
    if (!part.lcsc) {
      const t = templates[part.prefix], spec = CFG.templateDefaults[part.prefix];
      if (!t && !spec) {
        errors.push(`${part.d}: no LCSC code, and no ${part.prefix} template part on the page to copy`);
        return undefined;
      }
      const label = t ? `template ${t.getState_Designator()}` : `library part ${spec.name || spec.lcsc}`;
      const dev = await sourceDevice(label, t ? {
        lcsc: String((t.getState_SupplierId && t.getState_SupplierId()) || "").trim(),
        name: String((t.getState_SubPartName && t.getState_SubPartName()) || "").replace(/\.\d+$/, ""),
        footprint: ((t.getState_Footprint && t.getState_Footprint()) || {}).name,
      } : spec);
      if (!dev) { templateLost.get(label)[1].push(part.d); return undefined; }
      fromTemplate.set(label, [...(fromTemplate.get(label) || []), part.d]);
      return dev;
    }
    if (!devices.has(part.lcsc)) {
      const lib = await tryCall(() => eda.lib_Device.getByLcscIds(part.lcsc));
      devices.set(part.lcsc, (await projectCopy(lib)) || lib);
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
    const byNum = new Map(), merged = new Map();
    for (const p of pins) if (!byNum.has(p.num)) byNum.set(p.num, p);
    // A symbol pin can stand for several pads, its number joining theirs: USB-C "B1A12" is pads
    // B1 and A12. Netlist rows for those pads all land on that pin, if they share one net.
    for (const p of pins) {
      const pads = p.num.match(/[A-Z]+\d+/g);
      if (pads && pads.length > 1 && pads.join("") === p.num) for (const pad of pads) if (!merged.has(pad)) merged.set(pad, p);
    }
    const netOf = new Map();   // symbol pin -> net it was given
    const used = new Set(), links = [], missing = [], byName = [];
    const later = [];   // mounting pads: matched last, to whatever symbol pins are left
    for (const [num, name, net] of part.pins) {
      if (MOUNT.test(num) || MOUNT.test(name)) { later.push([num, name, net]); continue; }
      const m = !byNum.has(num) && merged.get(num);
      if (m && (!used.has(m) || netOf.get(m) === net)) {
        if (!used.has(m)) { used.add(m); netOf.set(m, net); links.push({ cell: m.cell, num: m.num, name: m.name, net, pin: m }); }
        continue;
      }
      let p = byNum.get(num);
      if (!p || used.has(p)) {
        const names = [name, num, ...(ALIASES[name.toUpperCase()] || [])].map((s) => s.toUpperCase());
        const c = pins.filter((q) => !used.has(q) && (names.includes(q.name.toUpperCase()) || q.num === name));
        const oneNet = part.pins.filter((r) => r[1] === name).every((r) => r[2] === net);
        p = c.length === 1 || (c.length > 1 && oneNet) ? c[0] : undefined;
        if (p) byName.push(`${num} as symbol pin ${p.num}${p.name !== p.num ? ` (${p.name})` : ""}`);
      }
      if (!p) { missing.push(name && name !== num ? `${num} (${name})` : num); continue; }
      used.add(p);
      netOf.set(p, net);
      links.push({ cell: p.cell, num: p.num, name: p.name, net, pin: p });
    }
    // Mounting pads (MP1, SHELL, EP...) carry no name the symbol shares; when they are all on one
    // net, give them the symbol's leftover pins in order (which pad gets which pin then does not matter).
    if (later.length) {
      const spare = pins.filter((q) => !used.has(q));
      const oneNet = later.every((r) => r[2] === later[0][2]);
      if (oneNet && spare.length >= later.length) {
        later.forEach(([num, , net], i) => {
          const p = spare[i];
          used.add(p);
          links.push({ cell: p.cell, num: p.num, name: p.name, net, pin: p });
          byName.push(`${num} as symbol pin ${p.num}`);
        });
      } else for (const [num, name] of later) missing.push(name && name !== num ? `${num} (${name})` : num);
    }
    // Sub-parts of a multi-part symbol repeat shared pins (a dual op-amp's V+ and V- on both
    // halves). They are the same pad, so each copy gets the net its namesake was given; left
    // unwired, EasyEDA's DRC stops with "pins with the same number are connected to different
    // networks" (U103, 2026-11-17).
    const netByNum = new Map();
    for (const [p, n] of netOf) if (!netByNum.has(p.num)) netByNum.set(p.num, n);
    for (const p of pins) {
      if (used.has(p) || !netByNum.has(p.num)) continue;
      used.add(p);
      links.push({ cell: p.cell, num: p.num, name: p.name, net: netByNum.get(p.num), pin: p });
      byName.push(`${p.num} (${p.name}) on sub-part ${p.cell + 1} as a copy of pin ${p.num}`);
    }
    const extra = pins.filter((p) => !used.has(p)).map((p) => p.num);
    return { links, missing, extra, byName };
  }
  // Pin names that mean the same thing (netlist name -> names a library symbol may use instead).
  const ALIASES = { K: ["C", "CATHODE", "KA"], A: ["ANODE"], "+": ["POS", "PLUS", "VBAT", "BAT+"], "-": ["NEG", "MINUS", "GND", "BAT-"] };
  const MOUNT = /^(MP|MH|SH|SHELL|EP|PAD)\d*$/i;

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
  // Every part is staged left of the page first, so the layout can be planned from the real
  // symbol sizes. Each part gets its own spot so that no two staged pins touch.
  const STAGE = [-8000, 0];
  const stageSpot = (k) => [STAGE[0] + (k % 10) * 500, STAGE[1] + CFG.down * Math.floor(k / 10) * 1200];
  async function stagePart(part, spot) {
    const dev = await deviceFor(part);
    if (!dev) return undefined;
    const first = await call(`${part.d}: place`, () => sch.create(dev, spot[0], spot[1], undefined, 0, false, part.fit, true));
    if (!first) return undefined;
    const cells = [{ comp: first, pins: await pinsOf(first) }];
    let res = match(part, cells);
    // Multi-part symbols (e.g. a dual op-amp) are named NAME.1, NAME.2, ...: add parts until every pin
    // is found. EasyEDA places *something* for any sub-part name, so a new part that is not really
    // NAME.k, or that finds no missing pin, is removed again and the search stops.
    const m = String((first.getState_SubPartName && first.getState_SubPartName()) || "").match(/^(.*)\.(\d+)$/);
    for (let k = m ? Number(m[2]) + 1 : 0; m && res.missing.length && k <= 16; k++) {
      const c = await tryCall(() => sch.create(dev, spot[0] + 250 * cells.length, spot[1], `${m[1]}.${k}`, 0, false, part.fit, true));
      if (!c) break;
      const cp = await pinsOf(c);
      const next = match(part, [...cells, { comp: c, pins: cp }]);
      const real = String((c.getState_SubPartName && c.getState_SubPartName()) || "") === `${m[1]}.${k}`;
      const sig = (ps) => ps.map((p) => p.num).sort().join(",");
      const copy = cells.some((cell) => sig(cell.pins) === sig(cp));   // the same sub-part again
      if (!real || copy || next.missing.length >= res.missing.length) {
        await tryCall(() => sch.delete([c.getState_PrimitiveId()]));
        break;
      }
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
        try {
          p.obj.setState_NoConnected(true);
          if ((await within(p.obj.done())) === TIMEOUT) throw new Error(noAnswer);
          nNC++;
        }
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

  // ---- packing --------------------------------------------------------------
  // Skyline packing: each box (in order) goes to the highest free spot of a strip `width` wide,
  // so small boxes fill the space beside and under big ones instead of leaving it empty.
  // Works in "page" coordinates: x to the right, y down the screen, (0, 0) top left.
  function skyline(items, width) {
    width = Math.max(width, ...items.map((it) => it.w));
    let sky = [{ x: 0, w: width, y: 0 }];
    const pos = [];
    let W = 0, H = 0;
    for (const it of items) {
      let best = null;
      for (const s of sky) {
        if (s.x + it.w > width) break;
        const y = Math.max(...sky.filter((t) => t.x < s.x + it.w && t.x + t.w > s.x).map((t) => t.y));
        if (!best || y < best.y) best = { x: s.x, y };
      }
      pos.push(best);
      const x0 = best.x, x1 = best.x + it.w, next = [];
      for (const t of sky) {
        if (t.x + t.w <= x0 || t.x >= x1) { next.push(t); continue; }
        if (t.x < x0) next.push({ x: t.x, w: x0 - t.x, y: t.y });
        if (t.x + t.w > x1) next.push({ x: x1, w: t.x + t.w - x1, y: t.y });
      }
      next.push({ x: x0, w: it.w, y: best.y + it.h });
      next.sort((a, b) => a.x - b.x);
      sky = next.reduce((acc, t) => {   // merge neighbours at the same height
        const last = acc[acc.length - 1];
        if (last && last.y === t.y && last.x + last.w === t.x) last.w += t.w; else acc.push({ ...t });
        return acc;
      }, []);
      W = Math.max(W, x1);
      H = Math.max(H, best.y + it.h);
    }
    return { pos, w: W, h: H };
  }
  // Try strip widths between the widest box and all boxes side by side; keep the packing that
  // needs the smallest rectangle of the given aspect ratio (the smallest sheet, for the page).
  // Orders tried: the given one, tallest / widest / largest first, and for the page (few
  // blocks) a fixed set of shuffles. The given order wins unless another is clearly smaller,
  // so parts and blocks keep their netlist / guide order where that costs nothing.
  // A page packing is scored by the smallest A-series sheet it fits first: inside the border,
  // with no block over the title block in the bottom right corner.
  const mm = (v) => Math.round(v * 0.254), units = (v) => Math.round(v / 0.254);
  const tbU = CFG.titleBlock ? CFG.titleBlock.map(units) : null;
  const withTb = !page || page.titleBlock;   // keep clear of the title block unless the page hides it
  // Does a layout w x h (boxes at page coordinates) fit a frame fw x fh, inside the border?
  function fitsIn(fw, fh, w, h, boxes) {
    const W = fw - 2 * units(CFG.border), H = fh - 2 * units(CFG.border);
    if (w > W || h > H) return false;
    return !(withTb && tbU) || !boxes.some((b) => b.x + b.w > W - tbU[0] && b.y + b.h > H - tbU[1]);
  }
  const sheetFor = (w, h, boxes = []) => SHEETS.findIndex(([, W, H]) => fitsIn(units(W), units(H), w, h, boxes));
  function packBest(items, aspect, extraW = 0, extraH = 0, bySheet = false) {
    const minW = Math.max(...items.map((it) => it.w)), sumW = items.reduce((s, it) => s + it.w, 0);
    const given = items.map((_, i) => i);
    const by = (f) => [...given].sort((a, b) => f(items[b]) - f(items[a]) || a - b);
    const orders = [given, by((it) => it.h), by((it) => it.w), by((it) => it.w * it.h)];
    let seed = 12345;   // fixed seed: the same netlist always gives the same layout
    const rnd = () => ((seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648);
    for (let s = 0; bySheet && s < CFG.shuffles; s++) {
      const o = [...given];
      for (let i = o.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [o[i], o[j]] = [o[j], o[i]]; }
      orders.push(o);
    }
    const steps = bySheet ? 120 : 40;
    let best = null;
    for (const [n, order] of orders.entries()) {
      const handicap = n === 0 ? 1 : 1 + CFG.orderBonus;
      const its = order.map((i) => items[i]);
      for (let k = 0; k <= steps; k++) {
        const p = skyline(its, minW + ((sumW - minW) * k) / steps);
        const w = p.w + extraW, h = p.h + extraH;
        const fit = bySheet ? sheetFor(w, h, p.pos.map((q, j) => ({ x: q.x, y: q.y, w: its[j].w + extraW, h: its[j].h + extraH }))) : 0;
        const score = (bySheet ? (fit < 0 ? SHEETS.length : fit) * 1e9 : 0)
          + (Math.max(w / aspect, h) + 1e-6 * w * h) * handicap;
        if (!best || score < best.score) {
          const pos = [];
          order.forEach((i, j) => { pos[i] = p.pos[j]; });
          best = { pos, w: p.w, h: p.h, score };
        }
      }
    }
    return best;
  }

  // ---- stage every part, then plan the layout ------------------------------
  const plan = [];   // {heading, items: [{part, cell, i, links, box, w, h}]}
  let nStaged = 0;
  for (const [block, title] of BLOCKS) {
    const parts = PARTS.filter((p) => p.block === block && !present.has(p.d));
    if (!parts.length) continue;
    const heading = PARTS.some((p) => p.block === block && present.has(p.d)) ? `${title} (continued)` : title;
    toast(`Auris ${SHEET}: loading ${heading} (${parts.length} parts)`);
    const items = [];
    for (const part of parts) {
      const staged = await stagePart(part, stageSpot(nStaged++));
      if (!staged) continue;
      nParts++;
      for (const [i, cell] of staged.cells.entries()) {
        const box = cellBox(cell, staged.links.filter((l) => l.cell === i));
        items.push({ part, cell, i, links: staged.links, box, w: box.r - box.l, h: box.hi - box.lo });
      }
    }
    if (items.length) plan.push({ heading, items });
  }
  // Pack each block's parts, then the blocks themselves (with a gap around each).
  for (const b of plan) {
    const headW = b.heading.length * CFG.headingCharW + 2 * CFG.padX;
    b.pack = packBest(b.items, CFG.blockAspect, 0, CFG.titleH);
    b.w = snap(Math.max(b.pack.w, headW));
    b.h = snap(b.pack.h + CFG.titleH);
  }
  const g = CFG.blockGap;
  const sheet = plan.length ? packBest(plan.map((b) => ({ w: b.w + g, h: b.h + g })), CFG.pageAspect, -g, -g, true) : { pos: [], w: 0, h: 0 };
  // Which sheet to lay out on: the page's own if it is big enough, else the smallest that fits.
  const boxesOf = (pk) => pk.pos.map((q, n) => ({ x: q.x, y: q.y, w: plan[n].w, h: plan[n].h }));
  const lw = sheet.w - g, lh = sheet.h - g;
  const needed = plan.length ? sheetFor(lw, lh, boxesOf(sheet)) : -1;
  const pageFits = !!page && plan.length > 0 && fitsIn(page.w, page.h, lw, lh, boxesOf(sheet));
  const frameH = pageFits ? page.h : needed >= 0 ? units(SHEETS[needed][2]) : null;
  // Page coordinates (x right, y down the screen, from the top left inside the border) to EasyEDA
  // coordinates. Parts already on the page from an earlier run push the new ones below them.
  const left = units(CFG.border);
  const top = farthest !== null ? farthest + CFG.down * 800
    : frameH !== null ? -CFG.down * (frameH - units(CFG.border)) : 0;
  const ex = (x) => left + x, ey = (y) => top + CFG.down * y;

  // ---- move everything into place ------------------------------------------
  for (const [n, b] of plan.entries()) {
    const bx = sheet.pos[n].x, by = sheet.pos[n].y;
    toast(`Auris ${SHEET}: placing ${b.heading} (${b.items.length} symbols)`);
    for (const [k, it] of b.items.entries()) {
      const cx = bx + b.pack.pos[k].x, cy = by + CFG.titleH + b.pack.pos[k].y;   // cell box top left, page coordinates
      const edge = CFG.down < 0 ? it.box.hi : it.box.lo;   // the box edge that is on top on the screen
      await finishCell(it.part, it.cell, it.i, it.links, snap(ex(cx) - it.box.l), snap(ey(cy) - edge));
    }
    // Box the block with its heading inside the top edge, as the hardware guide shows it.
    // The box's top left corner is (bx, by) and it extends right and down the screen.
    await decor(() => eda.sch_PrimitiveRectangle.create(ex(bx), ey(by), b.w, b.h, 0, 0, null, "none", CFG.boxLine));
    await decor(() => eda.sch_PrimitiveText.create(ex(bx + CFG.padX), ey(by + CFG.headingY), b.heading, 0, null, null, CFG.headingSize, true));
  }
  const layoutW = mm(Math.max(0, sheet.w - g)), layoutH = mm(Math.max(0, sheet.h - g));
  const named = (w, h) => (SHEETS.find(([, W, H]) => Math.abs(mm(w) - W) <= 2 && Math.abs(mm(h) - H) <= 2) || [])[0];
  const pageName = page ? named(page.w, page.h) || `${mm(page.w)} x ${mm(page.h)} mm` : "unknown";
  const smaller = needed >= 0 && page && units(SHEETS[needed][1]) * units(SHEETS[needed][2]) < page.w * page.h * 0.9;
  const sheetNote = !plan.length ? ""
    : farthest !== null ? `Layout: ${layoutW} x ${layoutH} mm, placed below the parts already on the page.`
    : pageFits ? `Layout: ${layoutW} x ${layoutH} mm, placed inside the page's ${pageName} frame.`
      + (smaller ? ` It would also fit ${SHEETS[needed][0]}: set that size before running to get it there.` : "")
    : needed < 0 ? `Layout: ${layoutW} x ${layoutH} mm, too big for A0: placed below the page frame.`
    : `Layout: ${layoutW} x ${layoutH} mm, placed for an ${SHEETS[needed][0]} frame. Set the page Size to ${SHEETS[needed][0]} (page properties; now ${pageName}) and it sits inside.`;

  // ---- report ---------------------------------------------------------------
  for (const [label, [why, ds]] of templateLost) errors.unshift(`${label[0].toUpperCase() + label.slice(1)}: ${why}, so not placed: ${ds.join(", ")}`);
  for (const [code, ds] of notFound) errors.unshift(`${code} not found in the EasyEDA library, not placed: ${ds.join(", ")}`);
  if (decorError) warnings.push(`Some block boxes or headings were not drawn: ${decorError}`);
  for (const [label, ds] of fromTemplate) {
    const td = label.startsWith("template ") ? label.slice(9) : null;
    warnings.push(`${ds.join(", ")}: placed as ${label}, so check value and footprint.${td ? ` Delete ${td} when done.` : ""}`);
  }
  const head = [`${SHEET} sheet: placed ${nParts} parts (${nCells} symbols), ${nWires} net wires, ${nNC} no-connect flags.`];
  if (present.size) head.push(`Skipped ${present.size} parts already on the page.`);
  if (sheetNote) head.push(sheetNote);
  const show = (title, list, max) =>
    list.length ? ["", `${title} (${list.length}):`, ...list.slice(0, max), ...(list.length > max ? [`...and ${list.length - max} more in the browser console`] : [])] : [];
  const report = [...head, ...show("Errors", errors, 25), ...show("Warnings", warnings, 10)].join("\n");
  log([...head, ...show("Errors", errors, 1e9), ...show("Warnings", warnings, 1e9)].join("\n"));
  showDialog(report, `Auris capture: ${SHEET}`) || toast(head[0]);
})().catch((e) => {
  const m = `Auris capture stopped: ${(e && e.stack) || e}`;
  console.error(m);
  showDialog(m, "Auris capture");
});

// EasyEDA Pro 3.2 has both sys_Dialog and sys_MessageBox; use whichever works.
function showDialog(text, title) {
  for (const box of [eda.sys_Dialog, eda.sys_MessageBox]) {
    try { if (box && typeof box.showInformationMessage === "function") { box.showInformationMessage(text, title); return true; } }
    catch (_) { /* try the next one */ }
  }
  return false;
}
