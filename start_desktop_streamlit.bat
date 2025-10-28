@echo off
chcp 65001 >nul
setlocal enableextensions enabledelayedexpansion

cd /d %~dp0

echo ======================================
echo   Starting JARVIS Desktop (Streamlit)
echo ======================================

echo.
if not defined OLLAMA_HOST set "OLLAMA_HOST=http://localhost:11434"
if not defined OLLAMA_TIMEOUT set "OLLAMA_TIMEOUT=120"
if not defined OLLAMA_RETRIES set "OLLAMA_RETRIES=2"

echo ⚙️  OLLAMA_HOST  = %OLLAMA_HOST%

start http://localhost:8501
streamlit run desktop_app_streamlit.py
