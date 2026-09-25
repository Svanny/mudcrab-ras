/** A keyboard-accessible camera menu with an icon for every view. */
export function createCameraControls(root, onChange) {
  const trigger = root.querySelector("#camera");
  const menu = root.querySelector('[role="menu"]');
  const options = [...menu.querySelectorAll('[role="menuitemradio"]')];
  let current = "overview";

  function close(returnFocus = false) {
    menu.hidden = true;
    trigger.setAttribute("aria-expanded", "false");
    if (returnFocus) trigger.focus();
  }

  function open() {
    menu.hidden = false;
    trigger.setAttribute("aria-expanded", "true");
    options.find((option) => option.dataset.camera === current).focus();
  }

  function select(value) {
    const selected = options.find((option) => option.dataset.camera === value);
    if (!selected) return;
    current = value;
    for (const option of options) {
      option.setAttribute("aria-checked", option === selected);
    }
    const label = selected.querySelector("span").textContent;
    trigger.querySelector(".camera-label").textContent = label;
    trigger.querySelector("use").setAttribute("href", `#view-${value}`);
    trigger.setAttribute("aria-label", `Camera view: ${label}`);
    trigger.dataset.view = value;
    onChange(value);
  }

  trigger.addEventListener("click", () => (menu.hidden ? open() : close()));
  trigger.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      open();
    }
  });
  options.forEach((option) =>
    option.addEventListener("click", () => {
      select(option.dataset.camera);
      close(true);
    }),
  );
  menu.addEventListener("keydown", (event) => {
    const index = options.indexOf(document.activeElement);
    const moves = {
      ArrowDown: (index + 1) % options.length,
      ArrowUp: (index - 1 + options.length) % options.length,
      Home: 0,
      End: options.length - 1,
    };
    if (event.key in moves) {
      event.preventDefault();
      options[moves[event.key]].focus();
    } else if (event.key === "Escape") {
      event.preventDefault();
      event.stopPropagation();
      close(true);
    } else if (event.key === "Tab") {
      // Restore the trigger before native tabbing continues past the menu.
      close(true);
    }
  });
  document.addEventListener("pointerdown", (event) => {
    if (!root.contains(event.target)) close();
  });
  root.addEventListener("focusout", (event) => {
    if (!root.contains(event.relatedTarget)) close();
  });
  window.addEventListener("blur", () => close());

  return {
    get value() {
      return current;
    },
    reset() {
      select("overview");
      close();
    },
  };
}
