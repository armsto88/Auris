# 09 — Backend, data architecture and evidence provenance

**Technology decisions remain open.** A relational metadata database plus object store is a reasonable **proposed** design, not a decision to use Supabase, AWS or any specific stack. Do not transfer architecture choices from unrelated projects into Auris without a recorded decision.

## Conceptual services

| Service | Main role | Delivery phase |
|---|---|---|
| Device registry + deployments | Identity, provisioning, ownership, location history | MVP / connected prototype |
| Sync endpoint | Idempotent telemetry/events/config acknowledgements | MVP connected |
| Recording catalog | Manifest and local/cloud availability, checksum, queue state | MVP |
| Object storage | Selected WAV/clips/diagnostic files and derived assets | MVP when uploading audio |
| Metrics service | Acoustic indices, noise summaries, profiles | PHASE-2 |
| Candidate review | Play/spectrogram/validate detections | PHASE-3 |
| Model registry/deployer | Compatibility, canary rollout/rollback | PHASE-4 |
| Detector Builder | Dataset annotations, training/evaluation | FUTURE |
| Reporting/export | Method-rich CSV/JSON/WAV and analysis report | PHASE-2+ |

## Core entities and relationships

- `organisation` or tenancy boundary — ownership/access; authentication technology **TBD**.
- `project` — goals, policy, schedule templates, analysis profiles, member permissions.
- `site` — place and location uncertainty; coordinates potentially sensitive.
- `recorder` — immutable hardware serial, board revision, microphone identity, firmware capability.
- `deployment` — recorder/site/project plus start/end UTC; no overwriting site history.
- `device_config_revision` — signed/sequenced and effective UTC time, hash, applied/rejected status.
- `recording` — raw file manifest, interval, health, checksum, retention and availability status.
- `measurement` — index/noise metric, method version, calibration and recording relationship.
- `detection_candidate` — score/time window/class/model version and provenance.
- `validation` — reviewer/time/label/comments with audit history; no silent overwrites.
- `training_dataset_version` — immutable clip labels and partition definitions.
- `model_version` / `deployment_rollout` — training, compatibility, activation and rollback history.
- `health_event` / `device_event` — battery, charging, uptime, resets, faults, free storage, signal, missed intervals.

## Data integrity and idempotency

- Device generates stable IDs for session, recording, measurement and candidate to survive retransmission.
- Chunked uploads should use checksums and *server acknowledgements* before queue removal.
- An accepted upload does not mean source can be deleted; deletion must follow explicit per-project policy and audit.
- Use sequence numbers and time correction events to distinguish delayed upload from acquisition time.
- Cloud reflects `stored_on_device`, `queued`, `uploaded`, `archived`, `deleted_by_policy` distinctly.
- Preserve raw-file checksum and derivation lineage from WAV to measurements/detections and model training records.

## Example contracts

See [`../specs/device-config.example.json`](../specs/device-config.example.json) and [`../specs/telemetry-event.example.json`](../specs/telemetry-event.example.json). These demonstrate structure and ownership only, **not stable APIs**, secure credentials, signed manifests or firmware-ready schemas.

## API capabilities (not routes)

- Register/commission device, bind/unbind deployment.
- Push health, recording manifest, acoustic summary, candidate, job and firmware state.
- Retrieve pending config revision and signed model/firmware package manifest.
- Request selected clip, full recording or diagnostic bundle with acknowledgement and queue handling.
- Query review queues, save validation decision, export source-related report.
- Support pagination, idempotency keys, data ownership, authentication, rate limiting and audit logs.

## Reports and exports

Detection tables with validity labels, recording effort/coverage tables, soundscape/noise time series, site comparisons, model performance and health/calibration histories; CSV/JSON/API access and audio/spectrogram export. A scientific export must include sampling and filtering parameters, time quality, gain/microphone calibration, analysis algorithm version, device firmware, detector threshold and human-review status.

## Observability (proposed)

Service side: ingest failure rates, queue backlog, per-device last-heard, unresolved commands, model update success, cost per GB/device. Device side: expected vs actual recording count, corruption rate, SOC, resets, BLE service frequency, LTE network attach time, modem TX bytes, audio clipping/near-silence, clock drift, model compute latency.

## Privacy and retention model

Define explicit project authority over raw and derived recordings. Legal basis, informed notice, retention/erasure requirements, incident response and cross-border transfer policies are jurisdiction/use-case-specific. Do not treat cloud analysis of ambient speech as automatically lawful. See `11-CONNECTIVITY-AND-SECURITY.md`.
