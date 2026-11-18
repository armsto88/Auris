# 04 — Hardware V1 engineering definition

**Maturity:** Schematic captured for all four sheets and reviewed against manufacturer datasheets (2026-11-17, `hardware/review/2026-11-17-schematic-review.md`); not demonstrated in a fabricated Auris device.

## 1. Compute and radio

**SELECTED concept:** `ESP32-S3-WROOM-1-N16R8` (`LCSC C2913202`) with 16 MB flash, 8 MB Octal PSRAM and 2.4 GHz Wi-Fi + Bluetooth LE. The MCU provides I²S, I²C, UART, native USB and SD/MMC host options. In Espressif datasheet v1.8, the N16R8 module's specified ambient temperature range is **−40 to +65 °C** (different from non-R8 variants); thermal and deployment envelope require explicit review. Espressif's `-1U` is a different **external-antenna** variant, not the selected `-1` PCB-antenna variant.

**Electrical constraints:** 3.0–3.6 V MCU supply per module datasheet; verify rail ramp, PSRAM power, boot strapping pins, flash programming, RF antenna keepout and PCB copper guidelines. Do not count all nominal GPIO as unconstrained general-purpose pins.

## 2. RTC and wake/latch

**SELECTED concept** (revised 2026-10-22, ADR-002): `DS3231MZ+TRL` (`C107410`), MEMS ±5 ppm, −40…+85 °C, two time-of-day alarms. **Alarm 1** = dynamic one-shot job alarm rewritten by the MCU each power-down; **Alarm 2** = standing wall-clock-aligned sync window (masked minute+hour match, UTC). Shared active-low open-drain INT on the INT/SQW pin; A1F/A2F flags identify the wake reason. Previous candidate RV-3129-C3 retained as fallback for hypothetical nanoamp SKUs — see [`adrs/ADR-002-rtc-selection.md`](adrs/ADR-002-rtc-selection.md).

- RTC VBAT backup rail stays powered when switched 3.3 V core is off; VBAT range 2.3–5.5 V.
- Always-on supply **SELECTED concept** (2026-10-23, ADR-010): TPL720F33 3.3 V keep-alive LDO (1.4 µA Iq) feeding DS3231 VCC and the wake latch, plus a CR1220 on DS3231 VBAT, as on FieldMesh Hub v2 / Node v4. Verify reverse current with main 3.3 V off. The DS3231M takes up to 130 µA from VCC in standby, so it dominates sleep current.
- Wake conditions: RTC INT (either alarm), field button, USB presence. MCU must assert `PWR_HOLD` before clearing alarm flags.
- Firmware must set `INTCN=1` (alarm interrupt mode) and `BBSQW=0` at every boot; verify INT/SQW never outputs a square wave while the latch is armed.
- `RST` pin has an integrated pushbutton debounce (PBDB ≈ 250 ms) — candidate debounce for the field service button; still requires its own wake-path test, not assumed.
- Clear alarm flags only after hold asserted, check stuck-low INT and power-down race; measure wake current through all paths.
- **DS3231 VBAT INT caveat:** with `BBSQW=0`, INT/SQW goes high-impedance if VCC drops below VPF — alarm INT is not specified while running on VBAT with VCC dead. In this topology RTC VCC comes from the always-on LDO, so this only occurs at total battery exhaustion; still bench-verify INT assertion with main 3.3 V off, and pin state during battery brownout near VPF (ADR-002).
- Failures to test: brownout, abrupt USB removal, failed SD close, firmware crash, spurious RTC wakes, RTC backup cold-start, A1/A2 interaction.

## 3. Analogue audio

**CANDIDATE:** Primo EM273 **or equivalent** electret microphone (working external price allowance $25), `PCM1863DBT` (`C1520794`) 24-bit I²S audio ADC, `TPS7A2033PDBVR` audio low-noise LDO. Choose front-end bias/gain/filtering and microphone protection only after sample bench tests. The July document found **1 unit of PCM1863 stock**, so supply risk is significant and an alternate ADC must be researched. ADC resolution does not establish actual noise floor, usable dynamic range or calibration quality.

Measure: absolute sensitivity, self-noise, saturation and clipping at intended sound pressures, 1 kHz calibration reference, frequency sweep, wind/water protective interface, supply noise and RF/SD EMI. Separate microphone ground/current return and high di/dt loop paths.

