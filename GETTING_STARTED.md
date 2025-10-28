# 🎯 คู่มือการใช้งาน JARVIS Local AI Agent - Phi-3 Enhanced

## 📋 สรุปโครงการที่สร้างเสร็จแล้ว

### ✅ ระบบที่พัฒนาเสร็จสิ้น:

#### 🧠 **AI Core System**
- ✅ รองรับ **Phi-3 mini** เป็น default model
- ✅ Fallback system สำหรับโมเดลอื่น ๆ (Llama, Qwen, etc.)
- ✅ Model performance monitoring และ statistics
- ✅ Automatic model detection และ health checks

#### 🌐 **Internet Connectivity**
- ✅ **Reddit API** - ดึงข้อมูลจาก Reddit (ไม่ต้อง auth)
- ✅ **YouTube API** - รองรับ (ต้องมี API key)
- ✅ **Facebook API** - รองรับ (ต้องมี access token)
- ✅ **Weather API** - ใช้ wttr.in (ฟรี)
- ✅ **General APIs** - รองรับ public APIs

#### 🖥️ **Windows Desktop GUI**
- ✅ **Multi-tab interface**: Chat, Internet Data, Analytics
- ✅ **Real-time monitoring** สถานะและประสิทธิภาพ
- ✅ **Model selection** และ platform selection
- ✅ **Statistics dashboard** แบบเรียลไทม์
- ✅ **Export และ database viewer**

#### 💾 **Local Data Management**
- ✅ **SQLite database** สำหรับ logging
- ✅ **Performance tracking** ต่อโมเดลและการเชื่อมต่อ
- ✅ **Structured logging** แบบครบถ้วน
- ✅ **Export capabilities** (JSON)

## 🚀 วิธีการเริ่มใช้งาน

### ขั้นตอนที่ 1: เตรียมสภาพแวดล้อม

```powershell
# 1. ติดตั้ง Ollama (ถ้ายังไม่มี)
# ดาวน์โหลดจาก: https://ollama.ai/

# 2. ติดตั้ง Phi-3 mini
ollama pull phi3:mini

# 3. เริ่ม Ollama server
ollama serve
```

### ขั้นตอนที่ 2: ติดตั้ง Dependencies

```powershell
# เข้าไปยังโฟลเดอร์โครงการ
cd c:\JARVIS_AI_Agent

# ติดตั้ง Python packages
pip install -r requirements.txt
```

### ขั้นตอนที่ 3: ทดสอบระบบ

```powershell
# ทดสอบระบบทั้งหมด
python test_phi3_system.py
```

### ขั้นตอนที่ 4: เริ่มใช้งาน

```powershell
# เริ่มใช้งาน JARVIS (วิธีที่แนะนำ)
python Local_AI_Agent_main.py
```

## 💡 คุณสมบัติที่ใช้งานได้

### 🗣️ การสนทนาพื้นฐาน
```
คุณ: สวัสดี JARVIS
AI: สวัสดีครับ! ผมคือ JARVIS ผู้ช่วย AI ที่พร้อมช่วยเหลือคุณ
```

### 🌐 การดึงข้อมูลจาก Reddit
```
คุณ: reddit AI news
AI: [ดึงโพสต์ล่าสุดเกี่ยวกับ AI จาก Reddit พร้อมคะแนนและ subreddit]
```

### 🌤️ การตรวจสอบสภาพอากาศ
```
คุณ: สภาพอากาศ กรุงเทพ
AI: [แสดงอุณหภูมิ ความชื้น ลม และคำอธิบายสภาพอากาศ]
```

### 🎥 การค้นหา YouTube (ต้องมี API key)
```
คุณ: youtube Python tutorial
AI: [แนะนำวิดีโอที่เกี่ยวข้อง]
```

### 📊 การดูสถิติ
- ใช้แท็บ "📊 Logs & Analytics"
- กดปุ่ม "📈 Refresh Stats"
- ดู performance ของแต่ละโมเดล

## ⚙️ การปรับแต่งขั้นสูง

### เปลี่ยน Default Model
แก้ไขใน `ai_agent.py` บรรทัดที่ 13:
```python
self.default_model = "phi3:mini"  # เปลี่ยนเป็นโมเดลที่ต้องการ
```

