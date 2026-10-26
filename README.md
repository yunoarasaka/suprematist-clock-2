# Супрематистские часы / Suprematist Clock

Аналоговые часы в духе супрематизма Малевича: чёрный / красный / жёлтый / белый / глубокий синий, асимметричные плоскости, чёрный квадрат на циферблате.

Стрелки движутся **непрерывно** — без секундных скачков. В браузере — на любой ОС; готовые сборки приложения и виджета — для **Windows и Linux**.

**Онлайн (GitHub Pages):** https://yunoarasaka.github.io/suprematist-clock/

**Репозиторий:** https://github.com/yunoarasaka/suprematist-clock

---

## Быстрый старт (для новичка)

### 1. Открыть в браузере (любая ОС, включая macOS)

Скачайте репозиторий или клонируйте и откройте файл `index.html` двойным кликом — либо:

```bash
# после git clone
cd suprematist-clock
# Python есть почти везде:
python3 -m http.server 8765
# откройте http://127.0.0.1:8765/
```

Или сразу Pages: https://yunoarasaka.github.io/suprematist-clock/

**macOS:** готовой сборки (`.dmg` / native install) нет. Откройте Pages по ссылке выше или запустите из исходников (`npm start` / `npm run widget`).

### 2. Приложение через npm (из исходников)

Нужны [Node.js](https://nodejs.org/) (LTS) и npm. Работает на Windows, Linux и macOS (исходники; готовый Mac-билд не публикуется).

```bash
git clone https://github.com/yunoarasaka/suprematist-clock.git
cd suprematist-clock
npm install
npm start          # обычное окно приложения
npm run widget     # виджет: без рамок, поверх окон (alwaysOnTop)
```

| Команда | Что делает |
| --- | --- |
| `npm start` | Electron-окно приложения |
| `npm run widget` | Frameless-виджет (`--widget`) |

### 3. Скачать готовый билд (Release) — Windows и Linux

1. Откройте [Releases](https://github.com/yunoarasaka/suprematist-clock/releases)
2. Выберите файл под вашу систему — в каждом релизе **два набора**:

| Имя файла | Что это |
| --- | --- |
| `SuprematistClock-1.x…` (без `Widget`) | Обычное **приложение** с рамкой окна |
| `SuprematistClock-Widget-1.x…` | Готовый **виджет**: frameless, поверх окон, без панели задач |

Платформы:
- **Windows:** `*-win-setup.exe` (установщик) или `*-win-portable.exe`
- **Linux:** `.AppImage` / `.deb`
- **macOS:** готовых артефактов в Releases нет — используйте [GitHub Pages](https://yunoarasaka.github.io/suprematist-clock/) или `npm start` из исходников

3. Скачал → запустил → для Widget сразу безрамочное окно. Исходники: `npm run widget`.

Сборки делает GitHub Actions (**Windows + Linux**, app и widget).

### 4. Как запустить виджет

| Платформа | Способ |
| --- | --- |
| **Windows / Linux** | Release-файл `SuprematistClock-Widget-*` **или** `npm run widget` |
| **macOS** | Только из исходников: `npm run widget` (или браузер / Pages) |
| **Ubuntu / GNOME** (доп.) | `./widget.sh` — нативный GTK+WebKit виджет (см. ниже) |

---

## English (short)

Suprematist analog clock. **Windows & Linux:** download app + Widget from [Releases](https://github.com/yunoarasaka/suprematist-clock/releases). **macOS:** no packaged build — use [GitHub Pages](https://yunoarasaka.github.io/suprematist-clock/) or `npm i && npm start` / `npm run widget` from source. Optional Linux-native GTK widget: `./widget.sh`.

---

## Linux-native виджет (только Ubuntu / GNOME)

Дополнительная опция **только для Linux** (GTK 3 + WebKit2). На Windows используйте Electron-виджет из Releases или `npm run widget`; на macOS — только `npm run widget` / браузер.

```bash
sudo apt install -y python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1
chmod +x widget.sh widget.py
./widget.sh
```

Установка в меню приложений (без sudo):

```bash
./install.sh
# удаление: ./uninstall.sh
```

Управление GTK-виджетом: ЛКМ — перетащить, ПКМ — меню (зафиксировать / слой / закрыть), **L** — lock, **Esc**/**Q** — закрыть.

> На Wayland `keep_below` / `skip_taskbar` — best-effort. На X11 обычно надёжнее.

---

## Сборка релизов локально

```bash
npm install
# приложение
npm run dist:linux          # AppImage, deb → dist/
npm run dist:win            # exe (wine на Linux или Windows)
# отдельный виджет (frameless по умолчанию)
npm run dist:linux:widget   # → dist-widget/
npm run dist:win:widget
```

CI (`.github/workflows/release.yml`) собирает **app и widget** только для **Linux и Windows**. Push tag `v*` или **workflow_dispatch**.

```bash
git tag v1.1.0
git push origin v1.1.0
```

Локальные скрипты `dist:mac` / `dist:mac:widget` в `package.json` могут оставаться для разработчиков на macOS; в CI и Releases они не используются.

---

## Структура

```
suprematist-clock/
  index.html                      # веб-ядро (браузер / Pages)
  css/  js/  icons/
  electron/main.js                # Electron: app + --widget
  electron/main-widget.js         # entry packaged widget (WIDGET по умолчанию)
  electron-builder.widget.yml     # отдельная сборка виджета
  package.json                    # electron + electron-builder
  widget.py / widget.sh           # Linux-native GTK виджет
  run.sh / install.sh             # Ubuntu: Chrome --app + меню
  .github/workflows/              # релизы app+widget Win/Linux
  LICENSE                         # MIT
```

## Лицензия

MIT — см. [LICENSE](LICENSE).
