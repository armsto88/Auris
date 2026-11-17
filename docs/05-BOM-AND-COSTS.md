# 05 — Rough BOM and economics

**Cost basis:** User-supplied early engineering BOM; LCSC listed US-dollar unit prices reportedly checked **28 July 2026**; microphone cost is a **working external allowance**. Exception: the RTC row (DS3231MZ+TRL) was re-quoted at LCSC on **22 October 2026** when the selection changed (ADR-002). These are NOT supplier confirmations, production costs or recommended retail prices.

## Major parts

| Block | Proposed part | LCSC | Status | Prototype USD | ~100 units USD |
|---|---|---|---|---:|---:|
| MCU | ESP32-S3-WROOM-1-N16R8 | C2913202 | **SELECTED** | 5.55 | 4.01 |
| RTC | DS3231MZ+TRL | C107410 | **SELECTED** | 3.54 | 2.28 |
| Audio ADC | PCM1863DBTR (reel) | C529569 | CANDIDATE | 5.92\* | 5.58\* |
| LTE | EG800K-EU (Quectel) | C44008839 | **SELECTED** | 6.85‡ | 4.83‡ |
| Microphone | Primo EM273 or equivalent | External | CANDIDATE | 25.00 | 25.00 |
| Charger | CN3791 + TMP390A2 (Node v4 circuit) | C154992 / C5219772 | **SELECTED** | 0.96‡ | 0.55‡ |
| Main 3.3 V | TPS63802DLAR | C2845237 | **SELECTED** | 0.91‡ | 0.58‡ |
| Audio LDO | TPS7A2033PDBVR | C2862740 | CANDIDATE | 0.18 | 0.11 |
| Fuel gauge | MAX17048G+T10 | C2682616 | NOT CHOSEN (ADR-027: ADC divider instead) | – | – |
| MicroSD holder | TF PUSH | C393941 | CANDIDATE | 0.06 | 0.05 |
| Nano-SIM holder | SNO-1303-C | C428450 | CANDIDATE | 0.43 | 0.25 |
| USB-C | HC-TYPE-C-16P-01A | C2894897 | CANDIDATE | 0.08 | 0.07 |
| Main PFET + battery reverse FET (2) | AO3401A | C15127 | **SELECTED** | 0.19‡ | 0.16‡ |
| Wake latch NFETs (3) | 2N7002 (JSCJ) | C8545 | **SELECTED** | 0.05‡ | 0.05‡ |
| LTE FPC antenna | TX4G-FPC-8121 or equivalent | C454897 | CANDIDATE | 0.51 | 0.29 |
| RF connectors (2) | U.FL / IPEX Gen-1 | TBD | CANDIDATE / allowance | 0.12 | 0.12 |
| Always-on LDO | TPL720F33-3TR (+ CR1220 holder C70381) | C2842389 | **SELECTED** | – | 0.09‡ |
| LTE power stage | TPS63020DSJR, 3.9 V | C15483 | **SELECTED** | 0.92‡ | 0.61‡ |
| ESD, magnetics, passives | Mixed | Mixed | **UNPRICED** | TBD | TBD |

## Reported preliminary estimate

| Layer | Prototype USD | ~100 units USD |
|---|---:|---:|
| Sum of priced major parts in source document | **59.40** | **53.72** |
| Included working microphone allowance | **25.00** | **25.00** |
| Practical **electronics** planning range after unpriced support/power | **66–74** | **59–66** |

**Do not calculate profit margin or retail price from the above.** The $66–$74 / $59–$66 estimates exclude substantial manufactured-product costs.

## Excluded costs (from source)

- PCB manufacture, solder assembly, stencil, inspection and test/rework.
- Battery, protection board as needed, solar panel, external wiring.
- MicroSD card, enclosure, acoustic membrane/windscreen, seals, mounting hardware.
- RF tuning/certification, environmental testing, regulatory compliance.
- Factory calibration equipment, labour, traceability and yield losses.
- Logistics, insurance, packaging, returns/warranty, import duties and VAT.
- SIM, data plan, backend/cloud storage/compute/egress and customer support.

