"""Build hardware/auris-hardware-guide.html: one page, one tab per hardware section.

Run from anywhere after editing specs/lcsc-orderable-*.csv or a sheet's
netlist/BOM (hardware/audio-frontend, hardware/power, hardware/lte):

    python3 hardware/tools/build_guide.py

The newest specs/lcsc-orderable-YYYY-MM-DD.csv is used for part codes. The build
also checks that each sheet's netlist and BOM agree, that no designator is used
on two sheets, that every part is drawn in a block, that the hand-drawn ADC pin
map and sheet-port tables match the netlists, and that every snapshot row
belongs to a known tab; it stops with an error if not.
"""
import argparse, csv, glob, html, json, os, re
from collections import Counter, OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
HW = os.path.dirname(HERE)
REPO = os.path.dirname(HW)
_snaps = sorted(glob.glob(os.path.join(REPO, "specs", "lcsc-orderable-*.csv")))
ap = argparse.ArgumentParser(description="Build the Auris hardware guide.")
ap.add_argument("--src", default=os.path.join(HW, "audio-frontend"), help="folder holding the audio netlist and BOM CSVs")
ap.add_argument("--power", default=os.path.join(HW, "power"), help="folder holding the power netlist and BOM CSVs")
ap.add_argument("--lte", default=os.path.join(HW, "lte"), help="folder holding the LTE netlist and BOM CSVs")
ap.add_argument("--out",default=os.path.join(HW, "auris-hardware-guide.html"))
ap.add_argument("--template", default=os.path.join(HERE, "guide_template.html"))
ap.add_argument("--orderable", default=_snaps[-1] if _snaps else None,
                help="dated LCSC snapshot (default: newest specs/lcsc-orderable-*.csv)")
ap.add_argument("--fragment", action="store_true",
                help="write the page without <html>/<head> wrapper (for publishing as a hosted page)")
args = ap.parse_args()
OUT = args.out
SHEETS = OrderedDict([("audio", (args.src, "audio-frontend")), ("power", (args.power, "power")), ("lte", (args.lte, "lte"))])
NO_NET = {"NC"}   # no-connect marker in the netlists, not a real net


def pretty(v):
    v = v.replace(" Mohm", " MΩ").replace(" kohm", " kΩ").replace(" ohm", " Ω").replace(" uF", " µF")
    return v


value, desc, fit, sheet_of = {}, {}, {}, {}
bom_part = {}   # designator -> exact orderable part from its BOM line
pins = defaultdict(list)
part_note = {}
net_rows, bom_by_sheet = [], OrderedDict()
for sh, (folder, stem) in SHEETS.items():
    s_net = list(csv.DictReader(open(f"{folder}/{stem}-netlist.csv")))
    s_bom = list(csv.DictReader(open(f"{folder}/{stem}-bom.csv")))
    # netlist and BOM must agree before anything is drawn
    seen = Counter()
    for r in s_bom:
        ds = r["designators"].split()
        assert int(r["qty"]) == len(ds), f"{sh}: BOM qty does not match designators: {r['designators']}"
        seen.update(ds)
    assert not [d for d, c in seen.items() if c > 1], f"{sh}: designator listed twice in BOM"
    for r in s_bom:
        for d in r["designators"].split():
            assert d not in fit, f"{d} is used on the {sheet_of[d]} and {sh} sheets"
            value[d], desc[d], fit[d], sheet_of[d] = pretty(r["value"]), r["description"], r["fit"], sh
            bom_part[d] = {"mpn": r["suggested_mpn"], "lcsc": r["lcsc"], "package": r["package"]}
    s_fit = defaultdict(set)
    for r in s_net:
        s_fit[r["designator"]].add(r["fit"])
    assert set(s_fit) == set(seen), f"{sh}: netlist/BOM designators differ: {sorted(set(s_fit) ^ set(seen))}"
    for d, f in s_fit.items():
        assert f == {fit[d]}, f"fit flag for {d} differs between netlist {f} and BOM {fit[d]}"
    for r in s_net:
        r["sheet"] = sh
        pins[r["designator"]].append(r)
        if r["notes"] and r["designator"] not in part_note:
            part_note[r["designator"]] = r["notes"]
    net_rows += s_net
    # every fitted part must be orderable by exact LCSC code (test pads are bare copper)
    no_code = [d for d in seen if fit[d] == "Y" and not d.startswith("TP") and not bom_part[d]["lcsc"]]
    assert not no_code, f"{sh}: fitted parts without an LCSC code: {sorted(no_code)}"
    bom_by_sheet[sh] = s_bom

BLOCKS = OrderedDict([
    ("power", ["U101", "C101", "C102", "FB101"]),
    ("adc", ["U102", "C103", "C104", "C105", "C106", "C107", "C108", "C109", "C110",
             "R108", "R109", "R110", "R111", "R112"]),
    ("clockio", ["Y101", "C111", "C112", "R101", "R102", "R103", "R104", "R105", "R106", "R107"]),
    ("mic", ["J101", "FB102", "C113", "D101", "R113", "R114", "R115", "R116", "C114", "R117",
             "R118", "C115"]),
    ("direct", ["C116", "R119", "C117", "R120", "C118"]),
    ("presupply", ["Q101", "Q102", "R126", "R127", "R128", "R129", "C125", "C126", "R130",
                   "R131", "C127", "C128"]),
    ("preamp", ["C119", "R121", "U103", "R122", "C120", "R123", "C121", "C122", "R124", "C123",
                "R125", "C124", "U104", "C140", "R144", "R145", "R132", "R133", "C129"]),
    ("mic2", ["J102", "FB103", "C135", "D102", "R137", "R138", "R139", "R140", "C136", "R141",
              "C137", "R142", "C138", "R143", "C139", "C131", "R134", "C130", "C132", "R135",
              "C133", "R136", "C134", "U105", "C141", "R146", "R147"]),
    ("test", [f"TP{n}" for n in range(101, 112)]),
    # power sheet
    ("p_solar", ["J201", "J202", "F201", "D201", "Q201", "R201", "D202", "C201", "C202", "C203", "C204",
                 "R238", "R239", "C235", "R240"]),
    ("p_charger", ["U201", "C205", "R204", "R205", "Q202", "D203", "D204", "L201", "R202", "R203", "C206",
                   "LED201", "R206", "LED202", "R207", "C207", "C208", "C209", "C210"]),
    ("p_temp", ["U202", "C211", "C212", "U203", "R208", "R209", "R210", "R211", "R212", "Q203", "R213", "Q204"]),
    ("p_battery", ["J203", "F202", "Q205", "R214", "R215", "U204", "C236", "C214", "C215", "R216", "R217", "C213", "R218"]),
    ("p_rtc", ["U205", "C216", "BT201", "C217", "R219", "R220", "R221"]),
    ("p_latch", ["R222", "Q206", "R223", "Q207", "Q208", "R224", "Q209", "R225", "R226", "R227", "SW201", "SW202",
                 "Q210", "R228", "C218", "C219", "C220", "C221"]),
    ("p_3v3", ["U206", "L202", "R230", "R231", "C222", "C223", "C224", "C225", "C226"]),
    ("p_modem", ["U207", "L203", "R232", "C227", "R233", "R234", "R235", "R236", "R237", "C228", "C229", "C230",
                 "C231", "C232", "C233", "C234", "D205"]),
    ("p_test", [f"TP{n}" for n in range(201, 214)]),
    # LTE sheet
    ("l_supply", ["R301", "C301", "C302", "C303", "C304", "C305", "C306"]),
    ("l_pins", ["U301", "C317", "C318", "C319", "C320", "C321", "C322", "C323"]),
    ("l_ctrl", ["Q301", "R302", "R303", "C316", "U302", "R304", "R305", "C307", "C308", "C309"]),
    ("l_sim", ["J301", "R306", "R307", "R308", "R309", "C310", "C311", "C312", "C313", "D301"]),
    ("l_ant", ["R310", "C314", "C315", "J302"]),
    ("l_test", ["R311"] + [f"TP{n}" for n in range(301, 314)]),
])
assigned = [d for ds in BLOCKS.values() for d in ds]
assert len(assigned) == len(set(assigned)), "part in two blocks"
missing = set(pins) - set(assigned)
assert not missing, f"parts not placed in a block: {sorted(missing)}"
assert set(assigned) <= set(pins), f"unknown parts: {set(assigned) - set(pins)}"
for k, ds in BLOCKS.items():
    assert len({sheet_of[d] for d in ds}) == 1, f"block {k} mixes sheets"

esc = html.escape


