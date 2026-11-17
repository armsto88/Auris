# EG800KEULC-I03-SNNSA — LTE Cat-1 bis module (Quectel EG800K-EU), LGA-109

| Field | Value |
|---|---|
| LCSC | C44008839 · JLC extended · see `parts.csv` for stock and price (**JLC stock 4 on 2026-11-17**) |
| Manufacturer | Quectel |
| Package | LGA, 109 pads, 17.7 × 15.8 × 2.4 mm (LA-HD Table 2) · EasyEDA footprint `LGA-109_L17.7-W15.8-AIR780E` |
| Used by | lte: U301 |
| Datasheet | **Not the EU manual.** Read: Quectel *EG800K-LA Hardware Design* V1.0.0, 2024-05-23, status Preliminary (local `pdf/EG800K-LA_HD.pdf`, from the FCC filing; cited below as **LA-HD**, page numbers are the printed "N / 69" footer, PDF page = N + 1). Also Quectel *EC800K & EG800K Series QuecOpen Reference Design* V1.2, 2025-02-26, Released (local `pdf/Quectel_EC800K_EG800K_QuecOpen_Ref_V1.2.pdf`, cited as **Ref**, by sheet number "x of 17"); Ref §1.1 states it covers EG800K-EU. EU-specific data: Quectel *EG800K Series LTE Standard Specification* V1.3, Released, 2024 (2-page product sheet, local `pdf/C44008839_EG800KEULC-I03-SNNSA.pdf`, cited as **Spec**). The EG800K-EU Hardware Design needs a Quectel login and was not read |
| Rated temperature | EG800K-EU: operating −35 to +75 °C, extended −40 to +85 °C (Spec p. 2). LA-HD Table 34 (p. 52) gives the same ranges and defines them: normal = 3GPP-compliant; extended = functional, RF parameters such as Pout may fall outside 3GPP tolerance; storage −40 to +90 °C. JLC attribute: −35 to +75 °C |

**EU vs LA.** Same series, same LGA-109 package and 17.7 × 15.8 × 2.4 mm outline (Spec p. 2). EG800K-EU bands are LTE-FDD **B1/3/5/7/8/20/28**, no LTE-TDD, no GNSS, certifications CE (Europe) and RCM (Australia/New Zealand), three UARTs (main, debug, auxiliary), USIM card detection supported (Spec p. 2) — this matches the project's band list. LA bands are B2/3/4/5/7/8/28/66 (LA-HD Table 3, Table 23), so LA-HD Tables 23–25 (frequencies, Tx power, sensitivity) do not apply to the EU part. EU typical currents from Spec p. 2: 7.47 µA power-off, 0.64/0.56 mA sleep (PF 128/256), 7.82 mA idle with USB disconnected, 19.66 mA with USB connected. The Spec gives no pin table and no peak/transmit current. Every pin Auris uses (7, 9, 11–25, 28, 29, 35, 38, 39, 42, 43, 59–61, 66, 67, 79, 82, 96) and the GND pins drawn on Ref sheet 3 (a symbol shared by EC800K-CN and EG800K-CN/EU/LA) agree with LA-HD Table 6. In the QuecOpen symbol, several pads that LA-HD calls RESERVED carry QuecOpen functions (2 ANT_GNSS on CN only, 30–33 GPIO1–4, 49–53 LCD, 54–58 GPIO5–9, 68/69 I2C1, 74–78 keypad/LCD_TE, 80/81/83 GPIO10–12, 86/87 keypad, 99 1PPS, 104/105 GRFC); with standard AT firmware they stay open, which is also what Ref note 6 (sheet 3) asks for unused pins.

## Pins

All 109 netlist rows were compared by script with LA-HD Table 6 (pp. 15–19) and the RESERVED list (p. 19): **109/109 pin numbers and names agree; every GND pad is on GND, every RESERVED pad is NC.**

