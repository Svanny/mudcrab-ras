// Arc-length interpolation keeps markers moving evenly through bends.
export function preparePath(points) {
  const segments = [];
  let total = 0;
  for (let i = 1; i < points.length; i++) {
    const a = points[i - 1],
      b = points[i];
    const delta = b.map((v, j) => v - a[j]);
    const length = Math.hypot(...delta);
    if (!length) continue;
    segments.push({ a, delta, length, start: total });
    total += length;
  }
  if (!total) throw new Error("A route must have nonzero length");
  return { segments, total };
}

export function samplePath(path, phase, target = { point: [], direction: [] }) {
  const distance = (((phase % 1) + 1) % 1) * path.total;
  const segment =
    path.segments.find((s) => distance < s.start + s.length) ??
    path.segments.at(-1);
  const t = (distance - segment.start) / segment.length;
  for (let i = 0; i < 3; i++) {
    target.point[i] = segment.a[i] + segment.delta[i] * t;
    target.direction[i] = segment.delta[i] / segment.length;
  }
  return target;
}

export const MODES = ["water", "waste", "electrical", "air", "all"];

export function readLocation(hash, routes) {
  const query = new URLSearchParams(hash.replace(/^#/, ""));
  const mode = MODES.includes(query.get("flow")) ? query.get("flow") : "water";
  const route = routes.find(
    (r) => r.key === query.get("route") && (mode === "all" || r.layer === mode),
  );
  return { mode, route: route?.key ?? "" };
}
