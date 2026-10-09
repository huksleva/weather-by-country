<div align="center">

<h1>Weather by Country</h1>
<p>Текущая погода в городах. Понятная статистика по странам.</p>

<p>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&amp;logoColor=white" alt="Запуск через Docker Compose"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&amp;logoColor=white" alt="Python 3.10 или новее"></a>
  <a href="https://github.com/huksleva/weather-by-country/actions/workflows/tests.yml"><img src="https://img.shields.io/github/actions/workflow/status/huksleva/weather-by-country/tests.yml?branch=main&amp;label=tests&amp;logo=githubactions&amp;logoColor=white" alt="Статус автоматических тестов"></a>
  <img src="https://img.shields.io/badge/dependencies-stdlib%20only-64748B" alt="Только стандартная библиотека">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-22A06B" alt="Лицензия MIT"></a>
</p>

<p>
  <a href="#демонстрация">Демонстрация</a> ·
  <a href="#быстрый-старт">Быстрый старт</a> ·
  <a href="#использование">Использование</a> ·
  <a href="#проверка">Проверка</a> ·
  <a href="CONTRIBUTING.md">Contributing</a> ·
  <a href="SECURITY.md">Security</a>
</p>

</div>

Консольная программа на Python: читает список городов из файла, запрашивает
текущую температуру через [wttr.in](https://github.com/chubin/wttr.in#json-output)
и группирует результаты по странам. Проект создан как решение тестового задания;
все температуры и итоговые показатели получаются и вычисляются во время запуска.

- **Три платформы:** Windows 11, Linux и macOS; единая команда Docker Compose.
- **Без установки пакетов:** только стандартная библиотека, без API-ключа.
- **Один город — один результат:** пустые строки и повторы удаляются до запросов.
- **Статистика по странам:** количество городов, среднее, минимум и максимум.
- **Обработка сбоев:** тайм-ауты, повторные попытки и явное предупреждение о неполных данных.

## Демонстрация

![Записанный вывод программы: погода для восьми городов и статистика по трём странам](docs/assets/demo.gif)

Реальный вывод `python main.py`, записанный **7 октября 2026 года** и оформленный
как терминальная демонстрация. GIF воспроизводит вывод с сокращёнными паузами.
При новом запуске значения будут зависеть от ответа API.

[Статический снимок](docs/assets/demo.png) · [Текстовая версия вывода](docs/assets/demo.txt)

## Быстрый старт

### Через Docker — одинаково на трёх платформах

Установите и запустите Docker. Python на компьютере для этого варианта не нужен.

| Система | Требования |
| --- | --- |
| Windows 11 | [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) с WSL 2 и режимом Linux containers |
| macOS, Intel или Apple Silicon | [Docker Desktop](https://docs.docker.com/desktop/setup/install/mac-install/) для своей архитектуры |
| Linux, AMD64 или ARM64 | [Docker Engine](https://docs.docker.com/engine/install/) и [плагин Compose](https://docs.docker.com/compose/install/linux/), либо Docker Desktop |

Команды одинаковы в PowerShell на Windows и в терминале Linux/macOS:

```console
git clone https://github.com/huksleva/weather-by-country.git
cd weather-by-country
docker compose run --rm --build weather
```

Первый запуск скачивает официальный образ Python 3.13 и собирает контейнер.
Программа выводит отчёт и завершается; `--rm` удаляет завершённый контейнер.
Публиковать порты или запускать фоновый сервис не требуется.
Для сборки и получения погоды нужен интернет.

На всех трёх системах выполняется один и тот же Linux-контейнер. Архитектура
выбирается при локальной сборке: `linux/amd64` для Intel/AMD или `linux/arm64`
для ARM, включая Apple Silicon. Эмуляция ARM на Mac для обычного запуска не нужна.

`cities.txt` подключается с компьютера в режиме только для чтения, поэтому его
можно редактировать без изменения программы. Параметры CLI передаются после
имени сервиса:

```console
docker compose run --rm weather --timeout 15 --attempts 2
docker compose run --rm weather --help
```

Для другого входного файла создайте `.env` рядом с `compose.yaml`
(образец — [.env.example](.env.example)):

```dotenv
CITIES_FILE="./data/my cities.txt"
```

Путь может быть относительным к `compose.yaml`; файл должен существовать
и быть доступен на чтение. Он подключается в `/app/cities.txt`. После сохранения
`.env` используйте ту же команду запуска. Отсутствующий файл не будет автоматически
создан как каталог.

Если Compose недоступен, контейнер со встроенным списком городов запускается так:

```console
docker build --tag weather-by-country .
docker run --rm weather-by-country
```

### Через Python

Нужны **Python 3.10+** и доступ к интернету. В папке клонированного проекта:

```console
python main.py
```

На Windows можно использовать `py main.py`, на Linux/macOS — `python3 main.py`,
если команда `python` недоступна. Скрипт читает `cities.txt` рядом с собой.
В комплекте — все восемь городов исходного задания.
Устанавливать пакеты или настраивать учётную запись не требуется.

## Использование

```console
python main.py [file] [--timeout SECONDS] [--attempts COUNT]
```

| Параметр | Назначение | По умолчанию |
| --- | --- | --- |
| `file` | Путь к файлу городов в UTF-8 | `cities.txt` рядом с `main.py` |
| `--timeout` | Тайм-аут одного запроса, секунды | `20` |
| `--attempts` | Максимум попыток при временной ошибке | `3` |
| `-h`, `--help` | Справка по команде | — |

Например, для своего списка:

```console
python main.py my-cities.txt --timeout 15 --attempts 2
```

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
python main.py > weather.txt 2> errors.txt
```

Для запуска через Compose:

```console
docker compose run --rm -T weather > weather.txt 2> errors.txt
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
| `130` | Выполнение прервано пользователем |

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
В программе нет собственной телеметрии или автоматического сохранения отчётов.

## Проверка

```console
python -m unittest discover -s tests -v
```

Тесты выполняются без интернета: ответы API подменяются через `unittest.mock`.
Проверяются загрузка и удаление повторов, схема JSON, кодирование URL,
повторные запросы, расчёты с отрицательными температурами и частичные ошибки.

[GitHub Actions](https://github.com/huksleva/weather-by-country/actions/workflows/tests.yml)
запускает тесты и проверяет `--help` при каждом push в `main` и в pull request:

| Платформа | Версии Python |
| --- | --- |
| Ubuntu | 3.10, 3.13 |
| Windows | 3.10, 3.13 |
| macOS | 3.10, 3.13 |

Дополнительно CI собирает и проверяет Docker-образы на **AMD64 и ARM64**:
офлайн-тесты, справку CLI, запуск без root, подключение своего файла с пробелами
и Unicode, а также передачу кода ошибки через Compose.
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
├── cities.txt                 # Исходный список городов
├── Dockerfile                 # Образы для запуска и тестов
├── compose.yaml               # Единая команда запуска и подключение входного файла
├── .dockerignore              # В сборку попадают только необходимые исходники
├── .env.example               # Образец выбора входного файла
├── tests/test_main.py          # Тесты без обращения к API
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
