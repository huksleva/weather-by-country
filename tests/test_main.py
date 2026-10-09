import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import main


def payload(temperature="18", country="Japan"):
    return {
        "current_condition": [{"temp_C": temperature, "FeelsLikeC": "99"}],
        "nearest_area": [{
            "areaName": [{"value": "Nearby station"}],
            "country": [{"value": country}],
        }],
    }


class WeatherTests(unittest.TestCase):
    def make_file(self, text):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "cities.txt"
        path.write_text(text, encoding="utf-8")
        return path

    def test_cities_bom_blanks_and_duplicates(self):
        path = self.make_file("\ufeff Moscow \r\n\r\nTokyo\r\nmoscow\n東京\nTokyo\n")
        self.assertEqual(main.load_cities(path), ["Moscow", "Tokyo", "東京"])

    def test_empty_input_is_rejected(self):
        with self.assertRaises(ValueError):
            main.load_cities(self.make_file("\n  \n"))

    def test_parse_current_temperature_and_requested_city(self):
        self.assertEqual(main.parse_weather("Tokyo", payload("-3")),
                         main.WeatherData("Tokyo", -3, "Japan"))

    def test_bad_schema_is_rejected(self):
        for data in ({}, None, {"current_condition": []}, payload("warm"),
                     payload("18", ""), payload(18)):
            with self.subTest(data=data), self.assertRaises(main.WeatherError):
                main.parse_weather("Tokyo", data)

    def test_url_encoding_and_one_successful_request(self):
        body = io.BytesIO(json.dumps(payload()).encode("utf-8"))
        with patch("main.urlopen", return_value=body) as request:
            result = main.fetch_weather("São Paulo & City", timeout=7)
        self.assertEqual(result.city, "São Paulo & City")
        request.assert_called_once()
        args, kwargs = request.call_args
        self.assertEqual(args[0].full_url,
                         "https://wttr.in/S%C3%A3o%20Paulo%20%26%20City?format=j1")
        self.assertEqual(kwargs["timeout"], 7)

    def test_temporary_http_failure_is_retried(self):
        error = HTTPError("https://wttr.in", 503, "Unavailable", {}, None)
        body = io.BytesIO(json.dumps(payload()).encode("utf-8"))
        with patch("main.urlopen", side_effect=[error, body]) as request, \
                patch("main.time.sleep") as sleep:
            self.assertEqual(main.fetch_weather("Tokyo").temperature_c, 18)
        self.assertEqual(request.call_count, 2)
        sleep.assert_called_once_with(1)

    def test_permanent_http_failure_is_not_retried(self):
        error = HTTPError("https://wttr.in", 404, "Not Found", {}, None)
        with patch("main.urlopen", side_effect=error) as request, \
                patch("main.time.sleep") as sleep:
            with self.assertRaisesRegex(main.WeatherError, "HTTP 404"):
                main.fetch_weather("Tokyo")
        request.assert_called_once()
        sleep.assert_not_called()

    def test_network_retries_are_bounded(self):
        with patch("main.urlopen", side_effect=URLError("offline")) as request, \
                patch("main.time.sleep") as sleep:
            with self.assertRaises(main.WeatherError):
                main.fetch_weather("Tokyo", attempts=3)
        self.assertEqual(request.call_count, 3)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [1, 2])

    def test_bad_json_is_not_retried(self):
        with patch("main.urlopen", return_value=io.BytesIO(b"<html>error</html>")) \
                as request:
            with self.assertRaisesRegex(main.WeatherError, "JSON"):
                main.fetch_weather("Tokyo")
        request.assert_called_once()

    def test_country_statistics_with_negative_and_fractional_average(self):
        weather = [main.WeatherData("A", -5, "Russia"),
                   main.WeatherData("B", 0, "Russia"),
                   main.WeatherData("C", 4, "Russia"),
                   main.WeatherData("D", 18, "Japan")]
        stats = main.country_statistics(weather)
        self.assertEqual([item.country for item in stats], ["Japan", "Russia"])
        self.assertEqual(stats[0], main.CountryStatistics("Japan", 1, 18, 18, 18))
        self.assertEqual(stats[1].city_count, 3)
        self.assertAlmostEqual(stats[1].average_c, -1 / 3)
        self.assertEqual((stats[1].minimum_c, stats[1].maximum_c), (-5, 4))
        self.assertEqual(main.country_statistics([]), [])

    def test_temperature_format(self):
        for value, expected in [(18, "+18 °C"), (-5, "-5 °C"), (0, "0 °C"),
                                (19.5, "+19.5 °C"), (-1 / 3, "-0.33 °C"),
                                (-0.001, "0 °C")]:
            with self.subTest(value=value):
                self.assertEqual(main.format_temperature(value), expected)

    def test_main_deduplicates_before_api_calls(self):
        path = self.make_file("Tokyo\ntokyo\nOsaka\n")
        output, errors = io.StringIO(), io.StringIO()
        with patch("main.fetch_weather", side_effect=[
            main.WeatherData("Tokyo", 18, "Japan"),
            main.WeatherData("Osaka", 21, "Japan"),
        ]) as fetch, contextlib.redirect_stdout(output), \
                contextlib.redirect_stderr(errors):
            status = main.main([str(path), "--no-report"])
        self.assertEqual(status, 0)
        self.assertEqual([call.args[0] for call in fetch.call_args_list],
                         ["Tokyo", "Osaka"])
        self.assertIn("Japan — 2 cities, avg: +19.5 °C, min: +18 °C, max: +21 °C",
                      output.getvalue())

    def test_main_continues_after_city_failure(self):
        path = self.make_file("Tokyo\nMoscow\nOsaka\n")
        output, errors = io.StringIO(), io.StringIO()
        with patch("main.fetch_weather", side_effect=[
            main.WeatherData("Tokyo", 18, "Japan"),
            main.WeatherError("HTTP 503"),
            main.WeatherData("Osaka", 22, "Japan"),
        ]), contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = main.main([str(path), "--no-report"])
        self.assertEqual(status, 1)
        self.assertIn("avg: +20 °C", output.getvalue())
        self.assertIn("Получены данные для 2 из 3", errors.getvalue())
        self.assertIn("Не обработаны: Moscow", errors.getvalue())

    def test_all_city_failures_do_not_produce_statistics(self):
        path = self.make_file("Tokyo\n")
        output, errors = io.StringIO(), io.StringIO()
        with patch("main.fetch_weather", side_effect=main.WeatherError("offline")), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            self.assertEqual(main.main([str(path), "--no-report"]), 1)
        self.assertNotIn("Статистика по странам:", output.getvalue())
        self.assertIn("Получены данные для 0 из 1", errors.getvalue())

    def test_input_error_prevents_api_calls(self):
        path = self.make_file(" \n")
        with patch("main.fetch_weather") as fetch, \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main.main([str(path), "--no-report"]), 2)
        fetch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
