FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

LABEL org.opencontainers.image.title="Weather by Country" \
      org.opencontainers.image.description="Current weather and country-level statistics" \
      org.opencontainers.image.source="https://github.com/huksleva/weather-by-country" \
      org.opencontainers.image.licenses="MIT"

WORKDIR /app
COPY main.py report.py report_template.html cities.txt ./
RUN mkdir /reports && chown 10001:10001 /reports
USER 10001:10001

FROM base AS test
COPY tests/ ./tests/
ENTRYPOINT ["python", "-m", "unittest", "discover", "-s", "tests", "-v"]

FROM base AS runtime
ENV WEATHER_REPORT_PATH=/reports/weather-report.html \
    WEATHER_NO_OPEN=1
ENTRYPOINT ["python", "/app/main.py"]
