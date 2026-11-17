# 02 — Market placement and commercial hypotheses

**Date:** 2026-10-22. Comparisons are illustrative snapshots from manufacturer sites, not a market census or procurement quote.

## Positioning

**Positioning statement (working):** For field researchers, ecologists, consultants and teams that need repeatable acoustic evidence in places that are difficult to visit, Auris aims to combine a field-ready autonomous recorder, intermittent remote operations, calibrated analysis and eventually project-trained acoustic event detection in one configurable platform.

**White-space hypothesis:** bridge the gap between affordable offline acoustic loggers, durable professional recorders and managed always-connected sensing platforms. The feature combination—not a claim that nobody offers it—is the potential differentiation.

### Competition / alternatives

| Category / example | Current market context | Implication for Auris |
|---|---|---|
| **Open Acoustic Devices AudioMoth** | Low-cost full-spectrum microSD logger; published shop listing **£79.99** at research time; 8–384 kHz sampling advertised | Strong low-price and ultrasound benchmark. Auris cannot credibly compete on cheapest logger or claim ultrasound without tests. |
| **Wildlife Acoustics Song Meter Mini 2** | BLE mobile configuration, flexible scheduled WAV capture, rugged IP67 housing; manufacturer currently lists **USD $499 AA / $599 Li-ion** | Durability, runtime and usability bar for paid field research. Auris needs a clear benefit from connectivity and integrated workflows. |
| **Frontier Labs BAR-LT** | Professional long-term autonomous recorder with rugged enclosure, GPS, multiple SD cards and configurable recording | Shows premium segment values field reliability, microphone performance, storage, schedule flexibility and traceability. |
| **Edge–cloud research prototypes (e.g. OrniSonix paper)** | Lightweight edge gate, LTE uploads and cloud inference demonstrate a similar broad architectural pattern | Novelty is not LTE+AI alone; prove excellent field evidence retention, model evaluation and easy per-project training. |
| **Existing lab workflows** | Offline recorders + notebooks + cloud storage + sound-analysis software | Primary alternative may be fragmented tools, not a single hardware competitor. |

Published product prices are **observations, not an Auris sales-price target**. Prices/availability vary by currency, variant, tax and date.

## Where Auris might win

1. **Project-trained sound signature detection:** not restricted to predefined animal species. Different detectors for a frog, insect, machine squeal or other signal.
2. **Remote, yet offline-capable:** useful service/telemetry over LTE while source evidence remains local and continues through outages.
3. **Acoustics + interpretation:** source WAV and metadata sit alongside environmental-noise summaries, ecoacoustic features and review status.
4. **Transparent confidence and validation:** users can interrogate mistakes, preserve negative samples, compare thresholds and export defensible metrics.
5. **Adaptable cost/power tiers:** potential hardware variants without forcing remote features on every deployment (**concept only**).

## Important positioning caveats

- Avoid saying **"certified sound level meter"**, **"scientifically validated biodiversity score"**, **"universal species recognition"**, **"ultrasonic bat recorder"**, **"zero maintenance"** or **"guaranteed solar autonomy"**.
- Do not lead product messaging only with AI: lead with trustworthy recording/monitoring and the capacity to adapt detectors to project needs.
- Current concept is **pre-schematic**. External descriptions should say *developing*, *exploring*, *designed to*, rather than *ships*, *supports today*, or *proven*.

## Suggested commercial packaging (hypotheses; not decisions)

- **Core local recorder:** lowest recurring cost; recording, BLE, SD, field configuration and export.
- **Connected recorder:** optional LTE hardware/services; sync telemetry, candidate events and remotely change schedules.
- **Analysis workspace:** project data, soundscape/noise plots, annotation and reviews; priced based on storage/usage if delivered as SaaS.
- **Detector Builder (later):** hosted training/version management; credits or recurring plans based on workload rather than claiming unlimited training.

One PCB shared across variants vs two SKUs is **open**; LTE inclusion is a significant hardware/operations cost contributor. Do not set retail prices without COGS including enclosure, PCB/assembly, QC, calibration, pack-out, warranty, SIM, bandwidth and hosting.

## Beachhead recommendation (strategy, not chosen market)

Start with **ecology/consultancy field teams requiring scheduled audible-band recording and remote recorder health**. They offer a bounded evidence-based pilot, useful early audio datasets and a direct path to project-specific detectors. Expand to environmental-noise studies only when calibration procedures are repeatable, and to operational event alerting only after alert reliability is quantified.

## Customer-discovery tests

- Interview 8–12 potential teams; record current devices, field-visit frequency, missing data events, minutes spent processing audio, data transfer and procurement budgets.
- Test willingness to pay separately for local recorder, connectivity, dashboard and training.
- Pilot competing performance against a known recorder under identical conditions (microphone noise floor, response, battery cost per recorded hour, failures, environmental durability).
- Test whether customers value **raw data availability + transparent model errors** more than headline detection count.
- Clarify regulatory constraints and acceptable microphone placement/recording near human activity.

## External market references

- [AudioMoth official product](https://www.openacousticdevices.info/product-page/audiomoth-1-2-0) (price/features observed 2026-10-22).
- [Song Meter Mini 2 official guide](https://answers.wildlifeacoustics.com/r/en-US/Song-Meter-Mini-2-User-Guide/About-the-Song-Meter-Mini-2).
- [Song Meter Mini 2 AA shop page](https://www.wildlifeacoustics.com/products/song-meter-mini-2-aa) and [Li-ion shop page](https://www.wildlifeacoustics.com/products/song-meter-mini-2-li-ion).
- [Frontier Labs BAR-LT official](https://www.frontierlabs.com.au/bar-lt).
- [OrniSonix published edge-cloud prototype](https://www.mdpi.com/2079-9292/15/20/4724).

## Historical pricing scenarios — superseded as a sales commitment

Earlier July 2026 brainstorming included possible fully built cost **€120–190**, connected recorder retail **€329–399**, field kit **€429–549**, and connectivity/platform service **€5–12 per recorder per month**. **These were rough, unverified scenarios, not pricing decisions.** No manufacturing yield, enclosure/assembly, certification, support, cloud/data usage or competitive willingness-to-pay model has validated them. Retain them solely for sensitivity analysis in the future COGS model; do not publish them as launch prices.
