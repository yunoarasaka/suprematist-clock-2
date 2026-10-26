#!/usr/bin/env bash
# Launch Suprematist Clock as a Chromium/Chrome app window (Ubuntu).
# Used by .desktop Exec= and by gtk-launch suprematist-clock.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INDEX="file://${ROOT}/index.html"

pick_browser() {
  local c
  for c in \
    google-chrome \
    google-chrome-stable \
    chromium-browser \
    chromium \
    brave-browser \
    microsoft-edge; do
    if command -v "$c" >/dev/null 2>&1; then
      echo "$c"
      return 0
    fi
  done
  return 1
}

BROWSER="$(pick_browser)" || {
  echo "Не найден Chrome/Chromium. Установите:" >&2
  echo "  sudo apt install chromium-browser" >&2
  echo "или откройте вручную: ${INDEX}" >&2
  exit 1
}

# App mode: no tab chrome. Translate disabled so the composition stays clean.
exec "$BROWSER" \
  --app="${INDEX}" \
  --disable-features=Translate,TranslateUI \
  --disable-translate \
  --lang=ru \
  --class=SuprematistClock \
  --window-size=1280,800 \
  "$@"
