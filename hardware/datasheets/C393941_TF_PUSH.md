# TF PUSH — microSD (TF) push-push card holder, SMD, with card-detect contact

| Field | Value |
|---|---|
| LCSC | C393941 · JLC extended · see `parts.csv` for stock and price |
| Manufacturer | SHOU HAN (Shenzhen Shouhan Technology) |
| Package | SMD holder 14.75 × 14.50 mm, 1.80–2.00 mm high; 8 card contacts at 1.10 mm pitch + card-detect pad "Cd" + 4 cover hold-down pads + 2 Ø0.80 mm pegs (drawing, sheet 1) · EasyEDA footprint `TF-SMD_TF-PUSH` |
| Used by | mcu: J402 (with Q401/Q402/R414/R415/C406 card-supply switch, C404/C405, R409–R413 pull-ups, R418 33 Ω SD_CLK series resistor, R419 card-detect pull-up) |
| Datasheet | SHOU HAN drawing "TF PUSH", Rev A, first release 2020-07-07, and "Specification for Approval" TF PUSH Rev A/0 (8 pp.), in one PDF: `pdf/C393941_TF_PUSH.pdf` (LCSC copy: https://www.lcsc.com/datasheet/lcsc_datasheet_1912111437_SHOU-HAN-TF-PUSH_C393941.pdf) |
| Rated temperature | **No operating range stated.** Storage −25…+85 °C (spec §3.8); qualified by thermal shock −55 ↔ +85 °C, 5 cycles (spec Table I item 9) and 85 °C for 96 h (Table I item 14). JLC lists −25…+85 °C |

## Pins

Contact table and pad row from the drawing (pin table lower middle; "Recommended P.C.B hole layout", top right). EasyEDA numbers from the JLCEDA/EasyEDA Official Library record.

| Pin | Name | Function (datasheet) | Auris net | Check |
|---|---|---|---|---|
| 1 | DAT2 | Data bit 2 (I/O, push-pull) | SD_D2: R412 10 kΩ to SD_VDD | OK (unused in 1-bit mode, held high) |
| 2 | CD/DAT3 | Card detect / data bit 3 | SD_D3: R413 10 kΩ to SD_VDD | OK: high at CMD0 keeps the card in SD mode |
| 3 | CMD | Command/response | SD_CMD → GPIO48; R409 10 kΩ to SD_VDD | OK |
| 4 | VDD | Card supply | SD_VDD: Q401 drain, C404 10 µF, C405 100 nF | OK |
| 5 | CLK | Clock (input) | SD_CLK → R418 33 Ω → SD_CLK_MCU → GPIO47 | OK (EasyEDA name "CLX", matched by number) |
| 6 | VSS | Supply ground | GND | OK |
| 7 | DAT0 | Data bit 0 | SD_D0 → GPIO44 (U0RXD); R410 10 kΩ to SD_VDD | OK; see back-feed (T2) |
| 8 | DAT1 | Data bit 1 | SD_D1: R411 10 kΩ to SD_VDD | OK (unused, held high) |
| Cd (EasyEDA symbol pin 9 `CD`, footprint pad `CD`) | Cd | Card-detect contact | SD_CD → GPIO3 (U401 pin 15); R419 100 kΩ to 3V3 | OK since 2026-11-17 (T3, owner decision); the PCB check confirms pad `CD` gets SD_CD (T4) |
| Cover pads ×4 (EasyEDA 10–13) | — | Metal cover hold-downs | GND (rows `J402,10`–`13` SHELL) | OK since 2026-11-17 (T3, owner decision) |
| Pegs ×2 | — | Ø0.80 ± 0.10 mm plastic pegs into Ø1.00 mm holes | — | EasyEDA holes Ø1.20 mm: looser, fine |

Card contacts 1–8 follow the microSD order in the drawing's table and the netlist matches it.

## Limits that matter for Auris

| Parameter | Datasheet (cite) | Auris condition | Verdict |
|---|---|---|---|
| Temperature | Storage −25…+85 °C (§3.8); thermal shock −55…+85 °C ×5 (Table I-9); no operating range | −40 °C in Scandinavian winters, hot enclosures in Australia | **Issue T1** |
| Contact resistance | ≤ 40 mΩ initial, ≤ 100 mΩ after 5000 cycles (Table I-2, I-5) | SD card current ≤ ≈ 0.1–0.2 A | OK |
| Current | 0.3 A per contact (Table I-6, temperature-rise test) | Card supply through one VDD contact | OK |
| Durability | 5000 mating cycles (Table I-5) | Field card swaps (F5-06) | OK |
| Insulation / withstand | 1000 MΩ min; 500 V AC 1 min (Table I-3, I-4) | 3.3 V | OK |
| Reflow | 255 °C (+5/−0) peak (Table III) | JLC standard profile | OK |

## Required external parts and equations

The holder itself needs nothing; the circuit around it was checked here.

- **Card-supply switch** (Q401 AO3401A P-FET, source 3V3, drain SD_VDD; Q402 2N7002 on GPIO45). On: Q402 pulls R415's lower end to GND, so the gate settles at 3.30 V × 10 kΩ/110 kΩ ≈ 0.30 V and VGS ≈ −3.0 V; RDS(on) lies between < 60 mΩ at −4.5 V and < 85 mΩ at −2.5 V (AO3401A Rev 3.1, Dec 2023, p. 1) → < 9 mV at 100 mA. Off: R414 100 kΩ holds VGS at 0; GPIO45's internal pull-down plus R402 keep Q402 off through reset. OK.
- **Soft start** (R415 10 kΩ, C406 100 nF gate-to-source). Gate time constant ≈ (10 kΩ ∥ 100 kΩ) × (100 nF + 645 pF Ciss) ≈ 0.92 ms; Q401 reaches its −0.5 … −1.3 V threshold (AO3401A p. 2) 0.17–0.52 ms after GPIO45 rises. Because the capacitor is gate-to-source and not gate-to-drain, it slows the gate but does not regulate the output slew: once past threshold the FET goes from off to fully on over a few hundred mV of gate swing, so SD_VDD probably rises in ≈ 0.1–0.3 ms, not ≈ 1 ms, and the inrush into C404 + C405 (≈ 5–10 µF effective) is ≈ 0.1–0.3 A (estimate). The 3V3 rail has ≈ 66 µF nominal (C224, C225, C401) and the TPS63802 behind it, so the dip should stay small; worth measuring (T5). The gate-to-source placement has one real advantage: when 3V3 itself ramps at wake, the gate follows the source and Q401 stays off. Turn-off: R414 × C406 ≈ 10 ms.
- **Pull-ups** R409–R413 10 kΩ to SD_VDD. Espressif asks for pull-ups on the SD lines (ESP32-S3 HWDG §1.3.12); tying them to the switched SD_VDD rather than 3V3 is right, because a pull-up to 3V3 would feed the unpowered card through each line (≈ 0.3 mA per line through the card's input diodes). The reverse path remains: whatever the ESP32 drives high on CMD/D0/CLK, or GPIO44's own reset pull-up, flows into SD_VDD while the card is off (T2). CLK needs no pull-up (the host always drives it when the card is powered); the recommended series resistor near the ESP32 is R418 33 Ω since 2026-11-17 (ESP32 file F9).
- **Decoupling**: C404 10 µF (X5R 10 V 0603, C19702) + C405 100 nF at J402. OK.
- **Card detect** (T3): the footprint has a single Cd pad; with only one pin, the switch can only close against the metal cover, so the cover must be on GND for CD to read anything (inference from the drawing; normally-open or normally-closed is not stated, check with a meter on a sample). With R419 100 kΩ to 3V3: 33 µA while awake in whichever state is closed, nothing while asleep. Wired this way since 2026-11-17: J402 pin 9 on SD_CD (GPIO3), pads 10–13 on GND.

## Layout notes and gotchas

- Pads 1–8 and Cd: 0.70 × 1.60 mm at 1.10 mm pitch; cover pads 1.20 × 1.50, 1.60 × 1.50 and 2 × 1.20 × 2.20 mm; pegs into Ø1.00 mm holes 8.00 mm apart (drawing layout). The EasyEDA footprint matches (holes Ø1.20).
- Card opening must face the service hatch so the card can be swapped without opening the main seal (F5-06); push-push operation (drawing: push in, push out) needs finger room in front of the slot.
- Keep CMD and D0 within ±50 mil of CLK (ESP32-S3 HWDG §1.4.9). C405 at pin 4.
- The cover pads carry the card-detect return and the ESD path from a hand inserting a card: short, wide connection to the ground plane.

## EasyEDA symbol and footprint

Source: JLCEDA/EasyEDA Official Library ([lceda.cn](https://lceda.cn/), [easyeda.com](https://easyeda.com)), record for C393941, read 2026-11-17.

- **Symbol** `TF PUSH`, 13 pins: 1 DAT2, 2 CD/DAT3, 3 CMD, 4 VDD, 5 CLX (sic, CLK), 6 VSS, 7 DAT0, 8 DAT1, **9 CD**, 10, 11, 12, 13 (unnamed: cover).
- **Footprint** `TF-SMD_TF-PUSH`: pads 1–8, a pad numbered **`CD`**, and pads 10–13 (cover). Pad geometry and order match the drawing's layout (Cd, 8 … 1 from left to right, 1.10 mm pitch).
- **Mismatch**: symbol pin 9 (`CD`) has no pad 9; the pad is numbered `CD`. If the schematic-to-PCB link goes by number, a net on pin 9 never reaches the pad (T4). Pins 1–8 and 10–13 match. After the 2026-11-17 re-capture the PCB net check confirmed that pad `CD` carries SD_CD.
- Capture: netlist rows `J402,1…13` match by number. Rows 9–13 were added on 2026-11-17 with explicit numbers, so the capture's habit of assigning unnumbered "mounting" rows to whatever pins are left cannot put GND on the CD pin.

## Findings

| Severity | Designator / pin | Issue | Evidence | Fix | Status |
|---|---|---|---|---|---|
| Should fix (T1) | J402 | No operating temperature given; storage is −25…+85 °C, below which only a 5-cycle −55 °C thermal shock was qualified. Auris must work at −40 °C (Europe) and in hot enclosures (Australia), and the card swap happens outdoors | Spec Rev A/0 §3.8, Table I items 9 and 14 | Choose a holder with a stated −40 °C operating rating, or qualify this one: cold soak at −40 °C, then card insert/eject and a write test, plus the SD card itself rated industrial (−40…+85 °C) | open (review W8/M9: qualify at −40 °C or choose a −40 °C holder) |
| Should fix (T2) | J402 pins 3, 5, 7 / U401 GPIO48, GPIO47, GPIO44; R409, R410 | The card is fed through its signal pins while SD_VDD is off: GPIO44 (U0RXD) has its weak pull-up on at and after reset and drives SD_VDD through R410; an SDMMC bus left idle-high at card power-off does the same through R409/R410 and the card's pin diodes. The card then never sees a clean power cycle | ESP32-S3 DS v2.2 Table 2-1; netlist; SD Physical Layer Simplified Spec §6.4.1 (not in repo, not re-read) | Firmware rule in the MCU README (ESP32 file F5): clear GPIO44's pull-up early, drive CLK/CMD/D0 low before SD_PWR_EN low, keep them low ≥ 100 ms, no internal pulls on SD pins. Bring-up: scope SD_VDD with a card in | fixed in docs (review M5, mcu README); firmware open |
| Should fix (T3) | J402 Cd, cover pads 10–13 | Card-detect and cover pads have no netlist rows | Drawing layout; EasyEDA pins 9–13 | Add `J402,10,SHELL,GND,Y` … `J402,13,SHELL,GND,Y` (cover to GND: needed for CD and as the ESD path). Add `J402,9,CD,SD_CD,Y`, `R419,1,1,3V3,Y` / `R419,2,2,SD_CD,Y` 100 kΩ (C25741), and move U401 pin 15 (GPIO3) from USB_VSENSE to SD_CD, dropping the DNP R407/R408. GPIO3's strap is ignored with default eFuses. Do not use GPIO46 (download-mode strap). If no GPIO is wanted, leave `J402,9,CD,NC,Y` explicitly | owner decision (review M6): applied as proposed |
| Should fix (T4) | J402 symbol pin 9 / pad `CD` | Symbol pin number 9 does not match footprint pad number `CD` | EasyEDA record C393941 | Once CD is wired, check after "Update PCB" that pad CD carries SD_CD; if not, renumber the footprint pad to 9 (or the symbol pin to CD) in a project copy of the part | fixed (PCB net check: pad CD carries SD_CD, review M6) |
| Note (T5) | Q401/C406 | Soft start is shorter than the README's ≈ 1 ms; inrush ≈ 0.1–0.3 A (estimate) | AO3401A Rev 3.1; calculation above | Measure 3V3 and SD_VDD at SD power-on. If the dip is too large, use a load switch with controlled slew, as the README already suggests | fixed in docs (mcu README now says ≈ 0.1–0.3 ms, review M11); measurement open (bench) |
| Note (T6) | J402 | Drawing, spec and JLC disagree on details (JLC description says "No Push-Push", attribute says push-push; drawing shows push-in/push-out travel) | Drawing sheet 1; JLC record | Drawing governs: push-push | no action |
