# Auris part data

One place to look up every part on the four schematic sheets (`audio-frontend`, `power`, `lte`, `mcu`): what it is, where it is used, what it costs at JLCPCB, and what its datasheet says about the way Auris wires it.

| File | Content |
|---|---|
| `parts.csv` | One row per LCSC code across all sheets: MPN, maker, package, designators that use it, JLC basic / extended / preferred, stock, unit price at 1, 10 and 100, datasheet link and the revision read, rated temperature range, date checked |
| `symbol-pins.csv` | The EasyEDA standard-library symbol's pins (number=name) and footprint pad numbers per LCSC code. Source: JLCEDA/EasyEDA Official Library ([lceda.cn](https://lceda.cn/), [easyeda.com](https://easyeda.com)) |
| `sources.csv` | Hand-kept: the manufacturer's datasheet link, the revision actually read and the local PDF name. Overrides the LCSC link in `parts.csv` |
| `<LCSC>_<MPN>.md` | One file for every IC, module, connector, FET, diode, crystal, inductor and polarised part: pin table against the Auris netlist, limits that matter, required external parts and equations, layout notes, symbol/footprint check, findings |
| `pdf/` | Local datasheet cache. Git-ignored (vendor copyright, repo size); `fetch_part_data.py --pdf` re-downloads what `sources.csv` lists |
| `cache/` | Raw JLCPCB and EasyEDA JSON. Git-ignored |

**Refresh** (prices and stock move daily): `python3 hardware/tools/fetch_part_data.py`. It reads the four BOMs, so a part added to a BOM appears on the next run. `--offline` rebuilds from the cache.

**Price columns** are JLCPCB's unit prices for parts bought through its assembly service, in USD. `jlc_class`: `basic` parts are always loaded on the machines; `extended` parts add a feeder-loading fee per unique part per order ($3.07 on Economic PCBA, checked 2026-11-17 on jlcpcb.com/help/article/pcb-assembly-price); `preferred` (extended) parts are exempt from that fee on Economic PCBA.

**Part files** paraphrase the datasheets: facts, numbers and tables with page, table or figure citations, never copied prose. Where no manufacturer PDF could be fetched, the file says so and the facts come from the JLCPCB parameter list and the EasyEDA library record; treat those as unverified.
