# Супрематистские часы / Suprematist Clock

Аналоговые часы в духе супрематизма Малевича: чёрный / красный / жёлтый / белый / глубокий синий, асимметричные плоскости, чёрный квадрат на циферблате.

Стрелки движутся **непрерывно** — без секундных скачков. Работает на **Windows, macOS и Linux**: в браузере, как приложение и как виджет.

**Онлайн (GitHub Pages):** https://yunoarasaka.github.io/suprematist-clock/

**Репозиторий:** https://github.com/yunoarasaka/suprematist-clock

---

## Быстрый старт (для новичка)

### 1. Открыть в браузере (любая ОС)

Скачайте репозиторий или клонируйте и откройте файл `index.html` двойным кликом — либо:

```bash
# после git clone
cd suprematist-clock
# Python есть почти везде:
python3 -m http.server 8765
# откройте http://127.0.0.1:8765/
```

Или сразу Pages: https://yunoarasaka.github.io/suprematist-clock/

### 2. Приложение через npm (Windows / macOS / Linux)

Нужны [Node.js](https://nodejs.org/) (LTS) и npm.

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

### 3. Скачать готовый билд (Release)

1. Откройте [Releases](https://github.com/yunoarasaka/suprematist-clock/releases)
2. Выберите файл под вашу систему:
   - **Windows:** `.exe` (установщик или portable)
   - **macOS:** `.dmg` или `.zip`
   - **Linux:** `.AppImage` или `.deb`
3. Установите / запустите. Для виджета из исходников используйте `npm run widget` (см. выше).

Сборки делает GitHub Actions на runners Win/macOS/Linux — с одной Linux-машины `.dmg` нативно не собрать, поэтому релизы приходят из CI.

### 4. Как запустить виджет

| Платформа | Способ |
| --- | --- |
| **Win / Mac / Linux** | `npm run widget` (Electron, без рамок, alwaysOnTop / skipTaskbar) |
| **Ubuntu / GNOME** (доп.) | `./widget.sh` — нативный GTK+WebKit виджет (см. ниже) |

---

## English (short)

Cross-platform Suprematist analog clock: open `index.html` / Pages, or `npm i && npm start` / `npm run widget`, or download a Release build for Windows, macOS, or Linux. Optional Linux-native GTK widget: `./widget.sh`.

---

## Linux-native виджет (только Ubuntu / GNOME)

Дополнительная опция **только для Linux** (GTK 3 + WebKit2). На Win/Mac используйте Electron-виджет.

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
npm run dist:linux   # AppImage, deb
npm run dist:win     # exe (нужен wine на Linux или сборка на Windows)
npm run dist:mac     # dmg — только на macOS / в CI
```

CI: `.github/workflows/release.yml` — push tag `v*` или ручной **workflow_dispatch**.

```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## Структура

```
suprematist-clock/
  index.html              # веб-ядро (браузер / Pages)
  css/  js/  icons/
  electron/main.js        # Electron: app + --widget
  package.json            # electron + electron-builder
  widget.py / widget.sh   # Linux-native GTK виджет
  run.sh / install.sh     # Ubuntu: Chrome --app + меню
  .github/workflows/      # релизы Win/Mac/Linux
  LICENSE                 # MIT
```

## Лицензия

MIT — см. [LICENSE](LICENSE).
