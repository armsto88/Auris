# Power sheet — schematic capture spec (prototype rev A)

**Baseline:** 2026-10-23. **Status:** **SELECTED IN CONCEPT** circuits, ready to capture in EasyEDA Pro. Nothing here has been built or measured on an Auris board. The circuits come from FieldMesh boards that are designed and reviewed but not field-proven; only the modem rail has a recorded bench pass (doc 20).

| File | Content |
|---|---|
| [`../auris-hardware-guide.html`](../auris-hardware-guide.html) | **Start here.** The *Power* tab has the block drawings, wire lists, sheet ports and parts list; the *RTC & wake* tab has the RTC and wake latch; the *Nets* tab checks a capture against this sheet and the audio sheet. Open it in a browser |
| `power-netlist.csv` | Every pin of every part and the net it connects to. The source of truth for connections. `NC` marks an unconnected pin, not a net |
| `power-bom.csv` | Grouped BOM with MPNs and LCSC codes for every line except the test pads |
| `../tools/build_guide.py` | Rebuild the guide after editing either CSV: `python3 hardware/tools/build_guide.py`. The build stops with an error if the netlist and BOM disagree, a designator is used on both sheets, or a sheet port is missing from the netlist |

**Sources.** FieldMesh repo `~/Documents/projects/Data-Logger-network---ESP32`: Node v4 prototype release 2026-10-22 (panel input, charger, temperature cut-out, battery input, keep-alive rail, battery sense) and Hub v2 r6 2026-10-10 (TPS63020 modem rail). The wake latch is common to both. Connections were taken from their pad-level EasyEDA netlists. Review and comparison: [`docs/20-FIELDMESH-POWER-AND-MODEM-REVIEW.md`](../../docs/20-FIELDMESH-POWER-AND-MODEM-REVIEW.md).

**Datasheets checked** (revision-pinned): Analog Devices DS3231M **19-5312 Rev 7** (Mar 2015), TI TMP390 **SBOS904A** (Aug 2020), TI TPS63802 **SLVSEU9D** (Jan 2021), TI TPS63020 **SLVS916I** (Oct 2019). CN3791, HT7533 and TPL720F33 values follow the FieldMesh design notes and were not re-checked against their datasheets here.

Designators run from 201 (audio uses 101–147). Shared nets with the audio sheet: `GND` and `VBAT_SW`.

## Block diagram

```mermaid
flowchart LR
  P1((J201 lid panel)) --> PIN
  P2((J202 cabled panel)) --> PIN[F201 + D201 TVS<br/>Q201 reverse-polarity FET]
  PIN -- SOLAR_IN --> CHG[U201 CN3791<br/>MPPT 6.05 V · 600 mA]
  PIN -- SOLAR_IN --> CUT[U202 HT7533 → U203 TMP390A2<br/>0 °C / +42 °C]
  CUT -. clamps MPPT .-> CHG
  CHG -- RAW_BAT --> BAT((J203 Node v4 pack<br/>1S2P 18650))
  BAT --> KA[U204 TPL720F33<br/>KEEP_ALIVE 3.3 V]
  KA --> RTC[U205 DS3231MZ<br/>+ CR1220]
  RTC -- INT --> LATCH[Wake latch<br/>Q206 · Q207–Q209]
  BTN[SW201 / VBUS / PWR_HOLD] --> LATCH
  LATCH -- SYS_GATE --> SW[Q210 AO3401A]
  BAT --> SW
  SW -- VBAT_SW --> R3[U206 TPS63802<br/>3V3]
  SW -- VBAT_SW --> RM[U207 TPS63020<br/>VMODEM 3.9 V · EN = MODEM_EN]
  SW -- VBAT_SW --> AUD[audio sheet<br/>TPS7A2033]
  SW -- VBAT_SW --> BS[R216/R217 → BATT_ADC]
```

## Design decisions

