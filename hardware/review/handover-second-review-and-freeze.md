# Handover: independent second review and schematic freeze (rev A)

Written 2026-11-19 for whoever gives the second opinion: a fresh Claude Code session (a different model is welcome) or a hardware engineer. Repo `/home/tom/Auris`, branch `main`, baseline commit `e961891`.

Auris is a solar-powered acoustic recorder for long-term biodiversity surveys, deployed in **Europe and Australia** (−40 °C winters to sealed enclosures in Australian sun). Its main parts:
- an ESP32-S3-WROOM-1-N16R2 module;
- a PCM1863 audio ADC with an OPA1662 preamp;
- a Quectel EG810M-EU LTE Cat 1 modem;
- microSD storage;
- a DS3231M RTC that wakes a latched power switch;
- a CN3791 MPPT solar charger.

Nothing has been built or measured.

The schematic has had one full datasheet review (2026-11-17), a BOM cost pass and a round of owner decisions (2026-11-18). Before PCB placement starts, the owner wants:
1. **A second, independent opinion** on whether the schematic is right.
2. **A freeze:** the schematic locked as the rev A layout baseline, with a record of exactly what was frozen and a rule for any later change.

## The baseline you are reviewing

| Item | Value |
|---|---|
| Commit | `e961891` on `main` (merge of PR #4) |
| Source of truth | `hardware/{power,audio-frontend,lte,mcu}/*-netlist.csv` and `*-bom.csv` |
| EasyEDA export | `hardware/2026-11-19/AURIS_2026-11-19.epro2`, SHA-256 `0c3d5120c6e0349351924550476266dd6c95ae8c2e7429ac9dc985f170307350` |
| PCB net check | `python3 hardware/tools/easyeda_check.py hardware/2026-11-19/AURIS_2026-11-19.epro2` passes: audio 114, power 123, LTE 53, MCU 47 parts |
| BOM cost per board | $48.32 at 10 boards, $27.44 at 100 (JLC parts + Economic feeder fees; `bom_cost.py`) |
| EasyEDA project | `AURIS` in the owner's account (EasyEDA Pro 4.1.105, web) |

**Locked from now on.** Don't edit the sheet CSVs, the EasyEDA project or the generated files while you review. Findings go in your report; fixes are applied only after the owner has approved them, in one batch, as part of the freeze (phase 3).

## Deliverables

1. **Review report** at `hardware/review/<date>-second-review.md`.
   - Order: the whole design first, then one section per sheet, then placement readiness.
   - Each finding gives:
     - severity (blocker / must fix / should fix / note);
     - sheet, designator and pin;
     - what is wrong, and what goes wrong on the board because of it;
     - evidence: datasheet document number, revision and page/table/figure, or a calculation;
     - the proposed fix;
     - status (proposed / owner decision needed).
   - Close with a section that compares your findings with the first review's (phase 2).
2. **Freeze recommendation:** freeze as is, freeze after listed fixes, or don't freeze yet. Add one grouped list of the decisions the owner must make.
3. **After the owner approves (phase 3):** the applied fixes, the freeze record and the tag.

Commit on a branch, never on `main`. Push, open a PR or merge only when the owner asks.

## Phase 1: independent review

Form your own view first, so the second opinion isn't anchored on the first.

**Don't open yet:**
- `hardware/review/2026-11-17-schematic-review.md`;
- `2026-11-17-bom-cost-changes.csv`;
- `handover-schematic-review.md`;
- the *Check* column and the *Findings* sections of `hardware/datasheets/*.md`.

Read the datasheets themselves instead. The sheet READMEs are design intent and calculations; read them, even though they mention some review outcomes.

### Inputs

- **Requirements and intent:**
  - `docs/00-SOURCE-OF-TRUTH.md` (precedence and status words);
  - `docs/19-V1-FUNCTIONAL-REQUIREMENTS.md` (energy budget, F-requirements);
  - `docs/04-HARDWARE-V1.md`, `docs/06-FIRMWARE-AND-POWER.md`, `docs/07-AUDIO-AND-CALIBRATION.md`, `docs/11-CONNECTIVITY-AND-SECURITY.md`;
  - `docs/14-DECISION-REGISTER.md` (ADRs), `docs/15-RISKS-AND-OPEN-QUESTIONS.md`.
- **Each sheet:** `README.md` (rationale, calculations, bring-up tests, firmware rules), `*-netlist.csv` (`designator,pin,pin_name,net,fit,notes`) and `*-bom.csv` (`designators,qty,value,description,package,suggested_mpn,lcsc,fit,notes`).
- **Cross-sheet ports:** the `PORTS` / `POWER_PORTS` / `LTE_PORTS` tables in `hardware/tools/build_guide.py`.
- **Drawings:** `hardware/auris-hardware-guide.html` has the block drawings and wire lists (audio, power and LTE; the MCU sheet is CSV only).
- **Part data:**
  - `hardware/datasheets/parts.csv`: per LCSC code, the MPN, JLC class, stock, price, datasheet link and revision, and rated temperature;
  - `symbol-pins.csv`: the EasyEDA symbol's pin numbers and names, and its footprint pads;
  - `sources.csv`: the manufacturer datasheet link and revision.
- **Datasheet PDFs:** on this machine they're in `hardware/datasheets/pdf/`, which is git-ignored. `python3 hardware/tools/fetch_part_data.py --pdf` re-downloads what `sources.csv` lists. Read them with `pdftotext -layout file.pdf -`.

### Method

The capture gives every pin a short wire stub labelled with its CSV net, so the drawing's connectivity is the CSV netlist. Correctness therefore rests on three things:
- (a) each CSV row's pin number and function match the datasheet;
- (b) the EasyEDA symbol maps that pin to the right footprint pad;
- (c) the chosen nets and values are right for the circuit.

`easyeda_check.py` already proves the PCB pads carry the CSV nets. It does not prove (a), (c), or that a footprint is the right package.

### Scope

**The whole design:**
- **Power tree:**
  - every rail's source, enable default and sequencing;
  - what stays alive while "off" (keep-alive LDO, RTC, wake latch Q206–Q210) and the sleep current against the F4 energy budget;
  - cold start from a flat battery with only the panel;
  - brown-out behaviour;
  - the inrush when the main switch closes.
- **Wake and power hold:** every path that can turn the board on or keep it on, including the USB VBUS wake and possible back-feed into the latch through I/O pins, ESD arrays or pull-ups.
- **Charging:**
  - CN3791 settings against the battery's spec;
  - the MPPT divider and the panel class;
  - the TMP390 temperature window and what happens if its output opens.
- **Modem:**
  - the TPS63020 3.9 V rail against peak current and bulk capacitance;
  - PWRKEY, RESET, STATUS and the 1.8 V ↔ 3.3 V level shifting (TXS0108E, OE control);
  - SIM ESD;
  - the antenna path;
  - bands B1/3/5/7/8/20/28 for Europe and Australia.
- **MCU:**
  - every GPIO used once;
  - strapping pins GPIO0/3/45/46 at boot;
  - EN supervision (driven by the TPS63802 power-good);
  - USB;
  - analogue inputs on ADC1;
  - the boot, programming and recovery path.
- **Audio:**
  - mic bias and DC sensing;
  - preamp gain and headroom;
  - PCM1863 clocking, mode and I²S/I²C;
  - the audio LDO's noise and dropout;
  - the analogue switches and DNP options;
  - grounding.
- **Storage:** card supply switch, pull-ups, card detect, ESD, and back-feed through I/O while the card is unpowered.
- **Protection:** reverse polarity, surge and ESD at the panel, battery, USB, SIM, microSD, microphone and antenna connectors.
- **Climate:** every part's rated range against −40 °C and hot enclosures. Check the datasheet, not only the JLC attribute.
- **Cross-sheet nets:** one name per signal on every sheet, voltage domains and directions agree, no orphan nets.
- **Supply:** stock, lifecycle (NRND/EOL) and single-source risk for every fitted part.

**Each sheet, part by part:** for every IC, module, connector, FET, diode, crystal, inductor and polarised capacitor, check:
- pins and unused-pin handling;
- required external parts, recomputed from the datasheet's equations;
- absolute maximums against real rail voltages and transients;
- ratings, and enable/reset defaults;
- symbol-to-footprint pad mapping.

For passives, check voltage rating and MLCC DC-bias derating, dielectric in the audio and timing paths, power and tolerance.

**Placement readiness:** what layout needs from the schematic.
- Footprints that are right and final, including test pads and connectors.
- Parts whose land pattern differs from the manufacturer's.
- Polarity marks.
- Required stack-up (LTE asks for at least four layers).
- Antenna keep-outs and isolation between the ESP32 PCB antenna and the LTE antenna.
- High-current and sensitive nets that need layout notes.

## Phase 2: reconcile with the first review

Now read `hardware/review/2026-11-17-schematic-review.md` (including section 8, the 2026-11-18 decisions), the cost-change log and the *Findings* sections of the part notes.

In your report:
- list where you agree;
- list where you disagree, and why;
- list what the first review missed;
- check every finding it marks **fixed** against the CSVs, so the fix is really there;
- give your view on each item it leaves **open**.

Its main open items at the baseline:
- **Bench:**
  - W6: inrush with no soft start on Q210;
  - W7: modem start-up sag on VBAT_SW;
  - P18: MPPT start threshold;
  - the BR1220 coin cell at −40 °C.
- **Firmware:**
  - W5: an ESP32 reset powers the board off;
  - W16: low-battery floor for audio;
  - the RTC register rules;
  - the modem start-up sequence;
  - flash/PSRAM at 80 MHz.
- **Layout:**
  - A5: D101 land pattern;
  - F202 land pattern;
  - the EG810M-EU footprint's outer pads (0.1 mm wider than Quectel's drawing);
  - 1.0 mm test-pad footprints (the library part is 0.5 mm);
  - TMP390 placement (P16).
