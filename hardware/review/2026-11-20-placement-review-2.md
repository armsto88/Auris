# Placement review 2: rev A block arrangement, pass 6 (2026-11-20)

**Outcome (2026-11-20):** applied as placement pass 7. The owner took the recommended answer to every question: the full 55-part move table, latch transistors at the RTC and Q210, charger +10 / −4 mm, Q204 to the charger, R203 moved; ≥ 12 mm box clearance beyond the right edge, with the LTE FPC antenna in the upper half of the right wall; audio bus as an L4 bundle. Export `hardware/2026-11-20/AURIS_2026-11-20_pass7.epro2`: `easyeda_check.py` identical to the cleared export, `place.py --check … pass7` all 346 parts at the plan with every check passing, DRC 709 unrouted connections only (after re-filling the existing pours). Record in `hardware/layout/README.md` (*Still to do*, pass 7).

This is an independent second opinion on the block arrangement of `hardware/2026-11-20/AURIS_2026-11-20_cleared.epro2` (pass 6 plus the owner's five hand moves near the charger; 346 parts, 187 nets, no tracks). Brief: `hardware/review/handover-placement-review-2.md`. Nothing in EasyEDA, the sheet CSVs, the exports or `place.py` was changed, and nothing was committed. `place.py --check … cleared` re-rendered `hardware/layout/placement-cleared.png` (same picture).

**How it was checked.** My scripts, the planner copy and the pictures are under `/tmp/auris-review2/` (not in the repo):

- `place_r2.py` is a copy of `place.py`.
- `refit.py` uses the previous review's method. It starts from the pass 6 board, puts the moved parts at their targets (or moves a group rigidly), evicts every part that now collides, and re-fits those parts with the planner's own margins, keep-outs and scoring. It then runs `check()` on the whole board.
- `fullplan.py` is a full planner re-plan with changed `ANCHORS`/`REGIONS`.
- `metrics.py` computes the numbers below.

**Measures.** All distances are pad centre to pad centre on the shared net unless stated otherwise.

- *Span* is the longest pad-to-pad distance on a net.
- *MST* is the length of the net's minimum spanning tree.
- *Crossings* counts where straight MST segments of different nets cross. It is a rough proxy for vias and layer changes. GND is excluded, and the "≥ 10 mm" count keeps only long segments and leaves out 3V3, VMODEM and VBAT_SW, which go on L3.

The brief's long-net table reproduces exactly from the export (SOLAR_ADC 77.2, AUD_SDA 66.4, USIM_VDD 57.5 mm and so on). *Measured* means computed from the export or read from a datasheet; *judgment* means my assessment.

## 1. Verdict

**Re-arrange three blocks and keep the rest.** The owner's doubt is right in three places:

- **The SIM is in the wrong place.** The holder is 71 mm from its pins, so four USIM nets of 40–58 mm cross the SD, power and audio areas.
- **The wake-latch transistors sit with the switches** instead of at their inputs, so four wake nets of 51–61 mm cross the board.
- **The charger's switching core sits 10 mm from the audio supply parts** while the bottom-right corner (x 65–80, y 8–30) is empty.

The rest of the arrangement is what the fixed edges force: ESP32 top-left, audio at the mic connector, LTE top-right, battery and power down the right. The bigger re-arrangement I tested, turning U301 so the SIM sits on the top edge (alternative B), saves about 14 % more crossings but adds 12 mm to the box and moves more parts.

The proposed pass 7 moves 55 parts. Every check passes and none of the pass 4 gains is lost.

## 2. Arrangement

### 2.1 Block by block

| Block | Pass 6 | Where it belongs, and why | Verdict |
|---|---|---|---|
| ESP32 U401, pogo row | Top-left, antenna in the notch; pogo row at x 26 | A top corner with the antenna in free air and far from the LTE side. Its largest bus (audio) runs down and its LTE UART runs right | **Keep** (owner decision; orientation in 2.4) |
| USB J401 | (4.5, 73), 8 mm below pins 13/14 | Next to pins 13/14 at the bottom of the left column | **Keep** |
| microSD J402 | (9, 56); SD nets 15–41 mm | Below the bottom-row SD pins 15/24/25/26 | **Keep.** SD_D0's 41 mm comes from the pin: it is pin 36 on the right column |
| SIM J301 | Left edge (8.3, 39.5), 71 mm from U301 | At U301's SIM corner (pins 11–14 at the module's bottom-left), at a board edge | **Move** (R2-F1, section 3) |
| Audio front end | Bottom-left (x 0–47, y 0–37), U102 at (22, 20) | At J101 on the bottom edge, as far as possible from U206, the charger, the SD bus and the LTE feed | **Keep.** Its 60–66 mm digital bus to U401 is set by geometry (U401 at the top, J101 at the bottom); see 2.4 |
| Panel input J201/J202, F201, D201, Q201 | Bottom edge, x 46–65 | Bottom edge (fixed), short to the charger | **Keep** |
| Charger core U201, Q202, D203, D204, L201, R202 and its passives | x 37–69, y 22–37: 10.1 mm from the audio supply parts, 16.4 mm from U103, 1.3 mm from BT201. The corner x 65–80, y 8–30 is empty | Bottom-right corner, between the panel inputs and the battery plug, as far from the audio as the panel connectors allow. It is the one switcher that runs during daytime recordings | **Move as a group** (R2-F3) |
| Battery input J203, F202, Q205, Q210, battery sense | Right edge, y 36–53 | Right edge (fixed plug), at the start of the 3 A path | **Keep** |
| Modem rail U207, L203, C219, C233 | (48, 62) | Between Q210 and U301. VMODEM runs 37 mm on L3 because U301's VBAT pins face the top edge | **Keep** (2.5) |
| 3V3 converter U206 | (34, 76) | Near its main loads (U401, U302, SD) and 39 mm from U102/U103 | **Keep** |
| LTE U301, VBAT array, RF feed, J302 | Top-right, 0° | Top-right: feed to J302 7.9 mm, VBAT array 4.5–7.7 mm from pads 42/43 | **Keep at 0°** (270° tested as alternative B) |
| U302 level shifter, Q301 PWRKEY | (43, 84), between U401 and U301 | Same | **Keep** |
| RTC U205, BT201 | Centre | Anywhere; slow nets. BT201 (21.7 × 14.4 mm) is the centre's main routing obstacle | **Keep** (owner) |
| TMP390 U203 and cut-out | (30, 52), over the pack | Over the pack | **Keep** (owner); move only the clamp transistor Q204 (R2-F4) |
| SW201, SW202, LED401 | Right edge, y 52–72 | At an edge, together, lid-off (owner) | **Keep at the right edge, 12–14 mm lower**, to make room for the SIM |
| Latch transistors Q208, Q209 | With the switches at x 65–69, y 69 | At their inputs: RTC INT (WAKE_N), the VBUS divider (USB_WAKE), PWR_HOLD from U401 | **Move** (R2-F2) |
| Button sense Q211, D206, R246 | At SW201 | At SW201: BTN_N is a 1 MΩ node and must stay short | **Keep at SW201** (they move with it) |
| Q210 gate network R245, C237 (C237 not fitted) | At the right edge, 17.5 / 23.8 mm from Q210 | At Q210 | **Move** (R2-F2) |

