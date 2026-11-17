"""Whole-board BOM cost at JLCPCB for N boards, from the four sheet BOMs and the part-data cache.

    python3 hardware/tools/bom_cost.py                 # N = 10 and 100
    python3 hardware/tools/bom_cost.py --n 10 100 --lines
    python3 hardware/tools/bom_cost.py --hw <folder with the four sheet folders>   # e.g. a git worktree

Prices come from hardware/datasheets/cache/jlc/<LCSC>.json (run fetch_part_data.py first); a code
missing from the cache is fetched once. For each fitted line the unit price is the JLC price break
for the order quantity (per-board quantity x N). Extended parts that are not "preferred" add the
Economic PCBA feeder-loading fee once per unique part per order (FEE_EXTENDED, checked 2026-11-17
on jlcpcb.com/help/article/pcb-assembly-price). Test pads and DNP lines cost nothing. Not included:
PCB, setup, stencil and per-joint assembly charges, the microphone capsule, battery, panel, antenna,
SIM and SD card.
"""
import argparse, csv, json, os, sys, urllib.request
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
HW = os.path.dirname(HERE)
CACHE = os.path.join(HW, "datasheets", "cache")
SHEETS = OrderedDict([("audio", "audio-frontend"), ("power", "power"), ("lte", "lte"), ("mcu", "mcu")])
FEE_EXTENDED = 3.07   # USD per unique extended (non-preferred) part per Economic PCBA order
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
SEARCH = "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList"
DETAIL = "https://cart.jlcpcb.com/shoppingCart/smtGood/getComponentDetail?componentCode={}"


def _json(kind, code, url, body=None):
    path = os.path.join(CACHE, kind, f"{code}.json")
    if os.path.exists(path):
        return json.load(open(path))
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, **({"Content-Type": "application/json"} if data else {})})
    d = json.load(urllib.request.urlopen(req, timeout=30))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(d, open(path, "w"), ensure_ascii=False, indent=1)
    return d


def part_info(code):
    """(jlc_class, price breaks, stock) for an LCSC code."""
    det = (_json("jlc", code, DETAIL.format(code)) or {}).get("data") or {}
    hit = next((x for x in ((_json("jlcsearch", code, SEARCH, {"keyword": code, "currentPage": 1, "pageSize": 5})
                             or {}).get("data") or {}).get("componentPageInfo", {}).get("list", []) or []
                if x.get("componentCode") == code), {})
    lib = det.get("componentLibraryType") or hit.get("componentLibraryType")
    cls = {"base": "basic", "expand": "preferred" if hit.get("preferredComponentFlag") else "extended"}.get(lib, "unknown")
    return cls, det.get("prices") or hit.get("componentPrices") or [], det.get("stockCount", hit.get("stockCount", 0))


def price_at(breaks, q):
    best = None
    for b in sorted(breaks, key=lambda b: b["startNumber"]):
        if b["startNumber"] <= q:
            best = b["productPrice"]
    return best if best is not None else (min(breaks, key=lambda b: b["startNumber"])["productPrice"] if breaks else 0.0)


def lines(hw=HW):
    for sheet, stem in SHEETS.items():
        for r in csv.DictReader(open(os.path.join(hw, stem, f"{stem}-bom.csv"))):
            if r["fit"].strip() != "Y" or not r["lcsc"].strip():
                continue
            yield sheet, r["designators"], int(r["qty"]), r["lcsc"].strip(), r["suggested_mpn"]


def cost(n, hw=HW, show=False):
    per_code = OrderedDict()
    for sheet, ds, qty, code, mpn in lines(hw):
        e = per_code.setdefault(code, {"qty": 0, "mpn": mpn, "ds": []})
        e["qty"] += qty
        e["ds"].append(f"{sheet}:{ds}")
    parts, ext = 0.0, []
    for code, e in per_code.items():
        cls, breaks, stock = part_info(code)
        unit = price_at(breaks, e["qty"] * n)
        parts += unit * e["qty"]
        if cls == "extended":
            ext.append(code)
        if show:
            print(f"  {code:>10} {e['mpn'][:24]:24} {cls:9} x{e['qty']:<3} @{unit:.4f} = {unit * e['qty']:.4f}"
                  f"{'  LOW STOCK ' + str(stock) if stock < e['qty'] * n else ''}")
    fee = FEE_EXTENDED * len(ext)
    return {"n": n, "parts": parts, "unique": len(per_code), "extended": len(ext), "fee_order": fee,
            "fee_board": fee / n, "total_board": parts + fee / n}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", type=int, nargs="+", default=[10, 100])
    ap.add_argument("--hw", default=HW)
    ap.add_argument("--lines", action="store_true")
    a = ap.parse_args()
    for n in a.n:
        if a.lines:
            print(f"N = {n}")
        c = cost(n, a.hw, a.lines)
        print(f"N={n:>4}: parts {c['parts']:.2f} USD/board; {c['unique']} unique codes, {c['extended']} extended "
              f"-> fee {c['fee_order']:.2f} USD/order = {c['fee_board']:.2f} USD/board; total {c['total_board']:.2f} USD/board")


if __name__ == "__main__":
    main()
