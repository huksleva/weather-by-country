from pathlib import Path
import json
import io
import contextlib
import unittest
import tempfile
from unittest.mock import Mock, patch

from docker_launcher import run_docker


class DockerLauncherTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.project = Path(self.directory.name)
        (self.project / "compose.yaml").write_text("services: {}", encoding="utf-8")

    def launch(self, logs, *, status=0, open_browser=True, browser_result=True):
        process = Mock(stdout=io.StringIO(logs))
        process.wait.return_value = status
        configuration = Mock(stdout=json.dumps({"services": {"weather": {
            "ports": [{"target": 8000, "published": "8123"}]
        }}}))
        with patch("docker_launcher.subprocess.run", return_value=configuration), \
                patch("docker_launcher.subprocess.Popen", return_value=process) as launch, \
                patch("docker_launcher.webbrowser.open", return_value=browser_result) as browser, \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()) as errors:
            result = run_docker(self.project, open_browser)
        return result, launch, browser, errors.getvalue()

    def test_opens_host_port_once_only_after_report_is_ready(self):
        logs = "weather-1 | Calculating\nweather-1 | Отчёт готов.\n" * 2
        result, launch, browser, _ = self.launch(logs)
        self.assertEqual(result, 0)
        browser.assert_called_once_with("http://localhost:8123/", new=2)
        self.assertIn("--force-recreate", launch.call_args.args[0])

    def test_failed_start_does_not_open_browser(self):
        result, _, browser, _ = self.launch("Cannot start Docker\n", status=1)
        self.assertEqual(result, 1)
        browser.assert_not_called()

    def test_does_not_follow_urls_in_weather_output(self):
        result, _, browser, _ = self.launch("weather-1 | Отчёт готов: https://example.org/\n")
        self.assertEqual(result, 0)
        browser.assert_not_called()

    def test_no_open_preserves_docker_run(self):
        result, _, browser, _ = self.launch("weather-1 | Отчёт готов.\n",
                                           open_browser=False)
        self.assertEqual(result, 0)
        browser.assert_not_called()

    def test_browser_failure_keeps_report_available(self):
        result, _, browser, errors = self.launch("weather-1 | Отчёт готов.\n",
                                                browser_result=False)
        self.assertEqual(result, 0)
        browser.assert_called_once()
        self.assertIn("http://localhost:8123/", errors)

    def test_missing_compose_does_not_start_docker(self):
        with patch("docker_launcher.subprocess.run") as command, \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(run_docker(Path(__file__).with_name("missing-project")), 2)
        command.assert_not_called()

    def test_interrupt_stops_weather_and_preserves_volume(self):
        process = Mock(stdout=io.StringIO("weather-1 | Starting\n"))
        process.wait.side_effect = [KeyboardInterrupt, 0]
        process.poll.return_value = None
        configuration = Mock(stdout=json.dumps({"services": {"weather": {
            "ports": [{"target": 8000, "published": "8000"}]
        }}}))
        with patch("docker_launcher.subprocess.run", return_value=configuration) as command, \
                patch("docker_launcher.subprocess.Popen", return_value=process), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run_docker(self.project), 130)
        process.terminate.assert_called_once()
        self.assertEqual(command.call_args.args[0][-2:], ["stop", "weather"])

    def test_interrupt_still_stops_service_if_compose_has_already_exited(self):
        process = Mock(stdout=io.StringIO("weather-1 | Starting\n"))
        process.wait.side_effect = [KeyboardInterrupt, 0]
        process.terminate.side_effect = ProcessLookupError("process already exited")
        process.poll.return_value = 0
        configuration = Mock(stdout=json.dumps({"services": {"weather": {
            "ports": [{"target": 8000, "published": "8000"}]
        }}}))
        with patch("docker_launcher.subprocess.run", return_value=configuration) as command, \
                patch("docker_launcher.subprocess.Popen", return_value=process), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run_docker(self.project), 130)
        self.assertEqual(command.call_args.args[0][-2:], ["stop", "weather"])
