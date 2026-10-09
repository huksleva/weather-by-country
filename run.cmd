@echo off
setlocal
chcp 65001 >nul
pushd "%~dp0" || exit /b 2
if not exist "reports" mkdir "reports"
if not exist "reports" (
  echo Не удалось создать папку reports.
  popd
  exit /b 3
)
:choose_report_name
set "report_name=weather-report-%RANDOM%-%RANDOM%.html"
if exist "reports\%report_name%" goto choose_report_name
docker compose run --rm --build -T weather --report "/reports/%report_name%" --no-open %*
set "weather_status=%ERRORLEVEL%"
if "%weather_status%"=="0" goto open_report
if "%weather_status%"=="1" goto open_report
goto finish
:open_report
if not exist "reports\%report_name%" goto finish
echo HTML-отчёт сохранён: "%CD%\reports\%report_name%"
if "%WEATHER_NO_OPEN%"=="1" goto finish
start "" "%CD%\reports\%report_name%"
:finish
popd
exit /b %weather_status%
