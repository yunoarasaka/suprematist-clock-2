"use strict";

const {
  app,
  BrowserWindow,
  Menu,
  Tray,
  shell,
  nativeImage,
} = require("electron");
const path = require("path");
const fs = require("fs");

const ROOT = path.join(__dirname, "..");
const INDEX = path.join(ROOT, "index.html");
const ICON = path.join(ROOT, "icons", "suprematist-clock.png");

// Required on Linux (X11/XWayland) for 32-bit ARGB transparent BrowserWindow
app.commandLine.appendSwitch("enable-transparent-visuals");

if (process.platform === "linux") {
  app.setName("suprematist-clock");
}

/** @type {BrowserWindow | null} */
let mainWindow = null;
/** @type {Tray | null} */
let tray = null;

function stateFilePath() {
  return path.join(app.getPath("userData"), "window-state.json");
}

function loadWindowState() {
  const defaults = {
    width: 440,
    height: 500,
    x: undefined,
    y: undefined,
    alwaysOnTop: false,
    skipTaskbar: true,
    opacity: 1.0,
    locked: false,
    clickThrough: false,
  };
  try {
    const p = stateFilePath();
    if (fs.existsSync(p)) {
      const raw = JSON.parse(fs.readFileSync(p, "utf-8"));
      return { ...defaults, ...raw };
    }
  } catch (_) {}
  return defaults;
}

let winState = null;

function saveWindowState() {
  if (!winState) return;
  try {
    if (mainWindow && !mainWindow.isDestroyed()) {
      const b = mainWindow.getBounds();
      winState.x = b.x;
      winState.y = b.y;
      winState.width = b.width;
      winState.height = b.height;
    }
    const p = stateFilePath();
    fs.mkdirSync(path.dirname(p), { recursive: true });
    fs.writeFileSync(p, JSON.stringify(winState, null, 2) + "\n", "utf-8");
  } catch (_) {}
}

function resolveIcon() {
  if (fs.existsSync(ICON)) {
    return nativeImage.createFromPath(ICON);
  }
  return undefined;
}

function runClockAction(jsExpr) {
  if (!mainWindow || mainWindow.isDestroyed()) return;
  mainWindow.webContents
    .executeJavaScript(`window.SuprematistClock && window.SuprematistClock.${jsExpr}`)
    .catch(() => {});
}

function applyWindowFlags() {
  if (!mainWindow || mainWindow.isDestroyed() || !winState) return;
  mainWindow.setAlwaysOnTop(Boolean(winState.alwaysOnTop));
  mainWindow.setSkipTaskbar(Boolean(winState.skipTaskbar));
  mainWindow.setOpacity(Number(winState.opacity) || 1.0);
  mainWindow.setMovable(!winState.locked);
  mainWindow.setResizable(!winState.locked);
  mainWindow.setIgnoreMouseEvents(Boolean(winState.clickThrough), {
    forward: true,
  });
  mainWindow.webContents
    .executeJavaScript(
      `document.documentElement.classList.toggle('locked', ${Boolean(winState.locked)});`
    )
    .catch(() => {});
  saveWindowState();
  updateTrayMenu();
}

