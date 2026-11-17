"""Check an EasyEDA Pro project's PCB against the Auris netlist and BOM CSVs.

    python3 hardware/tools/easyeda_check.py path/to/Auris.epro2
    python3 hardware/tools/easyeda_check.py path/to/Auris.epro2 --sheet power

In EasyEDA Pro, update the PCB from the schematic (Design > Update PCB), then
export the project (File > Export > EasyEDA Pro project, .epro2). This reads the
pad nets from the PCB in that file, which is the netlist the board is actually
made from, after EasyEDA has joined nets across schematic pages. For every part
in the sheet CSVs it checks:

  - the part is on the PCB and carries the BOM's LCSC code
  - every netlist pin's pad is on the net the CSV names
  - NC pins are not connected to anything else
  - no other pad of the part is connected

It also lists PCB parts that are in no sheet, such as leftover template parts.
Netlist pins given by name (C127 "+", J301 "C1") are found through the
symbol's pin names. Exits with status 1 if any check fails.
"""
import argparse, json, os, re, sys, zipfile
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from easyeda_capture import HW, SHEETS, read_sheet  # noqa: E402

NC = "NC"


def read_epru(path):
    """Documents in an .epro2 project: [{type, uuid, recs: [(head, body)]}]. Deleted records are dropped."""
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.endswith(".epru")]
        if len(names) != 1:
            sys.exit(f"{path}: expected one .epru file inside, found {names or 'none'}. Is this an .epro2 export?")
        text = z.read(names[0]).decode("utf-8")
    docs, cur = [], None
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        head, sep, body = line.partition("||")
        if not sep:
            sys.exit(f"{path}: line {n} is not a record; the export format may have changed")
        h = json.loads(head)
        body = body.rstrip("|")
        b = json.loads(body) if body else None
        if h["type"] == "DOCHEAD":
            cur = {"type": b["docType"], "uuid": b.get("uuid"), "recs": []}
            docs.append(cur)
        elif b is not None and cur is not None:
            cur["recs"].append((h, b))
    return docs


def index(docs):
    """LCSC code and symbol pin names for each library device, and the PCB parts with their pad nets."""
    symbols = {}
    for d in docs:
        if d["type"] != "SYMBOL":
            continue
        pin_ids = {h["id"] for h, b in d["recs"] if h["type"] == "PIN"}
        attrs = defaultdict(dict)
        for h, b in d["recs"]:
            if h["type"] == "ATTR" and b.get("parentId") in pin_ids:
                attrs[b["parentId"]][b["key"]] = str(b["value"])
        by_name = defaultdict(list)
        for a in attrs.values():
            if "Pin Number" in a:
                by_name[a.get("Pin Name", "")].append(a["Pin Number"])
        symbols[d["uuid"]] = by_name
    devices = {}
    for d in docs:
        if d["type"] == "DEVICE":
            meta = next((b for h, b in d["recs"] if h["type"] == "META"), {})
            a = meta.get("attributes", {})
            devices[d["uuid"]] = {"lcsc": a.get("Supplier Part", ""), "symbol": symbols.get(a.get("Symbol"), {})}

    pcbs = [d for d in docs if d["type"] == "PCB"]
    if not pcbs:
        sys.exit("no PCB in this project: run Design > Update PCB in EasyEDA, then export again")
    pcb = max(pcbs, key=lambda d: sum(h["type"] == "PAD_NET" for h, b in d["recs"]))
    note = f"{len(pcbs)} PCBs in the project; checking the one with the most connected pads" if len(pcbs) > 1 else None
    comps = {h["id"]: {"des": None, "device": None, "pads": {}} for h, b in pcb["recs"] if h["type"] == "COMPONENT"}
    for h, b in pcb["recs"]:
        if h["type"] == "ATTR" and b.get("parentId") in comps and b["key"] in ("Designator", "Device"):
            comps[b["parentId"]]["des" if b["key"] == "Designator" else "device"] = b["value"]
        elif h["type"] == "PAD_NET":
            _, comp_id, pad = json.loads(h["id"])[:3]
            if comp_id in comps and b.get("padNet"):
                comps[comp_id]["pads"][str(pad)] = b["padNet"]
    by_des = defaultdict(list)
    for c in comps.values():
        if c["des"]:
            by_des[c["des"]].append(c)
    net_size = defaultdict(int)
    for c in comps.values():
        for n in c["pads"].values():
            net_size[n] += 1
    return devices, by_des, net_size, note


