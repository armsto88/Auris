# Handover: Auris schematic deep-dive review and BOM cost pass

> **Done and superseded.** This handover was carried out on 2026-11-17 (`2026-11-17-schematic-review.md`). Several facts below are out of date (EasyEDA 3.2, the EG800K-EU and N16R8 parts). The next step is [`handover-second-review-and-freeze.md`](handover-second-review-and-freeze.md).

Written 2026-11-17 for the next Claude Code session. Repo `/home/tom/Auris`, branch `hardware-specs-and-easyeda`, last commit `ea00321`.

Auris is a solar-powered acoustic recorder for long-term biodiversity surveys. It has an ESP32-S3, a PCM186x audio ADC, a Quectel EG800K-EU LTE modem, microSD storage and a DS3231M RTC wake, and it is deployed in **Europe and Australia**. Nothing has been built or measured yet.

All four schematic sheets were just captured into EasyEDA Pro by script. Your job is to:
- review whether the schematic does what the hardware is meant to do;
- check every part's wiring against its datasheet;
- store part data so it is easy to find later;
- cut BOM cost without losing function or quality.

Fix what you find; don't just list it.

## Deliverables

1. **Part data index** in `hardware/datasheets/` (see *Part data*). Build it first, because the rest of the review uses it.
2. **Review report** at `hardware/review/<date>-schematic-review.md`.
   - Order: findings on the whole design first, then one section per sheet.
   - Each finding gives:
     - severity (blocker / must fix / should fix / note);
     - sheet, designator and pin;
     - what is wrong;
     - the evidence: datasheet document number, revision and page/table/figure;
     - the fix;
     - status: fixed / needs owner decision / open.
3. **Fixes:** apply them in the source CSVs, rebuild the generated files and re-capture the affected EasyEDA pages.
4. **BOM cost pass:** apply the changes and log them in `hardware/review/<date>-bom-cost-changes.csv`.
   - Log columns:
     - designators;
     - old and new MPN and LCSC code;
     - unit price at 10 and 100, before and after;
     - JLC basic/extended, before and after;
     - spec comparison;
     - reason.
   - Update `docs/05-BOM-AND-COSTS.md` and `specs/` to match.
   - Report the whole-BOM cost before and after at 10 and 100 units, including JLC extended-part fees.
5. **Export** the final project to `hardware/<date>/` with `hardware/tools/easyeda_export.js`.
   - Commit in logical steps on this branch.
   - Push only when the user asks.

## Sources of truth

**The schematic is generated, so make every design change in the CSVs and the sheet README rationale, never by hand in EasyEDA.**

- **Sheets:** each of `hardware/{audio-frontend,power,lte,mcu}/` has two CSVs:
  - `*-netlist.csv` with columns `designator,pin,pin_name,net,fit,notes`;
  - `*-bom.csv` with columns `designators,qty,value,description,package,suggested_mpn,lcsc,fit,notes`.

  Each sheet's `README.md` holds:
  - the design rationale and calculations;
  - which datasheets (with revisions) were already checked.

  For example, `power/README.md` says the CN3791, HT7533 and TPL720F33 values follow FieldMesh notes and were **not** re-checked against their datasheets.
- **After any CSV change:**
  1. `python3 hardware/tools/build_guide.py`
     - rebuilds `hardware/auris-hardware-guide.html`;
     - checks netlist/BOM agreement, unique designators, sheet-port tables and the ADC pin map;
     - stops on an error.

     Block grouping lives in its `BLOCKS` table; for the MCU sheet it is `EXTRA_BLOCKS` in `easyeda_capture.py`.
  2. `python3 hardware/tools/easyeda_capture.py [--sheet power]` regenerates `hardware/easyeda/capture-<sheet>.js`.
- **Intent and requirements** (read them first):
  - `docs/00-SOURCE-OF-TRUTH.md` (precedence and status words)
  - `docs/19-V1-FUNCTIONAL-REQUIREMENTS.md` (energy budget, F-requirements)
  - `docs/04-HARDWARE-V1.md`, `docs/06-FIRMWARE-AND-POWER.md`, `docs/07-AUDIO-AND-CALIBRATION.md`, `docs/11-CONNECTIVITY-AND-SECURITY.md`
  - `docs/20-FIELDMESH-POWER-AND-MODEM-REVIEW.md`
  - `docs/14-DECISION-REGISTER.md` (ADRs), `docs/15-RISKS-AND-OPEN-QUESTIONS.md`, `docs/16-REQUIREMENTS-TRACEABILITY.md`, `docs/05-BOM-AND-COSTS.md`
  - `specs/lcsc-orderable-2026-10-23.csv` (orderable codes, with a `jlc_library` column)
  - `references/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf`
