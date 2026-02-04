import argparse
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


def build_text(example, tokenizer):
    messages = example["messages"]
    label = example["response"]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    text = prompt + label.strip() + "\n"
    return {"text": text}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-7B-Instruct")
    parser.add_argument("--train", type=str, default="data/routing/prepared/train.jsonl")
    parser.add_argument("--valid", type=str, default="data/routing/prepared/valid.jsonl")
    parser.add_argument("--out", type=str, default="adapters/router_lora")
    parser.add_argument("--run_dir", type=str, default="runs/router_lora")

    parser.add_argument("--max_len", type=int, default=512)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--batch_size", type=int, default=1)
    parser.add_argument("--grad_accum", type=int, default=8)
    parser.add_argument("--logging_steps", type=int, default=20)
    parser.add_argument("--save_steps", type=int, default=250)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--grad_ckpt", action="store_true")

    # LoRA
    parser.add_argument("--lora_r", type=int, default=16)
    parser.add_argument("--lora_alpha", type=int, default=32)
    parser.add_argument("--lora_dropout", type=float, default=0.05)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU required for 7B QLoRA training.")

    # ---------------- Quantization ----------------
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,  
    )

    # ---------------- Load tokenizer & model ----------------
    tokenizer = AutoTokenizer.from_pretrained(args.model, use_fast=True)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        quantization_config=bnb_config,
        device_map={"": 0},  
        attn_implementation="sdpa",
    )
    model.config.use_cache = False

    if args.grad_ckpt:
        model.gradient_checkpointing_enable()

    # ---------------- Prepare for QLoRA ----------------
    model = prepare_model_for_kbit_training(model)

    lora_cfg = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
    )
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()

    # ---------------- Dataset ----------------
    ds = load_dataset("json", data_files={"train": args.train, "valid": args.valid})

    ds = ds.map(lambda ex: build_text(ex, tokenizer))

    def tokenize_fn(batch):
        out = tokenizer(
            batch["text"],
            truncation=True,
            max_length=args.max_len,
            padding=False,
        )
        out["labels"] = out["input_ids"].copy()
        return out

    ds_tok = ds.map(
        tokenize_fn,
        batched=True,
        remove_columns=ds["train"].column_names, 
    )

    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    # ---------------- Training ----------------
    train_args = TrainingArguments(
        output_dir=args.run_dir,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        num_train_epochs=args.epochs,
        learning_rate=args.lr,
        fp16=True,  
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        save_total_limit=2,
        eval_strategy="steps",
        eval_steps=args.save_steps,   
        report_to="none",
        remove_unused_columns=False,
        seed=args.seed,
    )

    trainer = Trainer(
        model=model,
        args=train_args,
        train_dataset=ds_tok["train"],
        eval_dataset=ds_tok["valid"],
        data_collator=collator,
    )

    trainer.train()

    model.save_pretrained(args.out)
    tokenizer.save_pretrained(args.out)
    print(f"Saved adapter: {args.out}")


if __name__ == "__main__":
    main()