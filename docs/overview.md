# Auris — Vision Plan & Focus Areas

## 1. Vision

Build **Auris**, a mid-cost, field-ready passive acoustic monitoring (PAM) recorder that bridges the gap between low-cost DIY devices (e.g. AudioMoth) and expensive professional systems.

The device should prioritise:

* **Reliability in real-world deployments** (rain, cold, humidity)
* **Ease of use** (no laptop required)
* **Scalable deployment** (10–100+ units)
* **Clean, usable audio data**

---

## 2. Core Value Proposition

> Auris is a deployable acoustic instrument that "just works" in the field.

### Key differentiators:

* WiFi-based configuration (no desktop software required)
* Robust enclosure + moisture management
* Stable long-term logging (no SD corruption)
* Thoughtful power design for multi-week deployments

---

## 3. Target Users

* Ecologists & field researchers
* Environmental consultancies
* Conservation NGOs
* Research institutions
* Early-stage conservation tech startups

---

## 4. Design Priorities (Ranked)

### 1. Reliability (Critical)

* Survive long deployments (weeks–months)
* No data loss
* Stable power system
* Moisture-resistant design

### 2. Ease of Use (Critical)

* No firmware flashing for users
* WiFi access point configuration
* Simple deployment workflow

### 3. Affordability (High)

* Target retail: €150–€250
* BOM target: €30–€60

### 4. Sound Quality (Moderate)

* Clean, consistent recordings
* Sufficient for species detection / ML workflows
* Not audiophile-grade

---

## 5. Key Technical Focus Areas

### A. Enclosure & Environmental Robustness

* Waterproof enclosure (IP65+ target)
* Pressure equalisation (vent membrane)
* Condensation mitigation (silica, airflow strategy)
* Acoustic transparency for microphone

### B. Power System

* Single-cell Li-ion (18650 preferred)
* Efficient sleep/wake scheduling
* Battery protection + charging circuit
* Optional solar integration (future)

### C. Data Integrity

* Reliable SD card writing strategy
* Brownout detection
* Safe shutdown handling
* File integrity (chunked writes, periodic flush)

### D. User Interface

* WiFi AP mode
* Browser-based UI (mobile-friendly)
* Configurable:

  * Recording schedule
  * Gain
  * Status monitoring

### E. Audio Chain

* Low-noise microphone front-end
* External ADC (better than MCU internal ADC)
* Anti-alias filtering
* Stable sampling clock

---

## 6. Suggested High-Quality Components to Research

### Microcontrollers / Processing

* ESP32-S3 (WiFi + good ecosystem)
* ESP32-C3 (lower power alternative)

### ADC (Audio Quality Critical)

* PCM1802 (proven, simple)
* PCM1808 (similar, improved specs)
* TLV320ADC family (integrated options)

### Microphones

* ICS-40720 (low noise MEMS)
* ICS-43434 (I2S digital MEMS option)
* Primo EM272 (high-quality electret)

### Analog Front-End (Op-Amps)

* TLV9062 (low noise, low power)
* OPA1678 (higher performance)
* NE5532 (classic, but higher power)

### Power Management

* TP4056 (basic Li-ion charging)
* MCP73831 (compact charger)
* BQ24074 (more advanced power path)

### DC-DC Converters

* MT3608 (boost, cheap)
* TPS63060 (buck-boost, efficient)
* LMR33630 (buck, high efficiency)

### RTC (Timekeeping)

* DS3231 (high accuracy, already proven)
* PCF8523 (lower cost alternative)

### Storage

* MicroSD card (industrial grade recommended)
* Consider SLC or high-endurance cards

### Environmental Protection

* Gore vent (ePTFE membrane)
* Hydrophobic acoustic vent membranes
* IP-rated enclosures (e.g. polycarbonate)

---

## 7. MVP Definition (Version 1)

### Must include:

* Scheduled recording
* WAV file storage (16-bit)
* SD card logging
* WiFi configuration interface
* Battery monitoring

### Must NOT include (yet):

* Real-time streaming
* Complex AI processing
* Cloud integration

---

## 8. Development Phases

### Phase 1 — Proof of Concept

* Dev board + external ADC
* Basic recording + SD logging
* Simple web UI

### Phase 2 — Reliability Prototype

* Custom PCB
* Power system validation
* Long-duration testing

### Phase 3 — Enclosure & Field Testing

* Waterproofing iterations
* Condensation testing
* Real deployments

---

## 9. Success Criteria

* Device records reliably for >2 weeks without failure
* No SD corruption during normal operation
* User can configure device in <5 minutes
* Audio quality sufficient for species detection workflows

---

## 10. Long-Term Vision

* Integration with analysis pipelines (e.g. BirdNET)
* Fleet management dashboard
* OTA updates
* Modular sensor expansion

---

## 11. Summary

**Auris** focuses on solving the practical challenges of real-world acoustic monitoring — reliability, usability, and scalability.

> If Auris is simple, reliable, and easy to deploy — it will outperform more complex systems in real-world use.

---

This project focuses on solving the **practical problems of field deployment**, not pushing technical extremes.

> If the device is simple, reliable, and easy to deploy — it will outperform more complex systems in real-world use.
