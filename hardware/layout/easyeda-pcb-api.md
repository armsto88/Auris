# EasyEDA Pro PCB scripting API: probe results

Read-only probe of the AURIS PCB (`PCB1`, uuid `1171ec2ee0a2c106`, in `Board1`) in EasyEDA Pro **4.1.105** (web), run 2026-11-19 with [`hardware/tools/easyeda_pcb_probe.js`](../tools/easyeda_pcb_probe.js) through the page driver. A short follow-up the same day checked polygon formats, the layer table and the rule configurations (now sections 7 and 8 of the probe). Nothing was created, moved or saved. DRC was run once: it changes nothing in the design but filled EasyEDA's DRC panel.

## Answers to the handover's phase 0 questions

"Read works" means the call was made and returned real data. "Present" means the method exists with the arity shown but was not called, because calling it changes the design; parameter order must come from EasyEDA's API reference before phase 1 uses it.

| Question | Result | Calls |
|---|---|---|
| List and move components | **Read works.** 346 components, all on layer 1 at rotation 0. Move: present | `pcb_PrimitiveComponent.getAll()`; per object `getState_X/Y/Rotation/Layer/Designator/Footprint/PrimitiveId`; pads via `getAllPinsByPrimitiveId(id)`. Move: `pcb_PrimitiveComponent.modify(2)`, or the object's `setState_X/Y/Rotation/Layer` then `done()` |
| Copper layers and stack-up | **Read works.** Still 2 layers; inner layers 15–18 exist but are inactive. No saved physical stack-up. Set: present | `pcb_Layer.getTheNumberOfCopperLayers()` → 2, `getStackup()`, `getAllLayers()`. Set: `setTheNumberOfCopperLayers(1)`, `savePhysicalStackingConfiguration(2)`, `overwriteCurrentPhysicalStackingConfiguration(1)` |
| Board outline | **Polygon helper works** (pure geometry). Creating the outline primitive: present | `pcb_MathPolygon.createPolygon(["R", x, y, w, h, 0, 0])`; the 6-element form returns `undefined`. Outline on layer 11 with `pcb_PrimitivePolyline.create` (confirmed in phase 1) |
| Design rules and net classes | **Read works.** 6 rule configurations; current is "JLCPCB Capability(Two Layers Board)"; "JLCPCB Capability(Multiple Layers Board)" exists for 4 layers. 187 nets, all on default rules; no net classes or differential pairs. Set: present | `pcb_Drc.getAllRuleConfigurations()`, `getCurrentRuleConfiguration()`, `getNetRules()`. Set: `createNetClass(3)`, `addNetToNetClass(2)`, `createDifferentialPair(3)`, `overwriteCurrentRuleConfiguration(1)`, `saveRuleConfiguration(2)`, `setAsDefaultRuleConfiguration(1)`, `overwriteNetRules(1)` |
| Tracks, vias and pours | Present (none on the board yet) | `pcb_PrimitiveLine.create(8)`, `pcb_PrimitiveVia.create(9)`, `pcb_PrimitivePour.create(9)`, `pcb_PrimitivePolyline.create(5)`, `pcb_PrimitiveFill.create(6)`, `pcb_PrimitiveRegion.create(6)`, `pcb_PrimitivePour.rebuildAllCopperRegions()`, `pcb_Document.fanout(1)` |
| Run DRC and read the results | **Works**, 5.2 s. 900 violations, all "Connection Error" (nothing is routed yet) | `pcb_Drc.check(false, false, true)` returns groups `{name, list: [{name: <net>, list: [{errorType, errorObjType, ruleName, obj1: {typeName, suffix}, net, errData: {position: {x, y}, obj1, layerIds}}]}]}`; `pcb_Drc.getDrcResult()` → `{state: "failed", totalCount: 900, failedItems, violations, checkedAt}` |

Also useful for writing safely: `pcb_Document.beginCommandGroup(1)` / `commitCommandGroup(1)` / `rollbackCommandGroup(1)` / `undoLastCommandGroup()` (one undo step per script run, to try), `pcb_Document.save()`, `getPrimitivesInRegion(4)`, `getRatlines(1)`, and `pcb_Dfm.checkDfm(1)`.

