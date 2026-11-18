# 19 — V1 design reference mission and functional requirements

**Baseline:** 2026-10-23. **Status:** Owner decisions (2026-10-23) plus **proposed** requirement values. Figures marked *est.* are planning estimates, not measurements; replace them with bench data from gates G1–G5 (`12-TEST-AND-VALIDATION.md`). For V1, this document takes precedence over the `MVP` rows of `16-REQUIREMENTS-TRACEABILITY.md` where they conflict.

## Purpose

Every acceptance criterion in doc 16 was `OPEN` because there was no reference mission to derive numbers from. This document fixes one mission (DRM-1) and states each V1 requirement by function, with a number, its origin and a verification method.

## Owner decisions (2026-10-23)

| # | Decision | Affects |
|---|---|---|
| D1 | The primary V1 mission is a long-term biodiversity survey (DRM-1). Audio stays on the recorder | ADR-025 (new); beachhead in doc 02 |
| D2 | The recorder runs until the SD card is full: energy must never be the limiting factor | REC-007, ADR-022; solar enters V1 |
| D3 | Energy-neutral sizing for 50–56°N in winter | ADR-022 |
| D4 | Both an enclosure-integrated panel and an external cabled panel are supported | ADR-022, ADR-020 |
| D5 | V1 LTE = daily heartbeat + remote configuration + clock sync. No audio upload in V1 | CON-001 (part) moves into V1; ADR-006 populated in V1 |
| D6 | Configuration is authored in a cloud web app (no native app). Sites without coverage use a device-hosted Wi-Fi hotspot page | ADR-015 (BLE superseded for V1), REC-005 |
| D7 | 48 kHz mono, 16-bit PCM WAV, factory-set gain plus a "loud site" preset | ADR-013, ADR-014 |

## DRM-1 — Long-term biodiversity survey

| Parameter | Value |
|---|---|
| Schedule | 60 s every 600 s, 24 h/day → 144 recordings/day, 10 % duty (configurable) |
| Audio | 48 kHz, mono, 16-bit PCM WAV with GUANO metadata |
| Data rate | 5.76 MB/file → 0.83 GB/day |
| Service interval | Set by card capacity: 128 GB ≈ 150 days, 256 GB ≈ 300 days |
| Connectivity | One LTE session/day, on the RTC Alarm 2 standing window (ADR-002). LTE only, no 2G fallback (ADR-006) |
| Reference site | 50–56°N, design month December. Integrated panel in open sky; cabled panel for shaded sites |
| Ambient (proposed) | −20 to +35 °C |
| Retrieval | SD card swap on site |

### Energy budget (design targets, *est.*)

| Load | Target | Basis |
|---|---:|---|
| Recording | ≤ 0.84 Wh/day | ≤ 350 mW average at the battery × 2.4 h |
| Wake / boot / commit | ≤ 0.05 Wh/day | ≤ 1.25 J per wake × 144 |
| LTE session | ≤ 0.05 Wh/day | ≤ 180 J/day, covers a weak-signal attach |
| Off state (RTC, latch, leakage) | ≤ 0.02 Wh/day | ≤ 200 µA at 3.7 V. The DS3231M alone takes up to 130 µA from VCC in standby (corrected 2026-10-23, doc 20) |
| **Design load** | **≤ 1.0 Wh/day** | Sum plus margin |

Recording dominates. The ESP32-S3 capture power is the main lever on panel and battery size, so F4-06 makes it a requirement in its own right.

### Solar and battery sizing (*est.*)