**Scope caution:** Any claim of ultrasound/bat coverage needs demonstrated microphone response, analogue bandwidth, ADC sample-rate selection, anti-aliasing, DSP, file throughput and energy budget. Not selected today.

## 4. Energy subsystem

| Function | Current part/topology | Status | Mandatory decision |
|---|---|---|---|
| Cell | FieldMesh Node v4 pack: protected 1S2P 18650, ≈ 5200 mAh, ≥ 600 mA charge, ≥ 1.5 A discharge, JST PH lead | SELECTED concept (2026-10-23, ADR-022) | Pack supply and protection limits; keyed connector, polarity check per batch |
| Solar charger | `CN3791` `C154992` + `TMP390A2` `C5219772` cut-out (FieldMesh Node v4 circuit) | SELECTED concept (2026-10-23, ADR-007) | Set MPPT divider from the real panel (6 V-class panels only); cold trip +5 °C (R209 18.7 kΩ, owner decision 2026-11-17); L201 47 µH; night leakage; no USB charging |
| Main regulated rail | `TPS63802DLAR` `C2845237` (3.3 V buck-boost, Node v4) | SELECTED concept (2026-10-23, ADR-008) | Efficiency, Wi-Fi load transients at low cell voltage, sleep-path backfeed |
| Audio supply | `TPS7A2033PDBVR` `C2862740` | CANDIDATE | PSRR/noise under worst LTE/DC-DC scenarios |
| Battery state | 220 kΩ/100 kΩ divider on `VBAT_SW` → ESP32-S3 ADC1; `MAX17048G+T10` dropped | SELECTED concept (2026-10-23, ADR-027) | ADC calibration per unit; voltage-to-charge table for the pack |
| Main load switch | `AO3401A` `C15127` high-side PFET + FieldMesh wake latch: `MMBT3904` inverter, 3 × `2N7002` (`C8545`) wired-OR, 1 MΩ resistors | SELECTED concept (2026-10-23, ADR-003) | Startup and hold transient, gate protection, safe off-state, latch current ≈ 5 µA |
| Always-on RTC supply | `TPL720F33-3TR` `C2842389` 3.3 V + CR1220 on RTC VBAT | SELECTED concept (2026-10-23, ADR-010) | Reverse current; total sleep current |
| Modem supply | `TPS63020DSJR` `C15483`, 3.9 V from the switched rail (Hub v2) | SELECTED concept (2026-10-23, ADR-011) | Pulse testing across full cell voltage/temp/radio load, including the battery fuse drop |

**Pin-level design:** [`hardware/power/`](../hardware/power/README.md) has the netlist, BOM, calculations and bring-up tests for all of the above, adapted from FieldMesh Node v4 and Hub v2 r6.

**Gate:** Do not complete schematic until **power tree, UVLO, charge-path and latch circuits** are reviewed as an integrated system. A solar panel cannot be sized from nominal wattage without energy balance and worst-case irradiance assumptions.

## 5. Cellular

**SELECTED concept** (owner decision 2026-10-23, ADR-006): Quectel `EG800K-EU` (`EG800KEULC-I03-SNNSA`, `C44008839`), LTE Cat-1 bis, LTE-FDD B1/3/5/7/8/20/28, no 2G, CE and RCM approved: Europe, Australia and New Zealand. LGA-109, 17.7 × 15.8 × 2.4 mm (half the area of the A7670G), supply 3.4–4.3 V, −35 to +75 °C. It replaced the `A7670G` (`C5846957`) on cost (4.83 vs 12.30 USD @100) once GSM was ruled out; the A7670G remains the global alternate, and the `EG800K-LA` (Americas bands) fits the same footprint. The pin-level sheet is in [`hardware/lte/`](../hardware/lte/README.md): 1.8 V UART with RTS/CTS and STATUS through a TXS0108E level shifter, open-collector PWRKEY, Quectel SIM and VBAT networks, π match to a U.FL. It was drawn from the EG800K-LA hardware design (same series and package); confirm the pin table against the EU manual. Quectel recommends a PCB of at least four layers. Operator acceptance (e.g. Telstra in Australia) and SIM plan per country still required. Nano-SIM (`SNO-1303-C` `C428450`) and LTE FPC antenna (`TX4G-FPC-8121` `C454897`) also candidates; Cat-1 bis uses one antenna. RF matching/ESD/protection, coax routing, antenna enclosure interaction and modem thermal/power dissipation remain design tasks.