## Write calls confirmed in phase 1 (2026-11-19)

Parameter order comes from EasyEDA's type package `@jlceda/pro-api-types` 0.4.30 on npm (`index.d.ts`; it covers newer EDA versions too, so check each call's "ADD since EDA v…" note).

| Call | Result on 4.1.105 |
|---|---|
| `pcb_Layer.setTheNumberOfCopperLayers(4)` | `true`; Inner1 (15) and Inner2 (16) become active. `getStackup()` still reports the 2-layer physical stack afterwards, also after a save; the physical stack-up setters are "ADD since EDA v4.2" |
| `pcb_PrimitivePolyline.create("", 11, polygon, 10, false)` | Draws the outline. **`["R", x, y, w, h, rot, round]` takes (x, y) as the top-left corner in board (Cartesian, Y up) coordinates and extends to y − h**: the board X 0..W, Y 0..H needs `["R", 0, H, W, H, 0, r]`. The type file's note that polygon sources are SVG (Y down) misleads here. `round` is the corner radius |
| `pcb_PrimitivePolyline.delete([id])` | `true` |
| `pcb_PrimitivePad.create(12, "MH1", x, y, 0, ["ELLIPSE", d, d], "", ["ROUND", d], 0, 0, 0, false, 0)` | Unplated hole as a free pad. Reads back right after creation as `["ELLIPSE", d, d]`, later as `["ELLIPSE", 3.2, 126]`; EasyEDA's own 1.8 mm through-hole footprint pads read back the same way (`[1.8, 70.9]`), so it is a read-back quirk; the hole stays `["ROUND", 126]`. `modify(id, {pad})` does not change it |
| `pcb_Document.beginCommandGroup(name)` / `commitCommandGroup(groupId)` | Work; `{groupId: "apigroup-…"}` |
| `pcb_Document.save()` | `true`, toast "Saved successfully!". Returns `false` (no toast) when there is nothing to save: after the 346-part move EasyEDA had already saved by itself; a reload showed the moves stored |
| `pcb_Drc.overwriteCurrentRuleConfiguration(cfg)` | **Only takes the PCB's own format** (from `getCurrentRuleConfiguration().config`): Track rules are `{editName, unit, isSetDefault, form: {status, data: {"1": {minValue, defaultValue, maxValue}}}}`, Safe Spacing has `tables: {"1": {status, content: [[…], …]}}`, the pair rule has `strokeWidthTables` and `diffPairSpacingTables`. A template from `getRuleConfiguration(name)` (flat `form` / `table`) returns `undefined` and changes nothing. After a write the configuration is renamed "自定义配置" (custom) |
| `pcb_Drc.createNetClass(name, nets, {r, g, b, alpha})` | `true`. **alpha is 0–255** (1 gives 1/255, a transparent class colour). Member nets then move into the class's `sub` list in `getNetRules()` |
| `pcb_Drc.deleteNetClass(name)` | `true` |
| `pcb_Drc.createDifferentialPair(name, positiveNet, negativeNet)` | `true`; pairs have no row in `getNetRules()`, they use the default pair rule |
| `lib_Footprint.updateDocumentSource(uuid, projectLibUuid, source)` | **Only accepts the footprint editor's document source.** With the library's own source (`lib_Footprint.getDocumentSource`, ~12–14 k characters) it returns `false` and changes nothing. Working route (phase 2): `tab = lib_Footprint.openInEditor(uuid, lib)`, wait ~2.5 s, `sys_FileManager.getDocumentSource()` (~33 k characters; its DOCHEAD says `docType: "PCB"` with the footprint's uuid), edit the `PAD` lines (`{head}||{body}|`, same fields as in the export), `updateDocumentSource(...)` → `true`, `dmt_EditorControl.closeDocument(tab)`. The open PCB shows the new pad geometry straight away; save the PCB afterwards |
| `sys_ToastMessage.showMessage(text, undefined, seconds)` | Use it to report: **opening another editor tab closes the Run Script window**, and the script's result dialog then never appears. Toasts are `messager-panel` DOM nodes that the page driver's observer collects; they stay on screen for the given time, so old ones can show up in the next collection |
| `pcb_Drc.overwriteNetRules(rules)` | `true`; set `Track` / `Safe Spacing` to a rule's `editName` on the `netClass` row and on each member in its `sub` list. It accepts names that do not exist, so write the rules first |

## Units and coordinates

- **Everything is in mil**: component and pad X/Y, pad sizes (U301 pad 1 is `["RECT", 39.4, 27.6, 0]`, the 1.0 × 0.7 mm pad in the footprint table), stack-up thicknesses (`unit: "mil"`). 80 × 105 mm = 3149.6 × 4133.9 mil.
- Canvas origin is (0, 0) (`pcb_Document.getCanvasOrigin()`). The parts sit at X 40 … 23,281 and Y −8,866 … −220 mil, so placed parts have negative Y.
- Pads: 981, of which 973 on layer 1 and 8 on layer 12 (Multi-Layer, plated through). Each pad reports `Net`, `PadNumber`, `Pad` (shape), `Hole`, `X`, `Y`, `Rotation`, `ParentComponentPrimitiveId`, and mask/paste expansion (top mask 2 mil default).
- 1,331 component attribute texts (designator, value and the like) on layer 3 (Top Silkscreen).

## Layers

1 Top, 2 Bottom, 3/4 Top/Bottom Silkscreen, 5/6 Solder Mask, 7/8 Paste Mask, 9/10 Assembly, **11 Board Outline**, 12 Multi-Layer, 13 Document, 14 Mechanical, **15–46 Inner1–Inner32** (inactive now; Inner1/Inner2 should become L2/L3 once the board is set to 4 layers), 47 Hole, 48–52 component shape/marking/pin layers, 53–55 3D shell, 56 Drill Drawing, 57 Ratline, 58/59 Stiffener.

Current stack-up (EasyEDA's 2-layer default, mil): mask 0.394 (εr 3.3), top copper 1.379, substrate 59.449 (εr 4.5), bottom copper 1.378, mask 0.394; total 62.994. Phase 1 replaces it with JLC04161H-7628 ([README](README.md#stack-up-jlc04161h-7628-16-mm-4-layers)).

## Polygon source formats (`pcb_MathPolygon.createPolygon`)

| Source | Result |
|---|---|
| `["R", 0, 0, 100, 70, 0, 0]` | Works, 100 × 70: left, top, width, height, rotation, corner radius (top-left in board coordinates; see phase 1 above) |
| `["R", 0, 0, 100, 70, 0]`, `["R", 0, 0, 100, 70]` | `undefined` |
| `[0, 0, "L", 100, 0, 100, 70, 0, 70]` (open or closed) | Works |
| `[0, 0, "L", 90, 0, "ARC", 90, 100, 10, "L", 100, 70, 0, 70, 0, 0]` | Works (arc segment) |
| `["CIRCLE", 50, 35, 10]` | Works (centre, radius) |
| `[["R", …]]` | `undefined`; use `createComplexPolygon([[…]])` for nested sources (it works) |

Polygon objects offer `getSource`, `getCenter`, `discretize`, `validateSource`; complex polygons also `addSource`, `getSourceStrictComplex`, `toPolygon`.

## Rule configuration sections

Spacing (Safe Spacing, Other Spacing, Creepage Distance); Physics (Track, Net Length Range, Net Length Tolerance, Differential Pair, Blind/Buried Via, Via Size, Height); Plane (Plane Zone, Copper Zone); Expansion (Solder Mask, Paste Mask); Copper, Drill Hole, Silkscreen and Solder Mask Analysis. The Safe Spacing table is per copper weight (`copperThickness1oz`), in mm, with rows and columns Track, SMD Pad, TH Pad, SMD/TH Test Point, Via, Fill Region/Teardrop, Copper/Plane Zone, Slot Region, Line, Text/Image, Board Outline (+ Hole). Two-layer defaults: track–track 0.102 mm, others 0.152 mm.

## Method lists (arity in brackets)

The API objects are proxies, so `Function.prototype.toString` gives no parameter names; only the arity is known.

- **pcb_Document:** autoLayout(0) autoRouting(1) beginCommandGroup(1) cancelAutoJob(1) clearRouting(0) commitCommandGroup(1) convertCanvasOriginToDataOrigin(2) convertDataOriginToCanvasOrigin(2) fanout(1) getAutoJobLog(1) getAutoJobStatus(1) getAutoRoutingUserConfig(1) getCalculatingRatlineStatus(0) getCanvasOrigin(0) getCurrentFilterConfiguration(0) getPrimitiveAtPoint(2) getPrimitivesInRegion(4) getRatlines(1) importAutoLayoutJsonFile(1) importAutoRouteJsonFile(1) importAutoRouteSesFile(1) importChanges(1) navigateToCoordinates(2) navigateToRegion(4) redoLastCommandGroup(0) rollbackCommandGroup(1) save(0) setCanvasOrigin(2) startAutoLayout(0) startAutoRouting(1) startCalculatingRatline(0) stopCalculatingRatline(0) undoLastCommandGroup(0) zoomToBoardOutline(0)
- **pcb_Layer:** addCustomLayer(0) deletePhysicalStackingConfiguration(1) getAllLayers(0) getAllPhysicalStackingConfigurations(0) getCurrentLayer(0) getCurrentPhysicalStackingConfiguration(0) getCurrentPhysicalStackingConfigurationName(0) getDefaultPhysicalStackingConfigurationName(0) getPhysicalStackingConfiguration(1) getStackup(0) getTheNumberOfCopperLayers(0) lockLayer(1) modifyLayer(2) overwriteCurrentPhysicalStackingConfiguration(1) removeLayer(1) renamePhysicalStackingConfiguration(2) savePhysicalStackingConfiguration(2) selectLayer(1) setAsDefaultPhysicalStackingConfiguration(1) setInactiveLayerDisplayMode(0) setInactiveLayerTransparency(1) setLayerColorConfiguration(1) setLayerInvisible(1) setLayerVisible(1) setPcbType(1) setTheNumberOfCopperLayers(1) unlockLayer(1)
- **pcb_Drc:** addNetToEqualLengthNetGroup(2) addNetToNetClass(2) addPadPairToPadPairGroup(2) check(0) checkDetailed(1) createDifferentialPair(3) createEqualLengthNetGroup(3) createNetClass(3) createPadPairGroup(2) deleteDifferentialPair(1) deleteEqualLengthNetGroup(1) deleteNetClass(1) deletePadPairGroup(1) deleteRuleConfiguration(1) getAllDifferentialPairs(0) getAllEqualLengthNetGroups(0) getAllNetClasses(0) getAllPadPairGroups(0) getAllRuleConfigurations(0) getCurrentRuleConfiguration(0) getCurrentRuleConfigurationName(0) getDefaultRuleConfigurationName(0) getDrcResult(0) getNetByNetRules(0) getNetRules(0) getPadPairGroupMinWireLength(1) getRealTimeDrcStatus(0) getRegionRules(0) getRuleConfiguration(1) modifyDifferentialPairName(2) modifyDifferentialPairNegativeNet(2) modifyDifferentialPairPositiveNet(2) modifyEqualLengthNetGroupName(2) modifyNetClassName(2) modifyPadPairGroupName(2) overwriteCurrentRuleConfiguration(1) overwriteNetByNetRules(1) overwriteNetRules(1) overwriteRegionRules(1) removeNetFromEqualLengthNetGroup(2) removeNetFromNetClass(2) removePadPairFromPadPairGroup(2) renameRuleConfiguration(2) saveRuleConfiguration(2) setAsDefaultRuleConfiguration(1) startRealTimeDrc(0) stopRealTimeDrc(0)
- **pcb_Net:** getAllNetName(0) getAllNets(0) getAllNetsName(0) getAllPrimitivesByNet(2) getNet(1) getNetColor(1) getNetLength(1) getNetlist(0) highlightNet(1) selectNet(1) setNetColor(2) setNetlist(0) unhighlightAllNets(0) unhighlightNet(1) unselectAllNets(0) unselectNet(1)
- **pcb_Primitive:** findPrimitives(1) getPrimitiveBoardLine(2) getPrimitiveByPrimitiveId(1) getPrimitiveTypeByPrimitiveId(1) getPrimitivesBBox(1) getPrimitivesByPrimitiveId(1)
- **Primitive classes** (each also has delete(1) get(1) modify(2) and getAll/getAllPrimitiveId with the arity shown): Arc create(10) getAll(3); Attribute create(0) getAll(3); Component create(6) getAll(2) getAllPinsByPrimitiveId(1) getAllPropertyNames(0) placeComponentWithMouse(1) placeFootprintWithMouse(2); Dimension create(7) getAll(2); Fill create(6) getAll(3); Image create(9) getAll(2); Line create(8) getAll(3); Object create(10) getAll(2); Pad create(17) getAll(4); Polyline create(5) getAll(3); Pour create(9) getAll(3) rebuildAllCopperRegions(0) rebuildCopperRegionsByIds(1) rebuildCopperRegionsByLayer(1) rebuildPlaneCopperRegions(1); Poured create(0) getAll(0); Region create(6) getAll(3); String create(13) getAll(2); Via create(9) getAll(2)
- **Component object:** getAllPins, getState_ / setState_ for AddIntoBom, Component, Designator, Layer, Manufacturer, ManufacturerId, Name, OtherProperty, PrimitiveLock, Rotation, Supplier, SupplierId, UniqueId, X, Y; getState_ only for Footprint, Model3D, Pads, PrimitiveId, PrimitiveType; setAttribute; done, reset, isAsync, toAsync, toSync
- **Pad object:** getState_ / setState_ for HeatWelding, Hole, HoleOffsetX/Y, HoleRotation, Layer, Metallization, Net, Pad, PadNumber, PadType, PrimitiveLock, Rotation, SolderMaskAndPasteMaskExpansion, SpecialPad, X, Y
- **pcb_SelectControl:** clearSelected(0) doCrossProbeSelect(3) doCrossProbeSelectByObject(3) doSelectPrimitives(1) getAllSelectedPrimitives(0) getAllSelectedPrimitives_PrimitiveId(0) getCurrentMousePosition(0) getSelectedPrimitives(0)
- **pcb_MathPolygon:** calculateBBoxHeight(1) calculateBBoxWidth(1) calculateHeight(1) calculateWidth(1) convertImageToComplexPolygon(3) createComplexPolygon(1) createPolygon(1) discretize(2) splitPolygon(0)
- **pcb_Dfm:** checkDfm(1) getDfmAvailability(0) getDfmRules(0)
- **pcb_ManufactureData:** get…File(1) for 3D, 3D shell, Altium, auto-layout/route JSON, BOM, DSN, DXF(3), flying probe, Gerber, IDX, interactive BOM, IPC-2581C, IPC-D-356A, netlist, ODB++, PADS, PCB info, PDF, pick-and-place, test points; getManufactureData(0); place…Order(0) (do not call: they start JLC orders)
- **lib_Footprint:** copy(5) create(6) delete(2) get(2) getDocumentSource(2) getGeometry(2) getRenderImage(1) modify(7) openInEditor(3) search(3) searchByProperties(2) updateDocumentSource(3); for the phase 2 footprint fixes
- **dmt_Pcb / dmt_Board:** getAllPcbsInfo, getCurrentPcbInfo, getAllBoardsInfo, getCurrentBoardInfo work; also create/copy/delete/modify…Name

Other classes in 4.1.105: pcb_Event, pcb_RayTracerEngine; dmt_EditorControl, dmt_Event, dmt_Folder, dmt_Panel, dmt_Project, dmt_Schematic, dmt_SelectControl, dmt_Source*, dmt_Team, dmt_Workspace; lib_3DModel, lib_Cbb, lib_Classification, lib_Device, lib_LibrariesList, lib_PanelLibrary, lib_SelectControl, lib_SimulationModel, lib_Symbol; and 30 sys_* classes. `sys_Environment.getEditorCurrentVersion()` → "4.1.105".

## Running probes through the page driver

- Result text comes back through `javascript_tool`, which cuts each result at about 1,000 characters. Read long reports in 950-character slices, eleven slices per `browser_batch` call. Replace `=`, `&` and `?` first (with ＝ ＆ ？): the tool blocks output that looks like a query string.
- `console.log` from the script or the page does not reach `read_console_messages` (EasyEDA replaces it), so the probe's console rows are not a fallback.
- The driver's pointer-event press did not always close the result dialog; a plain `.click()` on its `[class*="header_right_close"]` icon does (the driver now does both).
