# 11 — BLE, LTE, storage security, privacy and updates

**Status:** Requirements/proposed controls, not audited implementation. **EG810M-EU is selected in concept** (ADR-006, since 2026-11-18; it replaced the EG800K-EU): LTE only, Europe/Australia/NZ bands; backend and identity stack undecided.

## Distinct channels

| Path | Purpose | Non-negotiable behaviour |
|---|---|---|
| BLE / USB local | Commission, test microphone, inspect logs, recover configuration | Works offline; authenticated/authorised change path; service session bounded |
| LTE remote | Health, configs, detections, summary metrics, selected audio, signed firmware/model packages | Intermittent and non-blocking relative to audio capture; adaptive backoff, budget limits |
| microSD local | Primary recordings, metadata, pending queue | Captures through radio outage, explicit integrity and retention state |
| Optional Wi-Fi | Possible service/sync variant | **Not in current core feature commitment** despite ESP32-S3 Wi-Fi support |

## LTE uplink and backpressure rules (proposed)

- Connect only on a due synchronisation job or explicit service/test reason.
- Transmit heartbeat and summary data first, then requested clips, then permitted bulk recordings subject to battery/time/data budgets.
- Include `{device_id, event_id, sequence, timestamp_utc, config_hash, payload_hash}`; receiver must be idempotent.
- Queue on SD with an acknowledgement-based state machine; avoid removal when TCP/MQTT/HTTP write merely returned success without application receipt.
- Retry with exponential backoff and jitter while maintaining next recording schedule. Cap attachment attempts/bytes and defer uploads when SOC, temperatures or LTE signal are inadequate.
- Receive remote config as a versioned, authenticated desired-state document; apply only at a safe boundary and report **desired**, **applied** or **rejected** separately.
- Do not promise always-on live alerts from a fully off-duty-cycled device. Alert latency is dominated by next wake/sync unless explicitly specified otherwise.

## Device identity and trust (requirements)

- Assign a non-reassignable manufacturing serial and per-device credential (key/certificate or equivalent; exact mechanism TBD).
- Protect provisioning and ownership transfer, including a factory-reset procedure that does not leak another customer's keys or data.
- Restrict BLE service to a commissioning window and require authenticated writes; no hard-coded global secret in firmware/repo.
- Authenticate and encrypt all remote traffic, verify server identity, and pin minimum supported TLS/security capabilities of the chosen modem and stack.
- Sign/verify firmware and model bundles; define anti-rollback/version constraints and compatible hardware/feature schema.
- Use secure boot/flash encryption when feasible; evaluate ESP32-S3 eFuse irrevocability and manufacturing recovery risks before provisioning.
- Have recovery paths for failed update, bad model, incorrect schedule and expired certificates **without** corrupting recordings.

## Updates (proposed design gates)

1. Server advertises signed manifest: identifier, hash, size, hardware variant, min firmware/bootloader, required features, rollout cohort and rollback compatibility.
2. Device checks resource/energy/free space and verifies payload integrity/signature before activation.
3. Switch only after writing and safely closing recordings; allow test boot and health confirmation.
4. Roll back on boot failure/crash or reject incompatible package; retain update history.
5. Show staged/canary deployment and audit of operator who authorised change.

**Hard constraint:** the native ESP32 USB programming route is a development/recovery tool, not evidence that secure OTA exists.

## Privacy and lawful deployment

Ambient recordings can contain voices and personally identifiable information. Project configuration must specify authorised purposes, notice/consent or other applicable legal basis, access controls, location sensitivity, retention period, sharing and response to deletion requests. EU/GDPR and other regulations depend on location, organisation and use; compliance advice requires qualified legal review.

- Record only needed audio and minimise LTE upload; configurable time windows and acoustic triggers do not eliminate privacy issues.
- Segregate organisations/projects; maintain access log for playback and exports; restrict bulk download by role.
- Encrypt data at rest as appropriate to threat model; SD removal remains a physical security risk.
- Clarify how redaction requests interact with scientific record preservation and retention policies; don't silently overwrite evidence.
- Avoid marketing the product as a privacy-compliant surveillance/security system or certified legal-noise evidence device.

## Connectivity validation gates

- LTE no-service for days: no dropped scheduled WAV; bounded retry energy; eventual queue drain.
- Low-signal attach and TX peak: no brownout, audio clipping, SD corruption or analog rail contamination.
- Clock rollback/time correction: no duplicate IDs or overwritten files.
- Malicious config/model, BLE unauthorised request, stale token: fail closed for destructive operations.
- Partial upload and modem reset: resume/idempotency, checksum and server receipt.
- SIM absent/expired/roaming: explicit diagnosis instead of silent recording failure.

## Open decisions

LTE protocol and IoT provisioning, hosting/data residency, auth provider, SIM/eSIM/operator, GNSS/time sync strategy, encrypted SD feasibility, BLE pairing UX, secure boot/OTA partition layout, telemetry budget, over-the-air file transport and legal/privacy process owners.
