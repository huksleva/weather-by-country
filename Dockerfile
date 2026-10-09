FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

LABEL org.opencontainers.image.title="Weather by Country" \
      org.opencontainers.image.description="Current weather and country-level statistics" \
      org.opencontainers.image.source="https://github.com/huksleva/weather-by-country" \
      org.opencontainers.image.licenses="MIT"

WORKDIR /app
COPY main.py cities.txt ./
USER 10001:10001

FROM base AS test
COPY tests/ ./tests/
ENTRYPOINT ["python", "-m", "unittest", "discover", "-s", "tests", "-v"]

FROM base AS runtime
ENTRYPOINT ["python", "/app/main.py"]
