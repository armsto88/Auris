# PTS810SJG250SMTRLFS — 4.2 × 3.2 mm SMT tactile switch, SPST-NO, 400 gf (service / wake button)

| Field | Value |
|---|---|
| LCSC | C221895 · JLC extended · see `parts.csv` for stock and price (14 712 in stock, 0.29 USD at 50 on 2026-11-17) |
| Manufacturer | C&K |
| Package | SMT, 4.2 × 3.2 mm body (4.6 mm over the J-bend terminals), 2.5 mm high, 4 J-bend terminals · EasyEDA footprint `SW-SMD_4P_PTS810SJM250SMTRLFS` |
| Used by | power: SW201 (LATCH_LOGIC to GND; held until firmware asserts PWR_HOLD) |
| Datasheet | C&K PTS 810 Series catalogue pages B–31/B–32 (2 pages, PDF dated 2017-12) · www.ckswitches.com (local `pdf/C221895_PTS810SJG250SMTRLFS.pdf`) |
| Rated temperature | −40 to +85 °C operating (p. B–31 Environmental); JLC agrees |

## Pins

| Pin | Name | Function (p. B–32 schematic and drawing) | Auris net | Check |
|---|---|---|---|---|
| 1 | 1 | Contact side A; joined inside to pin 2 | LATCH_LOGIC | OK |
| 2 | 2 | Contact side A (top-right terminal) | LATCH_LOGIC | OK |
| 3 | 3 | Contact side B; joined inside to pin 4 | GND | OK |
| 4 | 4 | Contact side B (bottom-right terminal) | GND | OK |

Schematic (p. B–32): 1–2 is one continuous line, 3–4 the other, the contact between them. Drawing: 1 top-left, 2 top-right, 3 bottom-left, 4 bottom-right; the joined pairs run along the 4.2 mm side. The netlist puts LATCH_LOGIC on 1/2 and GND on 3/4, so the switch is across the pairs as intended.

## Limits that matter for Auris

| Parameter | Datasheet (p. B–31) | Auris condition | Verdict |
|---|---|---|---|
| Function | Momentary, 1 make contact (SPST-NO) | Hold to wake | OK |
| Max voltage / current | 16 V DC / 50 mA DC | RAW_BAT ≤ 4.2 V (4.67 V charger OVP with no pack); steady 64–89 µA (RAW_BAT through R228 47 kΩ) | OK steady state; see make current below |
| Contact resistance | ≤ 500 mΩ | — | OK |
| Insulation | ≥ 100 MΩ; dielectric 250 V AC 1 min | LATCH_LOGIC at RAW_BAT in sleep (via R228 and SW202) | ≤ 42 nA at 4.2 V → 2 mV on R228: OK (Q210 leakage margin ≈ 10 µA with 47 kΩ) |
| Bounce | ≤ 10 ms | Press held through boot; C218 with R228 bridges gaps (τ = 47 kΩ × 47 nF = 2.2 ms) | OK |
| Force / travel / life (SJG) | 400 ± 100 gf (blue actuator) / 0.20 ± 0.1 mm / 100 000 operations | Service use through the enclosure | OK; check feel with the enclosure (README) |
| Temperature | −40…+85 °C | −40 °C to hot enclosure | OK up to 85 °C |
| Soldering | IR reflow per IEC 61760-1 | JLC reflow | OK |

## Required external parts and equations

None in the datasheet. Circuit check:

- **Wake current:** pressing pulls LATCH_LOGIC to GND; through SW202 (closed) this pulls SYS_GATE (Q210 gate) low. Steady current = RAW_BAT / R228 = 3.0 V / 47 kΩ = 64 µA to 4.2 V / 47 kΩ = 89 µA. Within 50 mA.
- **Make current into C218:** C218 47 nF sits between SYS_GATE and RAW_BAT with 0 V across it in sleep. SW201 connects it to GND through SW202 only, **without R227** (R227 100 Ω is between WAKE_N and LATCH_LOGIC, so it limits only the 2N7002 path). C218 charges to RAW_BAT through two contact resistances (≤ 0.5 Ω + ≤ 0.13 Ω) and trace inductance: a peak of several amperes for tens of nanoseconds (estimate), Q = 47 nF × 4.2 V = 0.2 µC, E = 0.41 µJ per press. Above the 50 mA DC rating in peak, tiny in energy; dome wear at service-button use is not a concern, but the rating is exceeded on paper.
- Zero-part alternative: connect SW201 pins 1/2 to **WAKE_N** instead of LATCH_LOGIC. Function is identical (WAKE_N → R227 → LATCH_LOGIC → SW202 → SYS_GATE; SW202 open still blocks every wake source), and R227 then limits the make current to 4.2 V / 100 Ω = 42 mA (τ = 4.7 µs), inside the 50 mA rating.

## Layout notes and gotchas

- The latch node is high-impedance in sleep: keep the area under SW201 clean; if the board is conformal-coated, mask the switch.
- Recommended PCB layout (p. B–32): pads at the four corners, 5.2 mm outer / 3.1 mm inner across, 2.8 mm outer / 1.5 mm inner along → 1.05 × 0.65 mm pads. The footprint must sit where the enclosure button or membrane can reach the 2.5 mm-high actuator.

## EasyEDA symbol and footprint

Source: JLCEDA/EasyEDA Official Library, record C221895. Symbol pins 1 and 2 on one side, 3 and 4 on the other (switch drawn between the pairs), names equal numbers. Footprint `SW-SMD_4P_PTS810SJM250SMTRLFS` (the 160 gf variant's name; same body): pad 1 top-left, 2 top-right, 3 bottom-left, 4 bottom-right, as in the C&K drawing. Pads 1.20 × 0.65 mm, 5.35 mm outer / 2.95 mm inner across, 2.82 mm outer / 1.52 mm inner along: slightly longer than C&K's 1.05 mm pads, otherwise identical. Netlist rows SW201 1–4 match by number.

## Findings

| Severity | Designator / pin | Issue | Evidence | Fix |
|---|---|---|---|---|
| note | SW201 pins 1/2 | Make current into C218 47 nF is limited only by contact resistance (peak several A for tens of ns, 0.2 µC, 0.4 µJ per press, estimate) vs the 50 mA DC rating; R227 does not sit in this path | p. B–31 ratings; power-netlist rows R227, SW201, SW202, C218 | Optional, no extra part: move SW201 pins 1/2 from LATCH_LOGIC to WAKE_N, so R227 100 Ω limits the make current to 42 mA. Otherwise accept |
| OK | SW201 | Pinout and internal pairs, −40…+85 °C, 16 V / 50 mA vs 64–89 µA steady, insulation vs latch leakage, footprint | p. B–31, B–32; EasyEDA C221895 | — |
