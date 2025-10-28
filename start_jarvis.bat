@echo off
chcp 65001 >nul
title JARVIS AI System Launcher

echo.
echo ================================
echo    🚀 JARVIS AI System Launcher
echo ================================
echo.

REM ตรวจสอบ Ollama
echo 🔍 ตรวจสอบ Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama ไม่ทำงาน กำลังเริ่ม Ollama...
    start /min ollama serve
    echo ⏳ รอ Ollama เริ่มทำงาน...
    timeout /t 10 /nobreak >nul
) else (
    echo ✅ Ollama ทำงานปกติ
)

REM ตรวจสอบ Web Server
echo 🔍 ตรวจสอบ Web Server...
curl -s http://localhost:5000 >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Web Server ไม่ทำงาน กำลังเริ่ม Web Server...
    start /min python web_server.py
    echo ⏳ รอ Web Server เริ่มทำงาน...
    timeout /t 5 /nobreak >nul
) else (
    echo ✅ Web Server ทำงานปกติ
)

echo.
echo ✅ ระบบพร้อมใช้งาน!
echo.
echo 🌐 เปิด Browser ไปที่: http://localhost:5000
echo 🔑 ข้อมูล Login:
echo    Username: admin
echo    Password: admin123
echo.
echo 📖 คู่มือใช้งาน: WEB_INTERFACE_GUIDE.md
echo 🔧 แก้ไขปัญหา: TROUBLESHOOTING_GUIDE.md
echo.

choice /c YN /m "ต้องการเปิด Browser หรือไม่? (Y/N)"
if %errorlevel%==1 (
    start http://localhost:5000
)

echo.
echo กดปุ่มใดก็ได้เพื่อปิดหน้าต่าง...
pause >nul