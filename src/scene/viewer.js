import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { loadEquipment, setEquipmentAppearance, world } from "./equipment.js";
import { createFlows } from "./flows.js";

export async function createViewer(container, atlas, onSelect, onFailure) {
  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: false,
    powerPreference: "low-power",
  });
  renderer.setPixelRatio(
    Math.min(
      window.devicePixelRatio || 1,
      window.innerWidth < 760 ? 1.25 : 1.5,
    ),
  );
  renderer.setClearColor(0xedf1ef);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  const canvas = renderer.domElement;
  canvas.tabIndex = 0;
  canvas.setAttribute(
    "aria-label",
    "3D RAS schematic. Drag to orbit, scroll to zoom. Arrow keys pan; plus and minus zoom; Home resets. Equipment is available through the labels.",
  );
  container.append(canvas);
  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-5, 5, 4, -4, 0.01, 100);
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = false;
  controls.minZoom = 0.5;
  controls.maxZoom = 7;
  controls.maxPolarAngle = Math.PI * 0.95;
  controls.listenToKeyEvents(canvas);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x72958e, 2.5));
  const key = new THREE.DirectionalLight(0xffffff, 2);
  key.position.set(-3, 8, 5);
  scene.add(key);
  const fill = new THREE.DirectionalLight(0xd2e4eb, 1.2);
  fill.position.set(5, 3, -6);
  scene.add(fill);

  let equipment;
  try {
    equipment = await loadEquipment(atlas);
  } catch (error) {
    controls.dispose();
    renderer.dispose();
    canvas.remove();
    throw error;
  }
  scene.add(equipment);
  const flows = createFlows(atlas);
  scene.add(flows.group);
  const grid = new THREE.GridHelper(10, 40, 0xc4d2cc, 0xdce4df);
  grid.position.set(2.8, -0.09, -0.7);
  grid.material.transparent = true;
  grid.material.opacity = 0.5;
  scene.add(grid);
  const labelsContainer = document.getElementById("labels");
  const labels = atlas.tags.map((tag) => {
    const element = document.createElement("button");
    element.className = "equipment-label";
    element.dataset.equipment = tag.key;
    element.append(document.createTextNode(tag.text[0]));
    const sub = document.createElement("small");
    sub.textContent = tag.text[1] || "";
    element.append(sub);
    element.addEventListener("click", () => onSelect(tag.key));
    labelsContainer.append(element);
    return { element, position: world(tag.position), width: 100, height: 34 };
  });

  let width = 1,
    height = 1,
    playing = false,
    speed = 1,
    phase = 0.16;
  let frameId = 0,
    lastTime = 0,
    visible = true,
    lost = false,
    showLabels = true;
  let ghost = true,
    selected = "",
    cameraMode = "overview",
    frames = 0;
  let onTick = () => {};
  const debug = new URLSearchParams(location.search).has("debug");
  const projected = new THREE.Vector3();

  function updateLabels() {
    const occupied = [];
    for (const label of labels) {
      if (!showLabels) {
        label.element.hidden = true;
        continue;
      }
      projected.copy(label.position).project(camera);
      const x = ((projected.x + 1) * width) / 2,
        y = ((1 - projected.y) * height) / 2;
      const rect = {
        x: x - label.width / 2,
        y: y - label.height / 2,
        w: label.width,
        h: label.height,
      };
      const outside =
        projected.z < -1 ||
        projected.z > 1 ||
        rect.x < 4 ||
        rect.x + rect.w > width - 4 ||
        y < 57 ||
        y > height - 104;
      const overlaps = occupied.some(
        (r) =>
          rect.x < r.x + r.w + 4 &&
          rect.x + rect.w + 4 > r.x &&
          rect.y < r.y + r.h + 4 &&
          rect.y + rect.h + 4 > r.y,
      );
      label.element.hidden = outside || overlaps;
      if (!outside && !overlaps) {
        label.element.style.transform = `translate(${Math.round(x)}px,${Math.round(y)}px) translate(-50%,-50%)`;
        occupied.push(rect);
      }
    }
  }

  function requestRender() {
    if (!frameId && !document.hidden && visible && !lost)
      frameId = requestAnimationFrame(render);
  }
  function render(now) {
    frameId = 0;
    // Slow explanatory markers do not need high-refresh-rate GPU rendering.
    if (playing && lastTime && now - lastTime < 1000 / 30 - 0.5) {
      requestRender();
      return;
    }
    const dt = lastTime ? Math.min((now - lastTime) / 1000, 0.1) : 0;
    lastTime = now;
    if (playing) {
      phase = (phase + dt * 0.095 * speed) % 1;
      onTick(dt);
    }
    flows.animate(phase);
    renderer.render(scene, camera);
    frames++;
    if (debug)
      canvas.dataset.stats = JSON.stringify({
        frames,
        phase,
        playing,
        visible,
        pixelRatio: renderer.getPixelRatio(),
        drawCalls: renderer.info.render.calls,
        triangles: renderer.info.render.triangles,
        visibleRoutes: [...flows.routes]
          .filter(([, r]) => r.group.visible)
          .map(([id]) => id),
      });
    // Labels only need projection when the camera changes; the scene is static.
    if (playing) requestRender();
  }

  function fitCamera(mode = cameraMode) {
    cameraMode = mode;
    const skid = mode === "skid";
    const target = skid
      ? new THREE.Vector3(4.2, 1.1, -0.6)
      : new THREE.Vector3(2.75, 1.1, -0.5);
    const offset =
      mode === "top"
        ? new THREE.Vector3(0, 12, 0.001)
        : mode === "front"
          ? new THREE.Vector3(0, 0.001, 12)
          : new THREE.Vector3(3.9, 7, 12);
    camera.position.copy(target).add(offset);
    camera.up.set(0, 1, 0);
    camera.lookAt(target);
    controls.target.copy(target);
    camera.zoom = 1;
    const span = skid ? 4.6 : 7.4;
    const aspect = width / height;
    const vertical = Math.max(skid ? 3.8 : 4.4, span / aspect);
    camera.left = (-vertical * aspect) / 2;
    camera.right = (vertical * aspect) / 2;
    camera.top = vertical / 2;
    camera.bottom = -vertical / 2;
    camera.updateProjectionMatrix();
    controls.update();
    updateLabels();
    requestRender();
  }
  controls.addEventListener("change", () => {
    updateLabels();
    requestRender();
  });
  function zoom(factor) {
    camera.zoom = THREE.MathUtils.clamp(camera.zoom * factor, 0.5, 7);
    camera.updateProjectionMatrix();
    updateLabels();
    requestRender();
  }
  canvas.addEventListener("keydown", (e) => {
    if (e.key === "Home") {
      e.preventDefault();
      fitCamera();
    }
    if (e.key === "+" || e.key === "=") {
      e.preventDefault();
      zoom(1.2);
    }
    if (e.key === "-") {
      e.preventDefault();
      zoom(1 / 1.2);
    }
  });
  const resize = new ResizeObserver(() => {
    width = container.clientWidth;
    height = container.clientHeight;
    renderer.setSize(width, height, false);
    fitCamera();
  });
  resize.observe(container);
  const visibility = new IntersectionObserver((entries) => {
    visible = entries[0].isIntersecting;
    if (visible) {
      lastTime = 0;
      requestRender();
    } else {
      cancelAnimationFrame(frameId);
      frameId = 0;
    }
  });
  visibility.observe(container);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      cancelAnimationFrame(frameId);
      frameId = 0;
    } else {
      lastTime = 0;
      requestRender();
    }
  });
  canvas.addEventListener("webglcontextlost", (event) => {
    event.preventDefault();
    lost = true;
    cancelAnimationFrame(frameId);
    frameId = 0;
    onFailure(
      new Error(
        "The graphics context was interrupted. Reload to resume, or download the FreeCAD model.",
      ),
    );
  });
  labels.forEach((label) => {
    label.width = label.element.offsetWidth;
    label.height = label.element.offsetHeight;
  });
  setEquipmentAppearance(equipment, ghost);
  return {
    show(mode, route) {
      flows.show(mode, route);
      requestRender();
    },
    play(value) {
      playing = value;
      lastTime = 0;
      requestRender();
    },
    setSpeed(value) {
      speed = value;
    },
    setLabels(value) {
      showLabels = value;
      updateLabels();
    },
    setGhost(value) {
      ghost = value;
      setEquipmentAppearance(equipment, ghost, selected);
      requestRender();
    },
    select(value) {
      selected = value;
      setEquipmentAppearance(equipment, ghost, selected);
      labels.forEach((l) =>
        l.element.classList.toggle(
          "selected",
          l.element.dataset.equipment === value,
        ),
      );
      requestRender();
    },
    camera: fitCamera,
    zoom,
    onTick(callback) {
      onTick = callback;
    },
    stats() {
      return {
        frames,
        phase,
        playing,
        visible,
        pixelRatio: renderer.getPixelRatio(),
        drawCalls: renderer.info.render.calls,
        triangles: renderer.info.render.triangles,
        visibleRoutes: [...flows.routes]
          .filter(([, r]) => r.group.visible)
          .map(([id]) => id),
      };
    },
  };
}
