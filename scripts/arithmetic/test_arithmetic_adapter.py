import json
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

BASE = "Qwen/Qwen2.5-7B-Instruct"
ADAPTER = "adapters/arithmetic_v1"

def extract_json(text: str):
    """
    Tries to extract the first JSON object from model output.
    Useful if the model accidentally adds extra text.
    """
    # Find first '{' and last '}' that could form JSON
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None, "Could not find JSON braces in output."

    candidate = text[start:end+1].strip()

    # Try parse
    try:
        return json.loads(candidate), None
    except Exception as e:
        return candidate, f"JSON parse error: {e}"

def run_generation(model, tokenizer, prompt: str, max_new_tokens: int = 350):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )
    return tokenizer.decode(out[0], skip_special_tokens=True)

def main():
    print("Loading base model + adapter...")

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )

    tokenizer = AutoTokenizer.from_pretrained(BASE, use_fast=True)

    base_model = AutoModelForCausalLM.from_pretrained(
        BASE,
        quantization_config=bnb_config,
        device_map={"": 0},          # important on Windows/accelerate stability
        attn_implementation="sdpa",
    )
    base_model.config.use_cache = False

    model = PeftModel.from_pretrained(base_model, ADAPTER)
    model.eval()

    # -----------------------
    # Test 1: generate_mcq
    # -----------------------
    prompt_mcq = """SYSTEM:
You are an NEB Grade 10 Mathematics question generator for the chapter Arithmetic.
Output MUST be STRICT JSON only. No markdown, no explanation outside JSON.

USER:
Task: generate_mcq
Chapter: Arithmetic
Difficulty: 2
Rules:
- Create ONE NEB-style arithmetic word problem.
- Provide 4 options (A,B,C,D).
- Exactly ONE option is correct.
- The 3 wrong options must be based on common student mistakes.
- Include distractor mistake tags and short reasons.
Return JSON ONLY with keys:
question, options, correct_option, answer_explanation, distractor_rationales, meta
"""

    print("\n===== OUTPUT: generate_mcq =====")
    raw_mcq = run_generation(model, tokenizer, prompt_mcq, max_new_tokens=350)
    print(raw_mcq)

    parsed_mcq, err = extract_json(raw_mcq)
    if err:
        print("\n[!] Could not parse strict JSON:", err)
        if isinstance(parsed_mcq, str):
            print("Extracted candidate JSON string:\n", parsed_mcq)
    else:
        print("\n[OK] Parsed JSON object:")
        print(json.dumps(parsed_mcq, indent=2, ensure_ascii=False))

    # -----------------------
    # Test 2: solve
    # -----------------------
    sample_q = "Find the simple interest on Rs 8,000 at 10% per annum for 2 years."

    prompt_solve = f"""SYSTEM:
You are an NEB Grade 10 Mathematics tutor for the chapter Arithmetic.
Output MUST be STRICT JSON only. No markdown, no extra text.

USER:
Task: solve
Show full steps and final answer in JSON.
Question: {sample_q}

Return JSON ONLY with keys:
given, to_find, steps, final_answer
"""

    print("\n===== OUTPUT: solve =====")
    raw_solve = run_generation(model, tokenizer, prompt_solve, max_new_tokens=450)
    print(raw_solve)

    parsed_solve, err = extract_json(raw_solve)
    if err:
        print("\n[!] Could not parse strict JSON:", err)
        if isinstance(parsed_solve, str):
            print("Extracted candidate JSON string:\n", parsed_solve)
    else:
        print("\n[OK] Parsed JSON object:")
        print(json.dumps(parsed_solve, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
