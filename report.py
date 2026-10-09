"""Create a self-contained HTML weather report using the standard library."""

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import re
import tempfile
from typing import TYPE_CHECKING, Mapping, Sequence

if TYPE_CHECKING:
    if __package__:
        from .main import CountryStatistics, WeatherData
    else:
        from main import CountryStatistics, WeatherData


def format_temperature(value: float) -> str:
    rounded = round(value, 2)
    if rounded == 0:
        return "0 °C"
    sign = "+" if rounded > 0 else "-"
    number = f"{abs(rounded):.2f}".rstrip("0").rstrip(".")
    return f"{sign}{number} °C"


def _city_count(count: int) -> str:
    if 11 <= count % 100 <= 14:
        word = "городов"
    elif count % 10 == 1:
        word = "город"
    elif 2 <= count % 10 <= 4:
        word = "города"
    else:
        word = "городов"
    return f"{count} {word}"


def render_report(
    weather: Sequence["WeatherData"],
    statistics: Sequence["CountryStatistics"],
    failed: Mapping[str, str],
    requested_count: int,
    generated_at: datetime | None = None,
) -> str:
    now = generated_at or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    temperatures = [item.temperature_c for item in weather]
    complete = not failed
    status = "Все данные получены" if complete else "Получены не все данные"
    status_class = "success" if complete else "warning"
    if not weather:
        status, status_class = "Погодные данные недоступны", "error"
    average = format_temperature(sum(temperatures) / len(temperatures)) if temperatures else "—"
    low = min(temperatures) if temperatures else 0
    high = max(temperatures) if temperatures else 0
    span = max(high - low, 6)
    axis_min, axis_max = low - span * 0.15, high + span * 0.15
    if axis_min == axis_max:
        axis_min, axis_max = low - 3, high + 3

    def position(value: float) -> str:
        return f"{12 + (value - axis_min) / (axis_max - axis_min) * 256:.2f}"

    country_cards = []
    for item in statistics:
        country = escape(item.country)
        minimum, maximum = format_temperature(item.minimum_c), format_temperature(item.maximum_c)
        mean = format_temperature(item.average_c)
        x1, x2, xm = position(item.minimum_c), position(item.maximum_c), position(item.average_c)
        country_cards.append(f'''<article class="country-card">
          <div class="country-heading"><h3>{country}</h3><span class="count-badge">{_city_count(item.city_count)}</span></div>
          <div class="country-average">{mean}<span>средняя температура</span></div>
          <svg class="range-chart" viewBox="0 0 280 32" role="img" aria-label="{escape(f'{item.country}: минимум {minimum}, среднее {mean}, максимум {maximum}')}">
            <line x1="12" y1="16" x2="268" y2="16" stroke="#e6ebf1" stroke-width="6" stroke-linecap="round"/>
            <line x1="{x1}" y1="16" x2="{x2}" y2="16" stroke="#8db2f2" stroke-width="6" stroke-linecap="round"/>
            <circle cx="{x1}" cy="16" r="4" fill="#5686d5"/><circle cx="{x2}" cy="16" r="4" fill="#5686d5"/>
            <circle cx="{xm}" cy="16" r="7" fill="#244877" stroke="white" stroke-width="2"/>
          </svg>
          <div class="range-labels"><span>Минимум <strong>{minimum}</strong></span><span>Максимум <strong>{maximum}</strong></span></div>
        </article>''')

    city_cards = []
    for index, item in enumerate(weather, 1):
        tone = "cold" if item.temperature_c < 0 else "warm"
        temperature = format_temperature(item.temperature_c).removesuffix(" °C")
        city_cards.append(f'''<article class="city-card" data-city="{escape(item.city)}" data-country="{escape(item.country)}" data-temperature="{item.temperature_c}" data-index="{index}">
          <div class="city-meta"><span>{escape(item.country)}</span><span class="city-number">{index:02}</span></div>
          <h3 title="{escape(item.city)}">{escape(item.city)}</h3>
          <p class="city-temperature {tone}">{temperature}<span>°C</span></p>
          <span class="city-caption">Текущая температура</span>
        </article>''')

    error_block = ""
    if failed:
        entries = "".join(f"<li><strong>{escape(city)}</strong><span>{escape(message)}</span></li>" for city, message in failed.items())
        error_block = f'''<section class="error-panel" aria-labelledby="errors-title"><h2 id="errors-title">Не удалось получить данные</h2>
          <p>Эти города не включены в статистику. Отсутствующие значения не заменяются нулём.</p><ul>{entries}</ul></section>'''
    empty = '<div class="empty-state">Нет полученных данных. Причины ошибок приведены ниже.</div>'
    options = "".join(f'<option value="{escape(item.country)}">{escape(item.country)}</option>' for item in statistics)
    values = {
        "STATUS_CLASS": status_class,
        "STATUS": escape(status),
        "TIMESTAMP": now.isoformat(timespec="seconds"),
        "DATE": now.astimezone(timezone.utc).strftime("%d.%m.%Y · %H:%M UTC"),
        "CITY_COUNT": str(len(weather)),
        "REQUESTED_COUNT": str(requested_count),
        "COUNTRY_COUNT": str(len(statistics)),
        "AVERAGE": average,
        "MINIMUM": format_temperature(low) if temperatures else "—",
        "MAXIMUM": format_temperature(high) if temperatures else "—",
        "COUNTRIES": "".join(country_cards) or empty,
        "CITY_CARDS": "".join(city_cards) or empty,
        "COUNTRY_OPTIONS": options,
        "ERRORS": error_block,
    }
    template = Path(__file__).with_name("report_template.html").read_text(encoding="utf-8")
    # Substitute once; input text resembling a placeholder must remain literal.
    return re.sub(r"\{\{([A-Z_]+)\}\}", lambda match: values[match.group(1)], template)


def write_report(
    path: Path,
    weather: Sequence["WeatherData"],
    statistics: Sequence["CountryStatistics"],
    failed: Mapping[str, str],
    requested_count: int,
) -> Path:
    document = render_report(weather, statistics, failed, requested_count)
    destination = path.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=destination.parent,
                                         prefix=".weather-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(document)
        temporary.replace(destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return destination
