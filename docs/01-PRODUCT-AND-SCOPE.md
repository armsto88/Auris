# 01 — Product vision, scope and users

## Product thesis

AURIS is a **configurable, evidence-first environmental acoustic monitoring platform**. It should make long-duration audio sampling practical in remote places, connect acoustic measurements with the recordings that produced them, and eventually let project teams train detectors for *their own* target sound signatures.

A recorder is useful even with AI disabled. Remote connectivity saves field visits and enables selective transfer; it must not be a prerequisite for collecting valid local evidence.

## Design principles

1. **Raw audio is the evidence.** The platform may upload only summaries on most sync cycles, but source recordings and explicit retention records enable independent review.
2. **Project-driven, not locked to one species.** Support wildlife, soundscape change, community noise, biosecurity and equipment-event projects using a common platform.
3. **Low power by schedule.** Wake for recording/compute/sync only when needed; never silently equate long battery life with continuous capture.
4. **Field recoverability.** BLE, service button and USB provide access without LTE or internet.
5. **Reproducibility and calibration.** Record firmware, configuration, gain/microphone, calibration, algorithms and model versions with results.
6. **AI finds candidates.** A scored event is not a validated observation. False negatives matter, so negative/control audio retention is essential.
7. **Explicit consent and privacy.** Environmental audio may record people; policy depends on deployment jurisdiction and use case.
8. **Incremental engineering.** First make a dependable audio recorder, then analytics, then models and remote operations.

## Intended customers / project users

| Segment | Problem | Auris value hypothesis | Caution |
|---|---|---|---|
| Ecologists and conservation teams | Remote surveys with high retrieval/processing costs | Robust scheduled acoustic evidence; indices, targeted alerts, validation | Wildlife detection requires ground-truth review |
| Research institutions and environmental consultancies | Reproducible longitudinal field data | Versioned methods, calibration, API/export and project views | Academic credibility depends on validation and metadata |
| Land managers and biosecurity teams | Monitoring a known unwanted or rare signal | Narrow user-trainable detector, prioritised clips | Needs site-specific false-positive/false-negative reporting |
| Communities and environmental-noise researchers | Long-term sound-level and event evidence | Calibrated measurements with original recordings | Not a certified compliance meter unless separately qualified |
| Infrastructure/machinery operators | Event logging in remote settings | Solar/LTE status, specialised noise/acoustic event detection | Reliability, governance and liability differ by application |

These are **opportunities**, not verified market demand.

## Example project profiles (proposed defaults)

- **Biodiversity baseline:** scheduled reference WAV recordings, indices, effort tracking, no AI requirement.
- **Target acoustic event:** scheduled record → thresholded candidate model → positive/uncertain/negative sampling → review.
- **Environmental-noise survey:** calibration-led equivalent levels and band energy, consistent period aggregation.
- **Machinery event monitoring:** tailored event labels, controlled retention, network-robust alerts.
- **Research custom:** explicit sampling/calculation settings, rich metadata and reproducible exports.

## Workflow

1. Create a project with goal, sites, duration, retention and default analysis/recording profiles.
2. Commission a recorder locally, test audio, clock, battery/storage, radio and optional calibration.
3. Assign to a deployment with a **versioned** configuration and site coordinate record.
4. Record on schedule independently of LTE sync.
5. On recording completion, calculate configured metrics; optionally run a target detector; store source + metadata.
6. Send health/detections/summaries at sync intervals; retrieve clips/full audio on request or via explicit rules.
7. Review candidates, mark confirmed/rejected/uncertain, export measurements and monitor data quality.
8. In later phases, curate labelled recordings → train → evaluate → staged deployment → measure model drift and retrain.

## Deliverable boundaries

### V1 / core recorder pilot

Scheduled audio and metadata, safe SD storage, RTC wake/shutdown, offline field setup, basic health, data export, local configuration recovery, reference-test calibration capability. LTE prototype can initially send minimal health; it should not gate local reliability.

### Next product phases

Environmental-noise/ecoacoustic metrics, richer remote config, web project views, candidate detection and review, robust OTA/model update, detector registry.

### Differentiating long-term platform

Interactive Detector Builder, hard-negative mining, embedding/novelty discovery, semi-automated clustering/labeling, quantised edge deployment, per-site performance reporting and model feedback loop.

## Out of scope until specifically decided

Real-time streaming, unconditional full-audio LTE upload, certified IEC class 1/2 measurements, always-on ultrasound, animal species identification across all taxa, cellular fallback guarantees, public alerting for high-stakes events, a fixed phone application technology stack and an end-to-end cloud feature commitment.
