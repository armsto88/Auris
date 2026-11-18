# EG810MEULA-I05-SNNSA — LTE Cat 1 module (Quectel EG810M-EU), LGA-109

| Field | Value |
|---|---|
| LCSC | C20421924 · JLC extended · see `parts.csv` for stock and price (JLC stock 206 on 2026-11-18) |
| Manufacturer | Quectel |
| Package | LGA, 109 pads, (17.7 +0.3/−0.15) × (15.8 +0.3/−0.15) × (1.7 ± 0.2) mm, ≈ 0.98 g (HD Table 2, p. 13) · EasyEDA footprint `LGA-109_L17.7-W15.8-P1.10_EG810M-CN` |
| Used by | lte: U301 |
| Datasheet | Quectel *EG810M-EU QuecOpen&QuecPython Hardware Design* **V1.0**, 2024-06-25, Released · https://developer.quectel.com/en/wp-content/uploads/sites/2/2024/11/Quectel_EG810M-EU_QuecOpenQuecPython_Hardware_Design_V1.0.pdf (local `pdf/Quectel_EG810M-EU_QuecOpen_QuecPython_HD_V1.0.pdf`, cited as **HD**; page numbers are the printed "N / 78" footer, PDF page = N + 1). Also Quectel *EG810M-EU LTE Cat 1 Module* specification **V1.1**, Released, 3 pages (local `pdf/Quectel_EG810M-EU_Specification_V1.1.pdf`, cited as **Spec**). The standard-firmware *EC800M & EG810M Series Hardware Design* was **not** read |
| Rated temperature | Normal operating −35 to +75 °C, extended −40 to +85 °C, storage −40 to +90 °C (HD Table 47 p. 64 and Table 4 p. 15; Spec p. 2). Normal = 3GPP-compliant; extended = still works (voice, SMS, data), but Pout and similar RF figures may fall outside 3GPP tolerance and return to spec when back in the normal range (HD p. 64 footnotes 5, 6). JLC/`parts.csv`: −35 to +75 °C |

**Why this part.** Owner decision 2026-11-18: the EG800K-EU (C44008839, [`C44008839_EG800KEULC-I03-SNNSA.md`](C44008839_EG800KEULC-I03-SNNSA.md)) had 0 JLC stock that day (4 on 2026-11-17); the EG810M-EU had 206. Quectel sells it as package-compatible with the EG800K series (Spec p. 1). Same bands for Europe and Australia: LTE-FDD **B1/3/5/7/8/20/28**, no TDD, no 2G (HD Table 3 p. 13, Table 34 pp. 54–55); CE and RCM (Spec p. 2). Data rates 10 Mbps down / 5 Mbps up (HD Table 4 p. 15). Single antenna port (ANT_MAIN, shared with a receive-only Wi-Fi scan; no diversity column in HD Table 38 p. 56). Thinner than the EG800K (1.7 mm vs 2.4 mm). Unit price at 10/100 is about $8.04/$6.39 against $5.86/$4.80 for the EG800K-EU (`review/2026-11-17-bom-cost-changes.csv`).

**Which document.** The HD read here is the QuecOpen/QuecPython edition: its operating-mode, sleep, turn-off and SIM-detect sections name C/Python APIs, not AT commands. Pin numbers, electrical limits and reference circuits are hardware facts and apply whatever firmware the module runs; the Spec lists Quectel AT commands as standard and QuecOpen/QuecPython as options (Spec pp. 1–2), and HD Table 4 p. 15 lists 3GPP TS 27.007/27.005 plus Quectel AT commands. AT-specific behaviour Auris relies on (`AT+QPOWD`, `AT+QSCLK`, the `RDY` URC) is not in this document.

## Pins

Every connected U301 row of `lte/lte-netlist.csv` against HD Table 6 (pp. 18–23). All 109 netlist pin numbers were also compared with the HD by script: **every GND pad is on GND, every pad the HD calls RESERVED is NC, and every connected pad has the same function as on the EG800K** (EG800K-LA HD V1.0.0 Table 6).

