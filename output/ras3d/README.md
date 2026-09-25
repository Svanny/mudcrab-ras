# Mudcrab RAS · 3D flow atlas

Open **Launch_RAS.FCMacro** in FreeCAD and run **Macro → Execute macro (F6)**. The launcher opens the native model and adds the Flow atlas panel. Keep the macro, `ras_model/` folder and model together. No addons, downloads or network connection are required.

## Explore

| Control | What it does |
|---|---|
| Water | Blue normal process loop, plus dashed optional makeup service |
| Waste | Orange cleaning/purge/cup/sand services; rose overflow |
| Electrical | Dashed amber functional supply connections |
| Air + ozone | Green LP-100 aeration and separate violet ozone service |
| All systems | Overlays the four flow layers |
| Path dropdown | Isolates one connection and explains its function and evidence |
| Pause / Play | Stops or starts moving direction markers |
| Speed | Adjusts illustrative animation from 0.25× to 2× |
| Guided tour | Cycles Water → Waste → Electrical → Air, nine seconds per view |
| Transparent equipment | Reveals paths inside the simplified equipment |
| 3D / Top / Front / Skid | Resets the camera or frames the treatment skid |
| Save image | Saves the current view under `previews/` |
| Evidence / holds | Opens the source legend and unresolved evidence register |

Click a component to read its function and source reference. Use the standard FreeCAD navigation controls to orbit, pan and zoom. Selecting a flow button stops the guided tour. Pause also pauses tour advancement.

## Files

- `Mudcrab_RAS_Flows.FCStd` — editable native CAD, 148 objects with separately grouped equipment, labels and four flow layers. Static direction arrows are saved in the document.
- `Launch_RAS.FCMacro` — opens the model and starts the interactive panel/animation. A `.FCStd` document alone does not execute animation code automatically.
- `ras_model/` — modular, editable builder, source catalog, presentation and controller code.
- `previews/` — local exports created with Save image; existing large previews are omitted from the public download.
- `evidence/` — original revision-2 equipment and open-hold registers.
- `validation/` — local checks run against the model in FreeCAD 1.1.3; validation helpers remain in `ras_model/qa.py`.

To use only the static model, open the `.FCStd` and toggle the four `Flow_…` groups in FreeCAD's Model tree. The launcher provides the intended camera, light background, readable labels and one-click controls.

## Basis and interpretation

The model follows `mudcrab_schematics_rev2.pdf`, the LFS-10M equipment manual, and `mudcrab_realife_evidences.pdf` supplied in the workspace. `M` and `E` refer to PDF page indices in the manual and photographs. The nominal skid footprint is 2000 × 1210 mm, with a source overall height of 2200 mm. Other dimensions, equipment simplifications, elevations and routed paths are schematic. Two banks are represented with illustrative boxes; the displayed count is not an installed inventory. The DWG was not converted or treated as an as-built geometry source.

Water follows the manual sequence: culture return → rear inlet-duty pump → sand filter → skimmer → BIO-1 → BIO-2 → UV chamber → front outlet-duty STP50 → culture supply. Three UV lamp assemblies share one chamber; they are not depicted as three serial hydraulic reactors. Pump duties are reconstructed from the sources. The manual's optional preconditioned makeup service is shown entering culture units without an invented tank or transfer pump.

Waste services terminate independently at open boundaries. The two ambiguous skimmer stubs are represented by an identification boundary, not an asserted cup connection or merged pipe. The biological-drain path is a dashed functional association, since individual chamber/valve mapping is unresolved. Waste animations show service directions, not simultaneous operation or a backwash/startup procedure.

Electrical lines identify functional loads. They are not terminal wiring, verified panel branches, protective-device selections or AC-current waveforms. Air from LP-100 goes to BIO-2; ozone service is separate. Bubble locations do not prescribe diffuser hardware. The dashed off-gas indicator marks an unresolved interface, not installed treatment equipment.

Animations explain direction; speed does not represent measured flow, gas rate or electrical behavior. All H01–H12 evidence gaps remain in the included register. This is a process schematic, not an installation drawing.

## Reproduce or edit

Edit `ras_model/catalog.py` for connection paths and explanations, `equipment.py` for component geometry, and `presentation.py` for labels/camera framing. Existing saved models are loaded without rebuilding. To rebuild, move the existing `.FCStd` aside and run the launcher again in a fresh FreeCAD session.

All geometry was generated natively with FreeCAD primitives; no third-party 3D assets were needed. The animation uses FreeCAD's Coin scenegraph so frames do not modify the CAD document. Reference: [FreeCAD scenegraph documentation](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Scenegraph.md).