### 2.2 Alternatives tested

- **Proposed pass 7 (alternative A).** J301 and its network move to the right edge under U301. SW201/SW202/LED401 slide 12–14 mm down the right edge. Q208/Q209 move to the RTC and the USB divider, and R245/C237 to Q210. The charger core moves as one rigid group by +10 / −4 mm into the empty corner. Q204 moves to the charger and R203 moves off L201's body. That is 55 parts; every other part stays where pass 6 has it.
- **Alternative B.** U301 is turned 270° and moved to (61.5, 78.4); its VBAT array turns with it to the module's right side. J301 goes on the top edge at (52.7, 96.675, 180°) and J302 drops to (77.4, 72.06). The service cluster and latch change as in pass 7. That is 58 parts, without the charger, Q204 and R203 moves, which are independent and would bring it to about 85.
- **Full planner re-plans** (`fullplan.py`, all non-anchored parts re-placed greedily):
  - *control*: `place.py` unchanged.
  - *plan A*: the pass 7 anchors and regions, plus `l_supply` above U301 as in pass 4.
  - *plan B*: the alternative B anchors and regions.

  All three pass every check. They show that both block plans are feasible for the planner. They are not proposals, because a full re-plan undoes the pass 4 fixes (table in 2.3).

Pictures:

- `/tmp/auris-review2/blocks-compare.png`: pass 6, pass 7 and alternative B as block plans, with the SIM, latch, audio, ADC and modem UART nets drawn as straight lines.
- `/tmp/auris-review2/pass7.png`: the full pass 7 placement in `place.py`'s style.
- `/tmp/auris-review2/altB.png`
- `/tmp/auris-review2/blocks-planner.png`, `control.png`, `planA.png`, `planB.png`

