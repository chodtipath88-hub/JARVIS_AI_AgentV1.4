#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Start JARVIS - การเริ่มใช้งาน JARVIS แบบง่าย ๆ
"""

import os
import sys
import time
import webbrowser
import subprocess
import requests
from datetime import datetime

def check_and_start_ollama():
    """ตรวจสอบและเริ่ม Ollama"""
    print("🔍 ตรวจสอบ Ollama...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            print("✅ Ollama ทำงานปกติ")
            return True
    except:
        pass
    
    print("🚀 เริ่ม Ollama...")
    try:
        # เริ่ม Ollama ใน background
        if os.name == 'nt':  # Windows
            subprocess.Popen(['ollama', 'serve'], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
        else:  # Linux/Mac
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        
        # รอให้ Ollama เริ่มทำงาน
        for i in range(15):
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=1)
                if response.status_code == 200:
                    print("✅ Ollama เริ่มทำงานแล้ว")
                    return True
            except:
                pass
            time.sleep(1)
            print(f"⏳ รอ Ollama เริ่มทำงาน... ({i+1}/15)")
        
        print("❌ ไม่สามารถเริ่ม Ollama ได้")
        return False
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเริ่ม Ollama: {e}")
        return False

def check_and_start_web_server():
    """ตรวจสอบและเริ่ม Web Server"""
    print("🔍 ตรวจสอบ Web Server...")
    try:
        response = requests.get("http://localhost:5000", timeout=3)
        if response.status_code == 200:
            print("✅ Web Server ทำงานปกติ")
            return True
    except:
        pass
    
    print("🚀 เริ่ม Web Server...")
    try:
        # เริ่ม Web Server ใน background
        if os.path.exists('web_server.py'):
            if os.name == 'nt':  # Windows
                subprocess.Popen([sys.executable, 'web_server.py'], 
                               creationflags=subprocess.CREATE_NO_WINDOW)
            else:  # Linux/Mac
                subprocess.Popen([sys.executable, 'web_server.py'], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            
            # รอให้ Web Server เริ่มทำงาน
            for i in range(10):
                try:
                    response = requests.get("http://localhost:5000", timeout=1)
                    if response.status_code == 200:
                        print("✅ Web Server เริ่มทำงานแล้ว")
                        return True
                except:
                    pass
                time.sleep(1)
                print(f"⏳ รอ Web Server เริ่มทำงาน... ({i+1}/10)")
            
            print("❌ ไม่สามารถเริ่ม Web Server ได้")
            return False
        else:
            print("❌ ไม่พบไฟล์ web_server.py")
            return False
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเริ่ม Web Server: {e}")
        return False

def test_login():
    """ทดสอบการ Login"""
    print("🔍 ทดสอบการ Login...")
    try:
        data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post("http://localhost:5000/login", json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ ระบบ Login ทำงานปกติ")
                return True
        print("❌ ระบบ Login ไม่ทำงาน")
        return False
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการทดสอบ Login: {e}")
        return False

def main():
    """ฟังก์ชันหลัก"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("=" * 60)
    print("🚀 JARVIS AI - Quick Start")
    print("=" * 60)
    print(f"📅 เวลา: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # ตรวจสอบและเริ่มระบบ
    steps = [
        ("เริ่ม Ollama", check_and_start_ollama),
        ("เริ่ม Web Server", check_and_start_web_server),
        ("ทดสอบ Login", test_login)
    ]
    
    all_success = True
    for step_name, step_func in steps:
        print(f"📋 {step_name}")
        print("-" * 40)
        success = step_func()
        if not success:
            all_success = False
        print()
        time.sleep(1)
    
    # สรุปผล
    print("=" * 60)
    if all_success:
        print("🎉 ระบบพร้อมใช้งาน!")
        print()
        print("🌐 URL: http://localhost:5000")
        print("🔑 Login:")
        print("   Username: admin")
        print("   Password: admin123")
        print()
        
        # ถามว่าจะเปิด Browser หรือไม่
        try:
            answer = input("ต้องการเปิด Browser หรือไม่? (y/n): ").lower().strip()
            if answer in ['y', 'yes', 'ใช่']:
                print("🚀 เปิด Browser...")
                webbrowser.open("http://localhost:5000")
        except:
            pass
    else:
        print("❌ พบปัญหาในการเริ่มระบบ")
        print()
        print("🔧 แนะนำการแก้ไข:")
        print("1. ตรวจสอบว่าติดตั้ง Ollama แล้ว")
        print("2. ตรวจสอบว่าติดตั้ง dependencies: pip install -r requirements.txt")
        print("3. ดูคู่มือแก้ไขปัญหาใน TROUBLESHOOTING_GUIDE.md")
        print("4. รันการทดสอบระบบ: python test_system.py")

if __name__ == "__main__":
    try:
        main()
        print("\nกดปุ่ม Enter เพื่อปิดโปรแกรม...")
        input()
    except KeyboardInterrupt:
        print("\n\n⏹️  โปรแกรมถูกยกเลิก")
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()