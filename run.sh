#!/bin/sh
# Docker runs the program; the host opens the resulting HTML document.
set -u
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || exit 2
cd "$project_dir" || exit 2
mkdir -p reports || exit 3
report_name="weather-report-$(date -u +%Y%m%dT%H%M%SZ)-$$.html"
report_path="$project_dir/reports/$report_name"
LOCAL_UID="$(id -u)" LOCAL_GID="$(id -g)" docker compose run --rm --build -T weather --report "/reports/$report_name" --no-open "$@"
weather_status=$?
if { [ "$weather_status" -eq 0 ] || [ "$weather_status" -eq 1 ]; } && [ -f "$report_path" ]; then
    printf '\nHTML-отчёт сохранён: %s\n' "$report_path"
    if [ "${WEATHER_NO_OPEN:-0}" != "1" ]; then
        if [ "$(uname -s)" = "Darwin" ]; then
            open "$report_path" || printf 'Откройте HTML-файл вручную.\n' >&2
        elif command -v xdg-open >/dev/null 2>&1; then
            xdg-open "$report_path" >/dev/null 2>&1 &
        else
            printf 'Браузер не найден. Откройте HTML-файл вручную.\n' >&2
        fi
    fi
fi
exit "$weather_status"
