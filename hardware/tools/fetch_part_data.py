"""Build or refresh the Auris part-data index from the four sheet BOMs.

    python3 hardware/tools/fetch_part_data.py            # refresh everything (network)
    python3 hardware/tools/fetch_part_data.py --offline  # rebuild parts.csv from the cache only
    python3 hardware/tools/fetch_part_data.py --pdf      # also fetch manufacturer datasheet PDFs

Writes, under hardware/datasheets/:
  parts.csv        one row per LCSC code across all sheets: MPN, maker, package, which
                   designators use it, JLC basic/extended/preferred, stock, price at 1/10/100,
                   datasheet link and revision, rated temperature range, date checked
  symbol-pins.csv  EasyEDA standard-library symbol pins (number, name) and footprint pad
                   numbers per LCSC code, to check the netlist pin numbers against
  cache/           raw JLCPCB and EasyEDA JSON (git-ignored); --offline rebuilds from it
  pdf/             datasheet PDFs (git-ignored; vendor copyright and repo size)

Sources (no official free API exists; these answer an ordinary browser User-Agent):
  JLCPCB part detail  cart.jlcpcb.com/shoppingCart/smtGood/getComponentDetail?componentCode=C…
  JLCPCB search       jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList
                      (for preferredComponentFlag, which the detail call does not return)
  EasyEDA product     easyeda.com/api/products/C…/components (symbol pins, footprint, part class)

Hand-kept facts live in datasheets/sources.csv (lcsc, datasheet_url, datasheet_rev, pdf):
the manufacturer's own PDF link and the revision actually read. They override the LCSC
link JLC returns. Prices and stock move daily: re-run before ordering.
"""
import argparse, csv, datetime, json, os, re, sys, time, urllib.error, urllib.request
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
HW = os.path.dirname(HERE)
OUT = os.path.join(HW, "datasheets")
CACHE = os.path.join(OUT, "cache")
PDF = os.path.join(OUT, "pdf")
SHEETS = OrderedDict([("audio", "audio-frontend"), ("power", "power"), ("lte", "lte"), ("mcu", "mcu")])
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
JLC_DETAIL = "https://cart.jlcpcb.com/shoppingCart/smtGood/getComponentDetail?componentCode={}"
JLC_SEARCH = "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList"
EE_PRODUCT = "https://easyeda.com/api/products/{}/components?version=6.4.19.5"
COLUMNS = ["lcsc", "mpn", "manufacturer", "package", "used_by", "jlc_class", "stock", "usd_1", "usd_10",
           "usd_100", "datasheet_url", "datasheet_rev", "temp_min", "temp_max", "checked"]


def bom_parts(hw=HW):
    """LCSC code -> {mpn, package, used: {sheet: [designators]}} over all sheets, fitted or not."""
    parts = OrderedDict()
    for sheet, stem in SHEETS.items():
        for r in csv.DictReader(open(os.path.join(hw, stem, f"{stem}-bom.csv"))):
            code = r["lcsc"].strip()
            if not code:
                continue
            p = parts.setdefault(code, {"mpn": r["suggested_mpn"], "package": r["package"], "used": OrderedDict()})
            ds = r["designators"].split()
            if r["fit"].strip() != "Y":
                ds = [d + " (DNP)" for d in ds]
            p["used"].setdefault(sheet, []).extend(ds)
    return parts


def get(url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, "Accept": "application/json",
                                                          **({"Content-Type": "application/json"} if data else {})})
    with urllib.request.urlopen(req, timeout=30) as f:
        return json.load(f)


def cached(kind, code, fetch, offline):
    path = os.path.join(CACHE, kind, f"{code}.json")
    if offline or (os.path.exists(path) and time.time() - os.path.getmtime(path) < 3600):
        return json.load(open(path)) if os.path.exists(path) else None
    try:
        try:
            d = fetch()
        except urllib.error.HTTPError as e:
            if e.code != 403:
                raise
            time.sleep(90)   # easyeda.com rate limit: wait it out once, then retry
            d = fetch()
    except Exception as e:  # keep the last good copy rather than lose the row
        print(f"  {kind} {code}: {e}", file=sys.stderr)
        return json.load(open(path)) if os.path.exists(path) else None
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(d, open(path, "w"), ensure_ascii=False, indent=1)
    time.sleep(6 if kind == "easyeda" else 0.4)   # easyeda.com answers 403 when called faster
    return d


def price_at(breaks, n):
    """Unit price for quantity n from [{startNumber, endNumber, productPrice}]."""
    best = None
    for b in sorted(breaks or [], key=lambda b: b["startNumber"]):
        if b["startNumber"] <= n:
            best = b["productPrice"]
    if best is None and breaks:
        best = min(breaks, key=lambda b: b["startNumber"])["productPrice"]
    return "" if best is None else f"{best:.4f}"


def temp_range(text):
    """'-40℃~+85℃' or '-55℃~+155℃@(TJ)' -> ('-40', '85')."""
    m = re.search(r"(-?\+?\d+(?:\.\d+)?)\s*℃?\s*~\s*(-?\+?\d+(?:\.\d+)?)\s*℃", text or "")
    return (m.group(1).replace("+", ""), m.group(2).replace("+", "")) if m else ("", "")


