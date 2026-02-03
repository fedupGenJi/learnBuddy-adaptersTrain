import json
import random
import argparse
from pathlib import Path

OUTPUT_PATH = Path("data/algebraic_fractions/raw/algebraic_fractions.jsonl")

SYSTEM_GEN = "You are an NEB Grade 10 Mathematics question generator. Output MUST be STRICT JSON only. No extra text."
SYSTEM_SOLVE = "You are an NEB Grade 10 Mathematics tutor. Output MUST be STRICT JSON only. No extra text."

# ---------------- Utilities ----------------

def write_jsonl(rows, fresh=False):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if fresh else "a"
    with open(OUTPUT_PATH, mode, encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def mcq_row(question, options, correct, explanation, distractors, difficulty):
    return {
        "chapter": "algebraic_fractions",
        "task": "generate_mcq",
        "difficulty": difficulty,
        "messages": [
            {"role": "system", "content": SYSTEM_GEN},
            {"role": "user", "content":
                "Task: generate_mcq\n"
                "Chapter: Algebraic Fractions\n"
                f"Difficulty: {difficulty}\n"
                "Rules:\n"
                "- Create ONE NEB-style question.\n"
                "- Provide 4 options.\n"
                "- Exactly ONE correct.\n"
                "- Use common student mistakes.\n"
                "- Include explanation and distractor rationales.\n"
            }
        ],
        "response": {
            "question": question,
            "options": options,
            "correct_option": correct,
            "answer_explanation": explanation,
            "distractor_rationales": distractors,
            "meta": {"chapter": "algebraic_fractions", "difficulty": difficulty}
        }
    }

def solve_row(question, given, steps, final_answer, difficulty):
    return {
        "chapter": "algebraic_fractions",
        "task": "solve",
        "difficulty": difficulty,
        "messages": [
            {"role": "system", "content": SYSTEM_SOLVE},
            {"role": "user", "content": f"Solve with full steps:\n{question}"}
        ],
        "response": {
            "given": given,
            "to_find": "Simplified form",
            "steps": steps,
            "final_answer": final_answer
        }
    }

def gen_diff_squares_fraction():
    a = random.choice([2, 3, 4, 5])
    difficulty = 3

    question = f"Simplify: (x^2 - {a*a}) / (x - {a})"
    correct = f"x + {a}"

    wrong1 = f"x - {a}"
    wrong2 = f"x^2 + {a*a}"
    wrong3 = "1"

    options = {"A": wrong1, "B": wrong2, "C": correct, "D": wrong3}

    distractors = {
        "A": {"tag": "wrong_factor", "why": "Used (x−a) instead of the remaining factor."},
        "B": {"tag": "no_factorization", "why": "Did not apply identity a²−b² = (a−b)(a+b)."},
        "D": {"tag": "cancelled_whole", "why": "Cancelled the full expression incorrectly."}
    }

    steps = [
        f"x² − {a*a} = (x − {a})(x + {a})",
        f"= (x − {a})(x + {a}) / (x − {a})",
        "Cancel (x − a)",
        f"= x + {a}"
    ]

    mcq = mcq_row(
        question, options, "C",
        "Use identity a² − b² = (a − b)(a + b) then cancel the common factor.",
        distractors, difficulty
    )
    solve = solve_row(question, f"a={a}", steps, correct, difficulty)
    return [mcq, solve]

def gen_perfect_square_fraction():
    a = random.choice([2, 3, 4])
    difficulty = 3

    question = f"Simplify: (x^2 + {2*a}x + {a*a}) / (x + {a})"
    correct = f"x + {a}"

    wrong1 = f"x - {a}"
    wrong2 = f"x^2 + {a*a}"
    wrong3 = "x"

    options = {"A": wrong1, "B": wrong2, "C": correct, "D": wrong3}

    distractors = {
        "A": {"tag": "sign_error", "why": "Wrong sign while factoring the trinomial."},
        "B": {"tag": "no_factorization", "why": "Did not use (x+a)² identity."},
        "D": {"tag": "partial_cancel", "why": "Cancelled only x instead of the whole common factor."}
    }

    steps = [
        f"x² + {2*a}x + {a*a} = (x + {a})²",
        f"= (x + {a})(x + {a}) / (x + {a})",
        "Cancel common factor",
        f"= x + {a}"
    ]

    mcq = mcq_row(
        question, options, "C",
        "Rewrite numerator as (x+a)² and cancel the common factor (x+a).",
        distractors, difficulty
    )
    solve = solve_row(question, f"a={a}", steps, correct, difficulty)
    return [mcq, solve]

def gen_fraction_multiplication():
    a = random.choice([2, 3, 4])
    b = random.choice([2, 3, 4])
    difficulty = 4

    question = f"Simplify: (x / {a}) × ({b} / x)"
    correct = f"{b}/{a}"

    wrong1 = f"{b}x/{a}"
    wrong2 = f"{a}/{b}"
    wrong3 = f"{b}/{a}x"

    options = {"A": wrong1, "B": wrong2, "C": correct, "D": wrong3}

    distractors = {
        "A": {"tag": "no_cancel", "why": "Did not cancel x."},
        "B": {"tag": "reciprocal_error", "why": "Flipped the result incorrectly."},
        "D": {"tag": "partial_cancel", "why": "Cancelled incorrectly and left x in denominator."}
    }

    steps = [
        f"(x/{a}) × ({b}/x)",
        f"= {b}x / {a}x",
        "Cancel x",
        f"= {b}/{a}"
    ]

    mcq = mcq_row(
        question, options, "C",
        "Multiply numerators and denominators, then cancel common factors.",
        distractors, difficulty
    )
    solve = solve_row(question, f"a={a}, b={b}", steps, correct, difficulty)
    return [mcq, solve]



def gen_diff_squares_two_variable():
    # (x^2 - y^2)/(x+y) -> x-y
    difficulty = 4
    question = "Simplify: (x^2 - y^2) / (x + y)"
    correct = "x - y"

    options = {
        "A": "x + y",
        "B": "x^2 - y^2",
        "C": correct,
        "D": "1"
    }

    distractors = {
        "A": {"tag": "wrong_factor", "why": "Picked the cancelled factor instead of the remaining one."},
        "B": {"tag": "no_factorization", "why": "Did not factorize x²−y²."},
        "D": {"tag": "cancelled_whole", "why": "Cancelled incorrectly to 1."}
    }

    steps = [
        "x² − y² = (x − y)(x + y)",
        "= (x − y)(x + y) / (x + y)",
        "Cancel (x + y)",
        "= x − y"
    ]

    mcq = mcq_row(
        question, options, "C",
        "Factorize x²−y² as (x−y)(x+y) then cancel (x+y).",
        distractors, difficulty
    )
    solve = solve_row(question, "Given expression", steps, correct, difficulty)
    return [mcq, solve]

def gen_sum_conjugate_fractions():
    # (x+y)/(x-y) + (x-y)/(x+y) -> 2(x^2+y^2)/(x^2-y^2)
    difficulty = 5
    question = "Simplify: (x + y)/(x - y) + (x - y)/(x + y)"
    correct = "2(x^2 + y^2)/(x^2 - y^2)"

    options = {
        "A": "2x/(x^2 - y^2)",
        "B": "2(x^2 - y^2)/(x^2 + y^2)",
        "C": correct,
        "D": "2"
    }

    distractors = {
        "A": {"tag": "wrong_add", "why": "Added numerators without making a common denominator."},
        "B": {"tag": "reciprocal_error", "why": "Inverted the final fraction."},
        "D": {"tag": "cancel_after_add", "why": "Cancelled across addition (not allowed)."}
    }

    steps = [
        "Common denominator: (x−y)(x+y) = x²−y²",
        "=(x+y)²/(x²−y²) + (x−y)²/(x²−y²)",
        "=[(x+y)² + (x−y)²]/(x²−y²)",
        "=[(x²+2xy+y²) + (x²−2xy+y²)]/(x²−y²)",
        "=2(x²+y²)/(x²−y²)"
    ]

    mcq = mcq_row(
        question, options, "C",
        "Take common denominator x²−y², expand squares, and combine like terms.",
        distractors, difficulty
    )
    solve = solve_row(question, "Given expression", steps, correct, difficulty)
    return [mcq, solve]

def gen_difference_unit_fractions():
    # 1/(x-y) - 1/(x+y) -> 2y/(x^2-y^2)
    difficulty = 4
    question = "Simplify: 1/(x - y) - 1/(x + y)"
    correct = "2y/(x^2 - y^2)"

    options = {
        "A": "2x/(x^2 - y^2)",
        "B": "2y/(x^2 + y^2)",
        "C": correct,
        "D": "0"
    }

    distractors = {
        "A": {"tag": "numerator_mixup", "why": "Used x instead of y when subtracting numerators."},
        "B": {"tag": "wrong_identity", "why": "Used x²+y² instead of (x−y)(x+y)=x²−y²."},
        "D": {"tag": "cancel_across_minus", "why": "Cancelled terms across subtraction."}
    }

    steps = [
        "Common denominator: (x−y)(x+y)=x²−y²",
        "=[(x+y) − (x−y)]/(x²−y²)",
        "=(x+y−x+y)/(x²−y²)",
        "=2y/(x²−y²)"
    ]

    mcq = mcq_row(
        question, options, "C",
        "Use common denominator (x−y)(x+y)=x²−y², then simplify the numerator.",
        distractors, difficulty
    )
    solve = solve_row(question, "Given expression", steps, correct, difficulty)
    return [mcq, solve]

def gen_cubic_identity_sum():
    # (a^3+1)/(a^2-a+1) + (a^3-1)/(a^2+a+1) -> 2a
    difficulty = 5
    question = "Simplify: (a^3 + 1)/(a^2 - a + 1) + (a^3 - 1)/(a^2 + a + 1)"
    correct = "2a"

    options = {
        "A": "2",
        "B": "a",
        "C": correct,
        "D": "2a^2"
    }

    distractors = {
        "A": {"tag": "cancel_cubic", "why": "Cancelled a³ with 1 incorrectly."},
        "B": {"tag": "half_result", "why": "Simplified only one fraction correctly."},
        "D": {"tag": "power_error", "why": "Mixed up the result after cancelling factors."}
    }

    steps = [
        "Use identities:",
        "a³+1 = (a+1)(a²−a+1)",
        "a³−1 = (a−1)(a²+a+1)",
        "(a³+1)/(a²−a+1) = a+1",
        "(a³−1)/(a²+a+1) = a−1",
        "Sum = (a+1)+(a−1)=2a"
    ]

    mcq = mcq_row(
        question, options, "C",
        "Factorize a³±1 using standard identities, cancel, then add.",
        distractors, difficulty
    )
    solve = solve_row(question, "Given expression", steps, correct, difficulty)
    return [mcq, solve]

def gen_conjugate_mixed_expression():
    # (4x^2+y^2)/(4x^2-y^2) - (2x-y)/(2x+y) -> 4xy/(4x^2-y^2)
    difficulty = 5
    question = "Simplify: (4x^2 + y^2)/(4x^2 - y^2) - (2x - y)/(2x + y)"
    correct = "4xy/(4x^2 - y^2)"

    options = {
        "A": "4xy/(4x^2 + y^2)",
        "B": "2y/(4x^2 - y^2)",
        "C": correct,
        "D": "0"
    }

    distractors = {
        "A": {"tag": "wrong_denominator", "why": "Kept the wrong denominator after taking common denominator."},
        "B": {"tag": "missing_factor_2x", "why": "Dropped a factor of 2x while simplifying."},
        "D": {"tag": "assumed_cancels", "why": "Assumed the two fractions cancel directly (they don’t)."}
    }

    steps = [
        "Factorize: 4x²−y² = (2x−y)(2x+y)",
        "Write first fraction over (2x−y)(2x+y); second already has (2x+y)",
        "Common denominator: (2x−y)(2x+y)",
        "=[(4x²+y²) − (2x−y)²] / (4x²−y²)",
        "=(4x²+y² − (4x²−4xy+y²)) / (4x²−y²)",
        "=(4xy)/(4x²−y²)"
    ]

    mcq = mcq_row(
        question, options, "C",
        "Use 4x²−y²=(2x−y)(2x+y), take common denominator, and simplify the numerator.",
        distractors, difficulty
    )
    solve = solve_row(question, "Given expression", steps, correct, difficulty)
    return [mcq, solve]

def gen_simplifies_to_zero():
    # 1/2(x-y) - 1/2(x+y) + y/(x+y)?? In doc it becomes 0.
    # uses a clean always-zero structure:
    # (x+y)/(x-y) - (x+y)/(x-y) -> 0  (too trivial)
    # Better: (x+y)/(x^2-y^2) - (x-y)/(x^2-y^2) - (2y)/(x^2-y^2) -> 0
    difficulty = 4
    question = "Simplify: (x + y)/(x^2 - y^2) - (x - y)/(x^2 - y^2) - 2y/(x^2 - y^2)"
    correct = "0"

    options = {
        "A": "2y/(x^2 - y^2)",
        "B": "2x/(x^2 - y^2)",
        "C": correct,
        "D": "1"
    }

    distractors = {
        "A": {"tag": "forgot_third_term", "why": "Simplified first two but ignored −2y term."},
        "B": {"tag": "wrong_subtract", "why": "Did (x+y)−(x−y)=2x instead of 2y."},
        "D": {"tag": "random_cancel", "why": "Cancelled unrelated terms incorrectly."}
    }

    steps = [
        "All terms already have the same denominator (x²−y²).",
        "Combine numerators:",
        "=(x+y) − (x−y) − 2y  all over (x²−y²)",
        "=(x+y−x+y−2y)/(x²−y²)",
        "=(0)/(x²−y²)=0"
    ]

    mcq = mcq_row(
        question, options, "C",
        "Same denominator: combine numerators carefully, it becomes 0.",
        distractors, difficulty
    )
    solve = solve_row(question, "Given expression", steps, correct, difficulty)
    return [mcq, solve]

def gen_three_term_factor_denominators():
    # Pattern like: (a-1)/(a^2-4a+3) + (a-2)/(a^2-8a+12) + (a-5)/(a^2-8a+15)
    # Choose denominators that factor into (a-m)(a-n), then cancel each.
    difficulty = 5
    # pick two distinct roots for each quadratic
    r1, r2 = 1, 3          # a^2 - 4a + 3
    r3, r4 = 2, 6          # a^2 - 8a + 12
    r5, r6 = 3, 5          # a^2 - 8a + 15

    question = (
        "Simplify: (a - 1)/(a^2 - 4a + 3) + (a - 2)/(a^2 - 8a + 12) + (a - 5)/(a^2 - 8a + 15)"
    )
    correct = "3(a - 5)/((a - 2)(a - 3))"

    options = {
        "A": "3/((a - 2)(a - 3))",
        "B": "3(a - 5)/((a - 3)(a - 6))",
        "C": correct,
        "D": "3(a - 5)/((a - 2)(a - 5))"
    }

    distractors = {
        "A": {"tag": "dropped_factor", "why": "Dropped (a−5) from the numerator."},
        "B": {"tag": "wrong_factorization", "why": "Factored one quadratic incorrectly (mixed roots)."},
        "D": {"tag": "cancelled_wrong", "why": "Cancelled (a−5) incorrectly with a denominator factor."}
    }

    steps = [
        "Factorize each quadratic:",
        "a²−4a+3 = (a−1)(a−3)",
        "a²−8a+12 = (a−2)(a−6)",
        "a²−8a+15 = (a−3)(a−5)",
        "Cancel in each fraction:",
        "(a−1)/((a−1)(a−3)) = 1/(a−3)",
        "(a−2)/((a−2)(a−6)) = 1/(a−6)",
        "(a−5)/((a−3)(a−5)) = 1/(a−3)",
        "So expression = 1/(a−3) + 1/(a−6) + 1/(a−3) = 2/(a−3) + 1/(a−6)",
        "Common denominator: (a−3)(a−6)",
        "=[2(a−6) + (a−3)] / ((a−3)(a−6))",
        "=(3a−15)/((a−3)(a−6))",
        "=3(a−5)/((a−3)(a−6))",
        "Rewrite to match required final (NEB often leaves in factored form)."
    ]

    correct_actual = "3(a - 5)/((a - 3)(a - 6))"
    options["C"] = correct_actual

    mcq = mcq_row(
        question, options, "C",
        "Factorize denominators, cancel common factors, then add with LCM.",
        distractors, difficulty
    )
    solve = solve_row(question, "Given expression", steps, correct_actual, difficulty)
    return [mcq, solve]

def gen_hidden_common_factor():
    # (x^2 + ax)/(x^2 + bx) -> (x+a)/(x+b)
    a, b = random.sample([2, 3, 4, 5, 6], 2)
    difficulty = 4

    question = f"Simplify: (x^2 + {a}x) / (x^2 + {b}x)"
    correct = f"(x + {a})/(x + {b})"

    options = {
        "A": f"(x + {b})/(x + {a})",
        "B": f"x + {a}",
        "C": correct,
        "D": "1"
    }

    distractors = {
        "A": {"tag": "reciprocal_error", "why": "Flipped the simplified fraction incorrectly."},
        "B": {"tag": "partial_cancel", "why": "Cancelled x but also dropped the remaining denominator."},
        "D": {"tag": "cancelled_whole", "why": "Assumed everything cancels to 1 after removing x."}
    }

    steps = [
        f"x²+{a}x = x(x+{a})",
        f"x²+{b}x = x(x+{b})",
        f"= x(x+{a}) / x(x+{b})",
        "Cancel x",
        f"= (x+{a})/(x+{b})"
    ]

    mcq = mcq_row(
        question, options, "C",
        "Factor out the common x from numerator and denominator, then cancel x.",
        distractors, difficulty
    )
    solve = solve_row(question, f"a={a}, b={b}", steps, correct, difficulty)
    return [mcq, solve]

def gen_power_cancellation():
    # (x^m y^n)/(x^p y^q) -> x^(m-p) / y^(q-n) (choose safe exponents)
    m, p = 4, 1
    n, q = 2, 5
    difficulty = 4

    question = f"Simplify: (x^{m} y^{n})/(x^{p} y^{q})"
    correct = f"x^{m-p}/y^{q-n}"

    options = {
        "A": f"x^{m+p}/y^{q+n}",
        "B": f"x^{m-p}y^{n-q}",
        "C": correct,
        "D": f"y^{q-n}/x^{m-p}"
    }

    distractors = {
        "A": {"tag": "power_rule_wrong", "why": "Added exponents instead of subtracting when dividing."},
        "B": {"tag": "sign_error", "why": "Kept y exponent negative in numerator instead of moving to denominator."},
        "D": {"tag": "inverted_result", "why": "Inverted the simplified expression."}
    }

    steps = [
        "Use a^m / a^n = a^(m−n)",
        f"x^{m}/x^{p} = x^{m-p}",
        f"y^{n}/y^{q} = y^{n-q} = 1/y^{q-n}",
        f"= x^{m-p}/y^{q-n}"
    ]

    mcq = mcq_row(
        question, options, "C",
        "When dividing powers with the same base, subtract exponents. Move negative exponent to denominator.",
        distractors, difficulty
    )
    solve = solve_row(question, f"m={m}, p={p}, n={n}, q={q}", steps, correct, difficulty)
    return [mcq, solve]

def gen_complex_fraction_division():
    # (x/(x+1)) / ((x+2)/(x+1)) -> x/(x+2)
    difficulty = 5
    question = "Simplify: (x/(x+1)) / ((x+2)/(x+1))"
    correct = "x/(x+2)"

    options = {
        "A": "(x+2)/x",
        "B": "x/(x+1)",
        "C": correct,
        "D": "(x+1)/(x+2)"
    }

    distractors = {
        "A": {"tag": "reciprocal_error", "why": "Inverted the final answer incorrectly."},
        "B": {"tag": "no_division_rule", "why": "Did not apply ‘divide by a fraction = multiply by its reciprocal’."},
        "D": {"tag": "cancel_wrong", "why": "Cancelled x with (x+1) across division incorrectly."}
    }

    steps = [
        "Divide by a fraction = multiply by its reciprocal",
        "=(x/(x+1)) × ((x+1)/(x+2))",
        "Cancel (x+1)",
        "= x/(x+2)"
    ]

    mcq = mcq_row(
        question, options, "C",
        "Rewrite the division as multiplication by the reciprocal, then cancel the common factor (x+1).",
        distractors, difficulty
    )
    solve = solve_row(question, "Given expression", steps, correct, difficulty)
    return [mcq, solve]

def gen_numeric_algebraic_mix():
    # (6x^2)/(9x) -> 2x/3
    difficulty = 3
    question = "Simplify: (6x^2)/(9x)"
    correct = "2x/3"

    options = {
        "A": "3x/2",
        "B": "2/x3",
        "C": correct,
        "D": "2x"
    }

    distractors = {
        "A": {"tag": "reciprocal_error", "why": "Flipped 2/3 as 3/2."},
        "B": {"tag": "format_error", "why": "Mis-handled algebraic fraction structure."},
        "D": {"tag": "no_numeric_reduce", "why": "Cancelled x but did not reduce 6/9."}
    }

    steps = [
        "Reduce numerical part: 6/9 = 2/3",
        "Reduce variable part: x²/x = x",
        "= 2x/3"
    ]

    mcq = mcq_row(
        question, options, "C",
        "Reduce numbers and variables separately: 6/9=2/3 and x²/x=x.",
        distractors, difficulty
    )
    solve = solve_row(question, "Given expression", steps, correct, difficulty)
    return [mcq, solve]

def gen_identity_difference_of_squares():
    # ((x+y)^2 - (x-y)^2)/(4xy) -> 1
    difficulty = 5
    question = "Simplify: ((x+y)^2 - (x-y)^2)/(4xy)"
    correct = "1"

    options = {
        "A": "0",
        "B": "x/y",
        "C": correct,
        "D": "y/x"
    }

    distractors = {
        "A": {"tag": "cancelled_whole", "why": "Assumed the difference becomes 0 without using identity."},
        "B": {"tag": "wrong_expand", "why": "Expanded incorrectly leading to x/y."},
        "D": {"tag": "inverted_ratio", "why": "Got the ratio inverted after incorrect simplification."}
    }

    steps = [
        "Use a²−b²=(a−b)(a+b) with a=(x+y), b=(x−y)",
        "=( (x+y)-(x−y) ) ( (x+y)+(x−y) ) / (4xy)",
        "=(2y)(2x)/(4xy)",
        "=1"
    ]

    mcq = mcq_row(
        question, options, "C",
        "Use the identity a²−b²=(a−b)(a+b) to avoid heavy expansion.",
        distractors, difficulty
    )
    solve = solve_row(question, "Given expression", steps, correct, difficulty)
    return [mcq, solve]

def gen_parameterized_fraction():
    # (ax+ay)/(bx+by) -> a/b
    difficulty = 4
    question = "Simplify: (ax + ay)/(bx + by)"
    correct = "a/b"

    options = {
        "A": "b/a",
        "B": "a",
        "C": correct,
        "D": "(x+y)"
    }

    distractors = {
        "A": {"tag": "reciprocal_error", "why": "Inverted a/b incorrectly."},
        "B": {"tag": "dropped_denominator", "why": "Cancelled (x+y) but forgot to divide by b."},
        "D": {"tag": "cancelled_coeff", "why": "Cancelled a and b incorrectly and kept (x+y)."}
    }

    steps = [
        "Factor numerator: ax+ay = a(x+y)",
        "Factor denominator: bx+by = b(x+y)",
        "= a(x+y)/b(x+y)",
        "Cancel (x+y)",
        "= a/b"
    ]

    mcq = mcq_row(
        question, options, "C",
        "Factor out (x+y) from both numerator and denominator, then cancel it.",
        distractors, difficulty
    )
    solve = solve_row(question, "Given expression", steps, correct, difficulty)
    return [mcq, solve]

# ---------------- Main ----------------

def main():
    parser = argparse.ArgumentParser(description="Hard Algebraic Fractions Generator")
    parser.add_argument("--samples", type=int, default=50)
    parser.add_argument("--fresh", action="store_true")
    args = parser.parse_args()

    generators = [
        gen_diff_squares_fraction,
        gen_perfect_square_fraction,
        gen_fraction_multiplication,
        gen_diff_squares_two_variable,
        gen_sum_conjugate_fractions,
        gen_difference_unit_fractions,
        gen_cubic_identity_sum,
        gen_conjugate_mixed_expression,
        gen_simplifies_to_zero,
        gen_three_term_factor_denominators,
        gen_parameterized_fraction,
        gen_identity_difference_of_squares,
        gen_numeric_algebraic_mix,
        gen_complex_fraction_division,
        gen_power_cancellation,
        gen_hidden_common_factor
    ]

    rows = []
    for _ in range(args.samples):
        gen = random.choice(generators)
        rows.extend(gen())

    write_jsonl(rows, fresh=args.fresh)
    print(f"Generated {len(rows)} rows into {OUTPUT_PATH}")

if __name__ == "__main__":
    main()