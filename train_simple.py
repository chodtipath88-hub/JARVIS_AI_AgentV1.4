"""
🚀 สคริปต์เทรน AI ส่วนตัวแบบง่าย
- ใช้ Unsloth (เร็วกว่า Hugging Face 2-5 เท่า)
- รองรับ GTX 1060 6GB
- บันทึก checkpoint สำหรับเทรนต่อ
"""

from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
import torch

# ========== ตั้งค่าพื้นฐาน ==========
MODEL_NAME = "unsloth/llama-3-8b-bnb-4bit" # โมเดลเล็ก 4-bit
MAX_SEQ_LENGTH = 512 # ความยาวประโยค
DATASET_FILE = "my_data.json" # ไฟล์ข้อมูลของคุณ
OUTPUT_DIR = "./ai_brain" # โฟลเดอร์เก็บสมอง

# ========== โหลดโมเดล ==========
print("📥 กำลังโหลดโมเดล...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=None,
    load_in_4bit=True,
)

# ========== เพิ่ม LoRA Adapters ==========
print("🔧 เตรียม LoRA...")
model = FastLanguageModel.get_peft_model(
    model,
    r=16, # ลดเป็น 8 ถ้า VRAM ไม่พอ
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
)

# ========== โหลด Dataset ==========
print("📂 กำลังโหลดข้อมูล...")
dataset = load_dataset("json", data_files=DATASET_FILE, split="train")

# ฟอร์แมตข้อมูล
def format_prompts(examples):
    texts = []
    for instruction, input_text, output in zip(
        examples["instruction"], 
        examples["input"], 
        examples["output"]
    ):
        text = f"""### คำสั่ง:
{instruction}

### ข้อมูล:
{input_text}

### คำตอบ:
{output}"""
        texts.append(text)
    return {"text": texts}

dataset = dataset.map(format_prompts, batched=True)

# ========== ตั้งค่าการเทรน ==========
print("⚙️ ตั้งค่าการเทรน...")
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    args=TrainingArguments(
        per_device_train_batch_size=1, # ต้องเป็น 1 สำหรับ GTX 1060
        gradient_accumulation_steps=4, # ทำให้เหมือน batch=4
        warmup_steps=5,
        num_train_epochs=3, # เทรน 3 รอบ
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir=OUTPUT_DIR,
        save_steps=10, # บันทึกทุก 10 steps
        save_total_limit=3, # เก็บไว้ 3 checkpoint ล่าสุด
    ),
)

# ========== เริ่มเทรน ==========
print("🎯 เริ่มเทรน!")
print("=" * 50)
trainer.train()

# ========== บันทึกสมอง ==========
print("\n💾 กำลังบันทึกโมเดล...")
model.save_pretrained(f"{OUTPUT_DIR}/final_model")
tokenizer.save_pretrained(f"{OUTPUT_DIR}/final_model")

print("✅ เสร็จสิ้น! โมเดลถูกบันทึกที่:", f"{OUTPUT_DIR}/final_model")
print("\n📌 วิธีเทรนต่อ:")
print(f" python train_continue.py")