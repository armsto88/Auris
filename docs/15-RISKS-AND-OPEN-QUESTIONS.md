# 15 — Risk register, unknowns and unresolved scope

Scores are deliberately omitted: there is no quantified failure probability or engineering test dataset yet. Priorities reflect impact on a first usable recorder, not a completed FMEA.

| ID | Priority | Failure / uncertainty | Consequence | Mitigation & closure evidence |
|---|---|---|---|---|
| R01 | P0 | RTC INT/latch/back-power error | Cannot wake or stuck on; loss of stored recordings | Integrated power test, unpowered I/O leakage tests, watchdog recovery; DS3231 `BBSQW=0`/VPF INT high-impedance corner case and A1/A2 coexistence bench (ADR-002) |
| R02 | P0 | Modem TX brownout | Reboots, SD corruption, lost sync/data | Low-cell worst-signal current waveforms, regulator/load-switch design. GSM disabled 2026-10-23 (LTE only), which removes the ≈ 3 A battery-side bursts. LTE at full power is ≈ 0.65 A at the modem (A7670G figure; confirm for the EG800K-EU), ≈ 1 A from a 3.0 V cell with the MCU awake: inside the connector and pack ratings but close to the 1.1 A battery fuse's hold current when warm. Pulse-test (`hardware/power/README.md`, test 9) |
| R03 | P0 | Solar source collapse or unsafe charge behaviour | Battery depletion, thermal/battery hazard | Real panel sweep at the CN3791 MPPT setpoint, TMP390A2 cut-out trip test, pack protection qualification |
| R04 | P0 | SD long writes/power-down race | Silent missing/invalid WAV and metadata | Buffered I/O, commit/checksum, fault injection and endurance tests |
| R05 | P0 | Acoustic front-end EMI/self-noise | False measurements and poor detector recall | Reference spectra, RF isolation, fully assembled enclosure tests |
| R06 | P0 | Incorrect time, clock drift or gaps | Invalid deployment chronology and comparisons | UTC quality flags, RTC sync events, actual sample count, error budgets |
| R07 | P0 | Unauthorised config/OTA or recorded-person privacy | Compromised devices/data, legal exposure | Secure bootstrap, authenticated local/remote operation, privacy review |
| R08 | P1 | Mic membrane/port blocks or changes response | Systematic drift and missed targets | Weather/rain/wind tests, replacement/calibration process |
| R09 | P1 | ESP32-S3 PSRAM/temp/pin constraints | Firmware instability/out-of-spec use | Confirm module variant spec, pin map, temp and memory stress |
| R10 | P1 | ADC/microphone supply chain | Redesign, BOM volatility | Second-source risk assessment, test validated candidate alternatives |
| R11 | P1 | LTE operator/region incompatibility | Remote units unreachable | Modem band & SIM plan by target country, RF field trials |
| R12 | P1 | Network/AI filter causes data selection bias | Unscientific inference/false negative blind spots | Retain controls and uncertain examples; evaluate against raw audio |
| R13 | P1 | Very large raw-audio bandwidth/storage | High ongoing costs or loss-by-policy | Selective uploads, manifest, retention audits and per-project quotas |
| R14 | P1 | Unsupported acoustic calibration claim | Misleading clients / regulatory exposure | Define calibrated vs indicative outputs, field references and IEC pathway |
| R15 | P2 | Cloud vendor lock-in / services cost | Commercial margin, portability issues | Versioned schema, object-storage abstraction, measured COGS |
| R16 | P2 | Overly broad initial feature scope | No reliable deliverable | Gate-based roadmap; audible recorder MVP before user training/ultrasound |
| R17 | P2 | Physical theft/tampering or SD removal | Evidence loss and privacy risk | Lockable enclosure, mounting options, device ownership and retention policy |
| R18 | P2 | Unproven pricing demand | Unsustainable product direction | Interviews, pilot comparisons and actual unit economics |
| R19 | P1 | No 2G fallback (LTE-only EG800K-EU, 2026-10-23) | Sites with 2G-only coverage get no heartbeat, config or clock sync | Check LTE coverage (band 20 in rural Europe) before deployment; hotspot page and service-visit clock offset (F2-03) cover sites without LTE |

## Architecture blockers needing explicit decisions

1. **Solar charger (CN3791 + TMP390A2, selected 2026-10-23):** Does the MPPT setpoint hold on the real panel through irradiance collapse? Is night leakage low enough? Does the 0–2 °C cold cut-out leave enough December charging? USB no longer charges.
2. **RTC always-on rail (TPL720F33 + CR1220, selected 2026-10-23):** pull-up location and values (1 MΩ on the wake inverter), no parasitic powering of dead MCU rails, measured total sleep current.
3. **Modem:** EG800K-EU (selected 2026-10-23, sheet in `hardware/lte/`) pin table to confirm against the EU manual; operator acceptance per country, including Australia; low stock (151); transmit current with battery depleted. ESP32 GPIOs: all sections now placed, with GPIO3 spare (H0-06).
4. **Audio:** Electret bias, gain/filter and full assembled-system self-noise; PCM1863DBTR equivalent sourcing.
5. **Storage:** bus decided (1-bit SD mode, ADR-012, 2026-10-23); card power switch part, recoverable metadata/audio write strategy.
6. **Mechanical:** target IP, port type, membrane replacement, service/access seals, solar/panel routing, RF coexistence and condensation.
7. **Battery life:** record/sync schedules, battery capacity, seasonal solar irradiation, charge/discharge temperature and cell replacement safety.
8. **MVP business scope:** connectivity in every recorder or optional SKU; targets/willingness to pay, hosting choices, human support cost.
9. **Firmware/security:** image rollback and secure local provisioning; time-quality strategy.
10. **Measurement market:** required uncertainty, validation and regulatory claims before environmental-noise marketing.
11. **Australian deployments (owner works in Europe and Australia, 2026-10-23):** DRM-1 is sized for 50–56°N winter. Australia adds a heat case: the charger cut-out stops charging above +42 °C, the ESP32-S3 N16R8 is rated to +65 °C ambient, and an enclosure in full sun can exceed both. Add a hot-climate requirement before an Australian field trial. The EG800K-EU covers Australian LTE (B1/3/5/7/8/28, RCM); 2G and 3G are already switched off there, so LTE-only loses nothing.

## Deferred options, not forgotten product commitments

- High-rate ultrasonic microphone board or separate Auris Ultra variant; earlier 384 kS/s generic ESP32 assumptions **cannot establish S3-system bat performance**.
- Event camera triggered by acoustic cues on a switched power domain; only after dropped-audio, storage, GPIO and power validation.
- Continuous event watch instead of completely power-gated scheduled capture; energy and recording policy need new architecture.
- Rich multi-device ecosystem integration with FieldMesh environmental sensor data; useful research idea, not required V1 coupling.
- Novelty discovery/embeddings, broad multi-species recognition, certified noise-compliance meters and 24/7 real-time threat alerting.
