# Enclosure options for rev A (ADR-020 input)

Research note, 2026-11-19. Goal: the smallest stock enclosure that holds everything that must be inside, so the PCB outline and mounting holes can be taken from it. ADR-020 stays open until the owner chooses.

## What goes inside

Owner decisions 2026-11-19: the solar panel sits on a **separate bracket** (not the lid), and the microphone is a **separable acoustic head on a through-wall connector**. So the box carries no panel and no acoustic port or membrane.

| Item | Size | Source |
|---|---|---|
| PCB | ≈ 8,000–9,000 mm² with parts on the top side only (e.g. 105 × 80 mm); smaller only with parts on both sides | Footprint area from the freeze export, × 1.5–2 for routing |
| Tallest board parts | ≈ 8–12 mm (C-tantalum and electrolytics 5.8–7.7 mm, the J201/J202 screw terminals) | Repo datasheets |
| Battery | Two 18650 cells in parallel, ≈ 40 × 70 × 20 mm with wrap | docs/19: ≈ 15 Wh nominal, 1S2P 18650 |
| LTE antenna | TX4G-FPC-8121, 81 × 21 mm, stuck to an inside wall away from the ESP32 antenna | Retailer listing (no maker datasheet found) |
| Through the walls | Mic connector (4 pins), panel input(s), pressure vent (M12), sealed SD/USB service port (F5-06), light pipe (F5-05), button | Requirements |

Two ways to arrange it: battery **beside** the PCB (standing on its 70 × 20 edge in a ≈ 25 mm strip), or **under** it (PCB on standoffs above the pack). Either needs about **110 × 105 mm of floor and ≈ 45–50 mm of internal height**.

## Candidates

Dimensions in mm, L × W × H. "Internal" is the clear cavity.

| Enclosure | External | Internal | Material, sealing | Temperature | PCB mounting | Fit |
|---|---|---|---|---|---|---|
| **Hammond 1554N, polycarbonate (1554N2GY)** | 120 × 120 × 60 | ≈ 110 × 110 (inner panel 1554NPL is 108 × 107); height ≈ 45 base + 15 lid, exact internal not read | PC, UV-stabilised for outdoor use, IP68 / NEMA 4X; stainless M4 lid screws; silicone gasket | Not read | M3 brass inserts for a PCB or the inner panel; positions on the drawing (not read) | **Smallest that fits.** PCB ≈ 105 × 80 with the battery on edge beside it, or up to ≈ 105 × 105 above it. 1554P is the same at 80 mm high |
| Bopla Bocube B 141306 PC | 151 × 125 × 60 | Opening 112 × 113, cavity 114.4 × 118.4, height 52 | PC UL 94 V-0, UV f1 (UL 746C) "suitable outdoors"; IP66 / IP68 (1.2 m, 2 h); IK07; lid screws outside the seal | Not stated | Standoffs in base or lid; mounting plates | Fits; 31 mm longer outside than the Hammond for the same inside, because the screws sit in end pockets. Fully documented |
| Takachi WGPC15-16-6G | 145 × 155 × 55 | 107 × 120 × 43 | PC/ASA, UV-resistant, IP68; silicone gasket | −30 to +75 °C | Bosses inside (positions not given); plate WGP | Fits, but 43 mm is tight for battery under the PCB; battery beside it works |
| Takachi SPCP131806G | 125 × 175 × 60 | 115.5 × 141 × 45.5 | PC, IP66/67 | −20 to +75 °C | Optional plate SMP | Fits with room to spare; −20 °C is exactly F7-01's lower limit, no margin |
| Fibox MNX PC 125/75 HG | 130 × 130 × 75 | ≈ 90–99 square (drawing) | PC, IP66/67, IK08; 25-year UV life declared | −40 to +80 °C | Plate 98 × 98; screw bosses 75 × 90 | **Too small** for a single-sided PCB (≈ 88 × 88 usable) |
| Spelsberg TG PC 1212-6-o | 124 × 122 × 55 | Not published | PC, IP66/67, IK08, UV-resistant | −35 to +80 °C | Internal fixing cams, plates MPI/MPS-1212 | Rated for "protected outdoor" use only (UL Type 12): weaker for full sun |

Not suitable: Bopla Euromas II (IP65), Takachi BCPC/BCAP (IP65), Gainta G3xx (ABS), Fibox Tempo (IP65), Hammond 1554 in ABS (Hammond: not for outdoor use).

## Price, and cheaper options

