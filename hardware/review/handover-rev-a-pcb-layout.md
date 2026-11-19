# Handover: rev A PCB layout

Written 2026-11-19 for whoever lays out the rev A board: a fresh Claude Code session, or a layout engineer working with one. Repo `/home/tom/Auris`, branch `main`, the schematic is frozen at tag **`schematic-rev-a-freeze`** (merge commit `c866a2f`, PR #5).

Auris is a solar-powered acoustic recorder for long-term biodiversity surveys, deployed in **Europe and Australia** (−40 °C winters to sealed enclosures in Australian sun). The board carries:
- an ESP32-S3-WROOM-1-N16R2 module (PCB antenna);
- a PCM1863 audio ADC with an OPA1662 preamp and an electret mic on a cable;
- a Quectel EG810M-EU LTE Cat 1 module (LGA-109) with a U.FL to an off-board FPC antenna;
- microSD, a DS3231M RTC and wake latch, a CN3791 MPPT solar charger, two buck-boost converters (TPS63802 3.3 V, TPS63020 3.9 V for the modem).

Nothing has been built or measured.

## Where things stand

| Item | State |
|---|---|
| Schematic | Frozen. Record and accepted open items: `hardware/review/2026-11-19-schematic-freeze.md` |
| Source of truth | `hardware/{power,audio-frontend,lte,mcu}/*-netlist.csv` and `*-bom.csv` (346 parts on the PCB: audio 115, power 130, LTE 53, MCU 48) |
| EasyEDA project | `AURIS`, uuid `3ba79283056140b08e7552182142ce8a`, EasyEDA Pro 4.1.105 (web) in the owner's Chrome. Schematic pages: LTE `2d21daf7f429afc5`, POWER `7c88c20ee21429e4`, AUDIO `8fc023e05bc32d4e`, MCU `8b98bad55a285bd7`. **PCB `1171ec2ee0a2c106`** |
| PCB | Update PCB run on 2026-11-19 and saved. All 346 footprints are on it, wherever Update PCB dropped them; **no board outline decided, no tracks, no vias; still EasyEDA's default 2-layer stack**. The DRC's "connection errors" are the unrouted ratsnest |
| Latest export | `hardware/2026-11-19/AURIS_2026-11-19_freeze.epro2` (SHA-256 `ba1b68c0…f52e`); `easyeda_check.py` passes on all four sheets |
| Reviews | `hardware/review/2026-11-17-schematic-review.md`, `hardware/review/2026-11-19-second-review.md` (section 7 is placement readiness) |
| BOM | $48.98/board at 10, $27.76 at 100 (`bom_cost.py`). Owner still to buy EG810M-EU and PCM1863DBTR prototype stock |

## Rules that apply to this work

- **Schematic change control.** Any change to a sheet CSV needs a row in `hardware/review/schematic-change-log.csv`, the owner's approval first, and the full loop (`build_guide.py`, capture or tidy, Update PCB, export, a passing `easyeda_check.py`). Layout-only changes need no entry: placement, routing, and footprint geometry with unchanged pad numbers and nets. If layout shows that a part, value or net must change, stop and propose it.
- **Git.** Work on a branch, never on `main`. Commit with the attribution lines your harness gives you. Push, open a PR, merge or push tags only when the owner asks.
- **Browser (Claude in Chrome).** Use only `javascript_tool`, `find` and `file_upload`: screenshots and clicks pull Chrome to the front while the owner works in other windows. Ask before any real click. Design > Update PCB is a real click; the owner does it. Never delete pages, projects or parts in EasyEDA without asking.
- **Owner.** Give a one-line update between long steps. Ask in one grouped list, not one question at a time.

## Phase 0 — inputs from the owner, and an API probe

**Ask the owner first, as one list:**
1. Board outline and size, or the enclosure and its usable internal area. The enclosure is still open (ADR-020, `docs/14`); a provisional outline (for example about 100 × 70 mm) is acceptable if the owner wants to start before it is chosen.
2. Which edge each external item goes to: panel inputs J201/J202, battery lead J203, mic J101, USB-C J401, microSD J402 (must be swappable through a sealed port without opening the main seal, F5-06), status LED401 (behind a light pipe, F5-05), buttons SW201/SW202, LTE antenna cable J302.
3. Mounting holes: number, size, positions.
4. Top-side parts only, or both sides (JLC assembly is cheaper and simpler with top only).

**Then probe EasyEDA's PCB scripting, read-only, before changing anything.** Report which calls work in 4.1.105:
- list and move components (`eda.pcb_PrimitiveComponent` getAll/modify: x, y, rotation, layer);
- set the copper-layer count and stack-up (`eda.pcb_Layer`);
- create the board outline;
- read and set design rules and net classes;
- create tracks, vias and pours;
- run DRC and read its results.

Use the schematic tooling as the model for this (see *EasyEDA access* below). Expect surprises: 4.1 already needed two workarounds.

## Phase 1 — board setup

- **Stack-up:** 4 layers (Quectel minimum; LTE README open item 4). Pick a JLC standard 4-layer impedance stack-up (1.6 mm), confirm its layer thicknesses on JLC's site, and record them. Suggested use: L1 signals and parts, L2 solid GND, L3 power pours / slow signals, L4 signals. Solid GND under U301, and **nothing on layer 1 under the module** (Quectel).
- **Net classes and rules:**
  - RF: ANT_MAIN/ANT_FEED as 50 Ω coplanar waveguide over L2 (calculate with JLC's impedance calculator for the chosen stack-up);
  - USB: ESP_USB_DP/DN and USB_DP/DN as a 90 Ω differential pair; the modem's M_USB_DP/DM run only to test pads TP309/TP310;
  - Power: the battery path J203 → F202 → Q205 → RAW_BAT → Q210 → VBAT_SW → U207 → VMODEM → R301 → U301 carries peaks of ≈ 3 A (size for that); SOLAR_IN/charger path ≈ 0.6 A; 3V3 up to ≈ 1 A peaks.
  - Clearances to JLC's standard capability.

## Phase 2 — footprint fixes (layout-only)

From the freeze record and second review section 7. Make project footprints; keep pad numbers so nets stay unchanged:

| Part | Fix | Reference |
|---|---|---|
| U301 (`LGA-109_…_EG810M-CN`) | 48 outer-ring pads to 1.0 × 0.6 mm (now 1.0 × 0.7); inner rings 1.0 × 0.7 and centre 1.3 × 1.3 are right | Quectel EG810M-EU QuecOpen&QuecPython HD V1.0 Fig. 40, p.67 (`hardware/datasheets/pdf/`) |
| D101, D402 (`X1SON-2…P0.65`) | TI DPY0002A land: 0.3 × 0.5 mm at 0.7 mm centres (library: 0.6 × 0.6 at 1.0) | TI SLLSEB1G pp.19–20 |
| F201 (`R1812`), F202 (`F1812`) | Littelfuse 1812L pad layout (1.78 × 3.15 mm, 3.45 mm gap) | Littelfuse 1812L series, rev 07/21/17, p.5 |
| C207 (`CAP-SMD_BD4.0…`) | Pad gap ≥ 1.0 mm (now 0.52 mm under the can) | Panasonic FP-V size B |
| All 54 test pads | 1.0 mm pad (library 0.5 mm); TP401–TP403 and TP413–TP415 in one 2.54 mm pogo row | MCU README |
| J401 USB-C | Shell slots per the HCTL drawing (pads 3/4 slot 1.40 mm, copper 1.80; pads 1/2 ≈ 0.1 mm off) | `hardware/datasheets/pdf/C2894897_HC-TYPE-C-16P-01A.pdf` |

Re-run `easyeda_check.py` on an export afterwards: it must still pass.

## Phase 3 — placement

Place block by block. Each block's parts are in `BLOCKS` in `hardware/tools/build_guide.py` (audio and power) and `EXTRA_BLOCKS` in `hardware/tools/easyeda_capture.py` (MCU). The LTE blocks are `l_*` in `BLOCKS`.

**Rules:**
- **Decoupling:** each cap at its pin, on the same layer, no via between cap and pin. The netlist notes say which cap belongs where ("At U102 pin 8", "at U207 VINA", ...).
- **Switching loops tight:**
  - U206 + L202 + C222/C224/C225;
  - U207 + L203 + C228/C229/C230–C232, with thermal vias under U207's exposed pad;
  - the charger loop C203–Q202–D203/D204–L201;
  - R202 Kelvin-routed to U201 pins 7/8;
  - D203/D204 with ≈ 1 cm² cathode copper.
- **Separation:**
  - the audio front end (U101–U104, Y101, J101, mic bias) away from U206/U207/U201, the SD bus, I²S and the LTE feed;
  - follow the audio README's *Layout rules* (`hardware/audio-frontend/README.md`): PCM1863 analog pins facing the mic, crystal guard ring, ADC input pairs coupled with ground, room for a shield can.
- **RF:**
  - U301 with ≥ 3 mm clearance to other parts (Quectel Fig. 40 note);
  - R310/C314/C315 next to J302;
  - the ESP32-S3 module at a board edge with Espressif's antenna keep-out (no copper under or beside the antenna; Espressif ESP32-S3 hardware design guidelines, `hardware/datasheets/pdf/esp32-s3_hw_design.pdf`, and the WROOM-1 datasheet v1.8), as far as possible from the LTE antenna (Quectel asks ≥ 20 dB isolation; LTE B7 uplink is 2.50–2.57 GHz, next to 2.4 GHz Wi-Fi).
- **Thermal and sensing:**
  - U203 (TMP390) at the board edge nearest the battery pack, away from the charger and converters: it stands in for the cell temperature;
  - keep U203's SET pins short and coat them.
- **Mechanical:** connectors and openings per the owner's answers; polarity silkscreen on J201/J202, ON/SHIP on SW202 (meter the first board), SW202 locator holes as non-plated holes.
- **Conformal-coating areas:** TMP390 SET pins and mic input. The wake latch no longer has 1 MΩ nodes.

**Verify each placement pass yourself:** export, then parse the `.epro2` locally. `read_epru()` in `hardware/tools/easyeda_check.py` reads it. Footprint `PAD` records are in mils (× 0.0254 = mm). PCB `COMPONENT` records carry `ATTR` rows for Designator, Footprint and position. Check:
- courtyard/pad overlaps;
- cap-to-pin distances;
- clearances around U301 and the ESP32 antenna;
- that every part is inside the outline.

Render a PNG of the placement (matplotlib or PIL) for the owner to look at. That is the review loop, since screenshots of the live editor are off-limits.

## Phase 4 — routing and DRC

- **Claude can do by script (once the probe confirms the calls):** GND and power pours, stitching vias, fan-out, slow digital nets (I²C, UART, enables, test pads), the USB pair and the 50 Ω RF track geometry from the calculated widths.
- **Owner or a layout engineer should route, or at least review in the editor:** the RF feed U301 → J302, the TPS63802/TPS63020/CN3791 switching loops, the battery high-current path, and the analog audio (mic input, ADC pairs, VREF, crystal).
- Run DRC to zero errors, export, run `easyeda_check.py` (must pass), commit.

## Phase 5 — fabrication outputs

Gerbers, BOM and pick-and-place for JLC from EasyEDA. Check:
- DNP parts are excluded from assembly;
- every fitted line's stock at JLC (re-run `python3 hardware/tools/fetch_part_data.py` and `bom_cost.py` the day of ordering);
- rotations in the pick-and-place preview for polarised parts and U301/U401.

The owner places the order.

## EasyEDA access (from the schematic sessions)

- **Driver:** `hardware/tools/easyeda_page_driver.js` explains running EasyEDA scripts from page JavaScript.
  - Fresh tab: create the hidden "Auris script loader" file input (the first lines of the driver), `file_upload` scripts to it, run the driver with `new Function(window.__aurisFiles['easyeda_page_driver.js'])()`.
  - Then `__aurisRun` for short scripts, `__aurisStart` plus polling `__aurisJobResult` for long ones (a browser call times out after ≈ 45 s).
  - Watch EasyEDA's toasts (`messager-panel` DOM nodes) with a MutationObserver.
- **Opening the project:** `tabs_context_mcp` with createIfEmpty, navigate the new tab to `https://pro.easyeda.com/editor`, then a synthetic double-click (DOM events) on the `AURIS` item inside `.tree-content_*`. Inside scripts, `eda.dmt_EditorControl.openDocument(uuid)` switches documents.
- **"Opened in another browser tab":** if the owner has AURIS open elsewhere, EasyEDA asks to save and close it there. Answer **No** and ask the owner to close their tab: two tabs on one document can overwrite each other.
- **Output blocking:** `javascript_tool` output containing `=`, `&` or `?` is blocked as query-string data; replace those characters before returning text.
- **4.1 library quirks:**
  - `lib_Device.getByLcscIds` can return a stray footprint-less device;
  - placing a library device the project already holds fails ("Create project component failed");
  - use project copies that have footprints (`lib_Device.search(name, projectLibraryUuid)`).

  The capture template handles this now. It matters for layout only if a footprint is swapped.
- **Exports:** `hardware/tools/easyeda_export.js` downloads `AURIS_<date>.epro2` and a BOM into `~/Downloads` (it needs a schematic page active for the BOM). Rename when a same-day export already exists in the repo (as with `_freeze`), move it to `hardware/<date>/`, then run `python3 hardware/tools/easyeda_check.py <file>`.
- **Never clear and re-capture a whole schematic page in 4.1** (it broke a project on 2026-11-18). Schematic edits go remove-part → capture → tidy, in place.

## Deliverables

1. `hardware/layout/` (new):
   - a short layout README: stack-up and its numbers, net classes and widths, placement decisions block by block, what was routed by script and what by hand;
   - the rendered placement images.
2. Project footprints fixed (phase 2), board set up, placement done, routing and DRC as far as agreed with the owner.
3. An export in `hardware/<date>/` with a passing `easyeda_check.py`, committed on a branch.
4. Finish each session with:
   - what changed in EasyEDA;
   - what the owner must do (clicks, decisions, routing to review);
   - open items carried forward from the freeze record.