| # | Decision | Source and rationale |
|---|---|---|
| P1 | **CN3791 buck MPPT charger**, 600 mA, series Schottky against night back-feed | Node v4. Holds the panel at its maximum-power voltage; roughly a third more energy than a linear charger from the same panel (estimate, doc 20). ADR-007 |
| P2 | **TMP390A2 cut-out clamps the MPPT pin**; cold trip **0 °C** (FieldMesh: +5 °C) | Li-ion must not charge below 0 °C, but +5 °C would block most December charging at 50–56°N (F4-01). Panel-powered, so it costs nothing at night |
| P3 | **Two panel inputs in parallel**, no USB charging | Integrated and cabled panels both supported (ADR-022). A 5 V USB input sits below the 6 V MPPT point and cannot share the CN3791. USB is service only and wakes the board |
| P4 | **FieldMesh Node v4 battery pack** (protected 1S2P 18650, ≈ 5200 mAh, ≥ 600 mA charge, ≥ 1.5 A discharge) on a keyed JST PH | Owner decision 2026-10-23 (ADR-022); shared supply and harness with FieldMesh |
| P5 | **TPL720F33 keep-alive** for the RTC and latch only; **CR1220** on RTC VBAT | Node v4 / Hub v2. 1.4 µA quiescent; time survives a flat battery (F4-04). ADR-010 |
| P6 | **FieldMesh wake latch** with the RTC-inverter resistors raised from 100 kΩ to **1 MΩ** | ≈ 5 µA instead of ≈ 46 µA idle. Wake sources wired-OR: RTC alarm, PWR_HOLD, VBUS (new), button. ADR-003 |
| P7 | **TPS63802 main 3.3 V**, power-save mode, always on while awake | Node v4. Holds 3.3 V down to an empty cell. ADR-008 |
| P8 | **TPS63020 3.9 V modem rail**, forced PWM, EN and PG to the MCU, 470 µF bulk and SMAJ5.0A, for the **EG800K-EU** (3.4–4.3 V, LTE only) | Hub v2 r6, bench-tested there with an A7670G. ADR-011. The EG800K-EU (ADR-006) has no 2G, so no 2 A GSM bursts. The bulk capacitance may be more than it needs; keep it for the prototype |
| P9 | **Battery state from an ADC divider on VBAT_SW**; no fuel gauge. A second divider reads the panel | Node v4. No sleep drain; saves the MAX17048 (1.51 USD). ADR-027 |

## Calculations

| Item | Formula | Result |
|---|---|---|
| MPPT set point | 1.205 V × (1 + R204/R205) = 1.205 × (1 + 402k/100k) | **6.05 V**, for the Node v4 panel |
| MPPT for another panel | R204 = R205 × (Vmp / 1.205 V − 1), R205 = 100 kΩ | e.g. Vmp 5.5 V → 356 kΩ (use 357 kΩ) |
| Charge current | 120 mV / R202 = 0.12 / 0.200 | **600 mA**; R202 dissipates 72 mW |
| Cut-out, hot | R208 = 2.49 kΩ (TMP390 table 7-1) | trips **+42 °C**, resets +37 °C |
| Cut-out, cold | R209 = 21.5 kΩ, 5 °C hysteresis column (table 7-2) | trips **0 °C**, resets +5 °C |
| Main 3.3 V | 0.5 V × (1 + 511k/91k) | **3.31 V** |
| Modem rail | 0.5 V × (1 + 680k/100k) | **3.90 V** |
| Battery sense | R217 / (R216 + R217) = 100k / 320k | × 0.3125: 3.0 V → 0.94 V, 4.2 V → 1.31 V. 13 µA while awake, none asleep |
| Panel sense | R239 / (R238 + R239) = 150k / 1150k | × 0.130: 7 V → 0.91 V; 3.1 V ADC full scale ≈ 23.8 V. ≈ 5 µA from the panel only |
| Latch idle | (3.3 − 0.65) V / (R219 + R222) + 3.3 V / R223 | 1.3 µA + 3.3 µA ≈ **5 µA** |

## Sleep current (battery, board asleep)

| Load | Current | Basis |
|---|---:|---|
| DS3231M standby (VCC) | ≤ 130 µA | Datasheet max at 3.63 V; typical not given |
| Wake latch | ≈ 5 µA | Calculated above |
| Q205 gate divider (R215 + R214, 1.1 MΩ) | ≈ 4 µA | Always across the battery |
| TPL720F33 quiescent | 1.4 µA | FieldMesh notes |
| Q210 off-state, D203 reverse leakage | not known | Measure; D203 was chosen for low leakage |
| **Total** | **≈ 140 µA, ≤ 0.013 Wh/day at 3.7 V** | Inside the ≤ 200 µA / 0.02 Wh/day line in doc 19. The pack's own protection circuit adds a few µA |

