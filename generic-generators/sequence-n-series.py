import json
import random
import math
import argparse
from pathlib import Path

OUTPUT_PATH = Path("data/sequence_series/raw/seq_series_train.jsonl")

SYSTEM_GEN = "You are an NEB Grade 10 Mathematics question generator. Output MUST be STRICT JSON only. No extra text."
SYSTEM_SOLVE = "You are an NEB Grade 10 Mathematics tutor. Output MUST be STRICT JSON only. No extra text."

# ------------------ Utilities ------------------

def write_jsonl(rows, fresh=False):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if fresh else "a"
    with open(OUTPUT_PATH, mode, encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def mcq_row(question, options, correct, explanation, distractors, difficulty):
    return {
        "chapter": "sequence_series",
        "task": "generate_mcq",
        "difficulty": difficulty,
        "messages": [
            {"role": "system", "content": SYSTEM_GEN},
            {"role": "user", "content":
                "Task: generate_mcq\n"
                "Chapter: Sequence and Series\n"
                f"Difficulty: {difficulty}\n"
                "Rules:\n"
                "- Create ONE NEB-style word problem.\n"
                "- Provide 4 options (A,B,C,D).\n"
                "- Exactly ONE option is correct.\n"
                "- The 3 wrong options must be based on common student mistakes.\n"
                "- Include a short answer_explanation.\n"
                "- Include distractor_rationales for wrong options with mistake tag and why.\n"
                "Return JSON only with keys: question, options, correct_option, answer_explanation, distractor_rationales, meta."
            }
        ],
        "response": {
            "question": question,
            "options": options,
            "correct_option": correct,
            "answer_explanation": explanation,
            "distractor_rationales": distractors,
            "meta": {"chapter": "sequence_series", "difficulty": difficulty}
        }
    }

def solve_row(question, given, steps, final_answer, difficulty):
    return {
        "chapter": "sequence_series",
        "task": "solve",
        "difficulty": difficulty,
        "messages": [
            {"role": "system", "content": SYSTEM_SOLVE},
            {"role": "user", "content": f"Solve with full steps:\n{question}"}
        ],
        "response": {
            "given": given,
            "to_find": "Required value",
            "steps": steps,
            "final_answer": final_answer
        }
    }

def fmt(x):
    return int(round(x))


# ------------------ Arithmetic Series ------------------

def gen_arithmetic_sum():
    a = random.choice([2, 3, 5, 10])
    d = random.choice([2, 3, 4, 5])
    n = random.choice([5, 8, 10, 12])
    difficulty = random.choice([1, 2])

    tn = a + (n - 1) * d
    Sn = n / 2 * (a + tn)

    correct_val = fmt(Sn)

    question = f"Find the sum of first {n} terms of an arithmetic series with first term {a} and common difference {d}."

    wrong1 = fmt(n * (a + tn))              # forgot /2
    wrong2 = fmt(n / 2 * (2 * a + n * d))   # used n instead of (n-1)
    wrong3 = fmt(Sn + d)

    options = {
        "A": str(wrong1),
        "B": str(wrong2),
        "C": str(correct_val),
        "D": str(wrong3)
    }

    distractors = {
        "A": {"tag": "formula_miss_half", "why": "Forgot to divide by 2 in Sn formula."},
        "B": {"tag": "wrong_n_minus_1", "why": "Used n instead of (n−1) in formula."},
        "D": {"tag": "arithmetic_error", "why": "Minor calculation mistake."}
    }

    steps = [
        "tn = a + (n − 1)d",
        f"tn = {a} + ({n}-1)×{d} = {tn}",
        "Sn = n/2 (a + tn)",
        f"Sn = {n}/2 × ({a} + {tn}) = {correct_val}"
    ]

    mcq = mcq_row(question, options, "C",
                  "Use Sn = n/2 (a + tn) formula.",
                  distractors, difficulty)

    solve = solve_row(question, f"a={a}, d={d}, n={n}", steps, f"Sn = {correct_val}", difficulty)

    return [mcq, solve]


def gen_arithmetic_tn():
    a = random.choice([1, 3, 5, 7])
    d = random.choice([2, 4, 6])
    n = random.choice([6, 9, 12])
    difficulty = 2

    tn = a + (n - 1) * d
    correct_val = tn

    question = f"Find the {n}th term of an arithmetic sequence whose first term is {a} and common difference is {d}."

    wrong1 = a + n * d
    wrong2 = a * n
    wrong3 = tn - d

    options = {
        "A": str(wrong1),
        "B": str(correct_val),
        "C": str(wrong2),
        "D": str(wrong3)
    }

    distractors = {
        "A": {"tag": "used_n_instead_n_minus_1", "why": "Used a + nd instead of a + (n−1)d."},
        "C": {"tag": "multiplication_error", "why": "Multiplied instead of adding difference."},
        "D": {"tag": "off_by_one", "why": "Subtracted one difference extra."}
    }

    steps = [
        "tn = a + (n − 1)d",
        f"tn = {a} + ({n}-1)×{d} = {correct_val}"
    ]

    mcq = mcq_row(question, options, "B",
                  "Use tn = a + (n−1)d formula.",
                  distractors, difficulty)

    solve = solve_row(question, f"a={a}, d={d}, n={n}", steps, f"tn = {correct_val}", difficulty)

    return [mcq, solve]


# ------------------ Geometric Series ------------------

def gen_geometric_sum():
    a = random.choice([2, 3, 5])
    r = random.choice([2, 3, 0.5])
    n = random.choice([4, 5, 6])
    difficulty = 3

    if r > 1:
        Sn = a * (r**n - 1) / (r - 1)
    else:
        Sn = a * (1 - r**n) / (1 - r)

    correct_val = fmt(Sn)

    question = f"Find the sum of first {n} terms of a geometric series with first term {a} and common ratio {r}."

    wrong1 = fmt(a * (r**n))
    wrong2 = fmt(a * (r**n - 1))
    wrong3 = fmt(Sn + a)

    options = {
        "A": str(wrong1),
        "B": str(wrong2),
        "C": str(correct_val),
        "D": str(wrong3)
    }

    distractors = {
        "A": {"tag": "found_tn", "why": "Calculated nth term instead of sum."},
        "B": {"tag": "missed_denominator", "why": "Forgot to divide by (r−1) or (1−r)."},
        "D": {"tag": "arithmetic_error", "why": "Minor calculation mistake."}
    }

    steps = [
        "Use geometric series sum formula.",
        f"Sn = {correct_val}"
    ]

    mcq = mcq_row(question, options, "C",
                  "Apply geometric series sum formula correctly.",
                  distractors, difficulty)

    solve = solve_row(question, f"a={a}, r={r}, n={n}", steps, f"Sn = {correct_val}", difficulty)

    return [mcq, solve]


def gen_geometric_tn():
    a = random.choice([2, 3, 5])
    r = random.choice([2, 3])
    n = random.choice([4, 6, 8])
    difficulty = 2

    tn = a * (r ** (n - 1))
    correct_val = fmt(tn)

    question = f"Find the {n}th term of a geometric sequence with first term {a} and common ratio {r}."

    wrong1 = a * (r ** n)
    wrong2 = a + (n - 1) * r
    wrong3 = tn // r

    options = {
        "A": str(wrong1),
        "B": str(correct_val),
        "C": str(wrong2),
        "D": str(wrong3)
    }

    distractors = {
        "A": {"tag": "power_error", "why": "Used r^n instead of r^(n−1)."},
        "C": {"tag": "used_arithmetic_formula", "why": "Applied arithmetic formula wrongly."},
        "D": {"tag": "off_by_one", "why": "Divided by r once too many."}
    }

    steps = [
        "tn = a × r^(n − 1)",
        f"tn = {a} × {r}^({n}-1) = {correct_val}"
    ]

    mcq = mcq_row(question, options, "B",
                  "Use tn = ar^(n−1) formula.",
                  distractors, difficulty)

    solve = solve_row(question, f"a={a}, r={r}, n={n}", steps, f"tn = {correct_val}", difficulty)

    return [mcq, solve]


# ------------------ Main ------------------

def main():
    parser = argparse.ArgumentParser(description="Sequence and Series dataset generator")

    parser.add_argument("--samples", type=int, default=50)
    parser.add_argument("--fresh", action="store_true")

    args = parser.parse_args()

    generators = [
        gen_arithmetic_sum,
        gen_arithmetic_tn,
        gen_geometric_sum,
        gen_geometric_tn
    ]

    rows = []

    for _ in range(args.samples):
        gen = random.choice(generators)
        rows.extend(gen())

    write_jsonl(rows, fresh=args.fresh)

    mode_text = "overwritten" if args.fresh else "appended to"
    print(f"Generated {len(rows)} rows ({args.samples} questions) and {mode_text} {OUTPUT_PATH}")


if __name__ == "__main__":
    main()