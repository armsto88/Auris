# Auris schematic review — 2026-11-17

**Scope.** All four sheets as captured in EasyEDA Pro (POWER, AUDIO, LTE, MCU), checked as a system against the requirements (docs 00, 04, 06, 07, 11, 15, 19, 20, the ADRs) and part by part against manufacturer datasheets. Nothing has been built or measured; every number below is from a datasheet or a calculation.

**Sources.** Per-part notes with pin tables, limits and citations are in [`../datasheets/`](../datasheets/README.md) (one file per IC, module, connector, FET, diode, crystal, inductor and polarised part). Datasheet revisions read are in `../datasheets/sources.csv` and in each part file. BOM changes and prices are in [`2026-11-17-bom-cost-changes.csv`](2026-11-17-bom-cost-changes.csv).

**Severity:** **blocker** = the board cannot work or be built as drawn · **must fix** = wrong against a datasheet or requirement · **should fix** = works, but outside guidance or with no margin · **note** = check on the bench or at layout.
**Status:** **fixed** = changed in the CSVs and re-captured · **owner decision** = decided by the owner on 2026-11-17 (or on 2026-11-18 where dated) and applied · **needs owner decision** · **open** = for layout, bench or firmware.

## Summary

| | Count | |
|---|---:|---|
| Blockers | 2 | W1 modem not orderable (owner decision 2026-11-18: EG810M-EU) · W2 USB D+ back-feed kept the board on (fixed) |
| Must fix | 9 | all fixed or applied (W3 stock, P1 L201, P2 F202, P3 R237, P4 BT201, A1 C127, A2 U104, L2 J301 tabs; M2 module temperature by owner decision 2026-11-18: N16R2) |
| Should fix | 33 | 21 fixed, 7 applied as owner decisions (W12 and W17 on 2026-11-18), 5 open (W6, W7, W8 for the microSD and SIM holders, A5, L7) |
| Notes | 18 | Bench, layout and firmware items |

Cross-references (P14 = W10, P15 = W3, A4 = W16, L1 = W1, L6 = P10, M1 = W2, M3 = W15, M9 = W8) are counted once.