| Pin | Name (HD) | Function (HD Table 6) | Auris net | Check |
|---|---|---|---|---|
| 1, 10, 27, 34, 36, 37, 40, 41, 45–48, 70–73, 88–95 | GND | Ground, 24 pads (p. 19; Table 10 p. 28) | GND | OK — the same 24 pads as the netlist |
| 7 | PWRKEY | DI, Vnom = VBAT, VIL ≤ 0.5 V; low ≥ 700 ms to turn on, ≥ 650 ms to turn off; test point recommended (p. 19; §3.5.1 p. 30, §3.6.1 p. 31) | M_PWRKEY: Q301 collector, C316 10 nF, TP302 | OK — open-collector drive as Quectel recommends (§3.5.1); Fig. 7 values |
| 11 | USIM1_DATA | DIO, 1.8/3.0 V (p. 20) | SIM_DATA_M → R308 0 Ω | OK |
| 12 | USIM1_RST | DO (p. 20) | SIM_RST_M → R306 0 Ω | OK |
| 13 | USIM1_CLK | DO (p. 20) | SIM_CLK_M → R307 0 Ω | OK |
| 14 | USIM1_VDD | PO, 1.8 or 3.0 V, card class detected automatically (p. 20) | USIM_VDD: J301 C1, R309, C313, D301 pin 5 | OK |
| 15 | RESET_N | DI, active low, Vnom 1.8 V, VIL ≤ 0.5 V; test point recommended if unused (p. 19) | M_RESET_N: TP303 only | OK |
| 16 | NET_STATUS | DO, 1.8 V; open if unused (p. 19) | M_NETSTAT: TP305, C317 (DNP) | OK |
| 17 | MAIN_RXD | DI, 1.8 V (p. 20) | M_RXD ← U302 A2 ← ESP32 LTE_TX | OK |
| 18 | MAIN_TXD | DO, 1.8 V (p. 20) | M_TXD → U302 A1 → ESP32 LTE_RX | OK |
| 22 | MAIN_CTS | DO, "connect to the MCU's CTS" (p. 20; Table 20 p. 41) | M_CTS → U302 A4 → LTE_CTS (GPIO42, UART1 CTS) | OK — matches §4.4 note 2 (p. 42) |
| 23 | MAIN_RTS | DI, "connect to the MCU's RTS" (p. 20) | M_RTS ← U302 A3 ← LTE_RTS (GPIO41, UART1 RTS) | OK |
| 24 | VDD_EXT | PO, 1.8 V, 50 mA max; for external pull-ups; test point recommended (p. 19) | VDD_EXT: U302 VCCA, C308, R304, TP304 | OK — load well under 1 mA |
| 25 | STATUS | DO, 1.8 V, high once the module is on (p. 19; §4.12.2 p. 53) | M_STATUS → U302 A5 → LTE_STATUS (GPIO38) | OK |
| 35 | ANT_MAIN | AIO, 50 Ω; main antenna and Wi-Fi scan (p. 22; Table 33 p. 54) | ANT_MAIN → R310 0 Ω → J302 | OK |
| 38 | DBG_RXD | DI, 1.8 V; test points must be reserved (p. 21) | M_DBG_RXD: TP307 | OK |
| 39 | DBG_TXD | DO, 1.8 V; test points must be reserved (p. 21) | M_DBG_TXD: TP306, C323 (DNP) | OK |
| 42, 43 | VBAT | PI, 3.4–4.3 V, nom 3.8 V; supply ≥ 2.0 A; external TVS and a test point recommended (pp. 18–19) | VBAT_M: R301 from VMODEM 3.9 V, C301–C306, TP301 | OK (TVS: see findings) |
| 59 / 60 | USB_DP / USB_DM | AIO, USB 2.0, 90 Ω differential; test points must be reserved (p. 19) | M_USB_DP / M_USB_DM: TP309 / TP310 | OK |
| 61 | USB_VBUS | AI, 3.0–5.25 V (nom 5.0 V), USB connection detect; test point must be reserved (p. 19) | M_USB_VBUS: TP308 | OK |
| 82 | USB_BOOT/KP_MKOUT[4] | DI, 1.8 V, active low: low at turn-on forces download mode; must not be low before the module has started; test point recommended (p. 23; Table 16 p. 36). In QuecOpen it can also be keypad output 4 (Table 25 p. 47) | M_USB_BOOT → R311 4.7 kΩ → BOOT_PAD (TP311) | OK — Fig. 15 equivalent (see USB_BOOT below) |

