# Verification

Validation date: 25 September 2026. The native model was previously checked in FreeCAD 1.1.3 (148 objects, 113 valid shapes). The web implementation is a separate Three.js renderer using native exported equipment and the same catalog.

## Repeatable checks

`npm test` covers all 29 connections, layer counts, 12 evidence gaps, 44 equipment meshes, binary index bounds, retained materials, finite route interpolation, arc-length speed through bends, route wrapping and validated hash state. It also checks that ambiguous waste/electrical/off-gas associations remain dashed.

`npm run build` enforces a 550 KiB gzip viewer-asset budget and 1 MiB CAD-download budget. The production viewer measures approximately 352 KiB gzipped (excluding its 3.4 kB gzipped HTML). The CAD ZIP is approximately 317 KiB.

The binary is intentionally named `.mesh`. A development check caught automatic `Content-Encoding: gzip` handling on `.gz` paths; the neutral extension ensures that the browser's explicit decompression occurs exactly once. The production server was checked separately after that correction.

## Browser matrix

The initial production build was exercised in the Codex Chromium browser. Checks cover desktop and narrow viewport layouts. This is not a claim of testing on every physical device or every browser engine.

| Area | Expected behavior |
| --- | --- |
| Layer switching | Five distinct icon buttons with a filled active state; 12 water, 8 waste, 6 electrical, 3 gas connections; overview shows all 29 |
| Isolated routes | Exactly one visible route; detail/source and URL match |
| Connection controls | Centered chevrons on native connection/equipment selectors; no default helper paragraph; selected route/equipment details still appear and clear correctly |
| Animation | Starts automatically on model load; Pause stops advancement and tour; speed updates |
| Tour | Water → Waste → Electrical → Air, every nine visible seconds |
| Equipment | Labels and register show component description and evidence |
| Display | Label toggle hides/shows annotations; transparency changes equipment |
| Cameras | Icon menu for isometric, treatment skid, top and front; centered chevron; selection, arrow keys, Enter, Escape, outside dismissal, zoom and reset |
| Evidence | Modal contains all 12 gaps and can close by button or Escape |
| Navigation | Hash links restore selection; Back restores previous layer/route |
| Responsive | No horizontal page overflow; controls remain usable in a stacked mobile layout |
| Idle rendering | Frame counter stops while paused; hidden/offscreen views suspend rendering |
| Downloads | Native ZIP contains the model, launcher, modules, license and evidence CSVs |

The normal water view has about 36,236 rendered triangles and 69 draw calls; all layers together have about 46,176 triangles and 113 calls. These counts include equipment, routes and markers. Animation is capped at 30 fps; actual frame rate depends on hardware. Performance on low-end physical phones has not been measured.

For diagnostics, append `?debug` before the hash. The canvas exposes a `data-stats` JSON attribute with frame count, phase, visible route IDs, draw calls and triangles. Diagnostic DOM writes are disabled by default. Inspect these readings alongside console/network errors and responsive screenshots when changing the scene.

Browser reduced-motion preferences override automatic playback and start paused; changing to reduced motion stops active playback. Explicit Play remains available. Original engineering uncertainties are unchanged.

## Simplified interface update

The header was removed, the page title changed to “Recirculating Aquaculture System” without introductory copy, and Source/FreeCAD links moved to the footer. The camera selector now uses an SVG icon for each preset, with a chevron centered by a grid layout. Browser checks verified automatic playback, pause, all four camera selections, matching selected icons, keyboard selection, Escape, outside dismissal, reset and Tab focus. At 320 CSS pixels wide, the camera toolbar fits without horizontal overflow. The asset budget remains approximately 352 KiB compressed.

## Flow controls update

The five flow controls now have distinct SVG icons, bordered white button backgrounds, hover feedback and a solid layer-colored selected state. The connection and equipment dropdowns share an explicitly centered chevron while retaining native menu and keyboard behavior. The animation-speed caption and default connection guidance were removed; selecting a route or equipment still reveals its description and source.

Production-preview checks covered all five layer counts, single-route isolation, clearing route/equipment selections, automatic playback, keyboard selection in the native route menu and error-free browser logs. At desktop widths of 1600 and 922 CSS pixels and a mobile width of 320 CSS pixels, the controls fit without horizontal page overflow. The route chevron's vertical center matches the select's center, with a 12-pixel right inset. All six model checks and the production asset budget pass (352.3 KiB compressed viewer assets).