- **Parts:**
  - L7: consumer-grade SIM holder;
  - M9: microSD holder temperature;
  - LTE README open items 3–9: VBAT TVS not fitted (D205 is DNP), stack-up, SIM plan, RED/RCM compliance, firmware, footprint.
- **Reading:** Quectel's standard-firmware *EC800M & EG810M Series Hardware Design*. The 2026-11-18 pin comparison used the QuecOpen edition (`hardware/datasheets/pdf/Quectel_EG810M-EU_QuecOpen_QuecPython_HD_V1.0.pdf`).

## Phase 3: freeze (after the owner's go-ahead)

1. **Apply the approved fixes** in the CSVs and the sheet README rationale, then:
   1. `python3 hardware/tools/build_guide.py` (rebuilds the guide; stops on a netlist/BOM/port error);
   2. `python3 hardware/tools/easyeda_capture.py` (regenerates `hardware/easyeda/capture-<sheet>.js` and `tidy-<sheet>.js`);
   3. `python3 hardware/tools/fetch_part_data.py` if any part changed. Without flags it refreshes price and stock for every code. `--offline` rebuilds from the cache only and leaves out codes that aren't cached yet, so cache new codes first;
   4. `python3 hardware/tools/bom_cost.py` for the new cost, logged as rows in a new `hardware/review/<date>-bom-cost-changes.csv` with the same columns as the 2026-11-17 one.
