# Second schematic review, rev A baseline

**Date:** 2026-11-19. **Reviewer:** Claude Code (Claude Opus 5.5), an independent session that had not seen the first review while forming the findings in sections 2–7.

**Baseline:** commit `e961891` (merge of PR #4) on `main`. Export `hardware/2026-11-19/AURIS_2026-11-19.epro2`, SHA-256 `0c3d5120c6e0349351924550476266dd6c95ae8c2e7429ac9dc985f170307350` (re-hashed here). `easyeda_check.py` on that export passes: audio 114, power 123, LTE 53, MCU 47 parts. Nothing in the sheet CSVs, the EasyEDA project or the generated files was changed for this review.

**Status of every finding:** proposed. Fixes are applied only after the owner approves them, in one batch, as part of the freeze (phase 3 of the handover).

## 0. Summary

**Freeze recommendation: freeze after the listed fixes** (section 9). The schematic is sound: every pin number on all four sheets has the function its datasheet gives it, every footprint has the manufacturer's pin numbering and pin-1 position, the IC land patterns match, the cross-sheet nets are consistent, and every fix the first review claims is really in the CSVs. No blocker.

- **Two must-fixes**, both cheap:
  - R2-P1: the battery temperature cut-out (TMP390, U203) reads its trip-point resistors once, at a power-on reset that happens below its rated supply voltage on a slow dawn ramp, and keeps whatever it read all day.
  - R2-M1: switching on the microSD supply can dip 3V3 below the converter's power-good threshold, and since PG now drives the ESP32's EN, that resets the MCU and powers the board off.
- **Should-fixes that are cheap now and cost a respin later:**
  - a hardware undervoltage lockout on the 3.3 V converter (R2-G1);
  - a way for the MCU to read the service button (R2-G2);
  - option footprints for a main-switch soft start (R2-G3) and for forced PWM on the 3.3 V converter (R2-G6);
  - test pads for the TMP390 trip test (R2-P2);
  - pull-down on AUDIO_EN (R2-A1);
  - the land-pattern fixes in section 7.
- **Disagreements with the first review:** four that matter: M11 (now a must-fix), the 3.35 V recording floor, the W6 soft-start values (they would switch the board on at battery connect), and P22 (do it now).

| Severity | Count |
|---|---:|
| Blocker | 0 |
| Must fix | 2 |
| Should fix (incl. owner decisions) | 16 |
| Note | 19 |

| ID | Severity | Where | Finding | Status |
|---|---|---|---|---|
| R2-P1 | must fix | power U203 | TMP390 samples its trip resistors at a POR below its rated VDD on a slow panel ramp | owner decision (part) |
| R2-M1 | must fix | MCU Q401, power U206 PG | Card-supply turn-on can dip 3V3 below PG and reset the ESP32 → board off | proposed |
| R2-G1 | should fix | power U206 EN | No UVLO; depletion recovery (F4-04) depends on firmware | proposed |
| R2-G2 | should fix | power SW201, MCU | MCU cannot read the service button | owner decision |
| R2-G3 | should fix | power Q210 | Soft-start option footprints (W6) | proposed |
| R2-G4 | should fix | power R204 | MPPT set point against hot panels; per-region value | owner decision |
| R2-G6 | should fix | audio U101, power U206 MODE | Audio supply noise near LDO dropout; MODE option footprint | owner decision (gate value) |
| R2-G7 | should fix | LTE U301, audio U102 | Buy the EG810M-EU and PCM1863DBTR now (PCM1863 stock falling) | owner action |
| R2-P2 | should fix | power U203 | Cut-out fails open and is untestable; trip-test pads | proposed |
| R2-P4 | should fix | power C207, C219, C233 | 2000 h electrolytics; long-life parts for deployment | owner decision |
| R2-A1 | should fix | audio U101 EN | 100 kΩ pull-down on AUDIO_EN | proposed |
| R2-A2 / X2 | should fix | audio D101, MCU D402 | TPD1E10B06 land pattern | proposed (layout) |
| R2-L1 | should fix | LTE J301 | SIM holder −35…+75 °C (storage) | owner decision |
| R2-M2 | should fix | MCU C403 | PG discharges 1 µF directly; 100 nF | proposed |
| R2-X1 | should fix | LTE U301 footprint | 48 outer pads 1.0 × 0.7 mm against Quectel's 1.0 × 0.6 | proposed (layout) |
| R2-X3 | should fix | power F201, F202, C207 footprints | Fuse lands; C207 pad gap 0.52 mm under the can | proposed (layout) |
| R2-X4 | should fix | all TP | 1.0 mm test-pad footprint | proposed (layout) |
| R2-X5 | should fix | MCU J401 footprint | USB-C shell slots differ from the drawing | proposed (layout) |
| R2-G5, G8 | note | firmware | Modem transmit floor; crash loop, early PWR_HOLD, ROM log | firmware |
| R2-P3, P5–P8 | note | power | TMP390 placement; panel inputs; X5R; LEDs; TPL720 100 nF, R208/R209 TCR, BT201 meter check | bench/layout |
| R2-A3 | note | audio | MICBIAS, full scale, input impedance, crystal, AVDD_A hold-up, dielectrics, J101 contacts | bench |
| R2-L2, L3 | note | LTE | OE rationale (doc); STATUS, PWRKEY, power-down order, R301, levels | doc/firmware/bench |
| R2-M3, M4 | note | MCU | GPIO44 back-feed; floating inputs; eFuses; glitches; options | firmware |
| R2-X6–X12 | note | layout | Coating, stack-up, antennas, high-current and sensitive nets, placement, polarity | layout |

## 1. Method

1. **Design intent first:** `docs/00`, `04`, `06`, `07`, `11`, `14`, `15`, `19` and the four sheet READMEs; the cross-sheet port tables in `build_guide.py`.
2. **Whole design by hand** (section 2): every rail's source, default and sequence; the off state and sleep current; every path that turns the board on or keeps it on; cold start, brown-out and inrush; charging; the modem rail; protection; climate; supply.
3. **Part by part** (sections 3–6): every IC, module, connector, FET, diode, crystal, inductor and polarised capacitor against its datasheet: pin numbers and functions, unused pins, required external parts recomputed from the datasheet equations, absolute maximums against the real rails, defaults at power-up, temperature rating from the datasheet itself. Three helper sessions did the first pass of this per sheet (power, audio, LTE + MCU) under the same independence rule; I checked their evidence against the PDFs for every finding I kept, and kept only what the evidence supports.
4. **Footprints:** pad geometry was read out of the `.epro2` export itself (every pad's number, centre and size, plus the silkscreen and polarity marks) and compared with the manufacturer's land pattern and pin-1 position. `easyeda_check.py` already proves the pads carry the CSV nets.
5. **Stock:** JLC part-detail queries on 2026-11-19 for every low-stock or single-source part.

Datasheet references give the document number, revision and page, table or figure. Where a datasheet is silent, the finding says so.

## 2. Whole design

### 2.1 Power tree, defaults and sequence

| Rail | Source | Default at power-up | Notes |
|---|---|---|---|
| PANEL_IN → SOLAR_IN | J201 ∥ J202 → F201 → D201 → Q201 | — | Q201 is a correct high-side P-FET reverse-polarity switch (drain to the panel, gate to GND through R201, D202 clamps VGS ≤ 8.61 V) |
| TEMP_3V3 | U202 HT7533 from SOLAR_IN | follows the panel | powers only the TMP390 cut-out (see R2-P1) |
| RAW_BAT | pack J203 → F202 → Q205; CN3791 output | always | Q205 blocks a reversed pack only while the panel is dark (accepted) |
| KEEP_ALIVE | U204 TPL720F33 from RAW_BAT | always | DS3231M VCC and the latch pull-ups |
| RTC_VBAT | BT201 BR1220 | always | |
| VBAT_SW | Q210 from RAW_BAT, gated by the wake latch | off (R228 + C218) | |
| 3V3 | U206 TPS63802, EN tied to VBAT_SW | on with VBAT_SW | PG holds ESP_EN low until 3V3 > 95 % |
| VMODEM | U207 TPS63020, EN = MODEM_EN (GPIO11) | off (R235) | load disconnected while EN is low (SLVS916I §7.3.3) |
| AVDD_A, DVDD_A | U101 TPS7A2033, EN = AUDIO_EN (GPIO7) | off (500 kΩ internal, see R2-A1) | active discharge 150 Ω (SBVS338H p.7) |
| AVDD_PRE | Q101 from AVDD_A, PREAMP_EN (GPIO6) | off (R128) | |
| SD_VDD | Q401 from 3V3, SD_PWR_EN (GPIO45) | off (R402 + internal pull-down) | |
| VDD_EXT | module output, 1.8 V | off until the module runs | powers the TXS0108E A side and OE |

The sequence is right: VBAT_SW → 3V3 → PG → ESP_EN (+10 ms RC) → firmware asserts PWR_HOLD → domains on demand. Every switched domain defaults off through a pull-down or an internal default.

### 2.2 Off state and sleep current

What stays alive while "off": TPL720F33, DS3231M on VCC, the wake latch (Q206 inverter biased through 2 MΩ, R223 1 MΩ), the CN3791's battery pins, the two charger Schottkys' reverse leakage and the pack's own protection IC.

| Load | 25 °C | Datasheet maximum | Source |
|---|---:|---:|---|
| DS3231M standby on VCC | ≈ 88 µA typ (curve) | 130 µA at 3.63 V | ADI 19-5312 Rev 7 p.2 (I_CCS) |
| Wake latch (R219 + R222, R223) | 4.6 µA | 4.6 µA | (3.3 − 0.65)/2 MΩ + 3.3/1 MΩ |
| TPL720F33 | 1.4 µA | — (typ only) | 3PEAK TPL720 Rev A.2 p.7 |
| CN3791 BAT + CSP, sleep | ≈ 9 µA | 15 µA | Consonance CN3791 Rev 1.0 p.4 (I_BAT2) |
| D203 + D204 reverse leakage at ≈ 4 V | ≈ 2 µA | 70–90 µA each at 85 °C (typical curve; no maximum given) | Nexperia PMEG4010CEH Rev 02 Fig. 2 |
| C207, Q210 off-state, misc. | ≈ 1–3 µA | Q210 I_DSS 1 µA (25 °C), 5 µA (55 °C) at 30 V | AOS AO3401A Rev 3.1 p.2 |
| **Total** | **≈ 106 µA** | **≈ 160 µA** at 25 °C | |

At 3.7 V that is 0.009–0.014 Wh/day, inside the ≤ 0.02 Wh/day off-state line of doc 19. Only the Schottky leakage grows steeply with temperature (≈ 290 µA total at 85 °C), and that happens only in a hot enclosure, so it costs little energy in practice. I agree with the README's table. None of the fixes proposed here adds sleep current.

### 2.3 Wake and power hold, and back-feed

Every path that can pull WAKE_N/LATCH_LOGIC low, and so turn Q210 on, was traced:

| Path | Drives | Can it be back-fed? |
|---|---|---|
| RTC INT → Q206 → RTC_WAKE → Q207 | DS3231M INT/SQW, open drain, 1 MΩ pull-up to KEEP_ALIVE | No. DS3231M SDA/SCL/INT tolerate 5.5 V regardless of VCC (19-5312 p.2, p.8), so the unpowered 3V3 pull-ups on SYS_SDA/SCL neither feed nor load it. **Holds the board on while an alarm flag is set**, including after a firmware crash (the intended W5 workaround) and as soon as KEEP_ALIVE returns after a depletion (see 2.4). |
| PWR_HOLD (GPIO10) → Q208 | ESP32, R224 100 kΩ pull-down | No. GPIO10 is only driven by a powered ESP32. |
| VBUS → R225/R226 → Q209 | USB-C VBUS | No. With D401 pin 5 open nothing on the board reaches VBUS; D402 is a bidirectional TVS. Confirmed by tracing every VBUS pin: J401 A4/A9/B4/B9, D402, R225 only. |
| SW201 → LATCH_LOGIC | button to GND | — but the MCU **cannot read it** (R2-G2). |
| SW202 | ship mode: opens the gate path; frame terminals to GND | — |

Back-feed into unpowered domains:
- **3V3 while off:** the only source found is the panel-voltage divider. With the panel lit, SOLAR_SENSE (≈ 1 V, 130 kΩ Thevenin) feeds GPIO2's ESD diode and lifts the dead 3V3 rail with a few µA from the panel, not from the battery. Harmless; noted only.
- **Audio domain while 3V3 is up:** AUD_SDA/SCL pull-ups are on DVDD_A, so the bus is unpowered with the ADC; firmware must keep GPIO8/18 as inputs (README rule). No hardware issue.
- **Modem while off:** the TXS0108E's A side and OE come from VDD_EXT, so it is Hi-Z when the modem is off (R2-L section).
- **microSD while unpowered:** D403's reference is 3V3, never below SD_VDD; firmware drives CLK/CMD/D0 low before cutting SD_VDD (README rule). GPIO44 (U0RXD) has a reset-time pull-up that feeds SD_D0 → R410 → SD_VDD until firmware clears it; tens of µA for a few ms, noted in the MCU section.
- **Latch nodes:** RTC_INT_N, Q206_B and RTC_WAKE are 1 MΩ nodes and TP208 exposes one of them. In a sealed enclosure that sees condensation, surface leakage of about 1 µA would pull RTC_WAKE to ≈ 2.3 V, below the 2N7002's 2.5 V maximum threshold, and could stop an RTC wake. Conformal-coat the latch area (R2-X6), or remove those nodes with the first review's P22 (section 8.3).

### 2.4 Cold start from a flat battery, and brown-out

**Depletion and recovery (F4-04).** The pack's own protection opens at about 2.5 V. When the sun returns:
1. The CN3791 starts once the panel exceeds 6.17 V (MPPT > 1.23 V, CN3791 Rev 1.0 p.5) and, with the battery below 2.8 V, charges at its trickle rate of 17.5 % of I_CC: 10–36 mV across R202, i.e. **50–180 mA** (p.4).
2. KEEP_ALIVE returns and the DS3231M moves back from its backup cell to VCC. Its alarm flags kept being set on the backup cell ("the corresponding alarm flag is always set", 19-5312 p.13), and the standing Alarm 2 sets A2F every day, so **INT asserts at once and closes the latch**.
3. VBAT_SW follows RAW_BAT and the TPS63802 starts from **1.7 V** (UVLO rising 1.6–1.79 V, falling 1.2–1.29 V, SLVSEU9D p.6). The ESP32 boots on a battery that the trickle current cannot support: boot draws more than 50–180 mA at a 2 V input.

The result can be a boot/brown-out loop that eats the trickle current and holds the alarm flag set, so recovery depends on firmware winning a race at the worst moment. There is no hardware undervoltage lockout anywhere on the switched rail. **R2-G1** adds one with two resistors.

**Brown-out in operation.** Below the pack's cut-off everything stops at once (RAW_BAT, KEEP_ALIVE; the RTC keeps time on BT201). Above it, the TPS63802 rides through sags down to 1.25 V, so a modem burst does not reset the MCU. The audio LDO is the sensitive one (R2-G6). The ESP32 brown-out detector and the TPS63802 PG (90 % falling, 14 µs) both reset the ESP32, and any reset drops PWR_HOLD (accepted W5 behaviour, firmware workaround).

### 2.5 Inrush when the main switch closes

C218 is gate–source, so it delays turn-off but gives no soft start: Q210's gate is pulled to ≈ 0 V through R227 (100 Ω) and a 2N7002, or shorted directly by SW201, and Q210 turns on in microseconds. VBAT_SW carries C219 (470 µF) and ≈ 40 µF of effective MLCC (C220, C222, C228, C101 after DC-bias derating).

Estimate with a path resistance of ≈ 0.28 Ω (cells ≈ 25 mΩ, pack FETs ≈ 50 mΩ, connector and lead ≈ 60 mΩ, F202 ≈ 35 mΩ, Q205 and Q210 ≈ 50 mΩ each, board ≈ 10 mΩ):
- the MLCCs: ≈ 15 A peak for ≈ 10 µs;
- C219 (ESR ≈ 0.2 Ω at 100 kHz): ≈ 9 A decaying with τ ≈ 0.23 ms, ≈ 2 mC.

This agrees with the README's 5–12 A for 0.2–0.4 ms. A DW01-class pack protection (over-current ≈ 150 mV for ≈ 10 ms, short-circuit ≈ 1.35 V for tens of µs) would not trip, but the FieldMesh pack's protection is not documented and the event repeats 144 times a day. I agree with keeping it a bench item (test 2), and **R2-G3** adds option footprints so a soft start can be fitted without a respin if the bench shows a trip.

### 2.6 Charging

- **CN3791 against the pack:** 4.158–4.242 V regulation, 550–650 mA (0.11 C on 5200 mAh, inside the pack's ≥ 600 mA rating), trickle below 2.8 V, termination at 16 % of I_CC (≈ 96 mA) and recharge at 95.5 % (4.01 V), all from CN3791 Rev 1.0 p.4. The board's own load passes through R202, so termination is delayed while the recorder is awake (README already says so). Inductor rule and ripple pass (47 µH; ΔI ≈ 0.10 A nominal against the 0.18 A limit).
- **MPPT divider and the panel class:** 6.05 V set point, start only above 6.17 V. Right for a cold winter panel, wrong for a hot one (**R2-G4**).
- **TMP390 window:** +42 °C trip / +37 °C reset (R208 2.49 kΩ, Table 7-1) and +5 °C trip / +10 °C reset (R209 18.7 kΩ, Table 7-2, 5 °C column), ±1.5 °C at 0–70 °C with VDD ≥ 2.5 V (SBOS904A §6.5). Values right. Outputs are open-drain active-low, so the wired-OR on TEMP_FAULT_N is valid (§7.3).
- **If its output opens:** TEMP_FAULT_N stays high through R210, which the circuit reads as "temperature OK", and charging runs at any temperature. The README's "clamp on (fail-safe)" covers only a missing TEMP_3V3 (**R2-P2**).
- **Where it reads:** the TMP390 measures the PCB, not the cells, which sit off-board on a lead (**R2-P3**).
- **When it reads its trip points:** **R2-P1** (must fix).

### 2.7 Modem supply

- **Voltage:** 3.90 V (0.5 × (1 + 680/100)); EG810M-EU VBAT 3.4–4.3 V; TPS63020 abs max 7 V.
- **Peak current:** at 2 A out (EG810M-EU maximum peak) the TPS63020 needs 2.9 A in at 3.0 V and 3.5 A at 2.5 V; its average switch-current limit is 3.5 A minimum at VIN 3.6 V and falls below VIN 2.3 V (SLVS916I p.6, §7.3.2). The path drop at those currents is ≥ 0.7 V, so at a low cell the 2 A peaks are carried by C233, C301 and the ceramics. Firmware needs a transmit floor (R2-G5).
- **Start-up:** the current limit ramps from 400 mA only until VOUT ≈ 1.2 V, then the full limit applies (§7.4.1). Into ≈ 600 µF that is ≈ 4 A for ≈ 0.5 ms and a VBAT_SW sag of ≈ 1 V, as the README says (W7). PG flags current limit, not regulation (§7.3.4), and the 1 MΩ pull-up is right for its 10 µA V_OL spec.
- **Bulk:** C301 (100 µF polymer, 70 mΩ) meets Quectel's ≥ 100 µF / ≤ 0.7 Ω; C233 is extra and could be made optional after test 9.

### 2.8 Protection at the connectors

| Connector | Reverse polarity | Surge / ESD | Verdict |
|---|---|---|---|
| J201/J202 panel | Q201 | F201 1.1 A PPTC + D201 SMF12CA (V_RWM 12 V, 200 W) | Right for a 6 V-class panel. No blocking diode between the two panels (note in R2-P5). |
| J203 battery | Q205 (panel dark only) | internal connector | accepted |
| J401 USB-C | — | D401 on D+/D−/CC1/CC2, D402 on VBUS, shell to GND | right |
| J301 SIM | — | D301 SRV05-4, REF2 on USIM_VDD | right |
| J402 microSD | — | D403 SRV05-4, REF2 on 3V3 | right |
| J101 microphone | — | D101 on MIC1_OUT_C; return, source and shield tied to GND by 0 Ω at the connector | right; footprint fix R2-A2 |
| J302 antenna | — | none | acceptable for an internal FPC antenna |

### 2.9 Climate

Checked against each datasheet, not the JLC attribute:

| Part | Datasheet range | Against −40…+85 °C |
|---|---|---|
| U301 EG810M-EU | −35…+75 °C operating, −40…+85 °C extended | accepted (F7-01, doc 15) |
| J301 SNO-1303-C | −35…+75 °C | open (L7) |
| J402 TF PUSH | −25…+85 °C | open (M9) |
| J401 HC-TYPE-C-16P-01A | −25…+85 °C | service port only; low risk |
| J203 XY-S2B-PH (rev A) | −25…+85 °C (JLC); genuine JST PH −40…+105 °C | owner decision: genuine JST for deployment |
| BT201 cell BR1220 | −30…+80 °C; holder −40…+80 °C (JLC) | owner decision: bench at −40 °C |
| C201, C207, C219, C233 | −55/−40…+105 °C, but C207/C219/C233 are 2000 h parts | R2-P4 |
| X5R MLCCs | −55…+85 °C (EIA) | note R2-P6 |
| OPA1662, TS5A23166, TXS0108E, CN3791, HT7533, TPL720, DS3231M, ESP32-S3-WROOM-1-N16R2 | −40…+85 °C | OK, no margin above +85 °C |
| TMP390, TPS7A20, TPS63802, PCM1863, PMEG4010, SMF12CA, MMBT3904, AO3401A | to +125 °C or more | OK |

### 2.10 Cross-sheet nets

All 29 nets that cross a sheet boundary have one name on every sheet; no designator is used on two sheets; directions and voltage domains agree with the port tables. Three nets have a single fitted pin, all ESP32 inputs whose other end is a DNP option: AUD_INT_MCU (GPIO4), AUD_MCLK (GPIO9), MIC1_DC_SENSE (GPIO5). Firmware must enable a pull-down on each (the README covers GPIO9 only; note in the MCU section). `easyeda_check.py` maps 41 of U301's RESERVED pins to other RESERVED pads by name; every one of those pins is NC on both ends, so no connected pin is affected.

### 2.11 Supply

JLC stock on 2026-11-19:

| Part | Stock | Comment |
|---|---:|---|
| EG810M-EU (C20421924) | 206 | unchanged since 11-18; single source; EG800K-EU still 0; A7670G 107 (different footprint) |
| PCM1863DBTR (C529569) | **244** | **390 on 11-17**, falling; PCM1862DBTR (C544647) 208; PCM1863DBT (C1520794) 1 |
| SNO-1303-C (C428450) | 1,106 | |
| APXG250ARA470MF61G (C201) | 951 | |
| TPL720F33 (C2842389) | 2,165 | single source (3PEAK) |
| everything else checked | > 2,000 | TS5A23166 up to 2,525 |

**Buy the prototype quantity of the EG810M-EU and the PCM1863DBTR now** (R2-G7). Nothing on the BOM is marked NRND or EOL at JLC.

### 2.12 Whole-design findings

#### R2-G1 · should fix · power, U206 pin 1 (EN) · no undervoltage lockout on the switched rail
- **Problem:** EN is tied to VBAT_SW, so the TPS63802 starts at 1.6–1.79 V and runs down to 1.2–1.29 V. Nothing else on the switched rail has a UVLO, and the latch closes at any RAW_BAT.
- **On the board:** after a depletion, the RTC flag closes the latch as soon as the charger lifts RAW_BAT, and the ESP32 tries to boot from a 2 V cell fed by a 50–180 mA trickle charge. Recovery (F4-04) then depends on firmware. Also, at a hot ambient Q210's off-state leakage into the 320 kΩ battery-sense divider is the only load on VBAT_SW; at datasheet-maximum leakage it could float VBAT_SW above the TPS63802's start threshold.
- **Evidence:** SLVSEU9D (Jan 2021) p.6: UVLO rising 1.6–1.79 V, falling 1.2–1.29 V; EN threshold 1.07–1.13 V rising, 0.97–1.03 V falling; §9.3.2: "the enable pin can also be used with an external voltage divider to set a user-defined minimum supply voltage". CN3791 Rev 1.0 p.4 (trickle 10–36 mV / 0.2 Ω). DS3231M 19-5312 p.13 (flags always set). AO3401A Rev 3.1 p.2 (I_DSS).
- **Fix:** U206 EN from a divider: 150 kΩ (C25755) from VBAT_SW to EN, 100 kΩ (C25741) from EN to GND. Turn-on at 2.68–2.83 V, turn-off at 2.43–2.58 V, 17 µA while awake, nothing while off. The falling threshold sits below a 20 %-SOC cell's sag at full modem power and above the pack's own cut-off; confirm in power test 9 at −10 °C. PG stays low while EN is low (SLVSEU9D Table 9-1), so ESP_EN stays held.
- **Status:** proposed.

#### R2-G2 · should fix (owner decision: touches the ADR-003 latch) · power SW201, MCU · the MCU cannot read the service button
- **Problem:** SW201 pulls LATCH_LOGIC to GND and nothing else. While PWR_HOLD holds the board on, LATCH_LOGIC is already low, so a press changes nothing the MCU can see. VBUS sense was dropped for card detect (ADR-012), so a button wake is known only by elimination (no A1F/A2F, no USB host).
- **On the board:** a press while the recorder is awake (10 % of the time on DRM-1, longer during LTE or service) is lost; a press that coincides with an alarm is lost; firmware cannot offer long-press or "exit service mode"; and a button held closed by ice or a pressed membrane keeps the board on until the battery is flat, with no way for firmware to report why. F5-01, F5-02 and F5-05 all depend on "press the button".
- **Evidence:** power-netlist.csv SW201 rows; mcu-netlist.csv (no button net); doc 06 state machine "BOOT → SERVICE: Button/USB service reason".
- **Fix (3 parts, no sleep current):**
  - SW201 pins 1/2 to a new net BTN_N instead of LATCH_LOGIC;
  - a small-signal Schottky, anode LATCH_LOGIC, cathode BTN_N (a press still pulls the latch to ≈ 0.3 V);
  - 1 MΩ (C26083) from BTN_N to RAW_BAT, so the diode carries no current when idle;
  - a 2N7002 (C8545) with gate on BTN_N, source GND, drain to GPIO35 (free on the N16R2, WROOM-1 datasheet v1.8 §3 note) with its internal pull-up: GPIO35 reads high while the button is pressed.
  - Checked: idle, ship mode (SW202 open: the diode has no DC path), board held on (diode reverse-biased), board off (the 2N7002 only sinks, so nothing back-feeds the unpowered GPIO). The 1 MΩ draws 4 µA only while pressed.
- **Status:** owner decision needed.

#### R2-G3 · should fix · power, Q210 · option footprints for a main-switch soft start
- **Problem:** see 2.5: ≈ 9–15 A inrush on every wake into an undocumented pack protection. The bench may prove it harmless (test 2), but without footprints a fix needs a respin.
- **On the board:** if the pack protection trips at turn-on, the board and RTC brown out, the flag stays set and the board retries at every KEEP_ALIVE return.
- **Evidence:** calculation in 2.5; power README test 2.
- **Fix:** give Q210's gate its own net, Q210_G: a resistor from SYS_GATE to Q210_G (fit 0 Ω, C17168), C218 moved to Q210_G–RAW_BAT (gate–source, unchanged value) and a DNP 0603 capacitor from Q210_G to VBAT_SW (gate–drain). With 0 Ω and the capacitor not fitted the circuit is exactly today's. If test 2 shows a trip, fit 10 kΩ, 100 nF gate–drain and 2.2 µF for C218: the Miller plateau then slews VBAT_SW at ≈ 2.4 V/ms, ≈ 1.2 A for ≈ 1.8 ms; C218 ≫ C_gd keeps VGS ≈ −0.2 V at battery hot-plug; turn-on delay ≈ 13 ms, turn-off ≈ 130 ms. All wake sources, including SW201, then pass through the resistor.
- **Status:** proposed.

#### R2-G4 · should fix (owner decision) · power R204 · MPPT set point against a hot panel
- **Problem:** 6.05 V is about the maximum-power voltage of a 6 V-class panel at a 25 °C cell, and the CN3791 starts only once the panel exceeds 6.17 V. A panel's Voc falls ≈ 0.3 %/°C and Vmp ≈ 0.4 %/°C. For a typical 12-cell panel (Voc 7.2 V, Vmp 6.0 V at STC):

  | Cell temperature | Voc | Vmp | Power drawn at the 6.05 V set point |
  |---|---:|---:|---:|
  | 5 °C (European winter) | 7.7 V | 6.5 V | ≈ 97 % of maximum |
  | 50 °C | 6.6 V | 5.4 V | ≈ 90 % |
  | 70 °C | 6.2 V | 4.9 V | ≈ 30 %, and may not start |

- **On the board:** fine for the December design case (D3). In Australia, and for a cabled panel in sun while the recorder sits in shade (board below the +42 °C cut-out), harvest collapses on hot days.
- **Evidence:** CN3791 Rev 1.0 p.4 (V_MPPT 1.18–1.23 V), p.5 ("works normally when … MPPT > 1.23 V"); panel figures from a single-diode model with typical c-Si coefficients (the panel is not chosen yet, ADR-022).
- **Fix:** make R204 a per-build value chosen from the chosen panel's Vmp at its expected cell temperature: keep 402 kΩ for European builds; for Australian builds or hot cabled panels ≈ 330 kΩ (≈ 5.2 V set point, start above ≈ 5.3 V). Record the value per unit. Bench-check with the real panel (README open item).
- **Status:** owner decision needed.

#### R2-G5 · note (firmware) · power U207 · modem transmit floor and start-up
- **Problem / on the board:** see 2.7. At a low cell the TPS63020 cannot supply 2 A peaks from VBAT_SW; start-up sags VBAT_SW by ≈ 1 V.
- **Evidence:** SLVS916I p.6, §7.3.2, §7.4.1.
- **Fix:** firmware: no modem session below ≈ 3.3 V under load (tune in test 9), never during a recording (already a rule). Keep C233 for rev A; decide after test 9 whether it stays.
- **Status:** proposed (firmware and bench).

#### R2-G6 · should fix · audio U101, power U206 pin 2 (MODE) · audio supply noise near dropout
- **Problem:** the recording gate (VBAT_SW ≥ 3.35 V) leaves the TPS7A2033 35 mV of headroom; TI specifies regulation and PSRR only for VIN ≥ VOUT + 0.3 V. Near dropout PSRR falls towards 0 dB. At the same time the TPS63802 runs in power-save mode (MODE = GND), whose bursts move with load and can fall in the audio band; they appear as input-current pulses on VBAT_SW.
- **On the board:** VBAT_SW ripple then passes to AVDD_A and through the mic-bias filter (−36 dB at 100 Hz, −56 dB at 1 kHz) to the mic node. 30 mV of ripple at 100 Hz with 20 dB PSRR gives ≈ 50 µV at the mic, ≈ 20× the 2.4 µV self-noise.
- **Evidence:** TPS7A20 SBVS338H §5.5 conditions (p.6), §7.3 (p.31), Fig. 5-61; TPS63802 SLVSEU9D §9.3.3 (MODE); mic-bias filter from the audio README.
- **Fix:**
  - Firmware: raise the recording gate to VBAT_SW ≥ 3.6 V under load, or measure on the prototype and keep 3.35 V only if the noise floor holds (owner decision: it trades recording time at low charge).
  - Schematic: replace MODE's direct GND tie by 100 kΩ to GND (C25741, default power-save) plus a DNP 0 Ω to spare GPIO36, so G2 can try forced PWM (fixed ≈ 2 MHz, out of band) during recordings without a respin.
- **Status:** proposed; recording gate is an owner decision.

#### R2-G7 · should fix (procurement) · LTE U301, audio U102 · buy the scarce parts now
- See 2.11. **Status:** owner action.

#### R2-G8 · note · whole design · firmware-only behaviours that hardware cannot back up
- Any ESP32 reset drops PWR_HOLD (W5); the RTC-flag workaround also means a crash loop holds the board on until the pack cuts off. Keep a crash counter in RTC memory and fall back to a long alarm after N resets. Assert PWR_HOLD in the second-stage bootloader (a held button must otherwise stay pressed through the whole boot).
- Disable the ROM boot log on UART0 (eFuse) or accept a blink of LED401 on every wake: GPIO43 is U0TXD and idles high while it is the console.
- **Status:** proposed (firmware).

## 3. Power sheet

#### R2-P1 · must fix · U203 pin 5 (VDD), pins 1/2 (SETA/SETB) · the TMP390 latches its trip points at an unspecified supply voltage every dawn
- **Problem:** the TMP390 reads its SETA/SETB resistors once, after its power-on reset, and keeps those thresholds until the next power cycle. The POR is at 1.5 V (typical only) and the read follows 10 ms later. Its supply, TEMP_3V3, is the HT7533 output, which tracks the panel up through twilight over minutes. So the read happens at VDD ≈ 1.5 V, below the 1.62 V minimum for which the device, its resistor programming and its accuracy are specified. TI gives no ramp-rate requirement, and the brown-out at 1.1 V means a twilight hover between 1.1 and 1.5 V is possible.
- **On the board:** whatever thresholds U203 reads at dawn hold for the whole day. A mis-read cold threshold allows charging a frozen pack (lithium plating); a mis-read hot one blocks charging. This is the only charge-temperature protection on the board.
- **Evidence:** TI SBOS904A (Aug 2020) §6.3 (VDD 1.62–5.5 V), §6.5 p.5 (V_POR 1.5 V typ, brown-out 1.1 V, power reset time 10 ms), §7.3 p.7 ("powers on when the supply voltage goes beyond 1.5 V, and starts sampling the input resistors … These values will remain the same until the device goes through a power cycle"), §9 (no ramp requirement).
- **Fix:** give U203 a clean supply edge from the panel side, and keep the cut-out fail-safe:
  - a nano-power voltage detector with a **push-pull** output, threshold ≈ 2.9 V, powered from TEMP_3V3; its output supplies U203 VDD (pin 5, with C212 moved to it) **and** the R210 pull-up. TEMP_3V3 keeps C211.
  - Below the threshold U203 is unpowered and TEMP_FAULT_N is low, so the MPPT clamp is on (fail-safe, as today). Above it U203 gets a µs edge to ≈ 3 V, reads its resistors in spec, and TI's "pull-up ≤ VDD + 0.3 V" rule holds. The charger cannot start below 6.17 V anyway, so nothing is lost.
  - Candidate: Microchip MCP112-290 (push-pull, 2.90 V), or any nano-power detector with a push-pull output in that range; choose the part, check its output drive (≥ 1 mA, for R210's 330 µA plus U203's 250 µA start-up peak) and JLC stock in phase 3.
  - Not recommended: powering U203 from KEEP_ALIVE. After a depletion KEEP_ALIVE is ≈ 0 V, TEMP_FAULT_N would sit low, the clamp would stay on and the charger could never start: recovery (F4-04) would deadlock.
  - Keep a bench test either way: ramp TEMP_3V3 0 → 3.3 V over ≈ 10 min and confirm both trips with freeze spray and a heat gun.
- **Status:** proposed; owner decision on the part (it is inside the ADR-007 block).

#### R2-P2 · should fix · U203 pins 4/6, TEMP_FAULT_N · the cut-out cannot be tested and fails open
- **Problem:** OUTA/OUTB are open-drain, active-low. An open OUTA, OUTB, VDD or GND joint, or a missing U203, leaves TEMP_FAULT_N pulled high, which reads as "temperature OK" and enables charging at any temperature. An open R209 silently disables the cold channel. Nothing on the board tests the chain.
- **Evidence:** SBOS904A §7.3 (open-drain outputs), §7.3.2 (trip test: driving SETx above 0.8 × VDD forces the matching output low "for production testing after assembly"), §8.2.1.1.
- **Fix:** test pads on TMP_SETA and TMP_SETB. In production and in bring-up test 6, drive each above 0.8 × VDD and confirm charging stops (inductor current zero): that proves U203, both outputs, Q203/Q204 and the MPPT clamp on every board. Topology unchanged.
- **Status:** proposed.

#### R2-P3 · note (layout) · U203 · it senses the PCB, not the cells
The pack is off-board on a 2-wire lead with no thermistor, and the charger's own losses (≈ 0.3 W in Q202, D203, D204, L201, R202) warm the board while charging. A cold pack on a sun-warmed board can charge below 0 °C. Place U203 at the board edge nearest the pack, away from the charger and both converters, and mount the pack against that area; measure U203 against a thermocouple on the cells while charging (test 6). Agrees with the first review (W10/P16).

#### R2-P4 · should fix (deployment build) · C207, C219, C233 · 2000-hour electrolytics in a hot enclosure
- **Problem:** all three are 2000 h at 105 °C parts. By the usual ×2 per 10 °C rule that is ≈ 8,000 h continuous at 85 °C and ≈ 32,000 h at 65 °C (rule of thumb, not a datasheet figure). C207 sits across the battery permanently. Cold impedance: RVT Z(−40 °C)/Z(20 °C) ≤ 6 (≈ 3.4 Ω), FP ≤ 3. RVT ripple rating 198 mA rms at 120 Hz.
- **Evidence:** ROQANG RVT (no revision) spec table; Panasonic FP-V catalogue 2019-04-17.
- **Fix:** rev A as is. For deployment units, ≥ 5000 h (better 10,000 h) at 105 °C or polymer parts. Measure C233's temperature in test 9.
- **Status:** owner decision (deployment BOM).

#### R2-P5 · note · panel input
- The two panel inputs are paralleled without blocking diodes: a dark panel loads a lit one by a few percent of its I_sc, and a crushed cabled-panel lead shorts the input (F201 limits it, nothing is damaged, charging stops). Accept, or add one Schottky per input in rev B (≈ 0.3 V, ≈ 5 % at a 6 V panel).
- F201 1812L110/24 holds 0.73 A at 60 °C and 0.50 A at 85 °C (Littelfuse 1812L, rev 07/21/17, rerating table). Charger input is at most ≈ 0.49 A, and charging stops at +42 °C. OK.
- D201 (SMF12CA, 200 W) is modest for a long cabled-panel lead; 400 W SMA-class only if J202 leads exceed a few metres (agrees with the first review's D201 note).

#### R2-P6 · note · X5R MLCCs at +85 °C
X5R is rated only to +85 °C (EIA class II). Fine for rev A. Where a 0603/0805 X7R or X6S of the same value exists at JLC basic, prefer it around U206 and U207, which run hottest.

#### R2-P7 · note · LED201/LED202 take panel power
≈ 1.5–1.8 mA from SOLAR_IN whenever the CN3791 signals; ≈ 9–11 mW, several percent of a dim winter day's harvest, inside a sealed box where nobody sees them. Fit for rev A (bring-up); mark DNP for deployment builds. Agrees with the first review (P23).

#### R2-P8 · note · other power items
- U204 (TPL720): 3PEAK asks for ≥ 1 µF **plus 0.1 µF** at IN (Rev A.2 p.12–13). C236 (10 µF) is there; place C210 or a new 100 nF at pin 3 too.
- R208/R209 must be 1 % and ≤ ±100 ppm/°C (SBOS904A §6.5). Confirm the TCR of FRC0402F2491TS and 0402WGF1872TCE.
- D203/D204 leakage at heat, F202 3.5 A trip above the PH connector's 2 A, R233/C227 feedback values: agree with the first review (P19, P2, P21); nothing to add.
- BT201: the footprint has two end tabs and no pad under the cell; its document layer marks pad 1 "+" and pad 2 "−", consistent with a holder whose negative spring comes out to the second tab. The maker drawing is still not read, so the README's meter check on the first board stands.

### Power: verified
- **U201 CN3791** (Consonance Rev 1.0): pins 1–10 VG, GND, CHRG, DONE, COM, MPPT, BAT, CSP, VCC, DRV (p.3); VG–VCC 100 nF; COM 120 Ω + 220 nF; I_CC 550–650 mA (p.4); L rule and ripple (p.8); abs max VCC/DRV/CHRG/DONE 30 V against the 19.9 V TVS clamp, BAT/CSP/MPPT/COM 6.5 V (worst MPPT ≈ 4.0 V at clamp); DRV ≤ 8 V below VCC within the AO3401A's ±12 V. Footprint SSOP-10 at 1.0 mm pitch, pin 1 correct.
- **U202 HT7533-1** (Holtek Rev 2.81): SOT-89 1 GND, 2 VIN (tab), 3 VOUT; 30 V operating against 19.9 V.
- **U203 TMP390A2**: pins per p.3; R208 → +42/+37 °C (Table 7-1), R209 → +5/+10 °C (Table 7-2); open-drain wired-OR valid; R210 within the > 1 kΩ rule; DRL land pattern matches TI.
- **U204 TPL720F33** (3PEAK Rev A.2): 1 GND, 2 OUT, 3 IN; C_OUT 2.2–10 µF (C214 10 µF); VIN 6.5 V abs max.
- **U205 DS3231MZ** (19-5312 Rev 7): SO-8 pins per p.7; 32KHZ and RST may be open (RST has an internal 50 kΩ pull-up and must have no external one); C217 1 nF per p.10; VBAT 2.3–5.5 V.
- **U206 TPS63802** (SLVSEU9D): pins per Table 7-1; FB 0.5 × (1 + 510/91) = 3.30 V with R2 < 100 kΩ; L202 is TI-listed; C_IN/C_OUT above the effective minimums, no C_OUT maximum; PG 95 %/90 %, 14 µs; **DLA land pattern matches TI's DLA0010A**, including the long pads on the VOUT/L2/GND/L1/VIN side (pads 0.30 mm wide against TI's 0.25 mm; origin 0.075 mm off-centre: check the assembly centroid).
- **U207 TPS63020** (SLVS916I): pins 1–14 + exposed pad = PGND; 3.90 V; C229 100 nF at VINA; L203 ≥ 1 µH; 3 × 22 µF as TI; load disconnect when EN low; **DSJ land pattern and thermal pad match TI** (thermal vias are a layout task).
- **Q201, Q202, Q205, Q210 AO3401A** (AOS Rev 3.1): 1 G, 2 S, 3 D; VGS within ±12 V everywhere (D202 ≤ 8.61 V at Q201; CN3791 ≤ 8 V at Q202; ≤ 4.2 V at Q205/Q210). Orientations: Q201/Q205 drain to the source side, Q210 source to RAW_BAT, Q202 source to SOLAR_IN — all correct.
- **Q203, Q204, Q206 MMBT3904; Q207–Q209 2N7002**: pin 1 B/G, 2 E/S, 3 C/D; I_DSS ≤ 80 nA (25 °C) on WAKE_N leaves the Q210 gate within mV of RAW_BAT.
- **D201 SMF12CA** (V_RWM 12 V, V_BR 13.3–14.7 V, 200 W); **D202 MMSZ5237B** (checked against onsemi's MMSZ5221B series, the fitted maker's sheet not read: 7.79–8.61 V, ≤ 0.55 mA worst case); **D203/D204 PMEG4010CEH** (pin 1 = cathode, marked); **D205** DNP, cathode pad 1.
- **F201/F202** ratings as above. **L201 SWPA6045S470MT** (Sunlord, rev 2022-05-15, downloaded for this review): 47 µH, 1.40 A sat, 0.26 Ω max, −40…+125 °C; peak ≤ 0.79 A. **L203 PCR0420-1R5-M**: 5.5 A sat typ against a 4.6 A worst-case peak, comparable with TI's listed parts.
- **Polarised parts:** C201 (NCC APXG, 25 V polymer, 15,000 h), C207, C219, C233: pad 1 carries the "+" and sits on the positive net.
- **SW201** (C&K PTS810: 1–2 and 3–4 joined), **SW202** (ALPS SSSS811101: pin 2 common, 50 µA min load met by R228), **J201/J202** (Dorabo DB301V), **J203** (pin 1 left from the mating face, JST ePH p.4), **LED201** (anode pad 1).

## 4. Audio sheet

#### R2-A1 · should fix · U101 pin 3 (EN), net AUDIO_EN · no external pull-down
- **Problem:** GPIO7 has no pull at or after reset, and the TPS7A20's 500 kΩ EN pull-down is disconnected whenever EN is above V_EN(HI). After any ESP32 reset taken with audio on (and kept on by the RTC flag or USB), EN floats high and the ≈ 100 mW audio domain stays on until firmware drives GPIO7. Every other enable on the board (R128, R224, R235, R303, R402) has an external pull-down.
- **Evidence:** TPS7A20 SBVS338H pin functions p.4 ("When VEN > VEN(HI), the 500 kΩ pulldown is disconnected"); ESP32-S3 datasheet v2.2 Table 2-1 (GPIO7 no pull).
- **Fix:** 100 kΩ (C25741) from AUDIO_EN to GND. 33 µA while audio is on.
- **Status:** proposed. (The first review chose a firmware rule, A9.)

#### R2-A2 · should fix (layout) · D101 and D402 · TPD1E10B06 land pattern
The library pads are 0.6 × 0.6 mm at 1.0 mm centres; TI's DPY0002A pattern is 0.3 × 0.5 mm at 0.7 mm centres. Each terminal sits on the inner edge of its pad with ≈ 3× the solder: skew and tombstoning on a 0402-size part. **D402 on VBUS uses the same footprint.** Fix with a project footprint to SLLSEB1G pp.19–20. Agrees with the first review's A5, which named D101 only.

#### R2-A3 · notes
- **MICBIAS (U102 pin 5):** the regulator is on from reset until bring-up step 9 with no capacitor; TI allows the pin open but does not state stability. Keep TP101's stub minimal; optionally a DNP 1 µF footprint (SLAS831D §9.3.2.1 p.29, Table 121).
- **Full scale on a pseudo-differential input:** TI gives full scale as 2.1 Vrms per pin, out of phase; here the whole signal is on the P pin. If a per-pin limit applies, full scale is ≈ 6 dB lower than the README's 107 dB SPL. Covered by the G2 clipping-onset test (SLAS831D §7.5 p.13).
- **Input impedance:** 20 kΩ per pin, typical only, no tolerance or gain dependence, so the analog high-pass corners are estimates; at ±25 % the 100 Hz setting lands at 95–114 Hz. Measure (README already says so).
- **Crystal:** PCM1863 gives no drive level, margin or XI/XO capacitance; 15 pF caps give 12 pF only with ≈ 4.5 pF stray. Measure LRCK, cold-start at −40 °C (agrees with A8).
- **AVDD_A after AUDIO_EN goes low:** C114 (220 µF) back-feeds AVDD_A through R116 against the LDO's 150 Ω discharge: ≈ 0.75 V decaying with τ ≈ 0.14 s. The PCM1863 has no reset pin, so keep AUDIO_EN low ≥ 0.5 s before a retry (README step 11).
- **Dielectrics:** C128 (0.1 µF X7R) sits on VMID_PRE, against the README's A5 rule; its pickup is ≈ 60 dB down through C127 and R121/C119, negligible. C105 (VREF, X5R): include in the tap test.
- **J101 contacts:** tin-plated, 30–50 mΩ, in the µV mic path; ask JST for gold for deployment (agrees with A9).
- **Preamp switch-on:** Q101 charges C125 through R129 at ≈ 330 mA peak against the LDO's 360 mA minimum limit; a click, harmless between recordings.

### Audio: verified
- **U102 PCM1863DBTR** (SLAS831D Mar 2018): all 30 pins (pp.10–11); MD0 = GND → I²C, MS/AD = GND → 0x4A (Table 23); unused inputs reach only DNP parts ("do not connect", p.28); GPIO2 resets to input with pull-down; SCKI to GND with XTAL selected; 24.576 MHz within the 15–35 MHz crystal range (p.16); every README register value decodes as stated: 0x20 = 0x91, 0x26 = 0x07 (required: reset ÷4 would give 96 kHz BCK), 0x27 = 0x3F, 0x0B = 0x44, 0x06/0x07 = 0x50/0x60 select pins 3/1 and 30/28, PGA 0x40/0x28 = +32/+20 dB, GPIO 0x10/0x12/0x14, 0x71, read-back 0x72–0x74, Page 3 0x15 (Tables 27–121); abs max 3.9 V supplies, VIN −1.7…5 V; DBT land pattern within TI's.
- **U101 TPS7A2033P:** 1 IN, 2 GND, 3 EN, 4 NC, 5 OUT; C_OUT 0.47–200 µF effective (the 22 µF and 220 µF sit behind 10 Ω and 470 Ω); dropout ≈ 15 mV at 30 mA; 150 Ω active discharge.
- **U103 OPA1662** (SBOS489A): pins per Fig 4-1; 3 V minimum supply against ≈ 3.21 V; V_CM 0.5–2.2 V against 1.6 V; swing and loads; unity-gain stable; preamp noise recomputed ≈ 1.1 µV A-weighted, as the README.
- **U104 TS5A23166** (SCDS196J): pins and IN1/IN2 mapping; V_IH 2.0 V met by the PCM GPIO; corners 36 / 102 / 1001 / 1066 Hz recomputed; the "VSON8" footprint is the DCU gull-wing pattern (0.508 mm pitch, 12 µm error at the outer pads).
- **Y101** pads 1/3 crystal, 2/4 GND; YXC land exact. **Q101/Q102** pin order. **D101** pin 1 on the signal. **J101** pin 1 and tabs per JST GH. **C114, C121, C127** derating (31 %, 26 %, 10 %), polarity pad 1 = +. Signal-path caps C0G by part-number decode.

## 5. LTE sheet

#### R2-L1 · should fix (owner decision, existing open item) · J301 · SIM holder rated −35…+75 °C
The SOFNG drawing gives −35…+75 °C as storage, with no operating range; it is push-push. Agrees with the first review (L7). For rev A accept and keep the holder in the coolest part of the box; for deployment, a −40…+85 °C holder or a solder-down MFF2 eSIM (needs an eSIM-capable operator plan).

#### R2-L2 · note (doc and firmware) · U302 OE · the README's reasoning for L3 is wrong, the circuit is fine
OE = 0.909 × VCCA and the OE thresholds are ratios of VCCA (V_IH 0.65 × VCCA, V_IL 0.35 × VCCA), so OE never crosses its threshold: the translator is enabled from the moment VDD_EXT starts rising until it collapses. The README says OE "crosses its 0.65 × VCCA threshold as VDD_EXT reaches ≈ 1.3 V". No supply-derived OE can meet TI's §8.3 advice; Quectel's own 10 kΩ/120 kΩ behaves the same, so keep the divider. Correct the README; firmware should flush UART RX and ignore STATUS for ≈ 100 ms after VDD_EXT appears and during shutdown. (TXS0108E SCES642L §5.3, §8.3; EG810M-EU HD V1.0 Fig. 19.)

#### R2-L3 · notes
- **STATUS before boot:** between VDD_EXT on (≈ 10 ms after PWRKEY) and STATUS high (≥ 5 s), an undriven module STATUS is pulled up by the TXS0108E's internal resistors against the ESP32's pull-down: LTE_STATUS may read an ambiguous high. Confirm with `RDY`/`AT` before trusting STATUS; scope it at bring-up.
- **PWRKEY:** the off pulse (≥ 650 ms) is shorter than the planned 800 ms on pulse, so pulsing a module that is already on turns it off: read STATUS first (HD §3.6.1). C316 (10 nF ±10 %) sits at Quectel's 10 nF limit, as in their Fig. 7.
- **Power-down order:** after an ESP32 reset with the modem running, GPIO11 floats and R235 cuts VMODEM with no `AT+QPOWD` (Quectel warns of flash corruption), and VMODEM's ≈ 640 µF can outlast 3V3 so VCCA briefly exceeds VCCB at the TXS0108E. Same class as W5: firmware keeps LTE sessions short and the RTC flag set; no hardware change proposed.
- **R301 (0805 0 Ω):** the jumper's current rating is not in the JLC record against 1.5 A typical, 2 A maximum peaks (HD Table 41). Confirm it, or use a 1206 jumper (agrees with L9).
- **TXS0108E levels:** A-port V_IL 0.15 V against the module's V_OL 0.2 V; B-port V_IH VCCB − 0.4 V against the ESP32's 0.8 × VDD. Paper mismatches at µA loads, as in Quectel's reference; scope at bring-up (agrees with L9).
- **Optional:** tie unused A6–A8/B6–B8 to GND through 51 kΩ as Quectel's standard manual does; if the DNP filter caps (C317–C323) are ever fitted, start at 22 pF (TI characterises 15 pF); an ESD footprint (< 0.05 pF) at J302 as in the EU QuecOpen reference.

**Standard-firmware manual.** Quectel's *EC800M&EG810M 系列硬件设计手册* V1.3 (2024-05-14, Chinese; covers EG810M-CN/LA) was downloaded from developer.quectel.com to `hardware/datasheets/pdf/Quectel_EC800M_EG810M_Series_HD_V1.3_CN.pdf` (git-ignored). For every pin Auris connects it agrees with the EU QuecOpen manual: functions and GND list, VBAT range and capacitor array, PWRKEY ≥ 700 ms on / ≥ 650 ms off with 4.7 kΩ/47 kΩ/10 nF, STATUS ≥ 5 s and UART ≥ 10 s after PWRKEY, RESET_N, USB_BOOT 4.7 kΩ, the SIM network, the TXS0108E circuit, 1.8 V I/O levels, temperature and the footprint. Differences are only on pins Auris leaves open (GNSS on pins 2/44/99 for GNSS variants; QuecOpen camera/LCD/keypad functions) and the RF reference (plain π, as Auris). The English V1.4 is behind a Quectel login.

### LTE: verified
- **U301 EG810M-EU** (EU HD V1.0, Table 6 pp.18–23): every connected pad's function and direction; RTS/CTS wired module-to-MCU as Quectel requires (Table 20 note 2); TX/RX crossed correctly through A1/B1 and A2/B2; GND list identical in both manuals; RESERVED pads open. VBAT 3.9 V within 3.4–4.3 V (abs max 6 V); C301–C306 exactly Fig. 6; PWRKEY driver exactly Fig. 7; SIM network exactly Fig. 18; USB_BOOT, RESET_N, USB and DBG test pads as Tables 14–20 ask; VDD_EXT load ≪ 50 mA.
- **Bands and approvals:** B1/3/5/7/8/20/28 (Table 34) cover Europe and the Australian FDD layers (Telstra B1/3/5/7/28, Optus B1/3/7/28, TPG B1/3/5/8/28); CE and RCM. No B40 (TDD capacity only).
- **U302 TXS0108E** (SCES642L): pinout; VCCA 1.8 ≤ VCCB 3.3; OE 1.64 V against V_IH 1.17 V; pull-ups off while OE is low, so the ESP32 pulls define the lines with the modem off; LTE_STATUS high ≈ 3.0 V against the ESP32 pull-down.
- **Q301, D301, J301, J302, C301:** pin orders; D301 REF2 on USIM_VDD (Semtech option 1); J301 contact map C1/C2/C3/C5/C7 and pad order match the SOFNG drawing; **J302 matches Hirose's recommended pattern exactly**; C301 62 % voltage use, polarity pad 1.

## 6. MCU sheet

#### R2-M1 · must fix · Q401/Q402/R414/R415/C406, with U206 PG → ESP_EN · switching the card supply on can reset the ESP32 and power the board off
- **Problem:** C406 is gate–source, so it delays Q401's turn-on but does not slow it: once VGS passes threshold the AO3401A charges C404 (10 µF, ≈ 5.5 µF at 3.3 V) almost as a step from the 3V3 rail (≈ 35–40 µF effective). Charge sharing alone puts 3V3 at ≈ 3.3 × 36/41.5 ≈ 2.86 V, below the TPS63802's 90 % power-good threshold (2.97 V), and the converter is in power-save mode at light load. Since the first review's W15, PG drives ESP_EN: if the dip lasts longer than PG's 14 µs deglitch, the ESP32 resets, PWR_HOLD floats and the latch drops power. The first review rated the dip a measurement item (M11) before PG was tied to EN mattered.
- **On the board:** a recorder that turns itself off whenever it powers the card for a recording, worst at low battery. The same step happens if a card is inserted while SD_VDD is on.
- **Evidence:** TPS63802 SLVSEU9D p.6 (V_PG falling 90 %, t_PG 14 µs), Table 9-1; AO3401A Rev 3.1 (V_GS(th) −0.5…−1.3 V, C_iss 645 pF); capacitances from the BOM with typical DC-bias loss.
- **Fix (one part, two values; parts already on the BOM):**
  - add **10 nF gate–drain** on Q401 (SD_PSW_G to SD_VDD, 0402 X7R, C15195);
  - **R415 10 kΩ → 100 kΩ** (C25741);
  - **R414 100 kΩ → 1 MΩ** (C26083);
  - keep C406 100 nF gate–source: C406 ≫ C_gd keeps Q401 off while 3V3 itself ramps at power-up (VGS ≈ −0.3 V).
  - Result: Miller-limited slew ≈ 2 V/ms, so SD_VDD ramps in ≈ 2 ms at ≈ 15 mA; turn-on delay ≈ 6 ms; the gate still settles at ≈ 0.3 V (VGS ≈ −3.0 V). Turn-off slows too (gate τ ≈ 110 ms; Q401 can conduct for up to ≈ 0.2 s after SD_PWR_EN goes low), so the README's card power-cycle wait goes from ≥ 100 ms to **≥ 0.5 s**.
  - Alternative: a slew-controlled load switch with quick output discharge (TPS22917/TPS22919 class), which also discharges SD_VDD (R2-M3). Owner decision; the AO3401A + 2N7002 pair was chosen on 2026-11-17.
  - Firmware: power SD_VDD only with a card detected, and cut it on removal.
  - Bring-up: scope 3V3 and ESP_EN at card enable, at minimum battery, with the converter in power-save mode.
- **Status:** proposed.

#### R2-M2 · should fix (low) · C403 · PG discharges 1 µF directly
TI rates the PG pin to sink 1 mA (V_OL ≤ 0.4 V at 1 mA); every brown-out dumps C403 (1 µF at 3.3 V) through it, tens of mA for ≈ 0.1 ms. With PG now supervising EN, the RC only needs to exceed t_STBL = 50 µs: **C403 → 100 nF** (C1525) keeps τ = 1 ms. Or 1 kΩ in series between PG and the EN node. (SLVSEU9D §9.3.10; ESP32-S3 datasheet v2.2 Table 2-13.) The first review judged it acceptable (W15); cheap enough to fix.

#### R2-M3 · note (firmware) · GPIO44 (U0RXD) back-feeds the card at boot
GPIO44's weak pull-up is on at and after reset and stays on through the ROM and second-stage bootloader, feeding SD_VDD through R410 before any app code runs. The README's firmware rule handles it if firmware drives D0 low and waits with SD_VDD off **before** the first card power-on (≥ 100 ms today, ≥ 0.5 s with R2-M1), so the card always sees a clean power cycle. Alternatives if it misbehaves: SD_D0 to GPIO37 (free on the N16R2), or the load switch with output discharge (R2-M1). Agrees with the first review's M5.

#### R2-M4 · notes
- **Floating inputs after reset:** GPIO4, 5, 9 (DNP options) and GPIO35–37 (spare): enable internal pull-downs in firmware. The README covers GPIO9 only.
- **eFuses:** never burn EFUSE_DIS_USB_JTAG or EFUSE_STRAP_JTAG_SEL (GPIO39–42 carry the modem UART; GPIO3 = SD_CD would then select pad JTAG). Optionally burn EFUSE_DIS_USB_OTG_DOWNLOAD_MODE (the ROM drives GPIO38–40 in OTG download) and suppress the ROM log on UART0 (LED401 flicker, R2-G8).
- **Cold power-up glitches:** GPIO18 drives a 60 µs high glitch into AUD_SDA and the unpowered audio domain (chip Table 2-2). Minor.
- **Espressif options:** 22/33 Ω and reserved caps on D± (R405/R406 are 0 Ω, no cap pads) and a series resistor on every SDIO line (only CLK has one). Optional footprints if EMC needs them.
- **Chip variant:** the ESP32-S3R2 inside the N16R2 is listed end-of-life in chip datasheet v2.2 and replaced by the ESP32-S3RH2; modules from stock may carry either, same pins and VDD_SPI (first review F22). No action.

### MCU: verified
- **U401** all 41 pads (WROOM-1 v1.8 Table 3-1) and the footprint against Fig. 11-1; −40…+85 °C; GPIO35–37 free on quad-PSRAM variants; VDD_SPI 3.3 V; straps GPIO0 = 1 (R417), GPIO46 = 0 (internal), GPIO45 = 0 (R402 + internal), GPIO3 ignored with default eFuses; EN: PG holds it low to 95 %, then ≈ 13.9 ms RC to V_IH, far above t_STBL.
- **GPIO allocation across all four sheets:** every GPIO used once, no conflicts; every enable except AUDIO_EN (R2-A1) has an external pull-down; GPIO20's reset-time D+ pull-up is contained by D401 pin 5 being open; ADC inputs on ADC1_CH0/CH1/CH4 with calibrated ranges 0–1.6 V (6 dB) and 0–2.9 V (12 dB).
- **J401** pad order and CC/D± mapping; 5.1 kΩ Rd; **D402** V_RWM ±5.5 V for VBUS; **D401/D403** SRV05-4 options 3 and 1.
- **J402** contacts 1–8, the `CD` pad, cover pads and hole positions per the SHOU HAN drawing; pull-ups on CMD and DAT0–3, none on CLK; R418 33 Ω; D403 on the card side.
- **Q401/Q402** pin order; card off by default; Q401's body diode cannot back-feed. **LED401** cathode pad 2.

## 7. Placement readiness

Every footprint has the manufacturer's pin numbering and pin-1 position, and the IC land patterns match (TPS63802 DLA, TPS63020 DSJ, TSSOP-30, TSSOP-20, SOIC-8, SOT-563, SSOP-10, DCU, SOT-23, WROOM-1, U.FL). What layout still needs from the schematic or the library:

| # | Severity | Item | Action |
|---|---|---|---|
| R2-X1 | should fix | **U301 LGA-109:** all 103 signal/GND pads are 1.0 × 0.7 mm; Quectel's Fig. 40 (EG810M-EU HD V1.0 p.67) gives the **48 outer-ring pads 1.0 × 0.6 mm** (inner rings 1.0 × 0.7, centre 1.3 × 1.3, all positions match). 0.4 mm gaps at 1.1 mm pitch instead of 0.5 mm | Edit the outer ring to 1.0 × 0.6 mm in a project footprint; stencil per Quectel |
| R2-X2 | should fix | **D101, D402** TPD1E10B06 (R2-A2) | TI DPY0002A pattern |
| R2-X3 | should fix | **F201 (`R1812`) and F202 (`F1812`)** differ from Littelfuse's 1812L pad layout (1.78 × 3.15 mm, 3.45 mm gap): F201 1.28 × 3.46 / 3.00 mm gap, F202 1.41 × 3.50 / 2.30 mm gap. **C207** (`CAP-SMD_BD4.0`) has a 0.52 mm pad gap under the can against Panasonic's 1.0 mm terminal gap: a bridge shorts RAW_BAT to GND | Littelfuse land on both fuses; widen C207's gap to ≥ 1.0 mm |
| R2-X4 | should fix | **Test pads:** every TP uses the 0.5 mm library pad; the BOM asks for 1.0 mm (52 pads on the four sheets, plus the two TMP_SET pads of R2-P2) | 1.0 mm pad footprint; the 2.54 mm pogo row as one block |
| R2-X5 | should fix | **J401 USB-C:** shell slots for pads 3/4 are 1.20 mm (copper 1.60) against 1.40 (1.80) in the HCTL drawing, pads 1/2 ≈ 0.1 mm off; layout drawn for a 0.8 mm board | Match the drawing; pin-in-paste on 1.6 mm |
| R2-X6 | note | **Conformal coating:** 1 MΩ latch nodes (RTC_INT_N, Q206_B, RTC_WAKE, TP208), TMP390 SET pins (TI §10.1 recommends coating where they may see condensation), the mic input | Coat these areas, or adopt P22 (section 8), which removes the latch's 1 MΩ nodes |
| R2-X7 | note | **Stack-up:** the exported PCB is still EasyEDA's 2-layer default; Quectel asks for ≥ 4 layers, solid ground under U301 and nothing on layer 1 beneath it, 50 Ω ANT feed, 90 Ω USB pairs | Set 4 layers before placement |
| R2-X8 | note | **Antennas:** ESP32 PCB antenna at a board edge with Espressif's keep-out; LTE FPC antenna off-board, as far from it and from the mic front end as the enclosure allows; Quectel asks ≥ 20 dB isolation (B7 uplink is 2.50–2.57 GHz) | Place with the enclosure (ADR-020) |
| R2-X9 | note | **High-current nets:** J203 → F202 → Q205 → RAW_BAT → Q210 → VBAT_SW → U207 → VMODEM → R301 → U301 (≈ 3 A peaks); the charger loop C203–Q202–D203/D204–L201 tight; R202 Kelvin to U201 pins 7/8; U206/U207 loops per TI; D203/D204 ≈ 1 cm² cathode copper; thermal vias under U207 | Layout notes |
| R2-X10 | note | **Sensitive nets:** MIC1_OUT, AIN pairs, VREF, crystal (guard ring), mic return through R114 only; keep the TPS63802/TPS63020/CN3791 loops and SD/I²S lines away (audio README layout rules) | Layout notes |
| R2-X11 | note | **Placement constraints:** U203 at the pack edge (R2-P3); U301 ≥ 3 mm from other parts (Quectel Fig. 40 note); J402 and J401 reachable through sealed ports (F5-06); LED401 behind a light pipe (F5-05); SW201/SW202 reachable; SW202 locator holes come out as NPTH; J402 holes are ⌀1.2 mm against SHOU HAN's ⌀1.0 (optional); U206 centroid offset 0.075 mm | Layout notes |
| R2-X12 | note | **Polarity marks:** checked on every polarised part (tantalums, electrolytics, diodes, LEDs, BT201 "+", J203 pin 1). J201/J202 need "+"/"−" silkscreen (first review P23); SW202 needs ON/SHIP silkscreen after the meter check | Silkscreen at layout |

## 8. Comparison with the first review (phase 2)

Sections 2–7 were written before opening `2026-11-17-schematic-review.md`, the cost-change log or the part notes' *Findings*. This section compares them.

### 8.1 Every "fixed" or "applied" item is in the CSVs

Checked by script against the sheet CSVs, not the README text: W2 (D401 pin 5 NC, D402 on VBUS), W12 (TP404–TP415), W15 (U206 PG → ESP_EN, R229 gone), W17 (D403 on SD_CLK/CMD/D0/CD, REF2 on 3V3), P1 (L201 SWPA6045S470MT), P2 (F202 1812L200THPR), P3 (R237 1 MΩ), P4 (BT201 1 = RTC_VBAT), P5 (R225 10 kΩ), P6 (R215 DNP), P7 (C228 22 µF; C229 noted at VINA), P8 (C236 on RAW_BAT), P9 (C217 1 nF), P10 (D205 DNP), P13 (PTS810, SSSS811101, R228 47 kΩ), P14 (R209 18.7 kΩ), P15 (J203 XY), A1 (C127 1 = VMID_PRE), A2 (U104 TS5A23166), A7 (J101 tabs GND), L2 (J301 EH GND), L3 (C307 DNP), L4 (C316 on PWRKEY), L5 (C317–C323 DNP), M2 (U401 C2913205), M4 (R416 100 Ω, LED401 KT-0805G), M6 (J401 shell, J402 cover, CD → GPIO3), M7 (R417), M8 (R418, SD_CLK_MCU), D202 MMSZ5237B, Q201/Q202 AO3401A, U301 C20421924. **All 34 present.** Every row of `2026-11-17-bom-cost-changes.csv` with a new LCSC code matches the BOM line of its designators. The README text fixes (W4 sleep table, A3 step 9, W9/P3 panel class, P11/P12 descriptions) are in place.

### 8.2 Where I agree

W1 and the 2026-11-18 module choice; W2 and its fix; W4 sleep budget (I get the same ≈ 106 µA / ≈ 160 µA); W5 (any reset powers off; firmware); W7 (modem start-up sag; bench and firmware); W8 climate table; W9 6 V panels only; W10/P16 (TMP390 open output and placement); W11 cross-sheet nets; W13 bands; W14 pin budget; W17 microSD ESD; P1–P15 and P17, P19–P21 as written; A2, A3, A5 (D101 land), A6–A8; L2–L5, L7–L9 (including the EG810M footprint's outer pads: I measured Fig. 40 independently and get the same 0.1 mm); M1–M10. The first review found the hard blockers (W1, W2) and the BOM-level errors, and every fix it claims is really there.

### 8.3 Where I disagree, and why

| First review | My view | Why |
|---|---|---|
| **M11** (note): card supply ramps in 0.1–0.3 ms, "measure the 3V3 dip" | **Must fix now** (R2-M1) | W15 later tied the TPS63802 PG to ESP_EN, so a 3V3 dip below 90 % for > 14 µs is now a reset and a power-off, not just a dip. The charge-sharing estimate (≈ 2.86 V) is below that threshold. A one-part fix exists. |
| **W16/A4**: record only with VBAT_SW ≥ 3.35 V | **3.35 V is not enough**; ≥ 3.6 V or measure (R2-G6) | 3.35 V clears dropout (≈ 15 mV) but TI specifies regulation and PSRR only for VIN ≥ VOUT + 0.3 V. Near dropout, VBAT_SW ripple (including the TPS63802's power-save bursts) reaches the mic node through a bias filter that is only −36 dB at 100 Hz. |
| **W6**: if the pack trips, "10 kΩ in series with the gate pull-down plus ≈ 220 nF gate–drain" | **Don't fit those values as stated**; add option footprints now (R2-G3) | With C218 left at 47 nF gate–source, 220 nF gate–drain makes a capacitive divider at battery hot-plug: the gate sits at ≈ 18 % of RAW_BAT, VGS ≈ −3.4 V, and Q210 turns the board on every time a pack is plugged in. C218 must be ≫ C_gd (R2-G3: 2.2 µF with 100 nF). Also, SW201 shorts SYS_GATE directly, so a resistor "in series with the gate pull-down" (R227) does not slow a button wake; the resistor has to sit at the gate. And with no footprints, any fix after the bench is a respin. |
| **A9**: AUDIO_EN floats high after a reset; firmware drives it low | **Add a 100 kΩ pull-down** (R2-A1) | Firmware cannot act during the reset itself; every other enable already has a hardware pull-down. |
| **W15** note: C403 discharge through PG "acceptable" | Cheap to fix: C403 → 100 nF (R2-M2) | PG is rated to sink 1 mA; with PG supervising, the 1 µF no longer buys anything. Low severity either way. |
| **P12/P2**: electrolytic life "much longer at the real duty cycle" | Agree for rev A; **long-life or polymer parts for deployment** (R2-P4) | C207 is biased continuously, and Australian enclosures spend long hours above 60 °C. |
| **L3 / LTE README**: OE "crosses its 0.65 × VCCA threshold as VDD_EXT reaches ≈ 1.3 V" | Circuit right, reasoning wrong (R2-L2) | OE is a fixed fraction of VCCA, so it never crosses the ratio threshold: the translator is enabled throughout the ramp. Firmware should ignore the lines briefly. |
| **P22** (proposal, after the bench): drive WAKE_N directly from the RTC INT and drop Q206, Q207, R222, R223 | **Do it now, before layout** (owner decision; also drop R219) | It removes three 1 MΩ nodes that condensation can upset (R2-X6, and the first review's own MMBT3904 note) and 4.6 µA of sleep current. DS3231M INT/SQW is open-drain, pull-up allowed to 5.5 V regardless of VCC, V_OL 0.4 V at 3 mA (19-5312 p.2, pin table), so it can pull WAKE_N (R228 to RAW_BAT, ≤ 89 µA) directly, and it goes high-impedance below V_PF as the inverter does today. Nothing the bench would show changes this. |
| **U6 part note** (USB-C slots, optional) | Match the drawing at layout (R2-X5) | Free to fix while the footprint is being edited anyway. |

### 8.4 What the first review missed

| ID | Finding |
|---|---|
| **R2-P1** (must fix) | TMP390 reads its trip resistors at a POR below its rated supply on every slow dawn ramp. (Its part note says only that the output state during the 10 ms reset is unspecified.) |
| **R2-M1** (must fix) | The card-supply step and PG → EN interaction (above). |
| **R2-G1** | No hardware UVLO: after a depletion the RTC flag closes the latch as soon as KEEP_ALIVE returns, and the ESP32 tries to boot from a 2 V cell on a 50–180 mA trickle charge; F4-04 then rests on firmware. |
| **R2-G2** | The MCU cannot read the service button: presses while awake, long presses and a stuck-closed button are invisible. |
| **R2-G4** (sharpens P18) | The hot-panel harvest loss is large (≈ 30 % of maximum at a 70 °C cell) and matters for cabled panels in sun with the recorder in shade; R204 should be a per-region value now, not after the panel is chosen. |
| **R2-G6** | The TPS63802's power-save mode as an audio-band source; a MODE option footprint. |
| **R2-P2** | No production test for the cut-out; TI's trip test needs only two pads. |
| **R2-X3 (part)** | F201's footprint (`R1812`) also differs from Littelfuse's land; C207's 0.52 mm pad gap under the can. |
| **R2-A2 (part)** | D402 on VBUS uses the same undersized-pitch X1SON footprint as D101. |
| **R2-L2, R2-L3** | OE rationale; STATUS ambiguity before boot; PWRKEY pulse on an already-running module; VCCA > VCCB on an abrupt power-down. |
| **R2-M4 (part)** | GPIO4/5 and GPIO35–37 float after reset (README covers GPIO9 only). |

### 8.5 My view on each item the first review leaves open

| Open item | View |
|---|---|
| **W6** Q210 inrush (bench) | Bench test 2 with the real pack, but add the option footprints now (R2-G3) so a fix needs no respin. |
| **W7** modem start-up sag (bench) | Agree. Firmware rule stands; add a transmit floor (R2-G5). Decide C233 after test 9 (C301 already meets Quectel). |
| **P18** MPPT start and hot panels | Owner decision now (R2-G4): per-region R204, recorded per unit. |
| **BR1220 at −40 °C** | Agree: bench it. If it fails, a CR1225 holder with a −40 °C cell in rev B. |
| **W5** any reset powers off (firmware) | Agree, plus a crash counter and early PWR_HOLD in the bootloader (R2-G8). R2-G1 makes the depletion case safe in hardware. |
| **W16** low-battery floor for audio (firmware) | Disagree with 3.35 V (R2-G6). |
| RTC register rules (firmware) | Agree as written (INTCN = 1, BBSQW = 0, EN32KHZ = 0, bus clear). |
| Modem start-up sequence (firmware) | Agree; add: read STATUS before any PWRKEY pulse, confirm with `RDY`, ignore lines for ≈ 100 ms around VDD_EXT edges (R2-L2, R2-L3). |
| Flash/PSRAM at 80 MHz (firmware) | Agree. |
| **A5** D101 land (layout) | Agree, and D402 too (R2-A2). |
| **F202** land (layout) | Agree, and F201 too; also C207 (R2-X3). |
| EG810M-EU outer pads 0.1 mm wider (layout) | Confirmed independently from Fig. 40 (outer ring 1.0 × 0.6 mm): edit the footprint (R2-X1). |
| 1.0 mm test pads (layout) | Agree (R2-X4). |
| **P16** TMP390 placement (layout) | Agree (R2-P3); plus R2-P1 and R2-P2, which are schematic changes. |
| **L7** consumer SIM holder | Agree: rev A accept; deployment needs a −40…+85 °C holder or MFF2 eSIM (R2-L1). |
| **M9** microSD holder temperature | Agree: qualify at −40 °C on the bench; no −40 °C-rated push-push holder is on the BOM. |
| LTE open item 3: VBAT TVS (D205 not fitted) | Agree to leave it not fitted: the rail is internal and regulated, and no common TVS with V_RWM 4.7 V clamps below the module's 6 V. Keep the footprint. |
| LTE 4: stack-up | Agree: 4 layers. Note the exported PCB is still set to 2 (R2-X7). |
| LTE 5–8: stock, SIM plan, RED/RCM, firmware | Agree; buy the EG810M-EU and PCM1863 now (R2-G7). |
| LTE 9: footprint | Closed by R2-X1. |
| Standard-firmware manual | Read in its Chinese V1.3 edition (EG810M-CN/LA): no difference for any pin or circuit Auris uses (section 5). The English V1.4 is behind a Quectel login; worth a look once the owner has an account, but it does not block the freeze. |

## 9. Freeze recommendation and the owner's decisions

**Recommendation: freeze after the listed fixes.** Apply the two must-fixes and the should-fixes the owner accepts in one batch (phase 3), rebuild, update the EasyEDA project in place, run Update PCB, export, and pass `easyeda_check.py` on all four sheets. The layout items (section 7) are footprint and placement work and do not need to wait for the freeze.

**Proposed schematic batch** (all parts but one are already on the BOM as JLC basic or preferred parts):

| # | Finding | Change |
|---|---|---|
| 1 | R2-P1 (must) | Push-pull voltage detector (≈ 2.9 V) from TEMP_3V3 supplying U203 VDD and R210; C212 to its output. New part, chosen in phase 3 |
| 2 | R2-M1 (must) | + 10 nF Q401 gate–drain (C15195); R415 → 100 kΩ; R414 → 1 MΩ |
| 3 | R2-G1 | U206 EN: 150 kΩ (C25755) from VBAT_SW, 100 kΩ (C25741) to GND |
| 4 | R2-G2 | SW201 to new BTN_N; Schottky LATCH_LOGIC → BTN_N; 1 MΩ BTN_N → RAW_BAT; 2N7002 BTN_N → GPIO35 |
| 5 | R2-G3 | Q210 gate net Q210_G: 0 Ω SYS_GATE → Q210_G (fitted), C218 to Q210_G, DNP 0603 Q210_G → VBAT_SW |
| 6 | R2-G6 | U206 MODE: 100 kΩ to GND, DNP 0 Ω to GPIO36 |
| 7 | R2-P2 | Test pads on TMP_SETA and TMP_SETB |
| 8 | R2-A1 | 100 kΩ AUDIO_EN → GND |
| 9 | R2-M2 | C403 → 100 nF |
| 10 | P22 (first review) | INT/SQW → WAKE_N; remove Q206, Q207, R219, R222, R223 |

Estimated cost: one new extended part (the detector, ≈ $0.2–0.5 plus a $3.07 Economic-PCBA feeder fee: ≈ +$3.5/board at 10, ≈ +$0.5 at 100) and a few cents of basic passives; P22 removes four parts. `bom_cost.py` gives the real figure in phase 3. If the button-sense Schottky is not already on the BOM it adds a second extended code (choose a JLC basic one).

### Decisions the owner must make (grouped)

**A. Schematic changes inside owner-decided blocks**
1. R2-P1: accept the detector-switched TMP390 supply (ADR-007 block). *Recommended.*
2. R2-G2: add button sensing on GPIO35 (ADR-003 latch). *Recommended.*
3. P22: drive WAKE_N from the RTC INT directly and remove the inverter (ADR-003 latch). *Recommended, now.*
4. R2-M1: the AO3401A soft-start values, or a load-switch IC (ADR-012 card switch). *Recommended: the AO3401A values.*
5. R2-G3: Q210 soft-start option footprints (ADR-003 latch). *Recommended.*

**B. Values and firmware policy**
6. R2-G4: R204 per region / panel (402 kΩ Europe, ≈ 330 kΩ Australia or hot cabled panels).
7. R2-G6: recording gate VBAT_SW ≥ 3.6 V, or keep 3.35 V and decide on G2 noise data.
8. R2-G5: modem transmit floor (≈ 3.3 V under load, tuned in test 9).

**C. Procurement and deployment BOM**
9. R2-G7: buy the EG810M-EU and PCM1863DBTR prototype quantities now.
10. R2-P4: long-life or polymer C207/C219/C233 for deployment units.
11. R2-L1 and M9: SIM holder (−40…+85 °C holder or MFF2 eSIM) and microSD holder qualification for deployment.
12. R2-P7: LED201/LED202 not fitted on deployment units.

**D. Accept as notes** (no change): R2-P5, P6, P8, A3, L3, M3, M4 and the layout notes in section 7.

## 10. Change control after the freeze

As the handover specifies: every sheet-CSV change after the tag `schematic-rev-a-freeze` needs a row in `hardware/review/schematic-change-log.csv` (`date,id,sheets,designators,change,reason,evidence,owner_approval,check_result`), the owner's approval before the change, and the full loop (`build_guide.py`, capture or tidy, Update PCB, export, a passing `easyeda_check.py`). Layout-only changes (placement, routing, footprint geometry with unchanged pads and nets) need no entry; the footprint edits in R2-X1–X5 are of that kind.

## Appendix: sources added in this review

- `hardware/datasheets/pdf/Quectel_EC800M_EG810M_Series_HD_V1.3_CN.pdf` (Quectel, 2024-05-14).
- `hardware/datasheets/pdf/C36414_SWPA6045S_series_sunlord.pdf` (Sunlord SWPA series, revised 2022-05-15).
- `hardware/datasheets/pdf/mmsz5221bt1-d_onsemi.pdf` (onsemi MMSZ5221B series Rev 17, used as a stand-in for the hongjiacheng MMSZ5237B).
- JLC stock snapshot 2026-11-19 (section 2.11).

All three are git-ignored, like the rest of `hardware/datasheets/pdf/`.
