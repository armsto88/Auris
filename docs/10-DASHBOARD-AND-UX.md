# 10 — Dashboard, commissioning and interaction design

**Status:** Proposed product design, derived from `references/Overview.txt`. No frontend has been built or framework committed for AURIS.

## Product information architecture

A project is the primary organisational unit, not a device. A project has monitoring objectives, users, sites, deployed recorders, schedules, acoustic profiles, retention rules and (later) models. One physical recorder may participate in several consecutive deployments without destroying its history.

| Area | Primary question | Key content | First phase |
|---|---|---|---|
| Fleet / organisation | Is monitoring working? | Last seen; expected/received recordings; low battery; failed writes; overdue sync; health exceptions | Connected pilot |
| Project overview | Are we collecting useful evidence? | Sites, recorder availability, recording effort, upload backlog, task list, detections/metrics when enabled | Connected pilot |
| Recorder detail | What is happening on this unit? | Serial, hw revision, firmware, active config hash, RTC quality, SOC/solar/storage, schedule, fault log, calibration history | Prototype |
| Deployment detail | Where and when was it measuring? | Site, time window, coordinates/uncertainty, mic/calibration IDs, start/end checks | Prototype |
| Recording catalogue | What evidence exists and where? | WAV manifests, audio preview when uploaded, checksum, queued vs cloud vs archive state, download | Prototype/connected pilot |
| Review queue | What requires human judgement? | Candidate clips, waveforms/spectrograms, threshold/model, confirm/reject/uncertain, correction and comments | Detector phase |
| Soundscape | How did site acoustics vary? | ACI, NDSI, entropy, band energy, effort and profile comparisons; method details | Measurement phase |
| Environmental noise | What level/exposure pattern occurred? | LAeq etc. **only after calibration**; uncertainty and quality flags | Measurement phase |
| Detector Builder | Can I train a project detector? | Training clips/labels, confusion, threshold tradeoffs, release, rollback | Future |
| Reports/exports | Can I reproduce the result? | WAV/CSV/JSON, provenance, missing-effort and calibration reports, validation status | Pilot+ |

## Commissioning journey — offline first

1. Installer wakes recorder using service button or USB; app discovers it over BLE.
2. Display hardware serial, firmware, battery condition, storage, clock status and current assignment.
3. Associate with project/site; check coordinates and deployment identifiers; preserve history when a unit moves.
4. Configure recording schedule, sample/gain profile, required health reporting and data-retention policy.
5. Run short test WAV; display input level, clipping/near-silence, card read/write results and reference playback.
6. Perform or attach applicable mic calibration; capture membrane/port and enclosure inspection.
7. Review a concise **Ready to deploy / Requires attention** checklist with specific failed checks.
8. Commit versioned configuration locally; mark deployment started; produce a downloadable commissioning manifest.
9. On recovery, reconnect to inspect faults and reconfigure even without network access.

**UX constraint:** no setup path should silently require successful LTE/cloud login before local recording. If ownership proof/offline authentication is required, design and test offline-capable credentials; do not leave BLE publicly writable.

## Suggested web visual language — design direction, not brand decision

- Field-tech friendly: high-contrast monochrome base, restrained accent colour, information density appropriate for status dashboards; do not communicate status by colour alone.
- Map/site overview as a *navigation aid*, not a substitute for recorder list, accessibility or exact coordinates.
- A global health count should separate **offline by schedule** from **unexpected offline**. The recorder is normally powered off; never equate `last_seen > 1h` with fault absent a sync expectation.
- Recording effort must show both **scheduled** and **successfully obtained** minutes; missing audio is often the key scientific failure.
- Always display a visible `data available locally / queued for upload / cloud copy` state, avoiding ambiguous "uploaded" icons.
- Candidate AI detections labelled **unreviewed** by default; show score, threshold, clip and model version beside reviewer choice.
- Charts show units, time zone, analysis profile and confidence/quality flag. Allow compare only where sample/analysis profiles are compatible.
- Mobile first for commissioning and inspection; desktop first for reviewing large recording and model-training sets. Responsive layout and accessible tap sizes.

## Profile templates — optional starting configurations

`Biodiversity baseline`, `Target sound survey`, `Environmental noise research`, `Machinery event`, `Custom research`. Templates populate fields and are **not** hidden modes with undisclosed behaviour. Users can inspect a diff before applying a profile. Initial pilot should use at most one or two tested templates.

## Deployment swap and traceability

A failed recorder can be replaced in the field. End old deployment and create a new hardware-to-site association (or child deployment segment) while retaining the logical site identity. Old files remain linked to old microphone, firmware and calibration versions. Provide partial-swap recovery and no destructive overwrites. This is an implementation suggestion, not a feature already present in Auris.

## Review queue flow

`candidate → awaiting review → confirmed / rejected / uncertain → corrected-label (if appropriate)`; every change is auditable. Reviewers should not be forced to confirm candidates when audio is unavailable. Separate model score from ecological truth; avoid treating absence of detection as absence of a species.

## Screens to prototype before full backend development

1. Commissioning + recording test (offline BLE)
2. Recorder fault/status timeline with expected wake/sync
3. Project recording coverage matrix by site/day
4. Detection review: audio, spectrogram, negative examples, reviewer audit
5. Acoustic metrics with methodology and missing-effort overlay

## Acceptance tests for UX

- Field user can restore a failed configuration over local service link without LTE.
- A reviewer can trace every plotted metric/detection back to source recording ID and method version.
- An export retains deployment/site identity even after recorder swap.
- Overdue status cannot trigger merely because the expected sync schedule has not elapsed.
- User cannot accidentally delete sole raw recording through a misleading upload-state UI.
