# 🌐 คู่มือใช้งาน JARVIS Web Interface

## 🎯 ระบบที่พร้อมใช้งาน

### ✅ **ระบบ Web Interface สมบูรณ์**
- 🔐 **ระบบ Login/Authentication** - เข้าสู่ระบบด้วย username/password
- 💬 **Web Chat Interface** - สนทนากับ AI ผ่านเว็บเบราว์เซอร์
- 📊 **บันทึกประวัติ** - จัดเก็บการสนทนาพร้อมวันเวลาในฐานข้อมูล
- 🌐 **Internet Connectivity** - ดึงข้อมูลจาก Reddit, Weather, etc.
- 🔄 **Real-time Messaging** - Socket.IO สำหรับการสนทนาแบบเรียลไทม์

### 💾 **ข้อมูลที่จัดเก็บ**
- `jarvis_web.db` - ฐานข้อมูลผู้ใช้, การสนทนา, ข้อความ
- `ai_agent_logs.db` - ประสิทธิภาพ AI และการเชื่อมต่ออินเทอร์เน็ต
- `agent_activity.log` - ไฟล์บันทึกกิจกรรม

## 🚀 วิธีการเริ่มใช้งาน

### **ขั้นตอนที่ 1: เริ่มต้นระบบ**
```powershell
# วิธีที่ 1: ใช้สคริปต์ตั้งค่า (แนะนำ)
python start_web_jarvis.py

# วิธีที่ 2: เริ่มเซิร์ฟเวอร์โดยตรง  
python web_server.py

# วิธีที่ 3: ใช้ไฟล์ .bat
start_jarvis_web.bat
```

### **ขั้นตอนที่ 2: เข้าใช้งาน**
1. เปิดเบราว์เซอร์ไปที่: **http://localhost:5000**
2. หน้า Login จะแสดงขึ้นอัตโนมัติ
3. ใช้บัญชีทดสอบ:
   - **Username:** `admin`
   - **Password:** `admin123`

### **ขั้นตอนที่ 3: เริ่มสนทนา**
1. คลิก "แชทใหม่" เพื่อเริ่มการสนทนา
2. พิมพ์ข้อความและกด Enter
3. AI จะตอบกลับผ่าน Phi-3 mini model

## 💡 คุณสมบัติการใช้งาน

### 🗣️ **การสนทนาพื้นฐาน**
```
คุณ: สวัสดี JARVIS
AI: สวัสดีครับ! ผมคือ JARVIS ผู้ช่วย AI ของคุณ
```

### 🌐 **ดึงข้อมูลจากอินเทอร์เน็ต**
```
คุณ: reddit AI news
AI: [ดึงข้อมูลจาก Reddit เกี่ยวกับ AI]

คุณ: สภาพอากาศ กรุงเทพ  
AI: [แสดงข้อมูลสภาพอากาศปัจจุบัน]
```

### 📱 **รองรับ Mobile**
- Responsive design ใช้งานได้บนมือถือ
- Sidebar แบบ collapsible
- Touch-friendly interface

### 📊 **การจัดการประวัติ**
- ประวัติการสนทนาแสดงในแถบข้าง
- แสดงวันเวลาการสนทนา
- สามารถค้นหาการสนทนาได้
- Export ประวัติเป็นไฟล์ JSON

## 🔧 ระบบ Backend Architecture

### **Web Server (Flask + SocketIO)**
- **Flask**: Web framework หลัก
- **Flask-SocketIO**: Real-time WebSocket messaging
- **SQLite**: ฐานข้อมูลฝังตัว

### **AI Integration**
- เชื่อมต่อกับ `ai_agent.py` ที่มีอยู่เดิม
- ใช้ Ollama API สำหรับ Phi-3 mini
- รองรับ internet data fetching

### **Authentication System**  
- Session-based authentication
- Password hashing ด้วย SHA256
- Session timeout 24 ชั่วโมง

## 🗄️ Database Schema

### **Tables ที่สร้างขึ้น:**

