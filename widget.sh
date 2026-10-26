#!/usr/bin/env bash
# Launch Suprematist Clock as a frameless desktop widget (GTK3 + WebKit2).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Нужен python3" >&2
  exit 1
fi

# Optional local python3-gi-cairo (for WebKit snapshot / cairo foreign on minimal images)
GI_CAIRO_PATH="${ROOT}/.deps/gi-cairo/usr/lib/python3/dist-packages"
if [[ -d "${GI_CAIRO_PATH}" ]]; then
  export PYTHONPATH="${GI_CAIRO_PATH}${PYTHONPATH:+:${PYTHONPATH}}"
fi

if ! python3 -c '
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.1")
from gi.repository import Gtk, WebKit2  # noqa: F401
' 2>/dev/null; then
  echo "Нужны пакеты: python3-gi, gir1.2-gtk-3.0, gir1.2-webkit2-4.1" >&2
  echo "  sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1" >&2
  exit 1
fi

exec python3 "${ROOT}/widget.py" "$@"
