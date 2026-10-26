#!/usr/bin/env bash
# Install Suprematist Clock as a user-local Ubuntu application (no sudo).
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ID="suprematist-clock"
WIDGET_ID="suprematist-clock-widget"
ICON_NAME="suprematist-clock"

APPS_DIR="${HOME}/.local/share/applications"
HICOLOR="${HOME}/.local/share/icons/hicolor"
DESKTOP_DST="${APPS_DIR}/${APP_ID}.desktop"
WIDGET_DST="${APPS_DIR}/${WIDGET_ID}.desktop"

chmod +x "${APP_DIR}/run.sh" "${APP_DIR}/install.sh" "${APP_DIR}/widget.sh" "${APP_DIR}/widget.py"
[[ -f "${APP_DIR}/uninstall.sh" ]] && chmod +x "${APP_DIR}/uninstall.sh"

mkdir -p "${APPS_DIR}"
mkdir -p "${HICOLOR}/scalable/apps"
for sz in 48 64 128 256; do
  mkdir -p "${HICOLOR}/${sz}x${sz}/apps"
done

# Icons
install -m 644 "${APP_DIR}/icons/${ICON_NAME}.svg" \
  "${HICOLOR}/scalable/apps/${ICON_NAME}.svg"

for sz in 48 64 128 256; do
  src="${APP_DIR}/icons/${ICON_NAME}-${sz}.png"
  if [[ ! -f "$src" ]]; then
    echo "Missing icon: $src (run: python3 icons/render_pngs.py)" >&2
    exit 1
  fi
  install -m 644 "$src" "${HICOLOR}/${sz}x${sz}/apps/${ICON_NAME}.png"
done

# Also drop a fallback copy under ~/.local/share/icons/
mkdir -p "${HOME}/.local/share/icons"
install -m 644 "${APP_DIR}/icons/${ICON_NAME}-256.png" \
  "${HOME}/.local/share/icons/${ICON_NAME}.png"

# Desktop entry — ordinary app window (Chrome --app)
cat > "${DESKTOP_DST}" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Супрематистские часы
Name[en]=Suprematist Clock
Comment=Аналоговые часы в стиле супрематизма
Comment[en]=Analog clock in Suprematism style
Exec=${APP_DIR}/run.sh
Path=${APP_DIR}
Icon=${ICON_NAME}
Terminal=false
Categories=Utility;
StartupWMClass=SuprematistClock
Keywords=clock;часы;suprematism;супрематизм;malevich;малевич;
EOF
chmod +x "${DESKTOP_DST}"

# Desktop entry — frameless desktop widget
cat > "${WIDGET_DST}" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Супрематистские часы (виджет)
Name[en]=Suprematist Clock (widget)
Comment=Виджет на рабочий стол без рамок
Comment[en]=Frameless desktop widget clock
Exec=${APP_DIR}/widget.sh
Path=${APP_DIR}
Icon=${ICON_NAME}
Terminal=false
Categories=Utility;
StartupWMClass=suprematist-clock-widget
Keywords=clock;widget;виджет;часы;suprematism;супрематизм;
EOF
chmod +x "${WIDGET_DST}"

# Keep project-local .desktop files in sync
cp "${DESKTOP_DST}" "${APP_DIR}/suprematist-clock.desktop"
cp "${WIDGET_DST}" "${APP_DIR}/suprematist-clock-widget.desktop"

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "${APPS_DIR}" 2>/dev/null || true
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -f -t "${HICOLOR}" 2>/dev/null || true
fi

echo "Установлено:"
echo "  ${DESKTOP_DST}"
echo "  ${WIDGET_DST}"
echo "  ${HICOLOR}/*/apps/${ICON_NAME}.{png,svg}"
echo "В меню:"
echo "  «Супрематистские часы»           — обычное окно"
echo "  «Супрематистские часы (виджет)»  — без рамок на стол"
echo "Запуск: gtk-launch ${APP_ID}  |  gtk-launch ${WIDGET_ID}"
echo "        ${APP_DIR}/run.sh     |  ${APP_DIR}/widget.sh"
