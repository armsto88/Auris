# Handover: independent review of the rev A PCB placement (pass 3)

You are reviewing the component placement of the Auris rev A board before routing starts. Work on your own judgment: the person who placed it wants problems found, not the placement defended. Read-only: do not change EasyEDA, the sheet CSVs or the scripts, and do not commit. Your only output is the review file described at the end.

This runs unattended (the owner is asleep): do not use the browser, Chrome or any web tool, and do not wait for answers. Everything you need is in the repo and in `hardware/datasheets/pdf/`. Put your own scripts and images under `/tmp/auris-review/`. `place.py --check` re-renders `hardware/layout/placement-pass3.png` (same picture); that is the only repo file it touches. If something cannot be settled from the files, note it under *Questions for the owner* and carry on.

## The owner's main question: can the board be smaller?

The owner wants the board as small as practical. Pass 3 is 80 × 105 mm (≈ 8,190 mm² after the notch) and deliberately loose: after pass 1 looked cramped, every part got ≥ 0.7 mm clearance and ICs ≈ 1.6 mm for fan-out. Starting numbers (check them): parts cover ≈ 3,220 mm² of body and pads (39 %); 45 unfitted parts take ≈ 180 mm², 148 of it the optional second-mic chain (block `mic2`); the 54 test pads ≈ 55 mm²; the largest footprints are U401 (≈ 495 mm², the antenna strip over the notch), BT201's CR1220 holder (≈ 313 mm²), U301 (≈ 280 mm² plus its 3 mm keep-out ring), J402 (≈ 210 mm²) and J301 (≈ 208 mm²). Fixed costs: the notch (35 × 6 mm), four M3 hole keep-outs, U301's ring, the antenna's clearance.

Answer this:
- the smallest outline you would route with confidence on 4 layers, top side only, keeping the existing arrangement logic (give W × H, and where the holes and notch go);
- what sets that limit (which parts or keep-outs);
- what a further step would need, each as a separate option with its saving in mm² and its cost: dropping the second-mic footprints, a smaller RTC backup (smaller coin-cell holder or other), an embedded SIM instead of the holder, fewer or smaller test pads, parts on the bottom side, a different ESP32 corner or module orientation. Part or schematic changes need the owner's approval and a change-log row, so propose them; do not make them.

The box matters too: the pack (≈ 40 × 70 × 20 mm) now sits under the board on the plate, so say whether a smaller board still fits the pack's footprint or leaves it overhanging.

## The product, in one paragraph

