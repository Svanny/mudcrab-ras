import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import { preparePath, samplePath } from "../paths.js";
import { world } from "./equipment.js";

const UP = new THREE.Vector3(0, 1, 0);
const arrowGeometry = new THREE.ConeGeometry(0.046, 0.15, 9);
const bubbleGeometry = new THREE.SphereGeometry(0.021, 6, 4);

function tubeSegment(a, b, radius) {
  const direction = b.clone().sub(a);
  const geometry = new THREE.CylinderGeometry(
    radius,
    radius,
    direction.length(),
    7,
    1,
  );
  geometry.applyQuaternion(
    new THREE.Quaternion().setFromUnitVectors(UP, direction.normalize()),
  );
  geometry.translate(...a.clone().add(b).multiplyScalar(0.5).toArray());
  return geometry;
}

function routeGeometry(points, radius, dashed) {
  const pieces = [];
  for (let i = 1; i < points.length; i++) {
    const a = points[i - 1],
      b = points[i],
      delta = b.clone().sub(a);
    const length = delta.length();
    if (dashed) {
      for (let distance = 0; distance < length; distance += 0.115) {
        pieces.push(
          tubeSegment(
            a.clone().addScaledVector(delta, distance / length),
            a
              .clone()
              .addScaledVector(
                delta,
                Math.min(distance + 0.072, length) / length,
              ),
            radius,
          ),
        );
      }
    } else pieces.push(tubeSegment(a, b, radius));
  }
  const geometry = mergeGeometries(pieces);
  pieces.forEach((p) => p.dispose());
  return geometry;
}

export function createFlows(atlas) {
  const group = new THREE.Group(),
    routes = new Map();
  for (const route of atlas.routes) {
    const points = route.points.map(world);
    const color = new THREE.Color().setRGB(
      ...atlas.colors[route.color],
      THREE.SRGBColorSpace,
    );
    const material = new THREE.MeshPhongMaterial({
      color,
      shininess: 55,
      emissive: color.clone().multiplyScalar(0.12),
    });
    const routeGroup = new THREE.Group();
    const radius =
      route.layer === "water"
        ? 0.018
        : route.layer === "electrical"
          ? 0.011
          : 0.014;
    routeGroup.add(
      new THREE.Mesh(routeGeometry(points, radius, route.dashed), material),
    );
    const markerMaterial = new THREE.MeshBasicMaterial({ color });
    const path = preparePath(points.map((p) => p.toArray()));
    const count = Math.max(1, Math.min(4, Math.round(path.total / 2)));
    const markers = new THREE.InstancedMesh(
      arrowGeometry,
      markerMaterial,
      count,
    );
    markers.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    markers.frustumCulled = false;
    markers.renderOrder = 2;
    routeGroup.add(markers);
    if (route.layer === "waste" || route.key === "A03") {
      const boundary = new THREE.Mesh(
        new THREE.TorusGeometry(0.047, 0.005, 5, 20),
        markerMaterial,
      );
      boundary.position.copy(points.at(-1));
      boundary.rotation.x = Math.PI / 2;
      routeGroup.add(boundary);
    }
    routeGroup.userData.layer = route.layer;
    routes.set(route.key, {
      ...route,
      group: routeGroup,
      markers,
      path,
      count,
    });
    group.add(routeGroup);
  }
  const bubbles = new THREE.InstancedMesh(
    bubbleGeometry,
    new THREE.MeshBasicMaterial({ color: 0x0ca886 }),
    16,
  );
  bubbles.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  bubbles.frustumCulled = false;
  group.add(bubbles);
  const transform = new THREE.Object3D();
  const direction = new THREE.Vector3();
  const sample = { point: [], direction: [] };

  function animate(phase) {
    for (const route of routes.values()) {
      if (!route.group.visible) continue;
      for (let i = 0; i < route.count; i++) {
        samplePath(route.path, phase + i / route.count, sample);
        transform.position.fromArray(sample.point);
        direction.fromArray(sample.direction);
        transform.quaternion.setFromUnitVectors(UP, direction);
        transform.scale.setScalar(1);
        transform.updateMatrix();
        route.markers.setMatrixAt(i, transform.matrix);
      }
      route.markers.instanceMatrix.needsUpdate = true;
    }
    if (bubbles.visible) {
      transform.quaternion.identity();
      for (let i = 0; i < 16; i++) {
        transform.position.set(
          3.87 + (i % 4) * 0.12,
          0.3 + ((phase * 2 + i / 16) % 1) * 0.63,
          -1.25 - Math.floor(i / 4) * 0.085,
        );
        transform.scale.setScalar(0.65 + (i % 3) * 0.18);
        transform.updateMatrix();
        bubbles.setMatrixAt(i, transform.matrix);
      }
      bubbles.instanceMatrix.needsUpdate = true;
    }
  }

  function show(mode, key) {
    for (const [id, route] of routes) {
      route.group.visible =
        (mode === "all" || route.layer === mode) && (!key || key === id);
    }
    bubbles.visible =
      (mode === "air" || mode === "all") && (!key || key === "A01");
  }
  return { group, animate, show, routes };
}
