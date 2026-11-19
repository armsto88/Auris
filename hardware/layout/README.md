# Rev A PCB layout

Layout record for the rev A board. The schematic is frozen at tag `schematic-rev-a-freeze`; the plan and rules are in [`hardware/review/handover-rev-a-pcb-layout.md`](../review/handover-rev-a-pcb-layout.md). This file holds the numbers layout works to and the decisions made, phase by phase.

**State (2026-11-19, evening):** phases 0, 1 and 2 done in EasyEDA and saved, except the phase 1 items under *Still to do*. Phase 2 export `hardware/2026-11-19/AURIS_2026-11-19_phase2.epro2` passes `easyeda_check.py`. The PCB has 4 copper layers, the 80 × 105 mm outline, the four M3 holes, the net classes and the rules below (scripts [`hardware/easyeda/pcb-phase1-board.js`](../easyeda/pcb-phase1-board.js) and [`pcb-phase1-rules.js`](../easyeda/pcb-phase1-rules.js); API notes in [`easyeda-pcb-api.md`](easyeda-pcb-api.md)). The 346 parts are still where Update PCB dropped them (top side, 0°, below the board at negative Y); no tracks or vias. DRC: 900 errors, all "Connection Error" (unrouted).

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
- **All parts on the top side.**
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
- Phases 3–5 per the handover. Phase 3 starts with the pogo row and the board-area plan in *Board outline and arrangement*.
