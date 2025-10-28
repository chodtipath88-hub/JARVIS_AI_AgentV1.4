@echo off
echo 🚀 Starting JARVIS Web Interface...
echo.
echo 📍 Opening browser to: http://localhost:5000
echo 👤 Login: admin / admin123
echo.

start http://localhost:5000
python web_server.py

pause
