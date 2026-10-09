<div align="center">

<h1>Weather by Country</h1>
<p>Текущая погода в городах. Статистика по странам. Интерактивный HTML-отчёт.</p>

<p>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&amp;logoColor=white" alt="Запуск через Docker Compose"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&amp;logoColor=white" alt="Python 3.10 или новее"></a>
  <a href="https://github.com/huksleva/weather-by-country/actions/workflows/tests.yml"><img src="https://img.shields.io/github/actions/workflow/status/huksleva/weather-by-country/tests.yml?branch=main&amp;label=tests&amp;logo=githubactions&amp;logoColor=white" alt="Статус автоматических тестов"></a>
  <img src="https://img.shields.io/badge/HTML5-E34F26?logo=html5&amp;logoColor=white" alt="HTML5">
  <img src="https://img.shields.io/badge/CSS-663399?logo=css&amp;logoColor=white" alt="CSS">
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&amp;logoColor=black" alt="JavaScript">
  <img src="https://img.shields.io/badge/dependencies-stdlib%20only-64748B" alt="Только стандартная библиотека">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-22A06B" alt="Лицензия MIT"></a>
</p>

<p>
  <a href="#быстрый-старт">Запуск</a> ·
  <a href="#html-отчёт">HTML-отчёт</a> ·
  <a href="#демонстрация">Демонстрация</a> ·
  <a href="#параметры-python">Параметры</a> ·
  <a href="#проверка">Проверка</a> ·
  <a href="CONTRIBUTING.md">Contributing</a> ·
  <a href="SECURITY.md">Security</a>
</p>

</div>