- **EasyEDA project "AURIS":** already open in the user's Chrome; the tab title starts `AURIS |`.
  - Schematic1 has pages 1 LTE, 2 POWER, 3 AUDIO and 4 MCU. PCB1 is empty.
  - Your backup is the last export, `hardware/2026-11-17/AURIS_2026-11-17.epro2`.
  - Ignore `ProPrj_AURIS_2026-11-17.epro2` in the repo root; it is the old design from before the re-capture.
- **Memory:** the `auris-easyeda-capture` and `deployment-regions` memories load automatically and hold the same facts in short form.

## Owner decisions: propose, don't swap

The owner selected these:

| Part or choice | ADR |
|---|---|
| ESP32-S3-WROOM-1-N16R8 | ADR-001 |
| DS3231MZ+TRL | ADR-002 |
| FieldMesh wake latch | ADR-003 |
| EG800K-EU | ADR-006 |
| CN3791 + TMP390A2 charger | ADR-007 |
| TPS63802 | ADR-008 |
| TPL720F33 + CR1220 | ADR-010 |
| TPS63020 modem rail at 3.9 V | ADR-011 |
| 1-bit SD on GPIO47/48/44 | ADR-012 |
| ADC battery divider | ADR-027 |

- **Wiring or value errors in these blocks:** fix them.
- **Replacing one of these parts or changing its topology:** that is a proposal to the user, with evidence.
- **Candidates you may change in the cost pass** if the replacement is equivalent in spec (note it in the log):
  - PCM1863DBTR, TPS7A2033, OPA1662;
  - the microphone connector;
  - the SD and SIM holders and other connectors;
  - all passives and discretes.

## Browser access (Claude in Chrome)

**Loading the tools:** use one ToolSearch call:
`select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__javascript_tool,mcp__claude-in-chrome__find,mcp__claude-in-chrome__file_upload`
Then call `tabs_context_mcp`. If there is no EasyEDA tab, or the extension isn't connected, ask the user.

**Don't pull Chrome to the front.** The user works in other windows while you run.
- Screenshots and clicks (the `computer` tool) bring Chrome forward. `javascript_tool`, `find` and `file_upload` do not, so use only those.
- If you really need a real click (the page Size dropdown, Design > Update PCB), ask first and do all of them in one session.

### Running EasyEDA scripts without clicks

1. **Inject the driver:** read `hardware/tools/easyeda_page_driver.js` and pass its full text to `javascript_tool`. Re-inject it even if `window.__aurisRun` exists: the copy in the tab now is older and lacks `__aurisStart`.
2. **Load a script:** `find` "Auris script loader" to get the hidden file input, then `file_upload` your `.js` to it. Paths in the repo and in your scratchpad both work. The text lands in `window.__aurisFiles[name]`.
3. **Run it:**
   - Short runs: `await __aurisRun(__aurisFiles[name], {titleRe: /^Auris probe/, timeoutMs: 40000})`.
   - Anything that may take over ~40 s: `__aurisStart(name, {titleRe, timeoutMs})`, then poll `window.__aurisJobResult` in calls of at most 38 s. The Chrome connection gives up at 45 s; a whole-sheet capture takes 1–3 minutes.
   - Only one Run Script at a time.
4. **Read results:**
   - Scripts report with `eda.sys_MessageBox.showInformationMessage(text, "Auris …")`, and the title must match `titleRe`.
   - Keep long results on `window`.
   - Read them back in slices under ~1000 characters after replacing `= & ?`; the tool blocks output that looks like a query string.
5. **Pages:**
   - open: `eda.dmt_EditorControl.openDocument(pageUuid)`;
   - current page: `eda.dmt_Schematic.getCurrentSchematicPageInfo()`;
   - new page: `eda.dmt_Schematic.createSchematicPage(schematicUuid)`;
   - save: `eda.sch_Document.save()`;
   - rename: the API returns false, so use `__aurisRenamePage(from, to)`.

### EasyEDA API facts (Pro 3.2.209)

- **Coordinates:** y grows **up**; units are 10 mil.
- **Page frame:** a component of type `"sheet"` at (0,0), its bottom-left corner. Its real size is in OtherProperty `Width`/`Height`:
  - A4: 1170×825
  - A3: 1655×1170
  - A2: 2338×1652

  "Page Size" stays "A4" whatever the real size. The frame can't be modified by API, and the Size dropdown ignores synthetic events.
