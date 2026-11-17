# SM04B-GHS-TB(LF)(SN) — JST GH 4-pin 1.25 mm side-entry SMD header (mic connector)

| Field | Value |
|---|---|
| LCSC | C189895 · JLC extended · see `parts.csv` for stock and price |
| Manufacturer | JST |
| Package | GH series, 4 circuits, side entry, SMD with two reinforcement (solder) tabs · EasyEDA footprint `CONN-SMD_4P-P1.25_SM04B-GHS-TB-LF-SN` |
| Used by | audio: J101; J102 (DNP, mic 2) |
| Datasheet | JST GH connector catalog pages, `eGH.pdf` (no document number or revision printed; PDF dated 2026-04-10) · https://www.jst-mfg.com/product/pdf/eng/eGH.pdf (local `pdf/eGH.pdf`) |
| Rated temperature | −40 to +105 °C including temperature rise from current (eGH p. 1, Specifications). JLC's attribute (−25 to +85 °C, also copied into `parts.csv`) is wrong |

## Pins

| Pin | Name | Function (datasheet) | Auris net | Check |
|---|---|---|---|---|
| 1 | Circuit 1 | Contact (No. 1 circuit marked on the layout drawing, eGH p. 1) | MIC1_OUT_C | OK |
| 2 | Circuit 2 | Contact | MIC1_SRC | OK |
| 3 | Circuit 3 | Contact | MIC1_RET | OK |
| 4 | Circuit 4 | Contact | MIC1_SHLD | OK |
| 5 | Tab | Reinforcement, copper alloy, tin-plated (eGH p. 3); not connected to any contact | — (not in netlist) | Recommend GND, see findings |
| 6 | Tab | Reinforcement | — (not in netlist) | Recommend GND |

Pins 5/6 are the EasyEDA symbol's numbers for the two tabs; JST does not number them.

## Limits that matter for Auris

| Parameter | Datasheet (cite) | Auris condition | Verdict |
|---|---|---|---|
| Temperature | −40…+105 °C (p. 1) | −40 °C to hot enclosure | OK |
| Current / voltage | 1 A (AWG 26), 50 V AC/DC (p. 1) | < 1 mA, ≤ 3.3 V | OK |
| Contact resistance | ≤ 30 mΩ initial, ≤ 50 mΩ after test (p. 1) | µV-level mic signal at ≈ 2.3 kΩ source | OK electrically; see plating note |
| Insulation | ≥ 100 MΩ; 500 V AC withstand for 1 min (p. 1) | — | OK |
| Wire | AWG 30–26, insulation OD 0.76–1.0 mm (p. 1); mating housing GHR-04V-S, contact SSHL-002T-P0.2 (pp. 2–3) | Mic cable choice TBD (README open item) | Shielded mic cable must fit 1.0 mm insulation OD per conductor |
| Contact plating | Tin; gold-plated contacts on request (pp. 2–3) | Outdoor thermal cycling, µV signal | Tin-on-tin is prone to fretting corrosion under vibration/thermal cycling; consider gold-plated contacts or a sealed connector for the acoustic head |

## Required external parts and equations

None. Mic-side wiring: 1 = output (drain), 2 = source (EM273; R113 ties it to return), 3 = return, 4 = shield.

## Layout notes and gotchas

- JST's land drawing is viewed from the mounting surface (p. 1 note 1). The EasyEDA footprint's silkscreen dot sits beside pad 1, consistent with "No. 1 circuit".
- Solder both tabs: they carry the mechanical load of cable pulls.
- Keep R114/R115 and D101/C113 at the connector (README).

## EasyEDA symbol and footprint

Source: JLCEDA/EasyEDA Official Library ([lceda.cn](https://lceda.cn/), [easyeda.com](https://easyeda.com)), record C189895.

- Symbol pins 1–6, named "1"–"6". Netlist rows 1–4 match by number; pins 5 and 6 are not in the netlist and the capture leaves them unconnected (warning only).
- Footprint: signal pads 1–4 in a row at 1.25 mm pitch (4.921 units), 0.6 × 1.7 mm; tab pads 5 (beside pad 4) and 6 (beside pad 1), 1.0 × 2.7 mm. Silkscreen dot and documentation circle at pad 1.

## Findings

| Severity | Designator / pin | Issue | Evidence | Fix |
|---|---|---|---|---|
| should fix | J101.5/6 (J102.5/6) | Mounting tabs have no net, so the capture leaves floating copper beside the µV mic line | EasyEDA C189895 symbol pins 5/6; eGH p. 3 (tabs are separate reinforcement metal) | Recommendation only: add `J101,5,MP1,GND,Y,Mechanical solder tab` and `J101,6,MP2,GND,Y,Mechanical solder tab` (and the same for J102 with fit N). The tabs are not part of the mic return, so tying them to GND does not break the "mic return joins GND only through R114" rule |
| note | C189895 temperature | JLC/`parts.csv` say −25…+85 °C; JST says −40…+105 °C | eGH p. 1 | Correct `parts.csv` temp_min/temp_max to −40/105 |
| note | J101 contacts | Tin-plated contacts on a µV signal outdoors | eGH pp. 2–3 | Decide with the acoustic-head connector choice (README open item); gold-plated GH contacts are available from JST on request |
