"use strict";

const { app, BrowserWindow, Menu, shell } = require("electron");
const path = require("path");

const ROOT = path.join(__dirname, "..");
const INDEX = path.join(ROOT, "index.html");
const ICON = path.join(ROOT, "icons", "suprematist-clock.png");

const isWidget =
  process.argv.includes("--widget") ||
  process.env.SUPREMATIST_WIDGET === "1";

/** @type {BrowserWindow | null} */
let mainWindow = null;

function createWindow() {
  /** @type {Electron.BrowserWindowConstructorOptions} */
  const opts = {
    width: isWidget ? 440 : 1280,
    height: isWidget ? 500 : 800,
    minWidth: isWidget ? 280 : 640,
    minHeight: isWidget ? 320 : 480,
    backgroundColor: "#0a0a12",
    icon: ICON,
    show: false,
    autoHideMenuBar: true,
    title: isWidget ? "Супрематистские часы (виджет)" : "Супрематистские часы",
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
    },
  };

  if (isWidget) {
    opts.frame = false;
    opts.alwaysOnTop = true;
    opts.skipTaskbar = true;
    opts.hasShadow = false;
    opts.resizable = true;
    if (process.platform === "darwin") {
      opts.titleBarStyle = "hidden";
    }
  }

  mainWindow = new BrowserWindow(opts);

  // Prefer file URL with query so index.html early script sees widget=1
  const fileUrl = `file://${INDEX.replace(/\\/g, "/")}${isWidget ? "?widget=1" : ""}`;
  mainWindow.loadURL(fileUrl);

  mainWindow.once("ready-to-show", () => {
    if (mainWindow) mainWindow.show();
  });

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
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