- **Placing parts:** resolve the device by LCSC code (`lib_Device.getByLcscIds`) or by an exact `lib_Device.search` name. `getState_Component()` of a placed part is not a library reference; `create()` with it hangs.
- **Device update prompt:** EasyEDA sometimes asks "device have been updated" during create. The driver answers **Place**, which keeps the project's library version.
- **Network:** scripts can't open network connections (EasyEDA's external-interaction permission is off).

### Re-capturing a page

Re-capturing deletes the page's contents. Before the first one:
- export a backup with `easyeda_export.js`;
- tell the user which pages you're about to re-capture.

Steps:
1. Open the page.
2. Copy `hardware/tools/easyeda_clear_page.js` to your scratchpad, set `EXPECT` to the page name and run it. It refuses on any other page.
3. Run `capture-<sheet>.js` with `__aurisStart`.
4. Check the report: parts placed against the BOM, unwired pins, NC flags and the sheet size it asks for.
5. Save the page.

The LTE page was captured with an older script version and still has the template parts C1/TP1 in its SIM block. A re-capture with the current script removes them (test pads now come from the library part "Test-Point").

### Checking connectivity

The capture gives every pin a wire stub with a net label, so the drawing's connectivity is the CSV netlist, except for pins the report lists as unwired. Correctness therefore rests on three things:
- (a) each CSV row's pin number and function match the datasheet;
- (b) the EasyEDA symbol's pin numbers map to the right footprint pads for that package;
- (c) the nets chosen are right for the circuit.

Ways to read what EasyEDA actually has:
- **Read-only probes:** `sch_PrimitiveComponent.getAll()` plus `getAllPinsByPrimitiveId(id)` (pin number, name, NC flag) and `sch_PrimitiveWire.getAll()`.
- **Netlist export doesn't work:** `sch_ManufactureData.getNetlistFile()` returned nothing for 14 format names, and `sch_Netlist.getNetlist()` throws "i is not iterable". Don't sink time into these.
  - Untested leads: `sch_SourceNet.getConnections` and `sch_SourceNetlist.getNetlistInRegion`.
- **Strongest check:** `python3 hardware/tools/easyeda_check.py <export.epro2>`, which compares PCB pad nets against the CSVs. It needs Design > Update PCB first, a UI step: ask the user to do it or for permission to click it once. Then export the project.
- **Pictures without screenshots:** `sch_ManufactureData.getPngFile` / `getSvgFile` exist but are untested. Save the result with `sys_FileSystem.saveFile` (it lands in `~/Downloads`), then Read the image.
- **BOM export works:** `sch_ManufactureData.getBomFile(name, "csv")` gives the whole project, with LCSC/JLCPCB stock and price columns. `easyeda_export.js` saves it.

## Part data (endpoints checked 2026-11-17)

There is no official, free datasheet API. These work from a plain script (curl with an ordinary browser User-Agent):

- **JLCPCB part detail:** `https://cart.jlcpcb.com/shoppingCart/smtGood/getComponentDetail?componentCode=C70381`
  - `data.dataManualUrl` is the LCSC datasheet PDF link.
  - `componentLibraryType`: `base` means basic, `expand` means extended.
  - `preferredComponentFlag`, `stockCount`, `prices`.
  - `attributes` is the parameter list, including operating temperature.
  - `describe`, `componentBrandEn`, `componentModelEn`.
- **JLCPCB search:** POST `https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList` with body `{"keyword":"C70381","currentPage":1,"pageSize":5}`.
  - It returns `data.componentPageInfo.list[]` with `componentLibraryType`, `preferredComponentFlag`, `stockCount`, `componentPrices` (price breaks) and `dataManualUrl`.
  - Keyword search by text (e.g. "100nF 0402 X7R 50V") to find basic-part alternatives is untested; check what comes back.
- **EasyEDA product:** `https://easyeda.com/api/products/C70381/components?version=6.4.19.5`
  - `result.dataStr.head.c_para` has the manufacturer, MPN, package and "JLCPCB Part Class".
  - `result.lcsc` has price and stock.
  - `result.packageDetail` is the footprint.
  - Symbol pins are the `result.dataStr.shape` entries starting `P~`: the pin number is the 4th `~` field, and the pin name is in a later `^^` segment.

  Use it to check symbol pin numbering. It is EasyEDA's standard library record; if in doubt, confirm with an editor probe of the placed part.
