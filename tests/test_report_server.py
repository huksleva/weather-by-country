"""Exercise the report server over loopback without external network access."""
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

from report import create_report_server


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


if __name__ == "__main__":
    unittest.main()
