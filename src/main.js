import "./style.css";
import "./responsive.css";
import atlas from "./data/atlas.json";
import { MODES, readLocation } from "./paths.js";

const $ = (id) => document.getElementById(id);
const accents = {
  water: "#126dc2",
  waste: "#bf431f",
  electrical: "#936008",
  air: "#06795e",
  all: "#285d6e",
};
const initial = readLocation(location.hash, atlas.routes);
let mode = initial.mode,
  routeKey = initial.route,
  playing = false,
  tour = false,
  tourTime = 0;
let viewer,
  selected = "";
const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");

function syncUrl(replace = false) {
  const query = new URLSearchParams({ flow: mode });
  if (routeKey) query.set("route", routeKey);
  const hash = `#${query}`;
  if (location.hash !== hash)
    history[replace ? "replaceState" : "pushState"](null, "", hash);
}

function selectEquipment(key) {
  selected = key;
  $("equipment").value = key;
  $("clear-selection").hidden = !key;
  viewer?.select(key);
  if (key) {
    const data = atlas.equipment[key];
    $("route-detail").textContent = `${data[0]} — ${data[1]}`;
    $("route-source").textContent = data[2];
  } else updateConnection();
}

function updateConnection() {
  const route = atlas.routes.find((r) => r.key === routeKey);
  $("route-detail").textContent = route
    ? route.detail
    : mode === "all"
      ? "Select a layer or connection to see its role. Click an equipment label to inspect the component."
      : `Showing all ${atlas.routes.filter((r) => r.layer === mode).length} connections. Choose one above to trace its complete path.`;
  $("route-source").textContent = route ? `SOURCE / ${route.source}` : "";
}

function setView(nextMode, nextRoute = "", writeUrl = true, replace = false) {
  mode = nextMode;
  routeKey = nextRoute;
  selected = "";
  const data = atlas.modes[mode];
  const routes = atlas.routes.filter((r) => mode === "all" || r.layer === mode);
  document.documentElement.style.setProperty("--accent", accents[mode]);
  document.body.dataset.mode = mode;
  document.title = `${mode === "all" ? "Overview" : mode[0].toUpperCase() + mode.slice(1)} — Mudcrab RAS atlas`;
  document
    .querySelectorAll(".flow-tab")
    .forEach((b) => b.setAttribute("aria-pressed", b.dataset.mode === mode));
  $("stage-title").textContent = data[0];
  $("layer-kicker").textContent =
    `${mode === "all" ? "OVERVIEW" : mode.toUpperCase()} / ${routes.length} CONNECTIONS`;
  $("layer-title").textContent = data[1];
  $("layer-summary").textContent = data[2];
  $("layer-note").textContent = data[3];
  $("route").replaceChildren(
    new Option("All connections", ""),
    ...routes.map((r) => new Option(r.title, r.key)),
  );
  $("route").value = routeKey;
  $("equipment").value = "";
  $("clear-selection").hidden = true;
  updateConnection();
  viewer?.show(mode, routeKey);
  viewer?.select("");
  if (writeUrl) syncUrl(replace);
  updateStatus();
}

function updateStatus() {
  if (!viewer) return;
  $("render-status").textContent = tour
    ? `TOUR · ${mode.toUpperCase()}`
    : playing
      ? "FLOW IN MOTION"
      : "PAUSED · EXPLORE FREELY";
}

function setPlaying(value) {
  playing = value;
  if (!value) setTour(false);
  $("play").setAttribute("aria-pressed", value);
  $("play-icon").textContent = value ? "Ⅱ" : "▶";
  $("play-text").textContent = value ? "Pause flow" : "Play flow";
  viewer?.play(value);
  updateStatus();
}

function setTour(value) {
  tour = value;
  tourTime = 0;
  $("tour").setAttribute("aria-pressed", value);
  $("tour").textContent = value ? "Stop tour" : "Tour all";
  updateStatus();
}

