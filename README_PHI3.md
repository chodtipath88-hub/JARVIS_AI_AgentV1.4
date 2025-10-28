# 🤖 JARVIS Local AI Agent - Phi-3 Enhanced

ระบบ Local AI Agent ที่ใช้ Phi-3 mini สำหรับการสร้างตัวกลางเชื่อมต่ออินเทอร์เน็ต พร้อมหน้าเดสก์ท็อปบน Windows และระบบบันทึกการทำงานแบบ Local

## ✨ คุณสมบัติหลัก

### 🧠 AI Core Features
- **Phi-3 mini model support** - โมเดล AI ขนาดเล็กที่มีประสิทธิภาพสูง
- **Fallback model system** - รองรับหลายโมเดล (Llama, Qwen, etc.)
- **Performance monitoring** - ติดตามประสิทธิภาพแต่ละโมเดล
- **Response time optimization** - เพิ่มประสิทธิภาพการตอบสนอง

### 🌐 Internet Connectivity
- **Reddit Integration** - ดึงข้อมูลจาก Reddit (ไม่ต้อง API key)
- **YouTube Data** - รองรับ YouTube API (ต้องมี API key)
- **Facebook Graph** - รองรับ Facebook API (ต้องมี access token)
- **Weather Services** - ข้อมูลสภาพอากาศฟรีจาก wttr.in
- **General Web APIs** - ดึงข้อมูลจาก public APIs

### 🖥️ Desktop Interface
- **Multi-tab GUI** - อินเทอร์เฟซแบบแท็บสำหรับ Chat, Internet Data, Analytics
- **Real-time monitoring** - แสดงสถานะและประสิทธิภาพแบบเรียลไทม์
- **Model selection** - เลือกโมเดลและแพลตฟอร์มได้
- **Statistics dashboard** - แดชบอร์ดสถิติและการใช้งาน

### 💾 Local Data Management
- **SQLite logging** - บันทึกการทำงานใน SQLite database
- **Performance tracking** - ติดตามประสิทธิภาพโมเดลและการเชื่อมต่อ
- **Export capabilities** - ส่งออกข้อมูลเป็น JSON
- **Database viewer** - ดูข้อมูลในฐานข้อมูลผ่าน GUI

## 🚀 การติดตั้งและใช้งาน

### 1. ติดตั้ง Ollama
```bash
# Windows
curl https://ollama.ai/install.sh | sh

# หรือดาวน์โหลดจาก https://ollama.ai/
```

### 2. ติดตั้ง Phi-3 mini
```bash
ollama pull phi3:mini
```

### 3. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 4. เริ่มใช้งาน
```bash
# วิธีที่ 1: ใช้ launcher (แนะนำ)
python Local_AI_Agent_main.py

# วิธีที่ 2: ทดสอบระบบก่อน
python test_phi3_system.py

# วิธีที่ 3: เรียกใช้ GUI โดยตรง
python agent_gui.py
```

## 📝 วิธีการใช้งาน

### การสนทนาพื้นฐาน
```
User: สวัสดี JARVIS
AI: สวัสดีครับ! ผมคือ JARVIS ผู้ช่วย AI ที่พร้อมช่วยเหลือคุณ
```

### การดึงข้อมูลจาก Reddit
```
User: reddit AI news
AI: [ดึงข้อมูลล่าสุดเกี่ยวกับ AI จาก Reddit]
```

### การตรวจสอบสภาพอากาศ
```
User: สภาพอากาศ กรุงเทพ
AI: [แสดงข้อมูลสภาพอากาศปัจจุบัน]
```

### การค้นหาข้อมูลทั่วไป
```
User: ค้นหาข้อมูล Python programming
AI: [ดึงข้อมูลเกี่ยวกับ Python จาก public APIs]
```

## 🏗️ โครงสร้างโปรเจกต์

```
JARVIS_AI_Agent/
├── ai_agent.py              # Core AI Agent class
├── agent_gui.py             # Desktop GUI interface
├── Local_AI_Agent_main.py   # Main launcher
├── test_phi3_system.py      # System testing script
├── requirements.txt         # Python dependencies
├── ai_agent_logs.db        # SQLite database (created automatically)
├── agent_activity.log      # Application logs
└── .github/
    └── copilot-instructions.md  # AI coding agent guidelines
```

## 🔧 การกำหนดค่า

### เปลี่ยนโมเดล Default
แก้ไขใน `ai_agent.py`:
```python
self.default_model = "phi3:mini"  # เปลี่ยนเป็นโมเดลที่ต้องการ
```

### เพิ่ม API Keys
สร้างไฟล์ `config.json`:
```json
{
  "youtube_api_key": "YOUR_YOUTUBE_API_KEY",
  "facebook_access_token": "YOUR_FACEBOOK_TOKEN",
  "openweather_api_key": "YOUR_WEATHER_API_KEY"
}
```

## 📊 ฟีเจอร์การวิเคราะห์

### สถิติการใช้งาน
- จำนวนคำขอทั้งหมด
- อัตราความสำเร็จ
- เวลาตอบสนองเฉลี่ย
- การใช้งานแต่ละโมเดล
- สถิติการเชื่อมต่ออินเทอร์เน็ต

### การส่งออกข้อมูล
- Export logs เป็น JSON
- ดูฐานข้อมูลผ่าน GUI
- Export สถิติประสิทธิภาพ

## 🐛 การแก้ปัญหา

### Ollama ไม่ตอบสนอง
```bash
# ตรวจสอบสถานะ
ollama list

# เริ่มใหม่
ollama serve
```

### ไม่พบ Phi-3 model
```bash
# ติดตั้งโมเดล
ollama pull phi3:mini

# ตรวจสอบโมเดลที่มี
ollama list
```

### ปัญหา GUI
```bash
# ติดตั้ง tkinter (ถ้าจำเป็น)
pip install tk

# ทดสอบ GUI components
python test_phi3_system.py
```

## 🔮 แผนการพัฒนาต่อไป

- [ ] เพิ่มการรองรับ Voice Input/Output
- [ ] ระบบ Plugin architecture
- [ ] Web interface ผ่าน FastAPI
- [ ] การรองรับ Multi-language
- [ ] Advanced analytics dashboard
- [ ] Cloud sync capabilities

## 📄 License

MIT License - ใช้งานได้อย่างอิสระสำหรับโครงการส่วนตัวและเชิงพาณิชย์

## 🤝 การมีส่วนร่วม

ยินดีรับ Pull Requests และ Issue reports! 

### พัฒนาร่วมกัน:
1. Fork โปรเจกต์
2. สร้าง feature branch
3. Commit การเปลี่ยนแปลง
4. Push ไปยัง branch
5. เปิด Pull Request

---

🎯 **เป้าหมาย**: สร้างระบบ AI Agent ที่ใช้งานง่าย มีประสิทธิภาพ และปรับแต่งได้ตามความต้องการ