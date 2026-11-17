# 13 — Build roadmap, milestones and prioritised backlog

**This is a recommended sequencing of work, not a committed release timetable.** Acceptance gates take precedence over dates and cosmetic progress.

## Phase 0 — Close architecture blockers (now)

**Goal:** manufacturable *concept* with documented constraints and testable candidate choices, not yet a production schematic.

- [ ] H0-01 Obtain samples for microphone and PCM1863DBT/DBTR; validate availability and whether analog noise floor is suitable.
- [ ] H0-02 Bench the CN3791 solar charger and TMP390A2 cut-out (drawn in `hardware/power/`, 2026-10-23) with the real panel and the Node v4 pack: MPPT divider, harvest, night leakage, cold trip. USB charging dropped.
- [ ] H0-03 Measure EG800K-EU transmit current across cell voltage/temp (sheet drawn in `hardware/lte/`, 2026-10-23); choose safe supply and bulk/trace plan.
- [ ] H0-04 Bench the wake latch (drawn in `hardware/power/`, 2026-10-23): RTC VCC/VBAT/INT handling, button/USB wake, ship-mode switch, latch current and emergency shutdown.
- [ ] H0-05 Card bus chosen (1-bit SD mode, ADR-012); select the card power switch; prove sustained audio writes, write-latency buffering and recoverable file format.
- [ ] H0-06 Pin-map ESP32-S3 peripherals, boot/USB/radio restrictions and thermal constraints. All sections have proposed pins (MCU tab of the hardware guide); UART0 given up for the SD bus, console over USB; GPIO3 spare.
- [ ] H0-07 Draft enclosure/audio-port/RF placement with water, wind and condensation design constraints.

**Exit:** signed pin map/power tree and measured high-risk breadboard results; only then schematic freeze.

## Phase 1 — Local recorder proof of function (engineering MVP)

- [ ] F1-01 RTC wake → power hold → ADC capture → microSD WAV/manifest → safe shutoff.
- [ ] F1-02 Deterministic recording schedule and clock correction, UTC metadata, error reporting.
- [ ] F1-03 Console and programming over USB-Serial-JTAG (no UART0 header) and constrained BLE commissioning without LTE.
- [ ] F1-04 Battery/SD/recording status and visible error log.
- [ ] F1-05 Manual audio calibration record and microphone identity capture.
- [ ] F1-06 Failure injection, bench endurance, reference microphone side-by-side.

**Exit:** reproducible audio captures with no unexplained power/SD loss, documented gaps and test logs.

## Phase 2 — Connected field pilot

- [ ] C2-01 Safe LTE power domain and operator/antenna test.
- [ ] C2-02 Idempotent health/manifest sync, remote config versioning, upload queue.
- [ ] C2-03 First multi-recorder project/deployment registry and coverage/health dashboard.
- [ ] C2-04 Requested clip transfer, checksum/ack and configurable retention.
- [ ] C2-05 Solar energy balance and cold/weather field checks.
- [ ] C2-06 Threat model and authenticated device identity for remote operations.

**Exit:** record locally regardless of network; remote telemetry useful and correctly reports incomplete coverage.

## Phase 3 — Measurements and validation workflow

- [ ] A3-01 Implement versioned DSP fixtures and basic descriptors (RMS, clipping, band energy) first.
- [ ] A3-02 Add selected ecoacoustic indices as comparable profiles with known limitations.
- [ ] A3-03 Develop acoustic calibration, measurement uncertainty, reference comparison and noise-level outputs **only where validated**.
- [ ] A3-04 Build reviewer queue, source-linked clips, validated/false/uncertain audit and export.

**Exit:** methods are reproducible and charts cannot hide method/profile changes.

## Phase 4 — Limited edge detector

- [ ] M4-01 Gather fixed target, near-miss and background data from pilot audio; site-separated test set.
- [ ] M4-02 Build small feature/quantised model within ESP32-S3 measured RAM/compute budget.
- [ ] M4-03 Record positive/uncertain/negative controls, per-window score, and original WAV provenance.
- [ ] M4-04 Test threshold/recall and false positives/hour under field conditions; compare against raw baseline.
- [ ] M4-05 Versioned package, signed rollout and rollback if remote model updates are delivered.

**Exit:** honest domain-limited model claims backed by reviewable data.

## Phase 5 — Configurable detector service (long-term differentiator)

- [ ] B5-01 Human labelling, immutable datasets, split hygiene, trainer and evaluation UI.
- [ ] B5-02 Automated quantisation/compatibility bench tests and model registry.
- [ ] B5-03 Canary and batch deployments, threshold control, field-performance feedback.
- [ ] B5-04 Hard-negative mining and retraining loop; later optional novelty/embedding tools.

**Exit:** users can build and deploy **project-specific** models without accidental circular evaluation or data-loss policies.

## Separate research tracks (do not block recorder MVP)

Ultrasonic alternative head, event-triggered camera on switched rail, always-on event watch, GNSS, Wi-Fi option, multi-SKU hardware, FieldMesh context fusion, automated compliance reports and certifiable sound-level-meter path. Each needs an ADR to become core scope.

## Priority order

**P0 / safety and evidence:** wake/power, charger, modem supply, SD corruption, audio noise, data lineage, security basics.

**P1 / usable pilot:** BLE diagnostics, recording scheduler, firmware release process, recorder health, calibration history, backend queue.

**P2 / expanded product:** acoustic index suite, advanced dashboards, limited AI, batch model updates, commercial workflows.

**P3 / experiments:** open-ended detector training, novelty analysis, camera/ultrasound, advanced fusion and multi-market extensions.