def check_part(p, cs, devices, net_size):
    errors, info = [], []
    if len(cs) > 1:
        errors.append(f"{len(cs)} parts on the PCB carry this designator")
    c = cs[0]
    dev = devices.get(c["device"], {"lcsc": "", "symbol": {}})
    if p["lcsc"] and dev["lcsc"] != p["lcsc"]:
        errors.append(f"LCSC {dev['lcsc'] or 'none'} on the PCB, BOM says {p['lcsc']}")
    pads, used = c["pads"], set()
    for pin, name, net in p["pins"]:
        pad = pin
        if pin not in pads:   # netlist names the pin, or the pad has no net: look the name up on the symbol
            nums = [n for n in (dev["symbol"].get(name) or dev["symbol"].get(pin) or []) if n not in used]
            # a name on several pads (USB-C GND) is fine when every row with that name has the same net
            one_net = all(r[2] == net for r in p["pins"] if r[1] == name)
            if (len(nums) == 1 or (nums and one_net)) and nums[0] != pin:
                pad = nums[0]
                info.append(f"pin {pin} is pad {pad}")
        got = pads.get(pad)
        used.add(pad)
        if net == NC:
            if got and net_size[got] > 1:
                errors.append(f"pin {pin} should be unconnected but is on {got}")
        elif got is None:
            errors.append(f"pin {pin} ({name}) should be on {net}, but its pad has no net")
        elif got != net:
            errors.append(f"pin {pin} ({name}) is on {got}, netlist says {net}")
    for pad, got in sorted(pads.items()):
        if pad not in used and net_size[got] > 1:
            errors.append(f"pad {pad} is on {got} but not in the netlist")
    return errors, info


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("project", help="EasyEDA Pro project export (.epro2)")
    ap.add_argument("--sheet", choices=list(SHEETS), action="append", help="sheet to check (default: all)")
    ap.add_argument("--hw", default=HW, help=argparse.SUPPRESS)   # folder holding the sheet folders (tests)
    args = ap.parse_args()

    devices, by_des, net_size, note = index(read_epru(args.project))
    if note:
        print(note)
    sheets = args.sheet or list(SHEETS)
    all_spec = set()
    failed = 0
    for sheet in SHEETS:
        part, _ = read_sheet(SHEETS[sheet], args.hw)
        all_spec |= set(part)
        if sheet not in sheets:
            continue
        missing, bad, ok, notes = [], [], 0, []
        for d, p in part.items():
            if d not in by_des:
                missing.append(d)
                continue
            errors, info = check_part(p, by_des[d], devices, net_size)
            if errors:
                bad.append((d, errors))
            else:
                ok += 1
            if info:
                notes.append(f"{d}: {', '.join(info)}")
        print(f"\n{sheet}: {ok} of {len(part)} parts match, {len(bad)} with problems, {len(missing)} not on the PCB")
        if missing:
            print(f"  not on the PCB: {', '.join(missing)}")
        for d, errors in bad:
            for e in errors:
                print(f"  {d}: {e}")
        for n in notes:
            print(f"  note: {n}")
        failed += len(bad) + len(missing)
    if len(sheets) == len(SHEETS):
        extra = sorted(d for d in by_des if d not in all_spec and re.fullmatch(r"[A-Z]+\d+", d))
        if extra:
            print(f"\nOn the PCB but in no sheet: {', '.join(extra)}")
            failed += len(extra)
    print("\nAll checks passed." if not failed else f"\n{failed} problems.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