Block plan of pass 7 (x0–x1, y0–y1, mm; rough extents of each block's parts):

| Block | Pass 6 | Pass 7 |
|---|---|---|
| SIM J301 and network | x 0.5–30, y 32.7–50 | x 56–79.5, y 59.7–73.5 (holder x 64.3–79.5, y 59.75–73.45) |
| SW202 / SW201 / LED401 | x 69–79.3, y 54–72.2 | x 70–79.3, y 45.4–58.4 |
| Q208 / Q209 | (69, 69) / (65, 69) | (25.1, 60.0) / (23.3, 46.9) |
| Charger core (26 parts) | x 37.2–69.0, y 20.6–37.4 | x 47.2–79.0, y 16.6–33.4 (R203 re-fitted) |
| Everything else | unchanged | unchanged |

### 2.3 Numbers

| Measure | Pass 6 | **Pass 7** | Alt B | Planner control | Planner plan A | Planner plan B |
|---|---|---|---|---|---|---|
| Parts moved from pass 6 | 0 | **55** | 58 | 253 | 273 | 279 |
| Total net span, mm | 3,500 | **3,154** | 3,073 | 3,245 | 2,983 | 2,873 |
| Total MST length, mm | 4,028 | **3,671** | 3,602 | 3,695 | 3,484 | 3,341 |
| MST crossings, all nets | 896 | **758** | 720 | 872 | 732 | 678 |
| Crossings between ≥ 10 mm segments | 329 | **245** | 210 | 286 | 220 | 178 |
| USIM_VDD / SIM_CLK_M / SIM_DATA_M / SIM_RST_M, mm | 58 / 45 / 42 / 40 | **14 / 8 / 11 / 10** | 18 / 10 / 7 / 7 | 58 / 42 / 43 / 44 | 13 / 9 / 12 / 9 | 17 / 13 / 10 / 7 |
| PWR_HOLD / WAKE_N / USB_WAKE / LATCH_LOGIC, mm | 61 / 52 / 53 / 51 | **27 / 19 / 14 / 47** | 29 / 10 / 14 / 47 | 33 / 17 / 30 / 20 | 35 / 20 / 20 / 18 | 35 / 23 / 20 / 15 |
| BTN_SENSE / STATUS_LED, mm | 49 / 63 | **52 / 57** | 46 / 23 | 43 / 41 | 54 / 41 | 49 / 41 |
| Modem UART M_TXD / M_RXD / M_CTS, mm | 21 / 20 / 24 | **17 / 16 / 22** | 8 / 8 / 12 | 19 / 18 / 22 | 15 / 17 / 27 | 12 / 12 / 14 |
| MPPT (charger feedback node), mm | 40 | **18** | 40 | — | — | — |
| Audio part ↔ converter (U206, L202, U207, L203), edge to edge | 29.0 | **29.0** | 29.0 | 25.2 | 29.3 | 33.3 |
| Audio part ↔ charger switch (U201, L201, Q202, D203, D204, R202) | 10.1 | **18.4** | 10.1 | 6.8 | 7.0 | 10.1 |
| U102 / U103 ↔ charger switch | 16.4 | **22.3** | 16.4 | 17.0 | 18.0 | 18.0 |
| 3 A path J203 → … → U301.42/43 (sum of hops), mm | 73 | **73** | 73 | 61 | 68 | 61 |
| ESP32 antenna strip ↔ J302 | 53 | **53** | 58 | 53 | 53 | 58 |
| ESP32 antenna ↔ nearest converter | 24 (U206) | **24** | 24 | 24 | 23 | 26 |
| J302 ↔ nearest converter | 36 (U207) | **36** | 26 | 34 | 30 | 15 (L203) |

Why the move table is built from pass 6 and not from a re-plan (*measured*, pad to pad on the shared net, mm):

| Pass 4 gain | Pass 6 | Pass 7 | Alt B | Control | Plan A | Plan B |
|---|---|---|---|---|---|---|
| C402 → U401 pin 2 | 2.4 | 2.4 | 2.4 | 20.0 | 20.0 | 20.0 |
| C306 → U301 pad 42/43 | 4.5 | 4.5 | 4.5 | 25.9 | 6.8 | 9.8 |
| C222 → U206 VIN | 2.6 | 2.6 | 2.6 | 6.8 | 6.4 | 7.8 |
| C219 → U207 VIN | 4.7 | 4.7 | 4.7 | 17.9 | 15.8 | 34.7 |
| C203 → Q202 source | 4.8 | 4.8 | 4.8 | 18.2 | 16.8 | 16.8 |
| C216 → U205 pin 2 | 2.3 | 2.3 | 2.3 | 5.5 | 7.2 | 10.2 |
| R124 → U102 pin 30 | 3.3 | 3.3 | 3.3 | 8.9 | 8.9 | 8.9 |

`place.py`'s regions still encode pass 3. A re-plan with them puts the VBAT array back beside U207, 26 mm from the pins: the previous review's blocker F1.

### 2.4 The ESP32's connections (brief question 3)

*Measured.* At 0° the pin groups face:

- **Left column, pins 1–14** (GND, 3V3, EN, nine audio nets, USB D−/D+): the left edge, with 4.0 mm of board beside them where C401–C403 sit.
- **Bottom row, pins 15–26** (SD_CD, MCLK, PWR_HOLD, MODEM_EN/PG, SYS I²C, PWRKEY, SD_CLK/CMD/PWR_EN): J401, J402 and the SD parts.
- **Right column, pins 27–40** (BOOT, BTN_SENSE, BB_MODE, LTE UART and STATUS, SD_D0, STATUS_LED, SOLAR_ADC, BATT_ADC): the pogo row and U302.

The groups match their neighbours, with two exceptions: SD_D0 (pin 36) has to go round the module's corner to J402, and the ADC pins (38/39) sit at the top, 53–77 mm from the dividers.

*Judgment:*

- **Turning U401** does not pay. Only 0° puts the antenna in the notch. 90° CCW (antenna over the left edge) would point pins 1–14 down toward J401 and the audio and save about 15 mm per audio net, but it needs 21 mm of box beyond the left edge, which the owner declined. 180° and 270° put the antenna over the board.
- **Bringing the ADC's digital end closer** means moving U102 up. Every millimetre it moves up adds a millimetre to the analog chain J101 → U103 → U102 (audio rule 4) and brings U102 nearer the SD bus. A 3 MHz I²S bus over solid L2 tolerates 60 mm; the mic signal is the part that matters. Pin swaps would change the frozen schematic for 5–10 mm.
- **Recommendation:** keep U401 and U102 as they are. Route the 11 audio nets as one bundle: vias just inside the left pad column (under the module body, away from the antenna end), then down on L4 under J401 and J402 and through the strip the SIM leaves free (x 0.5–16, y 33–47). Keep the SD and USB nets on L1. Analog pins 1–8 and 27–30 stay at the bottom, toward J101.

### 2.5 Power (brief question 4)

- **U206** is next to its loads. 3V3 spans 51 mm (C402 at U401 pin 2 to R237 at U207's MODEM_PG); the phase 4a L3 pour (x 1–44, y 57–104.5) covers every 3V3 pad except R237 at (46, 70), which needs a short stub. Keep (*measured*).
- **U207**: VOUT → R301 is 37 mm because U301's VBAT pads 42/43 are on the module's top row and the array has to sit there. The phase 4a VMODEM strip on L3 (x 50.5–61.5, 0.5 oz, 1.1 mΩ per square) is about 3.4 squares, so about 3.8 mΩ and 11 mV at 3 A plus the via arrays. Moving U207 does not shorten it while the array stays at the pins. Keep (*measured*, the drop is a calculation).
- **3 A path**, hop by hop: J203 → F202 4.5, → Q205 2.1, → Q210 7.2, → U207 14.5, → R301 37.0, → U301 7.6; 73 mm in total. Pass 7 does not change it. Q210 → U207 no longer passes the latch transistors.
- **VBAT_SW** falls from 60 to 44 mm because C237 moves to Q210. What remains is U101's audio LDO branch (tens of mA), which a 0.3–0.5 mm track carries.
- **Heat** (*judgment*, distances measured): the charger is the only continuous daytime heat source. At 600 mA the two Schottkys carry about 0.2 W each, R202 72–85 mW and L201 about 70 mW. In pass 7 the core is:
  - 11.3 mm from BT201 (was 1.3; the BR1220 is rated to +80 °C);
  - 35.6 mm from U203 (was 25.5);
  - 22.3 mm from U102/U103 (was 16.4);
  - with U201 (x 62–67) outside the assumed pack outline (x 20–60).

  The cost is that R202 comes 3.9 mm from F202 (was 5.9) and U201 4.5 mm (was 8.9). F202's hold current falls from 1.50 A at 60 °C to 1.29 A at 85 °C; I expect less than 2 °C from R202 at 4 mm on a board with two ground planes. Measure F202's temperature in power test 9 with the charger running.

### 2.6 Routability on 4 layers (brief question 5)

*Judgment, from the placement and the crossing counts.* Where a hand router will struggle:

1. **U401's left column.** Eleven signals plus 3V3 and EN leave through a 4 mm strip that holds C401–C403. Use vias just inside the pad row and the L4 bundle (2.4).
2. **Below U401's bottom row** (x 6–28, y 64–79.5). Twelve pins fan into the USB and SD support parts. MCLK, PWR_HOLD and SYS_SDA/SCL go down; MODEM_EN/PG and LTE_PWRKEY go right and cross the right-column LTE nets heading for U302 near x 22–40, y 78–80. Put the right-bound bottom-row nets on L4.
3. **The pogo row** (x 26, y 78–93): seven 1.0 mm pads at 2.54 mm leave 1.54 mm gaps, two 0.2 mm tracks each. About 12 right-column nets must pass, so use both layers. SD_D0 takes a via under the module.
4. **Under U301's bottom edge** (pass 7). The SIM lines leave pins 11–14 downward on L1 to the network at y 60–73. The UART lines from pins 17, 18 and 22 and the right column (23–25) head left to U302 and would cross them. Drop the UART lines to L4 inside the 3 mm ring and run them under the module (L4 is allowed there; Quectel HD p. 17 rules out L1 copper and L2 tracks only). Keep the SIM on L1 over solid L2, so it needs no vias through the VMODEM strip below.
5. **Around BT201** (x 29–51, y 34–48). The slow cross-board nets pass round it on L4: LATCH_LOGIC 47 mm, SOLAR_ADC 77, BATT_ADC 53, TEMP_CLAMP 33, SYS I²C 45.
6. **L3.** The two pours stay as drawn in phase 4a; none of the pass 7 moves touches the rectangles in `phase4_planes.py` (U301, J302, the MCU corner, the VMODEM strip). L3 outside them (x 44–80 below y 57, and the band right of the VMODEM strip) can take the slow long nets: SOLAR_ADC, BATT_ADC, LATCH_LOGIC, TEMP_CLAMP.

Nets that must cross whatever the placement:

- the audio bundle and the USB pair (both leave the left column);
- the audio bundle and the SD bus (layer split);
- the bottom-row control nets and the right-column LTE nets;
- SD_D0 and the bottom-row nets.

Pass 7 removes the SIM nets' four crossings of the whole left half and the four wake nets' crossings of the centre. Long crossings per net fall sharply: PWR_HOLD 23 → 11, USB_WAKE 18 → 0, SIM_CLK_M 14 → 0, USIM_VDD 13 → 0, SIM_DATA_M 16 → 7, STATUS_LED 17 → 6. SD_D0 (21) and AUD_SDA/SCL (18–19) now lead.

## 3. The SIM (brief question 2)

Quectel EG810M-EU QuecOpen&QuecPython HD V1.0, p. 40, notes under Figures 17/18 (*measured*):

- USIM connector close to the module, trace as short as possible and at most 200 mm;
- USIM signals away from RF and power-supply traces;
- the 100 nF (≤ 1 µF) at the connector;
- USIM_DATA and USIM_CLK kept apart and surrounded by ground;
- a TVS array under 15 pF;
- 0 Ω links in series for debugging;
- the 33 pF capacitors and the peripheral circuit close to the connector;
- the data pull-up near the connector.

U301's SIM pins are at its bottom-left corner: pins 11–13 (DATA, RST, CLK) at (55.4, 78.9–81.1) and pin 14 (USIM_VDD) at (58.1, 77.45).

| Candidate | What moves | USIM spans: VDD / CLK_M / DATA_M / RST_M, mm | Cost |
|---|---|---|---|
| Pass 6: left edge | — | 58 / 45 / 42 / 40 | The nets cross the SD, RTC, TMP390 and converter areas |
| **Right edge below U301 (recommended)** | J301 to (71.675, 66.6, 90°), slot facing right, shell copper 0.5 mm inside the edge. The ten network parts and DNP C318–C320 re-fitted; SW201/SW202/LED401 slide 12–14 mm down; TP212 moves. **U301 and J302 stay** | **14 / 8 / 11 / 10.** Holder-side nets SIM_CLK/DATA/RST 8–11; C1 → pin 14 12.6 | Right box clearance 10 → 12 mm. The right edge now carries J302, J301, SW202, SW201 and J203 (R2-F8) |
| Top edge right of the notch, U301 turned 270° (alternative B) | U301 to (61.5, 78.4, 270°) with its VBAT array (now right of the module); J302 down to (77.4, 72.06); J301 to (52.7, 96.675, 180°), slot up; 44 parts evicted and re-fitted | 18 / 10 / 7 / 7 | The SIM card needs ≥ 12 mm beyond the top edge: +12 mm of box length on top of the 15 mm at the bottom. The phase 4a keep-outs under U301 and J302, the VMODEM strip and the RF feed must be redone. Gains over pass 7: modem UART 8–12 mm instead of 16–22, MODEM_EN 20 instead of 44 |
| Top edge, U301 at 0° moved down | U301 about 15 mm down, into U207's block | ≈ 24–28 (pins at the module's bottom, holder contacts at y 89.9; geometry only, not planned) | Displaces the modem-rail block; worse than both above |
| Left edge at the top, U401 moved right | U401 ≥ 15 mm right, notch widened, MH1 moved | ≈ 40–43 (geometry) | Does not fit: the top row (U401 19 mm, pogo row, U302, U301 with its ring 21.8 mm, J302) already uses ≈ 76 of 80 mm. No gain over today |

Pass 7 network (*measured*, to the holder contact):

| Part | Pass 7 | Pass 6 |
|---|---|---|
| C311 (33 pF, CLK) | 1.8 mm | 2.8 |
| C312 (33 pF, DATA) | 1.8 mm | 4.6 |
| C310 (33 pF, RST) | 2.2 mm | 3.9 |
| C313 (100 nF) | 3.7 mm | 2.0 |
| R309 (DATA pull-up) | 3.1 mm | 9.2 |
| D301 (TVS) | 5.9 mm | 4.2 |

R306–R308 sit between holder and module (7.8–10.6 mm to the module pins, 8.1–11.5 mm to the holder).

The network sits over the L3 VMODEM strip, with solid L2 between. Its nearest switching part is U207 (8.4 mm, R308); the RF feed parts R310/J302 are 16 mm away. On the right edge the holder's CLK contact C3 is the one farthest from the module: the CLK path runs 11.5 + 7.8 mm, past the DATA contact. Give CLK a ground guard on both sides (Quectel's DATA/CLK note) and keep it ≥ 2 mm from the VMODEM copper around C233 (*judgment*).