2. **Update EasyEDA** the in-place way (see *EasyEDA*). Ask the owner to run Design > Update PCB. Export with `hardware/tools/easyeda_export.js` to `hardware/<date>/`, then run `easyeda_check.py` on the export. It must pass for all four sheets.
3. **Write the freeze record** `hardware/review/<date>-schematic-freeze.md`. It holds:
   - the frozen commit;
   - the export path and SHA-256, with the `easyeda_check.py` and `build_guide.py` output;
   - the BOM cost at 10 and 100;
   - every accepted open item, with where it gets closed (layout, bench or firmware) and by whom;
   - the change-control rule below.
4. **Mark the status.** Update the status lines in `docs/00`, `docs/04`, `docs/13`, the repo `README.md` and the guide's title block (`hardware/tools/guide_template.html`, then rebuild) to "schematic frozen for rev A layout".
5. **Tag:** add an annotated git tag `schematic-rev-a-freeze` on the merge commit, and push it only when the owner says so.

**Change control after the freeze:** every change to a sheet CSV after the tag needs:
- a row in `hardware/review/schematic-change-log.csv` with columns `date,id,sheets,designators,change,reason,evidence,owner_approval,check_result`;
- the owner's approval, before the change;
- the full loop: `build_guide.py`, capture or tidy, Update PCB, export, a passing `easyeda_check.py`.

Layout-only changes (placement, routing, footprint geometry with unchanged pads and nets) don't need an entry.

## Owner decisions: propose, don't swap

| Part or choice | Where decided |
|---|---|
| ESP32-S3-WROOM-1-N16R2 | ADR-001 (2026-11-18) |
| DS3231MZ+TRL | ADR-002 |
| FieldMesh wake latch | ADR-003 |
| Quectel EG810M-EU | ADR-006 (2026-11-18) |
| CN3791 + TMP390A2 charger, cold cut-out +5 °C | ADR-007, review 2026-11-17 |
| TPS63802 main 3.3 V | ADR-008 |
| TPL720F33 keep-alive, CR1220 holder, Panasonic BR1220 cell | ADR-010, 2026-11-18 |
| TPS63020 modem rail at 3.9 V, D205 not fitted | ADR-011, 2026-11-17 |
| 1-bit SD on GPIO47/48/44, card detect on GPIO3, D403 ESD | ADR-012, 2026-11-17/18 |
| ADC battery divider | ADR-027 |
| Shells and tabs to GND, −40…+85 °C switches, JST-PH clone J203 for rev A, test pads TP404–TP415 | review 2026-11-17/18 |

