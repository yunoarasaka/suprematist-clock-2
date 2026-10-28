(() => {
  "use strict";

  const STORAGE_KEY = "suprematist_clock_prefs_v1";

  const hourIndicator = document.getElementById("hour-indicator");
  const minuteIndicator = document.getElementById("minute-indicator");
  const secondHand = document.getElementById("second-hand");
  const flyingSecond = document.getElementById("flying-second");
  const marks = document.getElementById("marks");
  const clockSvg = document.getElementById("clock-svg");
  const centerHub = document.getElementById("center-hub");
  const fieldEl = document.getElementById("field");
  const brandCaption = document.getElementById("brand-caption");
  const hudEl = document.getElementById("hud");

  const btnTheme = document.getElementById("btn-theme");
  const btnSecond = document.getElementById("btn-second");
  const btnBg = document.getElementById("btn-bg");
  const btnCaption = document.getElementById("btn-caption");

  const lblTheme = document.getElementById("lbl-theme");
  const lblSecond = document.getElementById("lbl-second");
  const lblBg = document.getElementById("lbl-bg");
  const lblCaption = document.getElementById("lbl-caption");

  const CX = 240;
  const CY = 240;
  const OUTER = 168;

  const THEMES = ["dark", "light", "red"];
  const THEME_LABELS = {
    dark: "чёрный",
    light: "холст",
    red: "клин",
  };

  const SECOND_MODES = ["flight30", "drift", "orbit"];
  const SECOND_LABELS = {
    flight30: "30с полёт",
    drift: "дрейф 60с",
    orbit: "в центре",
  };

  const BG_MODES = ["full", "minimal", "transparent", "transparent-dial"];
  const BG_LABELS = {
    full: "холст",
    minimal: "строгий",
    transparent: "прозр.+фиг.",
    "transparent-dial": "прозр.круг",
  };

  const CAPTION_MODES = ["manifesto", "digital", "hidden"];
  const CAPTION_LABELS = {
    manifesto: "манифест",
    digital: "цифры",
    hidden: "скрыть",
  };

  const DAYS_RU = ["вс", "пн", "вт", "ср", "чт", "пт", "сб"];
  const MONTHS_RU = [
    "янв", "фев", "мар", "апр", "май", "июн",
    "июл", "авг", "сен", "окт", "ноя", "дек",
  ];

  const state = {
    theme: "dark",
    secondMode: "flight30",
    bgMode: "full",
    captionMode: "manifesto",
  };

  function loadPrefs() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (THEMES.includes(parsed.theme)) state.theme = parsed.theme;
        if (SECOND_MODES.includes(parsed.secondMode)) state.secondMode = parsed.secondMode;
        if (BG_MODES.includes(parsed.bgMode)) state.bgMode = parsed.bgMode;
        if (CAPTION_MODES.includes(parsed.captionMode)) state.captionMode = parsed.captionMode;
      }
    } catch (_) {}

    const q = location.search || "";
    if (/(?:^|[?&])transparent=1(?:&|$)/.test(q)) {
      state.bgMode = "transparent";
    }
  }

  function savePrefs() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (_) {}
    try {
      window.webkit?.messageHandlers?.prefs?.postMessage(JSON.stringify(state));
    } catch (_) {}
  }

  function applyStateToDOM() {
    const root = document.documentElement;
    if (state.theme === "dark") {
      root.removeAttribute("data-theme");
    } else {
      root.setAttribute("data-theme", state.theme);
    }
    root.setAttribute("data-bg", state.bgMode);
    root.setAttribute("data-caption", state.captionMode);

    if (lblTheme) lblTheme.textContent = THEME_LABELS[state.theme] || state.theme;
    if (lblSecond) lblSecond.textContent = SECOND_LABELS[state.secondMode] || state.secondMode;
    if (lblBg) lblBg.textContent = BG_LABELS[state.bgMode] || state.bgMode;
    if (lblCaption) lblCaption.textContent = CAPTION_LABELS[state.captionMode] || state.captionMode;

    if (brandCaption) {
      if (state.captionMode === "manifesto") {
        brandCaption.classList.remove("is-digital");
        brandCaption.textContent = "время · плоскость";
      } else if (state.captionMode === "digital") {
        brandCaption.classList.add("is-digital");
        updateDigitalCaption(new Date());
      }
    }
  }

  let lastDigitalSecond = -1;
  function updateDigitalCaption(now) {
    if (state.captionMode !== "digital" || !brandCaption) return;
    const sec = now.getSeconds();
    if (sec === lastDigitalSecond) return;
    lastDigitalSecond = sec;

    const hh = String(now.getHours()).padStart(2, "0");
    const mm = String(now.getMinutes()).padStart(2, "0");
    const ss = String(sec).padStart(2, "0");
    const dayName = DAYS_RU[now.getDay()];
    const dayNum = now.getDate();
    const monthName = MONTHS_RU[now.getMonth()];
    brandCaption.textContent = `${hh} · ${mm} · ${ss}   —   ${dayName} · ${dayNum} ${monthName}`;
  }

  function buildMarks() {
    const frag = document.createDocumentFragment();
    for (let i = 0; i < 60; i++) {
      const angle = (i / 60) * Math.PI * 2 - Math.PI / 2;
      const major = i % 5 === 0;
      const cardinal = i % 15 === 0; // 12 / 3 / 6 / 9
      const len = cardinal ? 26 : major ? 18 : 8;
      const inset = cardinal ? 6 : major ? 8 : 12;
      const x1 = CX + Math.cos(angle) * (OUTER - inset);
      const y1 = CY + Math.sin(angle) * (OUTER - inset);
      const x2 = CX + Math.cos(angle) * (OUTER - inset - len);
      const y2 = CY + Math.sin(angle) * (OUTER - inset - len);
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", x1.toFixed(2));
      line.setAttribute("y1", y1.toFixed(2));
      line.setAttribute("x2", x2.toFixed(2));
      line.setAttribute("y2", y2.toFixed(2));
      const kind = cardinal
        ? "mark mark-major mark-cardinal"
        : major
          ? "mark mark-major"
          : "mark mark-minor";
      line.setAttribute("class", kind);
      frag.appendChild(line);
    }
    marks.appendChild(frag);
  }

  /**
   * Continuous angles from real wall-clock time (including ms).
   * Second sweeps; minute/hour interpolate with fractional seconds.
   */
  function anglesFromNow(now = new Date()) {
    const ms = now.getMilliseconds();
    const s = now.getSeconds() + ms / 1000;
    const m = now.getMinutes() + s / 60;
    const h = (now.getHours() % 12) + m / 60;

    return {
      second: s * 6,
      minute: m * 6,
      hour: h * 30,
      seconds: s,
    };
  }

  /** SVG attribute only — no CSS transform-origin (breaks Chrome). */
  function setRotate(el, deg) {
    el.setAttribute("transform", `rotate(${deg} ${CX} ${CY})`);
  }

  /** Local pivot rotate for flying second (around 0,0 in its viewBox). */
  function setLocalRotate(el, deg) {
    el.setAttribute("transform", `rotate(${deg})`);
  }

  // ——— Flying second: position & proportional scale in viewport coords ———
  let px = 0;
  let py = 0;
  let vx = 0;
  let vy = 0;
  let tx = 0;
  let ty = 0;
  let exiting = false;
  let offscreen = false;
  let prevSeconds = -1;
  let lastTs = 0;

  function viewportMetrics() {
    const W = window.innerWidth || document.documentElement.clientWidth || 1280;
    const H = window.innerHeight || document.documentElement.clientHeight || 800;
    const minDim = Math.min(W, H);
    // Scale the second hand proportionally to the clock SVG (78vmin capped at 560px)
    const dialPx = Math.min(minDim * 0.78, 560);
    const scale = Math.max(0.36, Math.min(1.18, dialPx / 480));
    const pad = Math.max(28, Math.round(72 * scale));
    const extent = Math.round(220 * scale);
    return { W, H, scale, pad, extent };
  }

  function dialCenterInViewport(W, H) {
    if (clockSvg) {
      const rect = clockSvg.getBoundingClientRect();
      if (rect.width > 0 && rect.height > 0) {
        return {
          cx: rect.left + rect.width * 0.5,
          cy: rect.top + rect.height * 0.5,
        };
      }
    }
    return { cx: W * 0.5, cy: H * 0.5 };
  }

  function pickTarget(W, H, pad) {
    tx = pad + Math.random() * Math.max(1, W - 2 * pad);
    ty = pad + Math.random() * Math.max(1, H - 2 * pad);
  }

  function spawnOnScreen(W, H, pad, scale = 1) {
    pickTarget(W, H, pad);
    px = tx;
    py = ty;
    const ang = Math.random() * Math.PI * 2;
    const speed = (40 + Math.random() * 50) * scale;
    vx = Math.cos(ang) * speed;
    vy = Math.sin(ang) * speed;
    pickTarget(W, H, pad);
    exiting = false;
    offscreen = false;
  }

  function parkOffscreen(W, H, extent) {
    px = W + extent * 2;
    py = H * 0.5;
    vx = 0;
    vy = 0;
    exiting = true;
    offscreen = true;
  }

  function beginExit(W, H, scale) {
    if (exiting) return;
    exiting = true;
    const cx = W * 0.5;
    const cy = H * 0.5;
    let dx = px - cx;
    let dy = py - cy;
    let n = Math.hypot(dx, dy);
    if (n < 8) {
      dx = vx;
      dy = vy;
      n = Math.hypot(dx, dy);
    }
    if (n < 8) {
      dx = Math.random() < 0.5 ? 1 : -1;
      dy = (Math.random() - 0.5) * 0.6;
      n = Math.hypot(dx, dy);
    }
    const boost = 180 * scale;
    vx += (dx / n) * boost;
    vy += (dy / n) * boost;
  }

  function isFullyOff(W, H, extent) {
    return (
      px < -extent ||
      px > W + extent ||
      py < -extent ||
      py > H + extent
    );
  }

  function updateFlight(dt, seconds) {
    const { W, H, scale, pad, extent } = viewportMetrics();

    if (state.secondMode === "orbit") {
      // Smoothly glide to and stay locked at the center of the dial
      const { cx, cy } = dialCenterInViewport(W, H);
      if (offscreen) {
        px = cx;
        py = cy;
      } else {
        const lerp = 1 - Math.pow(0.001, dt);
        px += (cx - px) * lerp;
        py += (cy - py) * lerp;
      }
      vx = 0;
      vy = 0;
      exiting = false;
      offscreen = false;
      prevSeconds = seconds;
      flyingSecond.style.transform = `translate(${px.toFixed(2)}px, ${py.toFixed(2)}px) scale(${scale.toFixed(3)})`;
      return;
    }

    // Minute wrap → reappear at random on-screen point (in flight30 mode)
    if (state.secondMode === "flight30" && prevSeconds > 50 && seconds < 10) {
      spawnOnScreen(W, H, pad, scale);
    }
    prevSeconds = seconds;

    const shouldDrift = state.secondMode === "drift" || seconds < 30;

    if (shouldDrift) {
      if (offscreen || exiting) {
        if (offscreen) spawnOnScreen(W, H, pad, scale);
        exiting = false;
        offscreen = false;
      }

      const dx = tx - px;
      const dy = ty - py;
      if (Math.hypot(dx, dy) < 48 * scale) pickTarget(W, H, pad);

      vx += dx * 1.1 * dt;
      vy += dy * 1.1 * dt;
      vx *= Math.pow(0.92, dt * 60);
      vy *= Math.pow(0.92, dt * 60);

      const sp = Math.hypot(vx, vy);
      const maxSp = 140 * scale;
      if (sp > maxSp) {
        vx = (vx / sp) * maxSp;
        vy = (vy / sp) * maxSp;
      }

      px += vx * dt;
      py += vy * dt;

      const loX = pad;
      const hiX = Math.max(pad, W - pad);
      const loY = pad;
      const hiY = Math.max(pad, H - pad);
      if (px < loX) {
        px = loX;
        vx = Math.abs(vx) * 0.7;
      } else if (px > hiX) {
        px = hiX;
        vx = -Math.abs(vx) * 0.7;
      }
      if (py < loY) {
        py = loY;
        vy = Math.abs(vy) * 0.7;
      } else if (py > hiY) {
        py = hiY;
        vy = -Math.abs(vy) * 0.7;
      }
    } else {
      // ≥30s in flight30 mode: leave the frame
      if (!offscreen) beginExit(W, H, scale);

      if (!offscreen) {
        const cx = W * 0.5;
        const cy = H * 0.5;
        const dx = px - cx;
        const dy = py - cy;
        const n = Math.hypot(dx, dy) || 1;
        vx += (dx / n) * 320 * scale * dt;
        vy += (dy / n) * 320 * scale * dt;
        px += vx * dt;
        py += vy * dt;

        if (isFullyOff(W, H, extent)) {
          offscreen = true;
          vx = 0;
          vy = 0;
        }
      }
    }

    flyingSecond.style.transform = `translate(${px.toFixed(2)}px, ${py.toFixed(2)}px) scale(${scale.toFixed(3)})`;
  }

  function frame(ts) {
    const now = new Date();
    const { hour, minute, second, seconds } = anglesFromNow(now);

    setRotate(hourIndicator, hour);
    setRotate(minuteIndicator, minute);
    setLocalRotate(secondHand, second);

    updateDigitalCaption(now);

    const dt = lastTs ? Math.min(0.05, (ts - lastTs) / 1000) : 1 / 60;
    lastTs = ts;
    updateFlight(dt, seconds);

    requestAnimationFrame(frame);
  }

  // ——— Controls & public API ———
  function cycleItem(arr, current) {
    const idx = arr.indexOf(current);
    return arr[(idx + 1) % arr.length];
  }

  function setTheme(theme) {
    if (!THEMES.includes(theme)) return;
    state.theme = theme;
    savePrefs();
    applyStateToDOM();
  }

  function cycleTheme() {
    setTheme(cycleItem(THEMES, state.theme));
  }

  function setSecondMode(mode) {
    if (!SECOND_MODES.includes(mode)) return;
    state.secondMode = mode;
    if (mode === "drift" && offscreen) {
      const { W, H, pad, scale } = viewportMetrics();
      spawnOnScreen(W, H, pad, scale);
    }
    savePrefs();
    applyStateToDOM();
  }

  function cycleSecondMode() {
    setSecondMode(cycleItem(SECOND_MODES, state.secondMode));
  }

  function setBgMode(mode) {
    if (!BG_MODES.includes(mode)) return;
    state.bgMode = mode;
    savePrefs();
    applyStateToDOM();
  }

  function cycleBgMode() {
    setBgMode(cycleItem(BG_MODES, state.bgMode));
  }

  function setCaptionMode(mode) {
    if (!CAPTION_MODES.includes(mode)) return;
    state.captionMode = mode;
    lastDigitalSecond = -1;
    savePrefs();
    applyStateToDOM();
  }

  function cycleCaptionMode() {
    setCaptionMode(cycleItem(CAPTION_MODES, state.captionMode));
  }

  // Expose API for Electron / GTK WebKit2 host menus
  window.SuprematistClock = {
    getState: () => ({ ...state }),
    setTheme,
    cycleTheme,
    setSecondMode,
    cycleSecondMode,
    setBgMode,
    cycleBgMode,
    setCaptionMode,
    cycleCaptionMode,
  };

  // ——— Wire UI events ———
  loadPrefs();
  buildMarks();
  applyStateToDOM();

  {
    const { seconds } = anglesFromNow();
    const { W, H, scale, pad, extent } = viewportMetrics();
    prevSeconds = seconds;
    if (state.secondMode === "orbit") {
      const { cx, cy } = dialCenterInViewport(W, H);
      px = cx;
      py = cy;
    } else if (state.secondMode === "drift" || seconds < 30) {
      spawnOnScreen(W, H, pad, scale);
    } else {
      parkOffscreen(W, H, extent);
    }
    flyingSecond.style.transform = `translate(${px.toFixed(2)}px, ${py.toFixed(2)}px) scale(${scale.toFixed(3)})`;
  }

  requestAnimationFrame(frame);

  if (btnTheme) btnTheme.addEventListener("click", cycleTheme);
  if (btnSecond) btnSecond.addEventListener("click", cycleSecondMode);
  if (btnBg) btnBg.addEventListener("click", cycleBgMode);
  if (btnCaption) btnCaption.addEventListener("click", cycleCaptionMode);

  if (brandCaption) {
    brandCaption.addEventListener("click", cycleCaptionMode);
    brandCaption.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        cycleCaptionMode();
      }
    });
  }

  if (centerHub) {
    centerHub.addEventListener("dblclick", () => {
      cycleSecondMode();
    });
  }

  // Subtle mouse parallax on background field + edge resize cursor in widget mode
  const reduceMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)");
  const RESIZE_EDGE = 14;
  window.addEventListener("pointermove", (e) => {
    const W = window.innerWidth || 1;
    const H = window.innerHeight || 1;

    if (
      document.documentElement.classList.contains("widget") &&
      !document.documentElement.classList.contains("locked")
    ) {
      const left = e.clientX < RESIZE_EDGE;
      const right = e.clientX > W - RESIZE_EDGE;
      const top = e.clientY < RESIZE_EDGE;
      const bottom = e.clientY > H - RESIZE_EDGE;
      let cur = "";
      if ((left && top) || (right && bottom)) cur = "nwse-resize";
      else if ((right && top) || (left && bottom)) cur = "nesw-resize";
      else if (left || right) cur = "ew-resize";
      else if (top || bottom) cur = "ns-resize";
      document.documentElement.style.cursor = cur;
      document.body.style.cursor = cur;
    } else {
      document.documentElement.style.cursor = "";
      document.body.style.cursor = "";
    }

    if (!fieldEl || reduceMotion?.matches) return;
    const nx = (e.clientX / W - 0.5) * 2;
    const ny = (e.clientY / H - 0.5) * 2;
    fieldEl.style.transform = `translate(${(-nx * 10).toFixed(1)}px, ${(-ny * 10).toFixed(1)}px)`;
  });

  document.addEventListener("keydown", (e) => {
    if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA")) return;
    const k = e.key;
    if (k === "f" || k === "F" || k === "F11") {
      e.preventDefault();
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen?.();
      } else {
        document.exitFullscreen?.();
      }
    } else if (k === "t" || k === "T" || k === "е" || k === "Е") {
      cycleTheme();
    } else if (k === "s" || k === "S" || k === "ы" || k === "Ы") {
      cycleSecondMode();
    } else if (k === "b" || k === "B" || k === "и" || k === "И") {
      cycleBgMode();
    } else if (k === "d" || k === "D" || k === "в" || k === "В") {
      cycleCaptionMode();
    } else if (k === "h" || k === "H" || k === "р" || k === "Р") {
      hudEl?.classList.toggle("is-pinned");
    }
  });
})();
