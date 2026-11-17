# 20 — FieldMesh Hub v2 / Node v4 power review, and modem cost options

**Date:** 2026-10-23. **Status:** Review and **proposed** options. Nothing here changes a decision until it is recorded in `14-DECISION-REGISTER.md`.

**Sources reviewed** (FieldMesh repo `~/Documents/projects/Data-Logger-network---ESP32`):

| Board | Revision | Where | Build status |
|---|---|---|---|
| Hub v2 | r6, 2026-10-10 | `hardware/FieldHub_v2/revisions/2026-10-10-r6` (branch `feat/hub-r6-bringup-harness`) | Five boards printed; bring-up in progress |
| Node v4 | 2026-10-22 prototype release | `hardware/NODE_v4/release/2026-10-22-v4-prototype` (branch `feat/fm2-provisioning-redemption` only) | Prototype order package; not built |

Connections below come from the pad-level netlists in the EasyEDA projects, not only from the design notes. Prices are LCSC, 100 units, 2026-10-23.

## 1. What the two boards do

Both boards use the same scheme Auris has planned (ADR-003): the battery always feeds a nano-power keep-alive rail for the RTC, and everything else sits behind a P-FET that the RTC alarm turns on and the MCU holds on.

| Function | Hub v2 r6 | Node v4 | Auris plan today |
|---|---|---|---|
| Solar charger | CN3791 buck, MPPT set 5.6 V, 600 mA (`C154992`) | CN3791 buck, MPPT set 6.05 V, 600 mA, series diode blocks night back-feed | BQ25185 linear (`C19725033`) |
| Panel protection | 1.1 A PPTC, SMF12A TVS, series Schottky | 1.1 A/24 V PPTC, SMF12CA TVS, AO3407A reverse-polarity switch with 8.2 V Zener gate clamp | Not designed |
| Charge temperature limit | **None** | **TMP390A2 hot/cold switch** clamps the MPPT pin; trip +5 °C / +42 °C; powered from the panel only | BQ25185 TS pin (NTC) |
| USB charging | None (USB is data only) | None (TP5100 removed) | Planned ("charge + service") |
| Battery connection | AO3407A reverse-battery switch, then 1.1 A PPTC | 1.1 A PPTC + AO3401A; reversed battery **not** blocked while the panel is live (accepted risk, keyed harness) | Not designed |
| Keep-alive rail | TPL720F33 (1.4 µA Iq) → DS3231MZ + latch; CR1220 on RTC VBAT | Same | TPS7A0230 (proposed, ADR-010); no backup cell |
| Main switch + wake latch | AO3407A, gate RC 100 kΩ/47 nF; wired-OR of 2N7002s (RTC INT via NPN inverter, `PWR_HOLD`, slide switch) | Same with AO3401A, plus wake button | AO3401A + AO3400A (concept) |
| Main 3.3 V | AP2112K-3.3 LDO | **TPS63802 buck-boost** (`C2845237`, 0.58 USD) | TPS63070 buck-boost (0.81 USD) |
| Modem rail | **TPS63020 buck-boost, 3.9 V** (`C15483`, 0.61 USD) for an **A7670G**; 3×22 µF + 470 µF + SMAJ5.0A; EN soft-start and power-good to the ESP32 | No modem | **Open (ADR-011)** |
| Battery measurement | 220k/100k divider on the raw battery | Divider on the switched rail | MAX17048 fuel gauge (1.51 USD) |

## 2. Assessment for Auris

**Worth adopting:**

1. **The Node v4 solar charger.** A linear charger like the BQ25185 turns the gap between panel voltage (~6 V) and battery voltage (~3.7 V) into heat: roughly 35–40 % of the panel's output. The CN3791 holds the panel at its maximum-power voltage and loses roughly 10–15 % in the buck stage. That is about a third more energy from the same panel (estimate; verify on the bench). Doc 19's ~4 W panel estimate should drop to roughly 3 W. Node v4 also adds the cold/hot interlock the Hub lacks, and a series diode so the battery does not leak back through the charger at night.
2. **The Hub v2 modem rail.** TPS63020 at 3.9 V with bulk capacitance and a TVS, already drawn, reviewed and bench-tested on an earlier hub ("Test 8") with the same A7670G. It is a ready answer to ADR-011.
3. **The Node v4 main 3.3 V buck-boost (TPS63802).** It holds 3.3 V down to an empty cell, unlike the Hub's LDO. It is cheaper than the TPS63070, which is designed for up to 16 V input and is more than a 1S battery needs.
4. **The keep-alive rail with a CR1220 on RTC VBAT.** Time survives a fully flat battery, which helps F4-04 (autonomous recovery). The TPL720F33 costs 0.09 USD.
5. **The wake latch.** It is the circuit Auris planned, with firmware that already does "hold before clearing the alarm flag".

**Must change for Auris:**

| Issue | Why it matters for Auris | Fix |
|---|---|---|
| Cold trip at +5 °C (reset +10 °C) | December daytime at 50–56°N is often below +5 °C, so charging would be blocked on most winter days and F4-01 (energy-neutral) would fail | Set the trip near 0–2 °C with the sensor coupled to the cells, and check the cells' charging range. The TMP390 thresholds are set by two resistors |
| No USB charging on either board | Auris plans USB-C charging. A 5 V USB input cannot share the CN3791: it sits below the 6 V MPPT setpoint, so the charger would deliver almost nothing | Either drop USB charging (service and programming only, as FieldMesh did) or add a small separate USB charger |
| Latch idle current ≈ 46 µA | The NPN inverter after the RTC INT has 100 kΩ pull-ups that conduct whenever the board is asleep | Raise those resistors to 1 MΩ: about 5 µA, with wake timing still in microseconds |
| Hub's battery divider on the raw battery | About 13 µA all the time | Put it on the switched rail as Node v4 does, or keep the MAX17048 |
| 1.1 A PPTC in series with everything | Modem current peaks pass through it and add voltage drop | Check drop and trip margin during the ADR-011 pulse test; a lower-peak LTE-only modem (section 3) reduces the issue |
| Two parts with low stock in Node v4 | 47 µH SRN5040TA (54 at LCSC), PMEG4010CEH (190) | Pick stocked equivalents before ordering |