GNSS is **optional** in the figure and has no selected GNSS device/antenna path.

## 6. USB, storage and I/O

- USB-C receptacle candidate `HC-TYPE-C-16P-01A` `C2894897` for programming and service only; it does not charge the battery (2026-10-23). 5.1 kΩ CC pull-downs; USB ESD on D+/D−/CC (SRV05-4 with its VBUS reference left open, 2026-11-17 review) and a separate VBUS ESD diode; VBUS wakes the board through the latch but does not power it; shell to GND.
- microSD push-push holder candidate `TF PUSH` `C393941`. Bus: SD mode 1-bit on GPIO47 (CLK, 33 Ω series), 48 (CMD), 44 (D0), card power enable on GPIO45 with a pull-down (ADR-012, 2026-10-23); card detect on GPIO3 (owner decision 2026-11-17).
- Prefer switchable/resettable microSD supply and buffered writes; validate operation when a card is absent, full, slow, removed mid-write or corrupted.
- Provision clear test pads for power rails, PWR_HOLD, RTC INT, I²C, I²S, modem UART/status and USB.
- Reserve debug/log/service access without forcing destructive enclosure opening in routine field recovery, subject to ingress engineering.

## 7. PCB and enclosure integration (proposals)

- Keep analogue microphone, ADC reference and input traces away from the LTE antenna/feed, buck-boost switching loops, SD buses and high-current charge paths.
- Contain current-loop area, use ground strategy driven by return paths, appropriate RF keep-outs, short decoupling loops, ESD at externally exposed connectors.
- Wind/rain acoustics: controlled acoustic opening, replaceable membrane/windscreen, drift-test after wet/dust exposure; prevent acoustic port from becoming an ingress short circuit.
- Mechanical: enclosure IP and mounting target **TBD**, battery and panel replacement approach **TBD**, anti-condensation/desiccant strategy **TBD**.
- Prototype PCB with explicit option footprints for ADC clock, modem power topology, audio gain/filter and measurement shunts where space allows.

## 8. Required schematic review checklist

- [ ] Manufacturer datasheets revision-pinned for **every** selected/candidate IC.
- [ ] RTC backup voltage valid when core off and during USB insertion.
- [ ] Logic levels from always-on RTC to unpowered MCU cannot back-power rails.
- [ ] Charger input protections, NTC limits, status/power-path behaviour under solar and USB.
- [ ] MCU rail and LTE supply survive worst-case current pulses and cell sag.
- [ ] All start/stop races simulated or prototyped; watchdog fallback defined.
- [ ] I²S clock and sample-rate accuracy verified; anti-aliasing present.
- [ ] SD reset/isolation, bus pins and removable-card mechanics verified.
- [ ] RF antenna and PCB antenna clearances supported by final enclosure.
- [ ] Calibration, manufacturing test, serial number and production programming access designed in.
- [ ] Total system thermal envelope and battery safety documented.

**Source:** original hardware document in `references/`; Espressif module datasheet cited in `17-SOURCES-AND-REFERENCES.md`.

## Later component/source clarifications (from project discussion)

- **Audio ADC ordering alternative:** The later discussion identified **PCM1863DBTR / LCSC C529569** as the alternate ordering/package suffix to the draft's PCM1863DBT / C1520794. The converter family remains a **candidate pending sourcing, schematic, and audio tests**; this is not a verified pin-by-pin substitution or current stock assertion.
- **Main-board reuse and acoustic-head variants:** Retain the option of an audible-band acoustic head for V1 and a separately engineered ultrasonic front end for a later bat-oriented variant. An ESP32-S3 plus PCM1863/electret audible design cannot be presented as a proven ultrasonic solution.
- **Fixed site position:** Prefer mobile-phone location captured at BLE setup; GNSS is not a core fixed-site requirement.

## Schematic review 2026-11-17

All four sheets were reviewed against manufacturer datasheets and re-captured: [`hardware/review/2026-11-17-schematic-review.md`](../hardware/review/2026-11-17-schematic-review.md). Per-part datasheet notes are in [`hardware/datasheets/`](../hardware/datasheets/README.md). Open hardware decisions from it: modem procurement, the N16R8's +65 °C rating (PSRAM ECC or another module variant), microSD ESD, extra test pads and the CR1220 cell part.
