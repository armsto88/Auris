# Rev A PCB layout

Layout record for the rev A board. The schematic is frozen at tag `schematic-rev-a-freeze`; the plan and rules are in [`hardware/review/handover-rev-a-pcb-layout.md`](../review/handover-rev-a-pcb-layout.md). This file holds the numbers layout works to and the decisions made, phase by phase.

**State (2026-11-19):** phase 0 and the preparation for phases 1–2. Nothing has been changed in EasyEDA yet. The PCB is still EasyEDA's 2-layer default with all 346 parts on the top side at 0°, spread over about 590 × 220 mm; no outline, tracks or vias. The read-only API probe ([`hardware/tools/easyeda_pcb_probe.js`](../tools/easyeda_pcb_probe.js)) is written but not yet run: the Claude in Chrome extension was not connected.

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

## Net classes (proposed, to set in EasyEDA in phase 1)

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

After the edits, re-export and run `python3 hardware/tools/easyeda_check.py <file>`: it must still pass.

## Still to do

- Phase 0: run the API probe; the owner's answers on outline, edges, mounting holes and top-side-only.
- Phase 1: set 4 layers and this stack-up, the outline, the net classes and rules; confirm the widths in JLC's calculator.
- Phases 2–5 per the handover.