def symbol_pins(ee):
    """EasyEDA symbol pins [(number, name)] and footprint pad numbers from a product record."""
    pins, pads = [], []
    if not ee or not ee.get("result"):
        return pins, pads
    res = ee["result"]
    shapes = list(res.get("dataStr", {}).get("shape", []))
    for sub in res.get("subparts") or []:   # multi-part symbols (e.g. a dual op-amp) keep pins per sub-part
        shapes += (sub.get("dataStr") or {}).get("shape", [])
    for s in shapes:
        if s.startswith("P~"):
            segs = s.split("^^")
            num = segs[0].split("~")[3]
            name = segs[3].split("~")[4] if len(segs) > 3 and len(segs[3].split("~")) > 4 else ""
            pins.append((num, name))
    for s in (res.get("packageDetail") or {}).get("dataStr", {}).get("shape", []):
        if s.startswith("PAD~"):
            f = s.split("~")
            pads.append(f[8] if len(f) > 8 else "")
    return pins, pads


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--offline", action="store_true", help="use cached JSON only")
    ap.add_argument("--pdf", action="store_true", help="download datasheet PDFs listed in sources.csv")
    args = ap.parse_args()
    today = datetime.date.today().isoformat()
    parts = bom_parts()
    src_path = os.path.join(OUT, "sources.csv")
    sources = {r["lcsc"]: r for r in csv.DictReader(open(src_path))} if os.path.exists(src_path) else {}
    old = {}
    old_path = os.path.join(OUT, "parts.csv")
    if os.path.exists(old_path):
        old = {r["lcsc"]: r for r in csv.DictReader(open(old_path))}
    rows, pin_rows = [], []
    for i, (code, p) in enumerate(parts.items(), 1):
        print(f"[{i}/{len(parts)}] {code} {p['mpn']}", file=sys.stderr)
        det = cached("jlc", code, lambda: get(JLC_DETAIL.format(code)), args.offline)
        srch = cached("jlcsearch", code, lambda: get(JLC_SEARCH, {"keyword": code, "currentPage": 1, "pageSize": 5}),
                      args.offline)
        ee = cached("easyeda", code, lambda: get(EE_PRODUCT.format(code)), args.offline)
        d = (det or {}).get("data") or {}
        hit = next((x for x in ((srch or {}).get("data") or {}).get("componentPageInfo", {}).get("list", []) or []
                    if x.get("componentCode") == code), {})
        lib = d.get("componentLibraryType") or hit.get("componentLibraryType") or ""
        pref = hit.get("preferredComponentFlag")
        jlc_class = {"base": "basic", "expand": "preferred" if pref else "extended"}.get(lib, lib or "unknown")
        attrs = {a["attribute_name_en"]: a["attribute_value_name"] for a in d.get("attributes") or []}
        tmin, tmax = temp_range(attrs.get("Operating Temperature") or d.get("describe", ""))
        breaks = d.get("prices") or hit.get("componentPrices")
        cpara = ((ee or {}).get("result") or {}).get("dataStr", {}).get("head", {}).get("c_para", {})
        s = sources.get(code, {})
        o = old.get(code, {})
        used = "; ".join(f"{sh}: {' '.join(ds)}" for sh, ds in p["used"].items())
        rows.append({
            "lcsc": code,
            "mpn": d.get("componentModelEn") or cpara.get("Manufacturer Part") or p["mpn"],
            "manufacturer": d.get("componentBrandEn") or cpara.get("Manufacturer", ""),
            "package": d.get("componentSpecificationEn") or cpara.get("package") or p["package"],
            "used_by": used,
            "jlc_class": jlc_class,
            "stock": d.get("stockCount", hit.get("stockCount", "")),
            "usd_1": price_at(breaks, 1), "usd_10": price_at(breaks, 10), "usd_100": price_at(breaks, 100),
            "datasheet_url": s.get("datasheet_url") or d.get("dataManualUrl") or o.get("datasheet_url", ""),
            "datasheet_rev": s.get("datasheet_rev") or o.get("datasheet_rev", ""),
            "temp_min": tmin, "temp_max": tmax,
            "checked": today if det else o.get("checked", ""),
        })
        pins, pads = symbol_pins(ee)
        pin_rows.append({"lcsc": code, "mpn": rows[-1]["mpn"],
                         "footprint": ((ee or {}).get("result") or {}).get("packageDetail", {}).get("title", ""),
                         "symbol_pins": " ".join(f"{n}={nm}" for n, nm in pins),
                         "footprint_pads": " ".join(pads)})
        if args.pdf and s.get("datasheet_url") and s.get("pdf"):
            dest = os.path.join(PDF, s["pdf"])
            if not os.path.exists(dest):
                try:
                    req = urllib.request.Request(s["datasheet_url"], headers={"User-Agent": UA})
                    blob = urllib.request.urlopen(req, timeout=60).read()
                    if blob[:4] == b"%PDF":
                        os.makedirs(PDF, exist_ok=True)
                        open(dest, "wb").write(blob)
                    else:
                        print(f"  {code}: {s['datasheet_url']} did not return a PDF", file=sys.stderr)
                except Exception as e:
                    print(f"  {code}: PDF {e}", file=sys.stderr)
    os.makedirs(OUT, exist_ok=True)
    with open(old_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(OUT, "symbol-pins.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["lcsc", "mpn", "footprint", "symbol_pins", "footprint_pads"])
        w.writeheader()
        w.writerows(pin_rows)
    print(f"wrote {len(rows)} parts to {os.path.relpath(old_path, os.path.dirname(HW))}", file=sys.stderr)


if __name__ == "__main__":
    main()
