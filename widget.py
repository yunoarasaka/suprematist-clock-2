#!/usr/bin/env python3
"""Frameless desktop widget for Suprematist Clock (GTK3 + WebKit2).

Designed for Ubuntu GNOME. Uses X11/XWayland backend when available so
32-bit RGBA window transparency, keep-below, skip-taskbar, and window
position persistence all work reliably under Mutter.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Under GNOME Wayland, native Wayland forbids window move/keep-below/skip-taskbar
# and can paint opaque window backers. XWayland (x11) supports full 32-bit RGBA
# transparency + desktop widget window hints.
if os.environ.get("DISPLAY"):
    os.environ.setdefault("GDK_BACKEND", "x11")

import gi  # noqa: E402

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
ICON_PATH = ROOT / "icons" / "suprematist-clock.png"
CONFIG_DIR = Path.home() / ".config" / "suprematist-clock"
CONFIG_PATH = CONFIG_DIR / "widget.json"

DEFAULTS = {
    "x": 48,
    "y": 48,
    "w": 440,
    "h": 500,
    "locked": False,
    "layer": "below",  # below | above | normal
    "opacity": 1.0,
    "theme": "dark",  # dark | light | red
    "secondMode": "flight30",  # flight30 | drift | orbit
    "bgMode": "full",  # full | minimal | transparent | transparent-dial
    "captionMode": "manifesto",  # manifesto | digital | hidden
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
    def __init__(self, framed: bool = False) -> None:
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.cfg = load_config()
        self._framed = framed
        self._drag_enabled = not bool(self.cfg.get("locked"))

        # Clear Adwaita's solid window background so 32-bit RGBA transparency works
        css = Gtk.CssProvider()
        css.load_from_data(
            b"window, window.background, .background {"
            b"  background-color: rgba(0, 0, 0, 0);"
            b"  background-image: none;"
            b"  box-shadow: none;"
            b"  border: none;"
            b"}"
        )
        screen = self.get_screen()
        if screen is not None:
            Gtk.StyleContext.add_provider_for_screen(
                screen,
                css,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )
            visual = screen.get_rgba_visual()
            if visual is not None and screen.is_composited():
                self.set_visual(visual)
                self.set_app_paintable(True)

        self.set_title("Супрематистские часы")
        self.set_name("SuprematistClock" if framed else APP_ID)
        self.set_decorated(False)
        self.set_resizable(True)
        self.set_accept_focus(True)
        if not framed:
            self.set_skip_taskbar_hint(True)
            self.set_skip_pager_hint(True)
            self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_urgency_hint(False)
        self.set_default_size(int(self.cfg["w"]), int(self.cfg["h"]))

        if ICON_PATH.is_file():
            try:
                self.set_icon_from_file(str(ICON_PATH))
            except Exception:
                pass

        self.connect("destroy", self._on_destroy)
        self.connect("delete-event", self._on_delete)
        self.connect("configure-event", self._on_configure)
        self.connect("key-press-event", self._on_key)

        ucm = WebKit2.UserContentManager()
        try:
            ucm.connect("script-message-received::prefs", self._on_js_prefs)
            ucm.register_script_message_handler("prefs")
        except Exception:
            pass

        self.view = WebKit2.WebView.new_with_user_content_manager(ucm)
        try:
            self.view.set_background_color(Gdk.RGBA(0.0, 0.0, 0.0, 0.0))
        except Exception:
            pass

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

        self.view.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.SCROLL_MASK
        )
        self.view.connect("button-press-event", self._on_press)
        self.view.connect("scroll-event", self._on_scroll)
        self.view.connect("context-menu", self._on_webkit_context_menu)

        self.add(self.view)

        uri = INDEX.resolve().as_uri() + "?widget=1"
        self.view.connect("load-changed", self._on_load_changed)
        self.view.load_uri(uri)

        if not self._framed:
            self._apply_layer(str(self.cfg.get("layer") or "below"))
        self._menu = self._build_menu()

        self.show_all()
        GLib.idle_add(self._place_initial)

    def _on_webkit_context_menu(self, *_args) -> bool:
        return True

    def _on_js_prefs(self, _ucm, js_result) -> None:
        try:
            val = js_result.get_js_value().to_string()
            data = json.loads(val)
            if isinstance(data, dict):
                for k in ("theme", "secondMode", "bgMode", "captionMode"):
                    if k in data:
                        self.cfg[k] = data[k]
                save_config(self.cfg)
        except Exception:
            pass

    def _run_js(self, script: str) -> None:
        try:
            self.view.evaluate_javascript(script, -1, None, None, None, None, None)
        except TypeError:
            self.view.run_javascript(script, None, None)

    def _sync_js_state(self) -> None:
        theme = self.cfg.get("theme", "dark")
        sec = self.cfg.get("secondMode", "flight30")
        bg = self.cfg.get("bgMode", "full")
        cap = self.cfg.get("captionMode", "manifesto")
        locked = "true" if not self._drag_enabled else "false"
        script = (
            "document.documentElement.classList.add('widget');"
            f"document.documentElement.classList.toggle('locked', {locked});"
            "document.title = 'Супрематистские часы';"
            "if (window.SuprematistClock) {"
            f"  window.SuprematistClock.setTheme({json.dumps(theme)});"
            f"  window.SuprematistClock.setSecondMode({json.dumps(sec)});"
            f"  window.SuprematistClock.setBgMode({json.dumps(bg)});"
            f"  window.SuprematistClock.setCaptionMode({json.dumps(cap)});"
            "}"
        )
        self._run_js(script)

    def _place_initial(self) -> bool:
        x, y = int(self.cfg["x"]), int(self.cfg["y"])
        try:
            self.move(x, y)
        except Exception:
            pass
        if not self._framed:
            self.set_skip_taskbar_hint(True)
            self.set_skip_pager_hint(True)
            self._apply_layer(str(self.cfg.get("layer") or "below"))
        self._apply_opacity(float(self.cfg.get("opacity") or 1.0))
        return False

    def _apply_layer(self, layer: str) -> None:
        layer = layer if layer in ("below", "above", "normal") else "below"
        self.cfg["layer"] = layer
        self.set_keep_below(layer == "below")
        self.set_keep_above(layer == "above")

    def _apply_opacity(self, opacity: float) -> None:
        opacity = max(0.3, min(1.0, float(opacity)))
        self.cfg["opacity"] = opacity
        try:
            Gtk.Widget.set_opacity(self, opacity)
        except Exception:
            pass

    def _on_load_changed(self, _view: WebKit2.WebView, event: WebKit2.LoadEvent) -> None:
        if event != WebKit2.LoadEvent.FINISHED:
            return
        self._sync_js_state()

    def _build_menu(self) -> Gtk.Menu:
        menu = Gtk.Menu()

        def item(label: str, cb, parent: Gtk.Menu = menu) -> None:
            mi = Gtk.MenuItem(label=label)
            mi.connect("activate", cb)
            parent.append(mi)

        def submenu(title: str) -> Gtk.Menu:
            mi = Gtk.MenuItem(label=title)
            sub = Gtk.Menu()
            mi.set_submenu(sub)
            menu.append(mi)
            return sub

        # Theme submenu
        sub_theme = submenu("Палитра Малевича (T)")
        for key, title in (
            ("dark", "Чёрный супремус (Тёмная)"),
            ("light", "Музейный холст (Светлая)"),
            ("red", "Красный клин (Авангард)"),
        ):
            prefix = "● " if self.cfg.get("theme") == key else "   "
            item(prefix + title, lambda _w, k=key: self._set_pref("theme", k), sub_theme)

        # Second hand submenu
        sub_sec = submenu("Секундная стрелка (S)")
        for key, title in (
            ("flight30", "Полёт 0–30с (улетает на 30с)"),
            ("drift", "Вечный дрейф (60с в кадре)"),
            ("orbit", "В центре циферблата (классика)"),
        ):
            prefix = "● " if self.cfg.get("secondMode") == key else "   "
            item(prefix + title, lambda _w, k=key: self._set_pref("secondMode", k), sub_sec)

        # Background submenu
        sub_bg = submenu("Фон и композиция (B)")
        for key, title in (
            ("full", "Холст + парящие фигуры"),
            ("minimal", "Строгий (без фоновых фигур)"),
            ("transparent", "Прозрачный фон + фигуры"),
            ("transparent-dial", "Только круг циферблата (прозрачный)"),
        ):
            prefix = "● " if self.cfg.get("bgMode") == key else "   "
            item(prefix + title, lambda _w, k=key: self._set_pref("bgMode", k), sub_bg)

        # Caption submenu
        sub_cap = submenu("Подпись внизу (D)")
        for key, title in (
            ("manifesto", "Манифест «время · плоскость»"),
            ("digital", "Цифровое время и дата"),
            ("hidden", "Скрыть подпись"),
        ):
            prefix = "● " if self.cfg.get("captionMode") == key else "   "
            item(prefix + title, lambda _w, k=key: self._set_pref("captionMode", k), sub_cap)

        menu.append(Gtk.SeparatorMenuItem())

        # Layer submenu
        sub_layer = submenu("Слой окна")
        for key, title in (
            ("below", "Под окнами (виджет на столе)"),
            ("above", "Поверх всех окон"),
            ("normal", "Обычное окно"),
        ):
            prefix = "● " if self.cfg.get("layer") == key else "   "
            item(prefix + title, lambda _w, k=key: self._set_layer(k), sub_layer)

        # Opacity submenu
        sub_op = submenu("Прозрачность окна")
        for op in (1.0, 0.85, 0.7, 0.5):
            active = abs(float(self.cfg.get("opacity", 1.0)) - op) < 0.05
            prefix = "● " if active else "   "
            item(f"{prefix}{int(op * 100)}%", lambda _w, val=op: self._set_opacity(val), sub_op)

        # Size presets submenu
        sub_sz = submenu("Размер виджета")
        for label, w, h in (
            ("Компактный (320 × 360)", 320, 360),
            ("Стандартный (440 × 500)", 440, 500),
            ("Квадратный (460 × 460)", 460, 460),
            ("Крупный (600 × 660)", 600, 660),
        ):
            item(label, lambda _w, rw=w, rh=h: self.resize(rw, rh), sub_sz)

        item(
            "Разблокировать перемещение (L)"
            if not self._drag_enabled
            else "Зафиксировать позицию (L)",
            self._toggle_lock,
        )

        menu.append(Gtk.SeparatorMenuItem())
        item("Закрыть (Esc / Q)", lambda *_: self.close())
        menu.show_all()
        return menu

    def _rebuild_menu(self) -> None:
        self._menu = self._build_menu()

    def _set_pref(self, key: str, val: str) -> None:
        self.cfg[key] = val
        save_config(self.cfg)
        self._sync_js_state()
        self._rebuild_menu()

    def _cycle_pref(self, key: str, options: tuple[str, ...]) -> None:
        cur = str(self.cfg.get(key) or options[0])
        idx = options.index(cur) if cur in options else 0
        nxt = options[(idx + 1) % len(options)]
        self._set_pref(key, nxt)

    def _toggle_lock(self, *_args) -> None:
        self._drag_enabled = not self._drag_enabled
        self.cfg["locked"] = not self._drag_enabled
        save_config(self.cfg)
        self._sync_js_state()
        self._rebuild_menu()

    def _set_layer(self, layer: str) -> None:
        self._apply_layer(layer)
        save_config(self.cfg)
        self._rebuild_menu()

    def _set_opacity(self, opacity: float) -> None:
        self._apply_opacity(opacity)
        save_config(self.cfg)
        self._rebuild_menu()

    @staticmethod
    def _edge_at(x: float, y: float, w: int, h: int, margin: int = 14) -> Gdk.WindowEdge | None:
        left = x < margin
        right = x > w - margin
        top = y < margin
        bottom = y > h - margin
        if top and left:
            return Gdk.WindowEdge.NORTH_WEST
        if top and right:
            return Gdk.WindowEdge.NORTH_EAST
        if bottom and left:
            return Gdk.WindowEdge.SOUTH_WEST
        if bottom and right:
            return Gdk.WindowEdge.SOUTH_EAST
        if top:
            return Gdk.WindowEdge.NORTH
        if bottom:
            return Gdk.WindowEdge.SOUTH
        if left:
            return Gdk.WindowEdge.WEST
        if right:
            return Gdk.WindowEdge.EAST
        return None

    def _on_scroll(self, _widget: Gtk.Widget, event: Gdk.EventScroll) -> bool:
        if not self._drag_enabled:
            return False
        # Ctrl + wheel or Alt + wheel scales the widget smoothly
        mods = event.state & (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD1_MASK)
        if not mods:
            return False
        step = 0
        if event.direction == Gdk.ScrollDirection.UP:
            step = 24
        elif event.direction == Gdk.ScrollDirection.DOWN:
            step = -24
        elif event.direction == Gdk.ScrollDirection.SMOOTH:
            ok, _dx, dy = event.get_scroll_deltas()
            if ok and abs(dy) > 0.01:
                step = -24 if dy > 0 else 24
        if step != 0:
            w, h = self.get_size()
            nw = max(220, min(1400, w + step))
            nh = max(240, min(1400, h + step))
            self.resize(nw, nh)
            return True
        return False

    def _on_press(self, widget: Gtk.Widget, event: Gdk.EventButton) -> bool:
        if event.type != Gdk.EventType.BUTTON_PRESS:
            return False
        if event.button == 3:
            self._rebuild_menu()
            self._menu.popup_at_pointer(event)
            return True
        if event.button == 1:
            alloc = widget.get_allocation()
            if self._drag_enabled:
                edge = self._edge_at(event.x, event.y, alloc.width, alloc.height)
                if edge is not None:
                    self.begin_resize_drag(
                        edge,
                        int(event.button),
                        int(event.x_root),
                        int(event.y_root),
                        int(event.time),
                    )
                    return True
            # Let clicks on the bottom HUD bar or caption pass through to WebKit!
            if event.y >= alloc.height - 68:
                return False
            if self._drag_enabled:
                self.begin_move_drag(
                    int(event.button),
                    int(event.x_root),
                    int(event.y_root),
                    int(event.time),
                )
                return True
        if event.button == 2:
            self.begin_move_drag(
                int(event.button),
                int(event.x_root),
                int(event.y_root),
                int(event.time),
            )
            return True
        return False

    def _on_key(self, _widget, event: Gdk.EventKey) -> bool:
        key = (Gdk.keyval_name(event.keyval) or "").lower()
        if key in ("escape", "q"):
            self.close()
            return True
        if key == "l":
            self._toggle_lock()
            return True
        if key == "t":
            self._cycle_pref("theme", ("dark", "light", "red"))
            return True
        if key == "s":
            self._cycle_pref("secondMode", ("flight30", "drift", "orbit"))
            return True
        if key == "b":
            self._cycle_pref("bgMode", ("full", "minimal", "transparent", "transparent-dial"))
            return True
        if key == "d":
            self._cycle_pref("captionMode", ("manifesto", "digital", "hidden"))
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


def _parse_args(argv: list[str]) -> tuple[str | None, float, bool]:
    """Return (snapshot_path_or_None, delay_sec, framed)."""
    snap: str | None = None
    delay = 1.6
    framed = False
    args = list(argv)
    while args:
        a = args.pop(0)
        if a == "--snapshot" and args:
            snap = args.pop(0)
        elif a.startswith("--snapshot="):
            snap = a.split("=", 1)[1]
        elif a == "--delay" and args:
            delay = float(args.pop(0))
        elif a == "--app":
            framed = True
        elif a in ("-h", "--help"):
            print(
                "Usage: widget.py [--app] [--snapshot FILE.png] [--delay SECONDS]\n"
                "  Frameless Suprematist Clock desktop widget."
            )
            sys.exit(0)
        else:
            print(f"widget: unknown arg {a}", file=sys.stderr)
            sys.exit(2)
    return snap, delay, framed


def main() -> int:
    if not INDEX.is_file():
        print(f"widget: missing {INDEX}", file=sys.stderr)
        return 1
    snap_path, delay, framed = _parse_args(sys.argv[1:])
    os.environ.setdefault("GTK_THEME", os.environ.get("GTK_THEME", "Adwaita:dark"))
    GLib.set_prgname("SuprematistClock" if framed else APP_ID)
    win = ClockWidget(framed=framed)

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
                    WebKit2.SnapshotOptions.TRANSPARENT_BACKGROUND,
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
