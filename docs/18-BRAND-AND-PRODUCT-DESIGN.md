# 18 — Product design, user experience and messaging direction

**Status:** Proposed communication, industrial-design and UI direction; no finished visual identity or validated product UI.

## Name, category and primary message

- **Name:** AURIS (capitalized in technical artifacts; `Auris` acceptable in prose).
- **Category:** Autonomous environmental acoustic monitoring platform.
- **Working one-liner:** **Record the evidence. Understand the soundscape. Detect what matters.**
- **Longer explanation:** An offline-first field recorder that captures source audio on a schedule, supports acoustic measurements and selectively connects to a dashboard. A future detector workflow lets projects teach the platform their own target sounds.
- **Language preference:** Emphasize recording integrity, reliability, and traceability **before** leading with AI; never imply species ID is the only use case.

## Core design principles

1. **Field confidence over gadget aesthetics:** seals, corrosion resistance, wind/rain protection, mounting and glove-friendly service points matter more than visual polish.
2. **No mystery measurements:** link every event, acoustic metric and AI score to its source audio (when retained), calibration version, configuration and model.
3. **Offline works:** recording never requires cloud connection; BLE covers commissioning, LTE connects when useful, the dashboard reports delays honestly.
4. **First response to a fault is diagnostic clarity:** battery, SD, microphone and modem each have distinguishable health states, not one generic offline badge.
5. **Modular where it matters:** share a central controller/power/data design while evaluating separate audible and possible ultrasonic acoustic heads.
6. **Use explicit uncertainty:** distinguish measured/noise-calibrated quantities, ecological indices, detections, and human-verified observations.

## V1 enclosure direction (candidate)

- UV-stabilized polycarbonate commercial enclosure for prototypes. Aim for testable ingress protection (initial IP66 design target; IP67 only after validation).
- Mount an acoustic opening/replaceable windscreen under a protected downward-facing geometry with hydrophobic acoustic membrane and separate pressure-equalization vent where needed.
- Internally protect microSD and nano-SIM; use a sealed/serviceable USB-C approach, solar lead routing and mounting system appropriate for branches/posts.
- Zone electronics into **audio analogue**, **RF/LTE**, **switch-mode power**, **digital/SD**, to reduce conducted and radiated coupling.
- Prioritize microphone/membrane field service without removing the full enclosure if tests support a separable acoustic head.
- Check any membrane/windscreen attenuation through the actual assembled product before publishing calibrated SPL metrics.

## Dashboard information architecture (concept)

**Project overview:** sites/map, recording effort, recent events, coverage/completeness and devices needing attention.

**Deployment:** installation identity, site GPS from phone, start/end times, acoustic head/microphone serial, gain/calibration/profile, assignment and timeline.

**Recorder detail:** clear online/offline/last-seen state, battery and charge history, SD fill/corruption risk, next record/sync, firmware/config/model revision, action queue and audit log.

**Audio browser:** search by date/device/site, compact waveform/spectrogram, segment playback, tagged candidate event, download and quality flags; raw-audio availability displayed explicitly.

**Analysis:** separate panes for uncalibrated audio features, calibrated SPL metrics and ecoacoustic indices; include algorithm definition and confidence limits.

**Detector workspace (later):** labels and consensus review → dataset split/quality → training job → independent validation → approval → deployment rollout → performance monitoring and rollback.

## Field commissioning journey

1. Select existing project or offline deployment draft on phone.
2. Connect to nearby device over authorized BLE and verify serial/hardware revision.
3. Confirm timestamp/time zone, position, storage, battery, microphone self-test and firmware.
4. Apply a versioned recording schedule and optional LTE upload settings.
5. Record a short local test and show whether the audio path is responding/clipping.
6. Start deployment and persist configuration, time, site and operator audit record.
7. At retrieval, run post-deployment checks, close deployment and flag drift/missing files.

## Visual and content style directions

- Calm field-science aesthetics: neutral backgrounds, restrained natural-world accent color, clear contrast and readable charts. This is a **design proposal**, not an approved brand palette.
- Show actual waveform/spectrograms, battery plots and deployment maps; avoid unsupported animal AI-score graphics as the hero visual.
- Differentiate recording coverage, connectivity, algorithm outputs and validation status with separate consistent visual systems.
- Support expert needs (timestamps, export schemas, dB weighting, model versions) without forcing those technical controls into basic mobile commissioning.
- Consistent vocabulary: **recording**, **acoustic feature**, **sound-level measurement**, **candidate detection**, **reviewed observation**, **deployment**.

## Product statements to avoid until demonstrated

- `Class 1/2 IEC 61672 compliant`, `calibrated noise meter`, `bat recorder`, `real-time alerts`, `continuous AI`, `fully solar powered`, `weeks/months runtime`, `cloud sync always available`, `accurate species identification`, `IP67`, `end-user model training live`.
- Prefer `designed for`, `under development`, `prototype target` or `planned` where appropriate.

## Potential packaging and channels (exploratory)

- Field ecologists and survey consultancies first; contact conservation teams and acoustic researchers who use both passive recordings and manually reviewed sound events.
- Lead demo with a site→deployment→audio→event→review chain; show why searchable, auditable recordings beat a bare detection-count dashboard.
- Consider a local-only recorder and optional connected service tier only after assembly costs, modem certification, and operational support economics are measured.
- A separate noise/soundscape positioning path should await calibration and measurement uncertainty evidence.