**Update 2026-11-18:** the owner decided the five open items (W1, M2, W17, W12 and the CR1220 cell in W8). The findings below are kept as written on 2026-11-17, with their status updated. Details, cost and capture state are in [section 8](#8-follow-up-2026-11-18-owner-decisions).

**What changed on the schematic** (all four pages re-captured and saved; export in `hardware/2026-11-17/`):

- USB ESD array no longer references VBUS (blocker W2); VBUS has its own ESD diode.
- Charger inductor 22 → 47 µH (CN3791 rules); battery fuse 1.1 A → 2.0 A hold (heat derating); modem power-good pull-up 10 k → 1 M; ESP32 EN now driven by the 3.3 V converter's power-good.
- Polarised parts BT201 and C127 now wired by pin number (pad 1 = +).
- Quectel and Espressif guidance added: PWRKEY 10 nF, OE without an RC, UART filter footprints, GPIO0 pull-up, SD_CLK series resistor, input cap for the keep-alive LDO.
- Owner decisions: shells/tabs to GND, card detect on GPIO3, D205 not fitted, −40…+85 °C switches, cold cut-out +5 °C, JST-compatible battery connector for rev A.
- BOM cost pass: 15 extended parts moved to JLC basic/preferred equivalents.
- 2026-11-18 owner decisions (section 8): EG810M-EU modem, ESP32-S3-WROOM-1-N16R2 module, microSD ESD array D403, test pads TP404–TP415, Panasonic BR1220 cell. Applied in the EasyEDA project (re-imported 2026-11-18, now named `AURIS`); the PCB net check passes again; latest export in `hardware/2026-11-19/`.

**BOM cost** (JLCPCB parts plus Economic PCBA feeder fee of $3.07 per unique extended part; PCB, setup, stencil and joints excluded):

| | 10 boards | 100 boards |
|---|---:|---:|
| Before: parts / fees / **total per board** | $29.14 / $21.18 / **$50.32** | $23.33 / $2.12 / **$25.45** |
| After: parts / fees / **total per board** | $29.74 / $16.27 / **$46.01** | $23.77 / $1.63 / **$25.40** |
| 2026-11-18 owner decisions: parts / fees / **total per board** | $32.05 / $16.27 / **$48.32** | $25.82 / $1.63 / **$27.44** |
| Unique codes, extended | 107 → 102, 69 → 53 (unchanged on 2026-11-18) | |

The cost pass alone saves $4.72/board at 10 and $0.54 at 100 (15 fewer extended parts, $0.08–0.11 cheaper parts). The fixes add $0.45–0.59/board (mostly the TS5A23166 that replaces the out-of-stock switch) and the owner's climate decisions $0.18–0.23/board. The modem ($4.80–5.86), ESP32 module ($3.75–4.71), PCM1863 ($2.43–2.88) and DS3231M ($2.24–2.73) are about 55 % of the part cost and were not changed. On 2026-11-18 the owner changed the modem and the module variant: +$2.31/board at 10 and +$2.04 at 100, mostly the modem (section 8).

---

## 1. Whole design

### Power tree, sequencing and what stays alive

RAW_BAT (pack → F202 → Q205) feeds the always-on TPL720F33 keep-alive (RTC VCC, latch pull-ups) and the main switch Q210. Q210 → VBAT_SW feeds the TPS63802 3.3 V (EN tied on), the TPS63020 3.9 V modem rail (EN = MODEM_EN, pulled low), the TPS7A2033 audio LDO (EN = AUDIO_EN, internal pull-down) and the battery divider. Defaults at power-up are all off except 3V3; the ESP32 is now held in reset until 3V3 is above 95 % (W15). The panel side (charger, HT7533, TMP390) is powered only by the panel.

### Sleep current

Corrected in `power/README.md`: ≈ 106 µA typical at 25 °C (≈ 157 µA with datasheet maxima), ≈ 0.01 Wh/day — inside the 200 µA / 0.02 Wh/day budget (doc 19). The DS3231M dominates (≤ 130 µA). Above ≈ 70 °C the two Schottky diodes' leakage exceeds the budget (W4).

### Findings

#### W1 · blocker · LTE U301 — the EG800K-EU cannot be ordered for a JLC build
- **Wrong:** JLC shows 4 in stock and none on pre-sale (2026-11-17); the module appears only as zero-stock "global sourcing" placeholders (e.g. C9900199191). The README's 151/179 figures are from 2026-10-23.
- **Evidence:** JLCPCB part record C44008839, 2026-11-17 (`../datasheets/parts.csv`).
- **Fix:** buy the prototype quantity now from LCSC or another distributor and consign it, or order it through JLC global sourcing. The A7670G remains the global alternate (different footprint).
- **Status:** owner decision 2026-11-18. JLC stock of the EG800K-EU was 0 that day, so U301 is now the Quectel **EG810M-EU** (EG810MEULA-I05-SNNSA, C20421924, 206 at JLC): same LGA-109 package and the same function on every pin Auris connects (section 8).

#### W2 · blocker · MCU D401 pin 5, power Q209 — the board could never turn off
- **Wrong:** D401's positive reference (pin 5) was on VBUS. The ESP32-S3 enables its USB D+ pull-up at reset, so with no cable D+ (≈ 3.3 V) fed VBUS through D401's steering diode: VBUS ≈ 2.7 V, USB_WAKE ≈ 1.8 V, above the 2N7002's typical threshold. Q209 then held the wake latch on and releasing PWR_HOLD did nothing.
- **Evidence:** ESP32-S3 datasheet v2.2 Table 2-1 (GPIO20 "USB_PU" at and after reset); Semtech SRV05-4 rev 08/11/04 p.5 (pin 5 may be left open, option 3); JSCJ 2N7002 Vth 1.0/1.6/2.5 V.
- **Fix:** D401 pin 5 → NC; new D402 TPD1E10B06 (C48260, already on the audio BOM) on VBUS. Bring-up test 4 now checks VBUS stays < 0.5 V with the ESP32 running and no cable.
- **Status:** fixed.

#### W3 · must fix · supply — three fitted parts had no stock at JLC
- **Wrong:** EG800K-EU (W1), SN74LVC2G66DCUR (U104, every DCU variant at 0) and JST S2B-PH-SM4-TB (J203, 0).
- **Fix:** U104 → TS5A23166DCUR (A2); J203 → XYECONN XY-S2B-PH-SM4-TB for rev A (owner decision, P15).
- **Status:** fixed / owner decision; the modem by owner decision on 2026-11-18 (W1).

#### W4 · should fix · power — sleep budget missed the charger and diodes
- **Wrong:** The README table omitted the CN3791 BAT+CSP current (≈ 9 µA typ, 15 µA max) and D203/D204 leakage (≈ 2 µA at 25 °C, ≈ 25 µA at 60 °C, ≈ 180 µA at 85 °C), and counted the Q205 gate divider (3.8 µA) that does nothing.
- **Evidence:** CN3791 Rev 1.0 p.4, p.9; PMEG4010CEH Rev 02 Fig. 2.
- **Fix:** table corrected; R215 not fitted (P6).
- **Status:** fixed.

#### W5 · should fix · firmware/power — any ESP32 reset powers the board off
- **Wrong:** PWR_HOLD (GPIO10) returns to an input on every reset (watchdog, brown-out, EN), so the latch drops power. If the next A1 alarm had already been cleared, the unit sleeps until the daily A2 window: up to a day of missed slots against H-01 (99.5 %).
- **Evidence:** ESP32-S3 datasheet v2.2 Table 2-1 (pin states at reset); wake latch in `power-netlist.csv`.
- **Fix:** firmware rule in `power/README.md` and `mcu/README.md`: arm the next alarm early and clear the RTC alarm flag only at the commit step, so the asserted INT keeps the board powered through a reboot; never release PWR_HOLD during a flash write.
- **Status:** fixed in the docs; firmware open.

#### W6 · should fix · power Q210/C218 — no soft start on the main switch
- **Wrong:** C218 sits gate–source and was labelled "soft start"; Q210 turns on in microseconds. Estimated inrush into VBAT_SW 5–12 A for 0.2–0.4 ms (C219 470 µF) with a 10–28 A, ~10 µs spike into the ceramics — inside the AO3401A's pulse rating, but the pack's protection IC is unknown.
- **Fix:** notes corrected; bring-up test 2 measures the battery-lead current. If the pack trips: 10 kΩ in series with the gate pull-down plus ≈ 220 nF gate–drain (ADR-003 block, owner decision).
- **Status:** open (bench).

#### W7 · should fix · power U207 — modem rail start-up sags VBAT_SW
- **Wrong:** The TPS63020 has no adjustable soft start and starts at its current limit; charging ≈ 600 µF (C233 + C301 + ceramics) draws ≈ 4 A for ≈ 0.4 ms, estimated to sag VBAT_SW by 1–1.5 V, which drops the audio LDO out.
- **Evidence:** TPS63020 SLVS916I §7.4.1.
- **Fix:** firmware never enables the modem rail during a recording (power and LTE READMEs); test 8 scopes VBAT_SW, 3V3 and AVDD_A with and without C233; C233 can be left off later (C301 already gives Quectel's ≥ 100 µF).
- **Status:** open (bench); rule documented.

#### W8 · should fix · climate — parts rated below the −40 °C / hot-enclosure envelope
| Part | Rated | Status |
|---|---|---|
| U401 ESP32-S3-WROOM-1-N16R8 | −40…+65 °C (+85 °C with PSRAM ECC, at 1/16 of the PSRAM) | owner decision 2026-11-18: **N16R2** (C2913205), −40…+85 °C, same footprint (ADR-001, M2) |
| SW201, SW202 | −25…+70 °C | owner decision: replaced by −40…+85 °C parts |
| J203 XYECONN (rev A) | −25…+85 °C (JLC); genuine JST PH −40…+105 °C | owner decision: clone for rev A, genuine for deployment |
| J402 microSD holder | storage −25…+85 °C, no operating range (passed −55↔+85 °C shock) | open: qualify at −40 °C or pick a −40 °C holder |
| J401 USB-C | −25…+85 °C | note: service port only |
| J301 nano-SIM holder | −35…+75 °C, consumer | open: MFF2 eSIM in rev B (LTE open item 6) |
| U301 EG800K-EU | −35…+75 °C operating, −40…+85 °C extended | note: gate LTE sessions on board temperature. The EG810M-EU fitted since 2026-11-18 has the same ratings |
| CR1220 cell (not on BOM) | typically −30…+60/70 °C | owner decision 2026-11-18: Panasonic **BR1220** (BR-1220/BN), −30…+80 °C, hand-fitted. No CR1220-size cell is rated to −40 °C; bench-test at −40 °C (section 8) |
| U207 TPS63020, OPA1662, TS5A23166, crystal, X5R MLCCs, CN3791, DS3231M, LDOs | +85 °C ambient | note |

#### W9 · should fix · power — panel input accepts 6 V-class panels only
- **Wrong:** The R239 note ("12 V reads 1.57 V") implied 12 V panels. Their open-circuit voltage (22–25 V) is above D201's 13.3 V breakdown, so D201 would conduct continuously and burn; the CN3791 would also need ≈ 100 µH.
- **Evidence:** SMF12CA (Jingdao 2020.10); CN3791 Rev 1.0 p.8.
- **Fix:** README P3 and the R239 note now say 6 V-class panels only (Voc ≤ 10 V at −40 °C).
- **Status:** fixed.

#### W10 · should fix · power U203 — charge temperature window
- **Wrong:** The TMP390's trip accuracy (±1.5/±2.5 °C) let the 0 °C setting charge down to ≈ −2.5 °C, against F4-05 (no charging below 0 °C). The sensor reads the PCB, not the cells, and an open TMP390 output lets R210 pull TEMP_FAULT_N high, which enables charging.
- **Evidence:** TMP390 SBOS904A Table 7-2 (only 5 °C steps).
- **Fix:** cold trip +5 °C (R209 18.7 kΩ), owner decision 2026-11-17; within the 0–70 °C accuracy band (±1.5 °C) it trips at +3.5…+6.5 °C. Placement near the pack and the open-output failure mode stay open.
- **Status:** owner decision; placement open.

#### W11 · note · cross-sheet nets
Every cross-sheet signal has one name on every sheet (3V3, VBAT_SW, VMODEM, VBUS, GND, the AUD_*, LTE_*, MODEM_*, SYS_* and ADC nets); voltage domains and directions agree with the port tables. New port: ESP_EN (power → MCU). The only single-pin nets are the documented DNP options (AUD_INT_MCU, AUD_MCLK, MIC1_DC_SENSE). USB_VSENSE is gone (GPIO3 is now SD_CD).

#### W12 · should fix · bring-up and test access
- **Wrong:** Doc 04 §6 asks for test pads on PWR_HOLD, RTC INT, I²C, I²S, modem UART/status and USB. Missing: PWR_HOLD, SYS_SDA/SCL, AUD_SDA/SCL, SD_VDD, LTE_STATUS, and UART0 (SD_D0/STATUS_LED) for Espressif's UART-only RF test firmware. Current measurement: only R301 (modem); sleep current is measured at J203 with a bench supply.
- **Fix:** add the pads at layout (copper only). The library test point has a 0.5 mm pad; the BOM asks for 1.0 mm (capture item 4).
- **Status:** owner decision 2026-11-18: TP404 PWR_HOLD, TP405/TP406 SYS_SDA/SCL, TP407/TP408 AUD_SDA/SCL, TP409 SD_VDD, TP410 LTE_STATUS, TP411/TP412 LTE_TX/RX, TP413 STATUS_LED = U0TXD, TP414 SD_D0 = U0RXD, TP415 3V3 on the MCU sheet. TP401–TP403 (BOOT, EN, GND) and TP413–TP415 in one 2.54 mm row for a pogo-pin jig. The 1.0 mm pad footprint remains a layout item.

#### W13 · note · LTE bands and regions
The EG800K Series Specification V1.3 confirms the EU variant's LTE-FDD B1/3/5/7/8/20/28, no GNSS, CE and RCM: it covers the main European and Australian LTE bands. Operator acceptance (e.g. Telstra) is still open (doc 15 R11). The EG810M-EU Specification V1.1 gives the same bands, no TDD, CE and RCM for the module fitted since 2026-11-18.

#### W14 · note · MCU pin budget
Every GPIO is used once; GPIO35–37 (octal PSRAM) are NC (free on the N16R2 fitted since 2026-11-18, still NC as spares); analogue inputs are on ADC1; USB is on GPIO19/20; GPIO47/48 run at 3.3 V on this module. Straps are safe: GPIO0 pulled up (now also externally), GPIO45 held low by R402 (high would select 1.8 V flash and stop the boot), GPIO46 NC, GPIO3 ignored with default eFuses. Full table in `../datasheets/C2913202_ESP32-S3-WROOM-1-N16R8.md`.

#### W15 · should fix · MCU ESP_EN — reset supervision
- **Wrong:** RC-only EN reset on a board that is power-cycled every job.
- **Evidence:** Espressif ESP32-S3 hardware design guidelines §1.3.3; TPS63802 SLVSEU9D §9.3.10 (PG low below 90 %, sinks 1 mA).
- **Fix:** U206 PG → ESP_EN (R401 pull-up, C403 kept); R229 removed. Note: when PG pulls low it also discharges C403 (1 µF), a brief peak above the datasheet's 1 mA test condition (≤ 5 µJ); acceptable, or add ≈ 1 kΩ between PG and ESP_EN.
- **Status:** fixed.

#### W16 · should fix · audio — low-battery floor
- **Wrong:** Below VBAT_SW ≈ 3.32 V the audio LDO is in dropout and AVDD_A follows the battery; the PCM1863 has no brown-out detector or reset pin.
- **Evidence:** TPS7A20 SBVS338H §6.4.3; PCM186x SLAS831D §7.3, §11.3.
- **Fix:** audio README: record only with VBAT_SW ≥ 3.35 V under load; check the clock registers before every recording and re-initialise on a mismatch.
- **Status:** fixed in docs; firmware open.

#### W17 · note · storage
1-bit SD on GPIO47/48/44 with a switched card supply; pull-ups to the switched SD_VDD are right. GPIO44 (U0RXD) has a pull-up at reset that back-feeds SD_VDD; firmware rule added (`mcu/README.md`). The card detect now goes to GPIO3. The slot is user-accessible but its signals have no ESD protection.
- **Fix:** an SRV05-4 on CLK/CMD/D0/D3 (part already on the BOM; reference to 3V3, not SD_VDD).
- **Correction (2026-11-18):** D3 is not wired to the ESP32 in 1-bit mode (only the R413 pull-up), so the four lines that reach ESP32 pins are CLK, CMD, D0 and card detect (CD). D1–D3 reach only 10 kΩ pull-ups to SD_VDD.
- **Status:** owner decision 2026-11-18: D403 SRV05-4.TCT (C13612, same part as D301 and D401, no new feeder fee) at J402 on SD_CLK (card side of R418), SD_CMD, SD_D0 and SD_CD; pin 2 to GND by its own via beside J402, pin 5 (REF2) to 3V3, which is never below SD_VDD, so nothing back-feeds; 3V3 is off in sleep. 3 pF typical, 5 pF maximum per line.

---

## 2. POWER sheet

#### P1 · must fix · L201 — inductor too small for the CN3791
- **Wrong:** 22 µH. The CN3791 asks for L > 5 × (VCC − VBAT) µH and ripple ≤ 0.3 × ICH; at the cold Voc (8.3 V) with a 3.0 V cell that needs ≥ 27 µH, and ≥ 38 µH for the ripple rule. Its 510 mΩ also wasted ≈ 0.18 W while charging.
- **Evidence:** CN3791 Rev 1.0 p.8 (formulas on the page image).
- **Fix:** 47 µH Sunlord SWPA6045S470MT (C36414): 1.4 A saturation, 0.20 Ω, 6 × 6 mm, 16k in stock, cheaper. Worst-case peak ≈ 0.77 A.
- **Status:** fixed.

#### P2 · must fix · F202 — battery fuse too small when warm
- **Wrong:** 1812L110PR holds 1.10 A at 20 °C but only 0.80 A at 60 °C and 0.60 A at 85 °C, against ≈ 1 A modem bursts from a 3.0 V cell; R1max 0.21 Ω.
- **Evidence:** Littelfuse 1812L series (07/21/17), hold-current derating table.
- **Fix:** 1812L200THPR (C207074): 1.50 A at 60 °C, 1.29 A at 85 °C, R1max 0.07 Ω, same 1812 footprint. Its 3.5 A trip is above the JST PH's 2 A; the pack's own protection covers 2–3.5 A faults. F201 stays (needs ≥ 10 V; 0.68 A hold at 65 °C against ≈ 0.5 A).
- **Status:** fixed.

#### P3 · must fix · R237 / U207 pin 14 — modem power-good could not read low
- **Wrong:** 10 kΩ to 3V3 asks the PG pin to sink 330 µA; its low level (≤ 0.4 V) is specified only at 10 µA, so MODEM_PG might stay above the ESP32's 0.825 V input-low limit.
- **Evidence:** TPS63020 SLVS916I §6.5 p.6 and Fig. 7; EVM SLVU365 Fig. 9 (1 MΩ). PG flags current limit, not output voltage (§7.3.4).
- **Fix:** R237 → 1 MΩ; firmware reads MODEM_PG only with MODEM_EN high.
- **Status:** fixed.

#### P4 · must fix · BT201 pins — CR1220 holder was unwired
- **Wrong:** Netlist pins "+"/"−"; the EasyEDA symbol (C70381) has pins 1/2 only.
- **Evidence:** EasyEDA footprint BAT-SMD_CR1220-2 draws "+" at pad 1 and "−" at pad 2 (document layer); the symbol's long plate is on pin 1. The maker drawing could not be obtained (LCSC has delisted it).
- **Fix:** BT201 1 = + (RTC_VBAT), 2 = − (GND). Meter-check the first board before fitting U205.
- **Status:** fixed (re-captured, wired).

#### P5 · should fix · R225 — USB wake gate drive
- **Wrong:** 47 k/100 k gave Q209 3.0–3.6 V of gate drive against a threshold of up to 2.5 V.
- **Evidence:** JSCJ 2N7002 (J, Sep 2016).
- **Fix:** R225 → 10 kΩ (4.5 V; JLC basic).
- **Status:** fixed.

#### P6 · should fix · R215 — Q205 gate divider does nothing
- **Wrong:** R214 alone holds the gate at GND and blocks a reversed pack the same way; R215 cost 3.8 µA permanently.
- **Fix:** R215 not fitted.
- **Status:** fixed.

#### P7 · should fix · C228, C229 — TPS63020 input capacitors
- **Wrong:** No 100 nF at VINA (C229 was "at VIN"); one 10 µF at VIN where TI uses 2 × 10 µF.
- **Evidence:** SLVS916I §8.2.2.5 p.15, Fig. 7, Table 4; EVM C8.
- **Fix:** C229 at U207 pin 1 (note); C228 → 22 µF 0603.
- **Status:** fixed.

#### P8 · should fix · U204 — keep-alive LDO had no input capacitor
- **Evidence:** TPL720 Rev A.2 "Input Capacitor and Output Capacitor": ≥ 1 µF plus 0.1 µF at IN.
- **Fix:** C236 10 µF at U204 pin 3.
- **Status:** fixed.

#### P9 · should fix · C217 — RTC backup capacitor value
- **Wrong:** 100 nF. The DS3231M needs no VBAT capacitor for backup use, and recommends 0.1–1 nF only to filter contact bounce at battery insertion (preferably power VCC first).
- **Evidence:** DS3231M 19-5312 Rev 7 pin description (VBAT) and "Initial VBAT Attachment".
- **Fix:** C217 → 1 nF; bring-up: fit the CR1220 after the main supply.
- **Status:** fixed.

#### P10 · should fix · D205 — modem-rail TVS protected nothing
- **Wrong:** SMAJ5.0A breakdown 6.40–7.07 V, clamp 9.2 V at 43.5 A: above the EG800K's 6 V and the TPS63020's 7 V absolute maximums; leakage up to 800 µA at 5 V. Quectel asks for VRWM 4.7 V.
- **Evidence:** TDSEMIC SMAJ spec; EG800K-LA HD Table 27, §3.4.4; SLVS916I abs max.
- **Fix:** not fitted, footprint kept (owner decision 2026-11-17, ADR-011).
- **Status:** owner decision.

#### P11 · should fix · C218, R234 — notes claimed soft start
- **Fix:** notes corrected (C218 holds Q210 off and delays turn-off; TPS63020 EN has no soft start). See W6.
- **Status:** fixed.

#### P12 · should fix · C219/C233 — description
- **Wrong:** Called "polymer/electrolytic"; ROQANG RVT is a wet electrolytic: ≈ 0.56 Ω at 120 Hz, impedance up to 6× at −40 °C, 2000 h at 105 °C (≈ 3.7 years continuous at 65 °C by the usual rule; much longer at the real duty cycle).
- **Fix:** BOM description corrected.
- **Status:** fixed.

#### P13 · should fix · SW201, SW202 — switch temperature range
- **Fix:** SW201 → C&K PTS810SJG250SMTRLFS (−40…+85 °C; pins 1–2 and 3–4 each one contact, C&K drawing); SW202 → ALPS SSSS811101 (−40…+85 °C; pin 2 common; four frame pads to GND); R228 100 k → 47 kΩ so SW202 carries more than ALPS's 50 µA minimum load while awake.
- **Status:** owner decision.

#### P14 · should fix · R209 — cold trip (see W10)
- **Status:** owner decision (+5 °C).

#### P15 · should fix · J203 — battery connector stock (see W3)
- **Fix:** XYECONN XY-S2B-PH-SM4-TB (C54582899), identical EasyEDA footprint; mating test with the pack's PHR-2 plug before use; genuine JST for deployment.
- **Status:** owner decision.

#### P16 · note · TMP390 is not fail-safe on an open output, and senses the PCB
- **Fix:** place U203 against the pack's lead-in or a thermal pad; consider a pull-down rather than pull-up default in rev B.
- **Status:** open.

#### P17 · note · CN3791 MPPT clamp is undocumented as a shutdown
- **Fix:** bring-up test 6 now checks inductor current is zero, DRV stays high and records CHRG/DONE while clamped.
- **Status:** open (bench).

#### P18 · note · MPPT start threshold and hot panels
- **Wrong:** The CN3791 runs only when MPPT > 1.23 V, i.e. Voc > 6.17 V at the 6.05 V setting; a 60–70 °C panel can sit near that.
- **Fix:** recalculate R204 for the chosen panel at its operating temperature (README open item).
- **Status:** open.

#### P19 · note · D203/D204 leakage at heat
- **Wrong:** The PMEG4010CEH is a very-low-VF diode, not a low-leakage one (≈ 90 µA each at 85 °C). Stock is no longer a concern (7,994).
- **Fix:** notes corrected; ≈ 1 cm² cathode copper each (0.17 W while charging); measure before changing.
- **Status:** open.

#### P20 · note · DS3231M firmware
Write EN32KHZ = 0 with INTCN = 1 and BBSQW = 0 at every boot (VBAT current maximum assumes it); run an I²C bus clear before the first access after each wake (SDA/SCL sit at 0 V while asleep). Documented in `power/README.md`. **Status:** open (firmware).

#### P21 · note · TPS63020 feedback network
R233 is 100 kΩ (TI suggests ≈ 200 kΩ) and C227 4.7 pF has no series resistor (TI Fig. 28 uses 68 kΩ); output 3.900 V within ±2.7 %, fine for the module's 3.4–4.3 V. Check stability in test 8/9. **Status:** open (bench).

#### P22 · note · wake-latch simplification (ADR-003)
RTC INT could drive WAKE_N directly (removing Q206, Q207, R222, R223 and ≈ 4.7 µA) if the DS3231M INT rating allows. **Status:** proposal, not applied.

#### P23 · note · bring-up order
Connect the pack with the panel covered (CN3791 p.7); scope RAW_BAT while hot-plugging (C207's ESR damps ringing; BAT/CSP are rated 6.5 V). Add "+"/"−" silkscreen at J201/J202. LED201/LED202 could be not fitted in production. Documented in the bring-up tests.

#### P24 · note · new parts from the review
- SW201 (PTS810): a press discharges C218 (47 nF at the battery voltage, ≈ 0.2 µC) straight through the contacts, because R227 is not in that path — a nanosecond peak of a few amperes, normal for a tact switch. Option with no extra part: move SW201 pins 1/2 to WAKE_N so R227 limits it to ≈ 42 mA.
- SW202 (ALPS): which slider position joins pins 1–2 is not stated in words; meter the first board and silkscreen ON / SHIP.
- F202: EasyEDA's `F1812` pads (1.41 × 3.50 mm) are smaller than Littelfuse's recommended land (1.78 × 3.15 mm, 3.45 mm gap); use the `FUSE-SMD_L4.7-W3.4` footprint or wide copper at layout.
- J203 (XYECONN): JLC gives 7.59 mm depth against ≈ 8.6 mm for JST; check fit, retention and mating with the PHR-2 plug on the first article.

#### Verified OK (power)
CN3791 pinout and topology match its Fig. 1; MPPT 1.205 × 5.02 = 6.05 V (5.83–6.27 V); charge current 0.60 A (0.55–0.65 A), R202 72–85 mW; CN3791 input/output capacitors and C201 ripple rating; gate swing ≤ 8 V below VCC. TPL720F33 and HT7533-1 pinouts and ratings (HT7533 30 V operating, 33 V abs max vs 19.9 V clamp). DS3231M pins, NC 32KHZ/RST, INT pull-up, I²C held low while powered (±0.1 µA). TPS63802 3.30 V and TPS63020 3.900 V; capacitance after DC-bias derating above both converters' minimums; L202/L203 saturation covers the peaks; TPS63020 ≈ 2.1–2.4 A available at a 3.0 V cell. TMP390 trip settings and the Q203/Q204 logic in every state. All SOT-23 parts G/B = 1, S/E = 2, D/C = 3 in datasheet, symbol and netlist; diode and LED cathodes; polarised capacitors pin 1 = +.

---

## 3. AUDIO sheet

#### A1 · must fix · C127 pins — tantalum was unwired
- **Wrong:** Netlist pins "+"/"−"; the C7171 symbol has pins 1/2.
- **Evidence:** EasyEDA footprint CAP-SMD_L3.2-W1.6-RD-C7171: polarity circle (layer 101), silk "+" and document-layer band all at pad 1.
- **Fix:** C127 1 = + (VMID_PRE), 2 = − (GND).
- **Status:** fixed (re-captured, wired).

#### A2 · must fix · U104/U105 — analog switch out of stock
- **Fix:** TS5A23166DCUR (C49148, 319 in stock at JLC — buy early): identical DCU pinout (NO1/COM1/IN2/GND/NO2/COM2/IN1/V+ = 1A/1B/2C/GND/2A/2B/1C/VCC), active-high control, ron ≤ 1.8 Ω (was ≤ 20 Ω), off leakage ≤ 50 nA (was ≤ 1 µA), 6 pC charge injection (≈ 27 µV step into C123, only between recordings). +$0.41/board.
- **Evidence:** TI TS5A23166 SCDS196J pin functions; SN74LVC2G66 SCES325N.
- **Status:** fixed.

#### A3 · should fix · U102 pin 5 — mic-bias regulator on by default
- **Wrong:** Page 3 register 0x15 resets to 0x01 (mic bias on), but MICBIAS is unused (TP101 only).
- **Evidence:** PCM186x SLAS831D Table 121 p.132.
- **Fix:** bring-up step 9 writes `0x00 = 0x03`, `0x15 = 0x00`, `0x00 = 0x00`.
- **Status:** fixed (docs).

#### A4 · should fix · low-battery floor (see W16)
- **Status:** fixed (docs).

#### A5 · should fix · D101 — library footprint larger than TI's land pattern
- **Wrong:** 0.6 × 0.6 mm pads 1.0 mm apart vs TI DPY0002A 0.3 × 0.5 mm, 0.7 mm apart: skew/tombstoning risk.
- **Evidence:** TPD1E10B06 SLLSEB1G pp.19–20.
- **Fix:** project footprint to TI's pattern, or inspect the first boards.
- **Status:** open (layout).

#### A6 · should fix · U103 — symbol sub-part B power pins (fixed)
- **Wrong:** The OPA1662 symbol repeats the supply pins on sub-part B; in the EasyEDA library record its V− is pin **9** (labelled 4), which has no pad. The capture leaves sub-part B's supply pins unwired.
- **Evidence:** EasyEDA DRC on 2026-11-17: "pins with the same number are connected to different networks" (2 fatal errors) and U103.8/U103.4 floating.
- **Fix:** the capture script now gives a sub-part's repeated pins the net of their namesake; AUDIO re-captured (279 wires). The PCB check confirms pad 4 = GND and pad 8 = AVDD_PRE.
- **Status:** fixed.

#### A7 · should fix · J101/J102 pins 5–6 — mechanical tabs unwired
- **Fix:** GND (owner decision 2026-11-17). The tabs are reinforcement metal, not part of the mic return, so R114 remains the only return-to-ground join.
- **Status:** owner decision.

#### A8 · note · crystal load capacitors
15 pF + 15 pF gives CL = 7.5 pF + stray; 12 pF needs ≈ 4.5 pF stray. With 3 pF the clock may run ≈ +15–25 ppm fast (estimate). Measure LRCK; go to 18 pF if fast. Cold-start the oscillator at −40 °C (SLAS831D gives no ESR or drive limit; YXC: ESR ≤ 50 Ω, 10–200 µW). **Status:** open (bench).

#### A9 · note · smaller items
OPA1662, TS5A23166, the crystal and X5R parts are rated to +85 °C. AUDIO_EN (GPIO7) has no pull at reset and the TPS7A20's pull-down is switched out while EN is high: firmware drives it low early (README). C105 (VREF, 1 µF X5R) is piezoelectric: include it in the tap test. JST GH contacts are tin-plated (fretting on a µV signal; gold on request). C114 leakage rises ≈ 10× at 85 °C (≤ ≈ 0.1 V on the mic bias). R108/R110 duplicate the PCM's internal pull-downs. The tantalum codes C7171/C16133 have no brand on JLC (AVX TAJ data used).

#### Verified OK (audio)
TPS7A20 pinout, EN thresholds 0.9/0.3 V, ≈ 15 mV dropout at 31 mA, ≈ 7 µVrms, caps within 0.47–200 µF effective. PCM1863 all 30 pins; I²C 0x4A; crystal mode with SCKI grounded; register values in the README (0x20, 0x26, 0x27, 0x0B, 0x06/0x07, PGA, GPIO 0x10/0x12/0x14, 0x71); power-up state of the filter-select GPIOs; 20 kΩ input impedance and ≈ 107 dB SPL full scale. OPA1662 at 3.3 V single supply (CM 0.5–2.2 V, swing 0.6–2.6 V), both channels stable. Ferrite currents (9 mA, 0.6 mA vs 200 mA). Tantalum derating (C114 31 %, C121 25 %, C127 10 %). Q101 G/S/D. Signal-path dielectrics (C0G or tantalum) and thin film where DC flows.

---

## 4. LTE sheet

#### L1 · blocker · U301 supply (see W1)

#### L2 · must fix · J301 pin 8 — SIM holder cover tabs unwired
- **Evidence:** SOFNG SNO-1303-C drawing p.1 ("4-PAD-GND"); EasyEDA symbol pin 8 "EH" on four pads.
- **Fix:** J301 8 → GND (owner decision).
- **Status:** owner decision.

#### L3 · should fix · C307 / U302 OE — RC on OE breaks TI's input-edge limit
- **Wrong:** The 100 kΩ × 100 nF RC crossed the OE threshold at ≈ 20 ms/V (limit 10 ns/V) and held OE high while VCCA collapsed.
- **Evidence:** TXS0108E SCES642L §5.3 (input transition rate) and §8.3; Quectel QuecOpen reference V1.2 sheet 7 (divider, no capacitor).
- **Fix:** C307 not fitted; OE = 0.91 × VDD_EXT through R304/R305 (1.64 V vs the 1.17 V threshold).
- **Status:** fixed.

#### L4 · should fix · U301 pin 7 — PWRKEY needs 10 nF
- **Evidence:** EG800K-LA HD V1.0.0 Fig. 9 p.26 (10 nF), §3.7 note 2 (≤ 10 nF on PWRKEY and RESET_N). PWRKEY is pulled up inside the module (Table 6).
- **Fix:** C316 10 nF (C15195, basic).
- **Status:** fixed.

#### L5 · should fix · UART/status filter footprints
- **Evidence:** QuecOpen reference V1.2 sheet 3 note 9.
- **Fix:** C317–C323 33 pF, not fitted, at NET_STATUS, RXD, TXD, CTS, RTS, STATUS and DBG_TXD.
- **Status:** fixed.

#### L6 · should fix · D205 (see P10)

#### L7 · should fix · J301 — consumer-grade push-push holder
- **Wrong:** −35…+75 °C (storage row; operating blank), and it is push-push, not push-pull as the BOM said.
- **Fix:** BOM description corrected; rev B: solder-down MFF2 eSIM (LTE open item 6).
- **Status:** description fixed; holder open.

#### L8 · note · start-up timing and sleep
STATUS goes high ≥ 6 s after PWRKEY but the UART is ready only ≥ 10 s after it (LA Fig. 11): wait for `RDY`. Keep `AT+QSCLK=0` (MAIN_DTR is open). Documented in the LTE README. **Status:** open (firmware).

#### L9 · note · smaller items
U302 logic levels: module VOL up to 0.2 V vs the A-port VIL 0.15 V; ESP32 levels vs B-port 0.15/2.9 V — not specified at the TXS's light load: scope at bring-up. Module footprint LGA-109 (AIR780E-named) has 1.3 mm outer pads vs 1.0 mm in LA Fig. 35: overlay before layout. Since 2026-11-18 the footprint is `LGA-109_L17.7-W15.8-P1.10_EG810M-CN`: compare it with EG810M-EU HD Fig. 40. R301 (0805 0 Ω): confirm ≥ 2 A. J302 U.FL: 30 mating cycles. Quectel wants ≥ 4 layers (open item 4).

#### Verified OK (LTE)
All 109 module pads match LA Table 6 by number and name, and QuecOpen V1.2 (which covers the EU variant) for every pin used; unused pins left open as Table 6 allows. VBAT 3.9 V within 3.4–4.3 V; Quectel's capacitor array and 0 Ω link; C301 ESR 70 mΩ ≤ 0.7 Ω, 62 % voltage use. RTS/CTS straight-through as LA §4.4 requires. USB_BOOT pulled low through 4.7 kΩ forces download (§4.2); USB_VBUS on a test pad is enough. Every Quectel-required test pad present. SIM network (0 Ω, 33 pF, 100 nF, 15 kΩ, TVS 3 pF) matches LA Figs. 19–20. D301 pin map matches Semtech Fig. 6. TXS0108E supplies, pin numbering, Hi-Z when the modem is off (≤ 1 µA into VDD_EXT). J302 pinout and pattern.

---

## 5. MCU sheet

#### M1 · blocker · D401 pin 5 (see W2) — fixed

#### M2 · must fix · U401 — module rated to +65 °C
- **Evidence:** ESP32-S3-WROOM-1 datasheet v1.8 §1.2, Table 1-1 (R8 variants −40…+65 °C; +85 °C with PSRAM ECC).
- **Fix:** enable PSRAM ECC in firmware (loses 1/16 of the PSRAM), or an N16 / N16R2 module (−40…+85 °C), ADR-001.
- **Status:** owner decision 2026-11-18: ESP32-S3-WROOM-1-**N16R2** (C2913205): 16 MB quad flash, 2 MB quad PSRAM, −40…+85 °C; same footprint, pads and symbol. PSRAM ECC no longer needed; GPIO35–37 free (spare).

#### M3 · should fix · ESP_EN supervision (see W15) — fixed

#### M4 · should fix · R416/LED401 — status LED too dim
- **Wrong:** The green LED is InGaN (VF 2.6–3.1 V at 5 mA); from 3.3 V through 2.2 kΩ it got ≈ 0.2–0.3 mA, not the 0.6 mA the README claimed — not readable in daylight (F5-05).
- **Evidence:** KENTO KT-0603G specification A.0.
- **Fix:** R416 → 100 Ω (2–7 mA); LED401 and LED202 → KT-0805G (same green InGaN, JLC basic).
- **Status:** fixed.

#### M5 · should fix · SD card back-powering
- **Wrong:** GPIO44 (U0RXD) has a weak pull-up at reset that feeds SD_VDD through R410; an idle-high bus keeps an unpowered card alive through its pin diodes.
- **Evidence:** ESP32-S3 datasheet v2.2 Table 2-1.
- **Fix:** firmware rule in `mcu/README.md` (clear the pull-up; drive CLK/CMD/D0 low before SD_PWR_EN low; hold ≥ 100 ms).
- **Status:** fixed (docs); firmware open.

#### M6 · should fix · J401 shell, J402 cover and card detect unwired
- **Fix:** J401 pins 1–4 and J402 pads 10–13 → GND; J402 card detect → GPIO3 (SD_CD) with R419 100 kΩ to 3V3; the unfitted VBUS sense (R407/R408) is removed. Owner decision 2026-11-17. The PCB check confirms the card-detect net reaches J402's `CD` pad.
- **Status:** owner decision.

#### M7 · should fix · GPIO0 — external pull-up
- **Evidence:** Espressif hardware design guidelines §1.3.9.
- **Fix:** R417 10 kΩ to 3V3.
- **Status:** fixed.

#### M8 · should fix · SD_CLK — series resistor
- **Evidence:** hardware design guidelines §1.3.8, §1.3.12.
- **Fix:** R418 33 Ω at U401 (U401 pin 24 now SD_CLK_MCU).
- **Status:** fixed.

#### M9 · should fix · J402 — holder temperature (see W8)
- **Status:** open. The card lines now have ESD protection (D403, W17).

#### M10 · note · programming needs a battery
VBUS only wakes the board. Flash with a battery or bench supply on J203 and SW202 on; to force download, short TP401–TP403 and pulse TP402 with the cable in. Documented in `mcu/README.md`. Since 2026-11-18 TP401–TP403 and TP413–TP415 (U0TXD, U0RXD, 3V3) share one 2.54 mm row for a pogo-pin jig (W12).

#### M11 · note · smaller items
C406 sits gate–source, so the card supply ramps in ≈ 0.1–0.3 ms rather than ≈ 1 ms: measure the 3V3 dip at card power-on (gate–drain 47 nF would give a real soft start). GPIO9 floats: enable a pull-down in firmware. GPIO13/14 glitch low at power-up with the RTC powered: I²C bus recovery. The ROM boot log on GPIO43 flashes the LED briefly. A low-VF LED401 at +85 °C may draw ≈ 7–8 mA, at the LED's derating limit: blink it rather than hold it on when hot, or use 150 Ω. The USB-C footprint is drawn for a 0.8 mm board; on 1.6 mm use pin-in-paste. ADC ranges in the port tables corrected to the datasheet's calibrated 0–1.6 V (6 dB) and 0–2.9 V (12 dB).

#### Verified OK (MCU)
All 41 module pads match Table 3-1, and the EasyEDA symbol/footprint match module Fig. 11-1. EN RC 13.9 ms, strap hold met. 3V3 decoupling per Fig. 9-1. Battery divider 1.31 V at 4.2 V, source impedance fine. USB-C A1…B12 and merged pads, 5.1 kΩ CC; microSD contacts 1–8, D3 pull-up, card switch VGS ≈ −3.0 V, off by default. LTE UART and STATUS directions.

---

## 6. Capture open items (from the handover)

| # | Item | Result |
|---|---|---|
| 1 | BT201, C127 unwired | Fixed: pad 1 = + on both footprints; netlists use pin numbers; re-captured and wired (P4, A1) |
| 2 | Pins with no netlist row (J301 8, J401 shell, J402 CD and 10–13, J101/J102 5–6) | Owner decision: shells, covers and tabs to GND; card detect to GPIO3 (L2, M6, A7) |
| 3 | Page sizes | POWER A2, AUDIO A2, LTE A2 (its layout grew with C316–C323) and MCU A3, all set by the owner |
| 4 | Test-pad footprint 0.5 mm vs 1.0 mm | Open: EasyEDA's library has only "Test-Point" with a 0.5 mm footprint; assign a 1.0 mm pad at PCB layout (W12). Applies to TP404–TP415 too (2026-11-18) |
| 5 | LTE template parts C1/TP1 | Removed by the re-capture |
| 6 | Supply risk | Modem: W1 (blocker; EG810M-EU by owner decision 2026-11-18). Second antenna covering 700–2700 MHz: still open (LTE open item 5) |
| 7 | Australian heat | W8 |

Re-capture results (2026-11-17, all pages saved): LTE 53 parts, 158 net wires, 72 no-connect flags; POWER 123 parts, 290 wires, 3 NC; AUDIO 114 parts, 277 wires, 1 NC; MCU 34 parts, 128 wires, 7 NC. Every netlist row is either a wire or an NC flag; the only warnings are expected name matches (diodes, LEDs, mounting pads, merged USB-C pads) and the library test points. AUDIO was re-captured once more after the DRC found U103's repeated supply pins unwired (A6).

**PCB-level check** (after Design > Update PCB, `easyeda_check.py` on the export): **all checks passed** — every part of all four sheets is on the PCB with its BOM's LCSC code, every pad is on the net the CSVs name, NC pins are unconnected and no other pad is connected. J402's card detect reaches its `CD` pad. EasyEDA DRC: the two U103 fatal errors are cleared by A6.

## 7. Decisions still needed

Items 1–5 were decided by the owner on 2026-11-18 (section 8).

1. ~~**Modem procurement** (W1): buy/consign EG800K-EU modules now, or JLC global sourcing.~~ Decided: EG810M-EU.
2. ~~**ESP32 temperature** (M2): PSRAM ECC in firmware, or an N16 / N16R2 module (ADR-001).~~ Decided: N16R2.
3. ~~**microSD ESD** (W17): add an SRV05-4 on the SD lines.~~ Decided: D403 on CLK, CMD, D0 and CD.
4. ~~**Test pads** (W12): PWR_HOLD, SYS and AUD I²C, SD_VDD, LTE_STATUS, UART0.~~ Decided: TP404–TP415.
5. ~~**CR1220 cell** (W8): name a wide-temperature cell.~~ Decided: Panasonic BR1220.
6. After the bench: Q210 soft start (W6), C233 fitted or not (W7), wake-latch simplification (P22).
7. Still open from W8: the J402 microSD holder at −40 °C and the J301 SIM holder (MFF2 eSIM in rev B).

## 8. Follow-up 2026-11-18: owner decisions

The owner decided the five open items. The sheet CSVs carry the changes (notes marked `owner decision 2026-11-18`); prices and reasons are the last five rows of [`2026-11-17-bom-cost-changes.csv`](2026-11-17-bom-cost-changes.csv).

| # | Finding | Decision |
|---|---|---|
| 1 | W1, L1 modem stock | U301 **EG800K-EU → Quectel EG810M-EU** (EG810MEULA-I05-SNNSA, C20421924). JLC stock of the EG800K-EU was 0 on 2026-11-18 (4 on 2026-11-17); the EG810M-EU had 206. LTE Cat 1 (10/5 Mbps; the EG800K is Cat 1 bis, which makes no difference to Auris), LTE-FDD B1/3/5/7/8/20/28, no TDD, no 2G, CE and RCM, −35…+75 °C (−40…+85 °C extended), LGA 17.7 × 15.8 × 1.7 mm (EG800K 2.4 mm). Quectel states it is compatible with the EG800K series in package. Checked against the released *EG810M-EU QuecOpen&QuecPython Hardware Design* V1.0 (2024-06-25): every pin Auris connects (1, 7, 10–18, 22–25, 27, 34–43, 45–48, 59–61, 70–73, 82, 88–95) has the same function, the GND pin list is identical, and the VBAT (3.4–4.3 V, ≥ 2 A, ≈ 100 µF low-ESR plus MLCC array), PWRKEY (low ≥ 700 ms, 10 nF), RESET_N (≥ 300 ms), USB_BOOT (pin 82, 4.7 kΩ to a GND test point), SIM and translator circuits agree with the sheet. Pins Auris leaves open carry QuecOpen-only functions (e.g. pin 8 = CAM_VDD, 2.8 V output) and stay open. The EasyEDA symbol's pin names match the netlist; the footprint is `LGA-109_L17.7-W15.8-P1.10_EG810M-CN` (was `LGA-109_L17.7-W15.8-AIR780E`): compare pad geometry at layout. The standard-firmware *EC800M & EG810M Series Hardware Design* was not read. The PCB footprint still accepts an EG800K-EU; firmware needs a Quectel AT driver either way. Part note: [`C20421924_EG810MEULA-I05-SNNSA.md`](../datasheets/C20421924_EG810MEULA-I05-SNNSA.md) |
| 2 | M2, W8 module temperature | U401 **ESP32-S3-WROOM-1-N16R8 → N16R2** (C2913205): 16 MB quad flash + 2 MB quad PSRAM, −40…+85 °C (Espressif WROOM-1 datasheet v1.8 §1.2, Table 1-1; the R8 variants are −40…+65 °C, +85 °C only with PSRAM ECC). Same footprint, pads and symbol. GPIO35–37 are free and stay unconnected (spare); PSRAM ECC is no longer needed. F3-05 (≥ 5 s audio buffer, 480 KB) fits in 2 MB. Edge AI (phase 2) gets 2 MB PSRAM instead of 8 MB, and quad PSRAM has about a quarter of the octal-DDR bandwidth at 80 MHz; model weights can stay in the 16 MB memory-mapped flash. New firmware rule: keep flash and PSRAM at 80 MHz (ESP-IDF *flash_psram_config*: the experimental 120 MHz mode can crash after a ≈ 20 °C temperature swing). Part note: [`C2913205_ESP32-S3-WROOM-1-N16R2.md`](../datasheets/C2913205_ESP32-S3-WROOM-1-N16R2.md) |
| 3 | W17 microSD ESD | New **D403 SRV05-4.TCT** (C13612) at J402 on SD_CLK (card side of R418), SD_CMD, SD_D0 and SD_CD; pin 2 to GND (own via beside J402); pin 5 (REF2) to 3V3, which is never below SD_VDD, so nothing back-feeds; 3V3 is off in sleep. 3 pF typical, 5 pF maximum per line. Correction to W17: D3 is not wired to the ESP32 in 1-bit mode, so CD takes its place |
| 4 | W12 test access | **TP404–TP415** on the MCU sheet: PWR_HOLD (GPIO10), SYS_SDA (GPIO13), SYS_SCL (GPIO14), AUD_SDA (GPIO18), AUD_SCL (GPIO8), SD_VDD, LTE_STATUS (GPIO38), LTE_TX (GPIO39), LTE_RX (GPIO40), STATUS_LED = U0TXD (GPIO43, UART0 for Espressif's RF test firmware), SD_D0 = U0RXD (GPIO44), 3V3. TP401–TP403 and TP413–TP415 in one 2.54 mm row for a pogo-pin jig. The 1.0 mm pad footprint remains a layout item |
| 5 | W8 coin cell | Holder unchanged (C70381 CR1220-2, −40…+80 °C per JLC). Cell, hand-fitted and not on the BOM: **Panasonic BR1220** (BR-1220/BN), −30…+80 °C. No CR1220-size cell is rated to −40 °C (Renata CR1220 MFR −30/+70 °C per Renata's coin-cell designer's guide; Maxell CR1220 −20…+85 °C). The −40 °C-rated 12.5 mm cells (Renata CR1225 −40/+85 °C, Panasonic BR1225A −40…+125 °C) need a CR1225 holder, and neither JLC option checked out: Antenk BT-S-G0-A-CR1225B (C52748081) has no datasheet and unknown polarity; TE BAT-HLD-012-SMT is rated −30…+70 °C. Bench-test the BR1220 at −40 °C; revisit if a documented −40 °C CR1225 holder turns up. DS3231M VBAT draw ≤ 3 µA maximum |

**BOM cost** (same basis as above, `python3 hardware/tools/bom_cost.py`):

| | 10 boards | 100 boards |
|---|---:|---:|
| 2026-11-17: parts / fees / **total per board** | $29.74 / $16.27 / **$46.01** | $23.77 / $1.63 / **$25.40** |
| 2026-11-18: parts / fees / **total per board** | $32.05 / $16.27 / **$48.32** | $25.82 / $1.63 / **$27.44** |

Still 102 unique codes, 53 extended: the modem and module replace extended parts one for one, and D403 reuses C13612. The modem adds $2.18/board at 10 and $1.58 at 100 ($8.04 and $6.39 against $5.86 and $4.80); the N16R2 −$0.02 at 10 and +$0.36 at 100; D403 +$0.16 and +$0.12. The test pads and the coin cell cost nothing on the JLC BOM.

**Capture:** EasyEDA Pro updated itself from 3.2.209 to 4.1.105 overnight. In 4.1, clearing and re-capturing a page failed in the AURIS project. Some devices could not be placed from the system library ("Create project component failed"; the script call never returns and the next placements fail too). Placing from the project library's copies gave some parts no footprint, and Update PCB then stopped with "lacks of property Footprint". So the 2026-11-17 export (`hardware/2026-11-17/AURIS_2026-11-17.epro2`, the version that passed the PCB check) was imported as a new project, **`AURIS_2026-11-18`**, and the changes were made there in place, without clearing pages:

- LTE: U301 removed with its 46 net stubs, then the EG810M-EU placed and wired (46 wires, 63 no-connect flags).
- MCU: U401 removed with its 37 stubs, then the N16R2, D403 and TP404–TP415 placed and wired (55 wires, 4 no-connect flags).
- The new parts first sat in boxes below the existing blocks. On 2026-11-19 both pages were re-laid out with the new `hardware/easyeda/tidy-<sheet>.js` (delete every wire, box and heading; move every part into the block layout a fresh capture would give; draw the net stubs from the netlist again). Afterwards every pin on both pages carries its netlist net (LTE 230 of 230 rows, MCU 157 of 157) and every part still has its footprint.

The capture template now places a device the project already holds from the project's copy (only one that has a footprint) and flags any part placed without a footprint. After Design > Update PCB (337 PCB parts) and an export, **`easyeda_check.py` passes for all four sheets**: audio 114, power 123, LTE 53, MCU 47 parts, each with its BOM's LCSC code and every pad on its CSV net. The project and EasyEDA's BOM are in `hardware/2026-11-18/`; the export after the tidy is in `hardware/2026-11-19/` and passes the same check. On 2026-11-19 the broken old `AURIS` project was deleted (backup kept outside the repo) and `AURIS_2026-11-18` renamed to **`AURIS`**.

**Docs updated the same day:** the LTE, MCU, power and audio READMEs, docs 00, 03–06, 08, 11, 13–15 and 19, the major-components CSV, the 2026-11-18 LCSC snapshot and the hardware guide.
