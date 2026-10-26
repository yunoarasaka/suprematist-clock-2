#!/usr/bin/env bash
# Remove user-local Suprematist Clock desktop entries and icons.
set -euo pipefail

APP_ID="suprematist-clock"
WIDGET_ID="suprematist-clock-widget"
ICON_NAME="suprematist-clock"
APPS_DIR="${HOME}/.local/share/applications"
HICOLOR="${HOME}/.local/share/icons/hicolor"

rm -f "${APPS_DIR}/${APP_ID}.desktop"
rm -f "${APPS_DIR}/${WIDGET_ID}.desktop"
rm -f "${HOME}/.local/share/icons/${ICON_NAME}.png"
rm -f "${HICOLOR}/scalable/apps/${ICON_NAME}.svg"
for sz in 48 64 128 256; do
  rm -f "${HICOLOR}/${sz}x${sz}/apps/${ICON_NAME}.png"
done

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "${APPS_DIR}" 2>/dev/null || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -f -t "${HICOLOR}" 2>/dev/null || true
fi

echo "Удалено: ярлыки ${APP_ID}, ${WIDGET_ID} и иконки"
