#!/usr/bin/env bash
# Launch Suprematist Clock 2.0 (frameless transparent desktop clock).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

GI_CAIRO_PATH="${ROOT}/.deps/gi-cairo/usr/lib/python3/dist-packages"
if [[ -d "${GI_CAIRO_PATH}" ]]; then
  export PYTHONPATH="${GI_CAIRO_PATH}${PYTHONPATH:+:${PYTHONPATH}}"
fi

if command -v python3 >/dev/null 2>&1 && python3 -c '
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.1")
' 2>/dev/null; then
  exec python3 "${ROOT}/widget.py" "$@"
fi

if [[ -x "${ROOT}/dist/linux-unpacked/SuprematistClock" ]]; then
  exec "${ROOT}/dist/linux-unpacked/SuprematistClock" --no-sandbox "$@"
fi

if [[ -x "${ROOT}/node_modules/electron/dist/electron" ]]; then
  exec "${ROOT}/node_modules/electron/dist/electron" "${ROOT}" --no-sandbox "$@"
fi

echo "Не найден ни GTK3+WebKit2, ни Electron." >&2
echo "  sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1" >&2
exit 1