- **Panel:** 1.0 Wh/day ÷ (0.5 peak-sun-hours × 0.5 end-to-end efficiency) ≈ **4 W**. 0.5 PSH is a conservative December in-plane value for a steep, south-facing panel at 50–56°N; check each real site with PVGIS. 0.5 efficiency assumed a non-MPPT linear charger plus temperature, soiling and angle losses. With the CN3791 buck charger now selected (ADR-007, 2026-10-23) the end-to-end figure should be nearer 0.65, giving **≈ 3 W**; keep 4 W until the bench confirms it.
- **Tilt:** winter noon sun elevation at 52°N is ~15°. A near-vertical south-facing panel (enclosure front rather than lid) outperforms a flat one in winter and sheds rain and leaf litter.
- **Shade:** deciduous canopy is leafless in December, so the winter open-sky case and a summer full-canopy case may be of similar severity. Conifer stands need the cabled panel. Measure, do not assume.
- **Battery:** ≥ 10 days of DRM-1 with zero harvest at 0 °C → ~10 Wh usable → ~15 Wh nominal after 80 % usable depth and cold derating. **1S2P 18650** (~21.6 Wh at 3,000 mAh) meets this with margin and keeps the 1S charger architecture.
- **Cold:** Li-ion must not charge below 0 °C, so frosty days harvest nothing. The TMP390A2 cut-out (ADR-007) trips at **+5 °C** and releases at +10 °C (owner decision 2026-11-17: with the TMP390's ±2.5 °C accuracy a 0 °C setting could charge down to −2.5 °C). That blocks more December charging at 50–56°N than the 0 °C setting assumed earlier, so the battery buffer and F4-03 carry more of the winter; re-check F4-01 against the measured winter harvest.

## Headline requirement

**H-01 — Scheduled-effort yield ≥ 99.5 %** over any 30-day window at reference conditions, defined as valid recorded minutes ÷ scheduled minutes. Every missed or degraded slot is logged with a cause code (`energy`, `storage`, `fault`, `service`, `time_unknown`) and reported in the heartbeat. Energy-degraded slots count as misses.

## Functional requirements

All rows are priority **V1** and status **OPEN** (no verification evidence yet).

### F1 — Capture

| ID | Requirement | Derived from | Verification |
|---|---|---|---|
| F1-01 | Record 48 kHz mono 16-bit PCM for a scheduled 1–3600 s. Sample count = duration × rate exactly; zero dropped buffers with injected SD write stalls ≤ 500 ms | DRM-1, D7 | 24 h bench run with stall injection (G2, G3) |
| F1-02 | Start ≤ 2 s after the scheduled time; store the actual start time to ≤ 1 s UTC | DRM-1 | Bench with GPS-referenced tone |
| F1-03 | Gain is factory-set per unit from bench measurement; a "loud site" preset is selectable by config | D7 | Per-unit calibration record |
| F1-04 | Per recording, compute RMS, clipping % and per-band noise floor ("mic fingerprint") | H-01, R08 | Reference WAV fixtures |
| F1-05 | Compare the mic fingerprint with the commissioning baseline; flag a shift > X dB in any band (X set from G2/G6 data) | R08 | Blocked-port and wet-membrane tests |
| F1-06 | Analog high-pass corner selectable by config before the gain stage: ≈ 100 Hz (default), ≈ 36 Hz (wide), ≈ 1 kHz; changed only between recordings | Wind/rumble overload; `hardware/audio-frontend/` | Swept sine per setting; wind clipping count |
| F1-07 | Digital filters selectable by config: Butterworth high-pass, low-pass, band-pass or notch, order 2–8, corners 20 Hz to 0.45 fs. Separate `record_filter` (default none) and `analysis_filter` chains; the mic fingerprint is computed before either | Raw audio is the evidence (doc 01) | Reference WAV fixtures through each filter type |

### F2 — Time and schedule

| ID | Requirement | Derived from | Verification |
|---|---|---|---|
| F2-01 | Run interval and daily-window schedules in UTC with no missed or duplicate slots across midnight, month-end and leap day | DRM-1 | Accelerated RTC test |
| F2-02 | Sync the clock at each LTE session; UTC error ≤ 1 s within 24 h of the last sync | D5; DS3231M ±5 ppm ≈ 0.43 s/day | Bench vs NTP reference |
| F2-03 | Without LTE, set the clock from the phone via the hotspot page. At every service visit, log the device-vs-phone offset **before** correcting, so drift can be corrected in post-processing | D6 | Offset log audit |
| F2-04 | Every file carries a time-quality flag (`lte_synced` / `phone_set` / `unsynced`) and the age of the last sync. Never write audio with an unflagged unknown time | R06 | Power-loss test |

### F3 — Storage and integrity

| ID | Requirement | Derived from | Verification |
|---|---|---|---|
| F3-01 | Never overwrite or delete audio on the device. When the card is full, stop recording, keep the heartbeat and report `storage_full` | D2 | Fill-the-card test |
| F3-02 | A power cut or card removal at any instant loses at most the in-progress file; closed files and the manifest stay valid | R04 | ≥ 1,000 randomized cuts and removals |
| F3-03 | SHA-256 of every closed file recorded in the manifest | Doc 09 | Manifest audit |
| F3-04 | Support cards up to 256 GB; report days-to-full daily | DRM-1 | Card matrix test |
| F3-05 | Buffer ≥ 5 s of audio (480 KB) in PSRAM to ride out SD write stalls (fits in the N16R2's 2 MB, 2026-11-18) | F1-01 (10 × 500 ms) | Stall injection |

### F4 — Energy

| ID | Requirement | Derived from | Verification |
|---|---|---|---|
| F4-01 | Energy-neutral on the DRM-1 schedule at the reference site over the worst 30-day window | D2, D3 | Energy model from G1/G5 measurements + winter field log |
| F4-02 | ≥ 10 days of DRM-1 operation with zero harvest at 0 °C | D3 | Climate-chamber discharge |
| F4-03 | Degrade in steps as charge falls: full schedule → reduced profile (defined in config) → heartbeat only → safe off. Default thresholds 40 / 20 / 10 % SOC with ≥ 10 % hysteresis, tunable. SOC is estimated from battery voltage measured before the modem turns on (ADR-027; no fuel gauge). Never brown out mid-write | D2 | SOC-sweep bench |
| F4-04 | Recover autonomously from complete depletion once harvest resumes, with no site visit | D2 | Drain and recharge test |
| F4-05 | No charging below 0 °C or above 45 °C | Battery safety | NTC chamber test |
| F4-06 | Meet the energy budget above; recording ≤ 350 mW average at the battery | Energy budget | Current-waveform measurement |
| F4-07 | Accept the integrated panel, an external panel through a sealed connector, or both. Charger input tolerates panel Voc at −20 °C | D4 | Bench with both panels, cold Voc |

### F5 — Commissioning and service

| ID | Requirement | Derived from | Verification |
|---|---|---|---|
| F5-01 | With coverage, from a phone browser with no install: scan the recorder QR → bind to a deployment → capture phone GPS and accuracy → press the button → device fetches its config over LTE, records a 10 s test and reports back → "Ready to deploy" checklist. ≤ 5 min end to end | D6 | Timed field trial, gloved |
| F5-02 | Without coverage, a button press starts a Wi-Fi hotspot (WPA2, per-device passphrase on the label/QR, ≤ 15 min idle timeout) serving a local page from device flash: status, test recording with level/clipping and playback, set clock from phone, edit schedule and gain preset, upload a signed config bundle, download manifest, start/end deployment | D6 | Offline field trial |
| F5-03 | Local config edits become a new revision with source `local`, are reported at the next LTE session, and are never silently overwritten by the cloud | D5, D6 | Config conflict test |
| F5-04 | Scheduled recordings take priority over service mode; the Wi-Fi radio is paused during a recording | H-01, R05 | Recording during an open service session; RF noise check |
| F5-05 | A status LED reports the test-recording, SD and config result after a button press, readable in daylight | D6 | Field check |
| F5-06 | The SD card is swappable without opening the main seal; the device checks the new card and resumes | D2 | Swap test |

**Position capture note:** browsers block geolocation on plain-HTTP pages, so the hotspot page cannot read the phone's GPS. Position is captured by the cloud web app (HTTPS, installable so it works offline) and joined via the deployment ID. The hotspot page accepts typed coordinates as a fallback.

### F6 — Health and remote configuration

| ID | Requirement | Derived from | Verification |
|---|---|---|---|
| F6-01 | One heartbeat per day, ≤ 1 KB payload: battery voltage and estimated SOC, panel voltage at each wake and the day-on-day battery change as a harvest proxy (V1 hardware does not measure charge current or tell the two panel inputs apart), temperature, SD free and days-to-full, scheduled/obtained/missed slots with cause codes, mic fingerprint and drift flag, fault counters, firmware and config revision, LTE signal | D5, H-01 | Payload audit |
| F6-02 | Apply cloud config at the next session, between recordings. Report `desired` / `applied` / `rejected`. Invalid config keeps last-known-good and never stops recording. The web app shows "pending until next check-in" with the expected time | D5 | Malformed-config test |
| F6-03 | LTE failure never affects recording; LTE energy is capped at the F4 budget; retries are bounded | D5 | No-SIM / no-coverage soak |
| F6-04 | ≤ 1 MB per recorder per month, including TLS overhead | D5 | Modem byte counters |
| F6-05 | Per-device identity; config signed and verified before apply; no shared secret in firmware | SEC-001, SEC-002 | Security test |

### F7 — Environment

| ID | Requirement | Derived from | Verification |
|---|---|---|---|
| F7-01 | Operate at −20 to +35 °C ambient; internal air ≤ 65 °C in full sun (set by the N16R8 module rating, doc 04; the N16R2 fitted since 2026-11-18 is rated to +85 °C, and the next limits are the modem and SIM holder at +75 °C, so this limit can be revisited), e.g. with the panel as a sun shade | DRM-1 | Climate chamber + sun-exposure log |
| F7-02 | Mic fingerprint shift after a wet/dry cycle ≤ X dB per band (X from G2/G6 data) | R08 | Spray and recovery test |
| F7-03 | Survive driving rain and condensation cycling for a full 300-day service interval. IP66 is a test target, not a claim (ADR-020) | D2 | G6 environmental tests |

### F8 — Provenance and export

| ID | Requirement | Derived from | Verification |
|---|---|---|---|
| F8-01 | Each WAV embeds serial, deployment ID, config revision and hash, firmware, start UTC and time quality, gain preset, mic ID, front-end path and the full filter chain (analog corner, ADC filter, digital filters) in a GUANO chunk, mirrored in the manifest | REC-008, F1-06, F1-07 | Metadata parse |
| F8-02 | The SD card alone yields a complete CSV/JSON manifest, with no cloud needed | Doc 01, principle 1 | Offline export test |

## Not in V1

Audio or clip upload over LTE, edge detection, acoustic indices and sound-level metrics (beyond the F1-04 fingerprint), BLE, GNSS and ultrasound. Each needs an ADR to enter V1.

## Values still to set

| Item | Where | How to close |
|---|---|---|
| Mic-drift threshold X dB | F1-05, F7-02 | G2/G6 bench data |
| Reduced-profile schedule | F4-03 | Project default per survey type |
| Card size shipped (128 vs 256 GB) | F3-04 | Cost vs service interval |
| Firmware update path in V1 | — | Decide: none, via hotspot page upload, or via SD file at service visits |
| Final panel and battery sizing | F4 | Replace *est.* figures with the measured load |
