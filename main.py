"""Current weather for unique cities and summary statistics by country."""

import argparse
import json
import math
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class WeatherData:
    city: str
    temperature_c: int
    country: str


@dataclass(frozen=True)
class CountryStatistics:
    country: str
    city_count: int
    average_c: float
    minimum_c: int
    maximum_c: int


class WeatherError(Exception):
    """An HTTP, network or response format error from the weather service."""


def load_cities(path: Path) -> list[str]:
    """Read UTF-8 lines and remove blanks and case-insensitive duplicates."""
    cities: list[str] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        city = line.strip()
        key = city.casefold()
        if city and key not in seen:
            seen.add(key)
            cities.append(city)
    if not cities:
        raise ValueError("Файл не содержит городов.")
    return cities


def parse_weather(city: str, payload: object) -> WeatherData:
    """Read the current temperature, not the forecast or feels-like value."""
    try:
        temperature = payload["current_condition"][0]["temp_C"]
        country = payload["nearest_area"][0]["country"][0]["value"]
        if not isinstance(temperature, str) or not isinstance(country, str):
            raise ValueError("Некорректный тип поля в JSON.")
        temperature_c = int(temperature)
        country = country.strip()
        if not country:
            raise ValueError("Страна не указана.")
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise WeatherError(f"Некорректный ответ API: {error}") from error
    # Keep the requested name: nearest_area can be a nearby weather station.
    return WeatherData(city=city, temperature_c=temperature_c, country=country)


def fetch_weather(city: str, timeout: float = 20, attempts: int = 3) -> WeatherData:
    """Query wttr.in; retry only temporary HTTP and network failures."""
    if attempts < 1 or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("Тайм-аут и количество попыток должны быть положительными.")
    url = f"https://wttr.in/{quote(city, safe='')}?format=j1"
    request = Request(url, headers={
        "User-Agent": "weather-by-country/1.0",
        "Accept": "application/json",
    })
    for attempt in range(attempts):
        try:
            with urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8-sig"))
            return parse_weather(city, payload)
        except HTTPError as error:
            retryable = error.code in (408, 429) or 500 <= error.code < 600
            message = f"HTTP {error.code}: {error.reason}"
            error.close()
            if not retryable:
                raise WeatherError(message) from error
        except (URLError, TimeoutError, OSError) as error:
            message = f"Ошибка сети: {error}"
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise WeatherError("API вернул некорректный JSON.") from error
        if attempt + 1 == attempts:
            raise WeatherError(message)
        time.sleep(2 ** attempt)
    raise AssertionError("Unreachable")


def country_statistics(weather: list[WeatherData]) -> list[CountryStatistics]:
    grouped: dict[str, list[int]] = defaultdict(list)
    for item in weather:
        grouped[item.country].append(item.temperature_c)
    return [
        CountryStatistics(
            country=country,
            city_count=len(temperatures),
            average_c=sum(temperatures) / len(temperatures),
            minimum_c=min(temperatures),
            maximum_c=max(temperatures),
        )
        for country, temperatures in sorted(grouped.items())
    ]


def format_temperature(value: float) -> str:
    # Keep two decimals for fractional averages; integers have no decimal tail.
    rounded = round(value, 2)
    if rounded == 0:
        return "0 °C"
    sign = "+" if rounded > 0 else "-"
    number = f"{abs(rounded):.2f}".rstrip("0").rstrip(".")
    return f"{sign}{number} °C"


def positive_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("Укажите положительное конечное число.")
    return number


def positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("Укажите положительное целое число.")
    return number


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Текущая погода в городах и статистика по странам."
    )
    parser.add_argument(
        "file", nargs="?", type=Path,
        default=Path(__file__).with_name("cities.txt"),
        help="UTF-8 файл: один город на строку (по умолчанию cities.txt).",
    )
    parser.add_argument("--timeout", type=positive_float, default=20,
                        help="Тайм-аут одного запроса в секундах (20).")
    parser.add_argument("--attempts", type=positive_int, default=3,
                        help="Максимум попыток при временной ошибке (3).")
    args = parser.parse_args(argv)
    try:
        cities = load_cities(args.file)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Не удалось загрузить города: {error}", file=sys.stderr)
        return 2

    print(f"Уникальных городов: {len(cities)}", file=sys.stderr, flush=True)
    weather: list[WeatherData] = []
    failed: list[str] = []
    print("Погода по городам:", flush=True)
    for city in cities:
        try:
            item = fetch_weather(city, args.timeout, args.attempts)
        except WeatherError as error:
            failed.append(city)
            print(f"{city}: {error}", file=sys.stderr, flush=True)
            continue
        weather.append(item)
        print(f"{item.city}, {item.country} {format_temperature(item.temperature_c)}",
              flush=True)

    if weather:
        print("\nСтатистика по странам:")
        for item in country_statistics(weather):
            print(
                f"{item.country} — {item.city_count} cities, "
                f"avg: {format_temperature(item.average_c)}, "
                f"min: {format_temperature(item.minimum_c)}, "
                f"max: {format_temperature(item.maximum_c)}"
            )
    if failed:
        print(
            f"Получены данные для {len(weather)} из {len(cities)} городов. "
            f"Статистика учитывает только успешно обработанные города. "
            f"Не обработаны: {', '.join(failed)}.", file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nВыполнение прервано.", file=sys.stderr)
        raise SystemExit(130)
