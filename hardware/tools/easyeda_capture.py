"""Write EasyEDA Pro capture scripts for the Auris schematic sheets.

    python3 hardware/tools/easyeda_capture.py            # all sheets
    python3 hardware/tools/easyeda_capture.py --sheet power

For each sheet this writes hardware/easyeda/capture-<sheet>.js from the sheet's
netlist and BOM CSVs and the BLOCKS table in build_guide.py. Paste a script into
EasyEDA Pro's Advanced > Run Script with that sheet's schematic page open: it
places every part by LCSC code, block by block, and gives each pin a wire stub
named after its net (see the comment at the top of each script). Each block gets
a box and the heading it has in the hardware guide (guide_template.html).

Parts without an LCSC code (test pads, untuned RF parts) are copied from a
template part placed on the page first; the script header says which.
"""
import argparse, ast, csv, datetime, html, json, os, re, sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
HW = os.path.dirname(HERE)
SHEETS = OrderedDict([("audio", "audio-frontend"), ("power", "power"), ("lte", "lte"), ("mcu", "mcu")])

# Blocks and headings for sheets the hardware guide does not draw yet (MCU, storage and USB).
# Move them into build_guide.py's BLOCKS once the guide gets a tab for the sheet.
EXTRA_BLOCKS = OrderedDict([
    ("m_module", ["U401", "C401", "C402", "R401", "C403", "R402", "R417"]),
    ("m_usb", ["J401", "D401", "D402", "R403", "R404", "R405", "R406"]),
    ("m_sd", ["J402", "R418", "R419", "R409", "R410", "R411", "R412", "R413", "Q401", "Q402", "R414", "R415", "C406",
              "C404", "C405"]),
    ("m_led", ["LED401", "R416"]),
    ("m_test", ["TP401", "TP402", "TP403"]),
])
EXTRA_TITLES = {"m_module": "ESP32-S3 module", "m_usb": "USB-C service port",
                "m_sd": "microSD card and card supply", "m_led": "Status LED", "m_test": "Test points"}


def load_blocks():
    """BLOCKS from build_guide.py (read without running the guide build), plus EXTRA_BLOCKS."""
    src = open(os.path.join(HERE, "build_guide.py")).read()
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "BLOCKS" for t in node.targets):
            blocks = eval(compile(ast.Expression(node.value), "build_guide.py", "eval"), {"OrderedDict": OrderedDict})
            clash = set(blocks) & set(EXTRA_BLOCKS)
            if clash:
                sys.exit(f"blocks defined in both build_guide.py and EXTRA_BLOCKS: {sorted(clash)}")
            blocks.update(EXTRA_BLOCKS)
            return blocks
    sys.exit("BLOCKS not found in build_guide.py")


def block_titles():
    """Each block's heading as the hardware guide shows it, e.g. 'Block 6 · Main 3.3 V'."""
    src = open(os.path.join(HERE, "guide_template.html")).read()
    tok = re.compile(r'<div class="eyebrow">(.*?)</div>\s*<h2>(.*?)</h2>|<h3>(.*?)</h3>'
                     r'|<summary>(.*?)</summary>|(</details>)|\{\{parts:(\w+)\}\}', re.S)
    plain = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()
    titles, block, h2, h3, summ = {}, None, None, None, None
    for m in tok.finditer(src):
        eyebrow, head2, head3, summary, end_details, key = m.groups()
        if head2 is not None:
            n = re.search(r"block (\d+)", eyebrow, re.I)
            block, h2, h3, summ = (f"Block {n.group(1)}" if n else None), plain(head2), None, None
        elif head3 is not None:
            h3 = plain(head3)
        elif summary is not None:
            summ = plain(summary)
        elif end_details:
            summ = None
        elif key:
            # numbered blocks use their heading; extras such as test points use their fold-out label
            titles[key] = f"{block} · {h3 or h2}" if block else (summ or h3 or h2)
    return {**titles, **EXTRA_TITLES}