**NC pins (all "keep open", Fig. 2 note 2 p. 17).** HD RESERVED: 2, 26, 44, 84–87, 97–103, 106–109 (p. 23; Fig. 2 also shows 99 as RESERVED). Optional functions that need Quectel's go-ahead or a codec: analog audio MIC_P/MIC_N/SPK_P/SPK_N on 3–6 (Table 27 p. 48), PCM on 30–33 (multiplexable as SPI0, Tables 21, 23 pp. 43, 45), I2C2 on 66/67 and I2C1 on 68/69 (Table 22 p. 43), USIM2 on 62–65 (Table 17 p. 38; optional, ask Quectel). Functions the Spec marks as QuecOpen-only (Spec p. 2 note ②): LCD 49–53 and LCD_TE 78 (Table 24 p. 46), camera 54–58, 80, 81 and **pin 8 CAM_VDD, a 2.8 V / 100 mA power output** (Table 26 pp. 47–48), keypad 74–77 and 83 (Table 25 p. 47), auxiliary UART 28/29 (Spec p. 2). Standard functions not used: ADC0/ADC1 on 9/96 (0–1.2 V, Table 28–30 p. 51), MAIN_DTR/RI/DCD on 19–21, USIM1_DET on 79 (Table 17 p. 38), GRFC1/GRFC2 antenna-tuner outputs on 105/104 (Table 35 p. 55). The netlist calls most of these pads `RESERVED` (it keeps functional names on 9, 19–21, 28/29, 66/67, 79 and 96); every one is NC, which matches the HD.

## Limits that matter for Auris

| Parameter | Datasheet (cite) | Auris condition | Verdict |
|---|---|---|---|
| VBAT operating | 3.4 / 3.8 / 4.3 V min/typ/max; never below 3.4 V (Table 41 p. 61; §3.4.4 p. 29) | VMODEM 3.9 V from TPS63020 (R232 680 kΩ / R233 100 kΩ, FB 0.5 V) through R301 | OK; 0.5 V droop margin, 0.4 V to the top |
| VBAT absolute max | −0.3 to 6 V; VBAT current 2 A max (Table 40 p. 61) | No TVS fitted (D205 footprint only) | See findings (TVS) |
| Supply current | Supply must deliver ≥ 2.0 A (Table 6 p. 18, §3.4.2 p. 28); peak 1.5 A typ, 2 A max at maximum power control level (Table 41 p. 61) | TPS63020 rail, C233 470 µF at the converter, C301 100 µF at the pins | Module side OK; converter and battery path are the power sheet's job |
| Transmit current | LTE data transmission, typ: B1 564, B3 532, B5 530, B7 633, B8 547, B20 526, B28 576 mA (Table 42 p. 62; power level not stated) | Power sheet assumed ≈ 0.65 A (LTE README open item 2) | Assumption now backed by a typical figure; still measure (README test 4) |
| Bulk + MLCC | ≈ 100 µF, ESR ≤ 0.7 Ω; MLCC array 100 nF, 33 pF, 10 pF, 3.9 pF, 1.8 pF near the VBAT pins; 0 Ω debug link ≥ 0603; VBAT trace ≥ 2 mm (§3.4.4, Fig. 6 p. 29) | C301 100 µF 70 mΩ polymer Ta; C302 100 nF, C303 33 pF, C304 10 pF, C305 3.9 pF, C306 1.8 pF; R301 0805 0 Ω | OK — identical values |
| PWRKEY | Low ≥ 700 ms on, ≥ 650 ms off; VBAT stable ≥ 30 ms first; capacitance on PWRKEY ≤ 10 nF (§3.5.1 p. 30, Fig. 9 note 1 p. 31, §3.6.1 p. 31, §3.7 note 2 p. 34) | Q301 + R302 4.7 kΩ + R303 47 kΩ + C316 10 nF; firmware 800 ms pulse after ≥ 30 ms of VBAT_M | OK. Q301 saturates far below VIL 0.5 V (≈ 0.54 mA base drive; see `C20526_…` note) |
| Turn-on timing | VDD_EXT ≈ 10 ms after PWRKEY falls; RESET_N up ≈ 27 ms; STATUS high ≥ 5 s; UART and USB active ≥ 10 s (Fig. 9 p. 31) | LTE README step 3 (wait for STATUS, then `RDY`/retry `AT`) | OK — the README rule is written for the EG800K (≥ 6 s / ≥ 10 s) and still holds |
| Turn-off | PWRKEY ≥ 650 ms, then 2–10 s power-down before STATUS falls (Fig. 10 p. 32); keep PWRKEY high after a software turn-off or the module turns on again (§3.6.2 note 2 p. 32); never cut VBAT while running (§3.4.2 note p. 28, §3.6.2 note 1) | README steps 5–6 | OK |
| RESET_N | Low ≥ 300 ms; VIH 1.3 V; only when software and PWRKEY turn-off fail; short trace, ground-guarded (§3.7 p. 32, Fig. 13 and notes p. 34) | Test pad only | OK |
| USB_BOOT | Low before turn-on → forced download over USB; 4.7 kΩ to GND recommended; may be driven low ≥ 1 s after VDD_EXT rises (keypad use) (§4.2 pp. 36–37, Fig. 9 p. 31, Fig. 16 notes p. 37) | R311 4.7 kΩ to BOOT_PAD, shorted to a GND pad by hand | OK |
| VDD_EXT | 1.8 V, 50 mA max (Table 6 p. 19) | U302 VCCA, R304/R305 (≈ 1.6 µA), C308 | OK |
| Digital I/O | 1.8 V domain: VIH 0.7·VDDIO…VDDIO + 0.2, VIL ≤ 0.3·VDDIO, VOH ≥ VDDIO − 0.2, VOL ≤ 0.2 V (Table 43 p. 63); abs max 2.2 V on digital pins (Table 40 p. 61) | All logic through U302 or test pads | OK — no 3.3 V signal touches the module |
| USB_VBUS | 3.0 / 5.0 / 5.25 V (Table 41 p. 61); abs max 5.5 V (Table 40) | TP308, from the service cable only | OK |
| USIM | 1.8 V class 1.62–1.98 V; 3.0 V class 2.7–3.3 V (Tables 44–45 p. 63) | D301 SRV05-4 VRWM 5 V | OK |
| ESD | VBAT/GND ±5 kV contact, ±10 kV air; antenna ±4/±8 kV; other interfaces ±0.5/±1 kV (Table 46 p. 64) | D301 at the SIM; service pads unprotected | OK for service-only pads |
| Current, off/idle | Power down 17.62 µA; idle PF 64: 19.24 mA USB disconnected, 29.34 mA USB connected; sleep 0.96–1.71 mA (PF 256…32) (Table 42 p. 62) | VMODEM switched off between sessions; USB_VBUS open in the field | Off current irrelevant (rail off). Leaving USB_VBUS open saves ≈ 10 mA idle |
| Temperature | −35…+75 °C normal, −40…+85 °C extended (Table 47 p. 64) | −40 °C winters; hot Australian enclosures | Marginal at both ends; see findings |
| Moisture / reflow | MSL 3, floor life 168 h, bake 8 h at 120 °C if exposed; peak reflow 235–246 °C, 246 °C absolute; stencil 0.13–0.15 mm (§8.1 p. 69, §8.2 p. 70) | JLC assembly | Ask JLC to keep the reel sealed/baked |

