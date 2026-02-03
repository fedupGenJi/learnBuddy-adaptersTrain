# 📘 Math Adapters with LoRA (Qwen2.5-7B)

This repository contains a modular pipeline for training **LoRA adapters** on top of  
**Qwen/Qwen2.5-7B-Instruct** for different mathematics domains such as arithmetic, quadratic equations, probability, growth & depreciation, and sequences & series.

The project is designed to:
- Generate domain-specific math datasets
- Prepare and preprocess data per chapter
- Train LoRA adapters independently per topic
- Run lightweight test and inference scripts

All training was performed using **Python 3.11** with **CUDA 12.1**.

---

## Base Model

- **Model**: `Qwen/Qwen2.5-7B-Instruct`
- **Fine-tuning method**: LoRA (via `peft`)
- **Frameworks**: Hugging Face Transformers, TRL

---

## Some Tips
- Disable the lower end GPU on computers having multiple GPUs. 
- Use manual labour to get vast variety of questions with unique english script.

---

## 🔄 Workflow Overview

---
### Initialisation
- Download base model by running download_model.py
- Check for cuda availability
- Check the base model operation by running scripts/quick_infer.py

---

### Dataset Generation
- Synthetic math datasets are created using scripts in `generic-generators/`
- Additional manual curation may be applied
- Final datasets are stored under `data/<chapter_name>/`

---

### Data Preparation
Each chapter has a `prepare_data.py` script that:
- Cleans and formats raw data
- Converts it into instruction-style prompt/response pairs
- Saves training-ready datasets (e.g. JSON / JSONL)

---

## LoRA Training

Each chapter has its own dedicated LoRA training script.

---

## LoRA Testing

Each chapter has its own dedicated LoRA testing script.

---