#### **users** - ข้อมูลผู้ใช้
```sql
id, username, password_hash, email, created_at, last_login, is_active, settings
```

#### **conversations** - การสนทนา
```sql  
id, user_id, title, created_at, updated_at, message_count
```

#### **messages** - ข้อความ
```sql
id, conversation_id, sender, content, timestamp, message_type, metadata
```

#### **user_sessions** - Session management
```sql
id, user_id, created_at, expires_at, ip_address, user_agent, is_active
```

## 🌟 ตัวอย่างการใช้งานจริง

### **1. การสนทนาปกติ**
- เข้าสู่ระบบ → สร้างแชทใหม่ → สนทนา
- ระบบบันทึกทุกข้อความพร้อมเวลา
- สามารถกลับมาดูประวัติได้ทุกเมื่อ

### **2. การดึงข้อมูลอินเทอร์เน็ต**
- พิมพ์ "reddit machine learning" → ดึงข้อมูลจาก Reddit
- พิมพ์ "อากาศวันนี้" → ดึงข้อมูลสภาพอากาศ
- Metadata แสดงแหล่งข้อมูลและเวลาในการประมวลผล

### **3. การจัดการผู้ใช้หลายคน**
- Admin สามารถสร้างผู้ใช้เพิ่มได้ (ต้องแก้โค้ด)
- แต่ละคนมีประวัติการสนทนาแยกกัน
- Session แยกกันโดยอิสระ

## 🔗 API Endpoints

### **Authentication**
- `POST /login` - เข้าสู่ระบบ
- `POST /logout` - ออกจากระบบ

### **Chat API**  
- `GET /api/conversations` - ดึงรายการการสนทนา
- `GET /api/conversations/{id}/messages` - ดึงข้อความ
- `POST /api/chat` - ส่งข้อความใหม่

### **WebSocket Events**
- `connect` - เชื่อมต่อ
- `send_message` - ส่งข้อความ
- `ai_response` - รับคำตอบจาก AI

## 🎛️ การปรับแต่ง

### **เปลี่ยน AI Model**
แก้ไขใน `ai_agent.py`:
```python
self.default_model = "phi3:mini"  # เปลี่ยนเป็นโมเดลอื่น
```

### **เพิ่มผู้ใช้ใหม่**
```python
# รันใน Python console
from web_server import WebJARVIS
web = WebJARVIS()
# สร้างผู้ใช้ใหม่โดยแก้โค้ดใน create_default_admin()
```

### **เปลี่ยนพอร์ต**
แก้ไขใน `web_server.py` บรรทัดสุดท้าย:
```python
socketio.run(app, debug=True, host='0.0.0.0', port=8080)
```

## 🛠️ การแก้ปัญหา

### **ปัญหา: ไม่สามารถเชื่อมต่อ**
- ตรวจสอบ Ollama: `ollama serve`
- ตรวจสอบ port 5000 ว่าไม่ถูกใช้งาน
- ลองรีสตาร์ท web server

### **ปัญหา: Login ไม่ได้**
- ใช้ admin/admin123 สำหรับครั้งแรก
- ลบไฟล์ `jarvis_web.db` เพื่อ reset

### **ปัญหา: AI ไม่ตอบ**
- ตรวจสอบ Ollama status
- ดู log ใน `agent_activity.log`
- ตรวจสอบโมเดล: `ollama list`

## 🎉 สรุป

ระบบ **JARVIS Web Interface** ตอบโจทย์ครบถ้วนตามที่ต้องการ:

✅ **เชื่อมต่อข้อมูลเก็บไว้** - ฐานข้อมูล SQLite  
✅ **ใช้ได้จริง** - Web interface ที่สมบูรณ์  
✅ **กรอกชื่อผู้ใช้และรหัสผ่าน** - ระบบ authentication  
✅ **ประวัติการสนทนาระบุวันเวลา** - บันทึกครบถ้วน  

🚀 **พร้อมใช้งานได้ทันที!**