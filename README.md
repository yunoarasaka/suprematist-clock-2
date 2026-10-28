# Супрематистские часы 2.0 / Suprematist Clock 2.0

Аналоговые часы в духе супрематизма Малевича: чёрный / красный / жёлтый / белый / глубокий синий, асимметричные плоскости, чёрный квадрат на циферблате.

Стрелки движутся **непрерывно** — без секундных скачков. Работает на **Windows, macOS и Linux**: в браузере, как приложение и как прозрачный виджет на рабочий стол.

- **Онлайн (GitHub Pages):** https://yunoarasaka.github.io/suprematist-clock-2/
- **Репозиторий:** https://github.com/yunoarasaka/suprematist-clock-2
- **Скачать готовые сборки (Releases):** https://github.com/yunoarasaka/suprematist-clock-2/releases

---

## Что нового в 2.0

- **3 палитры Малевича** (`T`):
  - *Чёрный супремус* — классическая глубокая тёмная сцена;
  - *Музейный холст* — светлая бумажная фактура холста с контрастной геометрией;
  - *Красный клин* — авангардный багрово-чёрный ноктюрн.
- **3 режима секундной стрелки** (`S` или двойной клик по центру циферблата):
  - *Полёт 0–30с* — свободно парит по холсту и улетает за край на 30-й секунде;
  - *Вечный дрейф 60с* — плавает в кадре всю минуту без исчезновений (масштаб стрелки адаптивно подстраивается под размер окна);
  - *В центре циферблата* — классическое вращение вокруг центральной оси.
- **4 режима фона и настоящая 32-битная RGBA-прозрачность** (`B`):
  - *Холст + фигуры* — полный фон и парящие супрематические плоскости;
  - *Строгий* — без фоновых фигур;
  - *Прозрачный фон + фигуры* — убирает коробку окна, фигуры и циферблат парят прямо поверх обоев рабочего стола;
  - *Только круг циферблата (прозрачный)* — на столе остаётся только сам круглый циферблат.
- **Живая подпись / цифровые часы** (`D` или клик по подписи): переключение между манифестом `время · плоскость`, цифровым временем с датой (`ЧЧ · ММ · СС — ДН · ЧИСЛО МЕС`) и скрытым режимом.
- **Быстрый HUD-док + контекстное меню (ПКМ) и системный трей**:
  - Фиксация позиции и размера (`L`);
  - Режим «Пропускать клики сквозь виджет» (click-through в Electron — управляется через иконку в трее);
  - Настройка прозрачности окна (`100% / 85% / 70% / 50%`);
  - Ресайз мышкой за любой край или угол окна (`14px` зона) либо плавное масштабирование через **`Ctrl + колесо мыши`** (`Alt + колесо`);
  - Автоматическое сохранение позиции, размеров и выбранной темы между перезапусками;
  - Обновлённая скруглённая иконка приложения (squircle) в точном дизайне циферблата.

---

## Горячие клавиши и управление

| Клавиша / действие | Что делает |
| --- | --- |
| **ЛКМ (внутри окна)** | Перетащить виджет / окно |
| **ЛКМ (за край или угол)** | Изменить размер окна |
| **`Ctrl` / `Alt` + колесо мыши** | Плавно увеличить / уменьшить размер виджета |
| **ПКМ** | Открыть контекстное меню со всеми настройками |
| **Двойной клик по центру** | Переключить режим секундной стрелки |
| **Клик по подписи внизу** | Переключить манифест / цифровое время и дату / скрыть |
| **`T`** | Сменить палитру (*Чёрный супремус* → *Музейный холст* → *Красный клин*) |
| **`S`** | Сменить режим секундной стрелки (*30с полёт* → *Дрейф 60с* → *В центре*) |
| **`B`** | Сменить режим фона (*Холст* → *Строгий* → *Прозр.+фигуры* → *Прозр.круг*) |
| **`D`** | Сменить режим нижней подписи (*Манифест* → *Цифры и дата* → *Скрыть*) |
| **`H`** | Закрепить / скрыть нижнюю панель быстрых кнопок (HUD) |
| **`L`** | Зафиксировать / разблокировать перемещение и размер окна |
| **`F` / `F11`** | Полноэкранный режим |
| **`Esc` / `Q`** | Закрыть окно / виджет |

---

## Быстрый старт

### 1. Скачать готовый билд (Windows / macOS / Linux)

