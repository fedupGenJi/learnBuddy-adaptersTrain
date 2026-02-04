import argparse
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

VALID_LABELS = [
    "algebraic_fractions",
    "arithmetic",
    "growth_depreciation",
    "probability",
    "quadratic_equations",
    "sequence_series",
    "none",
]

def build_messages(question: str):
    system = (
        "You are a routing classifier. "
        "Given a user's question, output ONLY the best route label from this set:\n"
        + ", ".join(VALID_LABELS)
        + "\n\nRules:\n"
        "- Output exactly one label.\n"
        "- No extra words, no punctuation, no explanation.\n"
    )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": question.strip()},
    ]

def extract_label(text: str) -> str:
    t = text.strip().lower()
    t = re.sub(r"\s+", " ", t)
    for lab in VALID_LABELS:
        if t == lab:
            return lab
        
    for lab in VALID_LABELS:
        if lab in t:
            return lab
    return "unknown"

@torch.inference_mode()
def route(model, tokenizer, question: str, max_new_tokens: int, temperature: float):
    messages = build_messages(question)
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    gen = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=(temperature > 0),
        temperature=temperature if temperature > 0 else None,
        top_p=1.0,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )

    new_tokens = gen[0][inputs["input_ids"].shape[-1]:]
    raw = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
    label = extract_label(raw)
    return label, raw, prompt

def load_model(base_model: str, adapter_path: str, device: str):
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )

    tokenizer = AutoTokenizer.from_pretrained(base_model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=bnb_config,
        device_map={"": 0} if device == "cuda" else None,
        attn_implementation="sdpa",
    )
    model = PeftModel.from_pretrained(model, adapter_path)
    model.eval()
    return model, tokenizer


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base_model", type=str, default="Qwen/Qwen2.5-7B-Instruct")
    p.add_argument("--adapter", type=str, required=True)
    p.add_argument("--device", type=str, default="cuda", choices=["cuda", "cpu"])
    p.add_argument("--max_new_tokens", type=int, default=6)
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--show_prompt", action="store_true")
    p.add_argument("--show_raw", action="store_true")
    args = p.parse_args()

    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA not available but --device=cuda was set.")

    model, tokenizer = load_model(args.base_model, args.adapter, args.device)

    print("Router ready. Type a question and press Enter. Type 'quit' to exit.\n")

    while True:
        q = input("question> ").strip()
        if not q:
            continue
        if q.lower() in {"quit", "exit", "q"}:
            break

        label, raw, prompt = route(
            model, tokenizer, q,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
        )

        print(f"label: {label}")
        if args.show_raw:
            print(f"raw: {raw}")
        if args.show_prompt:
            print("\n--- prompt sent to model ---")
            print(prompt)
            print("--- end prompt ---\n")


if __name__ == "__main__":
    main()