import json
import random
import math
import argparse
from pathlib import Path

OUTPUT_PATH = Path("data/quadratic/raw/quadratic_train.jsonl")

SYSTEM_GEN = "You are an NEB Grade 10 Mathematics question generator. Output MUST be STRICT JSON only."
SYSTEM_SOLVE = "You are an NEB Grade 10 Mathematics tutor. Output MUST be STRICT JSON only."

# --------------------------------------------------
# Utilities
# --------------------------------------------------

def write_jsonl(rows, fresh=False):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if fresh else "a"
    with open(OUTPUT_PATH, mode, encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def mcq_row(question, options, correct, explanation, distractors, difficulty):
    return {
        "chapter": "quadratic_equations",
        "task": "generate_mcq",
        "difficulty": difficulty,
        "messages": [
            {"role": "system", "content": SYSTEM_GEN},
            {"role": "user", "content":
                "Task: generate_mcq\n"
                "Chapter: Quadratic Equations\n"
                f"Difficulty: {difficulty}\n"
                "Rules:\n"
                "- One NEB-style question\n"
                "- 4 options (A,B,C,D)\n"
                "- Exactly one correct\n"
                "- Distractors must be common student mistakes\n"
                "- Return STRICT JSON only"
            }
        ],
        "response": {
            "question": question,
            "options": options,
            "correct_option": correct,
            "answer_explanation": explanation,
            "distractor_rationales": distractors,
            "meta": {"chapter": "quadratic_equations", "difficulty": difficulty}
        }
    }


def solve_row(question, given, steps, final_answer, difficulty):
    return {
        "chapter": "quadratic_equations",
        "task": "solve",
        "difficulty": difficulty,
        "messages": [
            {"role": "system", "content": SYSTEM_SOLVE},
            {"role": "user", "content": f"Solve step by step:\n{question}"}
        ],
        "response": {
            "given": given,
            "to_find": "Roots",
            "steps": steps,
            "final_answer": final_answer
        }
    }

# --------------------------------------------------
# 1. x² + bx + c = 0 (Simple factorization)
# --------------------------------------------------

def gen_simple_factorization():
    difficulty = 1
    r1, r2 = random.sample(range(1, 10), 2)
    b, c = r1 + r2, r1 * r2

    question = f"Solve: x² + {b}x + {c} = 0"
    correct = f"x = {-r1}, {-r2}"

    options = {
        "A": f"x = {r1}, {r2}",
        "B": f"x = {-b}, {-c}",
        "C": correct,
        "D": f"x = {b}, {c}"
    }

    distractors = {
        "A": {"tag": "sign_error"},
        "B": {"tag": "coefficient_as_root"},
        "D": {"tag": "concept_error"}
    }

    steps = [
        f"(x + {r1})(x + {r2}) = 0",
        f"x = -{r1}, -{r2}"
    ]

    return [
        mcq_row(question, options, "C",
                "Factorize and equate each factor to zero.",
                distractors, difficulty),
        solve_row(question, f"b={b}, c={c}", steps, correct, difficulty)
    ]

# --------------------------------------------------
# 2. ax² + bx + c = 0
# --------------------------------------------------

def gen_general_factorization():
    difficulty = 2
    a = random.choice([2, 3])
    r1, r2 = random.sample(range(1, 7), 2)

    b = a * (r1 + r2)
    c = a * r1 * r2

    question = f"Solve: {a}x² + {b}x + {c} = 0"
    correct = f"x = {-r1}, {-r2}"

    options = {
        "A": f"x = {r1}, {r2}",
        "B": f"x = {-b}, {-c}",
        "C": correct,
        "D": f"x = {-r1}, {r2}"
    }

    distractors = {
        "A": {"tag": "sign_error"},
        "B": {"tag": "coefficient_confusion"},
        "D": {"tag": "partial_root_error"}
    }

    steps = [
        "Factor by grouping",
        f"{a}(x + {r1})(x + {r2}) = 0",
        f"x = -{r1}, -{r2}"
    ]

    return [
        mcq_row(question, options, "C",
                "Use grouping to factorize.",
                distractors, difficulty),
        solve_row(question, f"a={a}, b={b}, c={c}", steps, correct, difficulty)
    ]

# --------------------------------------------------
# 3. Completing the square
# --------------------------------------------------

def gen_completing_square():
    difficulty = 2
    r1, r2 = random.sample(range(1, 9), 2)
    b, c = r1 + r2, r1 * r2

    question = f"Solve by completing the square: x² - {b}x + {c} = 0"
    correct = f"x = {r1}, {r2}"

    options = {
        "A": f"x = {-r1}, {-r2}",
        "B": f"x = {r1}, {-r2}",
        "C": correct,
        "D": f"x = {b}, {c}"
    }

    distractors = {
        "A": {"tag": "sign_error"},
        "B": {"tag": "one_root_only"},
        "D": {"tag": "concept_error"}
    }

    steps = [
        "Move constant to RHS",
        "Add (b/2)² to both sides",
        "Take square root",
        f"x = {r1}, {r2}"
    ]

    return [
        mcq_row(question, options, "C",
                "Complete the square and solve.",
                distractors, difficulty),
        solve_row(question, f"b={b}, c={c}", steps, correct, difficulty)
    ]

# --------------------------------------------------
# 4. Quadratic formula
# --------------------------------------------------

def gen_quadratic_formula():
    difficulty = 2
    a = random.choice([1, 2])
    b = random.randint(-8, 8)
    c = random.randint(-6, 6)

    d = b*b - 4*a*c
    if d <= 0:
        return gen_quadratic_formula()

    r1 = round((-b + math.sqrt(d)) / (2*a), 2)
    r2 = round((-b - math.sqrt(d)) / (2*a), 2)

    question = f"Solve using quadratic formula: {a}x² + {b}x + {c} = 0"
    correct = f"x = {r1}, {r2}"

    options = {
        "A": f"x = {-r1}, {-r2}",
        "B": f"x = {r2}, {r1}",
        "C": correct,
        "D": f"x = {b}, {c}"
    }

    distractors = {
        "A": {"tag": "sign_error"},
        "B": {"tag": "ordering_confusion"},
        "D": {"tag": "coefficient_as_root"}
    }

    steps = [
        "Use x = (-b ± √(b² - 4ac)) / 2a",
        f"D = {d}",
        f"x = {r1}, {r2}"
    ]

    return [
        mcq_row(question, options, "C",
                "Apply quadratic formula correctly.",
                distractors, difficulty),
        solve_row(question, f"a={a}, b={b}, c={c}", steps, correct, difficulty)
    ]

# --------------------------------------------------
# 5. Nature of roots (Discriminant)
# --------------------------------------------------

def gen_nature_of_roots():
    difficulty = 1
    a = random.choice([1, 2])
    b = random.randint(2, 10)
    c = random.randint(1, 10)

    d = b*b - 4*a*c

    if d > 0:
        nature = "two distinct real roots"
    elif d == 0:
        nature = "two equal real roots"
    else:
        nature = "no real roots"

    question = f"Find the nature of roots of {a}x² + {b}x + {c} = 0"

    options = {
        "A": "Two equal real roots",
        "B": "Two distinct real roots",
        "C": "No real roots",
        "D": "One real root"
    }

    correct_map = {
        "two equal real roots": "A",
        "two distinct real roots": "B",
        "no real roots": "C"
    }

    steps = [
        "Compute discriminant D = b² − 4ac",
        f"D = {d}",
        f"Nature: {nature}"
    ]

    return [
        mcq_row(question, options, correct_map[nature],
                "Use discriminant to determine nature of roots.",
                {}, difficulty),
        solve_row(question, f"a={a}, b={b}, c={c}", steps, nature, difficulty)
    ]

# --------------------------------------------------
# 6. Form equation from roots
# --------------------------------------------------

def gen_form_equation():
    difficulty = 2
    r1, r2 = random.sample(range(1, 10), 2)

    question = f"Form a quadratic equation whose roots are {r1} and {r2}."
    correct_eq = f"x² - {(r1+r2)}x + {r1*r2} = 0"

    options = {
        "A": f"x² + {(r1+r2)}x + {r1*r2} = 0",
        "B": f"x² - {(r1*r2)}x + {(r1+r2)} = 0",
        "C": correct_eq,
        "D": f"x² + {(r1*r2)}x - {(r1+r2)} = 0"
    }

    distractors = {
        "A": {"tag": "sign_error"},
        "B": {"tag": "sum_product_swapped"},
        "D": {"tag": "wrong_structure"}
    }

    steps = [
        "Sum of roots = r₁ + r₂",
        "Product of roots = r₁r₂",
        "Equation: x² − (sum)x + product = 0"
    ]

    mcq = mcq_row(question, options, "C",
                  "Use x² − (sum)x + product = 0",
                  distractors, difficulty)

    solve = solve_row(question, f"Roots = {r1}, {r2}", steps, correct_eq, difficulty)

    return [mcq, solve]

# --------------------------------------------------
# 7. Perfect square equation x² = a²
# --------------------------------------------------

def gen_perfect_square():
    difficulty = 1
    a = random.randint(2, 10)

    question = f"Solve: x² = {a*a}"
    correct = f"x = ±{a}"

    options = {
        "A": f"x = {a}",
        "B": f"x = -{a}",
        "C": correct,
        "D": f"x = {a*a}"
    }

    distractors = {
        "A": {"tag": "missed_negative_root"},
        "B": {"tag": "missed_positive_root"},
        "D": {"tag": "square_confusion"}
    }

    steps = [
        f"x² = {a*a}",
        f"x = ±{a}"
    ]

    return [
        mcq_row(question, options, "C",
                "Square root gives two solutions.",
                distractors, difficulty),
        solve_row(question, f"a={a}", steps, correct, difficulty)
    ]

# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Quadratic Equation Dataset Generator (7 Types)")
    parser.add_argument("--samples", type=int, default=100)
    parser.add_argument("--fresh", action="store_true")
    args = parser.parse_args()

    generators = [
        gen_simple_factorization,
        gen_general_factorization,
        gen_completing_square,
        gen_quadratic_formula,
        gen_nature_of_roots,
        gen_form_equation,
        gen_perfect_square
    ]

    rows = []
    for _ in range(args.samples):
        rows.extend(random.choice(generators)())

    write_jsonl(rows, fresh=args.fresh)
    print(f"Generated {len(rows)} rows → {OUTPUT_PATH}")

if __name__ == "__main__":
    main()