@echo off
chcp 65001 >nul
title JARVIS Mini Server Launcher (V1.2)

cd /d %~dp0

echo.
echo ======================================
echo      JARVIS Mini Server Launcher
echo ======================================
echo.

REM Configuration (can be overridden by existing environment)
if not defined OLLAMA_HOST set "OLLAMA_HOST=http://localhost:11434"
if not defined OLLAMA_MODEL set "OLLAMA_MODEL=phi3:mini"
if not defined OLLAMA_TIMEOUT set "OLLAMA_TIMEOUT=120"
if not defined OLLAMA_RETRIES set "OLLAMA_RETRIES=2"

echo ⚙️  OLLAMA_HOST    = %OLLAMA_HOST%
echo ⚙️  OLLAMA_MODEL   = %OLLAMA_MODEL%
echo ⚙️  OLLAMA_TIMEOUT = %OLLAMA_TIMEOUT%
echo ⚙️  OLLAMA_RETRIES = %OLLAMA_RETRIES%

REM Start Mini Server (single instance)
echo 🚀 Starting JARVIS Mini Server on http://127.0.0.1:5001
start "JARVIS Mini Server" cmd /c "set OLLAMA_HOST=%OLLAMA_HOST%& set OLLAMA_MODEL=%OLLAMA_MODEL%& set OLLAMA_TIMEOUT=%OLLAMA_TIMEOUT%& set OLLAMA_RETRIES=%OLLAMA_RETRIES%& python mini_server.py"

REM Wait for server health before opening browser (up to ~15s)
echo ⏳ Waiting for server to become healthy...
powershell -NoProfile -Command "for ($i=0; $i -lt 15; $i++) { try { $res = Invoke-WebRequest -Uri http://127.0.0.1:5001/health -TimeoutSec 2; if ($res.StatusCode -eq 200) { exit 0 } } catch {} Start-Sleep -Seconds 1 }; exit 1"
if errorlevel 1 (
  echo ⚠️  Server health not confirmed yet. You can still try opening the browser.
)

echo 🌐 Opening browser...
start http://127.0.0.1:5001

echo ✅ Done.