# ---------------------------------------------------------------- SVG helpers
class Sch:
    def __init__(self, w, h, label):
        self.w, self.h, self.label, self.e = w, h, label, []
        self.stack = []

    def add(self, s):
        self.e.append(s)

    def dnp(self, on=True):
        if on:
            self.add('<g class="dnp">')
        else:
            self.add("</g>")

    def wire(self, *pts):
        p = " ".join(f"{x},{y}" for x, y in pts)
        self.add(f'<polyline class="w" points="{p}"/>')

    def dot(self, x, y):
        self.add(f'<circle class="dot" cx="{x}" cy="{y}" r="3"/>')

    def text(self, x, y, s, cls, anchor="start"):
        self.add(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{esc(s)}</text>')

    def _labels(self, x, y, o, des, val, side):
        if o == "h":
            self.text(x, y - 12, des, "des", "middle")
            if val:
                self.text(x, y + 21, val, "val", "middle")
        else:
            dx, a = (12, "start") if side == "r" else (-12, "end")
            self.text(x + dx, y - 2, des, "des", a)
            if val:
                self.text(x + dx, y + 12, val, "val", a)

    def res(self, x, y, o, des, val, side="r"):
        if o == "h":
            self.wire((x - 25, y), (x - 15, y)); self.wire((x + 15, y), (x + 25, y))
            self.add(f'<rect class="b" x="{x-15}" y="{y-6}" width="30" height="12"/>')
        else:
            self.wire((x, y - 25), (x, y - 15)); self.wire((x, y + 15), (x, y + 25))
            self.add(f'<rect class="b" x="{x-6}" y="{y-15}" width="12" height="30"/>')
        self._labels(x, y, o, des, val, side)

    def cap(self, x, y, o, des, val, pol=False, side="r"):
        if o == "h":
            self.wire((x - 20, y), (x - 4, y)); self.wire((x + 4, y), (x + 20, y))
            self.add(f'<line class="w plate" x1="{x-4}" y1="{y-10}" x2="{x-4}" y2="{y+10}"/>')
            self.add(f'<line class="w plate" x1="{x+4}" y1="{y-10}" x2="{x+4}" y2="{y+10}"/>')
            if pol:
                self.text(x - 11, y - 6, "+", "val", "middle")
            self.text(x, y - 15, des, "des", "middle")
            if val:
                self.text(x, y + 25, val, "val", "middle")
        else:
            self.wire((x, y - 20), (x, y - 4)); self.wire((x, y + 4), (x, y + 20))
            self.add(f'<line class="w plate" x1="{x-10}" y1="{y-4}" x2="{x+10}" y2="{y-4}"/>')
            self.add(f'<line class="w plate" x1="{x-10}" y1="{y+4}" x2="{x+10}" y2="{y+4}"/>')
            if pol:
                px = x - 15 if side == "r" else x + 15
                self.text(px, y - 6, "+", "val", "middle")
            dx, a = (15, "start") if side == "r" else (-15, "end")
            self.text(x + dx, y - 2, des, "des", a)
            if val:
                self.text(x + dx, y + 12, val, "val", a)

    def bead(self, x, y, o, des, val):
        if o == "h":
            self.wire((x - 25, y), (x - 12, y)); self.wire((x + 12, y), (x + 25, y))
            self.add(f'<rect class="bead" x="{x-12}" y="{y-5}" width="24" height="10"/>')
            self.text(x, y - 11, des, "des", "middle")
            self.text(x, y + 20, val, "val", "middle")
        else:
            self.wire((x, y - 25), (x, y - 12)); self.wire((x, y + 12), (x, y + 25))
            self.add(f'<rect class="bead" x="{x-5}" y="{y-12}" width="10" height="24"/>')
            self.text(x + 12, y - 2, des, "des")
            self.text(x + 12, y + 12, val, "val")

    def tvs(self, x, y, des, val):
        self.wire((x, y - 20), (x, y - 9)); self.wire((x, y + 9), (x, y + 20))
        self.add(f'<polygon class="b" points="{x-6},{y-9} {x+6},{y-9} {x},{y}"/>')
        self.add(f'<polygon class="b" points="{x-6},{y+9} {x+6},{y+9} {x},{y}"/>')
        self.add(f'<line class="w" x1="{x-7}" y1="{y}" x2="{x+7}" y2="{y}"/>')
        self.text(x + 13, y - 2, des, "des")
        self.text(x + 13, y + 12, val, "val")

    def xtal(self, x, y, des, val):
        self.wire((x - 25, y), (x - 12, y)); self.wire((x + 12, y), (x + 25, y))
        for px in (x - 12, x + 12):
            self.add(f'<line class="w plate" x1="{px}" y1="{y-10}" x2="{px}" y2="{y+10}"/>')
        self.add(f'<rect class="b" x="{x-6}" y="{y-12}" width="12" height="24"/>')
        self.text(x, y - 30, des, "des", "middle")
        self.text(x, y - 16, val, "val", "middle")

    def rail(self, x, y, name):
        self.add(f'<line class="w" x1="{x-12}" y1="{y}" x2="{x+12}" y2="{y}"/>')
        self.text(x, y - 6, name, "net", "middle")

    def gnd(self, x, y):
        self.add(f'<line class="w" x1="{x-9}" y1="{y}" x2="{x+9}" y2="{y}"/>')
        self.add(f'<line class="w" x1="{x-6}" y1="{y+4}" x2="{x+6}" y2="{y+4}"/>')
        self.add(f'<line class="w" x1="{x-3}" y1="{y+8}" x2="{x+3}" y2="{y+8}"/>')

    def port(self, x, y, name, side):
        L = 18 + 7 * len(name)
        if side == "l":   # port body to the left, tip touches (x, y)
            pts = [(x - L, y - 9), (x - 8, y - 9), (x, y), (x - 8, y + 9), (x - L, y + 9)]
            tx = x - L + 6
        else:             # port body to the right, signal leaves rightwards
            pts = [(x, y - 9), (x + L - 8, y - 9), (x + L, y), (x + L - 8, y + 9), (x, y + 9)]
            tx = x + 6
        p = " ".join(f"{a},{b}" for a, b in pts)
        self.add(f'<polygon class="port" points="{p}"/>')
        self.text(tx, y + 4, name, "net")

    def svg(self):
        body = "\n".join(self.e)
        return (f'<svg viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{esc(self.label)}">'
                f"{body}</svg>")


# ---------------------------------------------------------------- figures
def fig_overview():
    s = Sch(1000, 330, "Signal flow: mic 1 feeds a direct path and a preamp path into the PCM1863, which streams I2S to the ESP32-S3")
    def box(x, y, w, h, title, sub="", dnp=False):
        s.add(f'<rect class="blk" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/>')
        s.text(x + w / 2, y + (h / 2 if not sub else h / 2 - 5), title, "bt", "middle")
        if sub:
            s.text(x + w / 2, y + h / 2 + 11, sub, "bs2", "middle")
    def arrow(pts, label="", lx=None, ly=None, anchor="middle"):
        p = " ".join(f"{x},{y}" for x, y in pts)
        s.add(f'<polyline class="w" points="{p}" marker-end="url(#ov-arrow)"/>')
        if label:
            s.text(lx, ly, label, "al", anchor)
    s.add('<defs><marker id="ov-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="ah"/></marker></defs>')
    box(20, 30, 110, 40, "VBAT_SW", "switched battery")
    box(190, 30, 200, 40, "U101 LDO 3.3 V", "on while AUDIO_EN is high")
    arrow([(130, 50), (186, 50)])
    arrow([(390, 50), (556, 50)], "AVDD_A / DVDD_A to every block", 473, 42)
    box(560, 30, 140, 40, "all audio parts", "ADC, mic bias, preamp")
    box(20, 150, 100, 50, "J101", "mic 1 connector")
    box(160, 150, 140, 50, "Bias + RF/ESD", "R116, C114, R117")
    arrow([(120, 175), (156, 175)])
    s.wire((300, 175), (330, 175), (330, 125)); s.wire((330, 175), (330, 230))
    arrow([(330, 125), (356, 125)])
    arrow([(330, 230), (356, 230)])
    box(360, 100, 160, 50, "Direct path", "C116 / C117, 47 Ω")
    box(360, 205, 120, 50, "U103A preamp", "+12 dB · PREAMP_EN")
    box(520, 205, 140, 50, "U104 high-pass", "36 / 100 / 1k Hz")
    arrow([(480, 230), (516, 230)])
    box(720, 100, 120, 155, "U102 PCM1863", "ADC + crystal")
    arrow([(520, 125), (716, 125)], "VIN1 · ADC1L", 618, 117)
    arrow([(660, 230), (716, 230)], "VIN3", 690, 222)
    box(880, 100, 100, 155, "ESP32-S3", "I²S slave RX")
    arrow([(840, 150), (876, 150)], "I²S", 858, 142)
    arrow([(880, 205), (844, 205)], "I²C", 862, 197)
    arrow([(780, 255), (780, 290), (590, 290), (590, 259)], "PCM GPIO0/1 → FILT_SEL0/1", 685, 306)
    return s.svg()


def fig_power():
    s = Sch(900, 210, "Audio supply: TPS7A2033 from the switched battery rail, ferrite bead to the ADC digital supply")
    s.port(110, 60, "VBAT_SW", "l")
    s.wire((110, 60), (210, 60)); s.dot(150, 60)
    s.cap(150, 80, "v", "C101", "10 µF"); s.gnd(150, 100)
    s.port(110, 120, "AUDIO_EN", "l"); s.wire((110, 120), (210, 120))
    s.add('<rect class="b" x="210" y="35" width="120" height="100"/>')
    s.text(270, 78, "U101", "des", "middle"); s.text(270, 90, "TPS7A2033", "val", "middle")
    s.text(216, 64, "1 IN", "pin"); s.text(216, 124, "3 EN", "pin")
    s.text(324, 64, "5 OUT", "pin", "end"); s.text(324, 124, "4 NC", "pin", "end")
    s.text(270, 104, "2 GND", "pin", "middle")
    s.wire((270, 135), (270, 155)); s.gnd(270, 155)
    s.wire((330, 60), (720, 60)); s.dot(390, 60); s.dot(470, 60)
    s.wire((390, 60), (390, 75)); s.cap(390, 95, "v", "C102", "10 µF"); s.gnd(390, 115)
    s.text(560, 52, "AVDD_A", "net")
    s.text(560, 78, "→ U102 AVDD (pin 8), mic bias, preamp switch, U104", "note")
    s.wire((470, 60), (470, 160), (485, 160)); s.bead(510, 160, "h", "FB101", "600 Ω @ 100 MHz")
    s.wire((535, 160), (600, 160))
    s.text(560, 152, "DVDD_A", "net")
    s.text(610, 164, "→ U102 DVDD (13), IOVDD (14), I²C pull-ups", "note")
    s.text(20, 155, "AUDIO_EN from ESP32 GPIO7.", "note")
    s.text(20, 169, "U101 has an internal 500 kΩ pull-down,", "note")
    s.text(20, 183, "so audio is off by default.", "note")
    return s.svg()


ADC_PINS = [
    (1, "VINL2/VIN1M", "AIN1M", "R120 47 Ω ← direct path, cold"),
    (2, "VINR2/VIN2M", "AIN2M", "mic 2 direct (DNP)"),
    (3, "VINL1/VIN1P", "AIN1P", "R119 47 Ω ← direct path, hot"),
    (4, "VINR1/VIN2P", "AIN2P", "mic 2 direct (DNP)"),
    (5, "MICBIAS", "PCM_MICBIAS", "unused, TP101 only"),
    (6, "VREF", "PCM_VREF", "C105 1 µF to GND"),
    (7, "AGND", "GND", ""),
    (8, "AVDD", "AVDD_A", "C103 0.1 µF + C104 10 µF to GND"),
    (9, "XO", "PCM_XO", "Y101 crystal, C112 15 pF"),
    (10, "XI", "PCM_XI", "Y101 crystal, C111 15 pF"),
    (11, "LDO", "PCM_LDO", "C106 0.1 µF + C107 10 µF to GND"),
    (12, "DGND", "GND", ""),
    (13, "DVDD", "DVDD_A", "C108 0.1 µF + C109 10 µF to GND"),
    (14, "IOVDD", "DVDD_A", "C110 0.1 µF to GND"),
    (15, "SCKI", "PCM_SCKI", "R101 0 Ω to GND; R102 DNP from AUD_MCLK"),
    (16, "LRCK", "PCM_LRCK", "R104 33 Ω → AUD_LRCK"),
    (17, "BCK", "PCM_BCK", "R103 33 Ω → AUD_BCK"),
    (18, "DOUT", "PCM_DOUT", "R105 33 Ω → AUD_DOUT"),
    (19, "GPIO3/INTC", "AUD_INT", "R108 100 kΩ to GND; R109 DNP → AUD_INT_MCU"),
    (20, "GPIO2/INTB", "PCM_GPIO2", "R110 100 kΩ to GND (unused)"),
    (21, "GPIO1/INTA", "FILT_SEL1", "→ U104 pin 3; R111 100 kΩ to GND"),
    (22, "MISO/GPIO0", "FILT_SEL0", "→ U104 pin 7; R112 100 kΩ to GND"),
    (23, "MOSI/SDA", "AUD_SDA", "R106 4.7 kΩ to DVDD_A"),
    (24, "MC/SCL", "AUD_SCL", "R107 4.7 kΩ to DVDD_A"),
    (25, "MS/AD", "GND", "sets I²C address 0x4A"),
    (26, "MD0", "GND", "selects I²C control"),
    (27, "VINL4/VIN4M", "AIN4M", "mic 2 preamp (DNP)"),
    (28, "VINR4/VIN3M", "AIN3M", "R125 47 Ω ← preamp path, cold"),
    (29, "VINL3/VIN4P", "AIN4P", "mic 2 preamp (DNP)"),
    (30, "VINR3/VIN3P", "AIN3P", "R124 47 Ω ← preamp path, hot"),
]
# cross-check the hand table against the netlist
_u102 = {int(r["pin"]): r["net"] for r in pins["U102"]}
for p, _, n, _ in ADC_PINS:
    assert _u102[p] == n, (p, n, _u102[p])


def fig_adc():
    s = Sch(980, 590, "PCM1863 pin map: every pin with its net and the parts attached to it")
    top, pitch = 62, 34
    x0, x1 = 360, 640
    s.add(f'<rect class="b" x="{x0}" y="{top-26}" width="{x1-x0}" height="{pitch*14+52}"/>')
    s.text((x0 + x1) / 2, top - 8 + pitch * 7, "U102", "des", "middle")
    s.text((x0 + x1) / 2, top + 8 + pitch * 7, "PCM1863DBT", "val", "middle")
    s.text((x0 + x1) / 2, top + 22 + pitch * 7, "TSSOP-30", "val", "middle")
    analog = set(range(1, 9)) | set(range(27, 31))
    for p, name, net, att in ADC_PINS:
        if p <= 15:
            y = top + (p - 1) * pitch
            s.wire((x0 - 30, y), (x0, y))
            s.text(x0 - 26, y - 4, str(p), "pnum")
            s.text(x0 + 6, y + 4, name, "pin")
            cls = "net dim" if "DNP" in att else "net"
            s.text(x0 - 36, y - 1, net, cls, "end")
            if att:
                s.text(x0 - 36, y + 12, att, "note", "end")
        else:
            y = top + (30 - p) * pitch
            s.wire((x1, y), (x1 + 30, y))
            s.text(x1 + 26, y - 4, str(p), "pnum", "end")
            s.text(x1 - 6, y + 4, name, "pin", "end")
            cls = "net dim" if "DNP" in att else "net"
            s.text(x1 + 36, y - 1, net, cls)
            if att:
                s.text(x1 + 36, y + 12, att, "note")
        if p in analog:
            s.add(f'<rect class="an" x="{x0-31 if p<=15 else x1}" y="{y-2}" width="31" height="4"/>')
    s.text((x0 + x1) / 2, top - 10, "coloured stubs = analog pins", "note", "middle")
    return s.svg()


def fig_clockio():
    s = Sch(980, 360, "Crystal, clock fallback, I2S series resistors and I2C pull-ups")
    # crystal
    s.port(100, 70, "XI · pin 10", "l")
    s.wire((100, 70), (145, 70)); s.dot(130, 70)
    s.xtal(170, 70, "Y101", "24.576 MHz")
    s.wire((195, 70), (240, 70)); s.dot(220, 70)
    s.port(240, 70, "XO · pin 9", "r")
    s.wire((130, 70), (130, 90)); s.cap(130, 110, "v", "C111", "15 pF", side="l"); s.gnd(130, 130)
    s.wire((220, 70), (220, 90)); s.cap(220, 110, "v", "C112", "15 pF"); s.gnd(220, 130)
    s.text(175, 160, "Y101 pads 2 and 4 to GND", "note", "middle")
    # SCKI
    s.port(110, 230, "SCKI · pin 15", "l")
    s.wire((110, 230), (180, 230)); s.dot(180, 230)
    s.wire((180, 230), (180, 240)); s.res(180, 265, "v", "R101", "0 Ω", side="l"); s.gnd(180, 290)
    s.dnp(); s.wire((180, 230), (215, 230)); s.res(240, 230, "h", "R102", "0 Ω DNP")
    s.wire((265, 230), (280, 230)); s.port(280, 230, "AUD_MCLK", "r"); s.dnp(False)
    s.text(20, 318, "Fit R102 and remove R101 only for the MCLK fallback.", "note")
    # I2S series resistors
    rows = [(40, "PCM_BCK · 17", "R103", "AUD_BCK", "GPIO15"),
            (95, "PCM_LRCK · 16", "R104", "AUD_LRCK", "GPIO16"),
            (150, "PCM_DOUT · 18", "R105", "AUD_DOUT", "GPIO17")]
    for y, src, rd, port, gpio in rows:
        s.port(620, y, src, "l")
        s.wire((620, y), (655, y)); s.res(680, y, "h", rd, "33 Ω"); s.wire((705, y), (760, y))
        s.port(760, y, port, "r")
        s.text(880, y + 4, f"→ ESP32 {gpio}", "note")
    s.text(690, 185, "Place R103–R105 next to U102.", "note", "middle")
    # I2C pull-ups
    s.text(560, 225, "DVDD_A", "net", "end")
    s.wire((565, 220), (720, 220)); s.dot(620, 220); s.dot(680, 220)
    s.wire((620, 220), (620, 230)); s.res(620, 255, "v", "R106", "4.7 kΩ", side="l")
    s.wire((680, 220), (680, 230)); s.res(680, 255, "v", "R107", "4.7 kΩ")
    s.port(540, 300, "AUD_SDA · 23", "l"); s.wire((540, 300), (800, 300))
    s.wire((620, 280), (620, 300)); s.dot(620, 300)
    s.port(540, 330, "AUD_SCL · 24", "l"); s.wire((540, 330), (800, 330))
    s.wire((680, 280), (680, 330)); s.dot(680, 330)
    s.port(800, 300, "AUD_SDA", "r"); s.port(800, 330, "AUD_SCL", "r")
    s.text(895, 304, "→ GPIO18", "note"); s.text(895, 334, "→ GPIO8", "note")
    return s.svg()


def fig_mic():
    s = Sch(980, 385, "Mic 1 connector, RF and ESD protection, and the filtered bias network")
    s.add('<rect class="b" x="40" y="180" width="70" height="180"/>')
    s.text(75, 172, "J101", "des", "middle")
    for y, n, lab in [(200, 1, "OUT"), (280, 2, "SRC"), (310, 3, "RET"), (340, 4, "SHLD")]:
        s.wire((110, y), (130, y)); s.text(104, y + 4, f"{n} {lab}", "pin", "end")
    # pin 1 path
    s.wire((130, 200), (265, 200)); s.dot(170, 200); s.dot(210, 200)
    s.wire((170, 200), (170, 210)); s.cap(170, 225, "v", "C113", "100 pF", side="l"); s.gnd(170, 245)
    s.wire((210, 200), (210, 205)); s.tvs(210, 225, "D101", "ESD"); s.gnd(210, 245)
    s.text(190, 190, "MIC1_OUT_C", "net", "middle")
    s.bead(290, 200, "h", "FB102", "600 Ω")
    s.wire((315, 200), (930, 200)); s.dot(470, 200); s.dot(660, 200)
    s.text(360, 192, "MIC1_OUT", "net")
    s.text(930, 192, "→ C116 (direct)  ·  C119 (preamp)", "note", "end")
    # pin 2/3/4
    s.wire((130, 280), (175, 280)); s.res(200, 280, "h", "R113", "0 Ω")
    s.wire((225, 280), (260, 280), (260, 310)); s.dot(260, 310)
    s.wire((130, 310), (930, 310)); s.dot(330, 310)
    s.text(400, 302, "MIC1_RET", "net")
    s.text(930, 302, "→ C117 (direct path, cold leg)", "note", "end")
    s.res(330, 335, "v", "R114", "0 Ω  only join to GND"); s.gnd(330, 360)
    s.wire((130, 340), (175, 340)); s.res(200, 340, "h", "R115", "0 Ω")
    s.wire((225, 340), (245, 340)); s.gnd(245, 340)
    # bias chain
    s.rail(470, 25, "AVDD_A"); s.res(470, 50, "v", "R116", "470 Ω thin film")
    s.wire((470, 75), (470, 140)); s.dot(470, 110)
    s.wire((470, 110), (400, 110), (400, 125)); s.cap(400, 145, "v", "C114", "220 µF tant.", pol=True, side="l"); s.gnd(400, 165)
    s.text(478, 104, "MIC1_BIASF", "net")
    s.res(470, 165, "v", "R117", "2.7 kΩ thin film"); s.wire((470, 190), (470, 200))
    # DC sense (DNP)
    s.dnp()
    s.wire((660, 200), (660, 175)); s.res(660, 150, "v", "R118", "1 MΩ DNP")
    s.wire((660, 125), (660, 105)); s.dot(660, 105)
    s.wire((660, 105), (620, 105), (620, 115)); s.cap(620, 135, "v", "C115", "100 nF DNP", side="l"); s.gnd(620, 155)
    s.wire((660, 105), (700, 105)); s.port(700, 105, "MIC1_DC_SENSE", "r")
    s.dnp(False)
    s.text(700, 130, "→ ESP32 GPIO5 (ADC) if fitted", "note")
    return s.svg()


def fig_direct():
    s = Sch(900, 210, "Direct path: pseudo-differential coupling from mic 1 into ADC pins 3 and 1")
    s.port(150, 70, "MIC1_OUT", "l"); s.wire((150, 70), (180, 70))
    s.cap(200, 70, "h", "C116", "0.22 µF C0G"); s.wire((220, 70), (305, 70))
    s.text(262, 62, "AIN1P_C", "net", "middle")
    s.res(330, 70, "h", "R119", "47 Ω"); s.wire((355, 70), (660, 70)); s.dot(560, 70)
    s.port(150, 150, "MIC1_RET", "l"); s.wire((150, 150), (180, 150))
    s.cap(200, 150, "h", "C117", "0.22 µF C0G"); s.wire((220, 150), (305, 150))
    s.text(262, 142, "AIN1M_C", "net", "middle")
    s.res(330, 150, "h", "R120", "47 Ω"); s.wire((355, 150), (660, 150)); s.dot(560, 150)
    s.text(450, 62, "AIN1P", "net", "middle"); s.text(450, 142, "AIN1M", "net", "middle")
    s.wire((560, 70), (560, 90)); s.cap(560, 110, "v", "C118", "470 pF C0G"); s.wire((560, 130), (560, 150))
    s.add('<rect class="b" x="660" y="40" width="150" height="140"/>')
    s.text(666, 74, "3 VIN1P", "pin"); s.text(666, 154, "1 VIN1M", "pin")
    s.text(735, 98, "U102", "des", "middle"); s.text(735, 112, "ADC1L", "val", "middle"); s.text(735, 126, "0x06 = 0x50", "val", "middle")
    s.text(20, 200, "Keep C118 and the 47 Ω pair at the ADC pins; route AIN1P/AIN1M as a coupled pair.", "note")
    return s.svg()


def fig_presupply():
    s = Sch(900, 290, "Preamp supply switch and mid-rail reference")
    s.port(90, 50, "AVDD_A", "l"); s.wire((90, 50), (210, 50)); s.dot(130, 50)
    s.add('<rect class="b" x="210" y="30" width="80" height="60"/>')
    s.text(250, 22, "Q101 AO3401A P-FET", "des", "middle")
    s.text(216, 54, "S", "pin"); s.text(284, 54, "D", "pin", "end"); s.text(250, 86, "G", "pin", "middle")
    s.wire((130, 50), (130, 70)); s.res(130, 95, "v", "R126", "100 kΩ", side="l")
    s.wire((130, 120), (130, 140), (250, 140), (250, 90)); s.dot(250, 140)
    s.text(190, 132, "PRE_GATE", "net", "middle")
    s.wire((250, 140), (250, 170))
    s.add('<rect class="b" x="210" y="170" width="80" height="60"/>')
    s.text(296, 182, "Q102 2N7002 N-FET", "des")
    s.text(250, 184, "D", "pin", "middle"); s.text(216, 204, "G", "pin"); s.text(284, 204, "S", "pin", "end")
    s.wire((290, 200), (320, 200), (320, 215)); s.gnd(320, 215)
    s.port(85, 200, "PREAMP_EN", "l"); s.wire((85, 200), (95, 200)); s.res(120, 200, "h", "R127", "1 kΩ")
    s.wire((145, 200), (210, 200)); s.dot(180, 200)
    s.res(180, 235, "v", "R128", "100 kΩ", side="l"); s.wire((180, 200), (180, 210)); s.gnd(180, 260)
    s.text(20, 282, "PREAMP_EN high → Q102 on → Q101 gate pulled low → preamp powered. Off by default.", "note")
    s.wire((290, 50), (325, 50)); s.res(350, 50, "h", "R129", "10 Ω"); s.wire((375, 50), (800, 50))
    s.dot(430, 50); s.dot(490, 50); s.dot(600, 50)
    s.wire((430, 50), (430, 60)); s.cap(430, 80, "v", "C125", "22 µF", side="l"); s.gnd(430, 100)
    s.wire((490, 50), (490, 60)); s.cap(490, 80, "v", "C126", "0.1 µF"); s.gnd(490, 100)
    s.text(700, 42, "AVDD_PRE", "net"); s.text(700, 68, "→ U103 pin 8 (V+)", "note")
    s.text(490, 125, "C126 at U103 pin 8", "note", "middle")
    s.wire((600, 50), (600, 70)); s.res(600, 95, "v", "R130", "10 kΩ")
    s.wire((600, 120), (600, 160)); s.dot(600, 140)
    s.res(600, 185, "v", "R131", "10 kΩ"); s.gnd(600, 210)
    s.wire((600, 140), (800, 140)); s.dot(680, 140); s.dot(770, 140)
    s.wire((680, 140), (680, 150)); s.cap(680, 170, "v", "C127", "10 µF tant.", pol=True); s.gnd(680, 190)
    s.wire((770, 140), (770, 150)); s.cap(770, 170, "v", "C128", "0.1 µF"); s.gnd(770, 190)
    s.text(805, 136, "VMID_PRE", "net"); s.text(805, 152, "→ R121, R132", "note")
    return s.svg()


def fig_preamp():
    s = Sch(980, 370, "Preamp U103A at +12 dB, coupling into ADC pins 30 and 28, with the switched high-pass across the pair")
    # input
    s.port(84, 170, "MIC1_OUT", "l"); s.wire((84, 170), (90, 170))
    s.cap(110, 170, "h", "C119", "0.22 µF"); s.wire((130, 170), (230, 170)); s.dot(170, 170)
    s.text(195, 162, "PRE1_INP", "net", "middle")
    s.wire((170, 170), (170, 190)); s.res(170, 215, "v", "R121", "100 kΩ", side="l")
    s.wire((170, 240), (170, 250)); s.port(170, 250, "VMID_PRE", "r")
    # op-amp (− on top, + at bottom)
    s.add('<polygon class="b" points="230,100 230,200 310,150"/>')
    s.text(238, 135, "−", "pin"); s.text(238, 175, "+", "pin")
    s.text(222, 126, "2", "pnum", "end"); s.text(222, 166, "3", "pnum", "end"); s.text(318, 144, "1", "pnum")
    s.text(255, 222, "U103A OPA1662", "des", "middle")
    # feedback
    s.wire((230, 130), (210, 130), (210, 70)); s.dot(210, 70); s.dot(235, 70)
    s.wire((210, 70), (255, 70)); s.res(280, 70, "h", "R122", "3.0 kΩ")
    s.wire((305, 70), (340, 70)); s.dot(340, 70)
    s.wire((235, 70), (235, 30), (260, 30)); s.cap(280, 30, "h", "C120", "")
    s.text(325, 22, "100 pF", "val", "start")
    s.wire((300, 30), (340, 30), (340, 150))
    s.text(204, 42, "PRE1_INN", "net", "end")
    s.res(150, 70, "h", "R123", "1.0 kΩ"); s.wire((175, 70), (210, 70))
    s.wire((125, 70), (100, 70)); s.dot(100, 70)
    s.cap(100, 90, "v", "C121", "100 µF tant.", pol=True, side="l"); s.gnd(100, 110)
    s.text(92, 62, "PRE1_CG", "net", "end")
    # output, hot leg
    s.wire((310, 150), (420, 150)); s.dot(340, 150)
    s.text(375, 142, "PRE1_OUT", "net", "middle")
    s.cap(440, 150, "h", "C122", "0.22 µF"); s.wire((460, 150), (615, 150)); s.dot(540, 150); s.dot(590, 150)
    s.text(500, 142, "AIN3P_C", "net", "middle")
    s.res(640, 150, "h", "R124", "47 Ω"); s.wire((665, 150), (800, 150)); s.dot(760, 150)
    s.text(715, 142, "AIN3P", "net", "middle")
    # cold leg
    s.wire((420, 300), (400, 300), (400, 312)); s.gnd(400, 312)
    s.cap(440, 300, "h", "C123", "0.22 µF"); s.wire((460, 300), (615, 300)); s.dot(540, 300); s.dot(590, 300)
    s.text(500, 292, "AIN3M_C", "net", "middle")
    s.res(640, 300, "h", "R125", "47 Ω"); s.wire((665, 300), (800, 300)); s.dot(760, 300)
    s.text(715, 292, "AIN3M", "net", "middle")
    s.wire((760, 150), (760, 205)); s.cap(760, 225, "v", "C124", "470 pF", side="l"); s.wire((760, 245), (760, 300))
    # switched high-pass
    s.add('<rect class="ubox" x="512" y="222" width="104" height="58" rx="3"/>')
    for x, rd, val, ctl, cy in [(540, "R144", "22.6k", "FILT_SEL0", 240), (590, "R145", "1.5k", "FILT_SEL1", 262)]:
        s.wire((x, 150), (x, 160)); s.res(x, 185, "v", rd, val, side="l" if x == 540 else "r")
        s.wire((x, 210), (x, 232))
        s.add(f'<circle class="b" cx="{x}" cy="232" r="2.5"/><circle class="b" cx="{x}" cy="268" r="2.5"/>')
        s.add(f'<line class="w" x1="{x}" y1="268" x2="{x-11}" y2="238"/>')
        s.wire((x, 270), (x, 300))
    s.text(548, 258, "S1", "pin"); s.text(598, 258, "S2", "pin")
    s.text(20, 345, "U104 TS5A23166: S1 = pins 1–2, closed by IN1 (pin 7) ← FILT_SEL0 → 100 Hz.  S2 = pins 5–6, closed by IN2 (pin 3) ← FILT_SEL1 → 1 kHz.", "note")
    s.text(20, 360, "U104 VCC pin 8 = AVDD_A with C140 0.1 µF; GND pin 4.  U103 V+ pin 8 = AVDD_PRE, V− pin 4 = GND.", "note")
    # ADC stub
    s.add('<rect class="b" x="800" y="120" width="160" height="210"/>')
    s.text(806, 154, "30 VIN3P", "pin"); s.text(806, 304, "28 VIN3M", "pin")
    s.text(880, 215, "U102", "des", "middle"); s.text(880, 229, "ADC1R", "val", "middle"); s.text(880, 243, "0x07 = 0x60", "val", "middle")
    return s.svg()


# ---------------------------------------------------------------- tables
def connects(d):
    if len(pins[d]) > 30:   # modules: one line per net, unconnected pads summarised
        by_net = OrderedDict()
        for r in sorted(pins[d], key=lambda r: int(r["pin"]) if r["pin"].isdigit() else 0):
            by_net.setdefault(r["net"], []).append(r)
        out = []
        for net, rs in by_net.items():
            if net in NO_NET:
                continue
            names = sorted({r["pin_name"] for r in rs})
            label = ", ".join(r["pin"] for r in rs) + (" " + names[0] if len(names) == 1 and names[0] != net else "")
            out.append(f'<span class="pinref">{esc(label)}</span> <span class="n">{esc(net)}</span>')
        nc = [r for r in pins[d] if r["net"] in NO_NET]
        out.append(f'<span class="pm">{len(nc)} reserved or unused pads: leave open</span>')
        return '<span class="pinlist">' + "".join(f"<span>{o}</span>" for o in out) + "</span>"
    rows = sorted(pins[d], key=lambda r: (len(r["pin"]), r["pin"]))
    if len(rows) == 2 and all(r["pin"] in ("1", "2", "+", "-") for r in rows):
        a, b = rows
        if a["pin"] == "+" or b["pin"] == "+":
            pos = a if a["pin"] == "+" else b
            neg = b if pos is a else a
            return f'<span class="n">{esc(pos["net"])}</span> <span class="pm">(+)</span> ↔ <span class="n">{esc(neg["net"])}</span>'
        return f'<span class="n">{esc(a["net"])}</span> ↔ <span class="n">{esc(b["net"])}</span>'
    out = []
    for r in sorted(pins[d], key=lambda r: int(r["pin"]) if r["pin"].isdigit() else 0):
        out.append(f'<span class="pinref">{esc(r["pin"])} {esc(r["pin_name"])}</span> <span class="n">{esc(r["net"])}</span>')
    return '<span class="pinlist">' + "".join(f"<span>{o}</span>" for o in out) + "</span>"


def part_table(block):
    rows = []
    for d in BLOCKS[block]:
        dn = fit[d] == "N"
        note = part_note.get(d, "")
        b = bom_part[d]
        ref = f'<td class="ref">{esc(d)}{" <span class=tag>DNP</span>" if dn else ""}</td>'
        part = " · ".join(x for x in (b["mpn"] if b["mpn"] != value[d] else "", b["package"]) if x)
        val = f'{esc(value[d])}<div class="nt">{esc(part)}</div>' if part else esc(value[d])
        if b["lcsc"]:
            lc = f'<td><span class="lc">{esc(b["lcsc"])}</span></td>'
        else:
            lc = '<td class="pm">pad only</td>' if d.startswith("TP") else '<td class="pm">–</td>'
        if len(pins[d]) > 8:
            cells = f'<td class="valc">{val}<div class="nt">{esc(note)}</div></td>{lc}<td colspan="2">{connects(d)}</td>'
        else:
            cells = f'<td class="valc">{val}</td>{lc}<td>{connects(d)}</td><td class="nt">{esc(note)}</td>'
        rows.append(f'<tr class="{"dnp" if dn else ""}">{ref}{cells}</tr>')
    return ('<div class="tw"><table class="parts"><thead><tr><th>Ref</th><th>Value / part</th><th>LCSC</th>'
            '<th>Connects</th><th>Note</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")


MIC2_MAP = [
    ("Connector", "J101", "J102"), ("RF ferrite bead", "FB102", "FB103"), ("RF shunt cap", "C113", "C135"),
    ("ESD diode", "D101", "D102"), ("Source link (2-wire mode)", "R113", "R137"),
    ("Return to GND (only join)", "R114", "R138"), ("Shield to GND", "R115", "R139"),
    ("Bias filter R", "R116", "R140"), ("Bias filter C", "C114", "C136"), ("Load resistor", "R117", "R141"),
    ("Direct coupling, hot", "C116", "C137"), ("Direct series R, hot", "R119", "R142"),
    ("Direct coupling, cold", "C117", "C138"), ("Direct series R, cold", "R120", "R143"),
    ("Direct differential cap", "C118", "C139"), ("Direct ADC pins", "VIN1 · pins 3/1", "VIN2 · pins 4/2"),
    ("Op-amp channel", "U103A · pins 1–3", "U103B · pins 5–7"), ("Preamp input cap", "C119", "C131"),
    ("Preamp input bias", "R121", "R132 (fitted)"), ("Feedback Rf", "R122", "R133 (fitted)"),
    ("Feedback C", "C120", "C129 (fitted)"), ("Rg", "R123", "R134"), ("Cg", "C121", "C130"),
    ("Output coupling, hot", "C122", "C132"), ("Output series R, hot", "R124", "R135"),
    ("Output coupling, cold", "C123", "C133"), ("Output series R, cold", "R125", "R136"),
    ("Output differential cap", "C124", "C134"), ("High-pass switch", "U104", "U105"),
    ("Switch decoupling", "C140", "C141"), ("100 Hz shunt", "R144", "R146"), ("1 kHz shunt", "R145", "R147"),
    ("Preamp ADC pins", "VIN3 · pins 30/28", "VIN4 · pins 29/27"),
]


def mic2_table():
    rows = "".join(f"<tr><td>{esc(a)}</td><td class=ref>{esc(b)}</td><td class=ref>{esc(c)}</td></tr>"
                   for a, b, c in MIC2_MAP)
    return ('<div class="tw"><table class="map"><thead><tr><th>Function</th><th>Mic 1</th>'
            '<th>Mic 2 (DNP)</th></tr></thead><tbody>' + rows + "</tbody></table></div>")


PORTS = [
    ("VBAT_SW", "power in", "—", "Switched battery rail after the main high-side switch"),
    ("AUDIO_EN", "out", "GPIO7", "High = audio domain on"),
    ("PREAMP_EN", "out", "GPIO6", "High = preamp powered"),
    ("AUD_BCK", "in", "GPIO15", "3.072 MHz bit clock from the ADC"),
    ("AUD_LRCK", "in", "GPIO16", "48 kHz word clock from the ADC"),
    ("AUD_DOUT", "in", "GPIO17", "Audio data"),
    ("AUD_SDA", "both", "GPIO18", "I²C1 data; pull-up on this sheet"),
    ("AUD_SCL", "out", "GPIO8", "I²C1 clock; pull-up on this sheet"),
    ("AUD_INT_MCU", "in", "GPIO4", "Only if R109 is fitted"),
    ("AUD_MCLK", "out", "GPIO9", "Only if R102 is fitted (clock fallback)"),
    ("MIC1_DC_SENSE", "analog in", "GPIO5", "Only if R118/C115 are fitted"),
]


POWER_PORTS = [
    ("VBAT_SW", "power out", "—", "Switched battery rail: audio LDO and the two rails below. 2.8–4.2 V"),
    ("3V3", "power out", "—", "Main 3.3 V: ESP32-S3, microSD supply switch, system I²C pull-ups"),
    ("VMODEM", "power out", "—", "3.9 V for the EG810M-EU VBAT pins; off unless MODEM_EN is high"),
    ("PWR_HOLD", "out", "GPIO10", "Drive high first thing at boot; low = power off. R224 holds it low while the ESP32 is unpowered"),
    ("MODEM_EN", "out", "GPIO11", "High = modem rail on. R235 holds it low"),
    ("MODEM_PG", "in", "GPIO12", "High = U207 out of current limit (start-up done); read it only with MODEM_EN high, then wait 30 ms before PWRKEY. R237 1 MΩ pull-up to 3V3"),
    ("ESP_EN", "out", "EN", "U206 power good: holds the ESP32-S3 EN low until 3V3 is above 95 %. Pull-up R401 and C403 on the MCU sheet"),
    ("SYS_SDA", "both", "GPIO13", "System I²C data: RTC at 0x68. 4.7 kΩ pull-up to 3V3 on this sheet"),
    ("SYS_SCL", "out", "GPIO14", "System I²C clock"),
    ("BATT_ADC", "analog in", "GPIO1 (ADC1_CH0)", "VBAT_SW × 0.3125 (R216/R217): 4.2 V reads 1.31 V; use 6 dB attenuation (calibrated range 0–1.6 V, ESP32-S3 datasheet v2.2 Table 5-6). Read before the modem turns on"),
    ("SOLAR_ADC", "analog in", "GPIO2 (ADC1_CH1)", "SOLAR_IN × 0.130 (R238/R239): 7 V reads 0.91 V. 12 dB range (0–2.9 V) covers up to about 22 V"),
    ("VBUS", "power in", "—", "From the USB-C connector; only wakes the board through R225 and Q209"),
]
LTE_PORTS = [
    ("VMODEM", "power in", "—", "3.9 V from U207 on the power sheet, through R301 to the module's VBAT pins"),
    ("3V3", "power in", "—", "ESP32 side of the level shifter (U302 VCCB)"),
    ("LTE_TX", "out", "GPIO39", "ESP32 UART TX → module MAIN_RXD. 115200 baud default"),
    ("LTE_RX", "in", "GPIO40", "Module MAIN_TXD → ESP32 UART RX. Enable the ESP32 pull-up: Hi-Z while the modem is off"),
    ("LTE_RTS", "out", "GPIO41", "ESP32 RTS → module MAIN_RTS (Quectel wires RTS to RTS)"),
    ("LTE_CTS", "in", "GPIO42", "Module MAIN_CTS → ESP32 CTS. Hi-Z while the modem is off"),
    ("LTE_STATUS", "in", "GPIO38", "High = module running. Enable the ESP32 pull-down: Hi-Z, so reads low, while the modem is off"),
    ("LTE_PWRKEY", "out", "GPIO21", "High pulls PWRKEY low through Q301: hold 800 ms to turn on. Keep low otherwise"),
]
for _sh, _ports in (("audio", PORTS), ("power", POWER_PORTS), ("lte", LTE_PORTS)):
    _sheet_nets = {r["net"] for r in net_rows if r["sheet"] == _sh}
    for _p in _ports:
        assert _p[0] in _sheet_nets, f"port {_p[0]} is not a net on the {_sh} sheet"


def ports_table(ports):
    rows = "".join(f"<tr><td class=n>{esc(a)}</td><td>{esc(b)}</td><td class=ref>{esc(c)}</td><td>{esc(d)}</td></tr>"
                   for a, b, c, d in ports)
    return ('<div class="tw"><table class="map"><thead><tr><th>Signal</th><th>Direction (ESP32 view)</th>'
            '<th>Proposed pin</th><th>Notes</th></tr></thead><tbody>' + rows + "</tbody></table></div>")


STATUS_LABEL = {"SELECTED_CONCEPT": "Selected (concept)", "CANDIDATE": "Candidate", "PROPOSED": "Proposed",
                "NOT_CHOSEN": "Not chosen", "FALLBACK": "Fallback", "ALTERNATE": "Alternate", "TBD": "To decide"}
SECTIONS = OrderedDict([("power", "Power"), ("mcu", "MCU"), ("rtc", "RTC & wake"), ("audio", "Audio front end"),
                        ("lte", "LTE"), ("io", "Storage & USB")])
COUNTED = {"SELECTED_CONCEPT", "CANDIDATE", "PROPOSED"}

assert args.orderable, "no specs/lcsc-orderable-*.csv found"
SNAP_PATH = os.path.normpath(args.orderable)
SNAP_DATE = (re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(SNAP_PATH)) or [None, "undated"])[1]
snap = list(csv.DictReader(open(SNAP_PATH)))
for r in snap:
    assert r["section"] in SECTIONS, f"unknown section {r['section']!r} in {SNAP_PATH}"
    assert r["status"] in STATUS_LABEL, f"unknown status {r['status']!r} in {SNAP_PATH}"


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _money(v):
    n = _num(v)
    return "–" if n is None else (f"{n:.2f}" if n >= 1 else f"{n:.3f}")


def comp_rows(rows, group=False, compact=False):
    """Parts table. compact drops the USD @1 and JLC library columns (used on the overview tab)."""
    out, last = [], None
    for r in rows:
        if group and r["section"] != last:
            last = r["section"]
            out.append(f'<tr class="grp"><td colspan="{7 if compact else 9}"><a href="#{last}">{esc(SECTIONS[last])}</a></td></tr>')
        off = r["status"] == "NOT_CHOSEN"
        tbd = r["status"] == "TBD"
        st_cls = "st sel" if r["status"] == "SELECTED_CONCEPT" else ("st tbd" if tbd else "st")
        ls, js = _num(r["lcsc_stock"]), _num(r["jlc_stock"])
        best = max([x for x in (ls, js) if x is not None], default=None)
        low = best is not None and best < 300
        stock = "–" if (ls is None and js is None) else f'{r["lcsc_stock"] or "–"} / {r["jlc_stock"] or "–"}'
        lc = f'<span class="lc">{esc(r["lcsc"])}</span>' if r["lcsc"] else '<span class="pm">not at LCSC</span>' if r["mpn"] != "TBD" else '<span class="pm">–</span>'
        tag = " <span class=tag>NOT CHOSEN</span>" if off else ""
        usd1 = "" if compact else f'<td class="num">{_money(r["usd_1"])}</td>'
        lib = "" if compact else f'<td>{esc(r["jlc_library"] or "–")}</td>'
        out.append(
            f'<tr class="{"dnp" if off else ""}"><td>{esc(r["role"])}</td><td class="valc">{esc(r["mpn"])}{tag}</td>'
            f'<td>{lc}</td><td class="num{" low" if low else ""}">{esc(stock)}</td>{usd1}'
            f'<td class="num">{_money(r["usd_100"])}</td>{lib}'
            f'<td><span class="{st_cls}">{esc(STATUS_LABEL[r["status"]])}</span></td><td class="nt">{esc(r["notes"])}</td></tr>')
    head = ('<th>Part</th><th>Part number</th><th>LCSC</th><th class="num">Stock LCSC / JLC</th>'
            + ("" if compact else '<th class="num">USD @1</th>') + '<th class="num">USD @100</th>'
            + ("" if compact else "<th>JLC library</th>") + "<th>Status</th><th>Notes</th>")
    return '<div class="tw"><table><thead><tr>' + head + "</tr></thead><tbody>" + "".join(out) + "</tbody></table></div>"


def comp_table(section):
    return comp_rows([r for r in snap if r["section"] == section])


def all_comp_table():
    order = list(SECTIONS)
    return comp_rows(sorted(snap, key=lambda r: order.index(r["section"])), group=True, compact=True)


counted = [r for r in snap if r["status"] in COUNTED]
def _qty(role):
    m = re.search(r"\(x(\d+)\)", role)
    return int(m.group(1)) if m else 1


COST = sum((_num(r["usd_100"]) or 0) * _qty(r["role"]) for r in counted)
TBD_ROLES = [r["role"] for r in snap if r["status"] == "TBD"]
_stocked = [(max(x for x in (_num(r["lcsc_stock"]), _num(r["jlc_stock"])) if x is not None), r["mpn"])
            for r in counted if r["lcsc"] and (_num(r["lcsc_stock"]) is not None or _num(r["jlc_stock"]) is not None)]
LOW = min(_stocked) if _stocked else (None, "–")


def blk(s, x, y, w, h, title, note=None, code=None, tbd=False):
    s.add(f'<rect class="blk{" tbd" if tbd else ""}" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/>')
    lines = [(title, "bt")] + ([(note, "bs2")] if note else []) + ([(code, "bs")] if code else [])
    y0 = y + h / 2 - (len(lines) - 1) * 7 + 4
    for i, (t, c) in enumerate(lines):
        s.text(x + w / 2, y0 + i * 14, t, c, "middle")


def arrow(s, pts, mid, cls="w", label=None, lx=None, ly=None, anchor="middle"):
    p = " ".join(f"{a},{b}" for a, b in pts)
    s.add(f'<polyline class="{cls}" points="{p}" marker-end="url(#{mid})"/>')
    if label:
        s.text(lx, ly, label, "al", anchor)


def fig_sys():
    s = Sch(1000, 390, "Board overview: the ESP32-S3 connects to the RTC, power sheet, microSD, audio front end, LTE modem and USB")
    blk(s, 400, 140, 200, 90, "ESP32-S3-WROOM-1", "N16R2 · MCU + Wi-Fi setup", "C2913205")
    for (y, t, n, c) in [(40, "RTC DS3231MZ+TRL", "always powered", "C107410"),
                         (157, "Power sheet", "battery + panel sense · PWR_HOLD", None),
                         (274, "microSD holder", "raw WAV + manifest", "C393941")]:
        blk(s, 60, y, 220, 56, t, n, c)
    for (y, t, n, c) in [(40, "Audio front end", "PCM1863DBTR + EM272", "C529569"),
                         (157, "LTE modem EG810M-EU", "daily sync · Europe, AU, NZ", "C20421924"),
                         (274, "USB-C", "programming + service", "C2894897")]:
        blk(s, 720, y, 220, 56, t, n, c)
    s.wire((400, 165), (330, 165), (330, 68), (280, 68)); s.text(365, 158, "I²C · INT", "al", "middle")
    s.wire((280, 185), (400, 185)); s.text(340, 178, "ADC · GPIO", "al", "middle")
    s.wire((400, 205), (330, 205), (330, 302), (280, 302)); s.text(365, 222, "SD bus", "al", "middle")
    s.wire((600, 165), (670, 165), (670, 68), (720, 68)); s.text(635, 158, "I²S · I²C", "al", "middle")
    s.wire((600, 185), (720, 185)); s.text(660, 178, "UART · PWRKEY", "al", "middle")
    s.wire((600, 205), (670, 205), (670, 302), (720, 302)); s.text(635, 222, "USB", "al", "middle")
    s.text(500, 356, "Power: solar → CN3791 charger (TMP390A2 cut-out) → 1S2P battery → AO3401A main switch →", "note", "middle")
    s.text(500, 372, "TPS63802 3.3 V, TPS7A2033 audio and TPS63020 3.9 V modem rails. TPL720F33 keeps the RTC alive. See the Power tab.", "note", "middle")
    return s.svg()


def fig_powertree():
    s = Sch(1000, 240, "Power tree: solar charger with temperature cut-out, battery, keep-alive rail for the RTC, and switched rails behind the main switch")
    s.add('<defs><marker id="pt-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="ah"/></marker></defs>')
    blk(s, 20, 60, 130, 50, "Solar panel", "Vmp ≈ 6 V · about 3 W")
    blk(s, 20, 150, 130, 50, "TMP390A2 cut-out", "panel-powered", "C5219772")
    blk(s, 190, 65, 150, 60, "CN3791 charger", "MPPT ≈ 6 V · 600 mA", "C154992")
    blk(s, 390, 70, 150, 50, "Battery 1S2P", "Node v4 pack · ~5.2 Ah")
    blk(s, 590, 70, 150, 50, "Main switch", "AO3401A", "C15127")
    blk(s, 800, 20, 190, 44, "TPS63802 3.3 V", "MCU, microSD", "C2845237")
    blk(s, 800, 80, 190, 44, "TPS7A2033 audio 3.3 V", "EN = AUDIO_EN", "C2862740")
    blk(s, 800, 140, 190, 44, "TPS63020 modem 3.9 V", "EG810M-EU · EN from MCU", "C15483")
    blk(s, 190, 175, 150, 50, "Battery sense", "divider → BATT_ADC")
    blk(s, 390, 175, 150, 50, "Keep-alive LDO 3.3 V", "TPL720F33", "C2842389")
    blk(s, 610, 175, 150, 50, "RTC + wake logic", "DS3231MZ · BR1220 backup", "C107410")
    m = "pt-arrow"
    arrow(s, [(150, 85), (186, 85)], m)
    arrow(s, [(150, 175), (170, 175), (170, 113), (186, 113)], m, cls="wd", label="clamps", lx=172, ly=150, anchor="start")
    arrow(s, [(340, 95), (386, 95)], m)
    arrow(s, [(540, 95), (586, 95)], m, label="VBAT", lx=563, ly=88)
    s.wire((740, 95), (770, 95)); s.dot(770, 95)
    s.wire((770, 42), (770, 162))
    for y in (42, 102, 162):
        arrow(s, [(770, y), (796, y)], m)
    s.text(770, 32, "VBAT_SW", "al", "middle")
    arrow(s, [(420, 120), (420, 150), (265, 150), (265, 171)], m, cls="wd", label="measures", lx=340, ly=145)
    arrow(s, [(465, 120), (465, 171)], m)
    arrow(s, [(540, 200), (606, 200)], m, label="KEEP_ALIVE", lx=573, ly=193)
    arrow(s, [(685, 175), (685, 124)], m, label="wake · PWR_HOLD", lx=678, ly=152, anchor="end")
    return s.svg()


# ---------------------------------------------------------------- power sheet drawings
def ic(s, x, y, w, h, des, val, pins):
    """IC body with pin stubs. pins: (side l/r/t/b, offset, number, name). Returns {number: stub end}."""
    s.add(f'<rect class="b" x="{x}" y="{y}" width="{w}" height="{h}"/>')
    s.text(x + w / 2, y + h / 2 - 2, des, "des", "middle")
    s.text(x + w / 2, y + h / 2 + 12, val, "val", "middle")
    ends = {}
    for side, pos, num, name in pins:
        if side == "l":
            py = y + pos; e = (x - 20, py); s.wire(e, (x, py))
            s.text(x - 3, py - 3, num, "pnum", "end"); s.text(x + 5, py + 4, name, "pin")
        elif side == "r":
            px, py = x + w, y + pos; e = (px + 20, py); s.wire((px, py), e)
            s.text(px + 3, py - 3, num, "pnum"); s.text(px - 5, py + 4, name, "pin", "end")
        elif side == "t":
            px = x + pos; e = (px, y - 20); s.wire(e, (px, y))
            s.text(px + 3, y - 8, num, "pnum"); s.text(px, y + 14, name, "pin", "middle")
        else:
            px, py = x + pos, y + h; e = (px, py + 20); s.wire((px, py), e)
            s.text(px + 3, py + 15, num, "pnum"); s.text(px, py - 6, name, "pin", "middle")
        ends[num] = e
    return ends


def tbox(s, x, y, w, h, title, labels, title_y=None):
    """Small transistor/switch box with pin letters inside."""
    s.add(f'<rect class="b" x="{x}" y="{y}" width="{w}" height="{h}"/>')
    if title:
        s.text(x + w / 2, y - 6 if title_y is None else title_y, title, "des", "middle")
    for lx, ly, t, a in labels:
        s.text(lx, ly, t, "pin", a)


def diode_h(s, x, y, des, val):
    """Anode left (x-25), cathode right (x+25)."""
    s.wire((x - 25, y), (x - 7, y)); s.wire((x + 7, y), (x + 25, y))
    s.add(f'<polygon class="b" points="{x-7},{y-7} {x-7},{y+7} {x+7},{y}"/>')
    s.add(f'<line class="w" x1="{x+7}" y1="{y-7}" x2="{x+7}" y2="{y+7}"/>')
    s.text(x, y - 12, des, "des", "middle")
    if val:
        s.text(x, y + 21, val, "val", "middle")


def diode_v(s, x, y, des, val, side="r", zener=False):
    """Cathode at the top (y-25), anode at the bottom (y+25)."""
    s.wire((x, y - 25), (x, y - 7)); s.wire((x, y + 7), (x, y + 25))
    s.add(f'<polygon class="b" points="{x-7},{y+7} {x+7},{y+7} {x},{y-7}"/>')
    s.add(f'<line class="w" x1="{x-7}" y1="{y-7}" x2="{x+7}" y2="{y-7}"/>')
    if zener:
        s.add(f'<polyline class="w" points="{x-10},{y-4} {x-7},{y-7}"/>')
        s.add(f'<polyline class="w" points="{x+7},{y-7} {x+10},{y-10}"/>')
    dx, a = (13, "start") if side == "r" else (-13, "end")
    s.text(x + dx, y - 2, des, "des", a)
    if val:
        s.text(x + dx, y + 12, val, "val", a)


def ind_h(s, x, y, des, val, above=False):
    """above=True puts value beside the designator, for inductors drawn just above an IC's pins."""
    s.wire((x - 25, y), (x - 16, y)); s.wire((x + 16, y), (x + 25, y))
    s.add(f'<path class="w" d="M{x-16},{y} a4,4 0 0 1 8,0 a4,4 0 0 1 8,0 a4,4 0 0 1 8,0 a4,4 0 0 1 8,0"/>')
    if above:
        s.text(x - 3, y - 10, des, "des", "end"); s.text(x + 3, y - 10, val, "val")
        return
    s.text(x, y - 10, des, "des", "middle")
    if val:
        s.text(x, y + 18, val, "val", "middle")


def cell(s, x, y):
    """Coin cell, + at top (y), - at bottom (y+6)."""
    s.add(f'<line class="w plate" x1="{x-12}" y1="{y}" x2="{x+12}" y2="{y}"/>')
    s.add(f'<line class="w plate" x1="{x-6}" y1="{y+6}" x2="{x+6}" y2="{y+6}"/>')


def fig_p_panel():
    s = Sch(1000, 250, "Panel input: two panel connectors, fuse, TVS and reverse-polarity switch feeding SOLAR_IN")
    for (y, name, note) in [(30, "J201", "integrated"), (120, "J202", "external")]:
        s.add(f'<rect class="b" x="20" y="{y}" width="64" height="50"/>')
        s.text(52, y - 6, name, "des", "middle"); s.text(52, y + 64, note, "note", "middle")
        s.text(78, y + 19, "+", "pin", "end"); s.text(78, y + 39, "−", "pin", "end")
        s.wire((84, y + 15), (120, y + 15))
        s.wire((84, y + 35), (100, y + 35)); s.gnd(100, y + 35)
    s.wire((120, 45), (120, 135)); s.dot(120, 90)
    s.text(124, 38, "PANEL_IN", "net")
    s.wire((120, 90), (155, 90)); s.res(180, 90, "h", "F201", "1.1 A 24 V")
    s.wire((205, 90), (300, 90)); s.dot(240, 90)
    s.text(208, 82, "PANEL_FUSED", "net")
    s.wire((240, 90), (240, 100)); s.tvs(240, 120, "D201", "SMF12CA"); s.gnd(240, 140)
    tbox(s, 300, 65, 80, 50, "Q201 AO3401A", [(306, 94, "D", "start"), (374, 94, "S", "end"), (340, 111, "G", "middle")])
    s.wire((340, 115), (340, 160)); s.dot(340, 160)
    s.res(340, 185, "v", "R201", "22 kΩ", side="l"); s.gnd(340, 210)
    s.wire((380, 90), (640, 90)); s.dot(420, 90); s.dot(480, 90); s.dot(560, 90)
    s.wire((420, 90), (420, 100)); diode_v(s, 420, 125, "D202", "8.2 V", side="l", zener=True)
    s.wire((420, 150), (420, 160), (340, 160))
    s.wire((480, 90), (480, 95)); s.cap(480, 115, "v", "C201", "47 µF", pol=True); s.gnd(480, 135)
    s.wire((560, 90), (560, 95)); s.cap(560, 115, "v", "C203", "10 µF"); s.gnd(560, 135)
    s.text(600, 82, "SOLAR_IN", "net")
    s.text(650, 94, "→ U201 VCC, U202 IN, R204, R213, R238", "note")
    s.text(650, 108, "also C202 4.7 µF, C204 100 nF; R238/R239 panel sense", "note")
    s.text(20, 240, "Q201's body diode starts the circuit with a correctly wired panel and blocks a reversed one; D202 limits its gate voltage.", "note")
    return s.svg()


def fig_p_charger():
    s = Sch(1060, 380, "CN3791 buck solar charger: MPPT divider, switching FET, series and catch diodes, inductor and current-sense resistor")
    e = ic(s, 300, 40, 170, 200, "U201", "CN3791", [
        ("l", 30, "1", "VG"), ("l", 70, "9", "VCC"), ("l", 150, "6", "MPPT"),
        ("r", 30, "10", "DRV"), ("r", 120, "8", "CSP"), ("r", 160, "7", "BAT"),
        ("b", 40, "5", "COM"), ("b", 90, "3", "CHRG"), ("b", 120, "4", "DONE"), ("b", 150, "2", "GND")])
    s.port(160, 110, "SOLAR_IN", "l")
    s.wire((160, 110), e["9"]); s.dot(200, 110); s.dot(250, 110)
    s.wire(e["1"], (250, 70)); s.cap(250, 90, "v", "C205", "100 nF", side="l")
    s.res(200, 135, "v", "R204", "402 kΩ", side="l")
    s.wire((200, 160), (200, 190)); s.dot(200, 190); s.wire((200, 190), e["6"])
    s.text(240, 183, "MPPT", "net", "middle")
    s.res(200, 215, "v", "R205", "100 kΩ", side="l"); s.gnd(200, 240)
    s.wire((200, 190), (150, 190)); s.text(146, 194, "Q204 cut-out clamp", "note", "end")
    s.res(340, 285, "v", "R203", "120 Ω", side="l"); s.cap(340, 330, "v", "C206", "220 nF", side="l"); s.gnd(340, 350)
    s.gnd(450, 260)
    s.text(395, 300, "CHRG, DONE → LED201/LED202", "note")
    s.text(395, 314, "via 2.2 kΩ; anodes on SOLAR_IN", "note")
    tbox(s, 560, 10, 80, 50, "", [(566, 39, "S", "start"), (634, 39, "D", "end"), (600, 56, "G", "middle")])
    s.text(600, 98, "Q202 AO3401A", "des", "middle")
    s.wire(e["10"], (520, 70), (520, 80), (600, 80), (600, 60))
    s.wire((560, 35), (536, 35)); s.text(532, 39, "SOLAR_IN", "net", "end")
    s.wire((640, 35), (665, 35)); diode_h(s, 690, 35, "D203", "PMEG4010")
    s.wire((715, 35), (775, 35)); s.dot(740, 35)
    s.text(745, 27, "CHG_SW", "net", "middle")
    s.wire((740, 35), (740, 55)); diode_v(s, 740, 80, "D204", "PMEG4010"); s.gnd(740, 105)
    ind_h(s, 800, 35, "L201", "47 µH")
    s.wire((825, 35), (860, 35), (860, 165)); s.dot(860, 160)
    s.text(868, 100, "CHARGE_SENSE", "net")
    s.wire(e["8"], (860, 160))
    s.res(860, 190, "v", "R202", "0.200 Ω"); s.wire((860, 215), (860, 230)); s.dot(860, 230)
    s.wire(e["7"], (540, 200), (540, 230), (900, 230))
    s.port(900, 230, "RAW_BAT", "r")
    s.text(560, 262, "R202 sets 600 mA (120 mV / 0.2 Ω). Kelvin-route CSP and BAT to its pads.", "note")
    s.text(560, 276, "Output caps on RAW_BAT: C207 10 µF electrolytic, C208 4.7 µF, C209 10 µF, C210 100 nF.", "note")
    return s.svg()


def fig_p_temp():
    s = Sch(1000, 340, "Charge temperature cut-out: panel-powered HT7533 and TMP390A2 clamp the CN3791 MPPT pin outside 0 to 42 °C")
    e1 = ic(s, 110, 80, 110, 70, "U202", "HT7533-1", [("l", 35, "2", "IN"), ("r", 35, "3", "OUT"), ("b", 55, "1", "GND")])
    s.port(90, 115, "SOLAR_IN", "l"); s.gnd(165, 170)
    s.wire(e1["3"], (300, 115), (300, 30), (445, 30)); s.dot(270, 115)
    s.wire((270, 115), (270, 125)); s.cap(270, 145, "v", "C211", "10 µF"); s.gnd(270, 165)
    s.text(306, 24, "TEMP_3V3", "net")
    e2 = ic(s, 380, 70, 160, 130, "U203", "TMP390A2", [
        ("t", 65, "5", "VDD"), ("r", 40, "6", "OUTA"), ("r", 90, "4", "OUTB"),
        ("b", 20, "1", "SETA"), ("b", 70, "2", "SETB"), ("b", 130, "3", "GND")])
    s.wire((445, 30), e2["5"])
    s.res(400, 245, "v", "R208", "2.49 kΩ", side="l"); s.gnd(400, 270)
    s.res(450, 245, "v", "R209", "18.7 kΩ"); s.gnd(450, 270)
    s.gnd(510, 220)
    s.wire(e2["6"], (590, 110), (590, 160)); s.wire(e2["4"], (590, 160)); s.dot(590, 135)
    s.wire((590, 135), (675, 135)); s.dot(640, 135)
    s.text(594, 152, "TEMP_FAULT_N", "net")
    s.wire((640, 135), (640, 115)); s.res(640, 90, "v", "R210", "10 kΩ"); s.rail(640, 65, "TEMP_3V3")
    s.res(700, 135, "h", "R211", "47 kΩ"); s.wire((725, 135), (770, 135)); s.dot(750, 135)
    s.wire((750, 135), (750, 145)); s.res(750, 170, "v", "R212", "100 kΩ", side="l"); s.gnd(750, 195)
    tbox(s, 770, 110, 56, 50, "Q203", [(775, 139, "B", "start"), (798, 124, "C", "middle"), (798, 156, "E", "middle")], title_y=200)
    s.wire((798, 160), (798, 175)); s.gnd(798, 175)
    s.wire((798, 110), (798, 70)); s.dot(798, 70)
    s.res(798, 45, "v", "R213", "100 kΩ"); s.rail(798, 20, "SOLAR_IN")
    s.text(806, 82, "TEMP_CLAMP", "net")
    s.wire((798, 70), (880, 70), (880, 135), (890, 135))
    tbox(s, 890, 110, 56, 50, "Q204", [(895, 139, "B", "start"), (918, 124, "C", "middle"), (918, 156, "E", "middle")], title_y=200)
    s.wire((918, 160), (918, 175)); s.gnd(918, 175)
    s.wire((918, 110), (918, 90), (965, 90)); s.text(968, 94, "MPPT", "net")
    s.text(20, 300, "R208 sets the hot trip at +42 °C (reset +37 °C). R209 sets the cold trip at +5 °C (reset +10 °C); TMP390 accuracy is ±2.5 °C.", "note")
    s.text(20, 314, "Temperature OK: TMP390 outputs open → Q203 on → TEMP_CLAMP low → Q204 off → charging allowed.", "note")
    s.text(20, 328, "Too cold or too hot, or no TEMP_3V3: Q203 off → R213 turns Q204 on → MPPT pulled low → no charging.", "note")
    return s.svg()


def fig_p_battery():
    s = Sch(1000, 250, "Battery connection, keep-alive LDO and battery-voltage sense")
    s.add('<rect class="b" x="20" y="40" width="64" height="60"/>')
    s.text(52, 34, "J203", "des", "middle"); s.text(80, 59, "BAT+", "pin", "end"); s.text(80, 89, "BAT−", "pin", "end")
    s.text(52, 116, "1S2P pack", "note", "middle")
    s.wire((84, 55), (130, 55)); s.wire((84, 85), (100, 85)); s.gnd(100, 85)
    s.res(155, 55, "h", "F202", "2.0 A PPTC")
    s.wire((180, 55), (260, 55)); s.text(190, 47, "BAT_FUSED", "net")
    tbox(s, 260, 30, 80, 50, "Q205 AO3401A", [(266, 59, "D", "start"), (334, 59, "S", "end"), (300, 76, "G", "middle")])
    s.wire((300, 80), (300, 110)); s.dot(300, 110)
    s.res(300, 135, "v", "R214", "100 kΩ", side="l"); s.gnd(300, 160)
    s.dnp(); s.wire((300, 110), (370, 110), (370, 100)); s.res(370, 75, "v", "R215", "DNP"); s.wire((370, 50), (370, 55)); s.dnp(False)
    s.wire((340, 55), (600, 55)); s.dot(370, 55); s.dot(450, 55)
    s.text(460, 47, "RAW_BAT", "net")
    s.text(605, 59, "→ main switch Q210, CN3791 BAT", "note")
    e = ic(s, 430, 120, 140, 60, "U204", "TPL720F33", [("t", 20, "3", "IN"), ("r", 30, "2", "OUT"), ("b", 70, "1", "GND")])
    s.wire((450, 55), e["3"]); s.gnd(500, 200)
    s.wire(e["2"], (640, 150)); s.dot(610, 150)
    s.wire((610, 150), (610, 160)); s.cap(610, 180, "v", "C214", "10 µF"); s.gnd(610, 200)
    s.port(640, 150, "KEEP_ALIVE", "r")
    s.rail(860, 30, "VBAT_SW"); s.res(860, 55, "v", "R216", "220 kΩ")
    s.wire((860, 80), (860, 95)); s.dot(860, 95)
    s.res(860, 120, "v", "R217", "100 kΩ"); s.gnd(860, 145)
    s.wire((860, 95), (940, 95)); s.cap(940, 115, "v", "C213", "100 nF"); s.gnd(940, 135)
    s.text(868, 88, "BATT_SENSE", "net")
    s.text(780, 180, "R218 2.2 kΩ → BATT_ADC (MCU).", "note")
    s.text(780, 194, "On the switched rail: no sleep drain.", "note")
    s.text(20, 230, "Keep-alive: 1.4 µA quiescent, feeds the RTC and wake latch only. Q205 does not block a reversed pack while the panel is live:", "note")
    s.text(20, 244, "use the keyed connector and check polarity on every battery batch.", "note")
    return s.svg()


def fig_p_latch():
    s = Sch(1000, 370, "RTC with coin-cell backup and the wake latch: RTC alarm, PWR_HOLD, USB or the button turn on the main P-FET")
    e = ic(s, 60, 100, 150, 140, "U205", "DS3231MZ+TRL", [
        ("l", 30, "2", "VCC"), ("l", 110, "6", "VBAT"), ("r", 30, "3", "INT"), ("r", 80, "7", "SDA"), ("r", 110, "8", "SCL"),
        ("b", 75, "5", "GND")])
    s.wire(e["2"], (40, 70)); s.rail(40, 70, "KEEP_ALIVE")
    s.wire(e["6"], (25, 210), (25, 232)); cell(s, 25, 232); s.text(40, 228, "+", "val"); s.wire((25, 238), (25, 246)); s.gnd(25, 246)
    s.text(12, 272, "BT201 CR1220", "note")
    s.gnd(135, 260)
    s.wire(e["7"], (270, 180)); s.text(274, 184, "SYS_SDA", "net")
    s.wire(e["8"], (270, 210)); s.text(274, 214, "SYS_SCL", "net")
    s.text(232, 236, "4.7 kΩ pull-ups to 3V3", "note")
    s.wire(e["3"], (300, 130)); s.dot(260, 130)
    s.text(234, 146, "RTC_INT_N", "net")
    s.wire((260, 130), (260, 115)); s.res(260, 90, "v", "R219", "1 MΩ"); s.rail(260, 65, "KEEP_ALIVE")
    s.res(325, 130, "h", "R222", "1 MΩ"); s.wire((350, 130), (360, 130))
    tbox(s, 360, 105, 56, 50, "", [(365, 134, "B", "start"), (388, 119, "C", "middle"), (388, 151, "E", "middle")])
    s.text(380, 176, "Q206", "des", "end")
    s.wire((388, 155), (388, 180)); s.gnd(388, 180)
    s.wire((388, 105), (388, 85), (455, 85)); s.dot(430, 85)
    s.wire((430, 85), (430, 80)); s.res(430, 55, "v", "R223", "1 MΩ"); s.rail(430, 30, "KEEP_ALIVE")
    s.text(460, 120, "RTC_WAKE", "net")
    s.wire((455, 85), (455, 185), (470, 185))
    for x, des in [(470, "Q207"), (570, "Q208"), (670, "Q209")]:
        tbox(s, x, 160, 60, 50, des + " 2N7002", [(x + 6, 189, "G", "start"), (x + 30, 174, "D", "middle"), (x + 30, 206, "S", "middle")], title_y=246)
        s.wire((x + 30, 210), (x + 30, 220)); s.gnd(x + 30, 220)
        s.wire((x + 30, 160), (x + 30, 140))
    s.wire((570, 185), (556, 185), (556, 255)); s.text(556, 270, "PWR_HOLD", "net", "middle")
    s.text(556, 284, "R224 to GND", "note", "middle")
    s.wire((670, 185), (656, 185), (656, 255)); s.text(656, 270, "USB_WAKE", "net", "middle")
    s.text(656, 284, "R225 from VBUS", "note", "middle"); s.text(656, 298, "R226 to GND", "note", "middle")
    s.wire((500, 140), (760, 140)); s.dot(600, 140); s.dot(700, 140)
    s.text(615, 133, "WAKE_N", "net")
    s.res(785, 140, "h", "R227", "100 Ω"); s.wire((810, 140), (840, 140)); s.dot(840, 140)
    s.text(846, 158, "LATCH_LOGIC", "net")
    s.wire((840, 140), (840, 170)); s.add('<rect class="b" x="832" y="170" width="16" height="10"/>')
    s.wire((840, 180), (840, 190)); s.gnd(840, 190)
    s.text(852, 184, "SW201", "des")
    s.wire((840, 140), (840, 110), (860, 110))
    s.add('<rect class="ubox" x="860" y="98" width="60" height="24" rx="2"/>'); s.text(890, 92, "SW202 ship mode", "des", "middle")
    s.wire((920, 110), (950, 110), (950, 303), (920, 303))
    s.text(944, 220, "SYS_GATE", "net", "end")
    tbox(s, 840, 280, 80, 46, "Q210 AO3401A", [(846, 307, "S", "start"), (914, 307, "G", "end"), (880, 322, "D", "middle")], title_y=274)
    s.wire((840, 303), (815, 303)); s.text(811, 307, "RAW_BAT", "net", "end")
    s.wire((880, 326), (880, 345), (930, 345)); s.text(934, 349, "VBAT_SW", "net")
    s.text(700, 330, "R228 47 kΩ + C218 47 nF from SYS_GATE to RAW_BAT:", "note", "end")
    s.text(700, 344, "main switch off by default (turn-on is fast: no soft start). C219 470 µF on VBAT_SW.", "note", "end")
    return s.svg()


def fig_p_rails():
    s = Sch(1020, 320, "Switched rails: TPS63802 main 3.3 V and TPS63020 3.9 V modem supply, both fed from VBAT_SW")
    e = ic(s, 120, 60, 150, 170, "U206", "TPS63802", [
        ("l", 30, "10", "VIN"), ("l", 70, "1", "EN"), ("l", 110, "2", "MODE"), ("l", 140, "3", "AGND"),
        ("t", 50, "9", "L1"), ("t", 100, "7", "L2"), ("r", 30, "6", "VOUT"), ("r", 115, "4", "FB"), ("b", 75, "8", "GND"), ("b", 120, "5", "PG")])
    s.port(80, 90, "VBAT_SW", "l"); s.wire((80, 90), e["10"]); s.wire((90, 90), (90, 130), e["1"]); s.dot(90, 90)
    s.wire(e["2"], (90, 170), (90, 200)); s.wire(e["3"], (90, 200)); s.gnd(90, 200)
    s.gnd(195, 250)
    s.wire(e["9"], (170, 25)); ind_h(s, 195, 25, "L202", "0.47 µH", above=True); s.wire((220, 25), e["7"])
    s.wire(e["6"], (370, 90)); s.dot(330, 90)
    s.port(370, 90, "3V3", "r")
    s.wire((330, 90), (330, 115)); s.res(330, 140, "v", "R230", "510 kΩ"); s.wire((330, 165), (330, 175)); s.dot(330, 175)
    s.wire(e["4"], (330, 175))
    s.text(240, 266, "ESP_EN (MCU)", "net", "middle")
    s.res(330, 200, "v", "R231", "91 kΩ"); s.gnd(330, 225)
    e2 = ic(s, 560, 60, 170, 190, "U207", "TPS63020", [
        ("l", 25, "10/11", "VIN"), ("l", 55, "1", "VINA"), ("l", 95, "13", "PS"), ("l", 135, "12", "EN"), ("l", 165, "2", "GND"),
        ("t", 50, "8/9", "L1"), ("t", 120, "6/7", "L2"), ("r", 30, "4/5", "VOUT"), ("r", 90, "3", "FB"), ("r", 140, "14", "PG"), ("b", 85, "EP", "PGND")])
    s.port(520, 85, "VBAT_SW", "l"); s.wire((520, 85), e2["10/11"]); s.wire((530, 85), (530, 115), e2["1"]); s.dot(530, 85)
    s.wire(e2["13"], (528, 155)); s.text(524, 159, "M_PS", "net", "end")
    s.port(455, 195, "MODEM_EN", "l"); s.wire((455, 195), (480, 195)); s.dot(468, 195)
    s.res(505, 195, "h", "R234", "100 Ω"); s.wire((530, 195), e2["12"])
    s.res(468, 220, "v", "R235", "100 kΩ", side="l"); s.gnd(468, 245)
    s.gnd(540, 225)
    s.gnd(645, 270)
    s.wire(e2["8/9"], (610, 25), (620, 25)); ind_h(s, 645, 25, "L203", "1.5 µH", above=True); s.wire((670, 25), (680, 25), e2["6/7"])
    s.wire(e2["4/5"], (940, 90)); s.dot(820, 90); s.dot(900, 90)
    s.port(940, 90, "VMODEM", "r")
    s.wire((820, 90), (820, 115)); s.res(820, 140, "v", "R232", "680 kΩ"); s.wire((820, 165), (820, 175)); s.dot(820, 175)
    s.wire(e2["3"], (790, 150), (790, 175), (820, 175))
    s.res(820, 200, "v", "R233", "100 kΩ"); s.gnd(820, 225)
    s.wire((900, 90), (900, 115)); s.cap(900, 135, "v", "C233", "470 µF", pol=True); s.gnd(900, 155)
    s.wire(e2["14"], (765, 200), (765, 222)); s.text(765, 236, "MODEM_PG", "net", "middle")
    s.text(20, 290, "U206: 3.30 V; EN tied to VIN, MODE low = power save; PG holds the ESP32 EN low until 3V3 > 95 % (pull-up R401, MCU sheet). "
                    "In: 22 µF + 100 nF. Out: 2 × 22 µF + 100 nF.", "note")
    s.text(20, 304, "U207: 3.9 V; R236 holds PS/SYNC high = forced PWM; R237 (1 MΩ) pulls MODEM_PG up to 3V3. "
                    "In: 22 µF + 100 nF at VIN, 100 nF at VINA. Out: 3 × 22 µF + 470 µF + 100 nF, C227 4.7 pF across R232; D205 not fitted.", "note")
    return s.svg()


# ---------------------------------------------------------------- LTE sheet drawings
U301_LEFT = [   # (pins, name, net, note): power, control and service side
    ("42, 43", "VBAT", "VBAT_M", "R301 from VMODEM; C301–C306 at the pins"),
    ("7", "PWRKEY", "M_PWRKEY", "Q301 open collector; TP302"),
    ("15", "RESET_N", "M_RESET_N", "TP303 only, not driven"),
    ("82", "USB_BOOT", "M_USB_BOOT", "R311 4.7 kΩ → BOOT_PAD (TP311)"),
    ("61", "USB_VBUS", "M_USB_VBUS", "TP308: 5 V from a PC for module updates"),
    ("59", "USB_DP", "M_USB_DP", "TP309"),
    ("60", "USB_DM", "M_USB_DM", "TP310"),
    ("39", "DBG_TXD", "M_DBG_TXD", "TP306, 1.8 V log output"),
    ("38", "DBG_RXD", "M_DBG_RXD", "TP307"),
]
U301_RIGHT = [  # data and SIM side
    ("18", "MAIN_TXD", "M_TXD", "U302 A1 → LTE_RX"),
    ("17", "MAIN_RXD", "M_RXD", "U302 A2 ← LTE_TX"),
    ("23", "MAIN_RTS", "M_RTS", "U302 A3 ← LTE_RTS"),
    ("22", "MAIN_CTS", "M_CTS", "U302 A4 → LTE_CTS"),
    ("25", "STATUS", "M_STATUS", "U302 A5 → LTE_STATUS"),
    ("24", "VDD_EXT", "VDD_EXT", "1.8 V out: U302 VCCA and OE divider; TP304"),
    ("16", "NET_STATUS", "M_NETSTAT", "TP305 only"),
    ("14", "USIM_VDD", "USIM_VDD", "J301 C1, C313, R309, D301"),
    ("11", "USIM_DATA", "SIM_DATA_M", "R308 → J301 C7"),
    ("12", "USIM_RST", "SIM_RST_M", "R306 → J301 C2"),
    ("13", "USIM_CLK", "SIM_CLK_M", "R307 → J301 C3"),
]
# cross-check the hand map against the netlist
_u301 = {r["pin"]: r["net"] for r in pins["U301"]}
for _p, _n, _net, _ in U301_LEFT + U301_RIGHT + [("35", "ANT_MAIN", "ANT_MAIN", "")]:
    for _q in _p.split(", "):
        assert _u301[_q] == _net, (_q, _net, _u301[_q])
assert sum(1 for n in _u301.values() if n == "GND") == 24


def fig_l_supply():
    s = Sch(1000, 190, "Modem supply: VMODEM through R301 to the module's VBAT pins, with Quectel's bulk and RF decoupling array")
    s.port(110, 60, "VMODEM", "l"); s.wire((110, 60), (135, 60)); s.res(160, 60, "h", "R301", "0 Ω 0805")
    s.wire((185, 60), (860, 60)); s.text(196, 52, "VBAT_M", "net")
    for x, des, val, pol in [(260, "C301", "100 µF", True), (350, "C302", "100 nF", False), (440, "C303", "33 pF", False),
                             (530, "C304", "10 pF", False), (620, "C305", "3.9 pF", False), (710, "C306", "1.8 pF", False)]:
        s.dot(x, 60); s.cap(x, 80, "v", des, val, pol=pol); s.gnd(x, 100)
    s.add('<rect class="b" x="860" y="38" width="110" height="44"/>')
    s.text(915, 56, "U301", "des", "middle"); s.text(915, 72, "VBAT 42, 43", "pin", "middle")
    s.text(20, 140, "Quectel asks for about 100 µF with ESR ≤ 0.7 Ω plus a 100 nF, 33 pF, 10 pF, 3.9 pF and 1.8 pF array at the VBAT pins,", "note")
    s.text(20, 154, "smallest value closest. VBAT trace at least 2 mm wide. The supply must be able to deliver 2 A: U207 on the power sheet does,", "note")
    s.text(20, 168, "and its 470 µF bulk sits at the converter (D205 not fitted). TP301 on VBAT_M. Lift R301 to measure module current.", "note")
    return s.svg()


def fig_l_pins():
    top, pitch, x0, x1 = 60, 34, 380, 620
    h = 30 + (len(U301_RIGHT) - 1) * pitch + 30
    s = Sch(1000, top + h + 70, "EG810M-EU pin map: every used pad with its net and where it goes")
    s.add(f'<rect class="b" x="{x0}" y="{top}" width="{x1-x0}" height="{h}"/>')
    s.text((x0 + x1) / 2, top + h / 2 - 8, "U301", "des", "middle")
    s.text((x0 + x1) / 2, top + h / 2 + 8, "EG810M-EU", "val", "middle")
    s.text((x0 + x1) / 2, top + h / 2 + 22, "LGA-109", "val", "middle")
    for i, (pn, name, net, note) in enumerate(U301_LEFT):
        y = top + 30 + i * pitch
        s.wire((x0 - 40, y), (x0, y)); s.text(x0 - 3, y - 4, pn, "pnum", "end"); s.text(x0 + 6, y + 4, name, "pin")
        s.text(x0 - 46, y - 1, net, "net", "end"); s.text(x0 - 46, y + 12, note, "note", "end")
    for i, (pn, name, net, note) in enumerate(U301_RIGHT):
        y = top + 30 + i * pitch
        s.wire((x1, y), (x1 + 40, y)); s.text(x1 + 3, y - 4, pn, "pnum"); s.text(x1 - 6, y + 4, name, "pin", "end")
        s.text(x1 + 46, y - 1, net, "net"); s.text(x1 + 46, y + 12, note, "note")
    xa = (x0 + x1) / 2
    s.wire((xa, top - 22), (xa, top)); s.text(xa + 4, top - 8, "35", "pnum"); s.text(xa, top + 14, "ANT_MAIN", "pin", "middle")
    s.text(xa + 8, top - 26, "ANT_MAIN → R310 π match → J302 U.FL", "net")
    s.wire((xa, top + h), (xa, top + h + 18)); s.gnd(xa, top + h + 18); s.text(xa, top + h - 8, "GND", "pin", "middle")
    s.text(xa + 16, top + h + 16, "24 GND pads to the plane", "note")
    n_res = sum(1 for r in pins["U301"] if r["pin_name"] == "RESERVED")
    n_open = sum(1 for r in pins["U301"] if r["net"] in NO_NET) - n_res
    s.text(20, top + h + 52, f"Leave the {n_res} RESERVED pads and {n_open} unused function pads open (ADC, DTR, RI, DCD, AUX UART, I²C, "
                             "USIM_DET). Solid ground under the module; no traces on the top layer beneath it.", "note")
    return s.svg()


def fig_l_ctrl():
    s = Sch(1000, 450, "Power key driver and the 1.8 V to 3.3 V UART level shifter, enabled only while the module's VDD_EXT is up")
    e = ic(s, 420, 90, 170, 250, "U302", "TXS0108EPWR", [
        ("l", 30, "1", "A1"), ("l", 70, "3", "A2"), ("l", 110, "4", "A3"), ("l", 150, "5", "A4"), ("l", 190, "6", "A5"), ("l", 228, "7–9", "A6–A8"),
        ("r", 30, "20", "B1"), ("r", 70, "18", "B2"), ("r", 110, "17", "B3"), ("r", 150, "16", "B4"), ("r", 190, "15", "B5"), ("r", 228, "14–12", "B6–B8"),
        ("t", 40, "2", "VCCA"), ("t", 130, "19", "VCCB"), ("b", 40, "10", "OE"), ("b", 150, "11", "GND")])
    for num, net, note in [("1", "M_TXD", "module MAIN_TXD (18)"), ("3", "M_RXD", "module MAIN_RXD (17)"), ("4", "M_RTS", "module MAIN_RTS (23)"),
                           ("5", "M_CTS", "module MAIN_CTS (22)"), ("6", "M_STATUS", "module STATUS (25)")]:
        x, y = e[num]
        s.text(x - 4, y - 1, net, "net", "end"); s.text(x - 4, y + 12, note, "note", "end")
    s.text(e["7–9"][0] - 4, e["7–9"][1] + 4, "open", "note", "end"); s.text(e["14–12"][0] + 4, e["14–12"][1] + 4, "open", "note")
    for num, net, gpio in [("20", "LTE_RX", "GPIO40"), ("18", "LTE_TX", "GPIO39"), ("17", "LTE_RTS", "GPIO41"),
                           ("16", "LTE_CTS", "GPIO42"), ("15", "LTE_STATUS", "GPIO38")]:
        x, y = e[num]
        s.port(x, y, net, "r"); s.text(x + 18 + 7 * len(net) + 8, y + 4, gpio, "note")
    # supplies
    xa, ya = e["2"]; s.wire((xa, ya), (xa, 50), (330, 50)); s.dot(400, 50)
    s.wire((400, 50), (400, 55)); s.cap(400, 75, "v", "C308", "100 nF", side="l"); s.gnd(400, 95)
    s.text(326, 54, "VDD_EXT", "net", "end")
    xb, yb = e["19"]; s.wire((xb, yb), (xb, 50), (660, 50)); s.dot(620, 50)
    s.wire((620, 50), (620, 55)); s.cap(620, 75, "v", "C309", "100 nF"); s.gnd(620, 95)
    s.rail(672, 50, "3V3")
    # OE follows VDD_EXT through R304/R305 (C307 not fitted: TI limits the OE edge to 10 ns/V)
    xo, yo = e["10"]; s.wire((xo, yo), (xo, 380))
    s.text(326, 384, "VDD_EXT", "net", "end"); s.wire((330, 380), (345, 380)); s.res(370, 380, "h", "R304", "100 kΩ")
    s.wire((395, 380), (520, 380)); s.dot(420, 380); s.dot(xo, 380); s.text(476, 374, "LS_OE", "net")
    s.res(420, 405, "v", "R305", "1 MΩ"); s.gnd(420, 430)
    s.dnp(); s.wire((520, 380), (520, 385)); s.cap(520, 405, "v", "C307", "DNP"); s.gnd(520, 425); s.dnp(False)
    xg, yg = e["11"]; s.gnd(xg, yg)
    # power key driver
    tbox(s, 740, 355, 50, 50, "", [(785, 384, "B", "end"), (765, 369, "C", "middle"), (765, 401, "E", "middle")])
    s.text(732, 384, "Q301", "des", "end"); s.text(732, 398, "MMBT3904", "val", "end")
    s.wire((765, 355), (765, 330)); s.text(765, 324, "M_PWRKEY", "net", "middle"); s.text(765, 310, "module PWRKEY (7)", "note", "middle")
    s.wire((765, 340), (700, 340)); s.dot(765, 340); s.cap(700, 360, "v", "C316", "10 nF", side="l"); s.gnd(700, 380)
    s.wire((765, 405), (765, 420)); s.gnd(765, 420)
    s.wire((790, 380), (850, 380)); s.dot(850, 380)
    s.res(850, 405, "v", "R303", "47 kΩ", side="l"); s.gnd(850, 430)
    s.wire((850, 380), (857, 380)); s.res(882, 380, "h", "R302", "4.7 kΩ"); s.port(907, 380, "LTE_PWRKEY", "r")
    s.text(951, 404, "GPIO21", "note", "middle")
    return s.svg()


def fig_l_sim():
    s = Sch(1000, 420, "Nano-SIM with series links, RF filter caps, pull-up and TVS array; antenna feed with a π match to the U.FL connector")
    e = ic(s, 540, 30, 100, 320, "J301", "", [
        ("l", 20, "C1", "VCC"), ("l", 90, "C2", "RST"), ("l", 170, "C3", "CLK"), ("l", 250, "C7", "I/O"), ("b", 50, "C5", "GND")])
    s.text(590, 300, "SNO-1303-C", "val", "middle"); s.text(590, 314, "nano-SIM", "note", "middle")
    s.gnd(*e["C5"])
    # USIM_VDD
    s.text(20, 54, "USIM_VDD", "net"); s.wire((90, 50), e["C1"]); s.dot(470, 50)
    s.wire((470, 50), (470, 55)); s.cap(470, 75, "v", "C313", "100 nF"); s.gnd(470, 95)
    for (y, src, dst, rdes, cdes, cx, pin) in [(120, "SIM_RST_M", "SIM_RST", "R306", "C310", 300, "C2"),
                                              (200, "SIM_CLK_M", "SIM_CLK", "R307", "C311", 340, "C3"),
                                              (280, "SIM_DATA_M", "SIM_DATA", "R308", "C312", 380, "C7")]:
        s.text(20, y + 4, src, "net"); s.wire((112, y), (135, y)); s.res(160, y, "h", rdes, "0 Ω")
        s.wire((185, y), e[pin]); s.text(200, y - 6, dst, "net")
        s.dot(cx, y); s.wire((cx, y), (cx, y + 5)); s.cap(cx, y + 25, "v", cdes, "33 pF"); s.gnd(cx, y + 45)
    s.dot(430, 280); s.res(430, 255, "v", "R309", "15 kΩ"); s.rail(430, 230, "USIM_VDD")
    s.text(590, 404, "C6 VPP and CD (card detect) open; cover tabs to GND", "note", "middle")
    # TVS array, connected by net name
    d = ic(s, 790, 200, 110, 130, "D301", "SRV05-4", [
        ("l", 25, "1", "IO1"), ("l", 60, "3", "IO2"), ("l", 95, "4", "IO3"), ("r", 25, "5", "REF2"), ("r", 60, "6", "IO4"), ("b", 55, "2", "REF1")])
    for num, net in [("1", "SIM_DATA"), ("3", "SIM_CLK"), ("4", "SIM_RST")]:
        s.text(d[num][0] - 4, d[num][1] + 4, net, "net", "end")
    s.text(d["5"][0] + 4, d["5"][1] + 4, "USIM_VDD", "net"); s.text(d["6"][0] + 4, d["6"][1] + 4, "open", "note")
    s.gnd(*d["2"])
    s.text(845, 370, "Place D301 and C310–C313 at the holder", "note", "middle")
    # antenna
    s.text(716, 74, "ANT_MAIN", "net", "end"); s.wire((720, 70), (765, 70)); s.dot(740, 70)
    s.dnp(True); s.wire((740, 70), (740, 75)); s.cap(740, 95, "v", "C314", "DNP", side="l"); s.gnd(740, 115); s.dnp(False)
    s.res(790, 70, "h", "R310", "0 Ω"); s.wire((815, 70), (900, 70)); s.dot(850, 70)
    s.dnp(True); s.wire((850, 70), (850, 75)); s.cap(850, 95, "v", "C315", "DNP"); s.gnd(850, 115); s.dnp(False)
    s.add('<circle class="b" cx="912" cy="70" r="12"/>'); s.add('<circle class="dot" cx="912" cy="70" r="3"/>')
    s.wire((912, 82), (912, 100)); s.gnd(912, 100)
    s.text(912, 50, "J302 U.FL", "des", "middle"); s.text(930, 74, "→ FPC", "note")
    s.text(820, 150, "50 Ω feed; π parts at the connector", "note", "middle")
    return s.svg()


# ---------------------------------------------------------------- data for search tables
# a net name used on two sheets is one net (GND, VBAT_SW)
nets, net_sheets = defaultdict(list), defaultdict(set)
for r in net_rows:
    if r["net"] in NO_NET:
        continue
    nets[r["net"]].append({"ref": r["designator"], "pin": r["pin"], "name": r["pin_name"], "fit": r["fit"]})
    net_sheets[r["net"]].add(r["sheet"])
net_data = [{"net": n, "sheets": sorted(net_sheets[n]), "conn": c} for n, c in sorted(nets.items())]
bom_data = OrderedDict()
for sh, rows in bom_by_sheet.items():
    for r in rows:
        r["value"] = pretty(r["value"])
        r["notes"] = r["notes"].replace(" uF", " µF")
    bom_data[sh] = [{k: r[k] for k in ("designators", "qty", "value", "description", "package", "suggested_mpn", "lcsc", "fit", "notes")}
                    for r in rows]

STATS = {}
for sh in SHEETS:
    ds = [d for d in pins if sheet_of[d] == sh]
    STATS[sh] = {"nparts": len(ds), "nfit": sum(1 for d in ds if fit[d] == "Y"),
                 "nnets": sum(1 for n in nets if sh in net_sheets[n])}

FIGS = {
    "sys": fig_sys(), "powertree": fig_powertree(),
    "overview": fig_overview(), "power": fig_power(), "adc": fig_adc(), "clockio": fig_clockio(),
    "mic": fig_mic(), "direct": fig_direct(), "presupply": fig_presupply(), "preamp": fig_preamp(),
    "p_panel": fig_p_panel(), "p_charger": fig_p_charger(), "p_temp": fig_p_temp(), "p_battery": fig_p_battery(),
    "p_latch": fig_p_latch(), "p_rails": fig_p_rails(),
    "l_supply": fig_l_supply(), "l_pins": fig_l_pins(), "l_ctrl": fig_l_ctrl(), "l_sim": fig_l_sim(),
}

tpl = open(args.template).read()
page = tpl
for k, v in FIGS.items():
    page = page.replace(f"{{{{fig:{k}}}}}", v)
for k in BLOCKS:
    page = page.replace(f"{{{{parts:{k}}}}}", part_table(k))
for k in SECTIONS:
    page = page.replace(f"{{{{comp:{k}}}}}", comp_table(k))
for sh, st in STATS.items():
    for k, v in st.items():
        page = page.replace(f"{{{{{k}:{sh}}}}}", str(v))
page = (page.replace("{{mic2map}}", mic2_table()).replace("{{ports}}", ports_table(PORTS))
        .replace("{{powerports}}", ports_table(POWER_PORTS)).replace("{{lteports}}", ports_table(LTE_PORTS))
        .replace("{{allcomp}}", all_comp_table()).replace("{{costsum}}", f"{COST:.2f}")
        .replace("{{ntbd}}", f"{len(TBD_ROLES)}: " + ", ".join(TBD_ROLES) if TBD_ROLES else "none")
        .replace("{{lowstock}}", f"{LOW[1]} · {int(LOW[0])}" if LOW[0] is not None else "–")
        .replace("{{snapdate}}", SNAP_DATE).replace("{{snappath}}", os.path.relpath(SNAP_PATH, REPO))
        .replace("{{nnets}}", str(len(nets))).replace("{{nshared}}", ", ".join(n for n in sorted(nets) if len(net_sheets[n]) > 1))
        .replace("{{netjson}}", json.dumps(net_data).replace("</", "<\\/"))
        .replace("{{bomjson}}", json.dumps(bom_data).replace("</", "<\\/")))
assert "{{" not in page, page[page.index("{{"):page.index("{{") + 40]
if not args.fragment:
    head, body = page.split("</style>\n", 1)
    head = head.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
    page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            + head + "</style>\n</head>\n<body>\n" + body + "</body>\n</html>\n")
open(OUT, "w").write(page)
print("wrote", OUT, len(page), "bytes;", len(snap), "major parts in", len(SECTIONS), "tabs;",
      "; ".join(f"{sh}: {st['nparts']} parts, {st['nfit']} fitted, {st['nnets']} nets" for sh, st in STATS.items()),
      f"| {len(nets)} nets on the board")