## Cost drivers / design levers

1. **Microphone allowance ($25)**: largest individual part in current estimates; affects acoustic noise and calibration credibility.
2. **LTE (~$11.50)**: adds modem, antenna, SIM, power transients, data fees and RF certification.
3. **Audio ADC (~$5.92)**: high supply risk at recorded stock; verify functional equivalents before commitment.
4. **MCU and RTC (~$9.09 prototype)**: the two selections appear disproportionate in a cheap logger but support compute and hard-off scheduling; the RTC re-selection (ADR-002) reduced this line by ~$1.13.
5. **Enclosure and assembly**: currently completely unpriced, potentially decisive in total cost and field reliability.

## Procurement / manufacturing work

- Requote all selected parts with quantity breaks and lifecycle/stock status at purchasing time.
- Resolve EOL, MOQ, alternate footprints, lead times and region-specific module variants.
- Build a **fully burdened COGS** worksheet after schematic and enclosure selection: every SMT/passive/mechanical part, yield/assembly, QA, calibration, warranty and packaging.
- Build separate variable monthly cost model for **data MB/recorder**, cloud storage, retraining GPU jobs and support.
- Instrument battery consumption and solar production before promising site operating expenses or lifetime.

Machine-readable component list is at [`../specs/auris-major-components.csv`](../specs/auris-major-components.csv); it preserves component **status** and source-date metadata.

**Later discussion note:** PCM1863DBTR / LCSC C529569 was identified as an ordering alternative after the preliminary BOM was written. It does **not** change the original quoted cost basis, nor prove current stock or qualification. Revalidate MPN, package, footprint, lifecycle and availability in procurement.

## LCSC orderable codes, checked 2026-10-23

Exact orderable codes, LCSC stock, JLCPCB assembly stock and LCSC USD prices for the main ICs are in [`../specs/lcsc-orderable-2026-10-23.csv`](../specs/lcsc-orderable-2026-10-23.csv). Changes from the July table:

- **Audio ADC:** order the reel version **PCM1863DBTR, C529569** (879 in stock, 2.44 USD at 100). The tube version PCM1863DBT (C1520794) had 1 unit in stock and costs 5.58 USD at 100. \*The July prices above are for the tube version. PCM1862DBTR (C544647) is the same-footprint fallback.
- **N-FETs:** the wake latch uses the JSCJ **2N7002, C8545** (JLCPCB basic, 2.3 M in stock). The audio preamp switch uses the Alpha & Omega original **AO3400A, C20917**, also basic; C5224194 is an ElecSuper copy. Avoid the CBI 2N7002 C51315010 (400 in stock).
- **LTE modem: EG800K-EU (C44008839) chosen** (owner decision 2026-10-23, ADR-006), replacing the global A7670G (C5846957, 12.30 USD) once GSM was ruled out: 7.47 USD less per unit at 100. 151 in stock at LCSC and 179 at JLC, so buy prototype quantity early. The LGA package needs JLC assembly or stencil and reflow. Avoid the EG800K-CN (China bands).
- **Footprint traps:** DS3231M+TRL (SOIC-16), ESP32-S3-WROOM-1U (external antenna) and SN74LVC2G66DCTR (SM8) are listed under similar names but need different footprints from the selected parts.

Stock and prices move daily; re-check before ordering.
- **Power stage (2026-10-23, doc 20):** charger, main 3.3 V, keep-alive LDO, wake latch and modem supply now come from FieldMesh Hub v2 / Node v4 (ADR-003/007/008/010/011); the MAX17048 is dropped for an ADC divider (ADR-027). The full power-sheet BOM is `hardware/power/power-bom.csv`. ‡Rows marked ‡ in the table above show LCSC prices from 2026-10-23, not the July quote. The charger price covers the CN3791 and TMP390A2 only; its FETs, diodes and inductor add about 0.5 USD.