Программа получает текущую погоду через [wttr.in](https://github.com/chubin/wttr.in#json-output),
рассчитывает статистику по странам и открывает HTML-отчёт в браузере.

## Быстрый старт

**Выберите один способ: Docker или вручную через Python.**
Скопируйте весь блок кнопкой в его правом верхнем углу и вставьте в терминал.
В каждом блоке есть все команды: скачать проект, перейти в папку и запустить.
Для первого запуска нужны [Git](https://git-scm.com/downloads) и интернет;
откройте терминал в папке, где хотите сохранить проект.

Проект уже скачан? Используйте [команды повторного запуска](#повторный-запуск).

### 1. Через Docker

**Нужен запущенный Docker.** На Windows 11 и macOS —
[Docker Desktop](https://www.docker.com/products/docker-desktop/);
на Linux — Docker Engine с плагином Compose. На Windows выберите Linux containers.
Python на компьютере не требуется.

**Windows 11 — CMD или PowerShell:**

```powershell
git clone https://github.com/huksleva/weather-by-country.git
cd weather-by-country
.\run.cmd
```

**Linux или macOS — терминал:**

```sh
git clone https://github.com/huksleva/weather-by-country.git
cd weather-by-country
sh run.sh
```

Скрипт сам собирает и запускает контейнер. После расчётов отчёт открывается
в браузере и сохраняется в `reports/`. Первый запуск может занять несколько минут:
Docker скачивает образ Python. Каждый запуск создаёт отдельный HTML-файл.

### 2. Вручную через Python

**Нужен установленный Python 3.10 или новее.** Дополнительные пакеты
устанавливать не нужно: используются только модули стандартной библиотеки.

**Windows 11 — CMD или PowerShell:**

```powershell
git clone https://github.com/huksleva/weather-by-country.git
cd weather-by-country
python main.py
```

**Linux или macOS — терминал:**

```sh
git clone https://github.com/huksleva/weather-by-country.git
cd weather-by-country
python3 main.py
```

Отчёт открывается в браузере и сохраняется в `reports/weather-report.html`.
Следующий запуск через Python перезапишет этот файл.

### Повторный запуск

Если проект уже скачан, откройте терминал **в папке `weather-by-country`**
и скопируйте нужную команду. Повторно клонировать репозиторий не нужно.

<details>
<summary><strong>Показать команды для уже скачанного проекта</strong></summary>

**Docker — Windows 11:**

```powershell
.\run.cmd
```

**Docker — Linux / macOS:**

```sh
sh run.sh
```

**Вручную через Python — Windows 11:**

```powershell
python main.py
```

**Вручную через Python — Linux / macOS:**

```sh
python3 main.py
```

</details>

В комплекте уже есть `cities.txt` с восемью городами задания.
Чтобы изменить список, отредактируйте этот файл и запустите программу снова.
Если браузер не открылся, откройте HTML из папки `reports/` вручную.

## HTML-отчёт

![HTML-отчёт: общие показатели, диапазоны температур по странам и карточки восьми городов](docs/assets/report.png)

Настоящий отчёт после запуска через Docker **9 октября 2026 года**.
Данные получены от API; при следующем запуске значения могут измениться.

По завершении расчётов программа сохраняет самостоятельный HTML-файл:

- Количество обработанных городов, число стран, средняя температура и общий диапазон.
- Карточки стран: среднее, минимум, максимум и количество городов. Все графики используют одну шкалу.
- Поиск по городу или стране, фильтр по стране, сортировка по температуре и названию.
- Адаптивное оформление для компьютера и телефона, кнопка **Печать / PDF**.
- При ошибках API — статус неполных данных и список пропущенных городов с причинами.

Файл работает офлайн: стили, графики и JavaScript встроены, внешние шрифты
и сервисы не подключаются. Отчёт отражает данные на момент запуска и сам не обновляет погоду.
Фильтры меняют список карточек; общие показатели и статистика стран сохраняют полный результат запуска.
При печати используется выбранный список городов; формат PDF выбирается в диалоге браузера.

## Демонстрация

![Записанный вывод программы: погода для восьми городов и статистика по трём странам](docs/assets/demo.gif)

Реальный вывод `python main.py`, записанный **7 октября 2026 года** и оформленный
как терминальная демонстрация. GIF воспроизводит вывод с сокращёнными паузами.
При новом запуске значения будут зависеть от ответа API.

[Статический снимок](docs/assets/demo.png) · [Текстовая версия вывода](docs/assets/demo.txt)

## Параметры Python

Все команды в этом разделе выполняются из папки проекта.
На Linux/macOS используйте `python3` вместо `python`; на Windows также можно
использовать `py`, если Python установлен с этим средством запуска.

```console
python main.py [file] [--timeout SECONDS] [--attempts COUNT] [--report PATH] [--no-open] [--no-report]
```

| Параметр | Назначение | По умолчанию |
| --- | --- | --- |
| `file` | Путь к файлу городов в UTF-8 | `cities.txt` рядом с `main.py` |
| `--timeout` | Тайм-аут одного запроса, секунды | `20` |
| `--attempts` | Максимум попыток при временной ошибке | `3` |
| `--report` | Путь для HTML-отчёта | `reports/weather-report.html` |
| `--no-open` | Сохранить HTML без открытия браузера | Открывать при прямом запуске Python |
| `--no-report` | Только консольный вывод, без HTML | HTML включён |
| `-h`, `--help` | Справка по команде | — |

Например, для своего списка:

```console
python main.py my-cities.txt --timeout 15 --attempts 2
```

Чтобы сохранить отдельный HTML без автоматического открытия:

```console
python main.py --report reports/today.html --no-open
```

Переменные `WEATHER_REPORT_PATH` и `WEATHER_NO_OPEN=1` задают путь и отключают
открытие по умолчанию. В контейнере уже настроены `/reports/weather-report.html`
и `WEATHER_NO_OPEN=1`; браузер открывает скрипт на компьютере.
При своём пути в Compose используйте каталог `/reports`, подключённый к компьютеру.

### Файл городов

Один город на строку. Поддерживаются UTF-8 и UTF-8 BOM.

```text
Moscow
Vienna
NhaTrang
Moscow
```

Пробелы по краям и пустые строки игнорируются. Повторы сравниваются без учёта
регистра: `Moscow` и `moscow` дадут один запрос. Сохраняются первое написание
и порядок городов. Пробелы и кириллица в названиях кодируются для URL.

### Вывод

Для каждого города программа выводит название, страну и текущую температуру
в градусах Цельсия. Затем для каждой страны рассчитывает:

| Показатель | Расчёт |
| --- | --- |
| `cities` | Количество успешно обработанных уникальных городов |
| `avg` | Сумма текущих температур / количество городов |
| `min` / `max` | Минимальная / максимальная текущая температура |

Среднее округляется только при выводе, до двух знаков после десятичной точки.
Страны выводятся по алфавиту. Минимум и максимум относятся к текущим температурам
городов, а не к дневному прогнозу.

Результаты идут в `stdout`, диагностика и ошибки — в `stderr`.
Чтобы сохранить отчёт отдельно от сообщений об ошибках:

```console
python main.py --no-report > weather.txt 2> errors.txt
```

Для запуска через Compose:

```console
docker compose run --rm -T weather --no-report > weather.txt 2> errors.txt
```

`-T` отключает псевдотерминал для сохранения потоков. Compose также может
добавлять собственные диагностические сообщения в `stderr`.

### Ошибки и повторные попытки

Сетевые ошибки, HTTP `408`, `429` и `5xx` вызывают повторные попытки.
При стандартных трёх попытках паузы составляют 1 и 2 секунды.
Другие HTTP-ошибки и некорректный JSON выводятся сразу.

Если один город недоступен, обработка остальных продолжается. В конце программа
перечисляет пропущенные города и предупреждает, что статистика учитывает только
успешно полученные данные. Отсутствующая температура не заменяется нулём.

| Код завершения | Значение |
| --- | --- |
| `0` | Данные получены для всех городов |
| `1` | Есть ошибки API; результат неполный или пустой |
| `2` | Ошибка входного файла или аргументов |
| `3` | Не удалось записать HTML; консольные результаты уже выведены |
| `130` | Выполнение прервано пользователем |

## Дополнительная настройка Docker

<details>
<summary><strong>Требования, параметры, свой файл городов и прямой запуск Compose</strong></summary>

### Установка Docker

| Система | Требования |
| --- | --- |
| Windows 11 | [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) с WSL 2 и режимом Linux containers |
| macOS, Intel или Apple Silicon | [Docker Desktop](https://docs.docker.com/desktop/setup/install/mac-install/) для своей архитектуры |
| Linux, AMD64 или ARM64 | [Docker Engine](https://docs.docker.com/engine/install/) и [плагин Compose](https://docs.docker.com/compose/install/linux/), либо Docker Desktop |

Запускается Linux-контейнер для архитектуры компьютера: AMD64 или ARM64.
Публиковать порты и запускать фоновый сервис не требуется.
На Linux автоматическое открытие HTML требует графического сеанса и `xdg-open`;
на macOS используется `open`. На сервере файл можно открыть вручную на другом компьютере.

### Параметры запуска

Команды выполняются из папки проекта. Например, тайм-аут 15 секунд и две попытки:

**Windows 11:**

```powershell
.\run.cmd --timeout 15 --attempts 2
```

**Linux / macOS:**

```sh
sh run.sh --timeout 15 --attempts 2
```

Переменная `WEATHER_NO_OPEN=1`, заданная на компьютере, отключает открытие браузера.
Флаг `--no-report` включает только консольный вывод.
Скрипты выбирают путь HTML автоматически; собственный `--report` задавайте
при прямом запуске Python или Compose.

### Другой файл городов

`cities.txt` подключается к контейнеру только для чтения. Чтобы использовать
другой файл, создайте `.env` рядом с `compose.yaml`
(образец — [.env.example](.env.example)):

```dotenv
CITIES_FILE="./data/my cities.txt"
```

Файл должен существовать и быть доступен на чтение. Путь отсчитывается
от `compose.yaml`; внутри контейнера файл доступен как `/app/cities.txt`.
После сохранения `.env` используйте обычную команду запуска.

### Compose без скриптов

Этот вариант сохраняет HTML, но не открывает браузер автоматически.
Команды выполняются из папки проекта.

**Windows 11:**

```powershell
docker compose run --rm --build weather
```

**Linux / macOS:**

```sh
mkdir -p reports
LOCAL_UID=$(id -u) LOCAL_GID=$(id -g) docker compose run --rm --build weather
```

HTML появится в `reports/weather-report.html`. Следующий прямой запуск
перезапишет этот файл. `run.sh` сам создаёт папку и передаёт UID/GID;
запускайте его от пользователя с доступом к Docker.

### Docker без Compose

Со встроенным списком городов, только консольный вывод:

```console
docker build --tag weather-by-country .
docker run --rm weather-by-country --no-report
```

Для сохранения HTML на компьютере используйте Compose или скрипты запуска.

</details>

## Как это работает

```text
Файл городов → удаление повторов → wttr.in → WeatherData → группировка по странам
```

| Поле `WeatherData` | Источник |
| --- | --- |
| `city: str` | Название из входного файла |
| `temperature_c: int` | `current_condition[0].temp_C` |
| `country: str` | `nearest_area[0].country[0].value` |

Запрос: `https://wttr.in/{City}?format=j1`. HTTP выполняется через
`urllib.request`, JSON разбирается модулем `json`, модели описаны через `dataclasses`.
Сторонние библиотеки не используются ни в программе, ни в тестах.

### Ограничения и данные

API определяет местоположение по названию. Одноимённые города могут разрешаться
неоднозначно, а `nearest_area` может указывать ближайшую станцию. Поэтому в выводе
сохраняется запрошенное название города; страна берётся из ответа сервиса.

Запросы выполняются последовательно, данные не кэшируются. Доступность
и актуальность погоды зависят от wttr.in. Скрипт передаёт сервису название города;
как при любом прямом HTTPS-запросе, сервис также видит IP-адрес клиента.
В программе нет собственной телеметрии. HTML сохраняется локально в указанную папку;
автоматической загрузки отчётов в облако нет. Папка `reports/` исключена из Git.

## Проверка

```console
python -m unittest discover -s tests -v
```

Тесты выполняются без интернета: ответы API подменяются через `unittest.mock`.
Проверяются загрузка и удаление повторов, схема JSON, кодирование URL,
повторные запросы, расчёты с отрицательными температурами и частичные ошибки.
Также проверяются HTML-экранирование, пустой отчёт, сохранение файла, открытие браузера
после записи и ошибки файловой системы.

[GitHub Actions](https://github.com/huksleva/weather-by-country/actions/workflows/tests.yml)
запускает тесты и проверяет `--help` при каждом push в `main` и в pull request:

| Платформа | Версии Python |
| --- | --- |
| Ubuntu | 3.10, 3.13 |
| Windows | 3.10, 3.13 |
| macOS | 3.10, 3.13 |

Дополнительно CI собирает и проверяет Docker-образы на **AMD64 и ARM64**:
офлайн-тесты, справку CLI, запуск без root, подключение своего файла с пробелами
и Unicode, передачу кода ошибки через Compose и сохранение HTML на компьютере.
Docker Desktop на macOS в CI не запускается: переносимость Linux-контейнера
проверяется на двух архитектурах, а Python-код отдельно тестируется на macOS.

Локальная проверка тех же тестов внутри контейнера:

```console
docker build --target test --tag weather-by-country:test .
docker run --rm --network none --read-only --tmpfs /tmp weather-by-country:test
```

## Структура проекта

```text
weather-by-country/
├── main.py                    # CLI, запросы, модели и статистика
├── report.py                  # Расчёт показателей отчёта и запись HTML
├── report_template.html        # Автономное оформление, поиск и фильтры
├── run.cmd / run.sh            # Docker и открытие отчёта на компьютере
├── reports/                    # Создаваемые отчёты, исключены из Git
├── cities.txt                 # Исходный список городов
├── Dockerfile                 # Образы для запуска и тестов
├── compose.yaml               # Единая команда запуска и подключение входного файла
├── .dockerignore              # В сборку попадают только необходимые исходники
├── .env.example               # Образец выбора входного файла
├── tests/                     # Тесты CLI и HTML без обращения к API
├── docs/assets/               # GIF, статический снимок и текст демонстрации
├── .github/workflows/tests.yml # Автоматические проверки
├── CONTRIBUTING.md            # Как предложить изменение
├── SECURITY.md                # Как сообщить об уязвимости
└── LICENSE                    # MIT
```

## Если Docker не запускается

- **Нет команды `docker compose`:** установите плагин Compose или Docker Desktop.
- **Cannot connect to the Docker daemon:** запустите Docker Desktop либо Docker Engine.
- **На Windows выбран режим Windows containers:** переключитесь на Linux containers.
- **Входной файл не найден или недоступен:** проверьте `CITIES_FILE`, существование
  файла и права чтения; в контейнере он доступен как `/app/cities.txt`.
- **API недоступен:** проверьте интернет, настройки прокси и диагностику `stderr`.
  Правила обработки неполных результатов одинаковы для Docker и прямого запуска.
- **Не удалось записать HTML:** проверьте права на `reports/` и свободное место.
  На Linux используйте `sh run.sh`, чтобы контейнер писал от имени вашего пользователя.
- **Браузер не открылся:** откройте созданный HTML из `reports/` вручную.
  Прямой запуск Compose только сохраняет файл; автоматически открывают его `run.cmd` и `run.sh`.

## Участие и поддержка

Для обычных ошибок и предложений используйте
[Issues](https://github.com/huksleva/weather-by-country/issues).
Порядок подготовки изменений описан в [CONTRIBUTING.md](CONTRIBUTING.md).
Об уязвимостях сообщайте приватно по инструкции в [SECURITY.md](SECURITY.md).

## Лицензия и источники

Код распространяется по [MIT License](LICENSE).

Исходный список городов: [gistpad](https://gistpad.com/raw/vk-task-14)
и [Облако Mail](https://cloud.mail.ru/public/LWcw/kpMqFgztw).
Формат погодных данных: [документация wttr.in](https://github.com/chubin/wttr.in#json-output).