| Pin | Name | Function (LA-HD Table 6) | Auris net | Check |
|---|---|---|---|---|
| 1, 10, 27, 34, 36, 37, 40, 41, 45–48, 70–73, 88–95 | GND | Ground (26 pads) | GND | OK — all to GND (Table 6 p. 16; Fig. 1 note 1) |
| 2–6, 8, 26, 30–33, 44, 49–58, 62–65, 68, 69, 74–78, 80, 81, 83–87, 97–109 | RESERVED | Keep open (p. 19) | NC | OK |
| 7 | PWRKEY | DI, VBAT domain (Vnom = VBAT, VIL ≤ 0.5 V); low ≥ 700 ms on, ≥ 650 ms off | M_PWRKEY (Q301 collector, TP302) | OK — internal pull-up to VBAT, open-collector drive is Quectel's recommendation (§3.5.1). Missing 10 nF, see findings |
| 9 | ADC0 | AI, 0–1.2 V; open if unused | NC | OK |
| 11 | USIM_DATA | DIO | SIM_DATA_M → R308 0 Ω | OK |
| 12 | USIM_RST | DO | SIM_RST_M → R306 0 Ω | OK |
| 13 | USIM_CLK | DO | SIM_CLK_M → R307 0 Ω | OK |
| 14 | USIM_VDD | PO, 1.8/3.0 V auto | USIM_VDD | OK |
| 15 | RESET_N | DI, active low, Vnom 1.8 V, VIL ≤ 0.5 V; test point recommended if unused | M_RESET_N (TP303 only) | OK |
| 16 | NET_STATUS | DO 1.8 V; open if unused | M_NETSTAT (TP305) | OK |
| 17 | MAIN_RXD | DI 1.8 V | M_RXD → U302 A2 ← ESP32 TX | OK |
| 18 | MAIN_TXD | DO 1.8 V | M_TXD → U302 A1 → ESP32 RX | OK |
| 19 | MAIN_DTR | DI; open if unused | NC | OK — open = high = sleep allowed only if `AT+QSCLK=1` (see findings) |
| 20 | MAIN_RI | DO; open if unused | NC | OK |
| 21 | MAIN_DCD | DO; open if unused | NC | OK |
| 22 | MAIN_CTS | DO, "connect to the MCU's CTS" | M_CTS → U302 A4 → ESP32 CTS (GPIO42) | OK |
| 23 | MAIN_RTS | DI, "connect to the MCU's RTS" | M_RTS → U302 A3 ← ESP32 RTS (GPIO41) | OK — matches LA-HD §4.4 note 2 (p. 37) and Ref sheet 7 (MAIN_RTS ↔ RTS_MCU) |
| 24 | VDD_EXT | PO 1.8 V, 50 mA max | VDD_EXT (U302 VCCA, R304, C308, TP304) | OK — load < 0.3 mA |
| 25 | STATUS | DO 1.8 V, high when on | M_STATUS → U302 A5 → ESP32 GPIO38 | OK |
| 28 / 29 | AUX_RXD / AUX_TXD | DI / DO; open if unused | NC | OK |
| 35 | ANT_MAIN | 50 Ω RF | ANT_MAIN → R310 → J302 | OK |
| 38 / 39 | DBG_RXD / DBG_TXD | 1.8 V; "test points must be reserved" | M_DBG_RXD / M_DBG_TXD (TP307 / TP306) | OK |
| 42, 43 | VBAT | PI, 3.4–4.3 V, nom 3.8 V; supply ≥ 2 A | VBAT_M | OK (3.9 V) |
| 59 / 60 | USB_DP / USB_DM | USB 2.0 HS, 90 Ω diff; test points must be reserved | M_USB_DP / M_USB_DM (TP309 / TP310) | OK |
| 61 | USB_VBUS | AI, 3.0–5.25 V, connection detect; test point must be reserved | M_USB_VBUS (TP308) | OK |
| 66 / 67 | I2C_SDA / I2C_SCL | OD; open if unused | NC | OK |
| 79 | USIM_DET | DI 1.8 V; open if unused | NC | OK |
| 82 | USB_BOOT | DI, active low; must not be low before start-up except to force download | M_USB_BOOT → R311 4.7 kΩ → BOOT_PAD (TP311) | OK — matches Fig. 17 |
| 96 | ADC1 | AI 0–1.2 V; open if unused | NC | OK |

