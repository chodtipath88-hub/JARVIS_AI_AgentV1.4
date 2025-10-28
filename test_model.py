"""
🧪 ทดสอบโมเดลที่เทรนแล้ว
"""

from unsloth import FastLanguageModel

# โหลดโมเดล
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="./ai_brain/final_model",
    max_seq_length=512,
    dtype=None,
    load_in_4bit=True,
)

FastLanguageModel.for_inference(model) # เปิดโหมด inference (เร็วขึ้น)

# ฟังก์ชันถามตอบ
def ask(instruction, input_text):
    prompt = f"""### คำสั่ง:
{instruction}

### ข้อมูล:
{input_text}

### คำตอบ:
"""
    inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
    outputs = model.generate(
        **inputs, 
        max_new_tokens=256, 
        temperature=0.7,
        top_p=0.9,
        use_cache=True
    )
    
    result = tokenizer.batch_decode(outputs)[0]
    # ตัดเอาเฉพาะคำตอบ
    answer = result.split("### คำตอบ:")[1].strip()
    return answer

# ทดสอบ
print("💬 ทดสอบโมเดล:")
print("=" * 60)

test_cases = [
    ("สรุปค่าใช้จ่าย", "อาหาร 5000 เดินทาง 2000 ของใช้ 1500"),
    ("วางแผนออม", "เงินเดือน 25000 ค่าใช้จ่าย 15000"),
]

for instruction, input_text in test_cases:
    print(f"\n❓ {instruction}")
    print(f"📝 {input_text}")
    answer = ask(instruction, input_text)
    print(f"✅ {answer}")
    print("-" * 60)
    