# 08 — Optional edge AI and user-trainable detection

**Product differentiation:** user-trainable detectors that can learn diverse *acoustic signatures*, not just a preloaded bird-species catalogue. **Delivery status:** future opportunity; there is no finished detector builder or validated Auris model in the source material.

## MVP versus later stages

1. **First:** dependable recorder and reproducible measurements with no model required.
2. **Then:** one internally trained, narrow target vs background/confusers; benchmark on ESP32-S3.
3. **Then:** versioned edge model registry, selective rollout and model fallback.
4. **Later:** project users upload, review and label examples, train in backend, compare metrics and deploy quantised models.
5. **Experimental extension:** embeddings/novelty/outlier discovery, clustering unrecognised sounds and semi-automated training set creation. This is exploratory and may initially run entirely in the cloud.

## Detection semantics

Run after a scheduled recording (source-draft architecture), with windowed analysis and per-window scores. **"Detected" means model candidate**, not biological confirmation. For each candidate retain event time/sample offsets, class, score, model hash, threshold, processing version, recorder/site and source clip identity. Include `unknown`, `uncertain` and `no_event` pathways; avoid forcing every clip into a named target.

### Proposed retention categories

- Positive candidates: keep clip or full source as defined by project policy.
- Uncertain cases and hard negatives: retain enough for expert review.
- Negative controls: retain periodic/random subsamples **even if no trigger**.
- Changed-model controls: temporarily sample more broadly around deployment changes.
- Whole-session reference recordings: optional for high-value studies; never rely exclusively on edge gate for assessing recall.

A filtering model that discards all "no event" audio destroys the evidence needed to estimate false negatives and can systematically bias occupancy/activity conclusions.

## Training data

Include positives, target lookalikes, overlapping calls, common confusers, wind/rain/insects, empty/background, recordings across devices and sites, multiple individuals/seasons/distances. Track licensing, origin, geography and context of source clips. Partition evaluation by **site/time/individual/recorder**, not merely random neighbouring windows, to reduce leakage and inflated accuracy.

### Detector Builder user journey (future)

1. Name detector and target/background/confuser classes.
2. Upload examples or select validated recordings from approved project data.
3. Annotate time regions and spectrograms; manage reviewer disagreements.
4. Create immutable dataset snapshot; show missing context/site-bias warnings.
5. Launch backend training, preserve model architecture/features/seeds.
6. Compare precision, recall, false positives per hour, PR curve, threshold-specific performance and worst-site metrics.
7. Quantise and hardware-benchmark before allowing deployment.
8. Release to one test recorder, then a selected group, then whole project, with rollback.
9. Audit field false positives/negatives and retrain on a new dataset version.

## Edge requirements (benchmarks not yet confirmed)

- Choose a feature pipeline (spectrogram, log-mel or band features) that fits RAM, flash and PSRAM. Since 2026-11-18 the module is the ESP32-S3-WROOM-1-N16R2 (ADR-001): 2 MB quad PSRAM instead of the N16R8's 8 MB octal PSRAM, with about a quarter of the octal-DDR bandwidth at 80 MHz, and 16 MB of memory-mapped flash where model weights can stay. The ≥ 5 s audio buffer (F3-05, 480 KB) also lives in PSRAM. Keep flash and PSRAM at 80 MHz (the experimental 120 MHz mode can crash after a temperature swing of about 20 °C, ESP-IDF *flash_psram_config* guide).
- Quantised TFLite Micro is a **current concept**, not an implementation commitment; check supported operators, conversion and ESP-IDF integration.
- Measure working-set and activation memory at runtime, inference milliseconds per audio window, battery joules per detection job, flash/PSRAM consumption and effects on SD capture.
- Package must include target labels, sample rate, window/hop, feature version, thresholds, compatible firmware, size/hash/signature and fallback link.
- Reject model updates that violate memory/latency constraints or sample-rate/feature compatibility.
- Separate model confidence score from calibrated probability. A score `0.8` is **not automatically an 80% likelihood** of truth.

## ESP32-S3 TinyML feasibility research (external source, 2026-10-22)

**Source:** OpenELAB, *ESP32-S3 TinyML Guide: Image, Audio & Sensor Models at the Edge* (published Aug 2026, reviewed 22 October 2026). Vendor blog with practical TinyML guidance; not an independent benchmark and not Auris-specific evidence. Findings below are **general platform facts**, not measured results on Auris hardware — they inform ADR-017 direction but do not close any benchmark.

