# Schematic freeze record: rev A layout baseline

**Date:** 2026-11-19. **Status:** the four sheet CSVs are frozen as the rev A layout baseline. Any later change to a sheet CSV follows the change-control rule at the end of this record.

## What is frozen

| Item | Value |
|---|---|
| Frozen commit | The merge into `main` of branch `second-review-2026-11-19`, tagged **`schematic-rev-a-freeze`** (annotated). On the branch, the schematic content is commit `7245e41` ("Apply the approved second-review fixes") plus this record's commit |
| Source of truth | `hardware/{power,audio-frontend,lte,mcu}/*-netlist.csv` and `*-bom.csv` |
| Reviews | `hardware/review/2026-11-17-schematic-review.md` (first review, owner decisions 2026-11-18) and `hardware/review/2026-11-19-second-review.md` (independent second review) |
| Owner approval | 2026-11-19: the second review's batch (section 9), with the recommended option wherever one was offered |
| EasyEDA project | `AURIS` (uuid `3ba79283056140b08e7552182142ce8a`), EasyEDA Pro 4.1.105. POWER, AUDIO and MCU updated in place on 2026-11-19 (remove-part, capture, tidy), each verified pin by pin against its CSV (0 mismatches) and saved; LTE unchanged; Design > Update PCB run by the owner |
| Export | `hardware/2026-11-19/AURIS_2026-11-19_freeze.epro2`, SHA-256 `ba1b68c031332c6b43b11e7aaf93feca11f284158c97b6b4dbb5845b1dca36f4`; EasyEDA BOM `hardware/2026-11-19/AURIS_BOM_2026-11-19_freeze.csv`. The review baseline export `AURIS_2026-11-19.epro2` (`0c3d5120…`) is kept unchanged beside it |
| PCB state | 346 components (the four sheets' 115 + 130 + 53 + 48), no tracks or vias yet: the PCB DRC's connection errors are the unrouted ratsnest before layout |
| BOM cost per board | **$48.98 at 10 boards, $27.76 at 100** (JLC parts plus Economic PCBA feeder fees, `bom_cost.py`); was $48.32 / $27.44. 104 unique codes, 54 extended. Changes: `hardware/review/2026-11-19-bom-cost-changes.csv` |

### Check output

`python3 hardware/tools/easyeda_check.py hardware/2026-11-19/AURIS_2026-11-19_freeze.epro2` (notes omitted):

```
audio: 115 of 115 parts match, 0 with problems, 0 not on the PCB
power: 130 of 130 parts match, 0 with problems, 0 not on the PCB
lte: 53 of 53 parts match, 0 with problems, 0 not on the PCB
mcu: 48 of 48 parts match, 0 with problems, 0 not on the PCB
All checks passed.
```

`python3 hardware/tools/build_guide.py`:

```
wrote hardware/auris-hardware-guide.html 457882 bytes; 44 major parts in 6 tabs; audio: 115 parts, 84 fitted, 72 nets; power: 130 parts, 126 fitted, 62 nets; lte: 53 parts, 43 fitted, 37 nets | 166 nets on the board
```

### Changes applied at the freeze

| Finding | Change |
|---|---|
| R2-P1 (must fix) | U208 MAX809STRG (C9965) switches the TMP390 supply (TEMP_VDD) on above 2.85–3.00 V; R210 47 kΩ to TEMP_VDD |
| R2-M1 (must fix) | Card-supply soft start: C407 10 nF gate–drain, R415 100 kΩ, R414 1 MΩ |
| R2-G1 | TPS63802 lockout: R241 150 kΩ / R242 100 kΩ on EN (on 2.75 V, off 2.50 V) |
| R2-G2 | Button through D206 (1N4148WS); Q211 and R246 give BTN_SENSE on GPIO35 |
| R2-G3 | Q210 gate link R245 (0 Ω) and DNP C237 for a soft start |
| R2-G6 | TPS63802 MODE via R243 100 kΩ to GND, DNP R244 to GPIO36; recording gate VBAT_SW ≥ 3.6 V |
| R2-P2 | Trip-test pads TP214 (TMP_SETA), TP215 (TMP_SETB) |
| R2-A1 | R148 100 kΩ AUDIO_EN pull-down |
| R2-M2 | C403 100 nF |
| P22 (first review) | RTC INT/SQW drives WAKE_N; Q206, Q207, R219, R222, R223 removed |

**Tooling fixed on the way** (EasyEDA Pro 4.1 library quirks): `getByLcscIds("C9965")` returned a stray device without a footprint, and the project library held a footprint-less "100nF" copy of C1525 beside two good ones. The capture template now looks copies up by name and MPN, requires the same LCSC code and a footprint, and the tidy clears a stale no-connect flag before drawing a net stub on a pin that was NC before (U401 pins 28/29). U208 and C403 were placed from devices with footprints; every part on all four pages has one.

## Accepted open items

None of these changes a net or a part on the sheets. "Owner" is the project owner; "layout", "bench" and "firmware" are whoever does that work for rev A.

### Layout (before or during PCB placement)

| Item | Detail | Who |
|---|---|---|
| Stack-up | Set the PCB to 4 layers before placement (the export still has EasyEDA's 2-layer default); solid ground under U301, nothing on layer 1 beneath it, 50 Ω ANT feed, 90 Ω USB pairs (Quectel) | layout |
| U301 footprint (R2-X1) | Outer-ring pads to 1.0 × 0.6 mm per EG810M-EU HD V1.0 Fig. 40 (library has 1.0 × 0.7); keep ≥ 3 mm clearance around the module | layout |
| D101, D402 (R2-A2, first review A5) | TI DPY0002A land pattern | layout |
| F201, F202, C207 (R2-X3) | Littelfuse 1812L pads on both fuses; C207 pad gap ≥ 1.0 mm | layout |
| Test pads (R2-X4) | 1.0 mm pad footprint for all 54 TPs; the pogo row (TP401–TP403, TP413–TP415) at 2.54 mm | layout |
| J401 (R2-X5) | Shell slots per the HCTL drawing; pin-in-paste on 1.6 mm | layout |
| Placement | U203 at the board edge nearest the pack, away from charger and converters (P16, R2-P3); ESP32 antenna at an edge with Espressif's keep-out and away from the LTE FPC antenna (≥ 20 dB isolation); J402 and J401 behind sealed ports (F5-06); LED401 behind a light pipe (F5-05); SW201/SW202 reachable | layout, owner (enclosure) |
| Layout notes | High-current path J203 → F202 → Q205 → Q210 → U207 → R301 → U301; charger loop tight; R202 Kelvin; D203/D204 ≈ 1 cm² copper; thermal vias under U207; audio layout rules (audio README); U206 centroid offset 0.075 mm | layout |
| Coating and silkscreen | Conformal coat the TMP390 SET pins and the mic input; "+"/"−" at J201/J202; SW202 ON/SHIP after the meter check; SW202 locator holes as NPTH | layout |

### Bench (rev A bring-up, gates G1–G4)

| Item | Detail | Who |
|---|---|---|
| Inrush (W6) | Power test 2 with the real pack; fit R245 10 kΩ, C237 100 nF, C218 2.2 µF if the protection trips | bench |
| Cut-out (R2-P1/P2/P3) | Test 6: trip test on TP214/TP215 on every board; slow 0 → 3.4 V panel ramp; freeze spray and heat gun; U203-to-cell ΔT while charging | bench |
| MPPT (P17, P18, R2-G4) | Clamp behaviour; set point with the chosen panel; R204 per region | bench, owner |
| Modem rail (W7, R2-G5) | Tests 8–9: start-up sag, C233 kept or removed, transmit floor, F202 temperature | bench |
| Lockout (R2-G1) | Test 11: 3V3 on 2.68–2.83 V, off 2.43–2.58 V | bench |
| Card supply (R2-M1) | Scope 3V3 and ESP_EN at card enable, minimum battery, power-save mode | bench |
| Button (R2-G2) | BTN_SENSE pressed/released, at +85 °C too | bench |
| Audio (G2) | A/B noise, MODE power-save vs forced PWM, recording gate 3.6 V vs lower, MICBIAS, LRCK and −40 °C crystal start, full scale on the P pin, high-pass corners | bench |
| LTE | STATUS before boot, translator levels, R301 current rating, π-match tuning | bench |
| Cold parts | BR1220 cell at −40 °C; J402 microSD holder at −40 °C | bench |
| First-board checks | BT201 polarity, SW202 position, J203 polarity against the pack | bench |

### Firmware

| Item | Detail | Who |
|---|---|---|
| Power hold (W5, R2-G8) | Assert PWR_HOLD in the second-stage bootloader; clear the RTC flag only at commit; crash counter with a long-alarm fallback | firmware |
| RTC | INTCN = 1, BBSQW = 0, EN32KHZ = 0 every boot; I²C bus clear | firmware |
| Audio | Record only with VBAT_SW ≥ 3.6 V under load; clock-register check; AUDIO_EN low ≥ 0.5 s before a retry | firmware |
| Modem | Read STATUS before any PWRKEY pulse; confirm with `RDY`/`AT`; flush RX around VDD_EXT edges; `AT+QSCLK=0`; no session below ≈ 3.3 V | firmware |
| microSD | Card power only with SD_CD; ≥ 0.5 s off before re-powering; clear GPIO44's pull-up | firmware |
| GPIO | Pull-downs on GPIO4/5/9/36/37; pull-up on GPIO35 (button; report a stuck button); flash/PSRAM at 80 MHz; never burn EFUSE_DIS_USB_JTAG or EFUSE_STRAP_JTAG_SEL | firmware |

### Parts, procurement and compliance

| Item | Detail | Who |
|---|---|---|
| Buy now (R2-G7) | EG810M-EU (206 at JLC) and PCM1863DBTR (244, falling) prototype quantities | owner |
| Deployment BOM | Genuine JST PH for J203; ≥ 5000 h or polymer C207/C219/C233; LED201/LED202 not fitted; −40…+85 °C SIM holder or MFF2 eSIM (L7); microSD holder qualified (M9) | owner |
| Accepted as is | D205 VBAT TVS not fitted; push-push SIM holder for rev A; consumer USB-C for service only | owner |
| Compliance and service | RED (Europe) and RCM (Australia) for the finished recorder; SIM plan and operator acceptance; Quectel's English standard-firmware manual V1.4 (login) | owner |

## Change control after the freeze

Every change to a sheet CSV after the tag `schematic-rev-a-freeze` needs:

1. a row in `hardware/review/schematic-change-log.csv` with the columns `date,id,sheets,designators,change,reason,evidence,owner_approval,check_result`;
2. the owner's approval, before the change;
3. the full loop: `build_guide.py`, capture or tidy, Design > Update PCB, export, a passing `easyeda_check.py` (recorded in `check_result`).

Layout-only changes (placement, routing, footprint geometry with unchanged pads and nets) need no entry; the footprint edits listed above are of that kind.
