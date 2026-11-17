# MST-12D18G2 SMD Slide Switch — SPDT side-actuated slide switch (ship-mode switch)

**Replaced 2026-11-17:** SW202 is now ALPS SSSS811101 (C109335, −40…+85 °C, R228 lowered to 47 kΩ for its 50 µA minimum load); see `C109335_SSSS811101.md`. This file keeps the check of the part it replaced.

| Field | Value |
|---|---|
| LCSC | C49023765 · JLC extended · see `parts.csv` for stock and price |
| Manufacturer | Shenzhen Shouhan Technology (首韩科技, SHOU HAN) |
| Package | SMD, body 9.1 × 3.5 mm, 3 terminals at 2.5 mm pitch, 2 Ø0.9 mm plastic posts at 6.8 mm, actuator 2.0 mm · EasyEDA footprint `SW-SMD_3P-L9.1-W3.5-P2.50_MST-12D18G2` |
| Used by | power: SW202 (common SYS_GATE; LATCH_LOGIC in one position, NC in the other: "open = board can never turn on") |
| Datasheet | Shouhan specification for approval MST-12D18G2, 2nd edition, 2022-03-18 (4 pages, with drawing) · manufacturer site not checked (local `pdf/C49023765_MST-12D18G2_SMD_Slide_Switch.pdf`) |
| Rated temperature | −25 to +70 °C (spec §1.2 p.3; drawing table p.1) |

## Pins

| Pin | Name | Function (drawing p.1 circuit: position A joins left + middle, position B joins middle + right) | Auris net | Check |
|---|---|---|---|---|
| 1 | outer | Throw, position A | LATCH_LOGIC | OK |
| 2 | middle | **Common** | SYS_GATE | OK |
| 3 | outer | Throw, position B | NC | OK |

The maker drawing does not number the terminals. EasyEDA numbers them left to right with pad 2 in the middle, so pad 2 is the common, as the netlist assumes.

## Limits that matter for Auris

| Parameter | Datasheet | Auris condition | Verdict |
|---|---|---|---|
| Rating | DC 12 V 0.1 A (p.1 table, §1.1) | ≈ 30–42 µA steady (RAW_BAT through R228 100 kΩ when a wake source pulls), plus the C218 47 nF charge pulse through R227 100 Ω at each wake | OK electrically; very low "dry" current |
| Contact resistance | ≤ 50 mΩ (p.1 table) | — | OK |
| Insulation | ≥ 100 MΩ | open position isolates SYS_GATE (at RAW_BAT) from LATCH_LOGIC | OK |
| Life / force | 10 000 cycles / 200 ± 30 gf | rare use | OK |
| Contacts | beryllium bronze, silver-white plating (p.1 BOM) | µA loads in humid enclosures | silver can tarnish at dry-circuit currents; worth a long-term check |
| Temperature | −25 to +70 °C | −40 °C to hot enclosure | **outside at both ends** |

## Required external parts and equations

None. The switch is in series between WAKE_N (through R227) and SYS_GATE (Q210 gate with R228/C218): with it open no wake source can turn Q210 on.

## Layout notes and gotchas

- Mark the ON (LATCH_LOGIC) side on the silkscreen: the slider position that joins pins 1–2 is ON.
- The two plastic posts need the Ø0.9 mm holes in the footprint (present).

## EasyEDA symbol and footprint

Source: EasyEDA library record C49023765. Symbol pins "1", "2", "3". Footprint `SW-SMD_3P-L9.1-W3.5-P2.50_MST-12D18G2`: pads 1 (x ≈ 3978.9), 2 (≈ 3988.8), 3 (≈ 3998.6) at 2.5 mm, two NPTH holes for the posts, actuator outline on the documentation layer between pads 1 and 2. Pad 2 is the middle terminal = common. Agrees with the netlist (by number).

**Comparison — ALPS SSSS811101, C109335** (ALPS catalogue page SSSS8 series, printed 2017-06-19, local `pdf/C109335_SSSS811101.pdf`): SPDT, 1 pole 2 positions, 1.5 mm travel, 1.4 mm high; −40 to +85 °C; rating 0.3 A 5 V DC max, **50 µA 3 V DC min** (resistive); contact resistance 70 mΩ initial / 130 mΩ after life; 10 000 cycles; cold −40 °C 500 h and dry heat 85 °C 500 h tests. Terminals ①②③ with ② = common (catalogue circuit diagram), but at 3.0 mm (①–②) and 1.5 mm (②–③) spacing, plus 4 ground (frame) terminals. EasyEDA C109335: symbol pins 1–7, footprint `SW-SMD_SSSS811101` with pads 1–3 on that uneven pitch and pads 4–7 for the frame. JLC: 38 595 in stock, 0.12 USD at 100.

## Findings

| Severity | Designator / pin | Issue | Evidence | Fix |
|---|---|---|---|---|
| should fix | SW202 | Rated −25 to +70 °C; units see −40 °C and hot enclosures | spec §1.2 p.3 | power-bom.csv SW202: **SSSS811101, C109335** (ALPS, −40 to +85 °C). Netlist: keep SW202 1 LATCH_LOGIC, 2 SYS_GATE (common), 3 NC, and add `SW202,MP1..MP4,MP,GND` for the frame terminals (the capture maps MP rows onto symbol pins 4–7). Footprint changes |
| note | SW202 with the ALPS part | Steady current through the switch is ≈ 30–42 µA, just under ALPS's 50 µA minimum rated load | ALPS SSSS811101 page 1 (rating min.) | Optional: R228 100 kΩ → 47 kΩ (FRC0402F4702TS, C2906872, already in BOM) gives 64–89 µA while awake and nothing in sleep. Turn-off time constant R228·C218 halves to 2.2 ms. Check with the latch owner |
| OK | SW202 | Common = pin 2, netlist rows, footprint posts | drawing p.1; EasyEDA C49023765 | — |
