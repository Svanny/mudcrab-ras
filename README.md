# Mudcrab · RAS flow atlas

An open source 3D schematic of a mudcrab recirculating aquaculture system, reconstructed in FreeCAD and made explorable in the browser.

**[Open the live atlas](https://svanny.github.io/mudcrab-ras/)** · **[Download the FreeCAD model and launcher](https://svanny.github.io/mudcrab-ras/downloads/Mudcrab_RAS_FreeCAD.zip)**

Switch between **water**, **waste**, **electrical**, **air + ozone**, or all layers. Isolate any of 29 connections, play directional markers, take a guided tour, inspect equipment, and switch between isometric, skid, top and front views. All 12 source evidence gaps remain visible in the explorer.

## Use the explorer

- Animation starts automatically when the model loads. Select a layer to follow its service, or use **Pause flow** to stop it. Reduced-motion preferences start the viewer paused.
- Use **Trace a connection** to isolate one route. URLs preserve the selected layer and route for sharing.
- **Tour all** cycles through the four services every nine seconds. **Pause flow** stops both the tour and markers.
- Drag to orbit, scroll/pinch to zoom, and right-drag/two-finger drag to pan.
- Click an equipment label or open **Inspect equipment** for descriptions and source references.
- The camera menu shows an angle/focus icon for each preset. Use arrow keys to navigate, Enter to select, and Escape to dismiss it. Source and FreeCAD download links are in the footer.
- Keyboard: **1–5** select layers. With the canvas focused, **Space** plays/pauses, **arrows** pan, **+ / −** zoom, and **Home** resets the view.
- **Reading this schematic → View 12 evidence gaps** opens the audit register.

The browser requires WebGL 2 and the Compression Streams API (current Chrome, Edge, Firefox and Safari). The FreeCAD download remains available if the 3D viewer cannot load. No account, backend, analytics or third-party asset service is required.

## Develop locally

Use Node.js 22.12+ (CI uses Node 24) and Python 3 for the download packaging step.

```sh
npm ci
npm run dev
```

```sh
npm test
npm run package:cad
npm run build
npm run preview
```

`build` checks a **550 KiB gzip budget** for all viewer assets. The current viewer is about **352 KiB gzipped**, plus its small HTML document. The optional FreeCAD package is about **317 KiB**, fetched only when downloaded. These are build measurements, not a promise about every connection's transfer encoding or load time.

## Project layout

| Path | Purpose |
| --- | --- |
| `src/scene/` | Three.js equipment, flow meshes, rendering and camera controls |
| `src/main.js` | Accessible controls, route state, tour and evidence register |
| `src/data/` | Exported catalog and compressed, quantized equipment geometry |
| `output/ras3d/ras_model/` | Editable native FreeCAD generator and explorer |
| `output/ras3d/Mudcrab_RAS_Flows.FCStd` | Native CAD document |
| `scripts/` | Deterministic CAD packaging, mesh export and size budgets |
| `tests/` | Geometry integrity, route data, interpolation and URL-state checks |
| `docs/` | Deployment, performance and browser verification notes |

The native catalog is the source of truth for process connections and evidence notes. Edit `output/ras3d/ras_model/catalog.py`, rebuild the native model if necessary, then regenerate the web data with FreeCAD's Python:

```sh
# macOS example; adjust for your FreeCAD installation.
FREECAD_LIB=/Applications/FreeCAD.app/Contents/Resources/lib \
  /Applications/FreeCAD.app/Contents/Resources/bin/python scripts/export_model.py
npm run package:cad
npm test
npm run build
```

Native editing and launcher instructions are in [the FreeCAD README](output/ras3d/README.md). FreeCAD is not required to build or host the website because exported geometry is committed.

## Performance

- One compressed equipment asset: **203 KB**, 44 meshes and 34,586 equipment triangles.
- Indexed geometry quantized to 0.5 mm; no textures, external fonts, CAD runtime or video download.
- Lazy-loaded 3D engine; the HTML controls paint first.
- Instanced direction markers and bubbles; merged pipe segments per route.
- Render on demand while paused; stop rendering when hidden or offscreen.
- Cap animated rendering at 30 fps, including on high-refresh-rate displays.
- Cap pixel density at 1.5× desktop / 1.25× mobile to bound GPU work.
- Labels project only when the camera changes; collisions are suppressed.
- Content-hashed production assets and a repeatable CI size budget.

## Deploy

GitHub Actions validates every pull request and deploys successful pushes to `main` to GitHub Pages. See [deployment instructions](docs/deployment.md) for forks and custom domains.

## Model scope and provenance

This is a **process schematic**, not an as-built installation drawing or a hydraulic, electrical or gas simulation. Positions, pipe routes and culture-box counts are representative. Waste animations illustrate separate service functions, not a simultaneous cleaning procedure. Electrical links represent functional loads, not terminal wiring or AC current direction. Source uncertainties H01–H12 remain unresolved.

The original basis is the supplied LFS-10M equipment manual, reference photographs and revision-2 audit. `M` and `E` identify PDF page indices in the manual and photograph collection. Original supplied PDFs, photographs, DWG and archives are **not redistributed** and are not covered by this repository's license. Source references and the equipment/evidence registers are retained. All published 3D geometry was generated with FreeCAD primitives; no external 3D assets were used.

## License and contributions

Original code, generated CAD/mesh geometry and project documentation are available under the **[MIT License](LICENSE)**. Dependencies retain their own licenses; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).
