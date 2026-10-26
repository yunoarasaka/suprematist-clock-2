(() => {
  "use strict";

  const hourIndicator = document.getElementById("hour-indicator");
  const minuteIndicator = document.getElementById("minute-indicator");
  const secondHand = document.getElementById("second-hand");
  const flyingSecond = document.getElementById("flying-second");
  const marks = document.getElementById("marks");

  const CX = 240;
  const CY = 240;
  const OUTER = 168;

  /** Soft pad inside viewport while drifting (0→30s). */
  const DRIFT_PAD = 72;
  /** Half extent of the hand graphic — used for off-screen checks. */
  const HAND_EXTENT = 220;

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

  // ——— Flying second: position in viewport coords ———
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

  function viewportSize() {
    return {
      W: window.innerWidth || document.documentElement.clientWidth || 1280,
      H: window.innerHeight || document.documentElement.clientHeight || 800,
    };
  }

  function pickTarget(W, H) {
    const pad = DRIFT_PAD;
    tx = pad + Math.random() * Math.max(1, W - 2 * pad);
    ty = pad + Math.random() * Math.max(1, H - 2 * pad);
  }

  function spawnOnScreen(W, H) {
    pickTarget(W, H);
    px = tx;
    py = ty;
    const ang = Math.random() * Math.PI * 2;
    const speed = 40 + Math.random() * 50;
    vx = Math.cos(ang) * speed;
    vy = Math.sin(ang) * speed;
    pickTarget(W, H);
    exiting = false;
    offscreen = false;
  }

  function parkOffscreen(W, H) {
    px = W + HAND_EXTENT * 2;
    py = H * 0.5;
    vx = 0;
    vy = 0;
    exiting = true;
    offscreen = true;
  }

  function beginExit(W, H) {
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
    // Boost outward so the leave reads clearly
    const boost = 180;
    vx += (dx / n) * boost;
    vy += (dy / n) * boost;
  }

  function isFullyOff(W, H) {
    return (
      px < -HAND_EXTENT ||
      px > W + HAND_EXTENT ||
      py < -HAND_EXTENT ||
      py > H + HAND_EXTENT
    );
  }

  function updateFlight(dt, seconds) {
    const { W, H } = viewportSize();

    // Minute wrap → reappear at random on-screen point
    if (prevSeconds > 50 && seconds < 10) {
      spawnOnScreen(W, H);
    }
    prevSeconds = seconds;

    if (seconds < 30) {
      if (offscreen || exiting) {
        // Page load mid-half or recovered early — ensure on screen
        if (offscreen) spawnOnScreen(W, H);
        exiting = false;
        offscreen = false;
      }

      // Soft seek toward wandering targets
      const dx = tx - px;
      const dy = ty - py;
      if (Math.hypot(dx, dy) < 48) pickTarget(W, H);

      vx += dx * 1.1 * dt;
      vy += dy * 1.1 * dt;
      vx *= Math.pow(0.92, dt * 60);
      vy *= Math.pow(0.92, dt * 60);

      const sp = Math.hypot(vx, vy);
      const maxSp = 140;
      if (sp > maxSp) {
        vx = (vx / sp) * maxSp;
        vy = (vy / sp) * maxSp;
      }

      px += vx * dt;
      py += vy * dt;

      // Soft clamp inside viewport
      const loX = DRIFT_PAD;
      const hiX = W - DRIFT_PAD;
      const loY = DRIFT_PAD;
      const hiY = H - DRIFT_PAD;
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
      // ≥30s: leave the frame
      if (!offscreen) beginExit(W, H);

      if (!offscreen) {
        // Keep accelerating outward
        const cx = W * 0.5;
        const cy = H * 0.5;
        let dx = px - cx;
        let dy = py - cy;
        const n = Math.hypot(dx, dy) || 1;
        vx += (dx / n) * 320 * dt;
        vy += (dy / n) * 320 * dt;
        px += vx * dt;
        py += vy * dt;

        if (isFullyOff(W, H)) {
          offscreen = true;
          vx = 0;
          vy = 0;
        }
      }
    }

    flyingSecond.style.transform = `translate(${px}px, ${py}px)`;
  }

  function frame(ts) {
    const now = new Date();
    const { hour, minute, second, seconds } = anglesFromNow(now);

    setRotate(hourIndicator, hour);
    setRotate(minuteIndicator, minute);
    setLocalRotate(secondHand, second);

    const dt = lastTs ? Math.min(0.05, (ts - lastTs) / 1000) : 1 / 60;
    lastTs = ts;
    updateFlight(dt, seconds);

    requestAnimationFrame(frame);
  }

  buildMarks();

  // Initial placement from wall-clock second
  {
    const { seconds } = anglesFromNow();
    const { W, H } = viewportSize();
    prevSeconds = seconds;
    if (seconds < 30) spawnOnScreen(W, H);
    else parkOffscreen(W, H);
    flyingSecond.style.transform = `translate(${px}px, ${py}px)`;
  }

  requestAnimationFrame(frame);

  document.addEventListener("keydown", (e) => {
    if (e.key === "f" || e.key === "F" || e.key === "F11") {
      e.preventDefault();
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen?.();
      } else {
        document.exitFullscreen?.();
      }
    }
  });
})();
