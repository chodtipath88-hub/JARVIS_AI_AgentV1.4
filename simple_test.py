#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple JARVIS Test - ทดสอบระบบแบบง่าย ๆ
"""

import requests
import json
import time
import sys

def test_basic_connection():
    """ทดสอบการเชื่อมต่อพื้นฐาน"""
    print("🔍 ทดสอบการเชื่อมต่อ Web Server...")
    
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print(f"✅ Server ตอบสนอง - Status Code: {response.status_code}")
        print(f"📄 Content Length: {len(response.text)} characters")
        
        # ตรวจสอบว่ามี HTML content หรือไม่
        if "html" in response.text.lower():
            print("✅ Server ส่ง HTML content ปกติ")
            return True
        else:
            print("❌ Server ไม่ส่ง HTML content")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ไม่สามารถเชื่อมต่อ Server ได้")
        return False
    except requests.exceptions.Timeout:
        print("❌ Server ตอบสนองช้าเกินไป")
        return False
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

def test_login_simple():
    """ทดสอบ Login แบบง่าย"""
    print("\n🔍 ทดสอบ Login API...")
    
    try:
        # ข้อมูล Login
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        # ส่ง Login request
        response = requests.post(
            "http://localhost:5000/login",
            json=login_data,
            timeout=10
        )
        
        print(f"📡 Login Response Status: {response.status_code}")
        print(f"📄 Login Response: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('success'):
                    print("✅ Login สำเร็จ!")
                    return result.get('session_id')
                else:
                    print(f"❌ Login ไม่สำเร็จ: {result.get('message')}")
                    return None
            except json.JSONDecodeError:
                print("❌ Server ส่ง response ที่ไม่ใช่ JSON")
                return None
        else:
            print(f"❌ Login failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_chat_simple(session_id):
    """ทดสอบ Chat แบบง่าย"""
    if not session_id:
        print("❌ ไม่มี session_id สำหรับทดสอบ Chat")
        return False
        
    print("\n🔍 ทดสอบ Chat API...")
    
    try:
        # ข้อมูล Chat
        chat_data = {
            "message": "สวัสดีครับ",
            "session_id": session_id
        }
        
        # ส่ง Chat request
        response = requests.post(
            "http://localhost:5000/api/chat",
            json=chat_data,
            timeout=30
        )
        
        print(f"📡 Chat Response Status: {response.status_code}")
        print(f"📄 Chat Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('success'):
                    print("✅ Chat API ทำงานปกติ!")
                    print(f"🤖 AI Response: {result.get('response', 'No response')[:100]}...")
                    return True
                else:
                    print(f"❌ Chat ไม่สำเร็จ: {result.get('message')}")
                    return False
            except json.JSONDecodeError:
                print("❌ Server ส่ง response ที่ไม่ใช่ JSON")
                return False
        else:
            print(f"❌ Chat failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False

def main():
    """ฟังก์ชันหลัก"""
    print("=" * 60)
    print("🧪 JARVIS Simple Test")
    print("=" * 60)
    
    # Test 1: Basic Connection
    if not test_basic_connection():
        print("\n❌ การเชื่อมต่อพื้นฐานล้มเหลว")
        print("💡 แนะนำ: ตรวจสอบว่า web server ทำงานอยู่หรือไม่")
        print("   รัน: python web_server.py")
        return
    
    # Test 2: Login
    session_id = test_login_simple()
    if not session_id:
        print("\n❌ Login ล้มเหลว")
        print("💡 แนะนำ: ตรวจสอบ database และ user accounts")
        return
    
    # Test 3: Chat
    if not test_chat_simple(session_id):
        print("\n❌ Chat ล้มเหลว")
        print("💡 แนะนำ: ตรวจสอบ AI Agent และ Ollama")
        return
    
    print("\n" + "=" * 60)
    print("🎉 ระบบทำงานได้ปกติทั้งหมด!")
    print("🌐 เปิด Browser ไปที่: http://localhost:5000")
    print("🔑 Login: admin / admin123")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  การทดสอบถูกยกเลิก")
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาดในการทดสอบ: {e}")
        import traceback
        traceback.print_exc()