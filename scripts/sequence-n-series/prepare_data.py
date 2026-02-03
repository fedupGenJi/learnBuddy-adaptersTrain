import json
from pathlib import Path

INP = Path("data/sequence_series/raw/seq_series_train.jsonl")
OUT = Path("data/sequence_series/processed/train.jsonl")

OUT.parent.mkdir(parents=True, exist_ok=True)

def build_prompt(messages):
    parts = []
    for m in messages:
        parts.append(f"{m['role'].upper()}:\n{m['content']}")
    return "\n\n".join(parts).strip()

with INP.open("r", encoding="utf-8") as fin, OUT.open("w", encoding="utf-8") as fout:
    for line in fin:
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        prompt = build_prompt(obj["messages"])
        response = json.dumps(obj["response"], ensure_ascii=False)

        # one single training string
        text = f"{prompt}\n\nASSISTANT:\n{response}"

        fout.write(json.dumps({"text": text}, ensure_ascii=False) + "\n")

print(f"Saved processed data to: {OUT}")
