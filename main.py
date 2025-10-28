from brain import Brain
from finance_manager import FinanceManager
from news_manager import NewsManager # ✅ แก้ตรงนี้!

news = NewsManager(api_key="a11de2d46a164d5dbd43282d93a33260")

try:
    jarvis = Brain()
except Exception as e:
    print(f"❌ เกิดข้อผิดพลาดในการเริ่มต้น Jarvis: {str(e)}")
    exit(1)

# สร้างระบบการเงิน
finance = FinanceManager()

print("🤖 JARVIS v3+: ผู้ช่วยครอบครัวอัจฉริยะ")

# ตรวจสอบว่า memory มี profile หรือยัง
if not hasattr(jarvis, 'memory') or 'profile' not in jarvis.memory:
    print("⚠️ ยังไม่มีข้อมูลผู้ใช้ กรุณาตรวจสอบไฟล์ config.json และ creator.json")
    current_user = "ผู้ใช้ทั่วไป"
else:
    current_user = jarvis.memory['profile']['name']
    role = jarvis.memory['profile'].get('role', 'สมาชิกครอบครัว')
    print(f"👤 ผู้ใช้ปัจจุบัน: {current_user} ({role})")

print("💡 พิมพ์ 'เปลี่ยนผู้ใช้ [ชื่อ]' เพื่อสลับผู้ใช้")
print("💡 พิมพ์ 'รายรับ [รายการ] [จำนวน]' หรือ 'รายจ่าย [รายการ] [จำนวน]' เพื่อบันทึกธุรกรรม")
print("💡 พิมพ์ 'สรุป' เพื่อดูสรุปรายเดือน\n")

while True:
    command = input("คุณ: ").strip()
    if not command:
        continue

    # คำสั่งออกจากระบบ
    if command.lower() in ["ออก", "จบ", "exit", "bye"]:
        print("JARVIS: แล้วพบกันใหม่นะครับ 👋")
        break

    # ---------------------------------------------------
    # 🔁 เปลี่ยนผู้ใช้
    # ---------------------------------------------------
    if command.startswith("เปลี่ยนผู้ใช้") or command.startswith("ผู้ใช้") or command.startswith("สลับ"):
        parts = command.split(maxsplit=1)
        if len(parts) > 1:
            current_user = parts[1].strip()
            print(f"JARVIS: ✅ เปลี่ยนผู้ใช้เป็น {current_user} เรียบร้อยครับ")
        else:
            print("JARVIS: ⚠️ กรุณาระบุชื่อผู้ใช้ เช่น 'เปลี่ยนผู้ใช้ แม่'")
        continue

    # ---------------------------------------------------
    # 💰 รายรับ / รายจ่าย
    # ---------------------------------------------------
    if command.startswith("รายรับ"):
        parts = command.split()
        if len(parts) >= 3:
            try:
                desc = parts[1]
                amount = float(parts[2])
                result = finance.add_transaction(current_user, "income", desc, amount)
                print("JARVIS:", result)
            except ValueError:
                print("JARVIS: ⚠️ รูปแบบไม่ถูกต้อง เช่น 'รายรับ เงินเดือน 15000'")
        else:
            print("JARVIS: ⚠️ กรุณาระบุรายการและจำนวน เช่น 'รายรับ เงินเดือน 15000'")
        continue

    if command.startswith("รายจ่าย"):
        parts = command.split()
        if len(parts) >= 3:
            try:
                desc = parts[1]
                amount = float(parts[2])
                result = finance.add_transaction(current_user, "expense", desc, amount)
                print("JARVIS:", result)
            except ValueError:
                print("JARVIS: ⚠️ รูปแบบไม่ถูกต้อง เช่น 'รายจ่าย อาหาร 200'")
        else:
            print("JARVIS: ⚠️ กรุณาระบุรายการและจำนวน เช่น 'รายจ่าย อาหาร 200'")
        continue

    # ---------------------------------------------------
    # 📊 สรุปรายเดือน
    # ---------------------------------------------------
    if command.startswith("สรุป"):
        print("JARVIS:", finance.get_summary(current_user))
        continue

    # ---------------------------------------------------
    # 🧠 การประมวลผลทั่วไป (Brain)
    # ---------------------------------------------------
    try:
        response = jarvis.think(command)
        print("JARVIS:", response)
    except Exception as e:
        print(f"JARVIS: เกิดข้อผิดพลาดในการประมวลผลคำสั่ง: {str(e)}")