- **LCSC:** the `wmsc.lcsc.com` product endpoint returned an empty result. LCSC's datasheet PDF links send script requests to the homepage.
  - **Don't spoof headers or otherwise work around this**; a harness check blocked that.
  - Get PDFs from the manufacturer's own site instead (TI, ADI and Espressif PDF links normally work with curl).
  - Or get them through Chrome: from a tab on lcsc.com, `fetch` the PDF in `javascript_tool` and save it with an `<a download>`, which lands in `~/Downloads`. This is untested, and Chrome may ask once to allow multiple downloads.
- **Quectel EG800K** datasheet and hardware design guide need a Quectel login. Ask the user for the PDFs if you can't find them.
- **Reading PDFs:** `pdftotext -layout file.pdf -` (poppler is installed; pypdf is not). For specific pages, use the Read tool's `pages` option.

The user approves downloading datasheet PDFs for parts on the Auris BOMs from manufacturer sites, lcsc.com and jlcpcb.com into `hardware/datasheets/pdf/` without asking each time.

### Index layout

- **`hardware/tools/fetch_part_data.py`:** builds and refreshes the index from all four BOMs, because prices and stock move daily.
- **`hardware/datasheets/parts.csv`:** one row per LCSC code across all sheets, with columns:
  - `lcsc`, `mpn`, `manufacturer`, `package`;
  - `used_by` (sheet: designators);
  - `jlc_class` (basic / extended / preferred);
  - `stock`, `usd_1`, `usd_10`, `usd_100`;
  - `datasheet_url`, `datasheet_rev`;
  - `temp_min`, `temp_max`;
  - `checked` (date).
- **`hardware/datasheets/<LCSC>_<MPN>.md`:** one file for every IC, module, connector, FET, diode, crystal, inductor and polarised part. It holds:
  - a pin table: number, name, function, what the Auris netlist connects it to, OK or issue;
  - the absolute-maximum and recommended limits that matter for Auris;
  - required external parts and the datasheet's equations;
  - layout notes and gotchas;
  - page/table citations.

  Paraphrase: facts and tables, not copied prose.
- **`hardware/datasheets/pdf/`:** local cache only. Add it to `.gitignore` for vendor copyright and repo size.

Extracting datasheets part by part runs well in parallel with subagents. Keep the EasyEDA steps in one thread.

## Review method

### 1. The whole design first

Read the docs above, then check the design as a system before opening any page. Cover at least:

- **Power tree and energy**
  - every rail's source, enable default and sequencing;
  - what stays alive while "off" (RTC, keep-alive LDO, wake latch) and the sleep current against the F4 energy budget;
  - cold start from a flat battery with only the panel, and brown-out behaviour;
  - reverse polarity, surge and ESD at the panel, battery, USB, SIM, SD, mic and antenna connectors.
- **Charging:**
  - charger settings against the battery's spec (charge voltage, current, temperature window);
  - the MPPT divider;
  - the 0 °C / +42 °C cut-out.
- **Climate:** −40 °C European winter and Australian summer enclosure heat. Check each part's rated range from the JLC attributes. A known gap: the ESP32-S3 N16R8 is rated to +65 °C and the charger cuts out at +42 °C (doc 15, open question 11).
- **LTE**
  - supply:
    - the TPS63020 at 3.9 V against the modem's peak-current and ripple requirements;
    - bulk capacitance;
  - control:
    - power key, reset and status lines;
    - the modem's I/O voltage domain and level shifting to the ESP32-S3's 3.3 V I/O;
  - SIM: the circuit's ESD protection, series resistors and capacitors;
  - antenna and bands:
    - the antenna path and matching;
    - band coverage for Europe and Australia (B1/3/5/7/8/20/28);
    - GNSS is not used.
- **MCU pin budget across all sheets:**
  - every GPIO used once;
  - strapping pins GPIO0/3/45/46 safe at boot;
  - GPIO35–37 unused, because the N16R8's octal PSRAM uses them;
  - analogue inputs on ADC1 (ADC2 conflicts with Wi-Fi);
  - USB on GPIO19/20;
  - a boot, programming and recovery path.
- **Audio:**
  - mic bias, preamp gain and headroom;
  - PCM186x clocking and mode, I²S/I²C wiring;
  - LDO noise;
  - audio power gating;
  - analogue/digital grounding.
- **Storage:** SD power switch, pull-ups, card detect, 1-bit mode.
- **Cross-sheet nets** (sheet-port tables in `build_guide.py`):
  - the same signal has the same net name on every sheet;
  - voltage domains and directions agree;
  - no single-pin (orphan) nets;
  - power-net names are consistent.
