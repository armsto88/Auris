# Auris

**Field-ready acoustic monitoring that works in the real world.**

---

## What is Auris?

**Auris** is a mid-cost, field-ready passive acoustic monitoring (PAM) device designed to bridge the gap between low-cost DIY recorders and expensive professional systems.

It is built for real deployments — not lab demos — prioritising reliability, ease of use, and scalable field workflows.

---

## Why Auris?

Current solutions often force a trade-off:

* Low-cost devices → affordable but fragile and difficult to use
* Professional systems → reliable but expensive and inflexible

**Auris is designed to sit in the middle:**

* Affordable enough for large deployments
* Robust enough for real field conditions
* Simple enough to deploy without friction

---

## Core Principles

### 1. Reliability First

* Designed for weeks–months of deployment
* Moisture-aware enclosure design
* Stable power and data handling

### 2. Ease of Use

* No laptop required for setup
* WiFi-based configuration interface
* Fast, repeatable deployment workflow

### 3. Scalable by Design

* Deploy 10–100+ units efficiently
* Minimal configuration overhead
* Consistent behaviour across devices

### 4. Practical Audio Quality

* Clean, consistent recordings
* Suitable for ecological analysis and ML pipelines
* Not over-engineered for unnecessary fidelity

---

## Key Features (Planned)

* Scheduled acoustic recording
* WAV file storage (16-bit)
* MicroSD logging
* WiFi access point configuration interface
* Battery monitoring
* Low-power duty-cycled operation

---

## System Overview

Auris is built around a simple but robust architecture:

* Microcontroller-based control system
* External ADC for improved audio quality
* Low-noise microphone front-end
* RTC-based scheduling
* SD card data logging
* Battery-powered operation

---

## Project Structure

```
auris/
├── docs/            # Engineering build brief (00–18), vision and design notes
├── specs/           # Machine-readable contracts and component starting points
├── assets/          # Diagrams and images
├── references/      # Supplied source documents (read-only, kept for provenance)
├── hardware/        # auris-hardware-guide.html (tab per section, LCSC codes) + audio, power and LTE sheet specs
├── firmware/        # Embedded code (planned)
├── enclosure/       # Mechanical designs and housing (planned)
├── tests/           # Validation and field testing (planned)
└── README.md
```

---

## Development Roadmap

### Phase 1 — Proof of Concept

* Basic recording pipeline
* SD logging
* Simple web interface

### Phase 2 — Reliability Prototype

* Custom PCB
* Power system validation
* Long-duration testing

### Phase 3 — Field-Ready Device

* Enclosure design and sealing
* Environmental testing
* Real-world deployments

---

## Documentation — Engineering Build Brief

**Baseline:** 22 October 2026  
**Status:** Pre-schematic concept / engineering definition (not a released or validated product)

> **Critical:** The build brief distinguishes selected components, candidate components, proposed behaviours and future opportunities. It is **not** a completed schematic, manufacturing BOM, verified acoustics specification or claim that features have been built.

### Read in this order

1. [Source of truth and current decisions](docs/00-SOURCE-OF-TRUTH.md)
2. [Product vision, users and scope](docs/01-PRODUCT-AND-SCOPE.md)
3. [Market positioning and commercial hypotheses](docs/02-MARKET-AND-POSITIONING.md)
4. [System architecture](docs/03-SYSTEM-ARCHITECTURE.md)
5. [Hardware V1 and schematic constraints](docs/04-HARDWARE-V1.md)
6. [BOM and preliminary economics](docs/05-BOM-AND-COSTS.md)
7. [Firmware, power and operating modes](docs/06-FIRMWARE-AND-POWER.md)
8. [Acoustic acquisition, metrics and calibration](docs/07-AUDIO-AND-CALIBRATION.md)
9. [AI, dataset and model lifecycle](docs/08-EDGE-AI-AND-MODELS.md)
10. [Backend, data contracts and retention](docs/09-BACKEND-AND-DATA.md)
11. [Dashboard and user journeys](docs/10-DASHBOARD-AND-UX.md)
12. [Connectivity, security and privacy](docs/11-CONNECTIVITY-AND-SECURITY.md)
13. [Verification and field trials](docs/12-TEST-AND-VALIDATION.md)
14. [Roadmap and prioritised backlog](docs/13-ROADMAP-AND-BACKLOG.md)
15. [Architecture decision register](docs/14-DECISION-REGISTER.md)
16. [Risks, unanswered questions and assumptions](docs/15-RISKS-AND-OPEN-QUESTIONS.md)
17. [Requirements and acceptance criteria](docs/16-REQUIREMENTS-TRACEABILITY.md)
18. [Reference sources and evidence](docs/17-SOURCES-AND-REFERENCES.md)
19. [Product messaging and design direction](docs/18-BRAND-AND-PRODUCT-DESIGN.md)
20. [V1 design reference mission and functional requirements](docs/19-V1-FUNCTIONAL-REQUIREMENTS.md)
21. [FieldMesh Hub v2 / Node v4 power review and modem cost options](docs/20-FIELDMESH-POWER-AND-MODEM-REVIEW.md)