## Required external parts and equations

Compared one by one with the LTE BOM and netlist. Values are the same as for the EG800K (see the EG800K note for the derivations, which still apply).

- **VBAT** (§3.4.4, Fig. 6 p. 29). HD: TVS D1 (VRWM 4.7 V, low clamp) at the supply end, C1 100 µF + C2–C6 100 nF / 33 pF / 10 pF / 3.9 pF / 1.8 pF, then R1 0 Ω into the module. Auris: C301–C306 exactly these values, R301 0805 0 Ω, **no TVS** (D205 not fitted, owner decision 2026-11-17). Topology difference as before: Quectel puts the 0 Ω between the capacitor array and the pins; Auris puts the array on the module side of R301, which keeps the capacitors at the pins and is acceptable. Droop budget (3.9 − 3.4) V = 0.5 V at up to 2 A. HD Fig. 5 (p. 28) shows a regulator with 470 µF + 100 nF at its output; Auris has C233 470 µF at VMODEM.
- **PWRKEY** (Fig. 7 p. 30). HD: NPN with 4.7 kΩ base resistor, 47 kΩ base–emitter, 10 nF from PWRKEY to GND. Auris Q301 MMBT3904, R302 4.7 kΩ, R303 47 kΩ, C316 10 nF X7R — **identical**. No external pull-up: PWRKEY's nominal level is VBAT (Table 6 p. 19).
- **RESET_N** (Figs. 11–12 p. 33). HD: same NPN driver as PWRKEY, or a button with 1 kΩ and a TVS. Auris: test pad only, which the HD allows for an unused RESET_N (Table 14 p. 33).
- **USB_BOOT** (Fig. 15 p. 37). HD: test points on the pin, then 4.7 kΩ to GND; optional TVS near the test points. Auris: R311 4.7 kΩ from pin 82 to BOOT_PAD (TP311), which the technician shorts to a GND pad. Electrically the same (4.7 kΩ to GND while shorted); the resistor sits on the module side, so the exposed pad is behind 4.7 kΩ. No TVS (optional in Fig. 15).
- **USB** (§4.1, Fig. 14 p. 35, bullets p. 36). HD: test points must be reserved; for a host link it adds a common-mode choke and 0 Ω (not mounted) between module and test points, ESD < 2 pF. Auris has no USB host on this pair: TP309/TP310 (DP/DM) and TP308 (VBUS) are the only loads, so no choke or links. The pair should still be 90 Ω and stub-free.
- **USIM** (§4.3, Fig. 18 p. 40, bullets p. 40). HD (6-pin holder, no detect): 0 Ω in series on RST/CLK/DATA, 33 pF to GND on each, 100 nF on USIM_VDD (≤ 1 µF, at the holder), 15 kΩ DATA pull-up to USIM_VDD, TVS array < 15 pF, trace ≤ 200 mm. Auris R306–R308 0 Ω, C310–C312 33 pF, C313 100 nF, R309 15 kΩ, D301 SRV05-4 (≤ 5 pF), USIM_DET open. **All values match.** Fig. 17 (p. 39) adds 51 kΩ USIM_DET to VDD_EXT only for an 8-pin holder with detect.
- **UART** (§4.4, Fig. 19 p. 42). HD: TXS0108EPWR, 0.1 µF on VCCA and VCCB, OE from VDD_EXT through 10 kΩ with 120 kΩ to GND, unused channel A8/B8 51 kΩ to GND on each side; module CTS to MCU CTS, RTS to RTS; hardware flow control recommended. Auris U302 TXS0108EPWR, C308/C309 100 nF, **OE divider R304 100 kΩ / R305 1 MΩ** (0.91 × VDD_EXT vs Quectel's 0.92 ×), **A6–A8/B6–B8 open**. Both differences are analysed in `C17206_TXS0108EPWR.md` (open channels are consistent with TI's datasheet). Channel order differs from Fig. 19 (A1 = TXD … A5 = STATUS on Auris), which is free on this part.
- **UART filter capacitors** C317–C323 (33 pF, DNP) on M_NETSTAT, M_RXD, M_TXD, M_CTS, M_RTS, M_STATUS, M_DBG_TXD come from the EG800K QuecOpen Reference Design (sheet 3 note 9). This HD asks only for an RC (0 Ω/33 pF) on PCM traces (§4.5 note 2 p. 45), which Auris does not use. The DNP footprints cost nothing; keep them.
- **Antenna** (§5.1.5, Fig. 30 p. 56, notes p. 57). HD: a "dual L" network — R1 0 Ω series, C1/C2 shunt not mounted, C3 100 pF series only if the antenna port carries DC (otherwise do not reserve it), ESD with Cj < 0.05 pF optional, all placed close to the antenna. Auris C314 (DNP) – R310 0 Ω – C315 (DNP) at J302, no DC block, no ESD. **Matches.** Antenna: VSWR ≤ 2, efficiency > 30 %, 50 Ω, cable loss < 1 / 1.5 / 2 dB for < 1 GHz / 1–2.3 GHz / > 2.3 GHz (Table 39 p. 59); Hirose U.FL-R-SMT recommended (§5.4 p. 59) — J302 is that part.
- **Status outputs** (Figs. 28–29 pp. 52–53). HD drives LEDs from NET_STATUS/STATUS with an NPN. Auris reads STATUS through U302 and brings NET_STATUS to TP305 only. Fine.

