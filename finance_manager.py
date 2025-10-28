import json
import os
from datetime import datetime

class FinanceManager:
    def __init__(self, file_path="finance.json"):
        self.file_path = file_path
        self.data = {}
        self.load_data()

    def load_data(self):
        """โหลดข้อมูลรายรับรายจ่าย"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                print("⚠️ ไฟล์ข้อมูลการเงินเสียหาย กำลังสร้างใหม่...")
                self.data = {}
        else:
            self.data = {}

    def save_data(self):
        """บันทึกข้อมูลกลับลงไฟล์"""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def add_transaction(self, user, t_type, description, amount):
        """เพิ่มข้อมูลรายรับหรือรายจ่าย"""
        user = str(user)
        date_str = datetime.now().strftime("%Y-%m-%d")

        if user not in self.data:
            self.data[user] = []

        self.data[user].append({
            "date": date_str,
            "type": t_type,
            "description": description,
            "amount": amount
        })
        self.save_data()
        return f"✅ บันทึก{'รายรับ' if t_type == 'income' else 'รายจ่าย'}: {description} {amount} บาท เรียบร้อยครับ ({date_str})"

    def get_summary(self, user, month=None):
        """สรุปยอดรวมตามเดือน"""
        user = str(user)
        if user not in self.data or not self.data[user]:
            return f"ℹ️ ยังไม่มีข้อมูลของ {user} ในระบบเลยครับ"

        income_total = 0
        expense_total = 0
        month_name = month or datetime.now().strftime("%Y-%m")

        for t in self.data[user]:
            if t["date"].startswith(month_name):
                if t["type"] == "income":
                    income_total += t["amount"]
                elif t["type"] == "expense":
                    expense_total += t["amount"]

        balance = income_total - expense_total
        return (
            f"📊 สรุปข้อมูลเดือน {month_name}\n"
            f"💰 รายรับ: {income_total:,.2f} บาท\n"
            f"💸 รายจ่าย: {expense_total:,.2f} บาท\n"
            f"💵 คงเหลือ: {balance:,.2f} บาท"
        )