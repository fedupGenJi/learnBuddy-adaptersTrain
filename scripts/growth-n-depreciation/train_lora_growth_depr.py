import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# ------------------ Config ------------------
BASE = "Qwen/Qwen2.5-7B-Instruct"
TRAIN_FILE = "data/growth_depreciation/processed/train.jsonl"  # <- your Growth/Depreciation dataset
ADAPTER_OUT = "adapters/growth_depr_v1"

# 4-bit load (QLoRA style)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.float16,
)

# ------------------ Tokenizer ------------------
tokenizer = AutoTokenizer.from_pretrained(BASE, use_fast=True)

# ------------------ Model ------------------
model = AutoModelForCausalLM.from_pretrained(
    BASE,
    quantization_config=bnb_config,
    device_map={"": 0},       # <-- IMPORTANT for CPU/GPU mapping
    attn_implementation="sdpa",
)
model.config.use_cache = False  # important for training

# Prepare for k-bit training
model = prepare_model_for_kbit_training(model)

# ------------------ LoRA ------------------
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# ------------------ Dataset ------------------
ds = load_dataset("json", data_files=TRAIN_FILE, split="train")

MAX_LEN = 1024

def tokenize_fn(batch):
    out = tokenizer(
        batch["text"],  # make sure your growth/depr dataset has a "text" column
        truncation=True,
        max_length=MAX_LEN,
        padding=False,
    )
    out["labels"] = out["input_ids"].copy()
    return out

ds_tok = ds.map(tokenize_fn, batched=True, remove_columns=ds.column_names)

collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# ------------------ Training ------------------
args = TrainingArguments(
    output_dir="runs/growth_depr_v1",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=5,
    save_steps=50,
    save_total_limit=2,
    report_to="none",
    remove_unused_columns=False,
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=ds_tok,
    data_collator=collator,
)

trainer.train()

# ------------------ Save LoRA Adapter ------------------
model.save_pretrained(ADAPTER_OUT)
tokenizer.save_pretrained(ADAPTER_OUT)

print(f"Saved adapter: {ADAPTER_OUT}")