## Limits that matter for Auris

| Parameter | Datasheet (cite) | Auris condition | Verdict |
|---|---|---|---|
| VBAT operating | 3.4 / 3.8 / 4.3 V min/typ/max (LA-HD Table 28, p. 49; §3.4.4) | 3.9 V from TPS63020 (power sheet R232/R233 divider, FB 0.5 V) | OK; 0.5 V headroom for droop, 0.4 V to the top |
| VBAT absolute max | −0.3 to 6 V (Table 27, p. 49) | SMAJ5.0A D205 on VMODEM: VRWM 5.0 V, breakdown ≥ 6.4 V, clamp ≈ 9.2 V at rated pulse (Littelfuse SMAJ family figures from memory, **not re-read**) | **Not protected**: the TVS only starts to conduct above the module's abs max. See findings |
| VBAT current | Peak 1.5 A typ, 2 A max at max power (Table 28); abs max 2 A (Table 27); supply "≥ 2.0 A" (Table 6, §3.4.2). Ref V1.2 lowered its supply requirement to 1.5 A (Ref revision history, sheet 5 note 1) | TPS63020 rail, 470 µF + 3 × 22 µF at the converter, C301 at the pins | OK for the module side; converter capability is the power-sheet review's job. LTE data-transmission currents are TBD in LA-HD Table 29 |
| Bulk capacitor | ≈ 100 µF, ESR ≤ 0.7 Ω, plus 100 nF, 33 pF, 10 pF, 3.9 pF, 1.8 pF MLCCs close to VBAT and a 0 Ω (≥ 0603) (§3.4.4 p. 25; Fig. 8 p. 26; Ref sheet 5) | C301 100 µF 70 mΩ polymer Ta; C302 100 nF, C303 33 pF, C304 10 pF, C305 3.9 pF, C306 1.8 pF; R301 0805 0 Ω | OK — values identical |
| VBAT trace | ≥ 2 mm wide (§3.4.4; Ref sheet 5 note 2) | layout | Layout rule |
| PWRKEY | Low ≥ 700 ms to turn on, ≥ 650 ms to turn off; VBAT stable ≥ 30 ms first; open-drain/collector driver recommended; capacitance ≤ 10 nF (§3.5.1, §3.6.1, §3.7 note 2; Figs. 9, 11, 12) | Q301 MMBT3904, R302 4.7 kΩ, R303 47 kΩ; firmware 800 ms pulse | OK. Ib ≈ (3.3 − 0.7)/4.7 k − 0.7/47 k ≈ 0.54 mA; collector current is only the internal pull-up's, so Q301 is deep in saturation (MMBT3904 VCE(sat) ≤ 0.2 V at 10 mA/1 mA, onsemi MMBT3904LT1/D Rev. 15) ≪ VIL 0.5 V |
| Turn-on timing | VDD_EXT ≈ 65 ms after PWRKEY low; STATUS high ≥ 6 s; UART and USB active ≥ 10 s (Fig. 11, p. 27) | README sequence step 3 | See findings (wait for UART, not only STATUS) |
| Turn-off | After PWRKEY release, power-down takes 2–10 s, then STATUS low (Fig. 12, p. 28); keep PWRKEY high after `AT+QPOWD` or the module restarts (§3.6.2 note 2); never cut VBAT while running (§3.4.2 note, §3.6.2 note 1) | README steps 5–6 | OK |
| RESET_N | Low ≥ 300 ms; use only if `AT+QPOWD` and PWRKEY fail; route short, guarded by ground (§3.7, p. 29–30) | Test pad only | OK |
| Digital I/O (1.8 V) | VIH 0.7·VDDIO … VDDIO + 0.2; VIL ≤ 0.3·VDDIO; VOH ≥ VDDIO − 0.2; VOL ≤ 0.2 V (Table 30, p. 51); abs max 2.2 V on digital pins (Table 27) | All via U302 or test pads | OK — no 3.3 V signal touches the module |
| VDD_EXT | 1.8 V, 50 mA max (Table 6 p. 16) | U302 VCCA (≤ 2 µA static + ≤ 45 µA per low line), R304/R305 1.6 µA | OK |
| USB_VBUS | 3.0–5.25 V operating, abs max 5.5 V (Tables 27, 28) | Test pad TP308, fed from the service cable | OK |
| USIM | 1.8 V class 1.62–1.98 V; 3.0 V class 2.7–3.3 V (Tables 31, 32) | SRV05-4 VRWM 5 V | OK |
| ESD | VBAT/GND ±5 kV contact; antenna ±4 kV; other interfaces only ±0.5 kV contact (Table 33, p. 52) | SIM protected by D301; test pads unprotected | OK for service-only pads (see notes) |
| Power-down current | 6.61 µA typ, VBAT applied (LA-HD Table 29, p. 50); EU 7.47 µA (Spec p. 2) | VMODEM switched off between sessions | Not relevant |
| Idle current | EU: 7.82 mA (USB disconnected) vs 19.66 mA (USB connected) at PF = 64 (Spec p. 2); LA 7.34 / 19.34 mA (LA-HD Table 29) | USB_VBUS open in the field | Good: leaving VBUS open saves ≈ 12 mA |
| Temperature | −35 to +75 °C operating, −40 to +85 °C extended (Spec p. 2; LA-HD Table 34) | −40 °C winters; hot Australian enclosures | Marginal at both ends; see findings |

