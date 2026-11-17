# 17 — Source documents, citations and provenance

**Documentation compiled:** 22 October 2026. This is a traceable project handover, not a claim that every idea has been approved.

## Supplied primary sources

| Source | Preserved copy | How interpreted | Limits |
|---|---|---|---|
| Current feature opportunity overview | `../references/Overview.txt` | Detailed product journeys, acoustic/ecoacoustic/noise workflows, optional AI and dashboard direction | Much of the language says *should/could/potential*; not delivered functionality |
| Auris Preliminary Block Diagram and Rough BOM | `../references/Auris_Preliminary_Block_Diagram_and_Rough_BOM.docx` | Selected parts, proposed wake/latch sequence, candidate BOM, cost snapshot and technical unresolved items | Early **pre-schematic** proposal; component costs checked 28 July 2026, not live prices |
| Espressif ESP32-S3-WROOM-1 / -1U datasheet | `../references/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf` | Module memory, I/O/radio/USB electrical capability and module constraints | Module datasheet, not an Auris electrical certification |
| Embedded architecture image from hardware draft | `../assets/auris-v1-preliminary-block-diagram.png` | Visual starting point for power domains, wake, audio and modem | Preliminary diagram; not a validated schematic or correct-by-construction wiring guide |
| OpenELAB, *ESP32-S3 TinyML Guide: Image, Audio & Sensor Models at the Edge* (Aug 2026) | `https://openelab.io/blogs/learn/esp32-s3-tinyml-image-audio-sensor-models` | ESP32-S3 TinyML platform capabilities/limits; findings summarised in `08-EDGE-AI-AND-MODELS.md` | **Vendor blog, not an independent benchmark**; dev-board examples, no Auris-specific measurements; claims require re-verification before use in marketing |
| AURIS project discussions through 22 October 2026 | Discussion history (not a file in the repository) | User decisions and preferences, flagged as distinct from design-file commitments | Conversations may be exploratory and not always formal ADR approvals |

## Later discussion items to preserve without overstating

- The **common core board with separable acoustic front ends** was discussed to avoid making every low-cost recorder pay for ultrasonic performance. The audible recorder is the first priority; any bat/ultrasound variant requires a purpose-built, independently validated audio path.
- The **PCM1863DBTR** (`LCSC C529569`) was identified in a later discussion as a packaging/ordering alternative to the draft's **PCM1863DBT** (`C1520794`). This is **not** evidence that stock is current or that electrical/PCB qualification has passed. BOM remains candidate until confirmed on a new purchase order/design revision.
- Fixed recorder position can be supplied by a commissioning phone; **GNSS is not required on every fixed-site recorder**. GNSS may become relevant for a mobile variant.
- A UV-stabilized polycarbonate, protected/downward acoustic-port enclosure was proposed; **IP66/IP67 is a target to test**, not certified status.
- FieldMesh/backend reuse was explored as an integration opportunity; **do not infer Auris currently runs on FieldMesh, Supabase, or ecoPi infrastructure**.
- Preliminary price targets and completion-cost guesses from July conversations are intentionally kept as **historical scenarios**, not used as a current retail recommendation.

## External manufacturer and competitor references

Product/market examples and their dates are in `02-MARKET-AND-POSITIONING.md`. Treat them as research pointers and recheck live prices, specifications, region, taxes and availability. The manufacturer is the preferred source for final electrical parameters, including module current limits, ADC clock topology, LTE radio bands and charger behavior. Any part selection should cite a specific datasheet version and relevant table/figure in its ADR/PR.

## Traceability / repository hygiene

- Preserve originals byte-for-byte. Do not rewrite the preliminary diagram as if it were a production schematic.
- Put verified schematics, netlists, PCB outputs, measured current profiles, acoustic recordings and test data under versioned engineering artifacts when they exist.
- Prefix untested examples with `example` and mark APIs/configs as **proposed**.
- Record every change in current selection/assumption with date, evidence and decision owner in `14-DECISION-REGISTER.md`.
- Separate observed facts (with source), calculations (with assumptions), accepted decisions, and product hypotheses in pull-request descriptions.
