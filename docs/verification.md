# Verification

Validation date: 25 September 2026. The native model was previously checked in FreeCAD 1.1.3 (148 objects, 113 valid shapes). The web implementation is a separate Three.js renderer using native exported equipment and the same catalog.

## Repeatable checks

`npm test` covers all 29 connections, layer counts, 12 evidence gaps, 44 equipment meshes, binary index bounds, retained materials, finite route interpolation, arc-length speed through bends, route wrapping and validated hash state. It also checks that ambiguous waste/electrical/off-gas associations remain dashed.

`npm run build` enforces a 550 KiB gzip viewer-asset budget and 1 MiB CAD-download budget. The initial production viewer measures approximately 352 KiB gzipped (excluding its 2.6 KiB gzipped HTML). The CAD ZIP is approximately 317 KiB.

The binary is intentionally named `.mesh`. A development check caught automatic `Content-Encoding: gzip` handling on `.gz` paths; the neutral extension ensures that the browser's explicit decompression occurs exactly once. The production server was checked separately after that correction.

## Browser matrix

The initial production build was exercised in the Codex Chromium browser. Checks cover desktop and narrow viewport layouts. This is not a claim of testing on every physical device or every browser engine.

| Area | Expected behavior |
| --- | --- |
| Layer switching | 12 water, 8 waste, 6 electrical, 3 gas connections; overview shows all 29 |
| Isolated routes | Exactly one visible route; detail/source and URL match |
| Animation | Markers advance; Pause stops advancement and tour; speed updates |
| Tour | Water → Waste → Electrical → Air, every nine visible seconds |
| Equipment | Labels and register show component description and evidence |
| Display | Label toggle hides/shows annotations; transparency changes equipment |
| Cameras | Isometric, treatment skid, top and front; zoom and reset |
| Evidence | Modal contains all 12 gaps and can close by button or Escape |
| Navigation | Hash links restore selection; Back restores previous layer/route |
| Responsive | No horizontal page overflow; controls remain usable in a stacked mobile layout |
| Idle rendering | Frame counter stops while paused; hidden/offscreen views suspend rendering |
| Downloads | Native ZIP contains the model, launcher, modules, license and evidence CSVs |

The normal water view has about 36,236 rendered triangles and 69 draw calls; all layers together have about 46,176 triangles and 113 calls. These counts include equipment, routes and markers. Animation is capped at 30 fps; actual frame rate depends on hardware. Performance on low-end physical phones has not been measured.

For diagnostics, append `?debug` before the hash. The canvas exposes a `data-stats` JSON attribute with frame count, phase, visible route IDs, draw calls and triangles. Diagnostic DOM writes are disabled by default. Inspect these readings alongside console/network errors and responsive screenshots when changing the scene.

Browser reduced-motion preferences keep the default paused state; changing to reduced motion stops active playback. Explicit Play remains available. Original engineering uncertainties are unchanged.