function buildContextMenu() {
  const template = [
    {
      label: "Палитра Малевича",
      submenu: [
        {
          label: "Чёрный супремус (Тёмная)",
          click: () => runClockAction("setTheme('dark')"),
        },
        {
          label: "Музейный холст (Светлая)",
          click: () => runClockAction("setTheme('light')"),
        },
        {
          label: "Красный клин (Авангард)",
          click: () => runClockAction("setTheme('red')"),
        },
      ],
    },
    {
      label: "Секундная стрелка",
      submenu: [
        {
          label: "Полёт 0–30с (улетает на 30с)",
          click: () => runClockAction("setSecondMode('flight30')"),
        },
        {
          label: "Вечный дрейф (60с в кадре)",
          click: () => runClockAction("setSecondMode('drift')"),
        },
        {
          label: "В центре циферблата (классика)",
          click: () => runClockAction("setSecondMode('orbit')"),
        },
      ],
    },
    {
      label: "Фон и композиция",
      submenu: [
        {
          label: "Холст + парящие фигуры",
          click: () => runClockAction("setBgMode('full')"),
        },
        {
          label: "Строгий (без фоновых фигур)",
          click: () => runClockAction("setBgMode('minimal')"),
        },
        {
          label: "Прозрачный фон + фигуры",
          click: () => runClockAction("setBgMode('transparent')"),
        },
        {
          label: "Только круг циферблата (прозрачный)",
          click: () => runClockAction("setBgMode('transparent-dial')"),
        },
      ],
    },
    {
      label: "Подпись внизу",
      submenu: [
        {
          label: "Манифест «время · плоскость»",
          click: () => runClockAction("setCaptionMode('manifesto')"),
        },
        {
          label: "Цифровое время и дата",
          click: () => runClockAction("setCaptionMode('digital')"),
        },
        {
          label: "Скрыть подпись",
          click: () => runClockAction("setCaptionMode('hidden')"),
        },
      ],
    },
    { type: "separator" },
    {
      label: "Поверх всех окон",
      type: "checkbox",
      checked: Boolean(winState?.alwaysOnTop),
      click: (item) => {
        winState.alwaysOnTop = item.checked;
        applyWindowFlags();
      },
    },
    {
      label: "Скрывать из панели задач (режим виджета)",
      type: "checkbox",
      checked: Boolean(winState?.skipTaskbar),
      click: (item) => {
        winState.skipTaskbar = item.checked;
        applyWindowFlags();
      },
    },
    {
      label: "Зафиксировать позицию и размер (L)",
      type: "checkbox",
      checked: Boolean(winState?.locked),
      click: (item) => {
        winState.locked = item.checked;
        applyWindowFlags();
      },
    },
    {
      label: "Пропускать клики сквозь окно",
      type: "checkbox",
      checked: Boolean(winState?.clickThrough),
      click: (item) => {
        winState.clickThrough = item.checked;
        applyWindowFlags();
      },
    },
    {
      label: "Прозрачность окна",
      submenu: [1.0, 0.85, 0.7, 0.5].map((op) => ({
        label: `${Math.round(op * 100)}%`,
        type: "radio",
        checked: Math.abs((winState?.opacity || 1) - op) < 0.05,
        click: () => {
          winState.opacity = op;
          applyWindowFlags();
        },
      })),
    },
    {
      label: "Размер окна",
      submenu: [
        {
          label: "Компактный (320 × 360)",
          click: () => mainWindow?.setSize(320, 360),
        },
        {
          label: "Стандартный (440 × 500)",
          click: () => mainWindow?.setSize(440, 500),
        },
        {
          label: "Квадратный (460 × 460)",
          click: () => mainWindow?.setSize(460, 460),
        },
        {
          label: "Крупный (600 × 660)",
          click: () => mainWindow?.setSize(600, 660),
        },
        {
          label: "Широкий холст (960 × 720)",
          click: () => mainWindow?.setSize(960, 720),
        },
      ],
    },
    { type: "separator" },
    {
      label: "Закрыть (Esc / Q)",
      click: () => app.quit(),
    },
  ];

  return Menu.buildFromTemplate(template);
}

function updateTrayMenu() {
  if (!tray) return;
  tray.setContextMenu(buildContextMenu());
}

function setupTray(iconImage) {
  if (!iconImage || iconImage.isEmpty()) return;
  try {
    const trayIcon = iconImage.resize({ width: 22, height: 22 });
    tray = new Tray(trayIcon);
    tray.setToolTip("Супрематистские часы");
    updateTrayMenu();
    tray.on("click", () => {
      if (!mainWindow) return;
      if (mainWindow.isVisible()) {
        mainWindow.focus();
      } else {
        mainWindow.show();
      }
    });
  } catch (_) {}
}

function createWindow() {
  winState = loadWindowState();
  winState.clickThrough = false;

  const iconImage = resolveIcon();

  /** @type {Electron.BrowserWindowConstructorOptions} */
  const opts = {
    width: winState.width,
    height: winState.height,
    x: winState.x,
    y: winState.y,
    minWidth: 220,
    minHeight: 240,
    backgroundColor: "#00000000",
    transparent: true,
    frame: false,
    hasShadow: false,
    alwaysOnTop: Boolean(winState.alwaysOnTop),
    skipTaskbar: Boolean(winState.skipTaskbar),
    resizable: !winState.locked,
    show: false,
    autoHideMenuBar: true,
    title: "Супрематистские часы",
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
    },
  };

  if (iconImage && !iconImage.isEmpty()) {
    opts.icon = iconImage;
  }

  mainWindow = new BrowserWindow(opts);

  const fileUrl = `file://${INDEX.replace(/\\/g, "/")}?widget=1`;
  mainWindow.loadURL(fileUrl);

  mainWindow.once("ready-to-show", () => {
    if (mainWindow) {
      if (process.platform === "linux" && iconImage && !iconImage.isEmpty()) {
        mainWindow.setIcon(iconImage);
      }
      applyWindowFlags();
      mainWindow.show();
    }
  });

  mainWindow.webContents.on("context-menu", () => {
    const menu = buildContextMenu();
    menu.popup({ window: mainWindow });
  });

  mainWindow.webContents.on("before-input-event", (event, input) => {
    if (input.type !== "keyDown") return;
    if (input.key === "Escape" || input.key === "q" || input.key === "Q") {
      event.preventDefault();
      app.quit();
    } else if (input.key === "l" || input.key === "L") {
      event.preventDefault();
      winState.locked = !winState.locked;
      applyWindowFlags();
    }
  });

  mainWindow.on("moved", saveWindowState);
  mainWindow.on("resized", saveWindowState);
  mainWindow.on("close", saveWindowState);

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });

  setupTray(iconImage);
}

app.whenReady().then(() => {
  Menu.setApplicationMenu(null);
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