Откройте [Releases](https://github.com/yunoarasaka/suprematist-clock-2/releases) и скачайте сборку под вашу ОС. В каждом релизе два варианта:

| Вариант | Поведение в системе |
| --- | --- |
| `SuprematistClock-2.x…` (Приложение) | Отображается в панели задач / доке и `Alt+Tab`, крупный стартовый размер (`1280×800`) |
| `SuprematistClock-Widget-2.x…` (Виджет) | Скрыт из панели задач и `Alt+Tab` (`skipTaskbar`), управляется из ПКМ и системного трея, компактный размер (`440×500`), закреплён на рабочем столе |

- **Windows:** `*-win-setup.exe` (установщик), `*-win-portable.exe` или `*-win-x64.zip`
- **macOS:** `SuprematistClock-*-mac.zip` / `.dmg` и `SuprematistClock-Widget-*-mac.zip` / `.dmg`
- **Linux:** `.deb` и `.AppImage` (на **Ubuntu 24.04+ / 26** рекомендуется **`.deb`** — он автоматически ставит AppArmor-профиль с `userns` в `/etc/apparmor.d/`):

```bash
sudo apt install ./SuprematistClock-2.0.0-linux.deb ./SuprematistClock-Widget-2.0.0-linux.deb
SuprematistClock
SuprematistClock-Widget
```

### 2. Запустить из исходников через npm (Windows / macOS / Linux)

Нужны [Node.js](https://nodejs.org/) (LTS) и npm:

```bash
git clone https://github.com/yunoarasaka/suprematist-clock-2.git
cd suprematist-clock-2
npm install
npm start          # окно приложения
npm run widget     # виджет на рабочий стол (--widget)
```

### 3. Linux-native GTK-виджет (Ubuntu / GNOME)

Лёгкий нативный вариант для Linux на **GTK 3 + WebKit2** с полной поддержкой 32-битной RGBA-прозрачности и слоя `keep_below`:

```bash
sudo apt install -y python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1
chmod +x widget.sh widget.py run.sh install.sh
./widget.sh
```

Установка ярлыков («Супрематистские часы» и «Супрематистские часы (виджет)») и скруглённых иконок в меню приложений без `sudo`:

```bash
./install.sh
# удаление: ./uninstall.sh
```

### 4. Открыть в браузере

Сразу онлайн на [GitHub Pages](https://yunoarasaka.github.io/suprematist-clock-2/) или локально:

```bash
python3 -m http.server 8765
# откройте http://127.0.0.1:8765/
```

---

## English (short)

**Suprematist Clock 2.0** — cross-platform analog clock & transparent desktop widget inspired by Kazimir Malevich's Suprematism.

- **Web Demo (GitHub Pages):** https://yunoarasaka.github.io/suprematist-clock-2/
- **Downloads (Win / macOS / Linux):** [Releases](https://github.com/yunoarasaka/suprematist-clock-2/releases) (`SuprematistClock-2.x` app vs `SuprematistClock-Widget-2.x` desktop widget)
- **What's new in 2.0:**
  - **3 Malevich Palettes** (`T`): *Dark Supremus*, *Museum Canvas (Light)*, *Red Wedge*;
  - **3 Second-Hand Modes** (`S` or double-click hub): *0–30s Flight*, *60s Eternal Drift*, *Center Orbit*;
  - **4 Background Modes & True 32-bit RGBA Transparency** (`B`): *Full Canvas*, *Minimal*, *Transparent + Planes*, *Transparent Dial Only*;
  - **Live Digital Time & Date Caption** (`D` or click caption);
  - **Edge/Corner Drag Resize & `Ctrl + Scroll` Zoom**, right-click context menu, system tray, click-through mode, window opacity (`100% / 85% / 70% / 50%`), and persistent window bounds.

---

## Сборка релизов локально и в CI

```bash
npm install
# приложение → dist/
npm run dist:linux
npm run dist:win
npm run dist:mac
# виджет → dist-widget/
npm run dist:linux:widget
npm run dist:win:widget
npm run dist:mac:widget
```

GitHub Actions (`.github/workflows/release.yml`) автоматически собирает и публикует в GitHub Releases пакеты под Linux, Windows и macOS при пуше тега `v*` или в ветку `main`:

```bash
git tag v2.0.0
git push origin v2.0.0
```

---

## Структура проекта

```text
suprematist-clock-2/
  index.html                      # веб-ядро + HUD быстрых настроек
  css/clock.css                   # палитры Малевича, анимации и прозрачные режимы
  js/clock.js                     # непрерывная кинематика стрелок и API настроек
  icons/                          # SVG, генератор render_pngs.py, PNG (48..512) и .icns
  electron/main.js                # Electron: прозрачное окно, контекстное меню, трей
  electron/main-widget.js         # точка входа для пакетной сборки виджета
  electron-builder.widget.yml     # конфиг сборки виджета
  widget.py / widget.sh           # Linux-native виджет на GTK 3 + WebKit2
  run.sh / install.sh             # запуск и установка ярлыков в меню Ubuntu
  .github/workflows/              # CI/CD релизы для Linux, Windows и macOS
  LICENSE                         # MIT
```

## Лицензия

MIT — см. [LICENSE](LICENSE).
