"""Exercise the report server over loopback without external network access."""
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
import contextlib
import io
from urllib.error import HTTPError
from urllib.request import urlopen

from report import create_report_server, serve_report


class ReportServerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.report = self.root / "weather-report.html"
        self.document = "<!doctype html><html lang='ru'>Москва</html>".encode("utf-8")
        self.report.write_bytes(self.document)
        (self.root / "private.txt").write_text("private", encoding="utf-8")
        self.server = create_report_server(self.report, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def test_report_and_download_have_exact_utf8_content(self):
        for route in ("/", "/weather-report.html", "/download"):
            with self.subTest(route=route), urlopen(self.url + route, timeout=3) as response:
                self.assertEqual(response.read(), self.document)
                self.assertEqual(response.headers.get_content_charset(), "utf-8")
                self.assertEqual(response.headers["Cache-Control"], "no-store")
                if route == "/download":
                    self.assertIn("attachment", response.headers["Content-Disposition"])

    def test_private_files_and_traversal_are_not_served(self):
        for route in ("/private.txt", "/../private.txt", "/%2e%2e/private.txt", "/.git/config"):
            with self.subTest(route=route), self.assertRaises(HTTPError) as error:
                urlopen(self.url + route, timeout=3)
            self.assertEqual(error.exception.code, 404)

    def test_missing_report_returns_404(self):
        self.report.unlink()
        with self.assertRaises(HTTPError) as error:
            urlopen(self.url + "/", timeout=3)
        self.assertEqual(error.exception.code, 404)


class BrowserOpeningTests(unittest.TestCase):
    def test_browser_opens_after_server_is_bound(self):
        server = create_report_server(Path("unused.html"), port=0)
        url = f"http://localhost:{server.server_port}/"
        events = []
        with patch("report.create_report_server", return_value=server), \
                patch("report.webbrowser.open", side_effect=lambda *args, **kwargs: events.append("open") or True) as browser, \
                patch.object(server, "serve_forever", side_effect=lambda: events.append("serve")), \
                contextlib.redirect_stdout(io.StringIO()):
            serve_report(Path("unused.html"), open_browser=True)
        browser.assert_called_once_with(url, new=2)
        self.assertEqual(events, ["open", "serve"])

    def test_browser_failure_does_not_stop_server(self):
        server = create_report_server(Path("unused.html"), port=0)
        with patch("report.create_report_server", return_value=server), \
                patch("report.webbrowser.open", side_effect=OSError("no GUI")), \
                patch.object(server, "serve_forever") as serve, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            serve_report(Path("unused.html"), open_browser=True)
        serve.assert_called_once()
        self.assertIn("Не удалось открыть браузер", output.getvalue())


if __name__ == "__main__":
    unittest.main()