def read_sheet(stem, hw=HW):
    """Parts of one sheet: designator -> {d, lcsc, fit, pins: [[pin, pin_name, net]]}, plus the pin row count."""
    folder = os.path.join(hw, stem)
    net = list(csv.DictReader(open(os.path.join(folder, f"{stem}-netlist.csv"))))
    bom = list(csv.DictReader(open(os.path.join(folder, f"{stem}-bom.csv"))))
    part = {}
    for r in bom:
        for d in r["designators"].split():
            if d in part:
                sys.exit(f"{stem}: {d} is on two BOM lines")
            part[d] = {"d": d, "lcsc": r["lcsc"].strip(), "fit": r["fit"].strip() == "Y", "pins": []}
    for r in net:
        d = r["designator"]
        if d not in part:
            sys.exit(f"{stem}: {d} is in the netlist but not the BOM")
        part[d]["pins"].append([r["pin"].strip(), r["pin_name"].strip(), r["net"].strip()])
    no_pins = [d for d, p in part.items() if not p["pins"]]
    if no_pins:
        sys.exit(f"{stem}: in the BOM but not the netlist: {no_pins}")
    return part, len(net)


def load_sheet(stem, blocks):
    part, n_rows = read_sheet(stem)
    block_of = {d: k for k, ds in blocks.items() for d in ds}
    order = [k for k in blocks if any(d in part for d in blocks[k])]
    unblocked = [d for d in part if d not in block_of]
    if unblocked:   # build_guide.py refuses this too; keep them rather than drop them
        print(f"{stem}: not in any block, placed under 'other': {unblocked}", file=sys.stderr)
        order.append("other")
    parts = []
    for k in order:
        ds = [d for d in blocks.get(k, []) if d in part] if k != "other" else unblocked
        for d in ds:
            p = part[d]
            p["block"] = k
            if not p["lcsc"]:
                p["prefix"] = re.match(r"[A-Z]+", d).group(0)
            parts.append(p)
    titles = block_titles()
    return parts, [[k, titles.get(k, k)] for k in order], n_rows


def template_step(parts):
    need = OrderedDict()
    for p in parts:
        if not p["lcsc"]:
            need.setdefault(p["prefix"], []).append(p["d"])
    if not need:
        return "Nothing to prepare: every part on this sheet has an LCSC code.", []
    kinds = {"TP": "a test pad", "C": "a 0402 capacitor"}
    asks = [f"{kinds.get(pre, 'a ' + pre + ' part')} for {', '.join(ds)}" for pre, ds in need.items()]
    step = ("Optional: place one template part per kind on the page, keeping its default designator: "
            + "; ".join(asks) + ". These parts have no LCSC code, so the script places more of the"
            " template's library part (found by its LCSC code or else by its name), or, with no template"
            " on the page, the default in CFG.templateDefaults. Delete any template afterwards.")
    return step, list(need)


def wrap_comment(text, width=78):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width - 7:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    return "\n//     ".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sheet", choices=list(SHEETS), action="append", help="sheet to write (default: all)")
    ap.add_argument("--out", default=os.path.join(HW, "easyeda"), help="output folder")
    args = ap.parse_args()
    template = open(os.path.join(HERE, "easyeda_capture_template.js")).read()
    blocks = load_blocks()
    os.makedirs(args.out, exist_ok=True)
    for sheet in args.sheet or SHEETS:
        stem = SHEETS[sheet]
        parts, block_list, n_rows = load_sheet(stem, blocks)
        step, prefixes = template_step(parts)
        js = (template
              .replace("__SHEET_JSON__", json.dumps(sheet))
              .replace("__PARTS_JSON__", "[\n" + ",\n".join("    " + json.dumps(p, ensure_ascii=False) for p in parts) + ",\n  ]")
              .replace("__BLOCKS_JSON__", json.dumps(block_list))
              .replace("__PREFIX_JSON__", json.dumps(prefixes))
              .replace("__TEMPLATE_STEP__", wrap_comment(step))
              .replace("__SHEET__", sheet)
              .replace("__NPARTS__", str(len(parts)))
              .replace("__NROWS__", str(n_rows))
              .replace("__DATE__", datetime.date.today().isoformat())
              .replace("__SOURCES__", f"{stem}/{stem}-netlist.csv and {stem}-bom.csv"))
        path = os.path.join(args.out, f"capture-{sheet}.js")
        open(path, "w").write(js)
        print(f"wrote {os.path.relpath(path, os.path.dirname(HW))}: {len(parts)} parts, {n_rows} pin rows,"
              f" {len(block_list)} blocks" + (f", templates needed: {prefixes}" if prefixes else ""))


if __name__ == "__main__":
    main()
