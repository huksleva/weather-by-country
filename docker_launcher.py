"""Launch Compose on the host and open its report in the host browser."""

import json
from pathlib import Path
from queue import Empty, Queue
import subprocess
import sys
from threading import Thread
import webbrowser


def run_docker(project: Path, open_browser: bool = True) -> int:
    if not (project / "compose.yaml").is_file():
        print("Для --docker запустите main.py из скачанного репозитория.", file=sys.stderr)
        return 2
    compose = ["docker", "compose", "--ansi", "never"]
    try:
        configuration = subprocess.run(
            [*compose, "config", "--format", "json"], cwd=project,
            capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
        )
        service = json.loads(configuration.stdout)["services"]["weather"]
        binding = next(port for port in service["ports"] if port["target"] == 8000)
        port = int(binding["published"])
        if not 1 <= port <= 65535:
            raise ValueError("Некорректный порт отчёта.")
        url = f"http://localhost:{port}/"
        process = subprocess.Popen(
            [*compose, "up", "--build", "--force-recreate", "weather"], cwd=project,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            encoding="utf-8", errors="replace", bufsize=1,
        )
    except subprocess.CalledProcessError as error:
        print(error.stderr, file=sys.stderr)
        return error.returncode
    except (OSError, ValueError, KeyError, StopIteration) as error:
        print(f"Не удалось запустить Docker: {error}", file=sys.stderr)
        return 2

    lines: Queue[str | None] = Queue()

    def read_output():
        try:
            for line in process.stdout:
                lines.put(line)
        finally:
            lines.put(None)

    reader = Thread(target=read_output, daemon=True)
    reader.start()
    attempted = False
    try:
        while True:
            try:
                line = lines.get(timeout=0.2)
            except Empty:
                continue
            if line is None:
                break
            print(line, end="", flush=True)
            # Compose prefixes container logs; never open arbitrary URLs from them.
            message = line.split("|", 1)[-1].strip()
            if message == "Отчёт готов: http://localhost:8000/" and not attempted:
                attempted = True
                print(f"Отчёт на компьютере: {url}", flush=True)
                if open_browser:
                    try:
                        opened = webbrowser.open(url, new=2)
                    except (OSError, webbrowser.Error):
                        opened = False
                    if not opened:
                        print(f"Не удалось открыть браузер автоматически. Откройте {url}",
                              file=sys.stderr)
        return process.wait()
    except KeyboardInterrupt:
        # Stop only this project's weather service; keep its report volume.
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        subprocess.run([*compose, "stop", "weather"], cwd=project, check=False)
        return 130
    finally:
        reader.join(timeout=2)
        process.stdout.close()
