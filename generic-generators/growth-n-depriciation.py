import json
import random
import math
import argparse
from pathlib import Path

OUTPUT_PATH = Path("data/growth_depreciation/raw/growth_depr_train.jsonl")

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
        "chapter": "growth_depreciation",
        "task": "generate_mcq",
        "difficulty": difficulty,
        "messages": [
            {"role": "system", "content": SYSTEM_GEN},
            {"role": "user", "content":
                "Task: generate_mcq\n"
                "Chapter: Growth and Depreciation\n"
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
            "meta": {"chapter": "growth_depreciation", "difficulty": difficulty}
        }
    }

def solve_row(question, given, steps, final_answer, difficulty):
    return {
        "chapter": "growth_depreciation",
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


# ------------------ Type 1: Single Rate Growth ------------------

def gen_growth_single():
    P = random.choice([1000, 2000, 5000])
    R = random.choice([2, 5, 8])
    T = random.choice([1, 2, 3])
    difficulty = random.choice([1, 2])

    PT = P * ((1 + R/100) ** T)
    PG = PT - P

    find = random.choice(["PT", "PG"])

    if find == "PT":
        question = f"The population of a city is {P}. It grows at a constant rate of {R}% per annum for {T} years. Find the population after {T} years."
        correct_val = format_money(PT)
        steps = [
            "PT = P * (1 + R/100)^T",
            f"PT = {P} * (1 + {R}/100)^{T} = {format_money(PT)}"
        ]
    else:
        question = f"The population of a city is {P}. It grows at a constant rate of {R}% per annum for {T} years. Find the increase in population after {T} years."
        correct_val = format_money(PG)
        steps = [
            "PG = P * ((1 + R/100)^T - 1)",
            f"PG = {P} * ((1 + {R}/100)^{T} - 1) = {format_money(PG)}"
        ]

    wrong1 = correct_val * 2
    wrong2 = max(1, correct_val // 2)
    wrong3 = correct_val + random.choice([5, 10, 20])

    options = {
        "A": str(wrong1),
        "B": str(wrong2),
        "C": str(correct_val),
        "D": str(wrong3)
    }

    distractors = {
        "A": {"tag": "formula_misuse", "why": "Multiplied incorrectly or ignored growth factor."},
        "B": {"tag": "arithmetic_error", "why": "Half of correct value by mistake."},
        "D": {"tag": "rounding_error", "why": "Minor rounding or unit error."}
    }

    mcq = mcq_row(question, options, "C",
                  "Use population growth formula to calculate.",
                  distractors, difficulty)

    solve = solve_row(question, f"P={P}, R={R}%, T={T}", steps, f"Answer = {correct_val}", difficulty)

    return [mcq, solve]


# ------------------ Type 2: Single Rate Depreciation ------------------

def gen_depreciation_single():
    P = random.choice([1000, 2000, 5000])
    R = random.choice([5, 10, 12])
    T = random.choice([1, 2, 3])
    difficulty = random.choice([1, 2])

    VT = P * ((1 - R/100) ** T)

    find = random.choice(["VT", "decrease"])

    if find == "VT":
        question = f"The present value of a machine is Rs {P}. It depreciates at {R}% per annum for {T} years. Find its value after {T} years."
        correct_val = format_money(VT)
        steps = [
            "VT = P * (1 - R/100)^T",
            f"VT = {P} * (1 - {R}/100)^{T} = {format_money(VT)}"
        ]
    else:
        decrease = P - VT
        question = f"The present value of a machine is Rs {P}. It depreciates at {R}% per annum for {T} years. Find the total decrease in value."
        correct_val = format_money(decrease)
        steps = [
            "Decrease = P - VT",
            f"Decrease = {P} - {format_money(VT)} = {format_money(decrease)}"
        ]

    wrong1 = correct_val * 2
    wrong2 = max(1, correct_val // 2)
    wrong3 = correct_val + random.choice([5, 10, 20])

    options = {
        "A": str(wrong1),
        "B": str(wrong2),
        "C": str(correct_val),
        "D": str(wrong3)
    }

    distractors = {
        "A": {"tag": "formula_misuse", "why": "Used growth formula instead of depreciation."},
        "B": {"tag": "arithmetic_error", "why": "Half of correct value by mistake."},
        "D": {"tag": "rounding_error", "why": "Minor rounding error."}
    }

    mcq = mcq_row(question, options, "C",
                  "Use depreciation formula to calculate.",
                  distractors, difficulty)

    solve = solve_row(question, f"P={P}, R={R}%, T={T}", steps, f"Answer = {correct_val}", difficulty)

    return [mcq, solve]


# ------------------ Type 3: Variable Rates Growth/Depreciation ------------------

def gen_variable_rates(mode="growth"):
    P = random.choice([2000, 3000, 5000])
    years = random.randint(3, 5)
    rates = [random.choice([5, 8, 10, 12]) for _ in range(years)]
    difficulty = 3

    factor = 1
    for r in rates:
        factor *= (1 + r/100) if mode == "growth" else (1 - r/100)

    final_val = P * factor
    delta = final_val - P if mode == "growth" else P - final_val

    rate_str = ", ".join([f"{r}%" for r in rates])

    if mode == "growth":
        question = f"A city has population {P}. It grows for {years} years at rates {rate_str} respectively. Find the total increase in population."
    else:
        question = f"An object worth Rs {P} depreciates for {years} years at rates {rate_str} respectively. Find the total decrease in value."

    correct_val = format_money(delta)

    wrong1 = format_money(P * sum(rates) / 100 * years)  # simple sum of rates
    wrong2 = format_money(final_val)
    wrong3 = format_money(P * (1 + sum(rates)/100) if mode=="growth" else P * (1 - sum(rates)/100))

    options = {
        "A": str(wrong1),
        "B": str(correct_val),
        "C": str(wrong2),
        "D": str(wrong3)
    }

    distractors = {
        "A": {"tag": "simple_sum_rates", "why": "Added rates and used simple interest style."},
        "C": {"tag": "amount_instead_delta", "why": "Calculated final value instead of increase/decrease."},
        "D": {"tag": "single_year", "why": "Used only sum of rates for single year instead of compounding."}
    }

    steps = [
        f"Multiply growth/depreciation factors for each year.",
        f"Final value = {format_money(final_val)}",
        f"{'Increase' if mode=='growth' else 'Decrease'} = {correct_val}"
    ]

    mcq = mcq_row(question, options, "B",
                  f"Multiply yearly factors then subtract principal to find {'increase' if mode=='growth' else 'decrease'}.",
                  distractors, difficulty)

    solve = solve_row(question, f"P={P}, Rates={rates}", steps,
                      f"{'Increase' if mode=='growth' else 'Decrease'} = {correct_val}",
                      difficulty)

    return [mcq, solve]


# ------------------ Main ------------------

def main():
    parser = argparse.ArgumentParser(description="Growth and Depreciation dataset generator")

    parser.add_argument("--samples", type=int, default=50, help="Number of questions to generate (default: 50)")
    parser.add_argument("--fresh", action="store_true", help="Overwrite existing dataset instead of appending")

    args = parser.parse_args()

    generators = [
        gen_growth_single,
        gen_depreciation_single,
        lambda: gen_variable_rates("growth"),
        lambda: gen_variable_rates("depreciation")
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