## Layout notes and gotchas

- At least four layers; uninterrupted ground plane directly under the module; no other traces on layer 1 next to the module (Fig. 2 note 4, pp. 17–18). Keep ≥ 3 mm between the module and other parts (Fig. 40 note p. 67).
- VBAT trace ≥ 2 mm; C302–C306 at pins 42/43 (§3.4.4 p. 29).
- RESET_N short and ground-guarded (§3.7 p. 32).
- USB DP/DM 90 Ω differential on an inner layer, ground on that layer and planes above and below; no signals under VBAT, crystals or magnetics (§4.1 p. 36).
- USIM: holder close, ≤ 200 mm; away from RF and VBAT; DATA and CLK apart with ground between (§4.3 p. 40).
- RF: 50 Ω (simulated), GND pads beside RF pins without thermal relief, 135° bends, clearance under the connector signal pin, ground vias ≥ 2 W from the trace; keep away from DC-DC, SIM/USB/SDIO and clock lines (§5.2 pp. 57–58).
- Antenna isolation ≥ 20 dB between antennas (Fig. 30 note 1 p. 57). On Auris that is the LTE FPC antenna vs the ESP32-S3 PCB antenna: B7 transmits at 2500–2570 MHz (Table 34 p. 54), next to the ESP32's 2.4 GHz band.
- Moisture and reflow: §8.1–8.2 pp. 69–70 (MSL 3; bake if the reel has been open > 24 h).

