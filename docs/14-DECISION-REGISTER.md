# 14 — Architecture decision register (ADR index)

The table explicitly separates current selections from **recommendations** and decisions that still require owner/test/date. Proposals below are **not** silently promoted to approved engineering decisions.

| ID | Decision topic | Present status, 2026-10-22 | Evidence or next action |
|---|---|---|---|
| ADR-001 | Main MCU | **SELECTED IN CONCEPT**: ESP32-S3-WROOM-1-N16R8 | Source hardware draft; confirm supply/temp/pin budgets |
| ADR-002 | RTC | **SELECTED IN CONCEPT** (revised 2026-10-22): DS3231MZ+TRL (`C107410`); was RV-3129-C3 | Two independent alarms (one-shot + standing UTC window) for the dual wake tasks; full ADR in [`adrs/ADR-002-rtc-selection.md`](adrs/ADR-002-rtc-selection.md); verify `INTCN=1`, INT-on-VBAT latch bench |
| ADR-003 | Normal power regime | **CURRENT DESIGN INTENT**: externally switched-off main domains; RTC alive. **SELECTED IN CONCEPT** (owner decision 2026-10-23): FieldMesh wake latch (RTC INT via NPN inverter, `PWR_HOLD`, wake button, slide-switch ship mode) with the inverter resistors raised to 1 MΩ (≈ 5 µA instead of ≈ 46 µA) and USB VBUS added as a wake source; drawn in `hardware/power/` | Power latch bench; safe file close; realistic energy budget |
| ADR-004 | Microphone | **CANDIDATE**: Primo EM272Z1 (2-wire) or EM273 (3-wire, wired as 2-wire); prototype connector takes either | EM272 specified at 5 V / 3.9 kΩ; prototype biases at 3.3 V / 2.7 kΩ — measure sensitivity and headroom on capsule samples (`hardware/audio-frontend/`) |
| ADR-005 | Audio converter | **CANDIDATE**: PCM1863DBT or same-silicon DBTR; footprint-compatible PCM1862 as fallback. **PROPOSED** (2026-10-23): ADC is I²S master from a 24.576 MHz crystal, replacing the BCK-PLL preference | ESP32-S3 has no audio PLL; master mode keeps the PGA DSP clocked. Noise/clock tests and actual availability still required |
| ADR-006 | Cellular device | **SELECTED IN CONCEPT** (owner decision 2026-10-23, revised the same day): Quectel **EG800K-EU** LTE Cat-1 bis (`C44008839`, 4.83 USD @100), LTE-FDD B1/3/5/7/8/20/28 with CE and RCM approval for **Europe, Australia and New Zealand**; LTE only, no 2G. Replaces the A7670G (`C5846957`, 12.30 USD), which stays as the **ALTERNATE** for global builds. The EG800K-LA (Americas bands, FCC) uses the same footprint | 151 in stock on 2026-10-23: buy prototype quantity early. LGA-109 package needs reflow or JLC assembly. New Quectel AT driver (FieldMesh has only an A7670G driver). Sheet drawn in `hardware/lte/` (2026-10-23) from the EG800K-LA hardware design V1.0.0: confirm the pin table against the EU manual; full-power TX current still unmeasured; check operator acceptance per country (e.g. Telstra in Australia); SIM/RF, antenna and current tests (ADR-011) still open |
| ADR-007 | Charger/power path | **SELECTED IN CONCEPT** (owner decision 2026-10-23, doc 20): FieldMesh Node v4 circuit, CN3791 buck solar charger (`C154992`) with TMP390A2 hot/cold cut-out (`C5219772`); replaces BQ25185. USB does not charge the battery | Cold trip set to 0 °C, resetting at +5 °C (R209 21.5 kΩ; schematic in `hardware/power/`); set MPPT divider from the real panel's Vmp; bench harvest, night leakage and termination with the recorder awake |
| ADR-008 | Main switched 3.3 V | **SELECTED IN CONCEPT** (owner decision 2026-10-23, doc 20): TPS63802DLAR (`C2845237`), Node v4 rail; replaces TPS63070 | Transient and efficiency check with ESP32-S3 Wi-Fi peaks at low cell voltage |
| ADR-009 | Audio 3.3 V clean rail | **CANDIDATE**: TPS7A2033PDBVR, fed from switched battery rail, EN from MCU (audio powered only while recording) | Regulates down to VBAT ≈ 3.32 V at ~30 mA; PSRR/load/analog noise tests |
| ADR-010 | Always-on supply | **SELECTED IN CONCEPT** (owner decision 2026-10-23, doc 20): TPL720F33-3TR 3.3 V keep-alive (`C2842389`, 1.4 µA Iq) plus CR1220 on DS3231 VBAT (`C70381`), as on Hub v2 and Node v4 | Measure total sleep current (DS3231M up to 130 µA on VCC); wake-latch inverter resistors are 1 MΩ (ADR-003) |
| ADR-011 | Modem supply | **SELECTED IN CONCEPT** (owner decision 2026-10-23, doc 20): Hub v2 rail, TPS63020DSJR (`C15483`) at 3.9 V from the switched rail, 3×22 µF + 470 µF, SMAJ5.0A, EN soft-start, power-good to MCU | Still pulse-test at low cell voltage and cold, including drop across the 1.1 A battery fuse (R02) |
| ADR-012 | microSD interface | **SELECTED IN CONCEPT** (owner decision 2026-10-23): SD mode 1-bit on GPIO47 (CLK), 48 (CMD), 44 (D0); card power enable on GPIO45 with pull-down; status LED on GPIO43. Pins freed by giving up the UART0 console (programming, console and debug over USB-Serial-JTAG on GPIO19/20); modem flow control, power-good and audio options kept; GPIO3 spare | ~1–2 MB/s vs 96 KB/s needed. Prove sustained writes, worst-case card write latency against the PSRAM buffer, power-cycle recovery and no back-powering of the switched-off card. Card power switch part still open |
| ADR-013 | Primary acoustic band | **CURRENT DESIGN INTENT** (owner decision 2026-10-23): audible band, 48 kHz mono; ultrasound needs separate proof | DRM-1 in `19-V1-FUNCTIONAL-REQUIREMENTS.md`; mic/ADC enclosure and bandwidth test still required |
| ADR-014 | Recording format | **CURRENT DESIGN INTENT** (owner decision 2026-10-23): 16-bit PCM WAV with GUANO metadata; factory-set gain plus "loud site" preset | Card capacity sets the service interval (128 GB ≈ 150 days); compression may be revisited later |
| ADR-015 | Device setup | **CURRENT DESIGN INTENT** (owner decision 2026-10-23, supersedes BLE): cloud web app with config over LTE; device Wi-Fi hotspot page for sites without coverage; no BLE in V1 | F5/F6 in `19-V1-FUNCTIONAL-REQUIREMENTS.md`; hotspot authentication and Wi-Fi/audio coexistence tests |
| ADR-016 | Backend technology | **OPEN**; no binding cloud/platform choice | Evaluate low-ops, cost, identity, access and data custody |
| ADR-017 | Edge inference | **PROPOSED**: optional narrow TFLite Micro-style model after record; platform feasibility research (OpenELAB ESP32-S3 TinyML survey, 2026-10-22) summarised in `08-EDGE-AI-AND-MODELS.md` | Quantisation/operator/memory/energy benchmarks on actual N16R8 module still open |
| ADR-018 | Detector Builder | **FUTURE** project-trained, not a V1 blocker | Labelled-data and independent field validation workflow |
| ADR-019 | Calibration/noise | **REQUIRED CAPABILITY** if providing noise values; no IEC compliance claim | Define reference, uncertainty, verification and reports |
| ADR-020 | Enclosure | **OPEN**: UV-resistant plastic, IP66/67 aspirational, downward protected acoustic port | Build/test fully assembled enclosure incl. membrane |
| ADR-021 | Business model / price | **OPEN**: optional hardware + service tiers | Interviews/COGS/willingness-to-pay, no fixed prices |
| ADR-022 | Solar panel/battery size | **REQUIRED CAPABILITY** (owner decision 2026-10-23): energy-neutral at 50–56°N in December; integrated and cabled panel both supported. Sizing **CANDIDATE**: ~4 W panel (≈ 3 W expected with the CN3791, ADR-007). Battery **SELECTED IN CONCEPT** (owner decision 2026-10-23): the FieldMesh Node v4 pack, protected 1S2P 18650, ≈ 5200 mAh, ≥ 600 mA charge, ≥ 1.5 A discharge, JST PH lead | Replace estimates in `19-V1-FUNCTIONAL-REQUIREMENTS.md` with measured load and harvest; PVGIS check per site |
| ADR-023 | Wi-Fi/GNSS/camera | **OPTIONAL / FUTURE** | Do not allocate irrevocable V1 cost unless justified |
| ADR-024 | Data ownership and retention | **REQUIREMENT / OPEN POLICY**: preserve evidence, project-defined deletion | Privacy review, audits, offline availability and fail-safe defaults |
| ADR-025 | V1 reference mission and scope | **CURRENT DESIGN INTENT** (owner decision 2026-10-23): DRM-1 long-term biodiversity survey; runs until SD full; V1 LTE = daily heartbeat + remote config + clock sync, no audio upload | `19-V1-FUNCTIONAL-REQUIREMENTS.md`; puts LTE (ADR-006) and solar charging (ADR-007) on the V1 critical path |
| ADR-026 | Audio front-end topology | **PROPOSED** (2026-10-23, prototype rev A): pseudo-differential direct path and OPA1662 +12 dB preamp path on one board, chosen by the PCM1863 input mux over I²C; both recordable at once for A/B. Filtering is layered: switched analog high-pass (≈100 Hz default, 36 Hz wide, 1 kHz) on the preamp path via PCM1863 GPIOs, ADC fixed at 48 kHz, all other filters digital in firmware | Spec in `hardware/audio-frontend/`; pick one path for V1 from G2 noise measurements; wind test decides if a 2nd-order analog stage is needed |
| ADR-027 | Battery state measurement | **SELECTED IN CONCEPT** (owner decision 2026-10-23): 220 kΩ/100 kΩ divider on `VBAT_SW` into ESP32-S3 ADC1 (`BATT_ADC`), as on FieldMesh Node v4; replaces the MAX17048 fuel gauge. A second divider reads the panel voltage (`SOLAR_ADC`) | Calibrate the ADC per unit; build a rest-voltage-to-charge table for the pack; read before the modem turns on; heartbeat reports volts as well as an estimated % |

## Recording an actual decision

Create `docs/adrs/ADR-NNN-short-name.md` with:

```
Status: Proposed | Accepted | Superseded | Rejected
Date: YYYY-MM-DD
Owner/reviewers: ...
Context and measurable requirements: ...
Options considered with costs/risks: ...
Decision and rationale: ...
Tests/supplier datasheet revisions: ...
Consequences and rollback plan: ...
Supersedes / superseded by: ...
```

Update this index, affected requirements, schematic pin map and BOM in the **same change**. No one should infer a selection merely because a candidate appears in a diagram or sample JSON.
