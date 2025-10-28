@echo off
chcp 65001 >nul
setlocal enableextensions enabledelayedexpansion

cd /d %~dp0

echo ======================================
echo     Starting JARVIS Desktop (PyQt5)
echo ======================================

if not defined OLLAMA_HOST set "OLLAMA_HOST=http://localhost:11434"
if not defined OLLAMA_TIMEOUT set "OLLAMA_TIMEOUT=120"
if not defined OLLAMA_RETRIES set "OLLAMA_RETRIES=2"

echo ⚙️  OLLAMA_HOST  = %OLLAMA_HOST%

REM Quick check for PyQt5
python -c "import PyQt5" 2>nul
if errorlevel 1 (
	echo ⚠️  PyQt5 ยังไม่ได้ติดตั้ง กำลังแนะนำการติดตั้ง...
	echo 👉 รัน: pip install -r requirements.txt
	pause
	goto :eof
)

python desktop_app_pyqt5.py
if errorlevel 1 (
	echo ❌ แอปล้ม โปรดตรวจสอบข้อความข้างต้น
	pause
)
endlocal
