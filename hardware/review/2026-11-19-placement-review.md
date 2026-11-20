# Placement review: rev A, pass 3 (2026-11-19)

**Outcome (2026-11-20):** applied as placement pass 4 (65 parts moved, all the F1–F6, F8–F10 and F12 moves plus the hand-placed U104/C140/C123/R125 cluster and TP203; export `hardware/2026-11-20/AURIS_2026-11-20_place4.epro2`, every check passes; record in `hardware/layout/README.md`). The owner answered section 5 on 2026-11-20 (record in `hardware/layout/README.md`, *Owner decisions*): keep the ESP32 corner, the 3 mm ring, the 80 × 105 outline and all test pads; U203 gets a bottom copper pad through the plate; rule 7 (shield can) dropped for rev A; BT201 is the top-entry Node v4 holder; SW202 stays (F14's 1 mm is to the flat solder tab, the holder body is 7.5 mm away at the knob's height); J201/J202 keep the footprint's wire-entry side (confirmed from the DB301V drawing); docs updated (ADR-028).

Independent review of `hardware/2026-11-19/AURIS_2026-11-19_place3.epro2` (346 parts, 187 nets) against the rules in `hardware/review/handover-rev-a-pcb-layout.md` (Phase 3), the audio README's *Layout rules*, and the makers' datasheets in `hardware/datasheets/pdf/`. Brief: `hardware/review/handover-placement-review.md`. Nothing in EasyEDA, the sheet CSVs or the scripts was changed; `place.py --check` re-rendered `placement-pass3.png` (same picture). My measurement scripts, the datasheet figure pages and the size-experiment pictures are under `/tmp/auris-review/` (not kept in the repo).

Every distance below is pad centre to pad centre on the shared net, computed with `pcb_board.py` from the export. *Measured* = computed from the export or read from a datasheet; *judgment* = my assessment.

## 1. Verdict

**Not ready to route; one more placement pass (pass 4) is needed.** Two items would cement datasheet violations on the two highest-current nodes of the board if routed as placed: the modem's VBAT capacitor array sits 20–26 mm from U301's VBAT pads, and U207's inductor sits on the opposite side of the chip from its switch pins. Five more should-fix items (U206's input capacitor, the charger's input loop, the RTC decoupling, the ESP32's 3V3 decoupling, the preamp-path ADC input pair) are each a handful of parts. Every proposed move below was tested against the planner's own margins and keep-outs (section 3, appendix); together they are a few hours of work, not a re-layout. The arrangement itself (blocks, edges, antenna in the notch, service access) is sound and can stay.

## 2. Board size

### 2.1 Starting numbers (checked)

| Item | Handover | Measured from the export |
|---|---|---|
| Parts, body + pads | ≈ 3,220 mm² (39 %) | 3,218 mm², 39 % of 8,190 mm² |
| Unfitted parts | ≈ 180 mm², mic-2 148 | 178 mm² (45 parts), mic-2 block 148 mm² (27 parts) |
| Test pads | ≈ 55 mm² | 54 mm² (54 × 1.0 mm) |
| Largest footprints | U401 495, BT201 313, U301 280, J402 210, J301 208 | same (then J203 77, C219/C233/C201 58 each, U102 58, J201/J202 56 each) |
| Fixed costs | notch, 4 holes, U301 ring, antenna clearance | notch 210 mm²; hole keep-outs 4 × 52 = 207 mm²; U301's 3 mm ring adds 237 mm² (517 mm² with the module); the planner's antenna keep-out 58 mm² |
| Occupancy including the planner's margins (0.35 mm passives, 0.5 mm connectors, 0.8 mm ICs) | — | 59 % of the board; the right-hand 10 mm column and the rows y 60–70 and y 90–105 are under 50 % |

### 2.2 The smallest outline I would route now

**76 × 100 mm (7,390 mm² after the notch, −10 %)**, same arrangement, notch at x 0–35 / y 94–100, holes at (4, 4), (72, 4), (40, 96), (72, 96), U301 and J302 keeping their offsets from the top-right corner, the left-edge stack (U401, J401, J402, J301) keeping its order.

