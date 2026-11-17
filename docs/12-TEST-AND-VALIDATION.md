# 12 — Engineering verification, calibration and field qualification

**No passing Auris V1 verification data has been supplied.** This is a test plan, not a test report. Numeric pass/fail limits marked `TBD` must be agreed and recorded *before* data collection.

## Evidence packet for every test

Use `test_id`, requirement ID, board serial/revision, BOM revision, hardware modification notes, firmware commit/hash, exact wiring, instruments/calibration status, environment, setup diagram, procedure, raw log/data path, measured results, pass/fail and reviewer/date. Preserve failures and reruns. Store captures in repository or suitable external artifact store with checksums.

## Gates

| Gate | Required verification | Why it matters | Status |
|---|---|---|---|
| G0 Architecture | Power tree/latch review, pins, parts, mechanical and cost assumptions | Prevent invalid schematic foundation | OPEN |
| G1 Power prototype | RTC VBACKUP, alarm INT, service wake, PWR_HOLD hold/release, brownout, USB insertion and protection | Device wakes/turns off deterministically | OPEN |
| G2 Audio chain | Mic/ADC gain, noise, linearity, sample clock accuracy, no lost samples, EMI/radio contamination | Valid evidence | OPEN |
| G3 Storage | Long WAV, slow/removed/corrupt/full SD, power-cut recovery, file checksum, journal policy | No silent data loss | OPEN |
| G4 LTE/solar | Attach/TX pulses at low battery/cold, charger solar sweeps, charge cutoff, worst-case standby | Stable remote field energy | OPEN |
| G5 Integrated recorder | 24h+ bench schedule and repeated wake/record/write/sync/off; firmware watchdog recovery | System reliability | OPEN |
| G6 Environmental | Membrane acoustic response, wet/dust, condensation, UV/thermal, seals, RF antenna after assembly | Deployable mechanical package | OPEN |
| G7 Controlled pilot | Paired reference recorder; missed effort, sensitivity, calibration drift, servicing | Field evidence for roadmap | OPEN |
| G8 Model qualification | Independent annotated data; site-level precision/recall and false positives/hour; edge memory/energy | Detector fitness for defined domain | FUTURE |

### Power and wake matrix

Test both alarms individually and together (A1 one-shot, A2 standing window, simultaneous match), plus button/USB wake, RTC I²C comms with main rail off, wake-line leakage/back-power, held INT flag, MCU late/failed PWR_HOLD, firmware crash and hard reset, cutoff during SD flush (simulate safely), charger brownout, and watchdog restart. Log current waveform and actual cut-off time.

### Energy budget methodology

Measure real `I × V` and cycle duration for: RTC always-on, boot, SD init, recording, index calculation, inference, LTE attach/TX, file transfer and shutdown. Define daily energy:

`E_day = E_RTC_24h + Σ(E_boot + E_record + E_analyse + E_store + E_shutdown)_jobs + Σ(E_attach + E_upload)_sync + E_losses`

Use **actual sample data**, conservative temperature/panel-season assumptions and battery usable-capacity derating. Report an energy *range* with survey schedule and locality. No autonomy claim until this model is backed by field measurements.

### Audio QA

- Reference calibrated acoustic source: multiple levels/frequencies and port orientations, record gain and distortion/clipping.
- Mic/ADC noise spectrum with charger/buck-boost/LTE/SD active vs inactive; test acoustic port and complete enclosure.
- Continuous recording with simultaneous SD writes and analysis (where supported); assert no dropped PCM buffers.
- Timestamp drift (RTC + sample clock) using known test signals; attach uncertainty to each recording.
- Calibration repeatability pre/post microphone replacement, enclosure modifications, and humidity cycling.
- Check SPL weighting/integration and frequency response separately before exposing LAeq or percentile plots.
- For acoustic indices, compare known WAV fixtures across firmware/backend implementations and pinned profile versions.

### Data and software QA

- Config round trip; unsupported schema fails safely; signed revisions applied at safe boundaries.
- Idempotent upload after disconnection/reboot; checksum unchanged and source preserved.
- Device replacement at same site retains provenance; mixed sample rates/analysis profiles not plotted as directly comparable.
- Negative control audio retained per project policy and candidate score always labelled unreviewed until human validated.
- Inject file corruption and invalid metadata; failures visible and no stale analysis displayed as valid.

### Field pilot design

Start with **3–5 prototype units** as a suggested pilot size, not a committed order; deploy alongside an established reference recorder at several acoustic environments (quiet woodland, wind/rain, human-made noise). Rotate units between sites to separate site effects from microphone/board effects. Keep a full reference-audio/control subset to evaluate missed model detections. Record service events, field repair time, weather, battery/panel orientation and all missing-effort periods. Establish acceptance thresholds before deployment, not retroactively.

## Release gates: no default pass values

- Sample drop/corruption: `TBD` permitted incidents across `TBD` endurance hours.
- Recording schedule accuracy: `TBD` seconds, with uncertainty and synchronization method.
- RTC always-on current / off current: `TBD` µA at `TBD` voltage/temperature.
- Audio self-noise, frequency response, SPL level error: `TBD` per intended product tier.
- LTE recovery and clip-upload integrity: `TBD` recovery time/data-loss tolerance.
- Operating temperature, water ingress and acoustic membrane life: `TBD` test methods and criteria.
- Detector threshold: preregister metric targets per species/sound/site domain.

Define limits with actual customer needs and reference instruments, then review with independent engineering judgement.
