# 16 — Requirements and acceptance criteria

**Baseline:** 2026-10-22. These are **proposed engineering acceptance criteria**, not passed tests. A requirement's appearance here does not imply delivery.

> **2026-10-23:** V1 functional requirements derived from design reference mission DRM-1 are in [`19-V1-FUNCTIONAL-REQUIREMENTS.md`](19-V1-FUNCTIONAL-REQUIREMENTS.md) and take precedence over the `MVP` rows below where they conflict: notably REC-005 (BLE commissioning, superseded by cloud web app + Wi-Fi hotspot), REC-007 (now energy-neutral operation, F4) and CON-001 (daily heartbeat and remote config move into V1). Full reconciliation of this table is pending.

Legend: `MVP` = needed for the first useful recorder pilot; `PHASE-2` = connected and analytical product capabilities after core recording is stable; `FUTURE` = option or opportunity. `OPEN` means numeric target or implementation is not yet accepted. Evidence is recorded in `12-TEST-AND-VALIDATION.md` and the issue tracker.

| ID | Priority | Requirement | Acceptance evidence / pass condition | Current state |
|---|---|---|---|---|
| REC-001 | MVP | Scheduled audible-band audio recording | Sample-accurate duration/file header, correct timestamp, listenable WAV across representative storage and temperatures; qualified frequency response | OPEN |
| REC-002 | MVP | Persist source WAV and metadata locally | Device can recover after interrupted writes; hashes and identifiers link audio to deployment/configuration | OPEN |
| REC-003 | MVP | Configure recording and upload schedules independently | Clock-controlled test demonstrates no unexpected modem activation during recording-only windows | OPEN |
| REC-004 | MVP | RTC-led power on/off | Wake by calendar alarm(s) and service button; graceful flush/power-down; measured off-state current | OPEN |
| REC-005 | MVP | BLE field commissioning | Authorized app reads device ID/status, applies versioned configuration and tests microphone/storage/time | OPEN |
| REC-006 | MVP | Weather-capable field enclosure | Defined ingress/UV/temp/condensation tests for real acoustic vent and cable arrangement; no unproven IP claim | OPEN |
| REC-007 | MVP | Battery/solar field autonomy | Energy profile from each power state and measured panel yield supports stated runtime in defined season/site | OPEN |
| REC-008 | MVP | Reproducible provenance | All recordings linked to serial, firmware, time source, gain, mic ID, config revision, position and calibration reference | OPEN |
| REC-009 | MVP | Safe configuration rollback | Corrupt/incompatible config rejected with safe defaults and explicit status, without loss of stored audio | OPEN |
| REC-010 | MVP | Field service | USB service/programming access, diagnostics, recoverable boot and failed-SD state | OPEN |
| CON-001 | PHASE-2 | Intermittent LTE telemetry | Queued health/config/detection summaries delivered after network outage; idempotent reconciliation | OPEN |
| CON-002 | PHASE-2 | Remote control and firmware | Signed/authorized commands with acknowledgements, audit log, safe staged update and rollback | OPEN |
| CON-003 | PHASE-2 | Upload audio selectively | User-selected/event clips transferred with checksum and retry; full source remains preserved locally | OPEN |
| ACO-001 | PHASE-2 | Acoustic/soundscape features | Definitions, units, windowing and reference implementation for selected indices; results versioned by algorithm | OPEN |
| ACO-002 | PHASE-2 | Sound-pressure metrics | Calibration and uncertainty method demonstrated for claimed LAeq or other metrics; never use IEC class language without assessment | OPEN |
| AI-001 | PHASE-2 | Single/few-target edge detector | Benchmarks of flash/RAM/PSRAM, latency, power, precision and recall on independent field data | OPEN |
| AI-002 | PHASE-2 | Transparent detection review | Users can inspect evidence and label true/false/uncertain; preserve model and threshold at event time | OPEN |
| AI-003 | FUTURE | End-user detector training | Versioned label->train->evaluate->approve->deploy->rollback workflow with train/test isolation | OPEN |
| PLT-001 | PHASE-2 | Project/deployment hierarchy | CRUD and permissions for project, site, device, deployment, configuration and observation; complete audit lineage | OPEN |
| PLT-002 | PHASE-2 | Health dashboard | Device last-seen, battery/storage/connectivity, schedule, alerts and sync queue identifiable per device | OPEN |
| PLT-003 | PHASE-2 | Research-grade export | WAV + CSV/JSON with timestamps, coordinates, calibration, algorithm/model version and review status | OPEN |
| SEC-001 | MVP | Unique device identity and protected credentials | Per-device keys/provisioning and documented compromise/replacement procedure | OPEN |
| SEC-002 | PHASE-2 | Network security and permissions | TLS validation, least-privilege projects, signed update delivery, secure storage and retention controls | OPEN |
| MFG-001 | MVP | Testable PCB/assembly | Tagged test points for battery/current, switched 3.3V, always-on RTC, modem, audio supply, SD, reset and wake logic | OPEN |
| MFG-002 | MVP | Sourcing/production readiness | Frozen schematic and BoM, known alternates, test fixture, QA checks and actual assembled product COGS | OPEN |

## Minimal pilot exit gates

1. **Audio gate:** unbiased listening and comparison against a reference recorder, plus objective noise/clipping/response results.
2. **Power gate:** measured state durations and current transients, reliable RTC wake/power hold/SD flush, conservative battery model and solar worst-case.
3. **Field gate:** successful deployments across representative rain, wind, humidity and temperature with a documented failure log.
4. **Reproducibility gate:** export package links every retained file/event to the exact configuration and time/calibration state.
5. **Commercial gate:** full enclosure/assembly/calibration/SIM/cloud economics and pilot-user feedback—not only component price.

For test protocols and unresolved targets, see `12-TEST-AND-VALIDATION.md` and `15-RISKS-AND-OPEN-QUESTIONS.md`.