Evidence (*measured*): I re-ran the planner (`place.py`'s `plan()`, with its anchors, regions and margins scaled to the new outline; nothing written to the repo) at five sizes:

| Outline | Result |
|---|---|
| 80 × 105 (control) | reproduces pass 3: every check passes, 39 % |
| **76 × 100** | **every check passes, 44 % coverage, same two parts outside their block regions as in pass 3 (C219, SW201)**; picture `/tmp/auris-review/size_76x100.png` |
| 72 × 96 | fits only with J401 moved off the left column (next to the SD parts) and 25 parts pushed out of their blocks (the USB ESD/CC parts, U205, SW201/SW202, the whole mic-2 chain, the audio test pads); min gap 0.56 mm; 48 % |
| 70 × 92 | no room (fails at C130) |
| 68 × 90 | no room (fails at TP104) |

The greedy planner is not an optimal packer, so 72 × 96 is probably reachable by hand, but not "with confidence" under the owner's spacing rules (≥ 0.7 mm between parts, ≈ 1.6 mm around ICs).

### 2.3 What sets the limit

1. **Height: the left-edge stack.** Audio block (y 0–32) + J301 (13.7 mm + gaps) + J402 (15.2) + J401 (9.8) + U401 (26.0, antenna in the notch) = 97 mm plus gaps. Nothing else on the board needs more than ≈ 85 mm of height. Only J401 (a vertical receptacle, no edge needed) can leave the column cheaply; the SIM needs an edge, the SD lid needs lid-off access only.
2. **Width: the top row and the power column.** Top row: U401 (19) + pogo/EN parts (8) + U302 and the LTE control parts (17) + U301 with its 3 mm ring (21.8) + J302 (4) + edge margins ≈ 76 mm. Right-hand power column (J203, F202, Q205, U204, the charger) is 28 mm wide beside BT201 (21.7) and U205/the SIM parts.
3. **Area: the spacing rules** more than the parts. 3,218 mm² of parts at 59 % occupancy with margins; at 76 × 100 the same rules give ≈ 65 %, which is where this kind of board usually lands.

### 2.4 Further steps, each on its own

Savings are board area at the pass-3 density (about 2 mm² of board per mm² of parts); part or schematic changes need the owner's approval and a change-log row.

| Option | Saving | Cost |
|---|---|---|
| **a. Drop the second-mic footprints** (27 unfitted parts, 148 mm²) | ≈ 300 mm²; the audio block loses ≈ 4 mm of height → 76 × 96 | No stereo/hydrophone option on rev A; schematic change (the parts are already DNP) |
| **b. Smaller RTC backup** (BT201 CR1220-2, 313 mm², the largest part after the two modules) | (i) no backup cell at all: ≈ 350 mm² (≈ 6 mm of the centre column); (ii) a 6.8 mm rechargeable MS621FE/ML621 with a diode + resistor from KEEP_ALIVE: ≈ 320 mm²; (iii) a smaller CR1220 retainer clip (≈ 14 × 16 mm): ≈ 100 mm² | (i) after a full depletion the clock is lost until the next LTE sync (F2-04 `time_unknown`; on a site without coverage, until the service visit); (ii) schematic change (the DS3231M has no trickle charger) and a −20…+60 °C cell, worse than the BR1220's −30…+80 °C for European winters; (iii) new part, polarity/drawing check |
| **c. Embedded SIM (MFF2, 6 × 5 mm) instead of J301** (208 mm² + 7 filter/ESD parts ≈ 20 mm²) | ≈ 200 mm², and the SIM leaves the left column (−14 mm of column height) and frees the 12 mm ejection clearance beyond the left edge | Provisioning (operator eSIM profiles, or a soldered removable-profile SIM), rev B part; bonus: −40…+105 °C instead of −35…+75 °C |
| **d. Fewer or smaller test pads** (54 × 1.0 mm = 54 mm², ≈ 160 mm² with probe clearance) | dropping ≈ 20 debug pads ≈ 60 mm²; the 7 DNP RF-filter footprints C317–C323 ≈ 20 mm²; 0.8 mm pads ≈ 20 mm² | Less bring-up access; keep the pogo row, the rails, the TMP390 trip pads, the modem USB/boot pads |
| **e. Parts on the bottom side** (≈ 240 passives and small parts, ≈ 820 mm² of parts, ≈ 1,900 mm² of board) | top side down to ≈ 2,400 mm² of parts → ≈ 60 × 85 mm (−38 %) | Two-sided assembly at JLC (setup and second stencil, the cans stay on top), taller standoffs over the pack (parts under the board), coating both sides; reverses the "all parts top" decision |
| **f. ESP32 corner / orientation** (see finding 7) | rotating U401 90° CCW at the top-left (antenna beyond the left edge, feed at the corner) removes the notch: +210 mm² of usable board at the same outline, and shortens the audio (65 → ≈ 40 mm) and SD runs | Re-place ≈ 30 parts at the top-left, move MH1; the box must leave ≥ 21 mm between the left board edge and the wall (6 mm overhang + Espressif's 15 mm) |
| **g. U301's ring 3 → 1.5 mm** | 128 mm² | Quectel's note gives the 3 mm for "soldering quality and maintenance convenience" (HD V1.0 p. 67), so this is a rework-access trade |

Combining a + c + d (no schematic cost beyond the SIM) brings the left column to ≈ 80 mm and makes ≈ 72 × 92 realistic; e is the only step that reaches ≈ 60 × 85.

### 2.5 The box and the pack

The pack (≈ 40 × 70 × 20 mm) under the board: a 76 × 100 board centred over it leaves 18 mm (x) and 15 mm (y) of board beyond the pack on every side; 72 × 96 leaves 16 and 13 mm; even 60 × 85 still covers it. No overhang in any option above. Clearances the box must give around the board, lid-off: ≥ 12 mm beyond the left edge for the ejected nano-SIM (the card stands out ≈ 3 mm after the push and is 8.8 mm deep), ≥ 15 mm beyond the bottom edge for the JST GH mic plug and the panel wires into J201/J202, ≥ 10 mm beyond the right edge for the JST PH battery plug. A 110 × 110 mm interior (Hammond 1554P, assumed, its drawing was never read) gives 15–17 mm around a 76 mm board. Option f needs 21 mm on the left, so the board would sit 6 mm off-centre or be ≤ 74 mm wide.

## 3. Findings, most severe first

Datasheet pages: Quectel EG810M-EU QuecOpen&QuecPython HD V1.0 ("Quectel HD"), TI SLVS916I (TPS63020), TI SLVSEU9D (TPS63802), Consonance CN3791 Rev 1.0, TI SLAS831D (PCM186x), Espressif ESP32-S3 Hardware Design Guidelines ("Espressif HDG") and ESP32-S3-WROOM-1 datasheet v1.8. Coordinates are part centres in mm, board frame, angle counter-clockwise. Every "Fix" was placed with the planner's own margins and keep-outs and passed `place.check()` (0 overlaps, inside the outline, no pad copper within 0.45 mm of an edge, nothing in a hole keep-out, nothing within 3 mm of U301); see the appendix.

### F1. Blocker (measured): the modem's VBAT capacitor array is 20–26 mm from U301's VBAT pads

- **Parts:** C301 (100 µF polymer), C302 (100 nF), C303 (33 pF), C304 (10 pF), C305 (3.9 pF), C306 (1.8 pF), R301 (0 Ω link). Now at x 44–51, y 71–76 (the `l_supply` region below the module).
- **Measured:** U301 pads 42/43 (VBAT_M) are on the module's top row at (59.2–60.3, 93.55). C306 is 25.9 mm away, C305 25.1, C304 24.0, C303 23.4, C302 22.4, C301 19.8.
- **Rule:** Quectel HD §3.4.4 p. 28: the MLCC array and the 0 Ω resistor "place these capacitors close to VBAT pins"; the BOM note says "smallest value closest to the pins". The pF caps are RF decoupling and do nothing 25 mm away; the 100 µF with ESR ≤ 0.7 Ω is what carries the 2 A transmit bursts.
- **Fix (tested):** move the array into the strip above the module (between the module's 3 mm ring and the top edge, left of MH2's keep-out): C306 (59.70, 98.00, 0°) 4.5 mm from pad 42/43; C305 (61.85, 98.00, 0°) 4.6; C304 (57.62, 98.18, 0°) 5.0; C303 (63.44, 99.25, 0°) 6.3; C302 (55.47, 98.25, 0°) 6.3; C301 (59.70, 100.40, 0°) 6.9; R301 (54.80, 100.40, 0°) 7.7 mm. R301 stays reachable for the current measurement. VMODEM then runs from U207's VOUT (47.7, 63.9) to R301 at (53.8, 100.4), ≈ 37 mm: do it as an L3 pour ≥ 4 mm wide (0.5 oz inner copper needs 7 mm for 3 A continuous; the peaks are short) with ≥ 4 vias at each end, straight under the module (Quectel forbids L1 copper under the module, not L3 under a solid L2). If the owner relaxes the 3 mm ring to ≈ 1 mm for 0402s (the ring is a rework note, finding 2.4 g), the pF caps can sit at ≈ 2 mm.

### F2. Blocker (measured): L203 sits on the wrong side of U207

- **Parts:** U207 (TPS63020) at (47.73, 62.40, 180°); L203 (1.5 µH) at (53.24, 62.40, 90°).
- **Measured:** U207's switch pins L1 (pads 8/9) and L2 (pads 6/7) are on its left side at x 46.2–46.7; L203's pads are at x 53.24, 6.3 mm away on the right, so both switching nodes (M_L1, M_L2, 3–4 A peaks at 2.4 MHz) would have to run around the chip past the VIN/VOUT capacitors.
- **Rule:** TI SLVS916I §10.1 p. 23 and Fig. 31: "Place the input capacitor, output capacitor, and the inductor as close as possible to the IC"; the inductor sits directly on the L1/L2 pins in TI's layout.
- **Fix (tested):** L203 → (42.37, 62.77, 90°): its M_L1 pad 3.9 mm from pads 8/9, M_L2 pad 3.9 mm from pads 6/7. To make room: TP210 → (41.30, 57.30), C220 → (43.30, 58.34, 90°) (5.2 mm from VIN, was 3.5). Use the freed right side for the bulk capacitors, which are also on the wrong sides today: C233 (470 µF VMODEM) sits below the chip while VOUT (pads 4/5) is on the top row, and C219 (470 µF VBAT_SW) sits 8.5 mm to the left while VIN (pads 10/11) is on the bottom row. Swap them: C219 → (47.98, 53.55, 270°) (its VBAT_SW pad 4.7 mm from pads 10/11), C233 → (56.20, 61.80, 0°) (≈ 6 mm from pads 4/5; 0.7 mm from C219's corner), with the unfitted D205 → (61.50, 55.50, 0°) and TP212 → (62.00, 63.00).

### F3. Should fix (measured): the charger's input loop is ≈ 47 mm round

- **Parts:** C203 (10 µF, "beside Q202/D204 switching loop") at (38.77, 15.34); C202 (4.7 µF) at (44.82, 13.35); C201 (47 µF bulk) at (49.55, 15.17); Q202 at (46.46, 30.10); D203 (53.40, 26.88); D204 (55.35, 22.95); L201 (61.48, 26.27); R202 (59.20, 35.37); U201 (54.60, 33.10).
- **Measured:** C203's SOLAR_IN pad to Q202's source (pad 2): 19.3 mm; C202 18.6 mm; C201 14.6 mm. Loop C203(+) → Q202 → D203 → D204 → C203(−): ≈ 19 + 7 + 2 + 17 ≈ 47 mm. The planner put all three input capacitors in the `p_solar` region (y < 20) with the TVS and the reverse-polarity FET, 15–20 mm from the switch. D203/D204 are 6–8 mm from L201 (fine); R202 is 3.6–4.6 mm from U201 pins 7/8 (Kelvin routing is possible); C207 is 3.8 mm from R202 (fine).
- **Rule:** CN3791 Rev 1.0 p. 9, PCB notes (1)–(4): the input filter capacitor's positive terminal close to the P-FET's source; the diodes and the sense resistor close to the inductor; the output capacitor close to the sense resistor; all those leads as short as possible. Note (5): the chip's GND and the compensation network's ground to system ground separately from the power ground.
- **Fix (tested):** C203 → (48.30, 26.23, 0°) (4.8 mm from Q202's source, 7.8 mm from D204's anode), C202 → (49.22, 24.17, 0°) (6.9 mm), LED201 (bring-up only) → (37.61, 31.71, 90°) to make room. Loop ≈ 24 mm. C201 (6.3 mm can) can stay where it is as the bulk. For the ≈ 1 cm² of switch-node copper the BOM asks for under D203/D204: the window x 50–64, y 19–30 has only ≈ 60 mm² free; move TP203 (53.34, 24.57) out of it and pour CHG_SW from D203's cathode over D204 to L201's pad 2 (judgment: the switch node radiates, so take the copper the cathodes need and no more).

### F4. Should fix (measured): U206's input capacitors are 7.6–9.3 mm from VIN

- **Parts:** U206 (TPS63802) at (34.14, 76.23, 270°), VIN pad 10 at (35.14, 75.40); C222 (22 µF "At U206 VIN") at (41.74, 68.11); C223 (100 nF) at (40.27, 69.43).
- **Measured:** C222 9.3 mm, C223 7.6 mm. The output side is fine (C225 2.3 mm, C224 3.8 mm; L202 2.4 mm from the L pins).
- **Rule:** TI SLVSEU9D §12.1 p. 28: input and output capacitors as close as possible to the IC, short wide traces.
- **Fix (tested):** C222 → (37.60, 75.40, 90°) 2.6 mm; C223 → (38.30, 73.30, 0°) 3.5 mm; R242 → (41.00, 69.85, 0°) and R243 → (41.70, 68.10, 270°) (the EN divider and MODE pull-down tolerate 9–11 mm).

### F5. Should fix (measured): the RTC's VCC decoupling is 9.9 mm from the pin

- **Parts:** U205 (DS3231M) at (25.14, 39.19, 0°), pin 2 (KEEP_ALIVE) at (24.51, 36.59); C216 ("At U205 pin 2") at (33.99, 32.60).
- **Measured:** 9.9 mm. There is no room below U205 (U101 and the audio LDO parts are there): the planner found none within 5 mm even with U101 nudged.
- **Fix (tested):** rotate U205 180° in place (25.145, 39.194, 180°) so pin 2 comes to the top row at (25.78, 41.79); C216 → (25.72, 44.53, 90°) 2.3 mm; C217 (the 1 nF contact-bounce filter on RTC_VBAT, which tolerates distance) → (33.99, 32.60, 0°) 9.9 mm from pin 6. Side effects checked: BT201's + pad 8.2 mm from pin 6 (was 6), R227 (WAKE_N) 3.5 mm from pin 3.

### F6. Should fix (measured): U401's 3V3 decoupling is 19–20 mm from pin 2 (flagged by the placer)

- **Parts:** U401 at (10.50, 88.61, 0°): pin 2 (3V3) at (1.75, 96.24) faces the left board edge with 1.5 mm of board beside it; C401 (22 µF) at (25.97, 93.17), C402 (100 nF) at (21.47, 93.49) on the far side of the module.
- **Measured:** C402 20.0 mm, C401 19.0 mm (from pin 2). All 14 left-column pins (3V3, EN, the audio enables, I²S, I²C, USB) escape through a 1.5 mm strip or by vias under the module.
- **Rule:** WROOM-1 datasheet v1.8 Fig. 9-1 / MCU README: 22 µF + 0.1 µF at 3V3; Espressif HDG §1.4.2.
- **Fix (tested):** shift U401 3 mm right to (13.50, 88.61, 0°) (body 4.0 mm from the edge, antenna still inside the notch, 12.5 mm from the notch wall); C402 → (2.42, 97.08, 90°) 2.4 mm from pin 2; C401 → (2.07, 93.85, 90°) 4.3 mm; C403 (EN 100 nF, now 20 mm from pin 3) → (2.42, 90.60, 90°) 5.3 mm. The pogo row moves with it: TP401/402/403/413/414/415 to x = 26.00 (same y, 2.54 mm pitch kept); TP410 → (27.75, 86.08), TP411 → (27.73, 87.84), TP412 → (27.91, 89.61); R401 → (24.50, 88.42, 270°), R417 → (24.48, 86.02, 270°); C406 → (24.99, 77.60), TP405 → (18.53, 73.73). The planner's `ANT_KEEP` region becomes (22.5, 95.5)–(39, 99). Bonus: 4 mm of escape room for the left column and the USB pair.

### F7. Should decide (measured, then judgment): the ESP32 corner is the one Espressif marks "not recommended"

- **Measured:** the WROOM-1's feed is at the right end of its antenna (datasheet Fig. 10-1 and the footprint). Espressif HDG §1.4.7 Fig. 24 (feed on the right) ticks only positions 3 (top-right corner, feed at the corner) and 4 (bottom-right); the top-left corner (position 1, where U401 sits) is unmarked, i.e. "not recommended". Fig. 26's cut-out puts ≥ 15 mm of clearance on the side away from the feed and ≤ 2 mm on the feed side; the notch does the mirror image (1.5 mm of board on the far side at the left edge, 15.5 mm on the feed side).
- **Judgment:** the antenna is in free air on three sides (board edge left, notch right and below the strip, nothing above), so the penalty is probably modest, and Wi-Fi is only used in service mode; but Espressif asks for a throughput/range test in the end product either way, and the LTE FPC antenna on the right wall is only ≈ 75 mm away.
- **Options for the owner:** (i) keep it and test range in the box; (ii) rotate U401 90° CCW at the top-left so the antenna hangs 6 mm over the left edge with the feed at the top-left corner (a ticked position by symmetry): no notch, MH1 can stay at (40, 101), pins 1–14 (3V3, EN, audio, USB) face down toward J401, the SD pins face right; the box must leave ≥ 21 mm beyond the left edge and the top-left (≈ 30 parts) is re-placed; (iii) top-right corner with the LTE module moved left: not recommended, the LTE antenna is on the right wall.

### F8. Should fix (measured): the preamp-path ADC input pair cannot be routed as a pair

- **Parts:** U102 pins 30/28 (AIN3P/AIN3M) at (19.14, 16.5/17.5), bottom of the left column. The P leg arrives from C122 (35.43, 6.54) and R124 (24.96, 9.49) at the bottom-right; the M leg from C123 (11.95, 23.05), R125 (15.27, 23.44) and the HPF switch U104 (14.47, 26.41) at the top-left; the HPF shunt resistors R144/R145 at (21.7/19.4, 11.5).
- **Measured:** R124 8.5 mm from pin 30 (and on the other side of the chip), C122 20 mm from R124's partner pads; R125 6.2 mm from pin 28; R144/R145 17 mm from U104's switch pads. The direct path is fine: C118 1.9 mm from pins 3/1, R119/R120 4.1/1.9 mm, C116/C117 within 8 mm.
- **Rule:** audio README rule 3 (each ADC input pair as a coupled pair with ground on both sides; C118/C124 and the 47 Ω resistors at the ADC pins) and rule 4; the A/B comparison of the two paths needs both pairs treated alike.
- **Fix (tested for the P side):** evict the six unfitted mic-2 parts that occupy the prime spot left-below U102 to free spots at x 38–51, y 16–31, clear of the charger capacitors moved in F3 (C134 → (40.94, 23.03, 90°), R135 → (38.64, 16.78, 0°), R146 → (49.11, 29.66, 90°), R147 → (50.46, 29.79, 90°), R143 → (46.54, 23.98, 90°), C138 → (48.71, 21.25, 0°)); if mic 2 is ever fitted, this network should come back beside pins 27/29, which the audio block only allows with ≈ 4 mm more height (or by dropping the mic-2 footprints, option 2.4 a); then C122 → (14.37, 13.65, 90°), R124 → (16.21, 14.59, 90°) (3.3 mm from pin 30, 2.1 mm from C122), R144 → (12.50, 12.59, 90°), R145 → (11.23, 12.22, 90°). The full cluster (U104, C123 and R125 too, so the switch legs are short as well) did not fit under the planner's 0.8 mm IC margin in the ≈ 60 mm² that frees up at x 8–17, y 9–18; place those three by hand in pass 4 (TP101/TP106 can move left to x ≈ 7.5 to help). If U104 leaves (12.6–16.4, 25.4–27.4), R103/R104/R105 fit there at 3.6–5.8 mm from pins 16–18 (finding F9).

### F9. Minor (measured): I²S series resistors 9.2–9.4 mm from U102 (flagged by the placer)

R103/R104/R105 at (16.9, 32.3), (18.2, 33.2), (15.2, 31.3); U102 pins 17/16/18 at (19.14, 23.0/23.5/22.5). Series termination belongs at the driver; at 3 MHz a 9 mm stub is harmless electrically, so this is tidiness. Tested spots if U104 moves (F8): R103 (15.00, 25.60, 0°) 5.3 mm, R104 (15.00, 27.00, 0°) 5.8 mm, R105 (16.76, 25.60, 90°) 3.6 mm.

### F10. Minor (measured): SIM filter parts 8–15 mm from the holder

C313 (100 nF USIM_VDD) 14.6 mm from J301 C1, C311 (33 pF CLK) 8.4 mm, C312 (33 pF DATA) 8.2 mm; C310 3.9 mm and D301 4–5 mm are fine. Quectel HD §4.3 wants the 33 pF and 100 nF at the holder. Tested: C313 → (17.00, 39.20, 90°) 2.0 mm; C311 → (17.25, 42.06, 0°) 2.9 mm; C312 → (16.56, 47.88, 90°) 4.6 mm; R309 (15 kΩ pull-up) stays, no room within 5 mm.

### F11. Minor (judgment): the crystal is 5.8 / 8.7 mm from XI / XO

Y101 at (28.12, 27.23) above-right of U102; pins 10/9 at (24.86, 21.0/20.5); C111/C112 are at the crystal (1.8/1.6 mm). Audio rule 5 wants it tight with a guard ring; TI gives no distance. The only closer spot, (28.4, 20.75) vertical, gives 4.6/3.0 mm but pushes the AVDD and LDO decoupling (C103/C104/C107, now 3.4–4.8 mm from pins 8/11) out to x ≈ 30–32, and the planner found no clean arrangement for that. Decoupling at the pins is TI's explicit rule (SLAS831D §12.1 p. 84), so I would keep Y101 where it is, route XI/XO as a short pair with the guard ring and GND around, and keep C111/C112 as placed.

### F12. Minor (measured, accept): SD ESD and card-supply capacitors 7–12 mm from J402's contacts (flagged by the placer)

D403 8.8 mm, C405 (100 nF) 7.2 mm from J402's VDD contact, C404 (10 µF) 12 mm. The TF-030's contacts sit 4.5 mm inside the holder's body edge, and the body plus the planner's margins keep any part ≥ 6 mm from a contact, so this is the holder's geometry, not the placement. The holder is used lid-off, so the ESD exposure is the open lid. Move C404 next to C405 at ≈ (17.6, 53.3) so the card's bulk is within 7 mm; leave D403.

### F13. Minor (measured): the USB pair splits around two 0 Ω links

R405 at (8.18, 71.06) and R406 at (12.42, 74.37) are 5 mm apart, so D+ runs 11.6 + 2.1 + 5.1 mm and D− 13.0 + 2.3 + 6.9 mm between U401 pins 14/13 and J401 with the legs apart. At full speed (12 Mbit/s) this costs nothing measurable; no room was found to pair them under the margins. Route the two legs side by side and put R405/R406 in line where the router has room; after F6 the module's USB pins are 4 mm further from the edge, which helps.

### F14. Minor (judgment): SW202's knob faces BT201 with a 1.0 mm gap

ALPS SSSS811101: the knob is on the long side opposite terminals 1–3 (drawing p. 2); SW202 at (55.13, 44.00, 270°) has those terminals at x 56.68, so the knob points at the 3 mm-tall coin-cell holder (gap 1.0 mm). It can still be slid with a fingernail from above, but turning SW202 180° (knob toward SW201, 1 mm) is no better. Either move SW202 up ≈ 3 mm so the knob clears the holder's corner, or accept; confirm the knob side on the physical part.

### F15. Minor (judgment): no room reserved for a shield can over the analog section

Audio rule 7 asks for space and pads for a can. The analog parts (U102, U103, the input networks) occupy x 7–38, y 2–30 with 0.7 mm gaps and the audio test pads inside; a can needs a ≈ 1.5 mm free ring. Decide whether to reserve it (≈ 2 mm more audio height) or drop the rule for rev A.

### F16. Note (measured): the 3 A path is 62 mm as the crow flies

J203.1 → F202 4.5 mm, F202 → Q205 2.1, Q205 → Q210 7.2, Q210 → U207 VIN 14.9 (through the latch and battery-sense cluster), U207 VOUT → R301 11.9, R301 → U301 pads 42/43 21.6 (must detour round the module on L1, or go straight on L3). After F1 the last two become one ≈ 37 mm L3 pour. Expect ≈ 20–40 mV at 3 A. Acceptable on 4 layers with via arrays at each layer change; the only congested segment is Q210 → U207 past R216/R217/C213/R245.

### F17. Note (measured): heat and the pack

All four converters/charger parts sit over the assumed pack footprint (x 20–60, y 25–95). Distances: U207 12 mm and L203 12 mm from BT201; U201 1.3 mm, Q202 2.3 mm and D203 6 mm from BT201's corner (the charger dissipates well under 1 W, the BR1220 is rated to +80 °C: fine, but the RTC cell is in the warm zone). U203 is 17 mm from U207, 22 mm from U206, 26 mm from U201, 34 mm from the charger diodes: no converter heats it. It will read board and box-air temperature, not the cells (see question 1).

### F18. Note (measured): RF feed

U301 pad 35 (69.6, 92.1) → R310 4.7 mm → J302's signal pad 3.2 mm, straight, inside the part-free ring (room for the via fence). C314/C315 (DNP) are 2.1–2.3 mm off the line; if ever fitted, put them on the line's edge. Cut the L2 ground under J302's signal pad (Quectel HD §5.2 p. 58). The ESP32 antenna is ≈ 75 mm from J302 and ≈ 75–90 mm from where the FPC antenna will sit on the right wall; isolation must be measured in the box (Quectel asks ≥ 20 dB); firmware never runs Wi-Fi and LTE at once.

### F19. Note (measured): test pads are tight

53 of the 54 test pads have a neighbour within 1.0 mm (0.70–0.97 mm): fine for pogo pins and fine-tipped probes, awkward for hand probing next to the cans (TP210 by C219, TP204/TP206 by C207, TP105 by J201). The pogo row TP401/402/403/413/414/415 is one column at 2.54 mm (y 80.50 … 93.20).

## 4. Checked and fine

- Export: 346 parts, 187 nets; `easyeda_check.py` passes; `place.py --check pass3`: 346/346 at the plan, 0 overlaps, all inside the outline, no pad copper within 0.45 mm of an edge, nothing in a hole keep-out, nothing within 3 mm of U301, minimum part gap 0.70 mm (median 0.76).
- Decoupling at the pin (≤ 3.5 mm, same side, direct connection possible): U102 (C103 3.6, C104 3.4, C105 3.7, C108 2.4, C109 2.7, C110 3.0; the LDO caps C106/C107 4.5/4.8), U101 (C101 3.0; C102 6.0 but on the AVDD_A star), U103 (C126 2.6; C125 7.9 is the RC filter), U104 (C140 3.7), U203 (C212 3.0), U204 (C214 1.7, C215 2.6, C236 2.7), U206 output (C225 2.3, C224 3.8), U207 (C228 2.0, C229 1.9, C230/C231 3.8/4.3), U302 (C308 4.9, C309 3.8), Q301/PWRKEY (C316 2.4), crystal load caps (1.6/1.8).
- Audio: PCM1863 analog pins 1–8 and 27–30 at the bottom end toward J101/U103, digital pins at the top (SLAS831D Fig. 74); direct-path pair C118 1.9 mm from pins 3/1, R119/R120 at the pins; preamp-path cap C124 2.3 mm from pins 30/28; R114 2.5 mm from J101; D101/C113 at the connector (5.5 mm, the connector body is 6 mm deep); AVDD_A star from C102 (FB101 1.8 mm, R116 3.7 mm).
- Separation: the converters and their inductors are ≥ 32 mm from every audio part, the charger ≥ 10 mm (Q202) / 17 mm (U201), the SD holder 17 mm, U401 45 mm, the LTE feed 72 mm; MIC1_OUT stays within x 11–24, y 5–19 at the bottom-left.
- RF: U301's 3 mm ring is empty; feed path straight and short (F18); nothing but the antenna in the notch; the parts nearest the antenna strip (C402 5.1 mm, C401 7.0 mm) are beside the module body, not the antenna.
- Power path: J203 → F202 → Q205 → Q210 in 14 mm with no part between; R202 3.6–4.6 mm from U201 pins 7/8 for Kelvin routing; C207 at R202; U207's exposed pad is free for thermal vias.
- Mechanical: J401 vertical, the plug overmold (≈ 12 × 6.5 mm) stays inside the outline and nothing under it is taller than the 6.5 mm receptacle; J402's lid hinges at the contact side (toward the SD parts) and its free end is at the board edge, nothing taller than 2 mm within its 110° swing; J301's slot faces the left edge (card stands out ≈ 3 mm after the push); J101/J102 GH plugs enter from the bottom edge (solder tabs on the edge side); J203's PH plug enters from the right edge; J201/J202's wire-entry arrows (footprint documentation layer) are on the edge side; SW201, SW202, LED401, BT201 and the pogo row are reachable from above; TP413/TP414 (UART0) sit in the row.
- Manufacturing: tallest parts J201/J202 8.5 mm, C219/C233 7.7 mm, J401 6.5 mm, C201 6.0 mm, J203 5.6 mm, all with ≥ 0.7 mm to their neighbours; D203/D204, C207 and the cans sit clear of the hole keep-outs.
- Polarised parts in the picture agree with the netlist (BT201 pad 1 = +, J203 pad 1 = BAT+, tantalums pad 1 = +); silkscreen "+"/"−" at J201/J202/J203/BT201 and ON/SHIP at SW202 are routing-stage items.
- The placer's own flags: C401/C402 (F6, fix), R103–R105 (F9, minor), D403 (F12, accept), the antenna corner (F7, owner), the pack position (question 1).

## 5. Questions for the owner

1. **Pack position and U203.** U203 at (30, 52) is inside the assumed pack outline and away from every heater, but it senses the board, separated from the cells by the PCB, an air gap, the plate and the wrap. In an Australian box the board will be at box-air temperature and the +42 °C cut-out will trip on box heat before the cells are hot; in a European winter it will read warmer than the cells while charging. Options: a bottom-side copper area with thermal vias under U203 and a thermal pad through a window in the plate onto the pack; or move U203 to wherever the pack's centre lands once the plate is drawn; or accept. The pack outline also decides whether C219/C233 (7.7 mm cans) and J203's lead need to clear a standoff.
2. **ESP32 corner (F7):** keep the top-left notch and test range in the box, or rotate U401 90° CCW with the antenna over the left edge (no notch, 21 mm wall clearance needed).
3. **U301's ring:** keep 3 mm everywhere, or allow the 0402 VBAT caps at ≈ 1 mm on the top edge (F1) and shrink the ring to 1.5 mm elsewhere (2.4 g)?
4. **Board size:** adopt 76 × 100 for pass 4 (the planner reproduces the arrangement with every check passing), or stay at 80 × 105 until the options in 2.4 are decided? Which of a–g, if any, go into rev A?
5. **BT201:** which side does the BR1220 slide in from (the Q&J holder drawing was never read)? That side needs ≈ 12 mm of low parts; today C130 (DNP), TP202 and R205 sit below it and SW202 beside it.
6. **SW202:** confirm the knob side on the physical part; move it 3 mm up if the knob really faces the coin-cell holder (F14).
7. **Shield can over the audio section (F15):** reserve the 1.5 mm ring or drop rule 7 for rev A.
8. **Test pads (F19, 2.4 d):** which debug pads can go; keep the pogo row, the rails and the TMP390 trip pads.
9. **J201/J202:** confirm on a sample that the wire entry faces the pin-side marked by the footprint arrows (the terminal body is symmetric about its pins).
10. **Enclosure:** the 110 × 110 mm interior and the 15 mm side clearances are assumed from the catalogue sheet; read the Hammond 1554P drawing (or measure the box) before fixing the outline, and draw the plate with the SIM, mic-plug and panel-wire clearances of 2.5.
11. **Docs:** F5-05/F5-06 and docs/18 still describe a light pipe and a sealed SD port; lid-off service makes LED401's placement moot but the documents should say so.

## Appendix: how the fixes were tested, and the move list

Tool: `/tmp/auris-review/fix_tool*.py` (not in the repo). For each set it evicts the named parts from the pass-3 placement, re-fits each one at the nearest free spot to a target position using `place.py`'s own `Grid`, `gap_of` margins, hole keep-outs, `ANT_KEEP` and the U301 ring (U401 and C219 were forced to their targets), then runs `place.check()` on the whole board. Sets were first tested one at a time from pass 3, then all of them together: the combined placement passes the same checks (0 overlaps, minimum gap 0.70 mm with the planner's margins). The only interaction found was between F3 and F8 (the evicted mic-2 parts and the charger capacitors both wanted the free area at x 41–50, y 21–29); the coordinates below already resolve it. Pass 4 can apply them with a `pcb-phase3-place.js`-style script (x, y, rotation per designator) and re-run `place.py --check`, or as new anchors in `place.py`.

| Set | Designator | From (x, y, °) | To (x, y, °) | Result |
|---|---|---|---|---|
| F1 | C306 | 44.71, 71.62, 270 | 59.70, 98.00, 0 | 4.5 mm to U301 pad 42/43 |
| F1 | C305 | 44.83, 73.27, 0 | 61.85, 98.00, 0 | 4.6 |
| F1 | C304 | 44.57, 74.98, 90 | 57.62, 98.18, 0 | 5.0 |
| F1 | C303 | 46.83, 73.29, 270 | 63.44, 99.25, 0 | 6.3 |
| F1 | C302 | 48.31, 73.51, 270 | 55.47, 98.25, 0 | 6.3 |
| F1 | C301 | 50.45, 74.44, 270 | 59.70, 100.40, 0 | 6.9 |
| F1 | R301 | 47.23, 75.64, 0 | 54.80, 100.40, 0 | 7.7 |
| F2 | L203 | 53.24, 62.40, 90 | 42.37, 62.77, 90 | 3.9 mm to pads 6–9 |
| F2 | C219 | 39.34, 61.56, 270 | 47.98, 53.55, 270 | 4.7 mm to VIN pads 10/11 |
| F2 | C233 | 47.98, 53.55, 270 | 56.20, 61.80, 0 | ≈ 6 mm to VOUT pads 4/5 (0.7 mm from C219) |
| F2 | C220 | 44.09, 60.06, 90 | 43.30, 58.34, 90 | 5.2 |
| F2 | TP210 | 43.99, 62.48 | 41.30, 57.30 | |
| F2 | D205 (DNP) | 55.51, 57.58, 0 | 61.50, 55.50, 0 | |
| F2 | TP212 | 56.61, 60.49 | 62.00, 63.00 | |
| F3 | C203 | 38.77, 15.34, 90 | 48.30, 26.23, 0 | 4.8 mm to Q202 source |
| F3 | C202 | 44.82, 13.35, 270 | 49.22, 24.17, 0 | 6.9 |
| F3 | LED201 | 49.76, 30.21, 90 | 37.61, 31.71, 90 | |
| F4 | C222 | 41.74, 68.11, 270 | 37.60, 75.40, 90 | 2.6 mm to VIN pad 10 |
| F4 | C223 | 40.27, 69.43, 270 | 38.30, 73.30, 0 | 3.5 |
| F4 | R242 | 38.55, 73.22, 270 | 41.00, 69.85, 0 | |
| F4 | R243 | 37.08, 76.47, 270 | 41.70, 68.10, 270 | |
| F5 | U205 | 25.14, 39.19, 0 | 25.14, 39.19, 180 | rotated in place |
| F5 | C216 | 33.99, 32.60, 0 | 25.72, 44.53, 90 | 2.3 mm to pin 2 |
| F5 | C217 | 25.72, 44.53, 90 | 33.99, 32.60, 0 | 9.9 mm to pin 6 (1 nF filter) |
| F6 | U401 | 10.50, 88.61, 0 | 13.50, 88.61, 0 | body 4.0 mm from the edge |
| F6 | C402 | 21.47, 93.49, 90 | 2.42, 97.08, 90 | 2.4 mm to pin 2 |
| F6 | C401 | 25.97, 93.17, 0 | 2.07, 93.85, 90 | 4.3 |
| F6 | C403 | 21.47, 82.35, 270 | 2.42, 90.60, 90 | 5.3 mm to pin 3 |
| F6 | TP401 … TP415 (pogo row) | x 23.00 | x 26.00 | y unchanged |
| F6 | TP410 / TP411 / TP412 | 24.75, 86.08 / 24.73, 87.84 / 24.91, 89.61 | 27.75, 86.08 / 27.73, 87.84 / 27.91, 89.61 | |
| F6 | R401 / R417 | 21.50, 88.42 / 21.48, 86.02 | 24.50, 88.42, 270 / 24.48, 86.02, 270 | |
| F6 | C406 / TP405 | 23.74, 77.73 / 21.78, 78.22 | 24.99, 77.60, 0 / 18.53, 73.73 | |
| F8 | C134, R135, R146, R147, R143, C138 (DNP) | x 12–16, y 12–17 | 40.94, 23.03, 90 / 38.64, 16.78, 0 / 49.11, 29.66, 90 / 50.46, 29.79, 90 / 46.54, 23.98, 90 / 48.71, 21.25, 0 | parked; see F8 |
| F8 | C122 | 35.43, 6.54, 0 | 14.37, 13.65, 90 | 2.1 mm to R124 |
| F8 | R124 | 24.96, 9.49, 180 | 16.21, 14.59, 90 | 3.3 mm to pin 30 |
| F8 | R144 / R145 | 21.66, 11.52 / 19.39, 11.56 | 12.50, 12.59, 90 / 11.23, 12.22, 90 | U104, C123, R125 by hand |
| F10 | C313 / C311 / C312 | 27.52, 47.52 / 23.11, 44.52 / 20.12, 49.19 | 17.00, 39.20, 90 / 17.25, 42.06, 0 / 16.56, 47.88, 90 | 2.0 / 2.9 / 4.6 mm to the holder |