## Required external parts and equations

**VBAT** (§3.4.4, Fig. 8; Ref sheet 5). Quectel: one ≈ 100 µF low-ESR bulk (ESR ≤ 0.7 Ω), MLCC array 100 nF / 33 pF / 10 pF / 3.9 pF / 1.8 pF next to the pins, a 0 Ω debug link (≥ 0603), a TVS with VRWM 4.7 V and low clamp at the front end. Auris BOM: C301 T520A107M006ATE070 (100 µF, 70 mΩ at 100 kHz), C302–C306 exactly the Quectel values, R301 0805 0 Ω. Droop budget: (3.9 − 3.4) V = 0.5 V. Through R301 + trace at the 2 A worst case, a 0805 jumper (typ. ≤ 50 mΩ max resistance class; check the UNI-ROYAL rating ≥ 2 A) costs ≤ 0.1 V. Topology difference: Quectel puts the 0 Ω between the array and the module pins; Auris puts the array on the module side of R301. Auris's arrangement keeps the capacitors directly at the pins and is acceptable; with R301 lifted for current measurement, C301 stays on the module side, so the ammeter sees averaged current.

**PWRKEY** (Fig. 9, p. 26; Ref sheet 4). Quectel draws an NPN with 4.7 kΩ base / 47 kΩ base-emitter (Ref uses DTC043ZEBTL, same values) **and 10 nF from PWRKEY to GND** (Fig. 9; Ref sheet 4 C0401). Auris has Q301 + R302 4.7 kΩ + R303 47 kΩ but no capacitor. No external pull-up is needed: Table 6 gives PWRKEY Vnom = VBAT (pulled up inside the module to VBAT, i.e. ≈ 3.9 V on TP302) and Fig. 11 shows PWRKEY rising with VBAT. ESP32-S3 GPIO21 has no pull at reset (ESP32-S3 Series Datasheet v2.2, Table 2-1 pin settings), so R303 holds Q301 off during ESP32 boot.

