# Rev A PCB layout

Layout record for the rev A board. The schematic is frozen at tag `schematic-rev-a-freeze`; the plan and rules are in [`hardware/review/handover-rev-a-pcb-layout.md`](../review/handover-rev-a-pcb-layout.md). This file holds the numbers layout works to and the decisions made, phase by phase.

**State (2026-11-20):** phases 0, 1 and 2 done in EasyEDA and saved, except the phase 1 items under *Still to do*; phase 3 finished with pass 5 (service cluster at the right edge, PWR_HOLD in the pogo row) and pass 6 (SW202 turned so the knob faces the board edge) placed and saved; the review's decisions are taken. Next: phase 4, routing. Phase 2 export `hardware/2026-11-19/AURIS_2026-11-19_phase2.epro2` passes `easyeda_check.py`. The PCB has 4 copper layers, the 80 × 105 mm outline, the four M3 holes, the net classes and the rules below (scripts [`hardware/easyeda/pcb-phase1-board.js`](../easyeda/pcb-phase1-board.js) and [`pcb-phase1-rules.js`](../easyeda/pcb-phase1-rules.js); API notes in [`easyeda-pcb-api.md`](easyeda-pcb-api.md)). Placement pass 6 is on the board (see *Still to do*); no tracks or vias. DRC: 901 errors, all "Connection Error" (unrouted).

## Board setup in EasyEDA (phase 1, 2026-11-19)