Auris is a solar-powered outdoor acoustic recorder with on-device detection and LTE uplink, deployed in Europe and Australia (check heat against Australian summer sun and cold against European winter). Main parts: ESP32-S3-WROOM-1 (U401), Quectel EG810M-EU LTE module (U301, u.FL J302 to an FPC antenna on the box's right wall), PCM1863 ADC (U102) with mic preamps (U103/U104/U105) and a separable mic head on J101 (J102 optional second mic), CN3791 solar MPPT charger (U201) from J201/J202, 1S2P 18650 pack on J203 (now **under** the board on a 3D-printed plate), TPS63802 main 3.3 V (U206), TPS63020 modem rail (U207, ≈ 3 A peaks into U301), DS3231M RTC with CR1220 (U205, BT201), TMP390 cell-temperature cut-out (U203). Service is lid-off. Take Auris facts from Auris docs only; `docs/20-FIELDMESH-…` describes another product and is background, not a spec.

## The board

- 80 × 105 mm, origin bottom-left, Y up, all dimensions mm, angles counter-clockwise. A 35 × 6 mm notch at the top-left (x 0–35, y 99–105) leaves U401's antenna strip in free air. M3 holes at (4, 4), (76, 4), (40, 101), (76, 101), kept clear ±3.6 mm.
- 4 layers, JLC04161H-7628 (1.6 mm); all parts on the top side; L2 solid GND, L3 power pours, L4 signals and GND.
- Owner decisions and the reasons for the arrangement: `hardware/layout/README.md` (outline, notch, battery under the board, top-access USB-C J401 and flip-top microSD J402, stack-up, impedance targets, net classes, current-carrying nets, footprint fixes, still to do).
- The placement rules you are checking against: `hardware/review/handover-rev-a-pcb-layout.md`, *Phase 3 — placement*, and the audio *Layout rules* in `hardware/audio-frontend/README.md`.

## What to look at

- Picture: `hardware/layout/placement-pass3.png` (parts coloured by sheet, pads in gold, U301's 3 mm ring dotted). Positions: `hardware/layout/placement-pass3.csv`.
- The real board: export `hardware/2026-11-19/AURIS_2026-11-19_place3.epro2`. `hardware/tools/pcb_board.py` loads it (parts, footprints, pad positions, pad nets); `python3 hardware/layout/place.py --check hardware/2026-11-19/AURIS_2026-11-19_place3.epro2 pass3` re-runs the placement checks and re-renders the PNG; `python3 hardware/tools/easyeda_check.py <export>` checks parts and nets against the sheet CSVs. Write your own measurements with `pcb_board.py` (and matplotlib for extra views) rather than trusting the planner's summary. Screenshots of the live editor are not available.
- Netlists and BOMs: `hardware/{audio-frontend,power,lte,mcu}/*-netlist.csv` and `*-bom.csv`; their notes say which cap belongs at which pin ("At U102 pin 8"). Sheet READMEs explain each block.
- Datasheets: `hardware/datasheets/pdf/` (local only, git-ignored), e.g. Quectel EG810M-EU hardware design (keep-out, Fig. 40), `esp32-s3_hw_design.pdf` (antenna placement, Fig. 24–26), `pcm1863.pdf`, TPS63802/TPS63020/CN3791 layout examples.
- Requirements and decisions: `docs/19-V1-FUNCTIONAL-REQUIREMENTS.md`, `docs/14-DECISION-REGISTER.md`; enclosure notes in `hardware/layout/enclosure-options.md`.

## Check at least

1. **Decoupling:** every decoupling cap at its pin, same layer, room for a direct connection; measure cap-pad-to-pin distances.
2. **Switching loops:** U206 + L202 + C222/C224/C225; U207 + L203 + C228–C232 (thermal vias under U207's pad); charger C203–Q202–D203/D204–L201; R202 Kelvin to U201 pins 7/8; D203/D204 cathode copper ≈ 1 cm².
3. **Power path:** J203 → F202 → Q205 → RAW_BAT → Q210 → VBAT_SW → U207 → VMODEM → R301 → U301 at ≈ 3 A: short, wide, few layer changes.
4. **Audio separation and rules:** front end away from the converters, charger, SD bus, I²S and the LTE feed; PCM1863 analog pins facing the mic and preamps; crystal tight to pins 9/10 with room for a guard ring; ADC input pairs; room for a shield can.
5. **RF:** U301's 3 mm keep-out; R310/C314/C315 at J302; a short, straight 50 Ω path from U301 pad 35 with room for a via fence; ESP32 antenna in the notch, and whether the chosen corner is right (the WROOM-1 feed is at its right end; Espressif's figures put the feed side at the board corner).
6. **Thermal:** U203 placement for cell temperature with the pack under the board (pack position not yet fixed); heat from U207/U206/U201/U301 relative to the pack, the coin cell and the audio.
7. **Mechanical and service:** lid-off access to J401 (vertical USB-C, 6.5 mm tall), J402 (flip-top lid, opens up to 110°), J301 (side-entry SIM at the left edge), SW201/SW202, LED401, BT201; the pogo row TP401–TP403 + TP413–TP415 at 2.54 mm; edge connectors J101/J102/J201/J202/J203 and which way their plugs go (facing was inferred from footprints: confirm against drawings where you can); polarity marking on J201/J202.
8. **Routability on 4 layers:** fan-out room around U401, U301, U102, U302; the USB pairs (90 Ω); congestion hot spots; where vias for the 3 A path and the GND stitching go.
9. **Manufacturing:** spacing between parts (≥ 0.7 mm now), copper-to-edge clearance, tall parts next to small ones (rework, reflow shadowing), test-pad access.

Things the placer already flagged; judge them, don't assume they are acceptable: U401's 3V3 decoupling (C401/C402) far from module pin 2 at the board edge; I²S series resistors R103–R105 9–14 mm from U102; SD ESD D403 ≈ 9 mm from J402's contacts; the antenna corner; the assumed pack position.

## Deliverable

Write `hardware/review/<today's date>-placement-review.md`:

1. **Verdict:** ready to route, or needs another placement pass, in two or three sentences.
2. **Board size:** your answer to the owner's main question above: the smallest outline you would route at this stage, what limits it, and the further options with savings and costs.
3. **Findings**, most severe first, each with: severity (blocker / should fix / minor), designators, where on the board (mm), what is wrong, the rule or datasheet page it breaks, and a concrete fix (target x, y, angle, or what to move where). Mark each finding *measured* (you computed it from the export or a datasheet) or *judgment*.
4. **Checked and fine:** a short list, so the owner knows what was covered.
5. **Questions for the owner:** decisions only the owner can make (e.g. the pack position, the antenna corner).

Keep it in plain language the owner can act on; give numbers where you have them.