**USB_BOOT** (§4.2, Figs. 17–18, pp. 32–33; Ref sheet 16). Active low; pulled high internally once VDD_EXT is up (Fig. 11 shows USB_BOOT rising with VDD_EXT). To force download, hold it low through **4.7 kΩ to GND** before turning the module on (note 3, p. 33); never low during normal start. Auris: R311 4.7 kΩ from pin 82 to BOOT_PAD, shorted to a GND pad by the technician — electrically the same as Fig. 17 (test points then 4.7 kΩ). Optional TVS near the pads is dashed in Fig. 17.

**USB / service** (§4.1, Fig. 16; Ref sheet 3 notes 1 and 8, sheet 16). Test points **must** be reserved for USB_DP/DM, USB_VBUS and DBG_TXD/RXD; recommended for VDD_EXT, USB_BOOT, PWRKEY, VBAT, and RESET_N when unused. Auris: TP309/TP310 (DP/DM), TP308 (VBUS), TP306/TP307 (DBG), TP304 (VDD_EXT), TP311 (BOOT_PAD), TP302 (PWRKEY), TP301 (VBAT_M), TP303 (RESET_N), TP305 (NET_STATUS), TP312/TP313 (GND). **Complete.** USB_VBUS is the connection detect: the module's USB only works when 3.0–5.25 V is present on pin 61 (Ref sheet 4 note 2 says USB_VBUS must be powered externally for USB detection), so the service jig must bring the cable's 5 V to TP308; a pad is enough. QFlash ≥ 6.0 is required (Table 4 note p. 13; §4.2 note 4).

**USIM** (§4.3, Figs. 19–20, pp. 34–35; Ref sheet 6). 0 Ω in series on RST/CLK/DATA, 33 pF to GND on each at the holder, 100 nF (< 1 µF) on USIM_VDD at the holder, 15 kΩ USIM_DATA pull-up to USIM_VDD near the holder, TVS array < 15 pF, trace < 200 mm, keep away from RF/VBAT, guard DATA vs CLK with ground. Auris R306–R308 0 Ω, C310–C312 33 pF, C313 100 nF, R309 15 kΩ to USIM_VDD on the card side of R308, D301 SRV05-4 (3 pF), USIM_DET open. **All values match.**

**UART** (§4.4, Fig. 21, p. 37; Ref sheet 7). TXS0108EPWR recommended; Ref's OE network is 10 kΩ from VDD_EXT with 120 kΩ to GND (no capacitor), unused channel A1/B1 each 51 kΩ to GND. Module CTS goes to MCU CTS and module RTS to MCU RTS (§4.4 note 2). Hardware flow control recommended (note 3). Auris uses U302 with R304 100 kΩ / R305 1 MΩ / C307 100 nF — see the U302 file (`C17206_TXS0108EPWR.md`) for the OE analysis.

**Filter capacitors on used I/O** (Ref sheet 3 note 9). If pins 16–18, 20–23, 25, 39 or 67 are used, Quectel asks to reserve 22/33 pF capacitors next to the pins (drawn not mounted). Auris uses 16, 17, 18, 22, 23, 25 and 39 and has none.

**Antenna** (§5.1.4 Fig. 25, §5.2, §5.4; Ref sheet 9). π network (series R1 0 Ω, two shunt C not mounted) placed **close to the antenna/connector**; 50 Ω controlled-impedance feed; GND pads next to RF pins without thermal relief; vias ≥ 2 W from the trace; Hirose U.FL-R-SMT recommended; antenna VSWR ≤ 2, efficiency > 30 %, cable loss < 1 / 1.5 / 2 dB for LB / MB / HB (Table 26). Ref V1.2 adds a series 100 pF (C0912) between ANT_MAIN and the π, needed only if there is DC at the antenna port (Ref sheet 9 note 9) and an optional ESD diode (Cj ≤ 0.05 pF, not mounted). Auris: C314 (DNP) – R310 0 Ω – C315 (DNP) at J302, matching Fig. 25.

## Layout notes and gotchas