## 4. Findings, most severe first

### R2-F1. Should fix (measured): the SIM holder is 71 mm from U301, and its nets cross half the board

- **Parts:** J301 (8.33, 39.50, 270°), C310–C313, D301, R306–R309 (x 16–30, y 39–50); U301 pins 11–14 (55.4–58.1, 77.45–81.1).
- **What is wrong:** USIM_VDD spans 57.5 mm and SIM_CLK_M/DATA_M/RST_M 45 / 42 / 40 mm. On the way they cross the SD support parts, U205, the TMP390 cut-out, U206's VIN side and the VMODEM strip. That is inside Quectel's 200 mm, but against "close to the module" and "away from power-supply traces" (HD V1.0 p. 40).
- **Fix:** move the SIM to the right edge (section 3; move table rows 1–14). Spans become 14 / 8 / 11 / 10 mm.

### R2-F2. Should fix (measured): the wake-latch transistors sit with the switches, so four wake nets cross the board

- **Parts:** Q208 (69.1, 68.7) and Q209 (65.5, 69.5), placed with SW201/SW202 in pass 5; R245 and C237 (Q210's gate network) at (71.6, 64.3) and (70.8, 72.7).
- **Measured:** PWR_HOLD 60.6 mm (U401.18 → Q208), WAKE_N 51.6 (U205.3 → Q208/Q209), USB_WAKE 52.8 (R226 → Q209), LATCH_LOGIC 51.3. Q210_G is 17.5 mm from R245 and 23.8 mm from C237. WAKE_N and LATCH_LOGIC are ≈ 47 kΩ nodes while idle.
- **Rule:** keep high-impedance nodes short and put a transistor at its input; the outputs here are the ones that are driven (*judgment*). The owner moved the transistors in pass 5 for the switches' sake; the switches can stay at the edge without them.
- **Fix:**
  - Q209 → (23.29, 46.88, 270°): WAKE_N 6.2 mm to U205.3, USB_WAKE 4.5 mm to R226.
  - Q208 → (25.06, 60.04, 270°): WAKE_N 19.3, PWR_HOLD 24.8.
  - R245 → (60.55, 48.62, 90°), 1.7 mm from Q210's gate; C237 (not fitted) → (56.87, 55.20, 270°), 3.5 mm.
  - Q211, D206 and R246 stay at SW201: BTN_N, the 1 MΩ node, 2.2–7.4 mm.

  Result: PWR_HOLD / WAKE_N / USB_WAKE / LATCH_LOGIC 27 / 19 / 14 / 47 mm. LATCH_LOGIC (R227 at the RTC → SW202) is the one long latch net left. BTN_SENSE (52 mm, low impedance when Q211 is on) and STATUS_LED (57 mm, LED drive) stay long by nature.

### R2-F3. Should fix (measured, judgment on the noise): the charger's switch node sits beside the audio while the corner is empty

- **Parts:** Q202 (46.5, 30.1), D203, D204, L201 (61.5, 26.3), U201 (54.6, 33.1) and their passives. Nearest audio parts: C125 and Q101/Q102 (AVDD_PRE, x 32–36, y 19–27); U103 at x 29–34.
- **Measured:**
  - Q202 is 10.1 mm from C125 and 16.4 mm from U103, and U201 is 1.3 mm from BT201.
  - x 65–80, y 8–30 holds only TP204.
  - The charger runs whenever the panel is lit, i.e. during daytime recordings. U207 is off during recordings (firmware rule), and both converters are ≥ 29 mm from every audio part.
- **Rule:** audio README rule 4 (MIC1_OUT away from switching loops) and the G2 noise test. The CN3791 notes (Rev 1.0 p. 9) cover the loop itself, which a rigid move keeps.
- **Fix:** shift the 26-part charger group by +10.00 / −4.00 mm with angles unchanged (rows 30–54). The pass 4 loop is kept exactly: C203 4.8 mm and C202 6.9 mm from Q202's source; R202 3.7 mm from U201 pins 7/8; D204 6.2 mm from L201.
  - Audio ↔ charger switch: 18.4 mm (was 10.1); U102/U103: 22.3 (was 16.4); BT201: 11.3 (was 1.3).
  - Costs: R202 is 3.9 mm from F202 (was 5.9); C207 2.8 mm from J203 (was 4.9); MPPT handled in R2-F4.
  - Shifts of +6 to +10 mm and −1 to −6 mm were scanned. +10 / −4 is the largest that disturbs no fitted part outside the group; −5 and −6 push the panel TVS D201 out.

### R2-F4. Should fix (measured): the MPPT feedback node runs 40 mm to the TMP390 clamp

- **Parts:** Q204 (MMBT3904, collector on MPPT) at (25.0, 59.9) beside U203; U201 pin 6 (MPPT); R204/R205 (402 k / 100 k, ≈ 80 kΩ at the node).
- **What is wrong:** MPPT is the CN3791's high-impedance regulation input. Any pickup on its 40 mm run (50 mm after R2-F3 without this fix) moves the panel set point. TEMP_CLAMP, which drives Q204's base, is held low by Q203 whenever the temperature is in range: a low-impedance node.
- **Fix:** Q204 → (47.87, 31.27, 180°), at the divider. MPPT becomes 17.7 mm and TEMP_CLAMP becomes the long net (33 mm). No schematic change.

### R2-F5. Minor (measured): R203 is 0.14 mm from L201's body outline

The owner's hand move after pass 6 put R203 (CN_COM/CN_COMRC) at (58.07, 30.60, 90°). Its pad box is 0.14 mm from the 6 × 6 mm inductor's outline, below the 0.7 mm rule (pick-and-place and rework). Fix with the planner's margins: R203 → (68.51, 27.69, 90°) inside the shifted group. It is 2.6 mm to U201.5 (was 1.6) and 3.0 mm to C206; the compensation network stays local.

### R2-F6. Note (judgment): the audio bus is 59–66 mm by geometry; route it, don't move it

AUD_BCK/LRCK/DOUT 61–64 mm, AUD_SDA/SCL 66, the enables 59–63. These are set by U401 at the top and J101 at the bottom (2.4). Route them as the L4 bundle down the left strip with GND on L2 above. Cross the SD and USB nets at right angles. Bring them back to L1 near R103–R105 (3.6–5.8 mm from U102's I²S pins). Keep MCLK (pin 17, bottom row) in the bundle.

### R2-F7. Note (measured): SOLAR_ADC 77 mm and BATT_ADC 53 mm

Both dividers sit at their sources, both are filtered there (C235 on SOLAR_SENSE, C213 on BATT_SENSE), and both drive the ADC pins through 2.2 kΩ. The long trace carries a filtered, 2.2 kΩ-driven DC level. Both ends are fixed by function (U401 pins 38/39, the panel input, Q210), so moving the dividers would only change which net is long. Route on L4 or L3 away from SD_CLK and AUD_BCK, and check the reading noise in power test 10.

### R2-F8. Note (judgment): the right edge gets crowded with lid-off items

From the top: J302 (u.FL cable, y 90–93), J301 (y 60–73, card ejecting right), SW202 (y 50–58, knob toward the edge), SW201 (y 45–49), J203 (y 36–44, battery plug from the right). The box/plate needs ≥ 12 mm beyond the right edge, up from 10. The left edge loses its SIM requirement: J401 and J402 are used from above, so the left clearance is whatever the plate needs. The LTE FPC antenna on the right wall must not sit in the SIM's ejection path at the board's height (question 6).

### R2-F9. Note (measured): the UART filter footprints move 0.2–1.7 mm away from the pins

C318–C320 (33 pF, not fitted) re-fit just below U301's ring at 5.0 / 7.1 / 6.0 mm from pins 17 / 18 / 22 (pass 6: 4.8 / 5.4 / 4.4), because the SIM network now uses the space. They are only for EMC fixes (QuecOpen Ref V1.2 sheet 3 note 9).

### R2-F10. Note (measured): U202's polygon tab clips its neighbours

R213 overlaps U202's box (0.17 mm, same net, known). TP214 is 0.36 mm and R209 0.65 mm from it. The box is the HT7533's tab polygon, which is conservative. Untouched by pass 7; DRC decides.

### R2-F11. Note (measured): the antennas and isolation do not change

- ESP32 antenna strip ↔ J302: 53 mm (alternative B: 58).
- ESP32 antenna ↔ nearest converter (U206): 24 mm.
- J302 ↔ nearest converter (U207): 36 mm.
- U301's ring is empty, and the feed U301.35 → R310 → J302 is unchanged.
- Nothing new within 10 mm of the antenna strip: C401 3.9, C402 2.2, C403 7.9, TP414 8.4, TP415 6.1, as in pass 6.
- The charger moves 10 mm toward the right wall. With the FPC antenna in the upper half of the wall, near J302, it stays ≥ 55 mm from it.
- The ≥ 20 dB isolation between the radios still has to be measured in the box.

## 5. Move table for pass 7

Tested together with `check()` on the whole board (`/tmp/auris-review2/pass7.py`):

- 0 new overlaps; the only overlap is the known R213/U202 polygon extent.
- Every part inside the outline; no pad copper within 0.45 mm of an edge; nothing in a hole keep-out; nothing within 3 mm of U301.
- Parts within 10 mm of the antenna strip unchanged.
- Gap to the nearest part: 10th percentile 0.71 mm, median 0.77.
- All 43 note targets as in pass 6, except Q202 → Q201, which goes from 14.7 to 16.4 mm (the input caps C202/C203 carry the loop).

`/tmp/auris-review2/placement-pass7-moves.csv` is in `apply_moves.py`'s format (designator, x_mm, y_mm, angle) and can be copied to `hardware/layout/placement-pass7-moves.csv` in stage 2.

| # | Part | From (x, y, °) | To (x, y, °) | Result |
|---|---|---|---|---|
| 1 | J301 | 8.33, 39.50, 270 | 71.67, 66.60, 90 | Slot at the right edge, shell copper 0.5 mm in; C1 (USIM_VDD) 12.6 mm from U301.14 |
| 2 | C311 | 17.25, 42.06, 0 | 63.16, 61.90, 90 | 1.8 mm to J301.C3 (pass 6: 2.8) |
| 3 | C312 | 16.56, 47.88, 90 | 63.15, 64.01, 90 | 1.8 mm to J301.C7 (pass 6: 4.6) |
| 4 | C310 | 19.35, 42.36, 0 | 63.18, 66.13, 90 | 2.2 mm to J301.C2 (pass 6: 3.9) |
| 5 | C313 | 17.00, 39.20, 90 | 62.70, 70.25, 90 | 3.7 mm to J301.C1 (pass 6: 2.0) |
| 6 | D301 | 19.43, 45.70, 90 | 59.66, 68.17, 270 | 5.9 mm to J301.C1 (pass 6: 4.2) |
| 7 | R309 | 22.23, 49.35, 0 | 61.86, 63.91, 90 | 3.1 mm to J301.C7 (pass 6: 9.2) |
| 8 | R307 | 23.98, 45.91, 180 | 58.66, 71.66, 0 | 7.8 mm to U301.13, 11.5 mm to J301.C3 |
| 9 | R308 | 27.54, 49.17, 180 | 56.76, 70.11, 270 | 10.6 mm to U301.11, 10.5 mm to J301.C7 |
| 10 | R306 | 29.79, 49.38, 180 | 60.96, 71.63, 0 | 9.8 mm to U301.12, 8.1 mm to J301.C2 |
| 11 | C318 (DNP) | 63.64, 72.98, 0 | 58.90, 72.91, 180 | 5.0 mm to U301.17 (pass 6: 4.8) |
| 12 | C319 (DNP) | 65.38, 72.47, 270 | 56.97, 72.55, 270 | 7.1 mm to U301.18 (pass 6: 5.4) |
| 13 | C320 (DNP) | 67.71, 73.02, 0 | 62.87, 72.61, 270 | 6.0 mm to U301.22 (pass 6: 4.4) |
| 14 | TP212 | 62.00, 63.00, 0 | 43.60, 69.07, 0 | VMODEM test pad, 2.9 mm to C227.1 |
| 15 | SW202 | 76.00, 68.00, 90 | 76.00, 54.20, 90 | Knob still toward the edge; 1.4 mm below J301's shell pads |
| 16 | SW201 | 76.00, 59.00, 0 | 76.00, 47.00, 0 | Pressed from above; 1.3 mm above J203's body |
| 17 | LED401 | 70.50, 55.00, 0 | 70.80, 51.20, 90 | Beside SW201/SW202, seen from above |
| 18 | R416 | 70.50, 52.60, 0 | 66.17, 56.31, 0 | 5.8 mm to LED401.1 |
| 19 | Q211 | 69.07, 64.91, 0 | 66.92, 53.36, 0 | BTN_N (1 MΩ node) 7.4 mm to SW201.1 |
| 20 | D206 | 71.00, 61.00, 90 | 71.43, 46.98, 90 | BTN_N 3.4 mm to SW201.1 |
| 21 | R246 | 71.32, 58.32, 0 | 72.57, 50.20, 90 | BTN_N 2.2 mm to SW201.1 |
| 22 | R228 | 71.57, 70.25, 90 | 64.91, 40.92, 90 | SYS_GATE pull-up beside Q205's RAW_BAT; 17.3 mm to SW202.2 |
| 23 | R245 | 71.57, 64.25, 90 | 60.55, 48.62, 90 | Q210_G 1.7 mm to Q210.1 (pass 6: 17.5) |
| 24 | C237 (DNP) | 70.78, 72.74, 0 | 56.87, 55.20, 270 | Soft-start option, 3.5 mm to Q210.3 (pass 6: 23.8) |
| 25 | Q208 | 69.12, 68.65, 90 | 25.06, 60.04, 270 | WAKE_N 19.3 mm to U205.3; PWR_HOLD 24.8 mm to U401.18 (pass 6: 51.6 / 60.6) |
| 26 | Q209 | 65.46, 69.50, 0 | 23.29, 46.88, 270 | WAKE_N 6.2 mm to U205.3; USB_WAKE 4.5 mm to R226.1 (pass 6: 48.6 / 52.8) |
| 27 | Q204 | 25.02, 59.89, 270 | 47.87, 31.27, 180 | MPPT 17.7 mm to U201.6 (pass 6: 40.3); TEMP_CLAMP becomes the long net |
| 28 | R146 (DNP) | 49.11, 29.66, 90 | 37.51, 30.59, 180 | Parked in the space the charger leaves |
| 29 | R147 (DNP) | 50.46, 29.79, 90 | 37.30, 32.12, 180 | Parked in the space the charger leaves |
| 30 | U201 | 54.60, 33.10, 0 | 64.60, 29.10, 0 | Charger group; R202 3.7 mm to pins 7/8; 11.3 mm from BT201 (pass 6: 1.3) |
| 31 | L201 | 61.48, 26.27, 270 | 71.48, 22.27, 270 | Charger group, rigid shift +10.00 / −4.00 mm |
| 32 | Q202 | 46.46, 30.10, 0 | 56.46, 26.10, 0 | Charger group; C203 4.8 / C202 6.9 mm to its source (as pass 4) |
| 33 | D203 | 53.40, 26.88, 0 | 63.40, 22.88, 0 | Charger group, rigid shift |
| 34 | D204 | 55.35, 22.95, 90 | 65.35, 18.95, 90 | Charger group, rigid shift |
| 35 | R202 | 59.20, 35.37, 270 | 69.20, 31.37, 270 | Charger group, rigid shift; 3.9 mm from F202 (pass 6: 5.9) |
| 36 | C202 | 49.22, 24.17, 0 | 59.22, 20.17, 0 | Charger group, rigid shift |
| 37 | C203 | 48.30, 26.23, 0 | 58.30, 22.23, 0 | Charger group, rigid shift |
| 38 | C205 | 50.12, 32.47, 0 | 60.12, 28.47, 0 | Charger group, rigid shift |
| 39 | C206 | 57.45, 27.98, 90 | 67.45, 23.98, 90 | Charger group, rigid shift |
| 40 | C207 | 63.04, 33.99, 270 | 73.04, 29.99, 270 | Charger group, rigid shift; 2.8 mm from J203's body (pass 6: 4.9) |
| 41 | C208 | 67.05, 35.61, 0 | 77.05, 31.61, 0 | Charger group, rigid shift |
| 42 | C209 | 67.60, 33.90, 0 | 77.60, 29.90, 0 | Charger group, rigid shift |
| 43 | C210 | 66.50, 32.06, 270 | 76.50, 28.06, 270 | Charger group, rigid shift |
| 44 | R204 | 47.72, 32.60, 0 | 57.72, 28.60, 0 | Charger group, rigid shift |
| 45 | R205 | 39.45, 32.53, 180 | 49.45, 28.53, 180 | Charger group, rigid shift |
| 46 | R206 | 49.61, 27.91, 180 | 59.61, 23.91, 180 | Charger group, rigid shift |
| 47 | R207 | 45.52, 32.67, 180 | 55.52, 28.67, 180 | Charger group, rigid shift |
| 48 | LED201 | 37.61, 31.71, 90 | 47.61, 27.71, 90 | Charger group, rigid shift |
| 49 | LED202 | 42.49, 31.39, 0 | 52.49, 27.39, 0 | Charger group, rigid shift |
| 50 | TP203 | 52.83, 24.52, 0 | 62.83, 20.52, 0 | Charger group, rigid shift |
| 51 | TP204 | 65.90, 28.61, 0 | 75.90, 24.61, 0 | Charger group, rigid shift |
| 52 | TP206 | 68.52, 32.03, 0 | 78.52, 28.02, 0 | Charger group, rigid shift |
| 53 | TP202 | 39.44, 30.66, 0 | 49.44, 26.66, 0 | Charger group, rigid shift |
| 54 | TP213 | 43.15, 29.20, 0 | 53.15, 25.20, 0 | Charger group, rigid shift |
| 55 | R203 | 58.07, 30.60, 90 | 68.51, 27.69, 90 | Off L201's body (pass 6: 0.14 mm gap); 2.6 mm to U201.5, 3.0 mm to C206 |

Before pass 7 reaches EasyEDA, the owner should check:

- the right edge in the picture (J301 against SW202, SW201 against J203);
- the charger corner (C207 and C208–C210 by J203, the PH plug's finger room);
- the SIM network's spot above C233 and U207's VOUT copper.

What pass 7 does not need:

- No L3 pour or keep-out region changes: the 4a rectangles are tied to U301, J302, the MCU corner and the VMODEM strip, and none of them moves.
- No new box clearances beyond the right edge's 12 mm.

`place.py` should get these anchors and regions in stage 2, so that a re-plan reproduces the arrangement:

- J301, SW201, SW202, LED401 anchors;
- `l_sim` (54, 56, 80, 74);
- `p_latch` and `m_led` as above;
- `p_charger` shifted;
- `l_supply` above U301, which pass 4 never wrote back (2.3).

## 6. What stays, and why

- **Decoupling at the pin**, from pass 4 (unchanged, *measured*):
  - C402/C401 2.4 / 4.3 mm from U401 pin 2, C403 5.3 mm from pin 3;
  - C222/C223 2.6 / 3.5 mm from U206 VIN, C225/C224 2.3 / 3.8 mm on its output;
  - U207's C228/C229 2.0 / 1.9 mm and C219 4.7 mm from VIN;
  - C216 2.3 mm from U205 pin 2;
  - U102's C103–C110 at 2.4–4.8 mm.
- **Both converters' switching loops:** L203 3.9 mm from U207's L pins, L202 2.4 mm from U206's. Untouched.
- **The charger's input loop:** C203/C202 4.8 / 6.9 mm from Q202's source, R202 3.7 mm from U201 pins 7/8. Moved as one rigid group, so the geometry is identical.
- **The modem's VBAT array above U301** (C306 4.5 mm … R301 7.7 mm from pads 42/43) and the empty 3 mm ring. A full re-plan would lose this (2.3).
- **The SIM filter at the holder:** kept, and closer than in pass 6 for C310–C312 and R309.
- **The preamp input network beside U102:** R124 3.3 mm from pin 30, the U104/C140/C123/R125 cluster, R103–R105 3.6–5.8 mm from the I²S pins. Untouched.
- **The RF feed** U301.35 → R310 → J302 (4.7 + 3.2 mm, straight) and J302's L2 cut. Untouched.
- **U401's corner, orientation and notch; the pogo row at x = 26; BT201 in the centre; U203 over the pack:** owner decisions; none of them is the cause of the long nets.
- **U301 at 0°:** turning it (alternative B) only pays if the SIM goes on the top edge, which costs box length.
- **J401 and J402 in the left column:** both sit next to their pin groups.

## 7. Questions for the owner

1. **Pass 7 scope.**
   - (a) **The full move table, 55 parts (recommended).**
   - (b) SIM, service cluster and latch only (rows 1–26, 26 parts); leave the charger, Q204 and R203.
   - (c) Alternative B instead: U301 turned, SIM on the top edge, box +12 mm.
   - (d) SIM only (rows 1–17).
2. **Latch transistors.**
   - (a) **Q208/Q209 at the RTC and USB divider, R245/C237 at Q210 (recommended);**
   - (b) keep them with the switches, as decided in pass 5 (PWR_HOLD, WAKE_N and USB_WAKE stay at 51–61 mm).
3. **Charger shift.**
   - (a) **+10 / −4 mm into the bottom-right corner (recommended);**
   - (b) a smaller +8 / −4 (audio gap 16.5 mm; F202 and J203 a little farther from the charger);
   - (c) leave it.
4. **Q204 to the charger** (MPPT 40 → 18 mm):
   - (a) **yes (recommended);**
   - (b) keep it beside U203.
5. **R203:**
   - (a) **take (68.51, 27.69, 90°) (recommended);**
   - (b) the owner places it by hand with ≥ 0.7 mm to L201.
6. **Right wall and plate.**
   - (a) **Right clearance 12 mm, the FPC antenna in the upper half of the right wall (near J302, clear of the SIM card at the board's height between y 60 and 73), left clearance only what the plate needs (recommended);**
   - (b) another antenna position: say where, so the SIM ejection path can be checked.
7. **Routing plan for the audio bus.**
   - (a) **L4 bundle down the left strip, SD and USB on L1 (recommended);**
   - (b) the owner prefers another split.

## Appendix: files

All under `/tmp/auris-review2/`, not in the repo:

| File | What it is |
|---|---|
| `common.py`, `metrics.py` | Board loading; spans, MST, crossings, separations, 3 A path |
| `place_r2.py` | Planner copy with the repo path fixed |
| `refit.py` | Evict and re-fit, then `check()` |
| `pass7.py` | The proposed pass 7 → `pass7.json`, `pass7.png`, `placement-pass7-moves.csv` |
| `altA.py`, `altA2.py`, `shift_scan.py` | SIM-only and charger-shift experiments |
| `altB.py` | Alternative B → `altB.json` / `.png` |
| `fullplan.py` | Full re-plans `control` / `planA` / `planB` (`.json` / `.png`) |
| `table.py`, `cmp.py` | The tables in 2.3 |
| `movetable.py` | The table in section 5 |
| `blockpic.py` | `blocks-compare.png`, `blocks-planner.png` |
| `quectel.txt` | Text of the Quectel HD V1.0 (USIM notes p. 40) |