## EasyEDA symbol and footprint

Source: JLCEDA/EasyEDA Official Library ([lceda.cn](https://lceda.cn/), [easyeda.com](https://easyeda.com)), record C20421924 (symbol `EG810MEULA-I05-SNNSA`, contributor lcsc), read 2026-11-18.

- **Symbol:** 109 pins numbered 1–109, each once. Names follow the standard-firmware pin map: USIM_DATA/RST/CLK/VDD (HD: USIM1_*), USIM_DET, USB_BOOT, I2C_SDA/I2C_SCL on 66/67, and RESERVED for the QuecOpen-only pads and most optional ones (USIM2, I2C1, GRFC, CAM_VDD) — so the names of all 46 connected netlist rows (22 signal and supply pins, 24 GND) match the symbol **by number and by name**. Name differences only on NC pads: 2 `ANT_GNSS` (HD: RESERVED; no GNSS on the EU part), 3–6 `MIC_P/MIC_N/SPK_P/SPK_N`, 30–33 `PCM_CLK/SYNC/DIN/DOUT`, 26 `RESERV` (truncated); the netlist calls these RESERVED. All 109 rows match by number, which is what the capture uses first.
- **Footprint:** `LGA-109_L17.7-W15.8-P1.10_EG810M-CN` (drawn by LCSC for the EG810M-CN; its link points to the EG810M-CN hardware design V1.0), 109 pads numbered 1–109, no extra pads. **Different from the EG800K footprint** (`LGA-109_L17.7-W15.8-AIR780E`), so the PCB footprint changes when U301 is re-captured. Pad-by-pad comparison of the two library records: pads 45–94 and 99–109 (inner rings, centre GND squares) are identical in position and size (1.0 × 0.7 mm; 1.3 mm squares on a 1.8 mm grid); the 48 outer-ring pads (1–44, 95–98) keep their pitch and inner edge but are 1.0 × 0.7 mm ending 0.3 mm inside the outline, where the AIR780E footprint has 1.3 × 0.6 mm pads reaching the outline. Against HD Fig. 40 (p. 67): outer pads 1.0 × 0.6 mm set 0.3 mm in from the outline, inner rings 1.0 × 0.7 mm, centre 1.3 mm squares on 1.8 mm, outer pitch 1.1 mm (12 × 1.1 = 13.2 and 10 × 1.1 = 11), inner pitch 1.2 mm, 4.15/5.95 mm row offsets — all agree **except the outer-pad width: 0.7 mm in the library vs 0.6 mm in Fig. 40** (copper gap 0.4 mm instead of 0.5 mm at 1.1 mm pitch). Overlay Fig. 40 on the footprint at layout and use Quectel's stencil thickness (§8.2).

## Findings

| Severity | Designator / pin | Issue | Evidence | Fix | Status |
|---|---|---|---|---|---|
| note | Source document | Compared against the QuecOpen&QuecPython HD; the standard-firmware *EC800M & EG810M Series Hardware Design* was not read. Pin functions, limits and reference circuits are hardware facts and agree with the EG800K design for every pin Auris connects; AT-command behaviour (`AT+QPOWD`, `AT+QSCLK`, `RDY`) is not covered by this HD | HD §3.1–3.7 (APIs, not AT); Table 4 p. 15 (AT command support); Spec pp. 1–2 | Get the standard HD and the EG810M AT command manual before firmware bring-up; check `AT+QPOWD` and `AT+QSCLK` there | open (LTE README open item 1, now for the EG810M-EU) |
| should fix | D205 (power sheet) / pins 42, 43 | HD recommends an external TVS on VBAT (VRWM 4.7 V, low clamp); none is fitted. Unchanged from the EG800K: abs max VBAT 6 V | Table 6 p. 18–19, Table 10 p. 28, §3.4.4 p. 29, Table 40 p. 61 | Power sheet / rev B decision, not a U301 change | owner decision (review P10/L6): D205 not fitted; rev B part open (LTE README open item 3) |
| note | U301 footprint | New library footprint (`…_EG810M-CN`) replaces the AIR780E one: inner pads identical, outer ring 1.0 × 0.7 mm inset 0.3 mm instead of 1.3 × 0.6 mm to the outline; vs Quectel Fig. 40 the outer pads are 0.1 mm wider (0.7 vs 0.6 mm) | EasyEDA C20421924 vs C44008839; HD Fig. 40 p. 67 | At layout: overlay Fig. 40, re-run the PCB net check after re-capture; optionally narrow the outer pads to 0.6 mm in a project copy | open (layout) |
| note | U301 (temperature) | Normal range −35…+75 °C; −40 °C and 75–85 °C are the extended range (works, RF may be outside 3GPP); above 85 °C out of spec, above 90 °C beyond storage | HD Table 47 p. 64, footnotes 5–6; Spec p. 2 | Firmware: skip or postpone the session above ≈ 80 °C board temperature or below −40 °C; enclosure shading. J301 (−35…+75 °C storage only) is the tighter limit | open (firmware; carried over from the EG800K note) |
| note | Firmware sequence (README step 3) | STATUS high ≥ 5 s after PWRKEY, UART/USB active only ≥ 10 s after it | HD Fig. 9 p. 31 | Keep the README rule: wait for `RDY` or retry `AT` until ≈ 15 s after PWRKEY | open (firmware) |
| note | C316 / pin 7 | C316 10 nF ±10 % sits at the HD's "never more than 10 nF" limit on PWRKEY, plus TP302 and trace capacitance; Quectel's own Fig. 7 uses the same 10 nF | HD §3.7 note 2 p. 34; Fig. 7 p. 30 | None (follows Quectel's reference) | — |
| note | MAIN_DTR (pin 19) open | The QuecOpen HD does not cover DTR-controlled sleep; with the EG800K, `AT+QSCLK=1` and DTR open meant the host could not wake the module | HD §3.2 p. 26 (API sleep, USB_VBUS must be disconnected); EG800K-LA HD §3.2.1 | Firmware: keep `AT+QSCLK=0` (default); the rail is cut after each session anyway | open (firmware) |
| note | Spec vs HD current | Spec p. 3 gives idle 19.2 mA "USB connected" and 29.3 mA "USB disconnected" and 0.73 mA "LTE sleep"; HD Table 42 gives 19.24 mA disconnected / 29.34 mA connected, and 0.73 mA is minimum-functionality mode (sleep 0.96–1.71 mA). The HD figures are the consistent set | Spec p. 3; HD Table 42 p. 62 | Use the HD numbers in power budgets | — (document error) |
| note | Product category | Spec and BOM call it "LTE Cat 1"; HD Table 4 p. 15 lists "3GPP Rel-13 Cat 1 bis FDD". Single antenna port and no diversity either way (Table 38 p. 56). No board impact | Spec p. 1; HD Table 4, Table 38 | Docs may use either term; data rates 10/5 Mbps | — |
| note | R301 0805 0 Ω | Up to 2 A peak through a jumper whose current rating is not in the JLC record | HD Table 41 p. 61; JLC C17477 | Confirm the UNI-ROYAL 0805 jumper rating ≥ 2 A | open (review L9, carried over) |
| note | U302 unused channels, OE divider | Fig. 19 pulls the unused A8/B8 to GND via 51 kΩ and uses 10 kΩ/120 kΩ on OE; Auris leaves A6–A8/B6–B8 open and uses 100 kΩ/1 MΩ | HD Fig. 19 p. 42; `C17206_TXS0108EPWR.md` | None (analysed in the U302 note) | — |
| note | Antenna isolation | HD asks ≥ 20 dB between antennas; the ESP32 PCB antenna and the LTE FPC antenna share the enclosure, and B7 transmits at 2.5–2.57 GHz | HD Fig. 30 note 1 p. 57; Table 34 p. 54 | Enclosure/antenna placement (ADR-020); check during RF bring-up (LTE README test 7) | open (layout, RF) |
