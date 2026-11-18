# S2B-PH-SM4-TB(LF)(SN) — JST PH 2-way SMT side-entry header (battery pack)

**Replaced 2026-11-17:** Rev A fits the XYECONN copy XY-S2B-PH-SM4-TB (C54582899, same footprint, −25…+85 °C) at J203 because this part is out of stock at JLC; see `C54582899_XY-S2B-PH-SM4-TB.md`. Deployment units use this genuine JST part (−40…+105 °C).

| Field | Value |
|---|---|
| LCSC | C295747 · JLC extended · see `parts.csv` for stock and price (**0 in stock** on 2026-11-17) |
| Manufacturer | JST |
| Package | PH series, 2.0 mm pitch, SMT side entry, 2 contacts + 2 reinforcement tabs · EasyEDA footprint `CONN-SMD_P2.00_S2B-PH-SM4-TB-LF-SN` |
| Used by | none on the rev A BOM since 2026-11-17: power J203 (BAT_CONN / GND; mates with the FieldMesh Node v4 pack's PHR-2 housing) is the XYECONN copy (C54582899); this genuine part is planned for deployment units (owner decision, review P15) |
| Datasheet | JST "PH connector" catalogue pages ePH (5 pages, PDF dated 2026-01, no revision number) · https://www.jst-mfg.com (local `pdf/ePH.pdf`) |
| Rated temperature | −40 to +105 °C, including temperature rise from current (ePH p.1 Specifications). JLC's "−25 to +85 °C" is out of date |

## Pins

| Pin | Name | Function | Auris net | Check |
|---|---|---|---|---|
| 1 | BAT+ | Circuit No. 1 (marked on the housing, p.4 drawing) | BAT_CONN | OK (FieldMesh pack convention) |
| 2 | BAT− | Circuit No. 2 | GND | OK |
| MP1, MP2 | reinforcement tabs | Tin-plated copper-alloy fixing tabs (p.4) | GND | OK |

JST defines circuit numbering, not polarity. Hobby LiPo packs with PH plugs are wired both ways; the FieldMesh pack is the reference (netlist note "check polarity on every pack batch").

## Limits that matter for Auris

| Parameter | ePH catalogue (p.1 Specifications) | Auris condition | Verdict |
|---|---|---|---|
| Current | 2 A AC/DC with AWG #24 | ≈ 1 A peaks (LTE at 3.0 V), 0.6 A charge | OK if the pack lead is AWG 24; thinner wire lowers the rating (catalogue rates only AWG 24) |
| Voltage | 100 V | 4.2 V | OK |
| Contact resistance | 10 mΩ max initial, 20 mΩ after test | 1 A → ≤ 20 mV per contact | OK |
| Wire range | AWG 32–24, insulation Ø0.5–1.5 mm | pack harness | specify AWG 24 |
| Temperature | −40 to +105 °C | −40 °C to hot enclosure | OK |
| Materials | posts copper alloy, tin-plated; housing PA (heat resistant) (p.4) | — | — |

## Required external parts and equations

None. F202 (PPTC) and Q205 follow on BAT_CONN.

## Layout notes and gotchas

- p.4 drawing: circuit No. 1 is marked on the housing; the EasyEDA footprint has a documentation-layer dot beside pad 1. Add "+" silkscreen at pad 1.
- Keep the reinforcement tabs soldered to large copper for pull strength.

## EasyEDA symbol and footprint

Source: EasyEDA library record C295747. Symbol pins 1, 2, 3, 4. Footprint `CONN-SMD_P2.00_S2B-PH-SM4-TB-LF-SN`: pads 1 (x ≈ 3996.1) and 2 (x ≈ 4003.9), 2.0 mm pitch; tabs 3 and 4 at y + 5.85 mm. Netlist rows 1/2 match by number; MP1/MP2 are mounting pads and the capture gives them the spare symbol pins 3/4 (all on GND). OK. Since 2026-11-17 the netlist names them by number (`J203,3,MP1,GND`, `J203,4,MP2,GND`).

**Alternative in stock:** XYECONN XY-S2B-PH-SM4-TB, C54582899 (2 972 in stock, 0.037 USD at 100). Its EasyEDA record uses the **same footprint** (`CONN-SMD_P2.00_S2B-PH-SM4-TB-LF-SN`, identical pad numbers and coordinates) and the same 4-pin symbol, so it is a drop-in for the PCB. JLC parameters: PH series, 2 A, 250 V, −25 to +85 °C, LCP housing, brass contacts, 8.0 × 7.59 × 5.6 mm (JST per JLC 7.9 × 8.6 × 5.5 mm). Mating with a JST PHR-2 housing is implied by "Reference Series = PH" but not guaranteed by JST, and its temperature rating stops at −25 °C. No datasheet available.

## Findings

| Severity | Designator / pin | Issue | Evidence | Fix | Status |
|---|---|---|---|---|---|
| should fix | J203 (supply) | C295747 is out of stock at JLC | `parts.csv` 2026-11-17 | Prototype: XY-S2B-PH-SM4-TB C54582899 (same footprint). Check mating and retention with the pack's JST PHR-2 plug, including at −25 °C. Deployment: genuine JST (−40 to +105 °C) via consignment or when restocked. power-bom.csv J203: add the alternative in notes | owner decision (review P15, W3: XYECONN copy for rev A, genuine JST for deployment) |
| note | pack harness | 2 A rating holds for AWG 24 wire | ePH p.1 | Ask for AWG 24 leads on the FieldMesh pack | open (pack harness spec) |
| note | parts.csv | JLC lists −25 to +85 °C; JST's current catalogue gives −40 to +105 °C | ePH p.1 | Use JST's figure | no action (C295747 no longer in `parts.csv`) |
| OK | J203 | Pin numbering, footprint, mounting tabs, current, temperature | ePH p.1, p.4 | — | no action |
