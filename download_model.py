from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"

print("Downloading tokenizer...")
AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)

print("Downloading model weights (this is large)...")
AutoModelForCausalLM.from_pretrained(MODEL_ID)

print("DONE. Model is now in your Hugging Face cache.")
