# start_web_jarvis.py - สคริปต์เริ่มต้นระบบ Web JARVIS
"""
สคริปต์สำหรับเริ่มต้นระบบ JARVIS Web Interface
รวมการตรวจสอบ dependencies, Ollama, และเริ่ม web server
"""

import subprocess
import sys
import time
import os
import sqlite3
from datetime import datetime

def check_python_packages():
    """ตรวจสอบและติดตั้ง Python packages ที่จำเป็น"""
    required_packages = [
        'flask', 'flask-cors', 'flask-socketio', 
        'requests', 'sqlite3'
    ]
    
    print("🔍 ตรวจสอบ Python packages...")
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            elif package == 'flask':
                import flask
            elif package == 'flask-cors':
                import flask_cors
            elif package == 'flask-socketio':
                import flask_socketio
            elif package == 'requests':
                import requests
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package} - ไม่พบ")
    
    if missing_packages:
        print(f"\n📦 กำลังติดตั้ง packages ที่ขาดหายไป: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ ติดตั้ง packages สำเร็จ!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ ไม่สามารถติดตั้ง packages: {e}")
            return False
    
    return True

def check_ollama_status():
    """ตรวจสอบสถานะ Ollama"""
    print("🔍 ตรวจสอบ Ollama...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"  ✅ Ollama ทำงานปกติ ({len(models)} models)")
            
            # ตรวจสอบ Phi-3
            phi3_models = [m for m in models if 'phi3' in m['name'].lower()]
            if phi3_models:
                print(f"  ✅ พบ Phi-3 models: {[m['name'] for m in phi3_models]}")
            else:
                print("  ⚠️ ไม่พบ Phi-3 models")
                
            return True
        else:
            print(f"  ❌ Ollama ตอบสนองแต่ status ผิด: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Ollama ไม่ตอบสนอง: {e}")
        return False

def suggest_ollama_setup():
    """แนะนำการติดตั้ง Ollama"""
    print("\n🔧 การติดตั้ง Ollama:")
    print("1. ดาวน์โหลดจาก: https://ollama.ai/")
    print("2. ติดตั้งและรันคำสั่ง:")
    print("   ollama serve")
    print("   ollama pull phi3:mini")
    print("3. ตรวจสอบด้วย: ollama list")

def setup_database():
    """ตั้งค่าฐานข้อมูลเริ่มต้น"""
    print("🗄️ ตั้งค่าฐานข้อมูล...")
    try:
        # Import และใช้ WebJARVIS class เพื่อตั้งค่า database
        from web_server import WebJARVIS
        web_jarvis = WebJARVIS()
        print("  ✅ Database ตั้งค่าเรียบร้อย")
        print("  ✅ Admin user พร้อมใช้งาน (admin/admin123)")
        return True
    except Exception as e:
        print(f"  ❌ ตั้งค่า Database ผิดพลาด: {e}")
        return False

def check_ports():
    """ตรวจสอบ port ที่ใช้งาน"""
    print("🌐 ตรวจสอบ ports...")
    
    # ตรวจสอบ port 5000 (Flask)
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        
        if result == 0:
            print("  ⚠️ Port 5000 ถูกใช้งานอยู่")
            return False
        else:
            print("  ✅ Port 5000 ว่าง")
            return True
    except Exception as e:
        print(f"  ❌ ตรวจสอบ port ผิดพลาด: {e}")
        return True  # ถือว่าใช้ได้

def create_launch_script():
    """สร้างสคริปต์สำหรับเริ่มต้นง่าย ๆ"""
    script_content = '''@echo off
echo 🚀 Starting JARVIS Web Interface...
echo.
echo 📍 Opening browser to: http://localhost:5000
echo 👤 Login: admin / admin123
echo.

start http://localhost:5000
python web_server.py

pause
'''
    
    with open('start_jarvis_web.bat', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("📄 สร้าง start_jarvis_web.bat สำเร็จ")

def show_usage_info():
    """แสดงข้อมูลการใช้งาน"""
    print("\n" + "="*60)
    print("🎯 JARVIS WEB INTERFACE - ข้อมูลการใช้งาน")
    print("="*60)
    print("🌐 URL: http://localhost:5000")
    print("👤 Admin Login:")
    print("   Username: admin")
    print("   Password: admin123")
    print()
    print("💾 ข้อมูลที่สร้างขึ้น:")
    print("   📁 jarvis_web.db - ฐานข้อมูลผู้ใช้และประวัติ")
    print("   📁 ai_agent_logs.db - ฐานข้อมูล AI performance")
    print("   📁 agent_activity.log - ไฟล์ log")
    print()
    print("🔧 ฟีเจอร์ที่ใช้ได้:")
    print("   ✅ เข้าสู่ระบบด้วย username/password")
    print("   ✅ สนทนากับ AI ผ่าน web interface")
    print("   ✅ บันทึกประวัติการสนทนาพร้อมวันเวลา")
    print("   ✅ ดึงข้อมูลจากอินเทอร์เน็ต (Reddit, Weather, etc.)")
    print("   ✅ Export ประวัติเป็นไฟล์")
    print("   ✅ Socket.IO real-time messaging")
    print()
    print("🚀 วิธีเริ่มต้น:")
    print("   1. รันไฟล์: start_jarvis_web.bat")
    print("   2. หรือ: python web_server.py")
    print("   3. เปิดเบราว์เซอร์ไปที่ http://localhost:5000")
    print("="*60)

def main():
    """ฟังก์ชันหลัก"""
    print("🎯 JARVIS WEB INTERFACE SETUP")
    print("="*50)
    
    # ตรวจสอบ Python packages
    if not check_python_packages():
        print("❌ ไม่สามารถติดตั้ง packages ที่จำเป็น")
        return False
    
    # ตรวจสอบ Ollama
    if not check_ollama_status():
        print("⚠️ Ollama ไม่พร้อมใช้งาน")
        suggest_ollama_setup()
        
        choice = input("\n❓ ต้องการดำเนินการต่อโดยไม่มี Ollama? (y/n): ")
        if choice.lower() != 'y':
            return False
    
    # ตรวจสอบ ports
    check_ports()
    
    # ตั้งค่าฐานข้อมูล
    if not setup_database():
        print("❌ ไม่สามารถตั้งค่าฐานข้อมูล")
        return False
    
    # สร้างสคริปต์เริ่มต้น
    create_launch_script()
    
    # แสดงข้อมูลการใช้งาน
    show_usage_info()
    
    # ถามว่าจะเริ่มเซิร์ฟเวอร์ทันทีหรือไม่
    choice = input("\n❓ เริ่มเซิร์ฟเวอร์ทันที? (y/n): ")
    if choice.lower() == 'y':
        print("\n🚀 เริ่มต้น JARVIS Web Server...")
        try:
            # Import และรัน web server
            from web_server import socketio, app
            socketio.run(app, debug=False, host='0.0.0.0', port=5000)
        except KeyboardInterrupt:
            print("\n👋 ปิดเซิร์ฟเวอร์แล้ว")
        except Exception as e:
            print(f"\n❌ เซิร์ฟเวอร์ผิดพลาด: {e}")
    else:
        print("\n💡 เริ่มเซิร์ฟเวอร์ด้วยคำสั่ง:")
        print("   python web_server.py")
        print("   หรือ start_jarvis_web.bat")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ การตั้งค่าไม่สำเร็จ")
            input("กด Enter เพื่อออก...")
    except KeyboardInterrupt:
        print("\n👋 ยกเลิกการตั้งค่า")
    except Exception as e:
        print(f"\n💥 เกิดข้อผิดพลาด: {e}")
        input("กด Enter เพื่อออก...")