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
├── docs/            # Vision, architecture, and design notes
├── hardware/        # PCB designs and schematics
├── firmware/        # Embedded code
├── enclosure/       # Mechanical designs and housing
├── tests/           # Validation and field testing
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

🚧 Early-stage development

---

## Author

Tom Armstrong
Conservation Technology | Bioacoustics | Environmental Sensing

---

## License

TBD
