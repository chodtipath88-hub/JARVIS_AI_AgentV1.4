import json
import os
import nltk
from nltk.corpus import wordnet

nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

class Brain:
    def __init__(self, memory_file="my_data.json"):
        self.memory_file = memory_file
        self.memory = {}
        self.load_memory()
        self.load_config()
        self.load_user_memory()
        self.ai_router = AIRouter()  # ✅ สร้าง instance ของ AIRouter

    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # ตรวจสอบว่า data เป็น dict จริงหรือไม่
                    if isinstance(data, dict):
                        self.memory = data
                    else:
                        print("⚠️ ไฟล์ my_data.json ไม่ใช่รูปแบบพจนานุกรม กำลังรีเซ็ต...")
                        self.memory = {}
            except (json.JSONDecodeError, FileNotFoundError):
                print("⚠️ ไฟล์ my_data.json เสียหายหรือไม่สามารถอ่านได้ กำลังรีเซ็ต...")
                self.memory = {}
        else:
            self.memory = {}

    def save_memory(self):
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=4)

    def similarity(self, word1, word2):
        """คำนวณความคล้ายกันของคำ"""
        syn1 = wordnet.synsets(word1)
        syn2 = wordnet.synsets(word2)
        if not syn1 or not syn2:
            return 0
        return syn1[0].wup_similarity(syn2[0]) or 0

    def find_best_match(self, command):
        """หาประโยคที่คล้ายที่สุดในความจำ"""
        best_match = None
        highest_score = 0

        for known_command in self.memory.keys():
            score = 0
            for word in command.split():
                for known_word in known_command.split():
                    score += self.similarity(word, known_word)
            if score > highest_score:
                highest_score = score
                best_match = known_command
        return best_match

    def think(self, command):
        """ประมวลผลคำพูด"""
        command = command.lower()

        # ถ้ามีในความจำ → ตอบเลย
        if command in self.memory:
            return self.memory[command]

        # ถ้ามีคำที่ใกล้เคียง → ใช้คำตอบนั้น
        match = self.find_best_match(command)
        if match:
            return f"คุณหมายถึง: '{match}' ใช่ไหม? ถ้าใช่ ผมจำได้ว่า {self.memory[match]}"

        # ถ้าไม่รู้จัก → ถามกลับและเรียนรู้
        print("JARVIS: ผมยังไม่รู้จักคำนี้เลยครับ ช่วยบอกหน่อยได้ไหมว่าควรตอบว่าอะไร?")
        response = input("คุณ: ")
        self.memory[command] = response
        self.save_memory()
        return "ขอบคุณครับ ผมจะจำไว้!"
    def set_user(self, username):
        """สลับผู้ใช้"""
        import datetime

        # สร้าง path สำหรับไฟล์ผู้ใช้
        user_file = os.path.join("users", f"{username}.json")

        if os.path.exists(user_file):
            self.memory_file = user_file
            self.load_memory()
            return f"✅ สลับเป็นผู้ใช้ '{username}' แล้วครับ"
        else:
            # ถ้ายังไม่มีไฟล์นี้ ให้สร้างใหม่
            self.memory_file = user_file
            self.memory = {
                "profile": {
                    "name": username,
                    "role": "user",
                    "created_at": datetime.datetime.now().isoformat()
                },
                "knowledge": {}
            }
            self.save_memory()
            return f"🆕 สร้างผู้ใช้ใหม่ '{username}' และเริ่มต้นความจำใหม่ครับ"