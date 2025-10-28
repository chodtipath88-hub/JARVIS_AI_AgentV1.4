"""
🔄 เทรนต่อจากโมเดลเดิม
"""

from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
import torch

# ========== โหลดโมเดลเดิม ==========
print("📥 กำลังโหลดโมเดลที่เทรนไว้แล้ว...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="./ai_brain/final_model", # โฟลเดอร์ที่บันทึกไว้
    max_seq_length=512,
    dtype=None,
    load_in_4bit=True,
)

# เตรียมโมเดลสำหรับเทรนต่อ
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
)

# โหลดข้อมูลใหม่ (หรือข้อมูลเดิม)
dataset = load_dataset("json", data_files="my_data_new.json", split="train")

def format_prompts(examples):
    texts = []
    for instruction, input_text, output in zip(
        examples["instruction"], examples["input"], examples["output"]
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

# เทรนต่อ
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=512,
    args=TrainingArguments(
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        num_train_epochs=2, # เทรนเพิ่มอีก 2 รอบ
        learning_rate=1e-4, # ลด learning rate ลงเล็กน้อย
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1,
        optim="adamw_8bit",
        output_dir="./ai_brain_v2",
        save_steps=10,
    ),
)

print("🎯 เริ่มเทรนต่อ!")
trainer.train()

# บันทึกเวอร์ชันใหม่
model.save_pretrained("./ai_brain_v2/final_model")
tokenizer.save_pretrained("./ai_brain_v2/final_model")
print("✅ เสร็จสิ้น! เวอร์ชันใหม่: ./ai_brain_v2/final_model")