- **Wiring or value errors inside these blocks:** report them as findings with fixes.
- **Replacing one of these parts or changing its topology:** a proposal to the owner, with evidence.

## Tools and data access

- **Part data endpoints:** JLC part detail, JLC search and EasyEDA product records work from a script with an ordinary browser User-Agent. `fetch_part_data.py` uses them; its docstring and the first handover's *Part data* section give the URLs.
  - The easyeda.com product API returns 403 if called more than about once every 6 s.
- **LCSC:** don't spoof headers or otherwise work around LCSC's script blocking. Take PDFs from the manufacturer, or through a Chrome tab on lcsc.com:
  1. load `/datasheet/<C code>.pdf` in a same-origin iframe;
  2. read the `datasheet.lcsc.com/datasheet/pdf/<hash>.pdf` link from its DOM;
  3. `fetch` it and save it with an `<a download>` (it lands in `~/Downloads`).
- **Datasheet downloads:** as in the first review, downloading datasheet PDFs for parts on the Auris BOMs from manufacturer sites, lcsc.com and jlcpcb.com into `hardware/datasheets/pdf/` needs no separate approval.
- **Climate:** deployment is Europe and Australia. Check bands, approvals and temperature against both.

## EasyEDA (needed only to apply fixes)

The review itself needs only the repo and the export. Touch EasyEDA only in phase 3.

- **Project:** `AURIS` (uuid `3ba79283056140b08e7552182142ce8a`), EasyEDA Pro **4.1.105** in the owner's Chrome.
  - Schematic pages keep their UUIDs: LTE `2d21daf7f429afc5`, POWER `7c88c20ee21429e4`, AUDIO `8fc023e05bc32d4e`, MCU `8b98bad55a285bd7`. The PCB is `1171ec2ee0a2c106`.
  - Page sizes: POWER, AUDIO and LTE are A2; MCU is A3.
- **Browser rules (Claude in Chrome):**
  - Use only `javascript_tool`, `find` and `file_upload`. Screenshots and clicks pull Chrome to the front, and the owner works in other windows.
  - Ask before any real click. Design > Update PCB is a real click; the owner usually does it.
  - The session's tab group may need recreating; ask the owner to move the EasyEDA tab into it, or open `https://pro.easyeda.com/editor` in it.
- **Running scripts:** `hardware/tools/easyeda_page_driver.js` explains how to run EasyEDA scripts from page JavaScript:
  - the "Auris script loader" file input;
  - `__aurisRun` for short runs;
  - `__aurisStart` plus polling for long ones.
- **Fresh tab:**
  1. Create the hidden file input with the few lines at the top of the driver.
  2. Upload the driver to it, then run it with `new Function(window.__aurisFiles['easyeda_page_driver.js'])()`.
  3. Watch EasyEDA's warnings as `messager-panel` DOM nodes with a MutationObserver.
- **Never clear and re-capture a whole page in 4.1.** On 2026-11-18 it broke the old project: some library devices can't be placed, and some project copies have no footprint. Make changes in place:
  1. To replace a part, run `hardware/tools/easyeda_remove_part.js` (set PAGE, TARGET, EXPECTED). It deletes one part and its stubs after checking the stub count.
  2. Run `capture-<sheet>.js`. It places only the parts missing from the page and wires them; it reports any part placed without a footprint.
  3. Run `tidy-<sheet>.js` to lay the page out again. It deletes all wires, boxes and headings, moves every part, then draws the stubs from the netlist.
  4. Save the page. Verify by dumping each pin's net from the page and comparing it with the CSV, then run Update PCB, export and `easyeda_check.py`.
- **What doesn't work by script:**
  - project rename and delete (`dmt_Project` returns false; the owner's account pages need a sign-in);
  - the page Size dropdown;
  - netlist export.

## Working with the owner

- Give a one-line update between long steps.
- Ask in one grouped list, not one question at a time.
- Ask before:
  - replacing an owner-selected part;
  - any real click in Chrome;
  - deleting anything in EasyEDA;
  - pushing, opening a PR, merging, or pushing the tag.
- Commit with the attribution lines your harness gives you.
- Finish with:
  - blockers;
  - disagreements with the first review;
  - fixes proposed;
  - decisions needed;
  - the freeze recommendation.