### Confirms the existing architecture assumption

- ESP32-S3 has **vector instructions, not a dedicated NPU**; acceleration applies to selected NN/DSP operations only. Fits the Auris position: small local decisions (audio classification, anomaly screening), not general real-time detection or speech-to-text.
- Keyword spotting / sound classification is a **realistic workload class** on ESP32-S3: fixed sample rate, fixed window length, MFCC/MFE features, INT8 quantization. This matches the `docs/08` windowed post-recording analysis concept.
- Offline inference works once model + preprocessing are deployed; Wi-Fi/BLE/LTE only needed to report results. Consistent with Auris: detections computed locally, evidence and summaries uploaded later (see `11-CONNECTIVITY-AND-SECURITY.md`).

### Auris-relevant cautions

1. **Operator support is the gating constraint.** Converting a model to `.tflite` does not guarantee it runs: microcontroller runtimes support a **subset of operators**; "compiles but will not run" usually means unsupported operator. The `08` requirement to reject incompatible model packages stands.
2. **Do not judge feasibility by model file size.** Runtime needs input buffers, intermediate tensors, audio buffers, stacks, heap and drivers on top of the model blob. 8 MB PSRAM ≠ 8 MB model budget — matches the existing rule to measure working-set at runtime. Auris now has 2 MB PSRAM (N16R2, 2026-11-18), shared with the audio buffer.
3. **Memory placement matters:** PSRAM is slower than internal SRAM; high-frequency audio/feature buffers and the Tensor Arena should be measured, with critical regions kept in internal RAM where possible.
4. **Dataset discipline echoes the Auris training-data section:** collect target + background + unknown + silence classes across distances/rooms/noise; a classifier trained only on clean desk recordings collapses near fans/motors/echo. **Never split frames/windows of one continuous recording across train and test sets** — inflated accuracy from leakage.
5. **Toolchain should be chosen before the model architecture** (supported operators, memory plan, deployment target), not after. Candidates compared in the source: **Edge Impulse** (rapid prototyping, integrated collection→export), **LiteRT Micro** (formerly TFLite Micro — more conversion control, more manual work), **ESP-DL accelerated by ESP-NN kernels** (ESP-IDF-native, most platform-specific), SenseCraft AI (low-code).
6. **Typical failure symptoms and fixes** (useful as bench triage for G8): allocation failed → Tensor Arena too small or simplify model; inference crash → RAM fragmentation, allocate buffers early, shrink input; very slow inference → quantize and reduce input dimensions; wrong results after quantization → rebuild representative dataset.
7. **Confidence handling:** return `unknown` when confidence is low rather than forcing a class — aligns with the `unknown`/`uncertain` pathways already required in Detection semantics above.

### What it does NOT establish

- No acoustic-model size/latency numbers for Auris' PCM1863 I²S pipeline (different audio path than the source's dev-board microphones).
- No energy-per-inference figures for the Auris power architecture (externally gated domains, LTE sync windows); the `G8` energy measurement remains open.
- No ecoacoustic multi-class evidence — the source demonstrates small-class-count classification; species-rich classification remains unproven on this platform.

### Follow-up actions captured

- First internal benchmark (roadmap phase 2) should still target **one narrow target vs background/confusers** on the actual ESP32-S3-WROOM-1-N16R2 module (the N16R8 until 2026-11-18), as planned in `13-ROADMAP-AND-BACKLOG.md`.
- Model packages must record the operator set supported by the chosen runtime (Edge Impulse export vs LiteRT Micro vs ESP-DL) to enforce compatibility rejection rules.

## Evaluation / validation

Required: confusion by class, precision, recall, false positive detections per hour, missed positives on independent reviewed audio, threshold curves, variation by site/weather/device and confidence intervals where enough ground truth exists. For rare-target screening prefer **high recall** but document cost of false positives. Human-confirmed/rejected/uncertain labels must be explicit.

Test comparisons: detector-enabled vs full-audio reference period; in- vs out-of-distribution sites; low SNR and overlap; changed microphone and enclosure; revised model vs baseline; delayed event upload. Audit drift after firmware/gain/calibration changes.

## Model lifecycle contract (proposed)

`experimental → bench_qualified → field_trial → validated_for_defined_domain → active → retired`

Each transition needs signed-off benchmarks and domain qualifiers. Store immutable version, dataset snapshot, training parameters, feature schema, applicable taxa/sounds, intended regions, confidence threshold, binary hash and rollout history. Rolling back the model must not roll back captured source evidence.
