# 00 — Source of truth, version policy and current decisions

**Document baseline:** 2026-10-22. **Design maturity:** Schematic frozen for rev A layout (2026-11-19, `hardware/review/2026-11-19-schematic-freeze.md`), after two independent datasheet reviews (2026-11-17, 2026-11-19); nothing built or measured.

## Evidence and precedence

| ID | Evidence | Meaning | Priority |
|---|---|---|---|
| S1 | `references/Overview.txt` (current user-provided opportunity overview, no internal revision date) | Broad workflow/feature direction; much of it uses *could*, *should*, *suggested* | Current product intent, but **not** completed feature set |
| S2 | `references/Auris_Preliminary_Block_Diagram_and_Rough_BOM.docx` (hardware design proposal with supplier prices checked **2026-07-28**) | Explicit component selection status, pre-schematic power diagram, sequencing and cost caveats | Best available concrete architecture evidence |
| S3 | Supplied Espressif `ESP32-S3-WROOM-1 / -1U` datasheet v1.8 | MCU capabilities, module variants, limits | Authoritative for module specifications, not the overall Auris design |
| S4 | Auris discussions through October 2026 | Exploratory positioning: lower-cost rugged recorder, solar/cellular, user-trainable acoustic models, broad use cases | Product direction; no claim that hardware choices are implemented |
| S5 | External manufacturer/market pages checked 2026-10-22 | Market context and competitor feature examples | Comparative research only; not Auris requirements |

**Precedence:** Explicit latest user decisions > supplied design's explicit `Selected`/`Candidate`/`TBD` labels > current product overview > earlier ideation > our recommendations. Where there is no decisive evidence, label it **OPEN**.

## Status vocabulary

- **SELECTED (concept):** Chosen in the current engineering proposal; may still fail validation.
- **CANDIDATE:** Identified part/topology; must not be treated as locked.
- **REQUIRED CAPABILITY:** Intent accepted in the workflow; implementation not yet demonstrated.
- **PROPOSED:** Suggested design/implementation detail written here for engineering review.
- **FUTURE:** Opportunity beyond core recorder pilot.
- **OPEN:** Requires test, decision, or customer discovery.
- **VERIFIED:** Only use after reproducible test evidence. **No end-to-end Auris hardware has been verified in these materials.**

## Presently selected in the supplied hardware proposal

1. **ESP32-S3-WROOM-1-N16R2** (LCSC `C2913205`; owner decision 2026-11-18, ADR-001), 16 MB flash, 2 MB quad PSRAM, native USB, BLE and optional Wi-Fi, rated −40…+85 °C, selected as MCU/radio/processing platform. It replaced the N16R8 (8 MB octal PSRAM, rated −40…+65 °C) from the supplied proposal; same footprint.
2. **DS3231MZ+TRL** (revised 2026-10-22, supersedes RV-3129-C3 concept), I²C RTC with two time-of-day alarms, selected as always-on calendar wake source; see ADR-002.
3. **EG810M-EU** (Quectel LTE Cat 1, LCSC `C20421924`; owner decision 2026-11-18, ADR-006) as the LTE modem, for Europe, Australia and New Zealand. It replaced the EG800K-EU (`C44008839`, chosen 2026-10-23), which had no JLC stock; same package, and the footprint still takes an EG800K. The A7670G is the global alternate; the EG800K-LA fits the same footprint for the Americas.
4. **System operating intent:** normally fully off between recording/sync tasks; RTC/wake rail alive; local BLE service; event-driven, intermittent LTE; raw audio retained as primary evidence; independent recording and sync schedules.

**Note:** `selected` means chosen for the **preliminary concept**, not validated or purchase-frozen.

## Not selected / not validated

- **Audio:** Primo EM273 or equivalent electret microphone; PCM1863DBT I²S ADC; preamp/bias, clocking, gain and calibration details.
- **Modem:** EG810M-EU supply (ADR-011), Quectel AT driver, antenna, SIM/operator and RF validation; GNSS optional only.
- **Power:** charger, main 3.3 V, keep-alive and modem supply now **selected in concept** from FieldMesh Hub v2 / Node v4 (CN3791 + TMP390A2, TPS63802, TPL720F33 + CR1220, TPS63020; ADR-007/008/010/011, 2026-10-23), but **none measured on Auris**; solar harvest **not** established; TPS7A2033 audio LDO candidate; battery capacity **TBD**.
- **Mechanical:** enclosure/IP target, acoustic vent/membrane, windscreen, mounting system, thermal layout, manufacturing approach.
- **SD:** 1-bit SD mode chosen (ADR-012); card power switch (AO3401A + 2N7002) and card detect on GPIO3 drawn (2026-11-17) and an ESD array on the card lines (D403, 2026-11-18), not measured; file-integrity behaviour still open.
- **Cloud/UI:** technology stack, hosting, product pricing, subscription model, API paths, deployments, production security and regulatory assessments.
- **AI:** models, supported rates/features, detection thresholds, real-world inference latency, false-negative rates, end-user training UX.

## Superseded or misleading interpretations to avoid

- **Not** a bird-only or species-list-only product: sound signatures can be ecological, anthropogenic, mechanical or other project-defined targets.
- **Not** an AI-only recorder: audio capture, metadata and reproducible measurements have independent value.
- **Not** a certified sound-level meter: IEC 61672 class claims need separate design verification/certification.
- **Not** an automatic bat/ultrasound recorder merely because bats appear in potential use cases. The current analogue chain's effective sampling/ultrasonic response is unverified.
- **Not** continuous listening with zero-power RTC-off architecture: continuous watch is a separate energy/firmware architecture and a future option.
- **Not** proven solar operation: the candidate charger has not been validated under panel dynamics.
- **Not** a promise of universal edge classification: the intended detector starts narrow and needs objective field evaluation.
- **Not** a product with fixed sale price, BOM, battery life or deployment duration: those require measurement and commercial validation.

## Evidence for transitions

A `Candidate → Selected` decision requires a documented part number, schematic/interface choice, calculation or test basis, sourcing check and sign-off. A `Selected → Verified` transition requires electrical, functional and environmental results tracked in `12-TEST-AND-VALIDATION.md`. A feature marked `FUTURE` only enters MVP scope via the decision register and requirements update.