### เพิ่ม API Keys สำหรับ YouTube/Facebook
สร้างไฟล์ `config.json`:
```json
{
  "youtube_api_key": "YOUR_YOUTUBE_API_KEY",
  "facebook_access_token": "YOUR_FACEBOOK_TOKEN"
}
```

### ปรับแต่งการเชื่อมต่อ
แก้ไข URL หรือ timeout ใน `ai_agent.py`:
```python
self.ollama_url = "http://localhost:11434/api/generate"
self.timeout = 60  # เปลี่ยนเป็น timeout ที่ต้องการ
```

## 🎛️ การใช้งาน GUI

### แท็บ Chat (💬)
- พิมพ์คำถามใน text box
- เลือกโมเดลจาก dropdown
- เลือก platform (หรือใช้ auto-detect)
- กดปุ่ม "🚀 Send"

### แท็บ Internet Data (🌐)
- ดูสถานะของแต่ละ platform
- ดูข้อมูลที่ดึงมาล่าสุด (JSON format)

### แท็บ Logs & Analytics (📊)
- ดูสถิติการใช้งานแบบเรียลไทม์
- Export logs เป็นไฟล์ JSON
- ดูข้อมูลในฐานข้อมูล SQLite

## 🔧 การแก้ปัญหาที่พบบ่อย

### ❌ Ollama ไม่ตอบสนอง
```powershell
# ตรวจสอบ Ollama
ollama list

# เริ่มใหม่
ollama serve
```

### ❌ ไม่พบ Phi-3 model
```powershell
# ติดตั้งโมเดล
ollama pull phi3:mini

# ตรวจสอบ
ollama list
```

### ❌ GUI ไม่แสดง
```powershell
# ติดตั้ง dependencies ใหม่
pip install --upgrade tkinter requests sqlite3

# ทดสอบ GUI
python agent_gui.py
```

### ❌ Internet connectivity ไม่ทำงาน
- ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
- ลองเปลี่ยน DNS เป็น 8.8.8.8
- ตรวจสอบ firewall settings

## 📈 การติดตามประสิทธิภาพ

### ไฟล์ Log ที่สร้างขึ้น:
- `ai_agent_logs.db` - SQLite database
- `agent_activity.log` - Text log file
- `jarvis_logs_YYYYMMDD_HHMMSS.json` - Exported statistics

### สถิติที่ติดตาม:
- จำนวนคำขอทั้งหมด
- อัตราความสำเร็จ (%)
- เวลาตอบสนองเฉลี่ย
- การใช้งานแต่ละโมเดล
- สถิติการเชื่อมต่ออินเทอร์เน็ต

## 🎯 ตัวอย่างการใช้งานจริง

### สำหรับงานวิจัย
```
คุณ: reddit machine learning research
AI: [ดึงกระทู้วิจัย ML ล่าสุดจาก r/MachineLearning]
```

### สำหรับการเรียนรู้
```
คุณ: youtube Python beginner tutorial
AI: [แนะนำคอร์ส Python สำหรับมือใหม่]
```

### สำหรับการทำงาน
```
คุณ: สภาพอากาศ วันนี้ มีฝนไหม
AI: [รายงานสภาพอากาศและโอกาสฝนตก]
```

## 🚀 คุณสมบัติที่พร้อมใช้งานทันที

✅ **Phi-3 mini AI model** - ตอบคำถามได้หลากหลาย  
✅ **Reddit integration** - ดึงข้อมูลจาก Reddit  
✅ **Weather data** - ข้อมูลสภาพอากาศฟรี  
✅ **Performance monitoring** - ติดตามประสิทธิภาพ  
✅ **Local database** - บันทึกการทำงานทั้งหมด  
✅ **Export capabilities** - ส่งออกข้อมูลได้  
✅ **Multi-model support** - รองรับหลายโมเดล  
✅ **Desktop GUI** - อินเทอร์เฟซที่ใช้งานง่าย  

---

🎉 **ระบบพร้อมใช้งานเต็มรูปแบบแล้ว!** ลองเริ่มต้นด้วยคำสั่ง:
```powershell
python Local_AI_Agent_main.py
```