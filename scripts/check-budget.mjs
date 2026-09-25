import { readdir, readFile, stat } from "node:fs/promises";
import { gzipSync } from "node:zlib";
import assert from "node:assert/strict";

const assets = await readdir("dist/assets");
let transfer = 0;
const report = [];
for (const name of assets) {
  const file = await readFile(`dist/assets/${name}`);
  const bytes = name.endsWith(".mesh") ? file.length : gzipSync(file).length;
  transfer += bytes;
  report.push({
    asset: name,
    rawKB: +(file.length / 1024).toFixed(1),
    gzipKB: +(bytes / 1024).toFixed(1),
  });
}
console.table(report);
console.log(
  `Viewer assets: ${(transfer / 1024).toFixed(1)} KiB (gzip estimate; excludes on-demand CAD download)`,
);
assert(transfer < 550 * 1024, "Viewer assets exceed the 550 KiB gzip budget");
const cad = await stat("dist/downloads/Mudcrab_RAS_FreeCAD.zip");
assert(cad.size < 1024 * 1024, "FreeCAD download exceeds 1 MiB");
