import random
from datetime import datetime
import json
import os

class AIRouter:
    def __init__(self):
        self.providers = {
            "qwen": {
                "model": "qwen-max",
                "api_key": "YOUR_QWEN_API_KEY",  # ⚠️ เปลี่ยนเป็น API Key จริงของคุณ
                "name": "Qwen (Alibaba)",
                "description": "เหมาะสำหรับคำถามทั่วไป, การเขียนโค้ด, ความคิดสร้างสรรค์"
            },
            "gemini": {
                "model": "gemini-pro",
                "api_key": "YOUR_GEMINI_API_KEY",  # ⚠️ เปลี่ยนเป็น API Key จริงของคุณ
                "name": "Gemini (Google)",
                "description": "เหมาะสำหรับข่าวสาร, ข้อมูลปัจจุบัน, การวิเคราะห์ข้อความ"
            },
            "openai": {
                "model": "gpt-4o",
                "api_key": "YOUR_OPENAI_API_KEY",  # ⚠️ เปลี่ยนเป็น API Key จริงของคุณ
                "name": "GPT-4o (OpenAI)",
                "description": "เหมาะสำหรับการเขียนโค้ด, คำแนะนำเชิงเทคนิค, การวิเคราะห์เชิงลึก"
            },
            "claude": {
                "model": "claude-3-opus-20240229",
                "api_key": "YOUR_CLAUDE_API_KEY",  # ⚠️ เปลี่ยนเป็น API Key จริงของคุณ
                "name": "Claude 3 Opus (Anthropic)",
                "description": "เหมาะสำหรับการเขียนบทความ, การอธิบายแนวคิดซับซ้อน, การวิเคราะห์เชิงตรรกะ"
            }
        }
        self.performance_log = []  # บันทึกประวัติการตอบ
        self.error_log = []        # บันทึกข้อผิดพลาด
        self.load_performance_log()  # โหลดประวัติจากไฟล์
        self.load_error_log()       # โหลดข้อผิดพลาดจากไฟล์

    def route(self, prompt, user_id="creator"):
        """
        รับคำถาม → วิเคราะห์ → เลือก AI → ถาม → บันทึก → แสดงแหล่งที่มา
        """
        category = self.analyze_category(prompt)
        selected_provider = self.select_provider(category, user_id)
        response = self.call_ai(selected_provider, prompt)

        # บันทึกผลลัพธ์ + ให้ผู้ใช้ประเมิน (ถ้ามี)
        self.log_performance(selected_provider, prompt, response, category)

        # เพิ่มข้อความระบุแหล่งที่มา
        source_info = f"\n\n🔍 คำตอบนี้มาจาก: {self.providers[selected_provider]['name']}"
        return response + source_info

    def analyze_category(self, prompt):
        """วิเคราะห์ประเภทคำถามแบบง่าย"""
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ["ข่าว", "วันนี้", "เหตุการณ์", "เมื่อวาน", "พรุ่งนี้"]):
            return "news"
        elif any(word in prompt_lower for word in ["เงิน", "รายรับ", "รายจ่าย", "สรุป", "ค่าใช้จ่าย", "บัญชี", "ภาษี"]):
            return "finance"
        elif any(word in prompt_lower for word in ["สุขภาพ", "น้ำหนัก", "อาการ", "หมอ", "ยา", "ออกกำลังกาย"]):
            return "health"
        elif any(word in prompt_lower for word in ["เขียนโค้ด", "โปรแกรม", "Python", "HTML", "CSS", "JavaScript", "แก้ไขโค้ด", "ฟังก์ชัน", "คลาส"]):
            return "coding"
        else:
            return "general"

    def select_provider(self, category, user_id):
        """เลือก AI ตามประเภทคำถาม + ประวัติการตอบที่ดีที่สุด"""
        # ตัวอย่างง่าย: ใช้ Qwen สำหรับทั่วไป, Gemini สำหรับข่าว, OpenAI สำหรับการเงิน/โค้ด
        provider_map = {
            "news": "gemini",
            "finance": "openai",
            "health": "claude",
            "coding": "openai",
            "general": "qwen"
        }

        # ตรวจสอบว่ามีประวัติการตอบที่ดีในหมวดนี้ไหม
        best_provider = provider_map.get(category, "qwen")

        # ถ้ามีประวัติการตอบดีในหมวดนี้ → เลือก AI นั้น
        recent_good = [log for log in self.performance_log if log["category"] == category and log["success"]]
        if recent_good:
            # หา AI ที่ตอบดีที่สุดในหมวดนี้ (ตัวอย่างง่าย: ใช้ตัวแรก)
            best_provider = recent_good[0]["provider"]

        return best_provider

    def call_ai(self, provider_name, prompt):
        """เรียก API ของ AI แต่ละเจ้า"""
        provider = self.providers[provider_name]
        model = provider["model"]
        api_key = provider["api_key"]

        try:
            if provider_name == "qwen":
                from dashscope import Generation
                Generation.api_key = api_key
                response = Generation.call(model=model, prompt=prompt, temperature=0.7)
                return response.output.choices[0].message.content

            elif provider_name == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model)
                response = model.generate_content(prompt)
                return response.text

            elif provider_name == "openai":
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content

            elif provider_name == "claude":
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                message = client.messages.create(
                    model=model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text

        except Exception as e:
            # บันทึกข้อผิดพลาด
            self.log_error(provider_name, prompt, str(e))
            return f"❌ {provider['name']} ไม่สามารถตอบคำถามนี้ได้ ({str(e)})"

    def log_performance(self, provider, prompt, response, category):
        """บันทึกผลลัพธ์เพื่อเรียนรู้ในอนาคต"""
        success = "❌" not in response  # ถ้าไม่มี ❌ ถือว่าสำเร็จ
        self.performance_log.append({
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "category": category,
            "prompt": prompt[:50] + "...",  # แสดงส่วนแรก
            "response_length": len(response),
            "success": success,
            "response_preview": response[:100] + "..." if len(response) > 100 else response
        })

        # ลบ log เก่าออกหากเกิน 100 รายการ
        if len(self.performance_log) > 100:
            self.performance_log.pop(0)

        # บันทึกลงไฟล์
        self.save_performance_log()

    def log_error(self, provider, prompt, error_message):
        """บันทึกข้อผิดพลาด"""
        self.error_log.append({
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "prompt": prompt[:50] + "...",
            "error": error_message
        })

        # ลบ log เก่าออกหากเกิน 50 รายการ
        if len(self.error_log) > 50:
            self.error_log.pop(0)

        # บันทึกลงไฟล์
        self.save_error_log()

    def load_performance_log(self):
        """โหลดประวัติการตอบจากไฟล์"""
        log_file = "ai_performance_log.json"
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                self.performance_log = json.load(f)

    def save_performance_log(self):
        """บันทึกประวัติการตอบลงไฟล์"""
        log_file = "ai_performance_log.json"
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(self.performance_log, f, ensure_ascii=False, indent=4)

    def load_error_log(self):
        """โหลดข้อผิดพลาดจากไฟล์"""
        log_file = "ai_error_log.json"
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                self.error_log = json.load(f)

    def save_error_log(self):
        """บันทึกข้อผิดพลาดลงไฟล์"""
        log_file = "ai_error_log.json"
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(self.error_log, f, ensure_ascii=False, indent=4)

    def get_feedback(self, prompt, response, user_id):
        """ให้ผู้ใช้ประเมินคำตอบ"""
        print("\n✅ คุณพอใจกับคำตอบนี้ไหม?")
        print("1. ดีมาก (ใช้ AI นี้อีกครั้ง)")
        print("2. พอใช้ได้ (ลอง AI อื่น)")
        print("3. แย่มาก (หลีกเลี่ยง AI นี้)")
        feedback = input("เลือก (1/2/3): ").strip()

        if feedback == "1":
            # บันทึกว่า AI นี้ตอบดี
            pass  # ไม่ต้องทำอะไร — เพราะ default คือ success=True
        elif feedback == "2":
            # ลดคะแนนของ AI นี้ในหมวดนี้
            pass  # อาจเพิ่มระบบคะแนนในอนาคต
        elif feedback == "3":
            # บันทึกว่า AI นี้ตอบแย่
            for log in self.performance_log:
                if log["prompt"] == prompt[:50] + "..." and log["provider"] == self.select_provider(self.analyze_category(prompt), user_id):
                    log["success"] = False
            self.save_performance_log()

        print("ขอบคุณสำหรับความคิดเห็น!")

    def edit_answer(self, original_prompt, new_answer):
        """ผู้ใช้แก้ไขคำตอบ"""
        if original_prompt in self.performance_log:
            # หา index ของคำตอบเดิม
            for i, log in enumerate(self.performance_log):
                if log["prompt"] == original_prompt[:50] + "...":
                    self.performance_log[i]["response_preview"] = new_answer[:100] + "..." if len(new_answer) > 100 else new_answer
                    self.performance_log[i]["source"] = "user_edited"
                    break
            self.save_performance_log()
            return "✅ ฉันได้บันทึกคำตอบใหม่แล้ว!"
        else:
            return "❌ ไม่พบคำถามนี้ในความจำ"