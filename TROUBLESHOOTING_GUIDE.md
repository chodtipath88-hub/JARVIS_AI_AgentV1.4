# คู่มือแก้ไขปัญหา JARVIS AI System

## ขั้นตอนการตรวจสอบปัญหา

### 1. ตรวจสอบ Ollama API
```powershell
# ตรวจสอบว่า Ollama ทำงานอยู่หรือไม่
curl http://localhost:11434/api/tags

# หากไม่ทำงาน ให้เริ่ม Ollama
ollama serve
```

### 2. ตรวจสอบ Web Server
```powershell
# ตรวจสอบว่า Web Server ทำงานอยู่หรือไม่
curl http://localhost:5000

# หากไม่ทำงาน ให้เริ่ม Web Server
python web_server.py
```

### 3. ตรวจสอบการเชื่อมต่อแบบ Manual

#### วิธีที่ 1: ใช้ Web Interface
1. เปิด Browser ไปที่ http://localhost:5000
2. ใช้ Username: `admin` Password: `admin123` เข้าสู่ระบบ
3. ลองส่งข้อความทดสอบ เช่น "สวัสดีครับ"

#### วิธีที่ 2: ใช้ Desktop GUI
```powershell
# เริ่ม Desktop GUI
python Local_AI_Agent_main.py
```

#### วิธีที่ 3: ทดสอบ AI Agent โดยตรง
```powershell
python test_ai_agent.py
```

### 4. ปัญหาที่พบบ่อย

#### ปัญหา: "Connection refused" หรือ "Cannot connect"
**สาเหตุ:** Ollama หรือ Web Server ไม่ได้เปิดอยู่
**วิธีแก้:** เริ่ม Ollama และ Web Server ใหม่

#### ปัญหา: "Model not found"
**สาเหตุ:** ไม่มี Model phi3:mini
**วิธีแก้:** 
```powershell
ollama pull phi3:mini
```

#### ปัญหา: หน้าเว็บไม่แสดงผล
**สาเหตุ:** Browser cache หรือ JavaScript error
**วิธีแก้:** กด Ctrl+F5 หรือเปิด Developer Tools (F12) ดู error

#### ปัญหา: Login ไม่ได้
**สาเหตุ:** Database ยังไม่ได้สร้างหรือเสียหาย
**วิธีแก้:** ลบไฟล์ `jarvis_web.db` และเริ่มใหม่

### 5. วิธีเริ่มระบบใหม่ทั้งหมด

```powershell
# 1. หยุดทุก Process ที่เกี่ยวข้อง
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*ollama*"} | Stop-Process -Force

# 2. เริ่ม Ollama
Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden

# 3. รอ 5 วินาที
Start-Sleep 5

# 4. เริ่ม Web Server
python web_server.py
```

### 6. Log Files สำหรับ Debug

- `ai_agent.db` - SQLite database ของ AI Agent
- `jarvis_web.db` - SQLite database ของ Web Interface  
- Console output ของ Python scripts จะแสดง error messages

### 7. ข้อมูล Login เริ่มต้น

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**Demo Account:** 
- Username: `demo`
- Password: `demo123`

### 8. การติดต่อ APIs ภายนอก

ระบบจะพยายามเชื่อมต่อ:
- Reddit API (ไม่ต้องใช้ API key)
- Weather API (wttr.in)
- YouTube/Facebook (ต้องการ API keys)

หาก APIs เหล่านี้ไม่ทำงาน ระบบจะใช้ AI model เพียงอย่างเดียว

## ขั้นตอนการทดสอบแบบละเอียด

### Test 1: ทดสอบ Ollama
```powershell
ollama list
ollama run phi3:mini "สวัสดีครับ"
```

### Test 2: ทดสอบ Web Server Connection
```powershell
curl -X POST http://localhost:5000/api/chat -H "Content-Type: application/json" -d '{\"message\": \"สวัสดีครับ\", \"session_id\": \"test123\"}'
```

### Test 3: ทดสอบ Database
```python
import sqlite3
conn = sqlite3.connect('jarvis_web.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
conn.close()
```

## หมายเหตุสำคัญ

1. **Port Conflicts:** หาก port 5000 หรือ 11434 ถูกใช้งาน ให้เปลี่ยน port ในไฟล์ config
2. **Firewall:** ตรวจสอบว่า Windows Firewall ไม่ได้ block ports เหล่านี้
3. **Python Environment:** ตรวจสอบว่าติดตั้ง dependencies ครบถ้วน: `pip install -r requirements.txt`
4. **Encoding Issues:** ใช้ UTF-8 encoding สำหรับข้อความภาษาไทย

เมื่อแก้ไขปัญหาแล้ว ระบบควรทำงานได้ปกติผ่าน http://localhost:5000