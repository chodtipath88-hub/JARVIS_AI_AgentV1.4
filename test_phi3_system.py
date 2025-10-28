# test_phi3_system.py - ทดสอบระบบ JARVIS Phi-3
"""
สคริปต์สำหรับทดสอบระบบ Local AI Agent กับ Phi-3 mini
รวมถึงการทดสอบ internet connectivity และ database logging
"""

import sys
import time
from datetime import datetime
import json

def test_ollama_connection():
    """ทดสอบการเชื่อมต่อ Ollama"""
    print("🔍 Testing Ollama connection...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama connected. Found {len(models)} models:")
            for model in models[:3]:  # แสดง 3 โมเดลแรก
                print(f"   - {model['name']}")
            return True
        else:
            print(f"❌ Ollama responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return False

def test_ai_agent():
    """ทดสอบ AI Agent"""
    print("\n🤖 Testing AI Agent...")
    try:
        from ai_agent import LocalAIAgent
        agent = LocalAIAgent()
        
        # ทดสอบคำถามง่าย ๆ
        test_query = "สวัสดี ทดสอบ Phi-3"
        print(f"📝 Testing query: {test_query}")
        
        start_time = time.time()
        result = agent.process_request(test_query)
        end_time = time.time()
        
        print(f"✅ AI Response: {result['ai_response'][:100]}...")
        print(f"⏱️ Response time: {end_time - start_time:.2f}s")
        print(f"🔧 Model used: {result.get('model_used', 'Unknown')}")
        
        return True
    except Exception as e:
        print(f"❌ AI Agent test failed: {e}")
        return False

def test_internet_features():
    """ทดสอบฟีเจอร์อินเทอร์เน็ต"""
    print("\n🌐 Testing Internet Features...")
    try:
        from ai_agent import LocalAIAgent
        agent = LocalAIAgent()
        
        test_cases = [
            ("reddit AI", "reddit"),
            ("สภาพอากาศ กรุงเทพ", "weather"),
            ("ค้นหาข้อมูล Python", "general")
        ]
        
        for query, expected_platform in test_cases:
            print(f"🔍 Testing: {query}")
            
            result = agent.process_request(query)
            
            if result.get('internet_data'):
                platform = result.get('platform_detected', 'Unknown')
                print(f"   ✅ Platform detected: {platform}")
                if 'error' not in str(result['internet_data']):
                    print(f"   ✅ Data retrieved successfully")
                else:
                    print(f"   ⚠️ Data retrieval had issues")
            else:
                print(f"   ℹ️ No internet data triggered")
        
        return True
    except Exception as e:
        print(f"❌ Internet features test failed: {e}")
        return False

def test_database_logging():
    """ทดสอบการบันทึกฐานข้อมูล"""
    print("\n💾 Testing Database Logging...")
    try:
        from ai_agent import LocalAIAgent
        import sqlite3
        
        agent = LocalAIAgent()
        
        # ทดสอบการบันทึก
        test_query = f"ทดสอบการบันทึก {datetime.now().strftime('%H:%M:%S')}"
        result = agent.process_request(test_query)
        
        # ตรวจสอบว่าบันทึกใน database หรือไม่
        cursor = agent.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM agent_logs")
        log_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM model_performance")
        performance_count = cursor.fetchone()[0]
        
        print(f"✅ Total log entries: {log_count}")
        print(f"✅ Model performance records: {performance_count}")
        
        # แสดงสถิติ
        stats = agent.get_statistics()
        print(f"📊 Overall success rate: {stats['overall']['success_rate']}%")
        print(f"📊 Average response time: {stats['overall']['avg_response_time']}s")
        
        return True
    except Exception as e:
        print(f"❌ Database logging test failed: {e}")
        return False

def test_gui_components():
    """ทดสอบส่วนประกอบ GUI (ไม่แสดงหน้าต่าง)"""
    print("\n🖥️ Testing GUI Components...")
    try:
        import tkinter as tk
        from agent_gui import AIAgentGUI
        
        # สร้าง root window (ไม่แสดง)
        root = tk.Tk()
        root.withdraw()  # ซ่อนหน้าต่าง
        
        # ทดสอบการสร้าง GUI
        app = AIAgentGUI(root)
        
        # ทดสอบฟังก์ชันพื้นฐาน
        app.load_initial_stats()
        app.update_platform_status()
        
        print("✅ GUI components loaded successfully")
        
        root.destroy()
        return True
    except Exception as e:
        print(f"❌ GUI components test failed: {e}")
        return False

def run_comprehensive_test():
    """รันการทดสอบครบถ้วน"""
    print("🧪 JARVIS PHI-3 SYSTEM COMPREHENSIVE TEST")
    print("=" * 50)
    
    tests = [
        ("Ollama Connection", test_ollama_connection),
        ("AI Agent Core", test_ai_agent),
        ("Internet Features", test_internet_features),
        ("Database Logging", test_database_logging),
        ("GUI Components", test_gui_components)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"💥 {test_name} crashed: {e}")
            results[test_name] = False
    
    # สรุปผลการทดสอบ
    print(f"\n{'='*60}")
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} | {status}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! JARVIS system is ready!")
        print("\n💡 Next steps:")
        print("   1. Run: python Local_AI_Agent_main.py")
        print("   2. Enjoy your enhanced AI assistant!")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure Ollama is running: ollama serve")
        print("   2. Install required models: ollama pull phi3:mini")
        print("   3. Check internet connection")
        print("   4. Install dependencies: pip install -r requirements.txt")

if __name__ == "__main__":
    run_comprehensive_test()