import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { preparePath, samplePath, readLocation } from "../src/paths.js";

const atlas = JSON.parse(
  readFileSync(new URL("../src/data/atlas.json", import.meta.url)),
);

test("all native routes and evidence holds survive web export", () => {
  assert.equal(atlas.routes.length, 29);
  assert.equal(new Set(atlas.routes.map((r) => r.key)).size, 29);
  for (const [layer, count] of Object.entries({
    water: 12,
    waste: 8,
    electrical: 6,
    air: 3,
  })) {
    assert.equal(atlas.routes.filter((r) => r.layer === layer).length, count);
  }
  assert.deepEqual(
    atlas.holds.map((h) => h.Hold),
    Array.from({ length: 12 }, (_, i) => `H${String(i + 1).padStart(2, "0")}`),
  );
  assert.equal(Object.keys(atlas.equipment).length, 12);
  assert(
    atlas.routes.every((r) => r.source && r.detail && r.points.length >= 2),
  );
});

test("equipment binary is complete, correctly indexed and retains distinct materials", () => {
  const buffer = gunzipSync(
    readFileSync(new URL("../src/data/equipment.mesh", import.meta.url)),
  );
  assert.equal(atlas.meshes.length, 44);
  assert(new Set(atlas.meshes.map((m) => m.color.join(","))).size >= 12);
  for (const mesh of atlas.meshes) {
    assert(
      mesh.positionOffset + mesh.vertexCount * 6 <= buffer.length,
      mesh.name,
    );
    assert(mesh.indexOffset + mesh.indexCount * 4 <= buffer.length, mesh.name);
    assert.equal(mesh.indexCount % 3, 0);
    for (let i = 0; i < mesh.indexCount; i++) {
      assert(
        buffer.readUInt32LE(mesh.indexOffset + i * 4) < mesh.vertexCount,
        mesh.name,
      );
    }
  }
});

test("markers use distance, not segment count, at bends and wrap safely", () => {
  const path = preparePath([
    [0, 0, 0],
    [4, 0, 0],
    [4, 0, 3],
  ]);
  assert.equal(path.total, 7);
  assert.deepEqual(samplePath(path, 0.5).point, [3.5, 0, 0]);
  assert.deepEqual(samplePath(path, 5 / 7).direction, [0, 0, 1]);
  assert.deepEqual(samplePath(path, 1).point, [0, 0, 0]);
  assert.deepEqual(samplePath(path, -0.5).point, [3.5, 0, 0]);
  assert.throws(() =>
    preparePath([
      [1, 1, 1],
      [1, 1, 1],
    ]),
  );
});

test("every route has finite positions and valid animation interpolation", () => {
  for (const route of atlas.routes) {
    const path = preparePath(route.points);
    for (let phase = 0; phase < 1; phase += 0.013) {
      const { point, direction } = samplePath(path, phase);
      assert(point.every(Number.isFinite), route.key);
      assert(Math.abs(Math.hypot(...direction) - 1) < 1e-10, route.key);
    }
  }
});

test("deep links reject invalid modes and cross-layer route selections", () => {
  assert.deepEqual(readLocation("#flow=air&route=A01", atlas.routes), {
    mode: "air",
    route: "A01",
  });
  assert.deepEqual(readLocation("#flow=all&route=E00", atlas.routes), {
    mode: "all",
    route: "E00",
  });
  assert.deepEqual(readLocation("#flow=water&route=E00", atlas.routes), {
    mode: "water",
    route: "",
  });
  assert.deepEqual(readLocation("#flow=bogus&route=unknown", atlas.routes), {
    mode: "water",
    route: "",
  });
});

test("schematic ambiguity is retained rather than converted to asserted plumbing", () => {
  for (const key of ["D04", "D07", "A03", "E00", "E01"])
    assert(atlas.routes.find((r) => r.key === key).dashed, key);
  assert(atlas.routes.find((r) => r.key === "A02").color === "ozone");
  assert(atlas.routes.find((r) => r.key === "D05").color === "overflow");
  assert.match(atlas.modes.electrical[3], /not verified wiring/);
  assert.match(atlas.modes.waste[3], /not simultaneous/);
});
