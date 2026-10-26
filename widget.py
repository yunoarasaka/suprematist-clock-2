#!/usr/bin/env python3
"""Frameless desktop widget for Suprematist Clock (GTK3 + WebKit2).

Designed for Ubuntu GNOME. On Wayland, decorations / skip-taskbar / keep-below
are best-effort Mutter hints (no gtk-layer-shell). Undecorated + drag still work.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import gi

try:
    gi.require_foreign("cairo")
except (ImportError, ValueError):
    pass

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("WebKit2", "4.1")

from gi.repository import Gdk, GLib, Gtk, WebKit2  # noqa: E402

APP_ID = "suprematist-clock-widget"
ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
CONFIG_DIR = Path.home() / ".config" / "suprematist-clock"
CONFIG_PATH = CONFIG_DIR / "widget.json"

DEFAULTS = {
    "x": 48,
    "y": 48,
    "w": 440,
    "h": 500,
    "locked": False,
    "layer": "below",  # below | above | normal
}


def load_config() -> dict:
    cfg = dict(DEFAULTS)
    try:
        if CONFIG_PATH.is_file():
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                cfg.update({k: data[k] for k in DEFAULTS if k in data})
    except (OSError, json.JSONDecodeError, TypeError):
        pass
    return cfg


def save_config(cfg: dict) -> None:
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(
            json.dumps(cfg, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"widget: cannot save config: {exc}", file=sys.stderr)


class ClockWidget(Gtk.Window):
    def __init__(self) -> None:
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.cfg = load_config()
        self._drag_enabled = not bool(self.cfg.get("locked"))

        self.set_title("Супрематистские часы")
        self.set_name(APP_ID)
        self.set_decorated(False)
        self.set_resizable(True)
        self.set_accept_focus(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_urgency_hint(False)
        # UTILITY tends to stay out of the GNOME dock / Alt-Tab better than NORMAL.
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_default_size(int(self.cfg["w"]), int(self.cfg["h"]))

        self.connect("destroy", self._on_destroy)
        self.connect("delete-event", self._on_delete)
        self.connect("configure-event", self._on_configure)
        self.connect("key-press-event", self._on_key)

        self.view = WebKit2.WebView()
        settings = self.view.get_settings()
        settings.set_enable_developer_extras(False)
        settings.set_allow_file_access_from_file_urls(True)
        settings.set_allow_universal_access_from_file_urls(True)
        settings.set_enable_smooth_scrolling(True)
        try:
            settings.set_hardware_acceleration_policy(
                WebKit2.HardwareAccelerationPolicy.ALWAYS
            )
        except (AttributeError, TypeError):
            pass

        # Invisible EventBox above the WebView captures drag / menu;
        # the clock itself needs no pointer interaction. (No DrawingArea:
        # python3-cairo is optional and a draw handler would spam errors.)
        overlay = Gtk.Overlay()
        overlay.add(self.view)

        self.grab = Gtk.EventBox()
        self.grab.set_visible_window(False)
        self.grab.set_hexpand(True)
        self.grab.set_vexpand(True)
        filler = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        filler.set_hexpand(True)
        filler.set_vexpand(True)
        self.grab.add(filler)
        self.grab.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
        )
        self.grab.connect("button-press-event", self._on_press)
        overlay.add_overlay(self.grab)
        overlay.set_overlay_pass_through(self.grab, False)

        self.add(overlay)

        uri = INDEX.resolve().as_uri() + "?widget=1"
        self.view.connect("load-changed", self._on_load_changed)
        self.view.load_uri(uri)

        self._apply_layer(str(self.cfg.get("layer") or "below"))
        self._menu = self._build_menu()

        self.show_all()
        GLib.idle_add(self._place_initial)

    def _place_initial(self) -> bool:
        x, y = int(self.cfg["x"]), int(self.cfg["y"])
        try:
            self.move(x, y)
        except Exception:
            pass
        # Re-assert hints after map (Mutter sometimes resets them).
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self._apply_layer(str(self.cfg.get("layer") or "below"))
        return False

    def _apply_layer(self, layer: str) -> None:
        layer = layer if layer in ("below", "above", "normal") else "below"
        self.cfg["layer"] = layer
        self.set_keep_below(layer == "below")
        self.set_keep_above(layer == "above")

    def _on_load_changed(self, view: WebKit2.WebView, event: WebKit2.LoadEvent) -> None:
        if event != WebKit2.LoadEvent.FINISHED:
            return
        # Mark document for widget-specific CSS; strip browser chrome affordances.
        script = (
            "document.documentElement.classList.add('widget');"
            "document.title = 'Супрематистские часы';"
        )
        try:
            view.evaluate_javascript(script, -1, None, None, None, None, None)
        except TypeError:
            view.run_javascript(script, None, None)

    def _build_menu(self) -> Gtk.Menu:
        menu = Gtk.Menu()

        def item(label: str, cb) -> None:
            mi = Gtk.MenuItem(label=label)
            mi.connect("activate", cb)
            menu.append(mi)

        item("Перемещать окно" if not self._drag_enabled else "Зафиксировать позицию", self._toggle_lock)
        item("Слой: под окнами (виджет)", lambda *_: self._set_layer("below"))
        item("Слой: поверх окон", lambda *_: self._set_layer("above"))
        item("Слой: обычный", lambda *_: self._set_layer("normal"))
        menu.append(Gtk.SeparatorMenuItem())
        item("Закрыть", lambda *_: self.close())
        menu.show_all()
        return menu

    def _rebuild_menu(self) -> None:
        self._menu = self._build_menu()

    def _toggle_lock(self, *_args) -> None:
        self._drag_enabled = not self._drag_enabled
        self.cfg["locked"] = not self._drag_enabled
        save_config(self.cfg)
        self._rebuild_menu()

    def _set_layer(self, layer: str) -> None:
        self._apply_layer(layer)
        save_config(self.cfg)

    def _on_press(self, _widget, event: Gdk.EventButton) -> bool:
        if event.type != Gdk.EventType.BUTTON_PRESS:
            return False
        if event.button == 3:
            self._rebuild_menu()
            self._menu.popup_at_pointer(event)
            return True
        if event.button == 1 and self._drag_enabled:
            self.begin_move_drag(
                int(event.button),
                int(event.x_root),
                int(event.y_root),
                int(event.time),
            )
            return True
        if event.button == 2:
            # Middle-click always moves, even when locked.
            self.begin_move_drag(
                int(event.button),
                int(event.x_root),
                int(event.y_root),
                int(event.time),
            )
            return True
        return False

    def _on_key(self, _widget, event: Gdk.EventKey) -> bool:
        key = Gdk.keyval_name(event.keyval) or ""
        if key in ("Escape", "q", "Q"):
            self.close()
            return True
        if key in ("l", "L"):
            self._toggle_lock()
            return True
        return False

    def _on_configure(self, _widget, event: Gdk.EventConfigure) -> bool:
        self.cfg["x"] = int(event.x)
        self.cfg["y"] = int(event.y)
        self.cfg["w"] = int(event.width)
        self.cfg["h"] = int(event.height)
        return False

    def _persist(self) -> None:
        self.cfg["locked"] = not self._drag_enabled
        save_config(self.cfg)

    def _on_delete(self, *_args) -> bool:
        self._persist()
        return False

    def _on_destroy(self, *_args) -> None:
        self._persist()
        Gtk.main_quit()


def _parse_args(argv: list[str]) -> tuple[str | None, float]:
    """Return (snapshot_path_or_None, delay_sec)."""
    snap: str | None = None
    delay = 1.6
    args = list(argv)
    while args:
        a = args.pop(0)
        if a == "--snapshot" and args:
            snap = args.pop(0)
        elif a.startswith("--snapshot="):
            snap = a.split("=", 1)[1]
        elif a == "--delay" and args:
            delay = float(args.pop(0))
        elif a in ("-h", "--help"):
            print(
                "Usage: widget.py [--snapshot FILE.png] [--delay SECONDS]\n"
                "  Frameless Suprematist Clock desktop widget."
            )
            sys.exit(0)
        else:
            print(f"widget: unknown arg {a}", file=sys.stderr)
            sys.exit(2)
    return snap, delay


def main() -> int:
    if not INDEX.is_file():
        print(f"widget: missing {INDEX}", file=sys.stderr)
        return 1
    snap_path, delay = _parse_args(sys.argv[1:])
    # Prefer dark chrome around the undecorated edge.
    os.environ.setdefault("GTK_THEME", os.environ.get("GTK_THEME", "Adwaita:dark"))
    GLib.set_prgname(APP_ID)
    win = ClockWidget()

    if snap_path:

        def _finish_ok(path: Path, detail: str) -> None:
            print(f"widget: wrote {path} ({detail})")
            Gtk.main_quit()

        def _do_snap() -> bool:
            out = Path(snap_path)
            out.parent.mkdir(parents=True, exist_ok=True)

            def _webkit_done(view, result, _data=None):
                try:
                    surface = view.get_snapshot_finish(result)
                    surface.write_to_png(str(out))
                    _finish_ok(out, f"{surface.get_width()}x{surface.get_height()} webkit")
                    return
                except Exception as exc:
                    print(f"widget: webkit snapshot failed: {exc}", file=sys.stderr)
                # Fallback: Gdk (often blank for GPU WebKit on Wayland)
                gdk_win = win.get_window()
                if gdk_win is None:
                    Gtk.main_quit()
                    return
                w = gdk_win.get_width()
                h = gdk_win.get_height()
                pb = Gdk.pixbuf_get_from_window(gdk_win, 0, 0, w, h)
                if pb is None:
                    print("widget: pixbuf_get_from_window returned None", file=sys.stderr)
                    Gtk.main_quit()
                    return
                try:
                    pb.savev(str(out), "png", [], [])
                    _finish_ok(out, f"{w}x{h} gdk")
                except Exception as exc:
                    print(f"widget: write png failed: {exc}", file=sys.stderr)
                    Gtk.main_quit()

            try:
                win.view.get_snapshot(
                    WebKit2.SnapshotRegion.VISIBLE,
                    WebKit2.SnapshotOptions.NONE,
                    None,
                    _webkit_done,
                    None,
                )
            except Exception as exc:
                print(f"widget: get_snapshot error: {exc}", file=sys.stderr)
                Gtk.main_quit()
            return False

        GLib.timeout_add(int(delay * 1000), _do_snap)

    Gtk.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
