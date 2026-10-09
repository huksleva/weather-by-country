import contextlib
from datetime import datetime, timezone
from html.parser import HTMLParser
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import main
import report


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.input = self.root / "cities.txt"
        self.input.write_text("Tokyo\nMoscow\n", encoding="utf-8")
        self.output = self.root / "output with spaces" / "weather.html"
        self.weather = [main.WeatherData("Tokyo", 18, "Japan"),
                        main.WeatherData("Moscow", -2, "Russia")]
        self.stats = main.country_statistics(self.weather)

    def run_main(self, responses, extra=()):
        output, errors = io.StringIO(), io.StringIO()
        with patch("main.fetch_weather", side_effect=responses), \
                patch("main.webbrowser.open", return_value=True) as browser, \
                patch.dict("main.os.environ", {"WEATHER_NO_OPEN": "0"}), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = main.main([str(self.input), "--report", str(self.output), *extra])
        return status, browser, errors.getvalue()

    def test_serve_starts_after_saving_report_without_opening_browser(self):
        def verify(path, **kwargs):
            self.assertTrue(path.is_file())
            self.assertIn("Tokyo", path.read_text(encoding="utf-8"))
            self.assertEqual(kwargs["port"], 8000)
        with patch("main.serve_report", side_effect=verify) as serve:
            status, browser, _ = self.run_main(self.weather, ["--serve"])
        self.assertEqual(status, 0)
        serve.assert_called_once()
        browser.assert_not_called()

    def test_partial_report_is_available_in_serve_mode(self):
        with patch("main.serve_report") as serve:
            status, _, _ = self.run_main([self.weather[0], main.WeatherError("offline")], ["--serve"])
        self.assertEqual(status, 1)
        serve.assert_called_once()

    def test_serve_bind_failure_preserves_saved_report(self):
        with patch("main.serve_report", side_effect=OSError("port busy")):
            status, _, errors = self.run_main(self.weather, ["--serve"])
        self.assertEqual(status, 3)
        self.assertTrue(self.output.is_file())
        self.assertIn("port busy", errors)

    def test_serve_requires_report_and_valid_port(self):
        for arguments in (["--serve", "--no-report"], ["--serve", "--port", "65536"]):
            with self.subTest(arguments=arguments), patch("main.fetch_weather") as fetch, \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                main.main(arguments)
            self.assertEqual(error.exception.code, 2)
            fetch.assert_not_called()

    def test_report_contains_actual_statistics_and_is_utf8(self):
        destination = report.write_report(self.output, self.weather, self.stats, {}, 2)
        self.assertEqual(destination, self.output.resolve())
        text = self.output.read_text(encoding="utf-8")
        self.assertIn('lang="ru"', text)
        self.assertIn('data-city="Tokyo"', text)
        self.assertIn('data-temperature="-2"', text)
        self.assertIn("+8 °C", text)  # Weighted mean of the two current temperatures.
        self.assertIn("Все данные получены", text)
        self.assertNotIn("{{AVERAGE}}", text)
        self.assertEqual(list(self.output.parent.glob(".weather-*.tmp")), [])

    def test_untrusted_names_and_errors_cannot_inject_html(self):
        weather = [main.WeatherData('<script>alert("city")</script>', 4,
                                    'Country" onfocus="alert(1)')]
        text = report.render_report(weather, main.country_statistics(weather),
                                    {"<img src=x>": '<script>alert("error")</script>'}, 2)
        self.assertNotIn('<script>alert("city")</script>', text)
        self.assertNotIn('<script>alert("error")</script>', text)
        self.assertIn("&lt;script&gt;", text)
        self.assertIn('Country&quot; onfocus=&quot;alert(1)', text)
        self.assertNotIn('<img src=x>', text)

    def test_placeholder_like_names_are_preserved(self):
        weather = [main.WeatherData("{{AVERAGE}}", 4, "{{DATE}}")]
        text = report.render_report(weather, main.country_statistics(weather), {}, 1)
        self.assertIn('data-city="{{AVERAGE}}"', text)
        self.assertIn('data-country="{{DATE}}"', text)

    def test_empty_report_has_no_fake_zero_temperatures(self):
        text = report.render_report([], [], {"Tokyo": "offline"}, 1)
        self.assertIn("Погодные данные недоступны", text)
        self.assertNotIn('data-temperature="0"', text)
        self.assertIn('metric-value">—', text)
        self.assertIn("offline", text)
        self.assertNotIn('class="country-card"', text)

    def test_partial_report_marks_missing_city(self):
        text = report.render_report(self.weather[:1], self.stats[:1], {"Moscow": "HTTP 503"}, 2)
        self.assertIn("Получены не все данные", text)
        self.assertIn("Не удалось получить данные", text)
        self.assertIn("HTTP 503", text)

    def test_output_has_no_external_assets(self):
        class Assets(HTMLParser):
            external = []
            def handle_starttag(self, tag, attrs):
                for name, value in attrs:
                    if name in ("src", "href") and value.startswith(("http:", "https:")):
                        self.external.append(value)
        parser = Assets()
        parser.feed(report.render_report(self.weather, self.stats, {}, 2))
        self.assertEqual(parser.external, [])

    def test_timestamp_is_explicit_and_can_be_localized(self):
        text = report.render_report(self.weather, self.stats, {}, 2,
                                    datetime(2026, 10, 9, 12, 30, tzinfo=timezone.utc))
        self.assertIn('datetime="2026-10-09T12:30:00+00:00"', text)
        self.assertIn("09.10.2026 · 12:30 UTC", text)

    def test_main_writes_report_before_opening_browser(self):
        def open_existing_file(uri, new):
            self.assertTrue(self.output.exists())
            self.assertEqual(uri, self.output.resolve().as_uri())
            self.assertEqual(new, 2)
            return True
        with patch("main.fetch_weather", side_effect=self.weather), \
                patch("main.webbrowser.open", side_effect=open_existing_file) as browser, \
                patch.dict("main.os.environ", {"WEATHER_NO_OPEN": "0"}), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main.main([str(self.input), "--report", str(self.output)]), 0)
        browser.assert_called_once()

    def test_no_open_still_creates_report(self):
        status, browser, _ = self.run_main(self.weather, ["--no-open"])
        self.assertEqual(status, 0)
        self.assertTrue(self.output.exists())
        browser.assert_not_called()

    def test_no_report_has_no_files_or_browser(self):
        status, browser, _ = self.run_main(self.weather, ["--no-report"])
        self.assertEqual(status, 0)
        self.assertFalse(self.output.exists())
        browser.assert_not_called()

    def test_partial_api_failure_preserves_status_and_opens_report(self):
        status, browser, _ = self.run_main([self.weather[0], main.WeatherError("offline")])
        self.assertEqual(status, 1)
        self.assertTrue(self.output.exists())
        self.assertIn("offline", self.output.read_text(encoding="utf-8"))
        browser.assert_called_once()

    def test_all_api_failures_create_explanatory_report(self):
        status, _, _ = self.run_main([main.WeatherError("offline"), main.WeatherError("timeout")])
        self.assertEqual(status, 1)
        self.assertIn("Погодные данные недоступны", self.output.read_text(encoding="utf-8"))

    def test_report_write_failure_returns_3_and_does_not_open_old_report(self):
        self.output.parent.mkdir(parents=True)
        self.output.write_text("old report", encoding="utf-8")
        with patch("main.write_report", side_effect=PermissionError("read-only")):
            status, browser, errors = self.run_main(self.weather)
        self.assertEqual(status, 3)
        self.assertIn("Не удалось сохранить HTML-отчёт", errors)
        self.assertEqual(self.output.read_text(encoding="utf-8"), "old report")
        browser.assert_not_called()

    def test_browser_failure_does_not_lose_a_valid_report(self):
        with patch("main.fetch_weather", side_effect=self.weather), \
                patch("main.webbrowser.open", side_effect=OSError("no browser")), \
                patch.dict("main.os.environ", {"WEATHER_NO_OPEN": "0"}), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as errors:
            status = main.main([str(self.input), "--report", str(self.output)])
        self.assertEqual(status, 0)
        self.assertTrue(self.output.exists())
        self.assertIn("Откройте HTML-файл вручную", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
