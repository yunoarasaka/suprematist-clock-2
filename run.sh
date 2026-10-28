#!/usr/bin/env bash
# Launch Suprematist Clock with true RGBA window transparency support.
# Uses native GTK3+WebKit2 (or built Electron app) instead of Chrome --app,
# because Chrome --app has an opaque white browser backdrop and cannot be transparent.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ -x "${ROOT}/widget.sh" ]] && python3 -c '
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.1")
' 2>/dev/null; then
  exec "${ROOT}/widget.sh" --app "$@"
fi

if [[ -x "${ROOT}/dist/linux-unpacked/SuprematistClock" ]]; then
  exec "${ROOT}/dist/linux-unpacked/SuprematistClock" --no-sandbox "$@"
fi

if [[ -x "${ROOT}/node_modules/electron/dist/electron" ]]; then
  exec "${ROOT}/node_modules/electron/dist/electron" "${ROOT}" --no-sandbox "$@"
fi

echo "Не найден ни GTK3+WebKit2, ни Electron." >&2
exit 1
