// Auris schematic capture: power sheet (123 parts, 287 pin connections).
// Generated 2026-11-17 by hardware/tools/easyeda_capture.py from power/power-netlist.csv and power-bom.csv.
// Don't edit this file: change the CSVs, then run the generator again.
//
// What it does: places every part of the sheet on the open schematic page by its
// LCSC code, grouped by the blocks in hardware/tools/build_guide.py, each in a box
// with the heading the block has in the hardware guide. It sets each
// designator and BOM flag, then gives every pin a short wire carrying its net
// name. Pins marked NC get a no-connect flag. Parts are not wired to each other:
// connections come from the net names, so move things around freely afterwards.
//
// To run it in EasyEDA Pro:
//  1. Open the Auris project and an empty schematic page for this sheet.
//  2. Place one template part per kind on the page, keeping its default
//     designator: a test pad (any test-point part from the library) for
//     TP201, TP202, TP203, TP204, TP205, TP206, TP207, TP208, TP209, TP210,
//     TP211, TP212, TP213. These parts have no LCSC code, so the script
//     copies the template's library part. It leaves the template where it is,
//     so delete it afterwards.
//  3. Advanced > Run Script (EasyEDA Pro v2: Settings > Extensions > Standalone
//     Script). Paste this whole file and run it. A dialog reports the result.
// Running it again skips designators already on the page, so after fixing an
// error you can run it again without getting duplicates.