- At least four layers; a solid reference ground directly under the module and no traces on layer 1 beneath it (Fig. 1 note 3, p. 14; Ref sheet 3 note 7). Keep ≥ 3 mm from other parts (§7.2 note, p. 55).
- VBAT trace ≥ 2 mm; C302–C306 at pins 42/43 with the smallest value nearest.
- RESET_N trace short and ground-guarded (§3.7).
- USB DP/DM 90 Ω differential, inner layer, ground above and below, no stubs (§4.1 bullets p. 32). TP309/TP310 should sit next to the module; the pads are the only load on the pair.
- RF: 50 Ω CPWG/microstrip per Figs. 26–29, 135° bends, GND pads beside pin 35 fully flooded (§5.2).
- USIM signals away from RF and VBAT; DATA and CLK separated by ground (§4.3 bullets).
- Moisture sensitivity and reflow profile: LA-HD §8.1–8.2 (bake if exposed).

## EasyEDA symbol and footprint

Source: JLCEDA/EasyEDA Official Library ([lceda.cn](https://lceda.cn/), [easyeda.com](https://easyeda.com)), record C44008839 (symbol `EG800KEULC-I03-SNNSA_C44008839`, contributor lcsc).

- **Symbol:** 109 pins numbered 1–109, every number present once. Names follow the QuecOpen symbol, not LA-HD Table 6: 11–14 are `USIM1_DATA/RST/CLK/VDD`, 82 is `USB_BOOT/KP_MKOUT[4]`, 2 is `ANT_GNSS`, 30–33 `GPIO1–4`, 49–53 `LCD_*`, 54–57 `GPIO5–8`, 68/69 `I2C1_SCL/SDA`, 74–78 `KP_*`/`LCD_TE`, 80/81/83 `GPIO10–12`, 86/87 `KP_*`, 99 `1PPS`, 104/105 `GRFC2/1`; the rest are `RESERVED`. GND (26 pins) and VBAT (42, 43) sets are identical to LA-HD. Because the capture matches **by number first**, all 109 netlist rows land on the right pins; the name differences only matter if a number lookup ever fails.
- **Footprint:** `LGA-109_L17.7-W15.8-AIR780E` — drawn by LCSC for the pin-compatible Luat Air780E, 109 pads numbered 1–109, no extra pads. Pad topology and pitches agree with LA-HD Fig. 1 and Fig. 35 (p. 55): outer ring 1.1 mm pitch (13 pads per long side at ±6.6 mm, 11 per short side at ±5.5 mm), second ring 1.2 mm pitch, third ring 1.2 mm pitch (73–80, 81–88), 107–109 bottom inner, six 1.3 mm square centre GND pads 89–94 on a 1.8 mm grid. Difference: outer pads are 1.3 × 0.6 mm reaching the body outline, where Quectel draws 1.0 × 0.6 mm starting 0.3 mm inside the outline; inner edges coincide. That is a normal hand-solder/inspection extension, but **overlay Fig. 35 on the footprint before layout** (inner-ring offsets were not measured here) and use Quectel's paste recommendation.

## Findings

| Severity | Designator / pin | Issue | Evidence | Fix |
|---|---|---|---|---|
| should fix | D205 (power sheet) protecting U301 pins 42/43 | SMAJ5.0A cannot protect the module: its breakdown (≥ 6.4 V) is above the module's VBAT absolute maximum (6.0 V), and its full clamp (≈ 9.2 V) is above C301's 8.2 V surge rating (KEMET T2076 p. 29); Quectel asks for VRWM 4.7 V with low clamp | LA-HD Table 27 p. 49; §3.4.4 p. 25; SMAJ5.0A family data from memory (not re-read) | Power sheet (already README open item 3): pick a TVS with VRWM ≥ 4.3 V (module max) and breakdown well below 6 V, or accept for rev A as surge-only. Not a U301 CSV change |
| should fix | M_PWRKEY (pin 7) | No 10 nF on PWRKEY; both Quectel drawings place 10 nF from PWRKEY to GND next to the driver; limit is ≤ 10 nF. PWRKEY also runs to an exposed pad (TP302) | LA-HD Fig. 9 p. 26, §3.7 note 2 p. 30; Ref sheet 4 (C0401 10 nF) and note 3 | Add `C316,1,1,M_PWRKEY,Y,CL05B103KB5NNNC: PWRKEY filter per Quectel Fig. 9 (≤ 10 nF)` and `C316,2,2,GND,Y,`; BOM row 10 nF X7R 0402 (e.g. C15195 — check code) |
| should fix | Pins 16, 17, 18, 22, 23, 25, 39 | Quectel asks for 22/33 pF filter capacitor footprints next to these pins when used (RF pickup on long lines); none reserved | Ref sheet 3 note 9 (drawn NM_22/33pF C0303–C0311) | Add DNP 0402 rows C317–C323 (each `…,<net>,N,DNP: 22/33 pF RF filter at module pin N per Ref sheet 3 note 9` + GND row) on M_NETSTAT, M_RXD, M_TXD, M_CTS, M_RTS, M_STATUS, M_DBG_TXD |
| should fix | U301 (procurement) | JLC stock is 4 pieces (parts.csv, checked 2026-11-17), not the 179 the README quotes | `parts.csv` row C44008839 | Order prototype quantities now or consign; refresh README open item 5 |
| note | U301 (temperature) | Normal range is −35 to +75 °C; −40 °C and anything above 75 °C fall into the extended range (functional, RF may be outside 3GPP limits); above 85 °C is out of spec, above 90 °C exceeds storage | Spec p. 2; LA-HD Table 34 p. 52, footnotes 4/5 | Firmware: skip or postpone the daily session when board temperature is above ≈ 80 °C or below −40 °C; enclosure shading. J301 (−35…+75 °C, no extended range) is the tighter limit |
| note | Firmware sequence (README step 3) | STATUS goes high ≥ 6 s after PWRKEY, but UART/USB are active only ≥ 10 s after it; sending AT on STATUS alone may hit a dead UART | LA-HD Fig. 11 p. 27 | Wait for the `RDY` URC or retry `AT` until ≈ 15 s after PWRKEY |
| note | MAIN_DTR (pin 19) open | With DTR open (= high), `AT+QSCLK=1` lets the module sleep and only DTR low wakes it over UART; Auris cannot drive DTR | LA-HD §3.2.1 p. 20 | Firmware: leave `AT+QSCLK=0` (default). The rail is cut after each session anyway |
| note | ANT_MAIN π match | Ref V1.2 adds a series 100 pF between ANT_MAIN and the π (only if the antenna port carries DC) and reserves an ESD diode (Cj ≤ 0.05 pF) | Ref sheet 9 notes 4, 9; Ref revision 1.1 | No change needed (no DC on the line, internal antenna). If the TX4G-FPC-8121 turns out to be DC-shorted, R310 can take 100 pF |
| note | TP309/TP310 USB pads | Pads are the only connection to a 480 Mbit/s pair; no ESD (Quectel wants ≤ 2 pF if fitted) | LA-HD §4.1 p. 32; Ref sheet 16 note 3 | Place pads beside the module on a 90 Ω pair; keep the service cable short; ESD by handling |
| note | Pin table source | The whole pin map comes from the LA manual (preliminary). Ref V1.2 (which covers EG800K-EU) and the EasyEDA symbol for the EU part agree for every pin used; bands, temperature and outline are now confirmed for the EU part by the Spec | LA-HD Table 6; Ref §1.1, sheet 3; Spec p. 2 | Keep README open item 1 (get the EU hardware design) |
| note | R301 0805 0 Ω | Quectel's 2 A worst-case peak passes through a jumper whose current rating is not in the JLC record | JLC C17477 attributes (no current rating listed) | Confirm the UNI-ROYAL 0805 jumper rating ≥ 2 A |