**Sleep current correction.** The DS3231M takes up to **130 µA from VCC** in standby (datasheet ICCS max at 3.63 V). Its VBAT supply runs only the 1 Hz square wave, not alarm interrupts, so VCC must stay on the always-on rail. Realistic sleep current is therefore about 140–180 µA, not the ≤ 50 µA in doc 19. That is about 0.016 Wh/day, still inside the 1.0 Wh/day design load. Doc 19's energy table has been corrected.

**Cost.** Using the charger, rails and latch above costs about 3.2 USD at 100 units including the modem rail, against about 3.7 USD for today's plan without one (2.2 USD of that is the BQ25185, TPS63070 and TPS7A0230; 1.5 USD is the MAX17048). The case for switching is efficiency, the temperature interlock, a finished modem rail and shared FieldMesh design and firmware, more than the part cost.

**Evidence level.** These circuits are designed and reviewed, not field-proven. The CN3791 has not yet been measured on either board; both bring-up plans include the tests. Only the TPS63020 modem rail has a recorded bench pass.

## 3. Cheaper modem options

The A7670G (global, 12.30 USD) was chosen for band coverage (ADR-006). Most cheaper Cat-1 modules on LCSC (ML307, A7680C, EG800K-CN) are China-band parts without LTE band 20 (800 MHz), which carries much rural UK and Irish coverage; they are not options.

| Option | Part (LCSC) | USD @100 | Stock | Coverage | Trade-offs |
|---|---|---:|---:|---|---|
| Current choice | A7670G (`C5846957`) | 12.30 | 214 | GSM quad-band; LTE B1/2/3/4/5/7/8/12/13/18/19/20/25/26/28/66, TDD B38 | FieldMesh driver and modem rail already exist; low stock; GSM bursts need the biggest supply |
| Cheapest credible | Quectel EG800K-EU (`C44008839`) | **4.83** | 151 | LTE Cat-1 bis B1/3/5/7/8/20/28; no 2G; −35 to +75 °C | Saves 7.47 USD/unit. Europe only; new 17.7×15.8 mm footprint and Quectel AT driver; single antenna; lower peak current than a GSM-capable module |
| Same family, less work | SIMCom A7672E-LASE (`C6116733`) | 10.09 | 496 | Cat-1 bis; GSM 900/1800, LTE B1/3/5/7/8/20 | Same A7672X/A7670X 24×24 mm family as the A7670G (check pin-out against the series hardware design); saves 2.21 USD; Europe only |
| Lowest power | SIMCom SIM7022 (`C7363803`) | 5.45 | 1,822 | NB-IoT only | Runs straight from the battery (2.2–4.3 V); enough for 1 KB/day; NB-IoT availability and roaming vary by operator and must be checked per country |
| No modem per recorder | FieldMesh Hub v2 as a gateway over ESP-NOW | 0 per recorder | — | Hub's A7670G | Removes the modem, its supply and the SIM plan from every recorder. Recorders must be within radio range of a hub (forest range is short), and decision D5 assumes each recorder has its own LTE. A different architecture, best for clustered deployments |

Over a multi-year deployment the SIM plan can cost more than the module, which favours the gateway option where recorders are clustered.

## 4. Decisions this review feeds

| ADR | Question | Proposed |
|---|---|---|
| ADR-007 | Charger | Replace BQ25185 with the Node v4 CN3791 + TMP390A2 circuit, cold trip retuned to ~0–2 °C |
| ADR-008 | Main 3.3 V | TPS63802 instead of TPS63070 |
| ADR-010 | Always-on supply | TPL720F33 plus a CR1220 on RTC VBAT |
| ADR-011 | Modem supply | Hub v2 TPS63020 3.9 V rail |
| ADR-006 | Modem | Keep A7670G, or EG800K-EU for Europe-only builds, or a hub gateway for clustered sites |
| doc 19 / REC | USB charging | Drop (service only) or add a separate USB charger |

## 5. Decisions taken (owner, 2026-10-23)

| ADR | Decision |
|---|---|
| ADR-007 | Adopt the Node v4 CN3791 + TMP390A2 charger; retune the cold trip to about 0–2 °C |
| ADR-008 | TPS63802 for the main 3.3 V |
| ADR-010 | TPL720F33 keep-alive plus CR1220 on RTC VBAT |
| ADR-011 | Hub v2 TPS63020 3.9 V modem rail |
| ADR-006 | LTE only, no GSM fallback. Revised the same day: **EG800K-EU** for the prototype (Europe, Australia, New Zealand; 4.83 USD), A7670G kept as the global alternate |
| USB | Programming and service only; no USB charging. VBUS wakes the board |
| ADR-003 | FieldMesh wake latch with the inverter resistors raised to 1 MΩ (≈ 5 µA) |
| ADR-022 | Battery: the FieldMesh Node v4 pack (protected 1S2P 18650, ≈ 5200 mAh, ≥ 600 mA charge, ≥ 1.5 A discharge) |
| ADR-027 | Battery state from an ADC divider on the switched rail, as on Node v4; MAX17048 dropped |

The resulting power sheet is drawn to pin level in [`hardware/power/`](../hardware/power/README.md), with the cold trip at 0 °C.