- Hammond 1554N2GY: about US$16–27 each (Octopart, myMectronic aggregators); DigiKey Canada CA$38.91 for one, CA$25.78 each at 100 (backorder). No element14 Australia price found.
- AliExpress (search pages read 2026-11-19, EUR): generic "125 × 125 × 75 mm" outdoor junction box from €3.35 each (material and IP not stated); "IP67 ABS/polycarbonate" boxes €7.89–8.39 (titles name both materials, no dimensions); 150 × 110 × 70 mm ABS IP65 boxes €15.42. None was verified as PC or ASA with IP66+ and a known internal size.
- Other low-cost routes not yet priced: RS PRO's own polycarbonate IP67 box at 119.8 × 119.8 × 60.1 mm (RS 186-2279), Chinese factories that sell on AliExpress with drawings and a PC option (e.g. Szomk), and LCSC's junction boxes.

The catch with cheap boxes: most are ABS, which chalks and turns brittle in sun within a year or two unless UV-stabilised (F7-03 asks for 300-day service intervals in Australian and European weather); the IP rating is untested and the gasket is often a foam strip; and sizes and listings change between batches, so a PCB outline tied to one listing's bosses is a risk.

**Way round it:** mount the PCB on its own holes (standoffs or a small plate fixed to the box floor), not on the box's bosses. Then any box with ≥ 110 × 105 mm floor and ≥ 45 mm inside height takes the same board: cheap boxes for rev A prototypes and bench work, and the production box (Hammond, Bocube, or a PC/ASA box bought direct from a factory with a drawing) chosen later without a PCB respin.

**Owner decision 2026-11-19:** the PCB mounts on a 3D-printed plate, so its outline and holes are not tied to any box's bosses. The plate can also carry the battery and hold the LTE antenna in a fixed place.

## Recommendation

1. **First choice: Hammond 1554N2GY** (120 × 120 × 60), with 1554P2GY (80 high) as the step up if the battery goes under the PCB with room for desiccant. It is the smallest box found that holds the PCB, the pack and the antenna; Hammond is stocked by the usual distributors in Europe and Australia (not checked for this part: the sites refused automated reads).
2. **Fallback: Bopla Bocube B 141306 PC**, the best-documented option, if the Hammond drawing shows less room than its inner panel suggests.
3. **Set the PCB from the box:** with the 1554N, about 105 × 80 mm, mounting holes on the M3 brass inserts (or on the 1554NPL inner panel, which decouples the PCB from the box). Take positions from Hammond's drawing before fixing the outline.

The board then has to be compact: the earlier edge layout (110 × 80 with 4 corner holes) is replaced by whatever the insert pattern allows.

## Open points

- **Not verified, needs the browser or the owner:** Hammond 1554N/P polycarbonate drawing (internal height, insert positions, temperature rating), distributor price and stock in Europe and Australia for the shortlisted parts. hammfg.com, RS and two catalogue mirrors refused automated fetches.
- **Radio:** inside a 120 mm box the ESP32 antenna and the LTE FPC antenna end up 80–100 mm apart at best. Quectel asks for ≥ 20 dB isolation; measure it with the first board in the box. If it falls short, an external LTE antenna on the bracket (bulkhead SMA) is the fallback.
- **Heat:** a smaller box has less surface to shed solar heat. Mounting it in the shade of the panel bracket helps F7-01 (internal air ≤ 65 °C).
- **Wall space:** the bottom wall carries the mic connector, panel input(s) and vent; the SD/USB service port may need a side wall. Choose the through-wall connectors (e.g. M8 4-pin for the mic) next.
- **Battery:** confirm the actual pack dimensions; the 40 × 70 × 20 mm here is an estimate for two wrapped 18650s.

## Sources (read 2026-11-19)

- Hammond 1554 product sheet (ABS version; sizes and inner panels): media.onlinecomponents.com/productfiles/mf-ham/basic_1554fla.htm.pdf
- Bopla Bocube: bopla.de/gehaeusetechnik/bocube and brochure bopla.de/fileadmin/product_data/00_the_red_book/bocube_de.pdf
- Takachi: takachi-enclosure.com/products/WGPC, /products/WG, /products/SPCP, /products/WP, /products/BCPC
- Fibox MNX: fibox.com/products/mnx/pc-abs-125h/6011308, declaration MD_FIBOX_MNX_PC.pdf, drawing MNX125H.gif
- Spelsberg TG PC: spelsberg.de/p/20040401/, /p/20040501/, /p/20040701/ and their datasheet PDFs
- LTE antenna size: hubtronics.in/TX4G-FPC-8121