- **Origin** at the board's bottom-left corner: outline X 0–80 mm, Y 0–105 mm, 2 mm corner radii, on the Board Outline layer.
- **Holes** MH1–MH4: unplated ⌀3.2 mm free pads on the Multi-Layer at (4, 101), (76, 101), (4, 4), (76, 4) mm. Add a copper keep-out (≈ ⌀7 mm, for M3 heads and washers) around each before pouring.
- **Copper layers:** 4 (Top, Inner1 = L2, Inner2 = L3, Bottom), all signal layers; L2/L3 become GND and power pours in phase 4.
- **Rules:** the PCB's own configuration (EasyEDA now calls it "自定义配置", custom), based on JLC's 2-layer capability, which is stricter than the multilayer one: track min 0.127 mm, default **0.2 mm**; default clearance 0.152 mm (track–track raised from 0.102); via 0.305/0.61 mm. Added Track rules RF_50 (0.30 fixed), USB_90 (0.25, 0.20–0.30), PWR_3A (1.5, min 0.8 so tracks can neck into small pads), PWR_1A (0.5, min 0.3), and Safe Spacing CLR_0.2 (JLC's table with every value raised to ≥ 0.2 mm). The default differential-pair rule is set to the USB geometry: 0.25 mm tracks, 0.15 mm gap (min 0.127). The pairs are USB (USB_DP/USB_DN) and ESP_USB (ESP_USB_DP/ESP_USB_DN).
- **Net classes** (rules on the class and on each member net):

| Class | Nets | Track rule | Clearance rule |
|---|---|---|---|
| RF_50 | ANT_MAIN, ANT_FEED | RF_50 | CLR_0.2 |
| USB_90 | ESP_USB_DP, ESP_USB_DN, USB_DP, USB_DN | USB_90 | default |
| PWR_3A | BAT_CONN, BAT_FUSED, RAW_BAT, VBAT_SW, VMODEM, VBAT_M, M_L1, M_L2 (U207's inductor nodes) | PWR_3A | CLR_0.2 |
| PWR_1A | 3V3, BB_L1, BB_L2 (U206's inductor nodes), PANEL_IN, PANEL_FUSED, SOLAR_IN, CHG_SW_RAW, CHG_SW, CHARGE_SENSE | PWR_1A | CLR_0.2 |

## Board outline and arrangement (phase 0, owner decisions 2026-11-19)

- **Outline 80 × 105 mm**, portrait as installed, 2 mm corner radii. **Four M3 holes** (⌀3.2 mm, unplated) 4 mm in from each corner, onto a 3D-printed plate; nothing ties the board to the box's bosses ([`enclosure-options.md`](enclosure-options.md)).
- **Antenna notch (owner, 2026-11-19, phase 3):** a 35 × 6 mm cut-out at the top-left (x 0–35, y 99–105 mm) so U401's 6 mm antenna strip sits in free air, per Espressif's ESP32-S3 HW design guide Fig. 26 (board cut away beside and below the antenna, ≥ 15 mm clearance). U401 sits flush at the top-left (body 1.5 mm from the left edge). **MH1 moves to (40, 101) mm**; the other three holes stay. Note: the WROOM-1 antenna's feed is at its right end (the footprint silkscreen shows the feed and short legs there), so Espressif's preferred corner would be top-right; top-left keeps the owner's arrangement, with free air at both ends of the antenna (board edge on the left, notch on the right). Fine for the service hotspot (F5-02); moving U401 to the top-right would mean swapping it with the LTE corner and moving the LTE antenna off the right wall.
- **All parts on the top side.**
- **Battery under the board (owner, 2026-11-19, phase 3 review):** the pack sits on the 3D-printed plate under the PCB, not beside it, so the box needs ≈ 45–50 mm inside height (Hammond 1554P2GY, 80 mm, rather than the 60 mm 1554N2GY). Reason: the left-edge service parts need room beyond the edge.
- **Top-access USB-C and microSD (owner, 2026-11-19, phase 3 review; approved as SC-001/SC-002 and applied):** J401 becomes a vertical USB-C receptacle and J402 a hinged (flip-lid) microSD holder, both used from above with the lid off; the nano-SIM J301 stays side-entry (set once, ejected with a tool). This changes the frozen schematic (BOM/footprints, same nets), so it goes through `hardware/review/schematic-change-log.csv` first.
- **Servicing is lid-off.** No sealed SD/USB port, light pipe or sealed button: the walls carry only the mic's through-wall connector, the panel input(s) and a pressure vent. This changes F5-06 ("swappable without opening the main seal") and the light-pipe reading of F5-05 in docs/19, and docs/18's "sealed/serviceable USB-C"; those documents are not yet updated.
- **Area check:** footprints with courtyards, the ESP32 antenna strip, U301's 3 mm ring and 1.0 mm test pads total ≈ 4,320 mm² (power 1,379, MCU 1,070, LTE 1,007, audio 864), 51% of the top side. Workable on 4 layers with the bottom free for routing; 85 × 105 mm (48%) is the fallback if placement runs out of room.

| Board area (as installed) | Contents | Reason |
|---|---|---|
| Top-left | U401, antenna at the top edge with Espressif's keep-out | Farthest from the battery and the LTE antenna |
| Left edge | J402 microSD, J401 USB-C, LED401, SW201 | Short SD/USB runs to U401; away from the audio inputs. Keep ≈ 20 mm clear beyond the edge (plate and box) for the card and the plug with the lid off |
| Bottom-left | Audio front end, J101 at the bottom edge | Short lead to the mic's through-wall connector; away from the converters |
| Bottom-right | J201, J202 | Short leads to the panel connector in the bottom wall |
| Right edge | J203, U203, then the charger and converters | U203 next to the pack; short 3 A path to U301 |
| Top-right | U301, J302; the LTE FPC antenna on the right wall above the pack | ≈ 80–90 mm from the ESP32 antenna |
| Anywhere reachable with the lid off | SW202, J301, BT201, pogo row (TP401–TP403, TP413–TP415) | Used only when the unit is open |

The battery (two 18650s) sits beside the board in a 25–30 mm strip, or under it on the plate if the box has ≥ 45–50 mm inside; either way the plate holds it.

## Stack-up: JLC04161H-7628, 1.6 mm, 4 layers

From JLC's impedance page (jlcpcb.com/impedance, read 2026-11-19). JLC calculates 4- to 8-layer boards for Nan Ya NP-155F laminate.

| Layer | Material | Thickness | εr | Use |
|---|---|---|---|---|
| L1 | Copper, 1 oz finished | 0.035 mm | | Signals and parts. Nothing under U301 (Quectel) |
| | Prepreg 7628 × 1 | 0.2104 mm | 4.4 | |
| L2 | Copper, 0.5 oz | 0.0152 mm | | Solid GND. Unbroken under U301, the RF feed and the USB pairs |
| | Core | 1.065 mm | 4.6 | |
| L3 | Copper, 0.5 oz | 0.0152 mm | | Power pours (3V3, VBAT_SW, VMODEM), slow signals |
| | Prepreg 7628 × 1 | 0.2104 mm | 4.4 | |
| L4 | Copper, 1 oz finished | 0.035 mm | | Signals, GND pour |
| | Solder mask | 1.2 mil on laminate, 0.6 mil on copper | 3.8 | |

Total about 1.59 mm. Why this one: it is the first on JLC's list, which JLC's calculator guide calls usually the cheapest and quickest, and it is the same build as JLC's "no requirement" 4-layer option. Its thin L1–L2 prepreg keeps the 50 Ω line narrow, close to the width of U301's RF pad (pad 35, 0.6 mm after the phase 2 fix) and J302's signal pad (1.0 mm), so the pads add little discontinuity.

JLC limits used for rules (capabilities page, 2026-11-19): track/space 0.09/0.09 mm minimum for 1 oz multilayer; via 0.15 mm drill / 0.25 mm pad minimum for multilayer; impedance tolerance ±10% standard.

## Controlled impedance

All on L1 referenced to the solid L2 plane (h = 0.2104 mm):

| Line | Nets | Proposed geometry | Field solver | Closed form (no mask, zero thickness) |
|---|---|---|---|---|
| 50 Ω grounded coplanar waveguide | ANT_MAIN (U301 pad 35 → R310), ANT_FEED (R310 → J302) | **track 0.30 mm, gap 0.20 mm** to L1 ground each side | 50 Ω at w 0.295 (gap 0.15: 0.264; gap 0.25: 0.316) | w 0.376 for gap 0.20 (44.5 Ω in the solver) |
| 90 Ω edge-coupled pair | ESP_USB_DP/DN, USB_DP/DN | **track 0.25 mm, spacing 0.15 mm** | 90 Ω at s 0.155 (w 0.20: s 0.120; w 0.30: s 0.219) | IPC-2141: s 0.113 |

The closed forms and the solver differ by about 6 Ω on the coplanar line: with 0.2 mm gaps the 35 µm copper side walls and the mask add capacitance that Wadell's zero-thickness formula leaves out. JLC's calculator models thickness and mask, so expect it to land near the solver.

- RF line: L1 ground beside it stitched to L2 with a via fence on both sides at ≤ 1 mm pitch, vias ≤ 0.5 mm from the gap edge; keep it short and straight, R310/C314/C315 at J302. L2 unbroken under the whole line.
- USB: the ESP32-S3's USB is full speed (12 Mbit/s), so the 90 Ω target is good practice rather than critical; keep the pair together and on one layer. The modem's M_USB_DP/DM (high speed) only go to TP309/TP310: keep that stub short.

Reproduce with `python3 hardware/layout/impedance.py`. It gives a closed-form value (no solder mask) and a 2-D field-solver value (with JLC's mask and the copper thickness) for each line. The solver matches the closed-form microstrip to within 1 Ω at 0.2, 0.38 and 0.6 mm with the mask off. **Confirm the chosen widths in JLC's impedance calculator before ordering** (it needs the browser).

## Current-carrying nets

IPC-2221 widths for a 10 °C rise (outer 1 oz; inner 0.5 oz):

| Net group | Peak current | Outer layer | Inner layer | Use |
|---|---|---|---|---|
| J203 → F202 → Q205 → RAW_BAT → Q210 → VBAT_SW → U207 → VMODEM → R301 → U301 | ≈ 3 A | 1.4 mm | 7.1 mm | Outer-layer pours or ≥ 1.5 mm tracks, with via arrays (≥ 4 × 0.3 mm vias) at each layer change |
| 3V3 | ≈ 1 A | 0.3 mm | 1.6 mm | 0.5 mm tracks; L3 pour |
| SOLAR_IN and the charger path | ≈ 0.6 A | 0.15 mm | 0.8 mm | 0.4 mm tracks; the charger loop as pours |

1 oz copper is 0.49 mΩ per square: 30 mm of 1.5 mm track drops about 29 mV at 3 A.

## Net classes (the plan; as set in EasyEDA see *Board setup* above)

| Class | Nets | Track | Clearance | Notes |
|---|---|---|---|---|
| RF_50 | ANT_FEED, ANT_MAIN | 0.30 mm | 0.20 mm to coplanar GND | L1 over L2, GND via fence both sides at ≤ 1 mm pitch |
| USB_90 | ESP_USB_DP/DN, USB_DP/DN | 0.25 mm | 0.15 mm in the pair | Differential pairs in EasyEDA; M_USB_DP/DM run only to TP309/TP310 |
| PWR_3A | J203 … U301 path above | ≥ 1.5 mm or pour | 0.2 mm | |
| PWR_1A | 3V3, SOLAR_IN, charger nets | 0.5 mm | 0.2 mm | |
| Default | everything else | 0.2 mm | 0.15 mm | via 0.3 mm drill / 0.6 mm pad |

## Footprint fixes (phase 2, layout-only: pad numbers and nets unchanged)

Current pads read from `hardware/2026-11-19/AURIS_2026-11-19_freeze.epro2`; targets from the datasheets in `hardware/datasheets/pdf/`. Coordinates are pad centres in mm in the footprint's own frame.

| Part | Footprint now | Change | Source |
|---|---|---|---|
| U301 | `LGA-109_L17.7-W15.8-P1.10_EG810M-CN`: 103 pads 1.0 × 0.7, 6 centre pads 1.3 × 1.3 | **Outer ring, pads 1–44 and 95–98 (48 pads, 1.1 mm pitch): 1.0 × 0.6** (1.0 radial, 0.6 along the row). Positions unchanged (columns at x ±7.1, rows at y ±8.05). Inner rings 1.0 × 0.7 and centre 1.3 × 1.3 stay | Quectel EG810M-EU QuecOpen&QuecPython HD V1.0, Fig. 40, p.67: outer ring 1 × 0.6 at 1.1 pitch, inner 1 × 0.7 at 1.2 pitch, centre 1.3 × 1.3; ≥ 3 mm to other parts |
| D101, D402 | `X1SON-2_L1.0-W0.6-P0.65-BI-1`: 0.6 × 0.6 at x ±0.5 | **0.3 × 0.5 pads (0.3 along the axis) at x ±0.35** (0.7 mm centres, 0.4 mm gap), corner radius 0.05. Mask opening ≤ 0.07 larger than the pad (EasyEDA's 0.05 default is fine) | TI SLLSEB1G, DPY0002A example board layout, p.20 (TI prefers solder-mask-defined; non-solder-mask-defined is within the drawing) |
| F201 (1812L110/24DR) | `R1812`: 1.283 × 3.456 at x ±2.141 (3.00 gap) | **1.78 × 3.15 at x ±2.615** (3.45 mm gap, 7.01 mm overall) | Littelfuse 1812L series, rev 07/21/17, p.5 pad layout |
| F202 (1812L200THPR) | `F1812`: 1.407 × 3.499 at x ±1.853 (2.30 gap) | Same as F201 | Same |
| C207 (EEE-FP1C100AR) | `CAP-SMD_BD4.0-L4.3-W4.3-FD`: 2.8 × 1.1 at x ±1.661 (0.52 gap) | **Gap ≥ 1.0: pads 2.56 × 1.1 at x ±1.78** (inner edges ±0.50, outer edges unchanged at ±3.06) | Panasonic FP-V size B: terminal gap P 1.0, terminal length I 1.8, width W 0.65 ± 0.1 |
| All 54 test pads | Library `Test-Point-0.5mm`: one 0.5 mm round top pad | **1.0 mm round top pad**, mask default. TP401–TP403 and TP413–TP415 (BOOT, EN, GND, U0TXD, U0RXD, 3V3) in one row at 2.54 mm for the pogo jig | MCU README; second review R2-X4 |
| J401 (HC-TYPE-C-16P-01A) | `USB-C-SMD_HC-TYPE-C-16P-01A` | **Pads 3/4 (front shell legs, y −2.41): copper 1.0 × 1.8, slot 0.6 × 1.4** (now 1.6 / 1.2). **Pads 1/2 (rear shell legs): move from y +1.77 to +1.87** (4.28 mm from pads 3/4, now 4.18); copper 1.0 × 2.1 and slot 0.6 × 1.7 already right. Signal-pad pitches, widths and inner edges match the drawing (the pads run 0.15 mm further back than drawn, which does no harm), and so do the ⌀0.65 locating holes (NPTH at ±2.89, +1.27) | HCTL drawing `C2894897_HC-TYPE-C-16P-01A.pdf`, recommended PCB layout (drawn for a 0.8 mm board: on 1.6 mm the shell legs do not pass through, so pin-in-paste) |
| J401 (TYPE-C-31-D-11, since SC-001) | `USB-C-SMD_TYPE-C-31-D-11_1` | **None needed**: contacts 0.40 × 1.60 at 0.78 pitch, rows ±1.20, shell slots 0.60 × 1.60 in 1.10 × 2.10 copper 8.70 apart, pin names A1…B12 all match | HRO drawing `C5370448_TYPE-C-31-D-11.pdf` (rev A1, 2022-07-27), recommended PCB layout |
| J402 (TF-030, since SC-002) | `CONN-SMD_TF-030` | **Contacts 1–8 moved 0.10 mm** (now #01 at +3.20, #08 at −4.50 from the cover-pad centreline; library had +3.30…−4.40); **upper cover pads 9/11 from y +4.20 to +4.10** (centre 5.70 above the contacts). Contacts 0.80 × 1.50 at 1.10 pitch and cover pads 1.45 × 2.00 at ±6.88 already right. The footprint has no body outline: the planner uses the drawn 13.10 × 13.80 body (y −6.05…+7.75) | Hanbo drawing `C5310449_TF-030.pdf` (rev A4), recommended PCB layout |

**Done 2026-11-19** with [`hardware/easyeda/pcb-phase2-footprints.js`](../easyeda/pcb-phase2-footprints.js), which edits the project-library footprints in place (the PCB takes pad geometry from them and keeps only pad-to-net links). Checked against the freeze export: only these eight footprints changed (62 pads; both Test-Point-0.5mm copies, one per test-point device), pad numbers unchanged, all 981 pad-to-net links identical, and `easyeda_check.py` gives the same output as for the freeze export. Notes:

- The X1SON-2 footprint is shared by **D101, D102 and D402** (all TPD1E10B06DPYR; D102 is the unfitted mic-2 option), so D102 gets the TI land too.
- X1SON-2 pad corners stay square: TI's 0.05 mm radius is cosmetic, and EasyEDA's `radius` field has no documented unit.
- The footprint names are unchanged (the test-point footprint is still called `Test-Point-0.5mm`, now with a 1.0 mm pad).
- DRC after the change: 8 clearance errors, all between neighbouring 1.0 mm test pads in the unplaced pile; they go away with placement. C207's library silkscreen touches its pad edges at the same 7 points as before the change (JLC clips silkscreen on pads).
- The 2.54 mm pogo row (TP401–TP403, TP413–TP415) is placement, phase 3.

## Still to do

- Phase 0: done (2026-11-19). Outline, arrangement, holes and top-side-only are decided (above). Panel on a separate bracket and mic on a through-wall connector (owner, 2026-11-19); enclosure shortlist in [`enclosure-options.md`](enclosure-options.md) — the PCB mounts on a 3D-printed plate (owner, 2026-11-19), so its outline and holes are free; it must fit a box with ≥ 110 × 105 mm floor and ≥ 45 mm inside height. API probe run, see [`easyeda-pcb-api.md`](easyeda-pcb-api.md).
- Phase 1, two items left:
  - **Physical stack-up in EasyEDA** still shows the 2-layer default (`getStackup()`), and the stack-up setters arrive only in EDA 4.2. Owner: enter JLC04161H-7628 in the Layer Manager's physical stack-up, or leave it and choose JLC04161H-7628 when ordering (the order is what JLC builds to).
  - **Confirm the RF and USB widths in JLC's impedance calculator** (browser).
- Phase 2: done (above).
- **Phase 3, pass 6 applied and saved in EasyEDA (2026-11-20): SW202 turned 180°** so its knob faces the board edge instead of the board centre (owner, after seeing pass 5): SW202 (76.0, 68.0, 90°), terminals 1–3 now at x 74.45, body 0.74 mm inside the edge, pad copper clear of the 0.45 mm edge rule. One move ([`placement-pass6-moves.csv`](placement-pass6-moves.csv), from the pass 5 export); export `hardware/2026-11-20/AURIS_2026-11-20_place6.epro2`: `easyeda_check.py` passes, `place.py --check <export> pass6` finds all 346 parts at the plan and passes every check, DRC has only the 901 unrouted connections ([`placement-pass6.png`](placement-pass6.png), [`placement-pass6.csv`](placement-pass6.csv)). `place.py`'s SW202 anchor follows.
- **Phase 3, pass 5 applied and saved in EasyEDA (2026-11-20): the service cluster at the right edge and PWR_HOLD in the pogo row** ([`placement-pass5.png`](placement-pass5.png), [`placement-pass5.csv`](placement-pass5.csv); export `hardware/2026-11-20/AURIS_2026-11-20_place5.epro2`: `easyeda_check.py` passes, `place.py --check <export> pass5` finds all 346 parts at the plan and passes every check, DRC has only the 901 unrouted connections). Owner (2026-11-20): the wake button SW201 and the ship switch SW202 sat in the middle of the board between the coin cell, the latch transistors and the battery-sense parts, with the LED 35 mm away; not friendly to use lid-off. The latch nets are slow, so the whole service cluster moved to the free strip at the right edge, above the battery connector: SW202 (76.0, 68.0, 270°, knob toward the board centre), SW201 (76.0, 59.0), LED401 (70.5, 55.0) with R416, and the latch parts Q208/Q209/Q211/D206/R228/R245/R246/C237 beside them (x 65–72, y 58–73). Q210 and the battery-sense parts stay. Also TP404 (PWR_HOLD) joined the pogo row at (26.0, 77.96), 2.54 mm below TP401, so a pogo jig can hold the board on through resets without a USB cable (MCU README, *Programming and recovery*); Q402 and C406 shifted to make room. 15 parts moved in all ([`placement-pass5-moves.csv`](placement-pass5-moves.csv), applied with `apply_moves.py` from the pass 4 export; script [`pcb-phase3-place-pass5.js`](../easyeda/pcb-phase3-place-pass5.js)). `place.py` now anchors SW201/SW202/LED401 there, has the 7-pad pogo row and a right-edge `p_latch` region. The Hub v2 config-button comparison is in the power README (*Firmware notes*).
- **Owner decisions on the placement review's questions (2026-11-20):** (1) U203 senses the pack through a bottom-side copper area with thermal vias under it and a thermal pad through a window in the plate (routing item; plate gets the window). (2) ESP32 stays in the top-left corner with the notch; range-test in the box. (3) U301's ring stays 3 mm everywhere. (4) Rev A is routed at 80 × 105 mm; shrinking (review §2.4) is a rev B question. (5) BT201 is the holder already used on FieldMesh Node v4 (QIJEY CR1220-2, `C70381`, same EasyEDA footprint `BAT-SMD_CR1220-2`, body ≈ 15.6 × 14.4 mm, pads to 21.7 mm); the owner has it on hand: the cell goes in from the top, so no slide-in clearance is needed and the netlist note's polarity meter-check is the only open item. (6) SW202: the review's 1 mm gap is to BT201's flat solder tab; the holder body (3 mm tall, chamfered corner) is 7.5 mm from the switch at the knob's height, and moving the switch up is blocked by R245 and the battery-sense parts, so it was first left in place; later the same day the owner found the button and switch in the middle of the board unfriendly, and pass 5 moved the whole service cluster to the right edge (below). (7) Audio layout rule 7 (room and pads for a shield can over the analog section) is dropped for rev A: no pad ring, no re-fit; the G2 noise test decides whether rev B gets a can. (8) All 54 test pads stay. (9) J201/J202: the Dorabo DB301V drawing (rev T0-1, 2022) shows the wire entry on the vertical face 3.5 mm from the pin axis and the screw on the sloped face 3.4 mm from it, so the body is nearly symmetric about the pins and the footprint's arrows (wire entry toward the bottom board edge) set the orientation at assembly; keep them and put the entry side on the silkscreen. (10) Outline fixed at 80 × 105 now; the box and plate follow with the review's clearances (SIM ≥ 12 mm left, mic plug and panel wires ≥ 15 mm bottom, battery plug ≥ 10 mm right). (11) Docs updated the same day: F5-05/F5-06 in docs/19, the port line in docs/18, ADR-028 (lid-off service) in docs/14.
- **Phase 3, pass 4 applied and saved in EasyEDA (2026-11-20): the placement review's fixes** ([`placement-pass4.png`](placement-pass4.png), [`placement-pass4.csv`](placement-pass4.csv); export `hardware/2026-11-20/AURIS_2026-11-20_place4.epro2`: `easyeda_check.py` passes, `place.py --check <export> pass4` finds all 346 parts at the plan and passes every check, DRC has only the 901 unrouted connections). The review ([`hardware/review/2026-11-19-placement-review.md`](../review/2026-11-19-placement-review.md)) found two blockers and five should-fix items; pass 4 moves 65 parts and leaves the other 281 where pass 3 put them: the modem's VBAT array C301–C306/R301 into the strip above U301 (4.5–7.6 mm from pads 42/43, was 20–26); L203 onto U207's switch side (3.9 mm from the L pads, was 6.3 mm on the far side) with C219/C233 swapped to the VIN/VOUT sides (4.7/6.1 mm); C222/C223 at U206's VIN (2.6/3.5 mm, was 9.3/7.6); C203/C202 beside Q202's source (4.8/6.9 mm; charger input loop ≈ 24 mm, was ≈ 47); U205 turned 180° so C216 is 2.3 mm from pin 2 (was 9.9; C217 takes C216's old spot); U401 3 mm to the right (body 4.0 mm from the left edge) with C401/C402/C403 in the strip beside pins 2/3 (4.3/2.4/5.3 mm, was 19–20) and the pogo row at x = 26; the preamp-path input network (C122, R124, R144, R145, U104, C140, C123, R125) in one cluster left-below U102 (R124/R125 3.3/3.7 mm from pins 30/28, C140 1.9 mm from U104 pin 8; TP101/TP106 moved left to make room) with the six unfitted mic-2 parts parked at x 38–51, y 16–30; R103–R105 at 3.6–5.8 mm from U102's I²S pins (was 9.2–9.4); the SIM filter caps C311–C313 at 2.0–4.6 mm from J301 (was 8–15); C404 next to C405 (6.8 mm from the card's VDD contact, was 12); TP203 beside D204 (out of the switch-node copper window). Not applied (owner decisions, review §5): the ESP32 corner, the 76 × 100 mm outline, U301's ring, SW202's knob side, the shield-can ring, the pack position. The moves are listed in [`placement-pass4-moves.csv`](placement-pass4-moves.csv) and applied with [`apply_moves.py`](apply_moves.py) (writes the CSV/PNG and [`pcb-phase3-place-pass4.js`](../easyeda/pcb-phase3-place-pass4.js), which moves only the listed parts); save + export with [`pcb-export.js`](../easyeda/pcb-export.js), DRC summary with [`pcb-drc.js`](../easyeda/pcb-drc.js). `place.py`'s U401 anchor, pogo column and antenna keep-out now match pass 4 (a re-plan would still re-place everything else greedily).
- **Phase 3, pass 3 (2026-11-19, superseded by pass 4)** ([`placement-pass3.png`](placement-pass3.png), [`placement-pass3.csv`](placement-pass3.csv); export `hardware/2026-11-19/AURIS_2026-11-19_place3.epro2`: `easyeda_check.py` passes, `place.py --check` finds all 346 parts at the plan and passes every check, DRC has only the 901 unrouted connections). Pass 3 follows the owner's decisions after pass 2: top-access J401/J402 (SC-001/SC-002) and the battery under the board. J401 (vertical USB-C) sits just below U401 near its USB pins, J402 (flip-top microSD) below it with its contacts facing the SD parts, the SIM J301 at the left edge where J401 was. U203 (TMP390) now sits over the battery: **the pack position is assumed centred under the board (x 20–60, y 25–95 mm); confirm when the plate is drawn.** BT201 is fixed in the centre, away from the charger and converters. Audio blocks are placed decoupling first, so U102's caps and C118 sit at their pins. TF-030's footprint has no body outline, so the planner uses a 13.1 × 14 mm body for it (`BODY_OVERRIDE` in `pcb_board.py`). J401's and J402's library footprints were checked against the makers' drawings (2026-11-19, PDFs fetched through the browser): J401 matches, J402 needed a 0.10 mm correction (footprint table below, applied with `pcb-phase2-footprints.js`; the placement did not move). Earlier pass 2 ([`placement-pass2.png`](placement-pass2.png)) answered the owner's review of pass 1 ("lots of space, everything cramped") ([`placement-pass2.png`](placement-pass2.png), [`placement-pass2.csv`](placement-pass2.csv); export `hardware/2026-11-19/AURIS_2026-11-19_place2.epro2`, checked the same way as pass 1 and read back after reloading EasyEDA). Pass 2 answers the owner's review of pass 1 ("lots of space, everything cramped"): margins per part instead of 0.3 mm everywhere (0.8 mm around ICs and multi-pin parts for fan-out, 0.5 mm around connectors, 0.35 mm around passives, so ≥ 0.7 mm between any two parts, median 0.76 mm) and larger block regions; parts now cover 40 % of the board (body and pads). Pass 1, for reference: export `hardware/2026-11-19/AURIS_2026-11-19_place1.epro2`: `easyeda_check.py` output identical to the freeze export; `place.py --check` finds all 346 parts exactly where planned and passes every placement check; DRC has only the 900 unrouted "Connection Error"s. The edge connectors J301, J101, J102 and J203 sit with their mounting-pad copper 0.5 mm inside the edge (their tabs reach past the body front). The rotation convention is confirmed (counter-clockwise; six probe pads land where predicted). Planner [`place.py`](place.py) (anchors, block regions, greedy placement toward connected pads and the BOM/netlist "At Uxxx pin N" notes, checks, PNG, EasyEDA script); helper model [`hardware/tools/pcb_board.py`](../tools/pcb_board.py). Result: [`placement-pass1.png`](placement-pass1.png), [`placement-pass1.csv`](placement-pass1.csv). Local checks: no overlaps, everything inside the outline, nothing in the hole keep-outs or within 3 mm of U301. Known compromises for review: U401's 3V3 decoupling (C401/C402) ≈ 20 mm from pin 2, which is at the board edge; I²S series resistors R103–R105 11–14 mm from U102; J101/J102/J203/J402/J301 facing directions inferred from the footprints (body overhang past the pads = mating side), to confirm against the drawings. Scripts: [`pcb-phase3-outline.js`](../easyeda/pcb-phase3-outline.js) (notch, MH1), then [`pcb-phase3-place.js`](../easyeda/pcb-phase3-place.js) (generated by `place.py`; moves all 346 parts and checks six pads), save, export, `easyeda_check.py`, `place.py --check <export>`.
- Phases 4–5 per the handover.
