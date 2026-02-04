import argparse
import json
import random
from pathlib import Path
from typing import List, Dict

RAW_PATH = Path("data/routing/raw/routing_raw.jsonl")
OUT_TRAIN = Path("data/routing/prepared/train.jsonl")
OUT_VALID = Path("data/routing/prepared/valid.jsonl")

SYSTEM_ROUTER = (
    "You are a router for NEB Grade 10 math chapter adapters.\n"
    "Task: Given a user question, choose exactly ONE label from the allowed list.\n"
    "Return ONLY the label text, in lowercase, with no extra words."
)

def write_jsonl(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def load_raw(path: Path) -> List[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows

def make_prompt(question: str, labels: List[str]) -> List[Dict[str, str]]:
    label_str = ", ".join(labels)
    user = (
        f"Allowed labels: {label_str}\n"
        "Question:\n"
        f"{question}\n\n"
        "Answer with exactly one label."
    )
    return [
        {"role": "system", "content": SYSTEM_ROUTER},
        {"role": "user", "content": user},
    ]

def main():
    parser = argparse.ArgumentParser(description="Prepare routing dataset (chat-style) for SFT.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--valid_ratio", type=float, default=0.05)
    parser.add_argument("--max_rows", type=int, default=0, help="If >0, truncate dataset for quick tests.")
    args = parser.parse_args()

    raw = load_raw(RAW_PATH)
    if args.max_rows and args.max_rows > 0:
        raw = raw[: args.max_rows]

    labels = sorted({r["label"] for r in raw})
    if "none" in labels:
        labels = [l for l in labels if l != "none"] + ["none"]  

    random.seed(args.seed)
    random.shuffle(raw)

    prepared = []
    for r in raw:
        question = r["question"].strip()
        label = r["label"].strip().lower()
        prepared.append({
            "messages": make_prompt(question, labels),
            "response": label,
            "meta": {
                "label": label,
                "source_chapter": r.get("source_chapter"),
                "difficulty": (r.get("meta") or {}).get("difficulty"),
            }
        })

    n_valid = max(1, int(round(len(prepared) * args.valid_ratio)))
    valid = prepared[:n_valid]
    train = prepared[n_valid:]

    write_jsonl(OUT_TRAIN, train)
    write_jsonl(OUT_VALID, valid)

    print(f"Labels: {labels}")
    print(f"Train: {len(train)} → {OUT_TRAIN}")
    print(f"Valid: {len(valid)} → {OUT_VALID}")

if __name__ == "__main__":
    main()