document.querySelectorAll(".flow-tab").forEach((button) =>
  button.addEventListener("click", () => {
    setTour(false);
    setView(button.dataset.mode);
  }),
);
document.querySelector(".skip-link").addEventListener("click", (event) => {
  event.preventDefault();
  $("explorer").focus();
});
$("route").addEventListener("change", () => {
  setTour(false);
  setView(mode, $("route").value);
});
$("equipment").append(
  ...Object.entries(atlas.equipment).map(
    ([key, data]) => new Option(data[0], key),
  ),
);
$("equipment").addEventListener("change", () =>
  selectEquipment($("equipment").value),
);
$("clear-selection").addEventListener("click", () => selectEquipment(""));
$("play").addEventListener("click", () => setPlaying(!playing));
$("tour").addEventListener("click", () => {
  if (tour) {
    setTour(false);
    setPlaying(false);
  } else {
    setView(mode === "all" ? "water" : mode);
    setPlaying(true);
    setTour(true);
  }
});
$("speed").addEventListener("input", () => {
  const speed = Number($("speed").value) / 100;
  $("speed-value").textContent = `${speed}×`;
  viewer?.setSpeed(speed);
});
$("show-labels").addEventListener("change", () =>
  viewer?.setLabels($("show-labels").checked),
);
$("ghost").addEventListener("change", () =>
  viewer?.setGhost($("ghost").checked),
);
$("camera").addEventListener("change", () => viewer?.camera($("camera").value));
$("zoom-in").addEventListener("click", () => viewer?.zoom(1.2));
$("zoom-out").addEventListener("click", () => viewer?.zoom(1 / 1.2));
$("reset").addEventListener("click", () => {
  $("camera").value = "overview";
  viewer?.camera("overview");
});
$("retry").addEventListener("click", () => location.reload());
window.addEventListener("hashchange", () => {
  const state = readLocation(location.hash, atlas.routes);
  setTour(false);
  setView(state.mode, state.route, false);
});
document.addEventListener("keydown", (event) => {
  if (
    event.altKey ||
    event.metaKey ||
    event.ctrlKey ||
    /INPUT|SELECT|TEXTAREA/.test(event.target.tagName) ||
    $("evidence-dialog").open
  )
    return;
  const index = Number(event.key) - 1;
  if (index >= 0 && index < 5) {
    setTour(false);
    setView(MODES[index]);
  }
  if (event.code === "Space" && event.target.tagName === "CANVAS") {
    event.preventDefault();
    setPlaying(!playing);
  }
});
reducedMotion.addEventListener("change", (event) => {
  if (event.matches) setPlaying(false);
});
if (reducedMotion.matches)
  $("motion-note").textContent =
    "Reduced motion enabled. Play only when you choose.";

for (const hold of atlas.holds) {
  const details = document.createElement("details");
  const summary = document.createElement("summary");
  const id = document.createElement("span");
  id.textContent = hold.Hold;
  summary.append(id, document.createTextNode(hold.Topic));
  const why = document.createElement("p");
  why.textContent = hold["Why still open"];
  const needed = document.createElement("p");
  const lead = document.createElement("strong");
  lead.textContent = "Evidence needed: ";
  needed.append(lead, document.createTextNode(hold["Exact evidence needed"]));
  const source = document.createElement("p");
  source.textContent = `Source pages: ${hold["Source PDF pages"]}`;
  details.append(summary, why, needed, source);
  $("holds").append(details);
}
$("open-evidence").addEventListener("click", () =>
  $("evidence-dialog").showModal(),
);
$("close-evidence").addEventListener("click", () =>
  $("evidence-dialog").close(),
);
setView(mode, routeKey, true, true);

function failed(error) {
  console.error(error);
  $("loading").hidden = true;
  $("scene-error").hidden = false;
  $("error-message").textContent =
    error.message ||
    "This browser could not initialize WebGL 2. Try a recent browser or download the native model.";
  $("viewport").setAttribute("aria-busy", "false");
  $("play").disabled = true;
  $("tour").disabled = true;
  $("render-status").textContent = "3D UNAVAILABLE";
}

// Let the static controls paint before downloading and compiling the 3D engine.
requestAnimationFrame(() =>
  requestAnimationFrame(async () => {
    try {
      const { createViewer } = await import("./scene/viewer.js");
      viewer = await createViewer(
        $("viewport"),
        atlas,
        selectEquipment,
        failed,
      );
      viewer.show(mode, routeKey);
      viewer.setGhost($("ghost").checked);
      viewer.setLabels($("show-labels").checked);
      viewer.setSpeed(Number($("speed").value) / 100);
      viewer.onTick((dt) => {
        if (!tour) return;
        tourTime += dt;
        if (tourTime >= 9) {
          tourTime = 0;
          setView(MODES[(MODES.indexOf(mode) + 1) % 4], "", true, true);
        }
      });
      $("loading").hidden = true;
      $("viewport").setAttribute("aria-busy", "false");
      $("play").disabled = false;
      $("tour").disabled = false;
      document.body.dataset.ready = "true";
      updateStatus();
      if (new URLSearchParams(location.search).has("debug")) {
        window.__RAS_DEBUG__ = { stats: () => viewer.stats() };
      }
    } catch (error) {
      failed(error);
    }
  }),
);
