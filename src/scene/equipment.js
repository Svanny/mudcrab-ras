import * as THREE from "three";
import meshUrl from "../data/equipment.mesh?url";

export const world = ([x, y, z]) =>
  new THREE.Vector3(x / 1000, z / 1000, -y / 1000);

export async function loadEquipment(atlas) {
  const response = await fetch(meshUrl);
  if (!response.ok)
    throw new Error(`Equipment download failed (${response.status}).`);
  const unpacked = response.body.pipeThrough(new DecompressionStream("gzip"));
  const binary = await new Response(unpacked).arrayBuffer();
  const group = new THREE.Group();
  for (const part of atlas.meshes) {
    const packed = new Int16Array(
      binary,
      part.positionOffset,
      part.vertexCount * 3,
    );
    const positions = new Float32Array(packed.length);
    for (let i = 0; i < packed.length; i += 3) {
      positions[i] = packed[i] / 2000;
      positions[i + 1] = packed[i + 2] / 2000;
      positions[i + 2] = -packed[i + 1] / 2000;
    }
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geometry.setIndex(
      new THREE.BufferAttribute(
        new Uint32Array(binary, part.indexOffset, part.indexCount),
        1,
      ),
    );
    geometry.computeVertexNormals();
    geometry.computeBoundingSphere();
    const color = new THREE.Color(`rgb(${part.color.join(",")})`);
    const material = new THREE.MeshPhongMaterial({
      color,
      shininess: 24,
      specular: 0x415255,
      transparent: true,
      opacity: 0.68,
      side: THREE.DoubleSide,
      depthWrite: false,
      forceSinglePass: true,
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.name = part.name;
    mesh.userData = {
      service: part.service,
      opacity: 1 - part.transparency / 100,
    };
    group.add(mesh);
  }
  return group;
}

export function setEquipmentAppearance(group, ghost, selected = "") {
  for (const mesh of group.children) {
    const highlighted = selected && mesh.userData.service === selected;
    mesh.material.opacity = highlighted
      ? 0.92
      : ghost
        ? Math.min(mesh.userData.opacity, 0.42)
        : mesh.userData.opacity;
    mesh.material.depthWrite = mesh.material.opacity >= 0.95;
    mesh.material.emissive.set(highlighted ? 0x123c48 : 0x000000);
  }
}
