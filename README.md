# Супрематистские часы 2.0 / Suprematist Clock 2.0

Аналоговые часы в духе супрематизма Малевича: чёрный / красный / жёлтый / белый / глубокий синий, асимметричные плоскости, чёрный квадрат на циферблате.

Стрелки движутся **непрерывно** — без секундных скачков. Работает на **Windows, macOS и Linux**: в браузере, как приложение и как виджет.

### Возможности (v2.0.0)

- **3 палитры Малевича** (`T`): *Чёрный супремус* (тёмная), *Музейный холст* (светлая бумажная текстура), *Красный клин* (авангардный ноктюрн).
- **3 режима секундной стрелки** (`S` или двойной клик по центру):
  - *Полёт 0–30с* — свободно парит по холсту и улетает за край на 30-й секунде;
  - *Вечный дрейф* — плавает в кадре все 60 секунд (масштаб стрелки адаптивно подстраивается под размер окна/виджета);
  - *В центре циферблата* — классическое вращение вокруг центральной оси.
- **4 режима фона** (`B`): полный холст с парящими фигурами, строгий (только циферблат), **прозрачный фон окна + фигуры** и **только круг циферблата без фона** (парит прямо поверх обоев рабочего стола в Electron и GTK).
- **Живая подпись / цифровые часы** (`D` или клик по подписи): переключение между манифестом `время · плоскость`, цифровым временем с датой (`ЧЧ · ММ · СС — ДН · ЧИСЛО МЕС`) и скрытым режимом.
- **Полноценное контекстное меню (ПКМ) и системный трей** в виджете: фиксация позиции (`L`), режим «пропускать клики сквозь виджет» (click-through), настройка прозрачности окна (`100% / 85% / 70% / 50%`), ресайз за любой край/угол или `Ctrl + колесо мыши`, пресеты размера и сохранение координат между перезапусками.

**Онлайн (GitHub Pages):** https://yunoarasaka.github.io/suprematist-clock-2/

**Репозиторий:** https://github.com/yunoarasaka/suprematist-clock-2

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
2. Выберите файл под вашу систему — в каждом релизе **два набора**:

| Имя файла | Что это |
| --- | --- |
| `SuprematistClock-1.x…` (без `Widget`) | Обычное **приложение** с рамкой окна |
| `SuprematistClock-Widget-1.x…` | Готовый **виджет**: frameless, поверх окон, без панели задач |

Платформы:
- **Windows:** `*-win-setup.exe` (установщик) или `*-win-portable.exe`
- **macOS:** `SuprematistClock-*-mac.dmg` / `.zip` и `SuprematistClock-Widget-*-mac.dmg` / `.zip`
- **Linux:** `.AppImage` / `.deb` — на **Ubuntu 24.04+ / 26** предпочтителен **`.deb`**: пакет ставит AppArmor-профиль с `userns`, и Chromium-sandbox работает без `--no-sandbox`. AppImage путь «плавает», профиль к нему не привязать автоматически — при необходимости запускайте с `--no-sandbox` (не отключайте глобально `apparmor_restrict_unprivileged_userns`). С **v1.1.3** в `.desktop` выставлен верный `StartupWMClass` (совпадает с WM_CLASS Electron), чтобы в доке GNOME была иконка часов, а не шестерёнка.

```bash
# Ubuntu: приложение + виджет из Releases
sudo apt install ./SuprematistClock-*-linux.deb ./SuprematistClock-Widget-*-linux.deb
SuprematistClock
SuprematistClock-Widget
```

3. Скачал → запустил → для Widget сразу безрамочное окно. Исходники: `npm run widget`.

Сборки: GitHub Actions — **Windows + Linux** в `release.yml`; **macOS** (app + widget) в отдельном `release-mac.yml` (`workflow_dispatch`, runner macos-14/13/15).

### 4. Как запустить виджет

| Платформа | Способ |
| --- | --- |
| **Win / Mac / Linux** | Release-файл `SuprematistClock-Widget-*` **или** `npm run widget` |
| **Ubuntu / GNOME** (доп.) | `./widget.sh` — нативный GTK+WebKit виджет (см. ниже) |

---

## English (short)

Cross-platform Suprematist analog clock. Download **Windows, Linux, and macOS** app + Widget from [Releases](https://github.com/yunoarasaka/suprematist-clock/releases) (`SuprematistClock-*` framed app vs `SuprematistClock-Widget-*` frameless; Mac: `.dmg` / `.zip`). On **Ubuntu 24+/26**, prefer the **`.deb`** (ships an AppArmor `userns` profile so the sandbox works without `--no-sandbox`); AppImage may still need `--no-sandbox`. Or use [GitHub Pages](https://yunoarasaka.github.io/suprematist-clock/) / `npm i && npm start` / `npm run widget`. Optional Linux-native GTK widget: `./widget.sh`.

---

## Linux-native виджет (только Ubuntu / GNOME)

Дополнительная опция **только для Linux** (GTK 3 + WebKit2). На Win/Mac используйте Electron-виджет из Releases или `npm run widget`.

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
npm run dist:mac            # dmg/zip — только на macOS / в CI
# отдельный виджет (frameless по умолчанию)
npm run dist:linux:widget   # → dist-widget/
npm run dist:win:widget
npm run dist:mac:widget
```

CI: `.github/workflows/release.yml` — Linux/Windows (app + widget); `.github/workflows/release-mac.yml` — macOS. Push tag `v*` / **workflow_dispatch** для Win+Linux; для Mac — **Release macOS** workflow с указанием тега.

```bash
git tag v1.1.2
git push origin v1.1.2
```

### Ubuntu 24+ / AppArmor (electron-builder ≥26)

`.deb` сборки (app + widget) включают профиль AppArmor (`build/apparmor-profile.tpl` → `/opt/…/resources/apparmor-profile`, установка через `after-install` в `/etc/apparmor.d/<executable>` с правом `userns`). Это снимает FATAL sandbox на системах с `apparmor_restrict_unprivileged_userns=1` без отключения sandbox в коде и без глобального sysctl.

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
  .github/workflows/              # релизы app+widget Win/Mac/Linux
  LICENSE                         # MIT
```

## Лицензия

MIT — см. [LICENSE](LICENSE).