### Machine-readable starting points

- [`specs/auris-major-components.csv`](specs/auris-major-components.csv) — transcribed major-component BOM with selection status and **historical** prices.
- [`specs/device-config.example.json`](specs/device-config.example.json) — **proposed** device configuration contract, not firmware API.
- [`specs/telemetry-event.example.json`](specs/telemetry-event.example.json) — **proposed** telemetry/event envelope, not backend API.
- [`specs/lcsc-orderable-2026-10-23.csv`](specs/lcsc-orderable-2026-10-23.csv) — exact LCSC codes, stock and prices for the main ICs, checked 2026-10-23.
- [`hardware/auris-hardware-guide.html`](hardware/auris-hardware-guide.html) — one page with a tab per hardware section and LCSC codes for every major component; open in a browser. Rebuild with `python3 hardware/tools/build_guide.py`.
- [`hardware/audio-frontend/`](hardware/audio-frontend/README.md), [`hardware/power/`](hardware/power/README.md) and [`hardware/lte/`](hardware/lte/README.md) — pin-level netlists and BOMs for the three sheets designed so far, with calculations and bring-up tests.
- [`assets/auris-v1-preliminary-block-diagram.png`](assets/auris-v1-preliminary-block-diagram.png) — extracted **preliminary** architecture image from the supplied engineering draft.
- [`references/`](references/) — supplied product overview and early hardware proposal retained unchanged for provenance.

### Engineering priorities before schematic capture

1. Verify the analogue microphone + ADC chain and realistic supported frequency range.
2. Bench-verify the selected CN3791 solar charger and TMP390A2 cut-out (from FieldMesh Node v4) with the real panel and cells.
3. Scope LTE power pulses at low cell voltage; decide direct-battery versus dedicated regulator.
4. Finish RTC backup supply, interrupt/power-latch and shutdown safety design.
5. Prove microSD recording integrity and ESP32-S3 resource budgets.
6. Confirm antenna, acoustic port, enclosure and environmental constraints together.

### Update discipline

- Change candidate/selected status only when design evidence or a dated decision exists.
- Add the reason to [`docs/14-DECISION-REGISTER.md`](docs/14-DECISION-REGISTER.md).
- Keep requirements tagged (`MVP`, `PHASE-2`, `FUTURE`) and associated with test evidence.
- Treat current cost figures as **28 July 2026 snapshots in USD**, not October 2026 supplier quotes.
- Avoid representing proposed JSON contracts, URLs, schemas and workflows as implemented.
- See [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution rules.

---

## Design Philosophy

Auris is not about pushing technical extremes.

It is about solving the real problems of field deployment:

* Devices failing in rain and humidity
* Data loss from unstable power systems
* Complex setup workflows slowing down teams

> If it works reliably in the field, it is successful.

---

## Future Directions

* Integration with acoustic analysis tools (e.g. BirdNET)
* Fleet management and deployment tracking
* OTA firmware updates
* Modular sensor expansion

---

## Status

🚧 Early-stage development — pre-schematic engineering definition (baseline: 22 October 2026)

---

## Author

Tom Armstrong
Conservation Technology | Bioacoustics | Environmental Sensing

---

## License

TBD