## Bring-up tests (rev A board)

Use a current-limited bench supply in place of the battery (3.7 V, 200 mA limit) and a second one, or a panel, on J202.

1. **Sleep:** battery only, SW202 on. Expect KEEP_ALIVE 3.3 V, VBAT_SW off, SYS_GATE at RAW_BAT and ≤ 150 µA total.
2. **Button and ship mode:** SW201 turns VBAT_SW and 3V3 on while held. With SW202 off, nothing turns the board on and the RTC keeps time.
3. **RTC wake:** with firmware, set alarm 1 a minute ahead and power down: the board must wake, assert PWR_HOLD, then clear the flag. Repeat with alarms 1 and 2 together and with PWR_HOLD late (RTC tab, gate G1).
4. **USB wake:** VBUS on wakes the board; VBUS off with PWR_HOLD low turns it off. The battery current must not change with VBUS present (no charging path).
5. **Charger:** supply J202 through a series resistor to imitate a panel. Check MPPT holds 6.05 V, 600 mA flows into a 3.7 V load, LED201 lights, and LED202 lights at 4.2 V. With the panel removed, measure battery current back into the charger.
6. **Cut-out:** cool U203 with freeze spray and warm it with a heat gun, thermocouple on U203. Charging must stop at 0 °C and +42 °C and restart at +5 °C and +37 °C.
7. **Reverse panel:** a reversed panel input must draw no current and warm nothing.
8. **Rails:** 3V3 ripple and droop during ESP32 Wi-Fi transmit at 3.0 V battery. MODEM_PG rises within milliseconds of MODEM_EN.
9. **Modem load (ADR-011):** with the EG800K-EU transmitting at full power (weak signal or attenuator) for a whole session at 3.0 V battery, at room temperature, −10 °C and +50 °C. Record VMODEM droop, battery current, and the drop and temperature of F202. Without a module, use a 0.7 A load step on VMODEM.
10. **ADC calibration:** BATT_ADC and SOLAR_ADC against a meter at 3.0, 3.7 and 4.2 V; store the correction per unit.

## Open items

| Item | Detail | Next step |
|---|---|---|
| VMODEM TVS | Quectel recommends VRWM 4.7 V at the module supply; D205 is an SMAJ5.0A (VRWM 5.0 V) from Hub v2 | See `hardware/lte/README.md` open item 3 |
| Battery fuse margin during LTE | No GSM (EG800K-EU, 2026-10-23), so no 2 A bursts. LTE at full power drew 0.51–0.64 A on the A7670G (hardware design V1.00); the EG800K-EU should be similar, to be confirmed from its hardware design manual. That is about 0.9 A from a 3.0 V cell after the boost, about 1 A with the MCU awake. That is inside the JST PH (2 A) and pack (1.5 A) ratings but close to F202's 1.1 A hold current, which drops further when warm | Test 9. If F202 heats or trips, fit a 1.5 A hold PPTC in the same 1812 footprint |
| PMEG4010CEH stock | 190 at LCSC on 2026-10-23 (D203, D204) | Order early, or use SL14PL-TP (`C725469`, 6710 in stock; higher leakage) |
| MPPT divider | Set for the Node v4 panel | Recalculate R204 once the Auris panel is chosen (ADR-022) |
| Harvest measurement | No charge-current sense, and J201/J202 cannot be told apart. F6-01 now reports panel voltage and the daily battery change as a proxy | Add a current monitor in rev B if a real harvested-Wh figure is needed |
| Reversed battery with a live panel | Q205 blocks a reversed pack only while the panel is dark (FieldMesh accepted this) | Keyed connector; polarity check on every battery batch |
| L201 rating | 22 µH from Hub v2 (Node v4's 47 µH part has 54 in stock) | Confirm saturation current covers 600 mA plus ripple, and charger efficiency, on the bench |
| No charge timer | CN3791 has none and no power path; an awake recorder delays termination | Check termination with a recording load in test 5 |
| GPIO numbers | GPIO1/2 ADC, GPIO10 PWR_HOLD, GPIO11/12 modem EN/PG, GPIO13/14 system I²C are proposals | Confirm in the pin map (H0-06) |
