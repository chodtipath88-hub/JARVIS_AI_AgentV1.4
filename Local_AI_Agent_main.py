import subprocess
import sys
import time

def check_ollama_running():
    """ตรวจสอบว่า Ollama กำลังทำงานอยู่หรือไม่"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except:
        return False

def check_phi3_model():
    """ตรวจสอบว่ามี Phi-3 model หรือไม่"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            available_models = [model['name'] for model in models_data.get('models', [])]
            
            phi3_models = [model for model in available_models if 'phi3' in model.lower()]
            
            if phi3_models:
                print(f"✅ พบ Phi-3 models: {phi3_models}")
                return True
            else:
                print("⚠️ ไม่พบ Phi-3 model กำลังแนะนำการติดตั้ง...")
                print("💡 รันคำสั่ง: ollama pull phi3:mini")
                return False
    except Exception as e:
        print(f"❌ ไม่สามารถตรวจสอบ models: {e}")
        return False

def install_phi3_model():
    """แนะนำการติดตั้ง Phi-3"""
    print("\n🤖 คำแนะนำการติดตั้ง Phi-3 mini:")
    print("1. เปิด Command Prompt หรือ PowerShell")
    print("2. รันคำสั่ง: ollama pull phi3:mini")
    print("3. รอการดาวน์โหลดเสร็จสิ้น")
    print("4. เริ่มใช้งาน JARVIS ได้เลย!")
    
    choice = input("\n❓ ต้องการให้ระบบติดตั้งอัตโนมัติหรือไม่? (y/n): ")
    if choice.lower() == 'y':
        try:
            import subprocess
            print("🔄 กำลังติดตั้ง Phi-3 mini...")
            result = subprocess.run(["ollama", "pull", "phi3:mini"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ ติดตั้ง Phi-3 mini สำเร็จ!")
                return True
            else:
                print(f"❌ ติดตั้งไม่สำเร็จ: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            return False
    return False

def start_ollama():
    """เริ่มต้นการทำงานของ Ollama"""
    print("🔧 กำลังเริ่มต้น Ollama...")
    try:
        # พยายามเริ่มต้น Ollama
        subprocess.Popen(["ollama", "serve"])
        time.sleep(5) # รอให้ Ollama เริ่มทำงาน
        
        if check_ollama_running():
            print("✅ Ollama พร้อมทำงานแล้ว!")
            return True
        else:
            print("❌ ไม่สามารถเริ่มต้น Ollama ได้")
            return False
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")
        return False

def main():
    """ฟังก์ชันหลัก"""
    print("🚀 เริ่มต้น JARVIS Local AI Agent with Phi-3 Support")
    
    # ตรวจสอบว่า Ollama ทำงานอยู่หรือไม่
    if not check_ollama_running():
        print("⚠️ Ollama ไม่ทำงาน กำลังพยายามเริ่มต้น...")
        if not start_ollama():
            print("กรุณาเริ่มต้น Ollama ด้วยตนเองโดยรัน: ollama serve")
            return
    
    # ตรวจสอบ Phi-3 model
    if not check_phi3_model():
        if not install_phi3_model():
            print("⚠️ จะใช้โมเดลอื่นที่มีอยู่แทน")
    
    # เริ่มต้น GUI
    print("🖥️ กำลังเริ่มต้น Enhanced Desktop Interface...")
    try:
        from agent_gui import AIAgentGUI
        import tkinter as tk
        
        root = tk.Tk()
        app = AIAgentGUI(root)
        
        print("✅ JARVIS พร้อมใช้งาน!")
        print("💡 Features:")
        print("   - Phi-3 mini AI model support")
        print("   - Internet connectivity (Reddit, YouTube, Facebook, Weather)")
        print("   - Local SQLite logging")
        print("   - Performance analytics")
        print("   - Multi-tab interface")
        
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ ไม่สามารถโหลด GUI: {e}")
        print("💡 กรุณาติดตั้ง dependencies: pip install tkinter")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเริ่มต้น: {e}")
        print("💡 ลองรันโดยตรง: python agent_gui.py")

if __name__ == "__main__":
    main()