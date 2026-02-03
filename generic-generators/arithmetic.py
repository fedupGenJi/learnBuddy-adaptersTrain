import json
import random
import math
import argparse
from pathlib import Path

OUTPUT_PATH = Path("data/arithmetic/raw/arithmetic_train.jsonl")

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
        "chapter": "arithmetic",
        "task": "generate_mcq",
        "difficulty": difficulty,
        "messages": [
            {"role": "system", "content": SYSTEM_GEN},
            {"role": "user", "content":
                "Task: generate_mcq\n"
                "Chapter: Arithmetic\n"
                f"Difficulty: {difficulty}\n"
                "Rules:\n"
                "- Create ONE NEB-style arithmetic word problem.\n"
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
            "meta": {"chapter": "arithmetic", "difficulty": difficulty}
        }
    }


def solve_row(question, given, steps, final_answer, difficulty):
    return {
        "chapter": "arithmetic",
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


def format_money(x):
    return int(round(x))


# ------------------ Type 1: Simple Interest ------------------

def gen_simple_interest():
    difficulty = random.choice([1, 2])

    P = random.choice([1000, 2000, 2500, 3000, 5000])
    R = random.choice([4, 5, 6, 8, 10])
    T = random.choice([1, 2, 3])

    I = (P * R * T) / 100

    find = random.choice(["I", "P", "R", "T"])

    if find == "I":
        question = f"Find the simple interest on Rs {P} at {R}% per annum for {T} years."
        correct_val = I
        steps = [
            "I = (P × R × T) / 100",
            f"I = ({P} × {R} × {T}) / 100 = {int(I)}"
        ]

    elif find == "P":
        question = f"The simple interest is Rs {int(I)} at {R}% per annum for {T} years. Find the principal."
        correct_val = (I * 100) / (R * T)
        steps = [
            "P = (I × 100) / (R × T)",
            f"P = ({int(I)} × 100) / ({R} × {T}) = {int(correct_val)}"
        ]

    elif find == "R":
        question = f"The simple interest on Rs {P} for {T} years is Rs {int(I)}. Find the rate percent per annum."
        correct_val = (I * 100) / (P * T)
        steps = [
            "R = (I × 100) / (P × T)",
            f"R = ({int(I)} × 100) / ({P} × {T}) = {int(correct_val)}%"
        ]

    else:  # find T
        question = f"The simple interest on Rs {P} at {R}% per annum is Rs {int(I)}. Find the time in years."
        correct_val = (I * 100) / (P * R)
        steps = [
            "T = (I × 100) / (P × R)",
            f"T = ({int(I)} × 100) / ({P} × {R}) = {int(correct_val)} years"
        ]

    correct_val = int(round(correct_val))

    wrong1 = int(correct_val * 2)
    wrong2 = max(1, int(correct_val / 2))
    wrong3 = correct_val + random.choice([5, 10, 20])

    options = {
        "A": str(wrong1),
        "B": str(wrong2),
        "C": str(correct_val),
        "D": str(wrong3)
    }

    distractors = {
        "A": {"tag": "formula_misuse", "why": "Incorrect rearrangement of formula."},
        "B": {"tag": "calculation_error", "why": "Arithmetic mistake."},
        "D": {"tag": "unit_error", "why": "Incorrect unit handling or rounding."}
    }

    mcq = mcq_row(question, options, "C",
                  "Use simple interest formula and rearrange for the missing variable.",
                  distractors, difficulty)

    solve = solve_row(
        question,
        f"P={P}, R={R}%, T={T}, I={int(I)}",
        steps,
        f"Answer = {correct_val}",
        difficulty
    )

    return [mcq, solve]

# ------------------ Type 2: Compound Interest Annually ------------------

def gen_ci_annual():
    mode = random.choice([
        "PTR_find_CI",
        "PTR_find_CA",
        "PTR_find_both",
        "given_CA_find_P",
        "given_CI_find_P"
    ])

    if mode in ["given_CA_find_P", "given_CI_find_P"]:
        difficulty = 1
    else:
        difficulty = random.choice([2, 3])

    P = random.choice([1000, 2000, 5000])
    R = random.choice([5, 8, 10])
    T = random.choice([2, 3])

    CA = P * ((1 + R / 100) ** T)
    CI = CA - P

    CAi = int(round(CA))
    CIi = int(round(CI))

    if mode == "PTR_find_CI":
        question = f"Find the compound interest on Rs {P} at {R}% per annum for {T} years."

        correct_val = CIi
        steps = [
            "CA = P(1+R/100)^T",
            f"CA = {CAi}",
            "CI = CA − P",
            f"CI = {CAi} − {P} = {CIi}"
        ]

    elif mode == "PTR_find_CA":
        question = f"Find the compound amount on Rs {P} at {R}% per annum for {T} years."
        correct_val = CAi
        steps = [
            "CA = P(1+R/100)^T",
            f"CA = {CAi}"
        ]

    elif mode == "PTR_find_both":
        question = f"Find the compound interest and compound amount on Rs {P} at {R}% per annum for {T} years."
        correct_val = CIi
        steps = [
            "CA = P(1+R/100)^T",
            f"CA = {CAi}",
            "CI = CA − P",
            f"CI = {CIi}"
        ]

    elif mode == "given_CA_find_P":
        question = f"The compound amount is Rs {CAi} at {R}% per annum for {T} years. Find the principal."

        correct_val = int(round(CAi / ((1 + R/100) ** T)))

        steps = [
            "P = CA / (1+R/100)^T",
            f"P = {CAi} / (1+{R}/100)^{T}",
            f"P = {correct_val}"
        ]

    else:  # given_CI_find_P
        question = f"The compound interest is Rs {CIi} at {R}% per annum for {T} years. Find the principal."

        CA_known = CIi + P
        correct_val = int(round(CAi / ((1 + R/100) ** T)))

        steps = [
            "CA = CI + P",
            "P = CA / (1+R/100)^T",
            f"P = {correct_val}"
        ]

    wrong1 = int(correct_val * 2)
    wrong2 = max(1, int(correct_val / 2))
    wrong3 = correct_val + random.choice([50, 100, 200])

    options = {
        "A": str(wrong1),
        "B": str(wrong2),
        "C": str(correct_val),
        "D": str(wrong3)
    }

    distractors = {
        "A": {"tag": "simple_interest_used", "why": "Used simple interest formula."},
        "B": {"tag": "power_ignored", "why": "Did not use exponent for time."},
        "D": {"tag": "rounding_error", "why": "Incorrect rounding or arithmetic."}
    }

    mcq = mcq_row(
        question, options, "C",
        "Use compound interest formula and rearrange if needed.",
        distractors, difficulty
    )

    solve = solve_row(
        question,
        f"P={P}, R={R}%, T={T}, CI={CIi}, CA={CAi}",
        steps,
        f"Answer = {correct_val}",
        difficulty
    )

    return [mcq, solve]

# ------------------ Type 3: Semi / Quarterly ------------------

def gen_ci_fractional():
    P = random.choice([2000, 5000])
    R = random.choice([8, 10])
    T = random.choice([2, 3])
    mode = random.choice(["semi", "quarter"])
    difficulty = random.choice([2, 3])

    if mode == "semi":
        CA = P * ((1 + R/200) ** (2*T))
        label = "semi-annually"
    else:
        CA = P * ((1 + R/400) ** (4*T))
        label = "quarterly"

    CI = CA - P

    question = f"Find the compound interest on Rs {P} at {R}% per annum compounded {label} for {T} years."

    correct = format_money(CI)
    wrong1 = format_money(P * R * T / 100)
    wrong2 = format_money(P * ((1 + R/100) ** T) - P)
    wrong3 = format_money(CA)

    options = {
        "A": f"Rs {wrong1}",
        "B": f"Rs {wrong2}",
        "C": f"Rs {correct}",
        "D": f"Rs {wrong3}"
    }

    distractors = {
        "A": {"tag": "simple_interest", "why": "Used simple interest formula."},
        "B": {"tag": "annual_formula", "why": "Used annual compounding instead of fractional."},
        "D": {"tag": "amount_instead_interest", "why": "Gave compound amount instead of interest."}
    }

    steps = [
        f"Use fractional compounding formula for {label}.",
        f"CA = {format_money(CA)}",
        f"CI = CA − P = {format_money(CI)}"
    ]

    mcq = mcq_row(question, options, "C",
                  "Use fractional compounding formula then subtract principal.",
                  distractors, difficulty)

    solve = solve_row(question, f"P={P}, R={R}%, T={T}", steps,
                      f"Compound Interest = Rs {format_money(CI)}",
                      difficulty)

    return [mcq, solve]


# ------------------ Type 4: Different Rates ------------------

def gen_ci_variable_rates():
    P = random.choice([2000, 3000, 5000])
    years = random.randint(3, 5)
    rates = [random.choice([5, 8, 10, 12]) for _ in range(years)]
    difficulty = 3

    factor = 1
    for r in rates:
        factor *= (1 + r/100)

    CA = P * factor
    CI = CA - P

    rate_str = ", ".join([f"{r}%" for r in rates])

    question = f"A sum of Rs {P} is invested for {years} years at rates {rate_str} respectively. Find the compound interest."

    correct = format_money(CI)
    wrong1 = format_money(P * sum(rates) * years / 100)
    wrong2 = format_money(CA)
    wrong3 = format_money(P * (1 + sum(rates)/100))

    options = {
        "A": f"Rs {wrong1}",
        "B": f"Rs {correct}",
        "C": f"Rs {wrong2}",
        "D": f"Rs {wrong3}"
    }

    distractors = {
        "A": {"tag": "simple_sum_rates", "why": "Added rates and used simple interest."},
        "C": {"tag": "amount_instead_interest", "why": "Calculated amount instead of interest."},
        "D": {"tag": "single_year", "why": "Used only one year compounding."}
    }

    steps = [
        "Multiply growth factors for each year.",
        f"CA = {format_money(CA)}",
        f"CI = CA − P = {format_money(CI)}"
    ]

    mcq = mcq_row(question, options, "B",
                  "Multiply yearly growth factors then subtract principal.",
                  distractors, difficulty)

    solve = solve_row(question, f"P={P}, Rates={rates}", steps,
                      f"Compound Interest = Rs {format_money(CI)}",
                      difficulty)

    return [mcq, solve]


# ------------------ Type 5: Years + Months ------------------

def gen_ci_year_month():
    P = random.choice([2000, 5000])
    R = random.choice([8, 10])
    years = random.choice([2, 3])
    months = random.choice([3, 6, 9])
    difficulty = 3

    CA = P * ((1 + R/100) ** years) * (1 + (months * R) / 1200)
    CI = CA - P

    question = f"Find the compound interest on Rs {P} at {R}% per annum for {years} years and {months} months."

    correct = format_money(CI)
    wrong1 = format_money(P * R * (years + months/12) / 100)
    wrong2 = format_money(P * ((1 + R/100) ** (years + months/12)) - P)
    wrong3 = format_money(CA)

    options = {
        "A": f"Rs {wrong1}",
        "B": f"Rs {wrong2}",
        "C": f"Rs {correct}",
        "D": f"Rs {wrong3}"
    }

    distractors = {
        "A": {"tag": "simple_interest", "why": "Used simple interest formula."},
        "B": {"tag": "used_fractional_power", "why": "Used fractional exponent instead of separate month formula."},
        "D": {"tag": "amount_instead_interest", "why": "Gave amount instead of interest."}
    }

    steps = [
        "Apply formula for years then simple interest for months.",
        f"CA = {format_money(CA)}",
        f"CI = CA − P = {format_money(CI)}"
    ]

    mcq = mcq_row(question, options, "C",
                  "Use compound for years and simple for remaining months.",
                  distractors, difficulty)

    solve = solve_row(question, f"P={P}, R={R}%, Time={years}y {months}m", steps,
                      f"Compound Interest = Rs {format_money(CI)}",
                      difficulty)

    return [mcq, solve]


# ------------------ Main ------------------

def main():
    parser = argparse.ArgumentParser(description="Arithmetic dataset generator")

    parser.add_argument(
        "--samples",
        type=int,
        default=50,
        help="Number of questions to generate (default: 50)"
    )

    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Overwrite existing dataset instead of appending"
    )

    args = parser.parse_args()

    generators = [
        gen_simple_interest,
        gen_ci_annual,
        gen_ci_fractional,
        gen_ci_variable_rates,
        gen_ci_year_month
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