- **Bring-up:**
  - test points on rails and key signals;
  - current-measurement points;
  - programming access.

### 2. Each page, part by part

**ICs, modules, connectors, FETs, diodes, crystals, inductors and polarised capacitors:** use the part index to check each against its datasheet:
- every pin's number, function and connection, and how unused pins are handled;
- required external parts, with values recomputed from the datasheet's equations;
- absolute-maximum limits against the real rail voltages, including transients;
- current and power ratings;
- enable, reset and default states;
- that the EasyEDA symbol maps to the footprint correctly (`audio-frontend/README.md` already asks for Q101/Q102's G/S/D order to be confirmed).

**Passives:** check:
- voltage rating, including MLCC DC-bias derating;
- dielectric where it matters (C0G or film in the audio and timing paths);
- resistor power and tolerance;
- divider accuracy.

### 3. BOM cost pass (same pass)

**Goal:** a lower cost at 10 and 100 units with no loss of function, performance, reliability or temperature range.

- **Assembly:** the BOMs carry LCSC codes, and `specs/` tracks JLC basic/extended, so assume JLCPCB assembly; confirm with the user if unsure.
  - JLC charges a per-order fee for each unique extended part. Check the current amount on jlcpcb.com, and whether "preferred extended" parts are exempt.
- **Levers, in order:**
  1. Move passives to JLC basic parts with equal or better specs.
  2. Merge near-identical values to cut the number of unique parts.
  3. Pick cheaper equivalents with the same spec, and deep stock, for discretes, connectors and holders.
  4. Remove parts that do nothing. Keep protection unless the threat it covers isn't real.
  5. Use `fit = N` (do not place) for optional variants.
- **Don't trade away:**
  - the −40 °C minimum and the high-temperature rating;
  - voltage and current margins;
  - audio noise performance (dielectric, resistor type);
  - RF parts;
  - protection at external connectors;
  - lifecycle (no NRND or EOL parts);
  - stock depth (no parts with a few hundred in stock unless they are already chosen).
- **Owner-decided parts:** propose only.
- **After a change:**
  - check that the footprint follows the part;
  - check that the capture resolves the new LCSC code.

### 4. Applying fixes

- **Clear-cut errors** (a wrong pin, missing decoupling, a value that contradicts the datasheet):
  1. Fix them in the CSVs.
  2. Re-run `build_guide.py` and `easyeda_capture.py`.
  3. Re-capture the affected pages.
- **Judgment calls and anything that touches owner decisions:** mark them "needs owner decision". Ask the user in one grouped list, not one at a time.

## Open items from the capture (resolve or report)

1. **BT201 and C127 are placed but unwired.** Their symbols number the pins 1/2 while the netlist uses +/−.
   - BT201 is the CR1220 holder, C70381.
   - C127 is the tantalum C7171; the BOM says "+ to VMID_PRE".

   Settle the polarity from the manufacturer datasheet and the footprint's polarity mark. Change the netlist pins to numbers, then re-capture. A third-party page claims CR1220-2 pin 1 is +; that is unverified.
2. **Pins with no netlist row:**
   - J301 pin 8 (SIM cover tabs; the BOM note says GND);
   - J401 shell pins 1–4 (USB-C);
   - J402 CD and pins 10–13 (microSD);
   - J101/J102 pins 5–6 (JST GH mounting pads).

   Recommend nets, and ask before changing them.
3. **Page sizes:** POWER and AUDIO need A2, MCU needs A3; LTE is already A3. Check whether the user has set them by reading the frame's Width/Height.
4. **Test-pad footprint:** all 40 test pads use the library part "Test-Point" with a 0.5 mm footprint, while the BOM says 1.0 mm.
5. **LTE templates:** C1/TP1 are still on the LTE page; a re-capture removes them.
6. **Supply risk:**
   - the EG800K-EU had 151 in stock at LCSC and 179 at JLC on 2026-10-23;
   - `lte/README.md` wants a second antenna that covers 700–2700 MHz.
7. **Australian heat:** see *Climate* above.

## Working with the user

- Give a one-line update between long steps.
- Ask before:
  - replacing an owner-selected part;
  - choosing nets for shells and tabs;
  - any real click in Chrome;
  - deleting anything beyond a page re-capture;
  - pushing.
- Commit with the attribution lines your harness gives you.
- Finish with a short summary:
  - blockers;
  - fixes made;
  - decisions needed;
  - BOM cost before and after.
