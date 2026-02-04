import argparse
import json
import random
import runpy
from pathlib import Path
from typing import Dict, List, Callable, Tuple

OUTPUT_PATH = Path("data/routing/raw/routing_raw.jsonl")

GEN_BASE = Path("generic-generators")

GENERATOR_FILES = {
    "algebraic_fractions": GEN_BASE / "algebraic-fractions.py",
    "arithmetic": GEN_BASE / "arithmetic.py",
    "growth_depreciation": GEN_BASE / "growth-n-depriciation.py",
    "probability": GEN_BASE / "probability.py",
    "quadratic_equations_a": GEN_BASE / "quadratic-equations.py",
    "quadratic_equations_b": GEN_BASE / "quadratic-equation-word.py",
    "sequence_series": GEN_BASE / "sequence-n-series.py",
}

LABEL_MAP = {
    "algebraic_fractions": "algebraic_fractions",
    "arithmetic": "arithmetic",
    "growth_depreciation": "growth_depreciation",
    "probability": "probability",
    "quadratic_equations_a": "quadratic_equations",
    "quadratic_equations_b": "quadratic_equations",
    "sequence_series": "sequence_series",
}

NONE_QUESTION_BANK = [
    "Explain photosynthesis in simple terms.",
    "Write a short email to my teacher asking for extra time.",
    "Who is the president of Nepal?",
    "Translate: 'Good morning' into Nepali.",
    "What is the capital of France?",
    "Summarize the plot of 'Harry Potter and the Philosopher's Stone'.",
    "Define democracy.",
    "What are the symptoms of common cold?",
    "Write a Python function to reverse a string.",
    "Explain the difference between speed and velocity.",
    "What is Newton's second law of motion?",
    "Give me a workout plan for beginners.",
    "What is the best smartphone to buy under $300?",
    "Describe the water cycle.",

    "Find the derivative of x^2 + 3x + 5.",
    "Evaluate the integral of 2x from 0 to 5.",
    "Find sin(30°) and cos(60°).",
    "Find the area of a circle of radius 7 cm.",
    "Prove that the angles in a triangle sum to 180 degrees.",
    "Solve the system of equations: x + y + z = 6, x - y = 2, 2z + y = 5.",
    "Compute log10(1000).",
]

def _write_jsonl(path: Path, rows: List[dict], fresh: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if fresh else "a"
    with path.open(mode, encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def _load_generators(py_path: Path) -> List[Callable[[], List[dict]]]:
    """
    Loads a script file via runpy and returns generator callables.

    Your generator scripts define functions like gen_...() that return [mcq_row, solve_row].
    We load the module globals and collect callables starting with 'gen_'.
    """
    g = runpy.run_path(str(py_path))
    gens = []
    for k, v in g.items():
        if callable(v) and k.startswith("gen_"):
            gens.append(v)
    if not gens:
        raise RuntimeError(f"No generator functions found in {py_path}")
    return gens

def _sample_question_from_gen(gen_fn: Callable[[], List[dict]]) -> Tuple[str, dict]:
    """
    Calls gen_fn() -> [mcq_row, solve_row] and extracts question text from the mcq row.
    """
    rows = gen_fn()
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("Generator returned empty rows")
    mcq = rows[0]

    q = mcq.get("response", {}).get("question")

    if not q and isinstance(mcq.get("messages"), list) and mcq["messages"]:
        q = mcq["messages"][-1].get("content")

    if not isinstance(q, str):
        raise RuntimeError("Could not extract question text")

    meta = {
        "chapter": mcq.get("chapter"),
        "task": mcq.get("task"),
        "difficulty": mcq.get("difficulty"),
    }
    return q.strip(), meta

def generate(samples_per_label: int, none_ratio: float, seed: int) -> List[dict]:
    random.seed(seed)
    all_rows: List[dict] = []

    for module_key, py_path in GENERATOR_FILES.items():
        label = LABEL_MAP[module_key]
        gens = _load_generators(py_path)

        for _ in range(samples_per_label):
            gen_fn = random.choice(gens)
            ok = False
            last_err = None

            for _retry in range(5):
                try:
                    q, meta = _sample_question_from_gen(gen_fn)
                    ok = True
                    break
                except Exception as e:
                    last_err = e
                    gen_fn = random.choice(gens)

            if not ok:
                raise RuntimeError(f"Failed generating question from {py_path}: {last_err}") from last_err

            all_rows.append({
                "question": q,
                "label": label,
                "source_chapter": module_key,
                "meta": meta,
            })

    num_none = int(round(len(all_rows) * none_ratio))
    for _ in range(num_none):
        q = random.choice(NONE_QUESTION_BANK)

        if random.random() < 0.25:
            q = q.replace("Find", "Compute").replace("What is", "Tell me").replace("Explain", "Briefly explain")

        all_rows.append({
            "question": q.strip(),
            "label": "none",
            "source_chapter": "none_bank",
            "meta": {"chapter": "none", "task": "route", "difficulty": 0},
        })

    random.shuffle(all_rows)
    return all_rows

def main():
    parser = argparse.ArgumentParser(description="Routing dataset raw generator (label selection)")
    parser.add_argument("--samples_per_label", type=int, default=600,
                        help="How many in-scope questions per label source-file.")
    parser.add_argument("--none_ratio", type=float, default=0.30,
                        help="Out-of-scope examples as a fraction of in-scope.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--fresh", action="store_true", help="Overwrite instead of appending.")
    args = parser.parse_args()

    rows = generate(args.samples_per_label, args.none_ratio, args.seed)
    _write_jsonl(OUTPUT_PATH, rows, fresh=args.fresh)
    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()