(async () => {
  const SHEET = "power";
  // d: designator, lcsc: LCSC code ("" = copy a template part), fit: false = not fitted,
  // block: block in build_guide.py, pins: [pin number, pin name, net] from the netlist
  const PARTS = [
    {"d": "J201", "lcsc": "C695629", "fit": true, "pins": [["1", "+", "PANEL_IN"], ["2", "-", "GND"]], "block": "p_solar"},
    {"d": "J202", "lcsc": "C695629", "fit": true, "pins": [["1", "+", "PANEL_IN"], ["2", "-", "GND"]], "block": "p_solar"},
    {"d": "F201", "lcsc": "C207066", "fit": true, "pins": [["1", "1", "PANEL_IN"], ["2", "2", "PANEL_FUSED"]], "block": "p_solar"},
    {"d": "D201", "lcsc": "C353317", "fit": true, "pins": [["1", "1", "PANEL_FUSED"], ["2", "2", "GND"]], "block": "p_solar"},
    {"d": "Q201", "lcsc": "C15155", "fit": true, "pins": [["1", "G", "Q201_G"], ["2", "S", "SOLAR_IN"], ["3", "D", "PANEL_FUSED"]], "block": "p_solar"},
    {"d": "R201", "lcsc": "C2909337", "fit": true, "pins": [["1", "1", "GND"], ["2", "2", "Q201_G"]], "block": "p_solar"},
    {"d": "D202", "lcsc": "C51625763", "fit": true, "pins": [["K", "K", "SOLAR_IN"], ["A", "A", "Q201_G"]], "block": "p_solar"},
    {"d": "C201", "lcsc": "C2161857", "fit": true, "pins": [["1", "1", "SOLAR_IN"], ["2", "2", "GND"]], "block": "p_solar"},
    {"d": "C202", "lcsc": "C69335", "fit": true, "pins": [["1", "1", "SOLAR_IN"], ["2", "2", "GND"]], "block": "p_solar"},
    {"d": "C203", "lcsc": "C19103847", "fit": true, "pins": [["1", "1", "SOLAR_IN"], ["2", "2", "GND"]], "block": "p_solar"},
    {"d": "C204", "lcsc": "C359190", "fit": true, "pins": [["1", "1", "SOLAR_IN"], ["2", "2", "GND"]], "block": "p_solar"},
    {"d": "R238", "lcsc": "C26083", "fit": true, "pins": [["1", "1", "SOLAR_IN"], ["2", "2", "SOLAR_SENSE"]], "block": "p_solar"},
    {"d": "R239", "lcsc": "C25755", "fit": true, "pins": [["1", "1", "SOLAR_SENSE"], ["2", "2", "GND"]], "block": "p_solar"},
    {"d": "C235", "lcsc": "C1525", "fit": true, "pins": [["1", "1", "SOLAR_SENSE"], ["2", "2", "GND"]], "block": "p_solar"},
    {"d": "R240", "lcsc": "C25879", "fit": true, "pins": [["1", "1", "SOLAR_SENSE"], ["2", "2", "SOLAR_ADC"]], "block": "p_solar"},
    {"d": "U201", "lcsc": "C154992", "fit": true, "pins": [["1", "VG", "CN_VG"], ["2", "GND", "GND"], ["3", "CHRG", "CN_CHRG"], ["4", "DONE", "CN_DONE"], ["5", "COM", "CN_COM"], ["6", "MPPT", "MPPT"], ["7", "BAT", "RAW_BAT"], ["8", "CSP", "CHARGE_SENSE"], ["9", "VCC", "SOLAR_IN"], ["10", "DRV", "CN_DRV"]], "block": "p_charger"},
    {"d": "C205", "lcsc": "C359190", "fit": true, "pins": [["1", "1", "SOLAR_IN"], ["2", "2", "CN_VG"]], "block": "p_charger"},
    {"d": "R204", "lcsc": "C5126256", "fit": true, "pins": [["1", "1", "SOLAR_IN"], ["2", "2", "MPPT"]], "block": "p_charger"},
    {"d": "R205", "lcsc": "C25741", "fit": true, "pins": [["1", "1", "MPPT"], ["2", "2", "GND"]], "block": "p_charger"},
    {"d": "Q202", "lcsc": "C15155", "fit": true, "pins": [["1", "G", "CN_DRV"], ["2", "S", "SOLAR_IN"], ["3", "D", "CHG_SW_RAW"]], "block": "p_charger"},
    {"d": "D203", "lcsc": "C193342", "fit": true, "pins": [["K", "K", "CHG_SW"], ["A", "A", "CHG_SW_RAW"]], "block": "p_charger"},
    {"d": "D204", "lcsc": "C193342", "fit": true, "pins": [["K", "K", "CHG_SW"], ["A", "A", "GND"]], "block": "p_charger"},
    {"d": "L201", "lcsc": "C2894720", "fit": true, "pins": [["1", "1", "CHARGE_SENSE"], ["2", "2", "CHG_SW"]], "block": "p_charger"},
    {"d": "R202", "lcsc": "C309630", "fit": true, "pins": [["1", "1", "RAW_BAT"], ["2", "2", "CHARGE_SENSE"]], "block": "p_charger"},
    {"d": "R203", "lcsc": "C2909315", "fit": true, "pins": [["1", "1", "CN_COMRC"], ["2", "2", "CN_COM"]], "block": "p_charger"},
    {"d": "C206", "lcsc": "C16772", "fit": true, "pins": [["1", "1", "GND"], ["2", "2", "CN_COMRC"]], "block": "p_charger"},
    {"d": "LED201", "lcsc": "C2286", "fit": true, "pins": [["A", "A", "SOLAR_IN"], ["K", "K", "LED201_K"]], "block": "p_charger"},
    {"d": "R206", "lcsc": "C25879", "fit": true, "pins": [["1", "1", "CN_CHRG"], ["2", "2", "LED201_K"]], "block": "p_charger"},
    {"d": "LED202", "lcsc": "C12624", "fit": true, "pins": [["A", "A", "SOLAR_IN"], ["K", "K", "LED202_K"]], "block": "p_charger"},
    {"d": "R207", "lcsc": "C25879", "fit": true, "pins": [["1", "1", "CN_DONE"], ["2", "2", "LED202_K"]], "block": "p_charger"},
    {"d": "C207", "lcsc": "C401746", "fit": true, "pins": [["1", "1", "RAW_BAT"], ["2", "2", "GND"]], "block": "p_charger"},
    {"d": "C208", "lcsc": "C1705", "fit": true, "pins": [["1", "1", "RAW_BAT"], ["2", "2", "GND"]], "block": "p_charger"},
    {"d": "C209", "lcsc": "C19702", "fit": true, "pins": [["1", "1", "RAW_BAT"], ["2", "2", "GND"]], "block": "p_charger"},
    {"d": "C210", "lcsc": "C1525", "fit": true, "pins": [["1", "1", "RAW_BAT"], ["2", "2", "GND"]], "block": "p_charger"},
    {"d": "U202", "lcsc": "C14289", "fit": true, "pins": [["1", "GND", "GND"], ["2", "IN", "SOLAR_IN"], ["3", "OUT", "TEMP_3V3"]], "block": "p_temp"},
    {"d": "C211", "lcsc": "C19702", "fit": true, "pins": [["1", "1", "TEMP_3V3"], ["2", "2", "GND"]], "block": "p_temp"},
    {"d": "C212", "lcsc": "C359190", "fit": true, "pins": [["1", "1", "TEMP_3V3"], ["2", "2", "GND"]], "block": "p_temp"},
    {"d": "U203", "lcsc": "C5219772", "fit": true, "pins": [["1", "SETA", "TMP_SETA"], ["2", "SETB", "TMP_SETB"], ["3", "GND", "GND"], ["4", "OUTB", "TEMP_FAULT_N"], ["5", "VDD", "TEMP_3V3"], ["6", "OUTA", "TEMP_FAULT_N"]], "block": "p_temp"},
    {"d": "R208", "lcsc": "C2933083", "fit": true, "pins": [["1", "1", "GND"], ["2", "2", "TMP_SETA"]], "block": "p_temp"},
    {"d": "R209", "lcsc": "C25872", "fit": true, "pins": [["1", "1", "GND"], ["2", "2", "TMP_SETB"]], "block": "p_temp"},
    {"d": "R210", "lcsc": "C25744", "fit": true, "pins": [["1", "1", "TEMP_3V3"], ["2", "2", "TEMP_FAULT_N"]], "block": "p_temp"},
    {"d": "R211", "lcsc": "C2906872", "fit": true, "pins": [["1", "1", "TEMP_FAULT_N"], ["2", "2", "TEMP_EN_DRV"]], "block": "p_temp"},
    {"d": "R212", "lcsc": "C25741", "fit": true, "pins": [["1", "1", "TEMP_EN_DRV"], ["2", "2", "GND"]], "block": "p_temp"},
    {"d": "Q203", "lcsc": "C20526", "fit": true, "pins": [["1", "B", "TEMP_EN_DRV"], ["2", "E", "GND"], ["3", "C", "TEMP_CLAMP"]], "block": "p_temp"},
    {"d": "R213", "lcsc": "C25741", "fit": true, "pins": [["1", "1", "SOLAR_IN"], ["2", "2", "TEMP_CLAMP"]], "block": "p_temp"},
    {"d": "Q204", "lcsc": "C20526", "fit": true, "pins": [["1", "B", "TEMP_CLAMP"], ["2", "E", "GND"], ["3", "C", "MPPT"]], "block": "p_temp"},
    {"d": "J203", "lcsc": "C295747", "fit": true, "pins": [["1", "BAT+", "BAT_CONN"], ["2", "BAT-", "GND"], ["MP1", "MP", "GND"], ["MP2", "MP", "GND"]], "block": "p_battery"},
    {"d": "F202", "lcsc": "C163516", "fit": true, "pins": [["1", "1", "BAT_CONN"], ["2", "2", "BAT_FUSED"]], "block": "p_battery"},
    {"d": "Q205", "lcsc": "C15127", "fit": true, "pins": [["1", "G", "Q205_G"], ["2", "S", "RAW_BAT"], ["3", "D", "BAT_FUSED"]], "block": "p_battery"},
    {"d": "R214", "lcsc": "C25741", "fit": true, "pins": [["1", "1", "GND"], ["2", "2", "Q205_G"]], "block": "p_battery"},
    {"d": "R215", "lcsc": "C26083", "fit": true, "pins": [["1", "1", "Q205_G"], ["2", "2", "RAW_BAT"]], "block": "p_battery"},
    {"d": "U204", "lcsc": "C2842389", "fit": true, "pins": [["1", "GND", "GND"], ["2", "OUT", "KEEP_ALIVE"], ["3", "IN", "RAW_BAT"]], "block": "p_battery"},
    {"d": "C214", "lcsc": "C19702", "fit": true, "pins": [["1", "1", "KEEP_ALIVE"], ["2", "2", "GND"]], "block": "p_battery"},
    {"d": "C215", "lcsc": "C1525", "fit": true, "pins": [["1", "1", "KEEP_ALIVE"], ["2", "2", "GND"]], "block": "p_battery"},
    {"d": "R216", "lcsc": "C22961", "fit": true, "pins": [["1", "1", "VBAT_SW"], ["2", "2", "BATT_SENSE"]], "block": "p_battery"},
    {"d": "R217", "lcsc": "C25803", "fit": true, "pins": [["1", "1", "BATT_SENSE"], ["2", "2", "GND"]], "block": "p_battery"},
    {"d": "C213", "lcsc": "C1525", "fit": true, "pins": [["1", "1", "BATT_SENSE"], ["2", "2", "GND"]], "block": "p_battery"},
    {"d": "R218", "lcsc": "C25879", "fit": true, "pins": [["1", "1", "BATT_SENSE"], ["2", "2", "BATT_ADC"]], "block": "p_battery"},
    {"d": "U205", "lcsc": "C107410", "fit": true, "pins": [["1", "32KHZ", "NC"], ["2", "VCC", "KEEP_ALIVE"], ["3", "INT/SQW", "RTC_INT_N"], ["4", "RST", "NC"], ["5", "GND", "GND"], ["6", "VBAT", "RTC_VBAT"], ["7", "SDA", "SYS_SDA"], ["8", "SCL", "SYS_SCL"]], "block": "p_rtc"},
    {"d": "C216", "lcsc": "C1525", "fit": true, "pins": [["1", "1", "KEEP_ALIVE"], ["2", "2", "GND"]], "block": "p_rtc"},
    {"d": "BT201", "lcsc": "C70381", "fit": true, "pins": [["+", "+", "RTC_VBAT"], ["-", "-", "GND"]], "block": "p_rtc"},
    {"d": "C217", "lcsc": "C1525", "fit": true, "pins": [["1", "1", "RTC_VBAT"], ["2", "2", "GND"]], "block": "p_rtc"},
    {"d": "R219", "lcsc": "C26083", "fit": true, "pins": [["1", "1", "RTC_INT_N"], ["2", "2", "KEEP_ALIVE"]], "block": "p_rtc"},
    {"d": "R220", "lcsc": "C25900", "fit": true, "pins": [["1", "1", "SYS_SDA"], ["2", "2", "3V3"]], "block": "p_rtc"},
    {"d": "R221", "lcsc": "C25900", "fit": true, "pins": [["1", "1", "SYS_SCL"], ["2", "2", "3V3"]], "block": "p_rtc"},
    {"d": "R222", "lcsc": "C26083", "fit": true, "pins": [["1", "1", "RTC_INT_N"], ["2", "2", "Q206_B"]], "block": "p_latch"},
    {"d": "Q206", "lcsc": "C20526", "fit": true, "pins": [["1", "B", "Q206_B"], ["2", "E", "GND"], ["3", "C", "RTC_WAKE"]], "block": "p_latch"},
    {"d": "R223", "lcsc": "C26083", "fit": true, "pins": [["1", "1", "RTC_WAKE"], ["2", "2", "KEEP_ALIVE"]], "block": "p_latch"},
    {"d": "Q207", "lcsc": "C8545", "fit": true, "pins": [["1", "G", "RTC_WAKE"], ["2", "S", "GND"], ["3", "D", "WAKE_N"]], "block": "p_latch"},
    {"d": "Q208", "lcsc": "C8545", "fit": true, "pins": [["1", "G", "PWR_HOLD"], ["2", "S", "GND"], ["3", "D", "WAKE_N"]], "block": "p_latch"},
    {"d": "R224", "lcsc": "C25741", "fit": true, "pins": [["1", "1", "PWR_HOLD"], ["2", "2", "GND"]], "block": "p_latch"},
    {"d": "Q209", "lcsc": "C8545", "fit": true, "pins": [["1", "G", "USB_WAKE"], ["2", "S", "GND"], ["3", "D", "WAKE_N"]], "block": "p_latch"},
    {"d": "R225", "lcsc": "C2906872", "fit": true, "pins": [["1", "1", "VBUS"], ["2", "2", "USB_WAKE"]], "block": "p_latch"},
    {"d": "R226", "lcsc": "C25741", "fit": true, "pins": [["1", "1", "USB_WAKE"], ["2", "2", "GND"]], "block": "p_latch"},
    {"d": "R227", "lcsc": "C25076", "fit": true, "pins": [["1", "1", "WAKE_N"], ["2", "2", "LATCH_LOGIC"]], "block": "p_latch"},
    {"d": "SW201", "lcsc": "C49234125", "fit": true, "pins": [["1", "1", "LATCH_LOGIC"], ["2", "2", "GND"]], "block": "p_latch"},
    {"d": "SW202", "lcsc": "C49023765", "fit": true, "pins": [["1", "1", "LATCH_LOGIC"], ["2", "2", "SYS_GATE"], ["3", "3", "NC"]], "block": "p_latch"},
    {"d": "Q210", "lcsc": "C15127", "fit": true, "pins": [["1", "G", "SYS_GATE"], ["2", "S", "RAW_BAT"], ["3", "D", "VBAT_SW"]], "block": "p_latch"},
    {"d": "R228", "lcsc": "C25741", "fit": true, "pins": [["1", "1", "SYS_GATE"], ["2", "2", "RAW_BAT"]], "block": "p_latch"},
    {"d": "C218", "lcsc": "C1622", "fit": true, "pins": [["1", "1", "SYS_GATE"], ["2", "2", "RAW_BAT"]], "block": "p_latch"},
    {"d": "C219", "lcsc": "C2977552", "fit": true, "pins": [["1", "1", "VBAT_SW"], ["2", "2", "GND"]], "block": "p_latch"},
    {"d": "C220", "lcsc": "C86295", "fit": true, "pins": [["1", "1", "VBAT_SW"], ["2", "2", "GND"]], "block": "p_latch"},
    {"d": "C221", "lcsc": "C1525", "fit": true, "pins": [["1", "1", "VBAT_SW"], ["2", "2", "GND"]], "block": "p_latch"},
    {"d": "U206", "lcsc": "C2845237", "fit": true, "pins": [["1", "EN", "VBAT_SW"], ["2", "MODE", "GND"], ["3", "AGND", "GND"], ["4", "FB", "FB_3V3"], ["5", "PG", "PG_3V3"], ["6", "VOUT", "3V3"], ["7", "L2", "BB_L2"], ["8", "GND", "GND"], ["9", "L1", "BB_L1"], ["10", "VIN", "VBAT_SW"]], "block": "p_3v3"},
    {"d": "L202", "lcsc": "C668312", "fit": true, "pins": [["1", "1", "BB_L1"], ["2", "2", "BB_L2"]], "block": "p_3v3"},
    {"d": "R230", "lcsc": "C23194", "fit": true, "pins": [["1", "1", "3V3"], ["2", "2", "FB_3V3"]], "block": "p_3v3"},
    {"d": "R231", "lcsc": "C23265", "fit": true, "pins": [["1", "1", "FB_3V3"], ["2", "2", "GND"]], "block": "p_3v3"},
    {"d": "R229", "lcsc": "C25741", "fit": true, "pins": [["1", "1", "PG_3V3"], ["2", "2", "3V3"]], "block": "p_3v3"},
    {"d": "C222", "lcsc": "C86295", "fit": true, "pins": [["1", "1", "VBAT_SW"], ["2", "2", "GND"]], "block": "p_3v3"},
    {"d": "C223", "lcsc": "C1525", "fit": true, "pins": [["1", "1", "VBAT_SW"], ["2", "2", "GND"]], "block": "p_3v3"},
    {"d": "C224", "lcsc": "C86295", "fit": true, "pins": [["1", "1", "3V3"], ["2", "2", "GND"]], "block": "p_3v3"},
    {"d": "C225", "lcsc": "C86295", "fit": true, "pins": [["1", "1", "3V3"], ["2", "2", "GND"]], "block": "p_3v3"},
    {"d": "C226", "lcsc": "C1525", "fit": true, "pins": [["1", "1", "3V3"], ["2", "2", "GND"]], "block": "p_3v3"},
    {"d": "U207", "lcsc": "C15483", "fit": true, "pins": [["1", "VINA", "VBAT_SW"], ["2", "GND", "GND"], ["3", "FB", "FB_M"], ["4", "VOUT", "VMODEM"], ["5", "VOUT", "VMODEM"], ["6", "L2", "M_L2"], ["7", "L2", "M_L2"], ["8", "L1", "M_L1"], ["9", "L1", "M_L1"], ["10", "VIN", "VBAT_SW"], ["11", "VIN", "VBAT_SW"], ["12", "EN", "MODEM_EN_F"], ["13", "PS/SYNC", "M_PS"], ["14", "PG", "MODEM_PG"], ["EP", "PGND", "GND"]], "block": "p_modem"},
    {"d": "L203", "lcsc": "C53896855", "fit": true, "pins": [["1", "1", "M_L1"], ["2", "2", "M_L2"]], "block": "p_modem"},
    {"d": "R232", "lcsc": "C2909377", "fit": true, "pins": [["1", "1", "VMODEM"], ["2", "2", "FB_M"]], "block": "p_modem"},
    {"d": "C227", "lcsc": "C325453", "fit": true, "pins": [["1", "1", "VMODEM"], ["2", "2", "FB_M"]], "block": "p_modem"},
    {"d": "R233", "lcsc": "C25741", "fit": true, "pins": [["1", "1", "FB_M"], ["2", "2", "GND"]], "block": "p_modem"},
    {"d": "R234", "lcsc": "C2906860", "fit": true, "pins": [["1", "1", "MODEM_EN"], ["2", "2", "MODEM_EN_F"]], "block": "p_modem"},
    {"d": "R235", "lcsc": "C25741", "fit": true, "pins": [["1", "1", "MODEM_EN"], ["2", "2", "GND"]], "block": "p_modem"},
    {"d": "R236", "lcsc": "C25741", "fit": true, "pins": [["1", "1", "M_PS"], ["2", "2", "VBAT_SW"]], "block": "p_modem"},
    {"d": "R237", "lcsc": "C25744", "fit": true, "pins": [["1", "1", "MODEM_PG"], ["2", "2", "3V3"]], "block": "p_modem"},
    {"d": "C228", "lcsc": "C19702", "fit": true, "pins": [["1", "1", "VBAT_SW"], ["2", "2", "GND"]], "block": "p_modem"},
    {"d": "C229", "lcsc": "C1525", "fit": true, "pins": [["1", "1", "VBAT_SW"], ["2", "2", "GND"]], "block": "p_modem"},
    {"d": "C230", "lcsc": "C86295", "fit": true, "pins": [["1", "1", "VMODEM"], ["2", "2", "GND"]], "block": "p_modem"},
    {"d": "C231", "lcsc": "C86295", "fit": true, "pins": [["1", "1", "VMODEM"], ["2", "2", "GND"]], "block": "p_modem"},
    {"d": "C232", "lcsc": "C86295", "fit": true, "pins": [["1", "1", "VMODEM"], ["2", "2", "GND"]], "block": "p_modem"},
    {"d": "C233", "lcsc": "C2977552", "fit": true, "pins": [["1", "1", "VMODEM"], ["2", "2", "GND"]], "block": "p_modem"},
    {"d": "C234", "lcsc": "C1525", "fit": true, "pins": [["1", "1", "VMODEM"], ["2", "2", "GND"]], "block": "p_modem"},
    {"d": "D205", "lcsc": "C46956328", "fit": true, "pins": [["K", "K", "VMODEM"], ["A", "A", "GND"]], "block": "p_modem"},
    {"d": "TP201", "lcsc": "", "fit": true, "pins": [["1", "TP", "SOLAR_IN"]], "block": "p_test", "prefix": "TP"},
    {"d": "TP202", "lcsc": "", "fit": true, "pins": [["1", "TP", "MPPT"]], "block": "p_test", "prefix": "TP"},
    {"d": "TP203", "lcsc": "", "fit": true, "pins": [["1", "TP", "CHG_SW"]], "block": "p_test", "prefix": "TP"},
    {"d": "TP204", "lcsc": "", "fit": true, "pins": [["1", "TP", "CHARGE_SENSE"]], "block": "p_test", "prefix": "TP"},
    {"d": "TP205", "lcsc": "", "fit": true, "pins": [["1", "TP", "TEMP_FAULT_N"]], "block": "p_test", "prefix": "TP"},
    {"d": "TP206", "lcsc": "", "fit": true, "pins": [["1", "TP", "RAW_BAT"]], "block": "p_test", "prefix": "TP"},
    {"d": "TP207", "lcsc": "", "fit": true, "pins": [["1", "TP", "KEEP_ALIVE"]], "block": "p_test", "prefix": "TP"},
    {"d": "TP208", "lcsc": "", "fit": true, "pins": [["1", "TP", "RTC_INT_N"]], "block": "p_test", "prefix": "TP"},
    {"d": "TP209", "lcsc": "", "fit": true, "pins": [["1", "TP", "SYS_GATE"]], "block": "p_test", "prefix": "TP"},
    {"d": "TP210", "lcsc": "", "fit": true, "pins": [["1", "TP", "VBAT_SW"]], "block": "p_test", "prefix": "TP"},
    {"d": "TP211", "lcsc": "", "fit": true, "pins": [["1", "TP", "3V3"]], "block": "p_test", "prefix": "TP"},
    {"d": "TP212", "lcsc": "", "fit": true, "pins": [["1", "TP", "VMODEM"]], "block": "p_test", "prefix": "TP"},
    {"d": "TP213", "lcsc": "", "fit": true, "pins": [["1", "TP", "GND"]], "block": "p_test", "prefix": "TP"},
  ];
  const BLOCKS = [["p_solar", "Block 1 \u00b7 Panel input"], ["p_charger", "Block 2 \u00b7 Solar charger (U201 CN3791)"], ["p_temp", "Block 3 \u00b7 Charge temperature cut-out"], ["p_battery", "Block 4 \u00b7 Battery input, keep-alive rail and battery sense"], ["p_rtc", "Block 5 \u00b7 RTC"], ["p_latch", "Block 5 \u00b7 Wake latch and main switch"], ["p_3v3", "Block 6 \u00b7 Main 3.3 V"], ["p_modem", "Block 6 \u00b7 Modem 3.9 V"], ["p_test", "Test points"]];
  const TEMPLATE_PREFIXES = ["TP"];
  const NC = "NC";

  const CFG = {
    grid: 5,          // schematic coordinates are in 10 mil units
    stub: 30,         // shortest wire stub from a pin
    charW: 6,         // estimated width of one net-name character
    padX: 30,         // room around each part for its pins' wires
    padY: 40,         // room above and below each part for designator and value text
    blockW: 900,      // width a block packs its parts into before starting a new row
    blockGap: 150,    // space between blocks
    pageW: 3200,      // width before blocks wrap to a new row
    titleH: 60,       // band at the top of each block box for its heading
    headingY: 40,     // heading baseline below the top of the box
    headingSize: 20,  // heading font size, bold
    headingCharW: 13, // estimated width of one heading character
    boxLine: 2,       // block box line width (1-10)
    down: 1,          // direction rows advance in: +1 = y grows downwards, as in EasyEDA Pro 3.2 (checked on the AURIS project)
    origin: [0, 0],   // top left corner of the first block
  };

  const sch = eda.sch_PrimitiveComponent;
  const errors = [], warnings = [];
  let nParts = 0, nCells = 0, nWires = 0, nNC = 0;
  const log = (m) => console.log(`[auris ${SHEET}] ${m}`);
  const toast = (m) => { log(m); try { eda.sys_ToastMessage.showMessage(m); } catch (_) { /* no toast in this version */ } };
  const snap = (v) => Math.round(v / CFG.grid) * CFG.grid;
  const msg = (e) => (e && e.message) || String(e);
  const tryCall = async (fn) => { try { return await fn(); } catch (_) { return undefined; } };
  let decorError = null;   // boxes and headings are drawing only: report the first failure once
  const decor = async (fn) => {
    try { if ((await fn()) === undefined) decorError = decorError || "EasyEDA returned nothing"; }
    catch (e) { decorError = decorError || msg(e); }
  };
  async function call(what, fn) {
    try {
      const r = await fn();
      if (r === undefined || r === false) errors.push(`${what}: EasyEDA returned nothing`);
      return r;
    } catch (e) {
      errors.push(`${what}: ${msg(e)}`);
      return undefined;
    }
  }

  // ---- what is on the page already ----------------------------------------
  const wanted = new Set(PARTS.map((p) => p.d));
  const present = new Set();
  const templates = {};
  let farthest = null;   // the existing sheet part farthest along CFG.down
  for (const c of (await tryCall(() => sch.getAll())) || []) {
    const des = c.getState_Designator && c.getState_Designator();
    if (!des) continue;
    if (wanted.has(des)) {
      present.add(des);
      const y = c.getState_Y();
      if (farthest === null || (y - farthest) * CFG.down > 0) farthest = y;
      continue;
    }
    for (const pre of TEMPLATE_PREFIXES) {
      if (!templates[pre] && new RegExp(`^${pre}\\d*\\??$`).test(des)) templates[pre] = c;
    }
  }

  // ---- library parts --------------------------------------------------------
  const devices = new Map();
  const notFound = new Map();   // LCSC code -> designators
  const fromTemplate = new Map();   // template designator -> designators copied from it
  async function deviceFor(part) {
    if (!part.lcsc) {
      const t = templates[part.prefix];
      if (!t) {
        errors.push(`${part.d}: no LCSC code, and no ${part.prefix} template part on the page to copy`);
        return undefined;
      }
      const td = t.getState_Designator();
      fromTemplate.set(td, [...(fromTemplate.get(td) || []), part.d]);
      return t.getState_Component();
    }
    if (!devices.has(part.lcsc)) {
      let dev;
      try { dev = await eda.lib_Device.getByLcscIds(part.lcsc); } catch (e) { dev = undefined; }
      devices.set(part.lcsc, dev);
    }
    const dev = devices.get(part.lcsc);
    if (!dev) notFound.set(part.lcsc, [...(notFound.get(part.lcsc) || []), part.d]);
    return dev;
  }

  // ---- pins -----------------------------------------------------------------
  const pinInfo = (p) => ({
    obj: p,
    num: String(p.getState_PinNumber()),
    name: String(p.getState_PinName() ?? ""),
    x: p.getState_X(),
    y: p.getState_Y(),
    rot: (((p.getState_Rotation() || 0) % 360) + 360) % 360,
  });
  const pinsOf = async (comp) =>
    ((await tryCall(() => sch.getAllPinsByPrimitiveId(comp.getState_PrimitiveId()))) || []).map(pinInfo);

  // Match netlist rows to symbol pins: by number first, then by pin name. A name shared by
  // several symbol pins (four GND pins on a USB-C socket) is only used when every netlist row
  // with that name is on the same net, so it does not matter which pin each row gets.
  function match(part, cells) {
    const pins = cells.flatMap((cell, i) => cell.pins.map((p) => Object.assign(p, { cell: i })));
    const byNum = new Map();
    for (const p of pins) if (!byNum.has(p.num)) byNum.set(p.num, p);
    const used = new Set(), links = [], missing = [], byName = [];
    for (const [num, name, net] of part.pins) {
      let p = byNum.get(num);
      if (!p || used.has(p)) {
        const c = pins.filter((q) => !used.has(q) && (q.name === name || q.name === num || q.num === name));
        const oneNet = part.pins.filter((r) => r[1] === name).every((r) => r[2] === net);
        p = c.length === 1 || (c.length > 1 && oneNet) ? c[0] : undefined;
        if (p) byName.push(`${num} as symbol pin ${p.num}`);
      }
      if (!p) { missing.push(name && name !== num ? `${num} (${name})` : num); continue; }
      used.add(p);
      links.push({ cell: p.cell, num: p.num, name: p.name, net, pin: p });
    }
    const extra = pins.filter((p) => !used.has(p)).map((p) => p.num);
    return { links, missing, extra, byName };
  }

  // A wire stub leaves each pin away from the middle of the symbol.
  function outward(p, cx, cy) {
    if (p.rot === 0 || p.rot === 180) return [Math.sign(p.x - cx) || (p.rot === 0 ? -1 : 1), 0];
    return [0, Math.sign(p.y - cy) || (p.rot === 90 ? -1 : 1)];
  }
  const stubLen = (net) => (net === NC ? 0 : Math.ceil(Math.max(CFG.stub, CFG.charW * net.length + 10) / 10) * 10);

  // Box around a symbol's pins and their stubs, relative to the symbol origin.
  function cellBox(cell, links) {
    const ox = cell.comp.getState_X(), oy = cell.comp.getState_Y();
    const ps = cell.pins;
    if (!ps.length) return { l: -40, r: 40, lo: -40, hi: 40 };
    const xs = ps.map((p) => p.x), ys = ps.map((p) => p.y);
    let minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
    const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2;
    for (const l of links) {
      [l.ux, l.uy] = outward(l.pin, cx, cy);
      const len = stubLen(l.net);
      minX = Math.min(minX, l.pin.x + l.ux * len); maxX = Math.max(maxX, l.pin.x + l.ux * len);
      minY = Math.min(minY, l.pin.y + l.uy * len); maxY = Math.max(maxY, l.pin.y + l.uy * len);
    }
    return { l: minX - CFG.padX - ox, r: maxX + CFG.padX - ox, lo: minY - CFG.padY - oy, hi: maxY + CFG.padY - oy };
  }

  // ---- place one part (all of its symbol parts) at a staging spot ----------
  const STAGE = [CFG.origin[0] - 4000, CFG.origin[1]];
  async function stagePart(part) {
    const dev = await deviceFor(part);
    if (!dev) return undefined;
    const first = await call(`${part.d}: place`, () => sch.create(dev, STAGE[0], STAGE[1], undefined, 0, false, part.fit, true));
    if (!first) return undefined;
    const cells = [{ comp: first, pins: await pinsOf(first) }];
    let res = match(part, cells);
    // Multi-part symbols (e.g. a dual op-amp) are named NAME.1, NAME.2, ...: add parts until every pin is found.
    const m = String((first.getState_SubPartName && first.getState_SubPartName()) || "").match(/^(.*)\.(\d+)$/);
    for (let k = m ? Number(m[2]) + 1 : 0; m && res.missing.length && k <= 16; k++) {
      const c = await tryCall(() => sch.create(dev, STAGE[0], STAGE[1] + CFG.down * 600 * cells.length, `${m[1]}.${k}`, 0, false, part.fit, true));
      if (!c) break;
      cells.push({ comp: c, pins: await pinsOf(c) });
      res = match(part, cells);
    }
    const tag = part.lcsc ? `${part.d} (${part.lcsc})` : part.d;
    if (res.missing.length) errors.push(`${tag}: netlist pins not on the EasyEDA symbol: ${res.missing.join(", ")}`);
    if (res.extra.length) warnings.push(`${tag}: symbol pins not in the netlist, left unconnected: ${res.extra.join(", ")}`);
    if (res.byName.length) warnings.push(`${tag}: matched by pin name: ${res.byName.join(", ")}`);
    return { cells, links: res.links };
  }

  // ---- move a staged symbol into place and wire its pins -------------------
  async function finishCell(part, cell, i, links, ox, oy) {
    const id = cell.comp.getState_PrimitiveId();
    const moved = await call(`${part.d}: move and set designator`, () =>
      sch.modify(id, { x: ox, y: oy, designator: part.d, addIntoBom: part.fit, addIntoPcb: true }));
    if (!moved) return;
    nCells++;
    const pins = await pinsOf(cell.comp);
    for (const l of links.filter((l) => l.cell === i)) {
      const p = pins.find((q) => q.num === l.num && q.name === l.name);
      if (!p) { errors.push(`${part.d} pin ${l.num}: not found after moving the part`); continue; }
      if (l.net === NC) {
        try { p.obj.setState_NoConnected(true); await p.obj.done(); nNC++; }
        catch (e) { warnings.push(`${part.d} pin ${l.num}: could not set the no-connect flag (${msg(e)})`); }
        continue;
      }
      const len = stubLen(l.net);
      const ex = p.x + l.ux * len, ey = p.y + l.uy * len;
      // Start the wire at its left (or lower) end, where EasyEDA anchors the net name.
      const line = l.ux < 0 || l.uy < 0 ? [ex, ey, p.x, p.y] : [p.x, p.y, ex, ey];
      const w = await call(`${part.d} pin ${l.num} to ${l.net}`, () => eda.sch_PrimitiveWire.create(line, l.net));
      if (w) nWires++;
    }
  }

  // ---- lay out block by block ----------------------------------------------
  const page = { x: CFG.origin[0], y: farthest === null ? CFG.origin[1] : farthest + CFG.down * 800, rowH: 0 };
  for (const [block, title] of BLOCKS) {
    const parts = PARTS.filter((p) => p.block === block && !present.has(p.d));
    if (!parts.length) continue;
    if (page.x > CFG.origin[0] && page.x + CFG.blockW > CFG.origin[0] + CFG.pageW) {
      page.x = CFG.origin[0];
      page.y += CFG.down * (page.rowH + CFG.blockGap);
      page.rowH = 0;
    }
    const bx = page.x, by = page.y;
    const heading = PARTS.some((p) => p.block === block && present.has(p.d)) ? `${title} (continued)` : title;
    toast(`Auris ${SHEET}: placing ${heading} (${parts.length} parts)`);
    let rx = bx, ry = by + CFG.down * CFG.titleH, rowH = 0, width = 0;
    for (const part of parts) {
      const staged = await stagePart(part);
      if (!staged) continue;
      nParts++;
      for (const [i, cell] of staged.cells.entries()) {
        const box = cellBox(cell, staged.links.filter((l) => l.cell === i));
        const w = box.r - box.l, h = box.hi - box.lo;
        if (rx > bx && rx + w > bx + CFG.blockW) {
          rx = bx;
          ry += CFG.down * rowH;
          rowH = 0;
        }
        const top = CFG.down < 0 ? box.hi : box.lo;
        await finishCell(part, cell, i, staged.links, snap(rx - box.l), snap(ry - top));
        rx += w;
        rowH = Math.max(rowH, h);
        width = Math.max(width, rx - bx);
      }
    }
    // Box the block with its heading inside the top edge, as the hardware guide shows it.
    // The box's top left corner is (bx, by) and it extends right and in the CFG.down direction.
    const boxW = snap(Math.max(width, heading.length * CFG.headingCharW + 2 * CFG.padX));
    const boxH = snap(Math.abs(ry - by) + rowH);
    await decor(() => eda.sch_PrimitiveRectangle.create(bx, by, boxW, boxH, 0, 0, null, "none", CFG.boxLine));
    await decor(() => eda.sch_PrimitiveText.create(bx + CFG.padX, by + CFG.down * CFG.headingY, heading, 0, null, null, CFG.headingSize, true));
    page.x = bx + boxW + CFG.blockGap;
    page.rowH = Math.max(page.rowH, boxH);
  }

  // ---- report ---------------------------------------------------------------
  for (const [code, ds] of notFound) errors.unshift(`${code} not found in the EasyEDA library, not placed: ${ds.join(", ")}`);
  if (decorError) warnings.push(`Some block boxes or headings were not drawn: ${decorError}`);
  for (const [td, ds] of fromTemplate) {
    warnings.push(`${ds.join(", ")}: copied from template ${td}, so check value and footprint. Delete ${td} when done.`);
  }
  const head = [`${SHEET} sheet: placed ${nParts} parts (${nCells} symbols), ${nWires} net wires, ${nNC} no-connect flags.`];
  if (present.size) head.push(`Skipped ${present.size} parts already on the page.`);
  const show = (title, list, max) =>
    list.length ? ["", `${title} (${list.length}):`, ...list.slice(0, max), ...(list.length > max ? [`...and ${list.length - max} more in the browser console`] : [])] : [];
  const report = [...head, ...show("Errors", errors, 25), ...show("Warnings", warnings, 10)].join("\n");
  log([...head, ...show("Errors", errors, 1e9), ...show("Warnings", warnings, 1e9)].join("\n"));
  try { eda.sys_Dialog.showInformationMessage(report, `Auris capture: ${SHEET}`); } catch (_) { toast(head[0]); }
})().catch((e) => {
  const m = `Auris capture stopped: ${(e && e.stack) || e}`;
  console.error(m);
  try { eda.sys_Dialog.showInformationMessage(m, "Auris capture"); } catch (_) { /* console only */ }
});
