#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ไฟล์ทดสอบระบบ JARVIS AI
สำหรับตรวจสอบว่าทุกส่วนทำงานได้ปกติหรือไม่
"""

import requests
import json
import sqlite3
import os
import sys
import time
from datetime import datetime

def test_ollama_connection():
    """ทดสอบการเชื่อมต่อ Ollama"""
    print("🔍 กำลังทดสอบ Ollama API...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            print(f"✅ Ollama ทำงานปกติ - พบ models: {models}")
            return True
        else:
            print(f"❌ Ollama API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ไม่สามารถเชื่อมต่อ Ollama: {e}")
        return False

def test_web_server():
    """ทดสอบการเชื่อมต่อ Web Server"""
    print("🔍 กำลังทดสอบ Web Server...")
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Web Server ทำงานปกติ")
            return True
        else:
            print(f"❌ Web Server error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ไม่สามารถเชื่อมต่อ Web Server: {e}")
        return False

def test_chat_api():
    """ทดสอบ Chat API พร้อม Login"""
    print("🔍 กำลังทดสอบ Chat API...")
    try:
        # ขั้นตอนที่ 1: Login
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        login_response = requests.post(
            "http://localhost:5000/login",
            json=login_data,
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        login_result = login_response.json()
        if not login_result.get('success'):
            print(f"❌ Login failed: {login_result.get('message')}")
            return False
        
        session_id = login_result.get('session_id')
        print(f"✅ Login สำเร็จ - Session ID: {session_id[:10]}...")
        
        # ขั้นตอนที่ 2: ส่งข้อความ Chat
        chat_data = {
            "message": "สวัสดีครับ ทดสอบระบบ",
            "session_id": session_id
        }
        chat_response = requests.post(
            "http://localhost:5000/api/chat",
            json=chat_data,
            timeout=30
        )
        
        if chat_response.status_code == 200:
            result = chat_response.json()
            print(f"✅ Chat API ทำงานปกติ")
            print(f"   Response: {result.get('response', 'No response')[:100]}...")
            return True
        else:
            print(f"❌ Chat API error: {chat_response.status_code}")
            print(f"   Error details: {chat_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat API error: {e}")
        return False

def test_database():
    """ทดสอบ Database"""
    print("🔍 กำลังทดสอบ Database...")
    try:
        # ทดสอบ Web Database
        if os.path.exists('jarvis_web.db'):
            conn = sqlite3.connect('jarvis_web.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"✅ Web Database ทำงานปกติ - พบตาราง: {[t[0] for t in tables]}")
            conn.close()
        else:
            print("⚠️  Web Database ไม่พบ (จะสร้างใหม่เมื่อเริ่มระบบ)")
        
        # ทดสอบ AI Agent Database
        if os.path.exists('ai_agent.db'):
            conn = sqlite3.connect('ai_agent.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"✅ AI Agent Database ทำงานปกติ - พบตาราง: {[t[0] for t in tables]}")
            conn.close()
        else:
            print("⚠️  AI Agent Database ไม่พบ (จะสร้างใหม่เมื่อเริ่มระบบ)")
        
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_ai_agent_direct():
    """ทดสอบ AI Agent โดยตรง"""
    print("🔍 กำลังทดสอบ AI Agent โดยตรง...")
    try:
        # Import AI Agent
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from ai_agent import LocalAIAgent
        
        agent = LocalAIAgent()
        response = agent.process_message("สวัสดีครับ ทดสอบระบบ", "test_user")
        
        if response and len(response) > 0:
            print(f"✅ AI Agent ทำงานปกติ")
            print(f"   Response: {response[:100]}...")
            return True
        else:
            print("❌ AI Agent ไม่ตอบสนอง")
            return False
    except Exception as e:
        print(f"❌ AI Agent error: {e}")
        return False

def test_internet_connectivity():
    """ทดสอบการเชื่อมต่ออินเทอร์เน็ต"""
    print("🔍 กำลังทดสอบการเชื่อมต่ออินเทอร์เน็ต...")
    
    # ทดสอบ Reddit API
    try:
        response = requests.get("https://www.reddit.com/r/python.json", timeout=10)
        if response.status_code == 200:
            print("✅ Reddit API ทำงานปกติ")
        else:
            print("⚠️  Reddit API ไม่สามารถเข้าถึงได้")
    except Exception as e:
        print(f"⚠️  Reddit API error: {e}")
    
    # ทดสอบ Weather API
    try:
        response = requests.get("https://wttr.in/Bangkok?format=j1", timeout=10)
        if response.status_code == 200:
            print("✅ Weather API ทำงานปกติ")
        else:
            print("⚠️  Weather API ไม่สามารถเข้าถึงได้")
    except Exception as e:
        print(f"⚠️  Weather API error: {e}")

def run_full_test():
    """เรียกใช้การทดสอบทั้งหมด"""
    print("=" * 60)
    print("🚀 เริ่มการทดสอบระบบ JARVIS AI")
    print("=" * 60)
    print(f"📅 เวลา: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Ollama Connection", test_ollama_connection),
        ("Web Server", test_web_server),
        ("Database", test_database),
        ("Chat API", test_chat_api),
        ("AI Agent Direct", test_ai_agent_direct),
        ("Internet Connectivity", test_internet_connectivity)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 ทดสอบ: {test_name}")
        print("-" * 40)
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการทดสอบ {test_name}: {e}")
            results[test_name] = False
        time.sleep(1)
    
    # สรุปผลการทดสอบ
    print("\n" + "=" * 60)
    print("📊 สรุปผลการทดสอบ")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ ผ่าน" if result else "❌ ไม่ผ่าน"
        print(f"{test_name:<25} : {status}")
    
    print(f"\n🎯 ผลรวม: {passed}/{total} การทดสอบผ่าน")
    
    if passed == total:
        print("🎉 ระบบทำงานได้ปกติทั้งหมด! สามารถใช้งานได้แล้ว")
        print("🌐 เปิด Browser ไปที่: http://localhost:5000")
        print("🔑 Login: admin / admin123")
    else:
        print("⚠️  พบปัญหาบางส่วน กรุณาตรวจสอบ:")
        for test_name, result in results.items():
            if not result:
                print(f"   - {test_name}")
        print("\n📖 ดูคู่มือแก้ไขปัญหาใน TROUBLESHOOTING_GUIDE.md")

if __name__ == "__main__":
    try:
        run_full_test()
    except KeyboardInterrupt:
        print("\n\n⏹️  การทดสอบถูกยกเลิก")
    except Exception as e:
        print(f"\n❌ ข้อผิดพลาดในการทดสอบ: {e}")
        import traceback
        traceback.print_exc()