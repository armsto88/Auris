# Handover: second opinion on the rev A placement, then a better arrangement (pass 7)

You are giving an independent second opinion on the component placement of the Auris rev A board, and then helping the owner re-place it. The owner placed the board with a script planner, had one review (`hardware/review/2026-11-19-placement-review.md`), applied its fixes as passes 4–6, started routing by hand and stopped: the placement does not convince them. Their example: the nano-SIM holder J301 sits at the left edge, 71 mm from the LTE module U301 at the top-right, so the four SIM signals cross the whole board. The last review judged the block arrangement "sound" and fixed local distances only; the owner wants exactly that arrangement questioned. Work from first principles and on your own judgment: say what is wrong with the arrangement, propose a better one, and show what it costs. Problems found, not the placement defended.

## How this runs

- **Stage 1, the review (read-only, deliver first).** Write the review file described under *Deliverable*. Do not change EasyEDA, the sheet CSVs, the exports or the repo copy of `place.py`; do not commit. Put your own scripts, planner copies and pictures under `/tmp/auris-review2/`. `python3 hardware/layout/place.py --check hardware/2026-11-20/AURIS_2026-11-20_cleared.epro2 cleared` re-renders `hardware/layout/placement-cleared.png` (same picture); that is the only repo file it may touch.
- **Stage 2, pass 7 (after the owner has answered the review's questions).** Apply the agreed moves with the tooling under *Applying a pass*, re-check, export, record it in `hardware/layout/README.md` (*Still to do*, one bullet like the pass 4–6 ones). Ask before every change to the board. The owner is available and answers multiple-choice questions readily; ask when a decision is theirs.
- **Rules that always apply.** Part, footprint or schematic changes need the owner's approval first and a row in `hardware/review/schematic-change-log.csv` (the schematic is frozen at tag `schematic-rev-a-freeze`). Commit and push only when asked. Take Auris facts from Auris docs only: `docs/20-FIELDMESH-…` describes another product and is background, not a spec. The browser workflow is hands-off (see *EasyEDA*).

## The product, in one paragraph

Auris is a solar-powered outdoor acoustic recorder with on-device detection and LTE uplink, deployed in Europe and Australia (heat in Australian summer sun, cold in European winter). Main parts: ESP32-S3-WROOM-1 (U401), Quectel EG810M-EU LTE module (U301, u.FL J302 to an FPC antenna on the box's right wall), PCM1863 ADC (U102) with mic preamps (U103/U104/U105) and a separable mic head on J101 through the bottom wall (J102 is the optional second mic, not fitted), CN3791 solar MPPT charger (U201) fed from the panel terminals J201/J202, a 1S2P 18650 pack on J203 under the board on a 3D-printed plate, TPS63802 main 3.3 V (U206), TPS63020 modem rail (U207, ≈ 3 A peaks into U301), DS3231M RTC with a CR1220 (U205, BT201), TMP390 cell-temperature cut-out (U203), a wake button SW201, a ship switch SW202, a status LED and a 7-pad pogo row for programming. Service is lid-off: USB-C J401 (vertical), microSD J402 (flip lid), SIM, switches and pogo row are used with the lid off; the walls carry only the mic connector, the panel wires and a vent.

## What is fixed, what is open

**Fixed (mechanics and owner decisions; do not spend time on them):**
- Outline 80 × 105 mm (origin bottom-left, Y up, mm, angles counter-clockwise), 2 mm corner radii; M3 holes at (4, 4), (76, 4), (40, 101), (76, 101), kept clear ± 3.6 mm; the 35 × 6 mm notch at the top-left (x 0–35, y 99–105) for the ESP32 antenna strip.
- 4 layers JLC04161H-7628, 1.6 mm; all parts on the top side; L2 solid GND, L3 power pours, L1/L4 signals.
- The pack under the board (≈ 40 × 70 × 20 mm, assumed centred at x 20–60, y 25–95, not yet drawn); the LTE antenna on the right wall (J302 at the right edge near the top); the mic connector J101 at the bottom edge; the panel wires into J201/J202 at the bottom edge; the battery plug J203 at the right edge; lid-off service; box and plate follow the board, with ≥ 12 mm beyond the edge at the SIM, ≥ 15 mm at the bottom edge (mic plug, panel wires), ≥ 10 mm at the right edge (battery plug).
- U301's 3 mm part-free ring; all 54 test pads stay; no shield can on rev A; BT201 is the top-entry QIJEY CR1220-2 holder (no slide-in clearance).

**Decided on 2026-11-20, but may be reopened if you make the case (say what the change costs):**
- ESP32 at the top-left with the antenna in the notch (Espressif's preferred corner is top-right; the owner chose a range test over a move; the LTE antenna is on the right wall, which argues for keeping the two radios apart).
- The service cluster SW201/SW202/LED401 + latch parts at the right edge above J203 (pass 5); the pogo row TP404/TP401–TP403/TP413–TP415 at x = 26 beside U401; BT201 in the centre; U203 over the pack (gets a bottom copper pad through a plate window when routed).

**Open: everything else.** The position of every block and part, the three left-edge connectors J401/J402/J301 and their order, U401's and U301's orientation, the converters' and the charger's positions, the RTC, the level shifter U302, the test pads.

## The board as it is

- **Export:** `hardware/2026-11-20/AURIS_2026-11-20_cleared.epro2` (346 parts, 187 nets; no tracks or vias; pours GND on L1/L2/L4, 3V3 and VMODEM on L3; 7 keep-out regions). Picture `hardware/layout/placement-cleared.png` (parts coloured by sheet, pads gold, U301's ring dotted), positions `hardware/layout/placement-cleared.csv`. It is placement pass 6 plus five small hand moves by the owner near the charger (TP203, TP204, TP206, R203, C206). `hardware/tools/easyeda_check.py` passes; `place.py --check … cleared` passes every check except the known cosmetic R213/U202 overlap (a polygon-pad extent on the same net, 0.17 mm).
- **Arrangement by block (pass 6):** top-left U401 with the USB/SD support parts and the pogo row to its right; left edge from the top: J401 USB-C (4.5, 73), J402 microSD (9, 56), J301 SIM (8.3, 39.5); bottom-left the audio front end (U102 at (22, 20), preamps, J101 at the bottom edge); bottom-right J201/J202 with the charger U201/L201 above them; centre BT201 (40, 41), U205 RTC (25, 39), U203 (30, 52); centre-right U206 (34, 76) and U207 (47.7, 62.4) with their inductors and 470 µF cans; right edge J203 (74.9, 40) with the fuse, the reverse-polarity and load FETs and the battery-sense parts, then the service cluster; top-right U301 (62.5, 85.5) with its VBAT array above it, J302 (77.4, 91), and U302 (the UART level shifter) between U301 and U401. Reasons as the owner gave them: `hardware/layout/README.md`, *Board outline and arrangement* (table).
- **How it got here:** `hardware/layout/place.py` placed pass 1–3 greedily from anchors and block regions; the 2026-11-19 review moved 65 parts (pass 4: decoupling and switching loops to their pins, the modem's VBAT array above U301, the SIM filter caps at the holder, the preamp input network beside U102); passes 5–6 moved the service cluster. So the local rules are mostly met and the block arrangement is the planner's first guess, never re-examined.

### Numbers that back the owner's doubt (measured from the export, pad centre to pad centre)

Longest nets (the span is the longest pad-to-pad distance on the net):

| Span mm | Net | Pads | Between | Note |
|---|---|---|---|---|
| 77.2 | SOLAR_ADC | 2 | R240.2 ↔ U401.38 | panel-voltage sense into the ESP32 ADC |
| 66.4 / 65.6 | AUD_SDA / AUD_SCL | 4 | U102 ↔ U401.11/12 | audio I²C |
| 63.9 / 61.3 / 61.2 / 45.1 | AUD_BCK / AUD_LRCK / AUD_DOUT / AUD_MCLK | 3 | R103–R105 ↔ U401.8/9/10, R102 ↔ U401.17 | I²S clocks and data across the board |
| 63.3 / 61.2 / 59.7 / 59.0 | MIC1_DC_SENSE / PREAMP_EN / AUDIO_EN / AUD_INT_MCU | 2–3 | audio ↔ U401.5/6/7/4 | audio control |
| 63.0 / 60.6 / 49.0 | STATUS_LED / PWR_HOLD / BTN_SENSE | 2–4 | service cluster ↔ U401.37/18/28 | slow, but they cross everything |
| 60.2 | VBAT_SW | 19 | U101.1 ↔ C237.2 | the switched battery rail feeds the audio LDO (bottom-left), both converters (centre) and the latch (right edge) |
| 57.5 | USIM_VDD | 5 | J301.C1 ↔ U301.14 | SIM supply |
| 45.3 / 42.1 / 39.6 | SIM_CLK_M / SIM_DATA_M / SIM_RST_M | 2 | R307/R308/R306 ↔ U301.13/11/12 | SIM signals, holder side via the 0 Ω links |
| 52.8 / 51.6 / 51.3 | USB_WAKE / WAKE_N / LATCH_LOGIC | 3–5 | latch ↔ R226 / U205 / SW202 | latch logic between the right edge, the RTC and the USB corner |
| 52.6 | BATT_ADC | 2 | R218.2 ↔ U401.39 | battery sense |
| 50.9 | 3V3 | 22 | C402.1 ↔ R237.2 | |
| 45.2 | VMODEM | 12 | D205.1 ↔ R301.1 | U207 output to the module (L3 pour planned) |
| 44.7 | SYS_SDA / SYS_SCL | 4 | U205 ↔ U401.21/22 | RTC I²C |
| 43.6 / 40.9 | MODEM_EN / MODEM_PG | 3 | U207 ↔ U401.19/20 | |
| 41.5 | SD_D0 | 5 | U401.36 ↔ J402.7 | SD bus |
| 40.3 | MPPT | 5 | Q204.3 ↔ U201.6 | charger |

Block-to-block (part centre to part centre): J301 → U301 71 mm; U102 → U401 69; J402 → U401 33; J401 → U401 18; U302 → U301 20; U302 → U401 30; J203 → U207 35; U207 → U301 27; J101 → U103 20; U203 → J203 47; BT201 → U205 15.

The maker's rule for the SIM (Quectel EG810M-EU QuecOpen&QuecPython HD V1.0, *USIM interface*, the notes under Figure 17): place the USIM connector close to the module, trace length as short as possible and at most 200 mm, keep the USIM signals away from RF and power-supply traces, the 33 pF/100 nF parts at the connector, ground shielding between USIM_CLK and USIM_DATA. So 45–58 mm is inside the letter of the rule; the owner's point is that it should not need to be that long, and that the signals cross the audio/SD/power areas on the way.

Snippet to reproduce the table (`pcb_board.py` loads the export; `part.pad_xy(pad)` gives board-frame pad centres):

```python
import sys, math, itertools
sys.path.insert(0, "hardware/tools")
from pcb_board import load_board
b = load_board("hardware/2026-11-20/AURIS_2026-11-20_cleared.epro2")
def pxy(des, num):
    p = b.parts[des]; return p.pad_xy(next(q for q in p.fp.pads if q.num == str(num)))
for net, pads in b.net_pads.items():
    if net == "GND" or len(pads) < 2: continue
    pts = [(d, n, pxy(d, n)) for d, n in pads]
    d, a, c = max((math.dist(x[2], y[2]), x, y) for x, y in itertools.combinations(pts, 2))
    print(f"{d:6.1f} {net} {a[0]}.{a[1]} <-> {c[0]}.{c[1]}")
```

## What to answer

1. **Is the block arrangement right?** For each block, say where it belongs and why (connectivity, the fixed edges, heat, noise, lid-off service), and whether the present spot is that. Give at least one alternative arrangement as a block plan with coordinates and a picture, and compare it with pass 6 on numbers: the long-net table above recomputed, total net span, the audio-to-converter and audio-to-charger separation, the 3 A path length, the distances between the two antennas and from each antenna to the converters, estimated crossings. Test arrangements with the planner, not by eye: copy `place.py` to `/tmp/auris-review2/`, change `ANCHORS`/`REGIONS`/`ORDER`, run it on the cleared export, and run its `check()`; it is greedy, so a failed fit is "the planner could not", not "impossible".
2. **The SIM.** Where J301 goes so that the four USIM nets are short and away from the RF feed and the VBAT/VMODEM copper, while the holder stays at a board edge (side entry, ≥ 12 mm beyond the edge for the card) reachable lid-off. Candidates to test, at least: the right edge below J302 (U301 and its ring may have to move left or down, and J302 with it), the top edge right of the notch, the left edge at the top with U401 moved. Give what moves and what the new USIM spans are. R306–R308 (0 Ω), C310–C313 and D301 belong at the holder.
3. **The ESP32's connections.** Audio I²S/I²C/control to U102 at the bottom-left (60–66 mm), SD (J402, up to 41 mm), USB (J401), the sense lines SOLAR_ADC/BATT_ADC (77/53 mm), status LED and latch (49–63 mm), the modem UART through U302. Is U401's orientation right (which pin groups face which way; today pins 1–14 are on the left column facing the board edge, with C401–C403 in the strip and J401 below)? Would turning U401, or bringing the ADC's digital end (I²S pins 16–18, I²C 23/24) closer, help more than it costs? Keep the audio analog end (pins 1–8, 27–30) toward the mic and away from the converters and the SD bus.
4. **Power.** The 3 A path J203 → F202 → Q205 → Q210 → VBAT_SW → U207 → VMODEM → R301 → U301 pads 42/43; VBAT_SW spans 60 mm because it also feeds the audio LDO U101, U206 and the latch; 3V3 spans 51 mm. Are U206/U207 where the loads and the pack want them? Where does the charger's heat go relative to the cells, BT201 and the audio?
5. **Routability on 4 layers.** Where a hand router will struggle (corridors between the left-edge connectors and U401, around BT201, between the converters and the modem), which nets must cross which, and the L3 pour corridors the 3V3 and VMODEM rails need.
6. **Keep what works.** List what should not move and why, so the gains of pass 4 are not lost: decoupling at the pins, both converters' switching loops, the charger's input loop, the modem's VBAT array above U301, the SIM filter at the holder, the preamp input network beside U102, the RF feed U301.35 → R310 → J302.

Check at least (condensed from the first brief; the previous review's section 4 says what was measured then): decoupling at the pin; switching loops; the audio rules in `hardware/audio-frontend/README.md` (*Layout rules*, rule 7 dropped); RF (U301 ring, feed, ESP32 antenna keep-out, ≥ 20 dB isolation between the two radios); thermal; mechanical and lid-off access (J401 plug overmold, J402's lid swing, the SIM ejection, the pogo jig over the row, the knob side of SW202 toward the edge); manufacturing (≥ 0.7 mm between parts, tall parts beside small ones, copper 0.45 mm from the edge). Mark each finding *measured* or *judgment*, as the previous review did.

## Tooling

- `hardware/tools/pcb_board.py`: `load_board(export)` → `board.parts[des]` (x, y, angle, `fp.pads` with `num`, `nets[pad] = net`, `fit`, `block`), `board.net_pads[net]`, `part.pad_xy(pad)`, `part.extent(margin)`.
- `hardware/layout/place.py`: `ANCHORS`, `REGIONS` (block → rectangles), `ORDER`, per-part margins (`gap_of`), `plan(board)` (greedy, toward connected pads and the "At Uxxx pin N" BOM notes), `check(board, place, targets)`, `render()`, `write_csv()`, `write_js()`. `python3 place.py <export> <tag>` re-plans every part and writes `placement-<tag>.csv/.png` and `hardware/easyeda/pcb-phase3-place.js`; `--check <export> <tag>` compares an export with `placement-<tag>.csv` and runs the checks.
- `hardware/layout/apply_moves.py <base export> <moves.csv> <tag>`: moves only the listed parts (`designator,x_mm,y_mm,angle`) and writes `placement-<tag>.csv/.png` plus `hardware/easyeda/pcb-phase3-place-<tag>.js`. Passes 4–6 were applied this way; `placement-pass4-moves.csv` is the format for your move table.
- The previous review's method for testing moves (evict the named parts, re-fit each at the nearest free spot with the planner's margins, then `check()` the whole board) is described in its appendix; its scripts under `/tmp/auris-review/` may be gone.
- `hardware/tools/easyeda_check.py <export>` checks parts and nets against the sheet CSVs. Netlists and BOMs: `hardware/{audio-frontend,power,lte,mcu}/*-netlist.csv`, `*-bom.csv` (the notes say which cap belongs at which pin); sheet READMEs explain each block; `hardware/layout/README.md` holds every layout decision and number; `hardware/review/handover-rev-a-pcb-layout.md` *Phase 3* has the placement rules.
- Datasheets in `hardware/datasheets/pdf/` (local, git-ignored): Quectel EG810M-EU HD V1.0 (keep-out Fig. 40, USIM, VBAT, RF), `esp32-s3_hw_design.pdf` (antenna corners Fig. 24–26), the WROOM-1 datasheet, `pcm1863.pdf`, TPS63802/TPS63020/CN3791, the connector drawings (TYPE-C-31-D-11, TF-030, the SIM holder, DB301V, JST).
- Requirements and decisions: `docs/19-V1-FUNCTIONAL-REQUIREMENTS.md`, `docs/14-DECISION-REGISTER.md` (ADR-028 lid-off service), `hardware/layout/enclosure-options.md`.

### EasyEDA (stage 2 only)

EasyEDA Pro 4.1.105, web, project **AURIS** (uuid 3ba79283056140b08e7552182142ce8a), PCB `PCB1` (uuid 1171ec2ee0a2c106). Everything goes through scripts run by the page driver so the browser is never clicked by hand: `mcp__claude-in-chrome__tabs_context_mcp` with createIfEmpty → navigate the group's tab to `https://pro.easyeda.com/editor` → synthetic dblclick on the `[class*="prj_name_"]` element whose text is `AURIS` → add a hidden file input, `file_upload` `hardware/tools/easyeda_page_driver.js` to it and run its text with `new Function` → `find` the "Auris script loader" input, `file_upload` the scripts → `window.__aurisStart(name, { titleRe })` and poll `window.__aurisJobResult` (replace `=`, `&`, `?` in anything you return from `javascript_tool`). Scripts: `hardware/easyeda/pcb-phase3-place-<tag>.js` (the moves; it opens PCB1 itself), `pcb-export.js` (saves and downloads `~/Downloads/AURIS_<date>.epro2`; rename it `_pass7` into `hardware/<date>/`), `pcb-drc.js` (DRC summary), `pcb-clear-routing.js`. If EasyEDA asks "document opened in another browser tab … save and close the other?", answer **No** (the owner's own tab) and ask the owner to close or reload their PCB1 tab before you save. If parts move a lot, the L3 pours and the keep-out regions must be regenerated: `hardware/layout/phase4_planes.py` → `pcb-phase4-planes.js` (its rectangles are tied to the pass 6 positions of U301, J302, the MCU corner and the VMODEM strip; adjust them). API facts: `hardware/layout/easyeda-pcb-api.md`.

## Applying a pass (stage 2)

1. Write `hardware/layout/placement-pass7-moves.csv` from the agreed move table; `python3 hardware/layout/apply_moves.py hardware/2026-11-20/AURIS_2026-11-20_cleared.epro2 hardware/layout/placement-pass7-moves.csv pass7`; look at `placement-pass7.png`; the check must pass before anything touches EasyEDA.
2. Run `pcb-phase3-place-pass7.js` through the driver, then `pcb-export.js`; move the export to `hardware/<date>/AURIS_<date>_pass7.epro2`; run `easyeda_check.py` and `place.py --check <export> pass7`; run `pcb-drc.js` (only "Connection Error"s are expected).
3. Update `place.py`'s anchors/regions to match (so a re-plan reproduces the arrangement), the README bullet, and the review file's *Outcome* line. Commit only when the owner asks.

## Deliverable

Write `hardware/review/<today's date>-placement-review-2.md`:

1. **Verdict:** keep the arrangement with local moves, or re-arrange; two or three sentences.
2. **Arrangement:** your assessment of each block's position, the alternative(s) with a picture and the numbers from *What to answer* 1, and your recommendation with its cost (how many parts move, what the owner must re-check, what it does to the box/plate clearances).
3. **The SIM:** the answer to question 2.
4. **Findings**, most severe first, each with severity, designators, where on the board (mm), what is wrong, the rule or datasheet page, and a concrete fix (target x, y, angle), marked *measured* or *judgment*.
5. **Move table** for the recommended pass 7 (designator, from, to, result), tested together with `check()`.
6. **What stays**, with reasons.
7. **Questions for the owner:** decisions only they can make, as multiple choice where possible.

Plain language the owner can act on, numbers where you have them.
