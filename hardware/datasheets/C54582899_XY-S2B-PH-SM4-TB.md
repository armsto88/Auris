# XY-S2B-PH-SM4-TB — 2-way 2.0 mm SMT side-entry header, JST PH compatible (battery pack, rev A)

| Field | Value |
|---|---|
| LCSC | C54582899 · JLC extended · see `parts.csv` for stock and price (2 950 in stock, 0.037 USD at 100 on 2026-11-17) |
| Manufacturer | XYECONN (辛译) — a copy of JST S2B-PH-SM4-TB(LF)(SN) |
| Package | SMT right angle, 2 contacts at 2.0 mm + 2 auxiliary solder tabs; JLC: 8.0 (X) × 7.59 (Y) × 5.6 mm (Z) · EasyEDA footprint `CONN-SMD_P2.00_S2B-PH-SM4-TB-LF-SN` (the JST footprint) |
| Used by | power: J203 (BAT_CONN / GND; mates with the FieldMesh Node v4 pack's PHR-2 plug). **Rev A only**; deployment units use genuine JST (C295747) |
| Datasheet | **PDF not read: XYECONN publishes none** (JLC record has no datasheet link). Facts from the JLC parameter list and the EasyEDA record. Reference: JST ePH catalogue (local `pdf/ePH.pdf`, see `C295747_S2B-PH-SM4-TB_LF__SN_.md`) |
| Rated temperature | **−25 to +85 °C** (JLC attribute). Genuine JST PH: −40 to +105 °C including temperature rise (ePH p.1) |

## Pins

| Pin | Name | Function | Auris net | Check |
|---|---|---|---|---|
| 1 | BAT+ | Circuit 1 | BAT_CONN | OK (FieldMesh pack convention; JST defines numbering, not polarity) |
| 2 | BAT− | Circuit 2 | GND | OK |
| MP1, MP2 | — | Auxiliary solder tabs (EasyEDA pads/pins 3, 4) | GND | OK |

## Limits that matter for Auris

| Parameter | JLC record (unverified) | Genuine JST PH (ePH p.1, p.4) | Auris condition | Verdict |
|---|---|---|---|---|
| Current | 2 A | 2 A AC/DC with AWG 24 | ≈ 1 A LTE bursts, 0.6 A charge | OK |
| Voltage | 250 V | 100 V | 4.2 V | OK |
| Contact resistance | not given | ≤ 10 mΩ initial, ≤ 20 mΩ after test | ≤ 20 mV at 1 A (JST) | Unknown for the copy |
| Materials | Brass contacts, tin-plated; LCP housing | Copper-alloy posts, tin-plated; PA housing | — | LCP is the more heat-resistant housing; brass has lower spring properties than JST's copper alloy (retention unknown) |
| Size | 8.0 × 7.59 × 5.6 mm | S2B-PH-SM4-TB: B = 7.9 mm wide, 6 + (2.6) mm deep, 5.5 mm high (ePH p.4) | Same footprint | Depth figure differs by ≈ 1 mm: check tab position on the first article |
| Temperature | −25…+85 °C | −40…+105 °C | −40 °C (Europe), hot enclosure | **Outside at the cold end**: rev A only |

## Required external parts and equations

None. F202 (PPTC) and Q205 follow on BAT_CONN. The 2 A rating is above the ≈ 1 A load; F202's 3.5 A trip is above 2 A (see `C207074_1812L200THPR.md`).

## Layout notes and gotchas

- Same footprint as the JST part, so the PCB stays valid when switching back to genuine JST for deployment.
- Add a "+" silkscreen at pad 1; check polarity on every pack batch (netlist note).
- Solder both tabs to large copper for pull strength; a copy with brass contacts may hold the plug less firmly. Check mating and retention with the pack's JST PHR-2 plug, including at −25 °C (the copy's lowest rating) and after several insertions.

## EasyEDA symbol and footprint

Source: JLCEDA/EasyEDA Official Library, record C54582899. Symbol pins 1, 2 (contacts) and 3, 4 (tabs), names equal numbers; the same 4-pin layout as C295747. Footprint `CONN-SMD_P2.00_S2B-PH-SM4-TB-LF-SN`: **all 18 footprint shapes are identical to C295747's record** (pads 1 and 2: 1.0 × 3.8 mm at 2.0 mm pitch; tabs 3 and 4: 1.5 × 3.4 mm, 6.7 mm apart, 5.85 mm behind the contact pads). Netlist rows 1/2 match by number; MP1/MP2 are mounting rows, which the capture gives to the spare symbol pins 3/4 (both GND). OK.

## Findings

| Severity | Designator / pin | Issue | Evidence | Fix |
|---|---|---|---|---|
| should fix (deployment) | J203 | Rated only −25…+85 °C; units see −40 °C | JLC C54582899 | Already decided: rev A only, genuine JST S2B-PH-SM4-TB (C295747, −40…+105 °C) for deployment units (consignment or when restocked) |
| note | J203 | No datasheet; mating with JST PHR-2, retention force, contact resistance and the exact tab position are unverified; JLC's 7.59 mm depth differs from JST's ≈ 8.6 mm | JLC records C54582899 vs C295747; ePH p.4 | First article: fit check on the footprint, mate/unmate with the pack plug, measure the drop at 1 A (expect ≤ 20 mV) |
| OK | J203 | Pin numbering, footprint identical to JST, current and voltage vs the load | EasyEDA C54582899 = C295747 | — |
