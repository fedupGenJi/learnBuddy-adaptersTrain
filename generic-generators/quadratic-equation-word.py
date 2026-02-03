import json
import random
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
                "Chapter: Quadratic Equations (Word Problems)\n"
                f"Difficulty: {difficulty}\n"
                "Rules:\n"
                "- One NEB-style quadratic word problem\n"
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
            "to_find": "Required value(s)",
            "steps": steps,
            "final_answer": final_answer
        }
    }


def make_mcq_options(correct_text, wrong_texts):
    """
    correct_text: str
    wrong_texts: list[str] of length 3
    returns (options_dict, correct_key)
    """
    keys = ["A", "B", "C", "D"]
    all_opts = wrong_texts + [correct_text]
    random.shuffle(all_opts)
    options = {k: all_opts[i] for i, k in enumerate(keys)}
    correct_key = [k for k, v in options.items() if v == correct_text][0]
    return options, correct_key


# --------------------------------------------------
# 1) Consecutive numbers (even / natural)
# --------------------------------------------------

def gen_consecutive_numbers():
    difficulty = 3
    mode = random.choice(["even", "natural"])

    if mode == "even":
        x = random.randint(4, 12)
        if x % 2 != 0:
            x += 1
        product = x * (x + 2)
        question = f"The product of two consecutive positive even numbers is {product}. Find the numbers."
        correct = f"{x} and {x+2}"

        wrong1 = f"{x-2} and {x}"  # shift back
        wrong2 = f"{x} and {x+1}"  # not even consecutive
        wrong3 = f"{x+2} and {x+4}"  # shift forward

        steps = [
            "Let the numbers be x and x+2",
            f"x(x+2) = {product}",
            "x² + 2x − product = 0",
            f"x = {x} (positive even solution)",
            f"Numbers: {x} and {x+2}"
        ]

    else:
        x = random.randint(3, 10)
        product = x * (x + 1)
        question = f"The product of two consecutive natural numbers is {product}. Find the numbers."
        correct = f"{x} and {x+1}"

        wrong1 = f"{x-1} and {x}"
        wrong2 = f"{x} and {x+2}"
        wrong3 = f"{x+1} and {x+2}"

        steps = [
            "Let the numbers be x and x+1",
            f"x(x+1) = {product}",
            "x² + x − product = 0",
            f"x = {x} (natural solution)",
            f"Numbers: {x} and {x+1}"
        ]

    options, correct_key = make_mcq_options(correct, [wrong1, wrong2, wrong3])

    distractors = {
        [k for k, v in options.items() if v == wrong1][0]: {"tag": "shift_error", "why": "Chose previous consecutive pair."},
        [k for k, v in options.items() if v == wrong2][0]: {"tag": "sequence_error", "why": "Did not use correct consecutive pattern."},
        [k for k, v in options.items() if v == wrong3][0]: {"tag": "shift_error", "why": "Chose next consecutive pair."}
    }

    mcq = mcq_row(
        question, options, correct_key,
        "Form a quadratic equation based on consecutive numbers and solve for x.",
        distractors, difficulty
    )

    solve = solve_row(question, "Consecutive numbers", steps, correct, difficulty)

    return [mcq, solve]


# --------------------------------------------------
# 2) Sum & product of two numbers
# --------------------------------------------------

def gen_sum_product():
    difficulty = 3
    a, b = random.sample(range(4, 15), 2)
    S, P = a + b, a * b

    question = f"The sum of two positive numbers is {S} and their product is {P}. Find the numbers."
    correct = f"{min(a,b)} and {max(a,b)}"

    wrong1 = f"{S} and {P}"
    wrong2 = f"{a} and {b+1}"
    wrong3 = f"{a-1} and {b}"

    options, correct_key = make_mcq_options(correct, [wrong1, wrong2, wrong3])

    steps = [
        "Let the numbers be x and y",
        f"x + y = {S}",
        f"xy = {P}",
        "y = S − x",
        "x(S − x) = P",
        "x² − Sx + P = 0",
        f"Roots give x = {a} and {b}",
        f"Numbers: {correct}"
    ]

    distractors = {
        [k for k, v in options.items() if v == wrong1][0]: {"tag": "data_confusion", "why": "Returned sum and product as numbers."},
        [k for k, v in options.items() if v == wrong2][0]: {"tag": "near_miss", "why": "Made arithmetic adjustment error."},
        [k for k, v in options.items() if v == wrong3][0]: {"tag": "near_miss", "why": "Made arithmetic adjustment error."}
    }

    mcq = mcq_row(
        question, options, correct_key,
        "Use x+y=S and xy=P, substitute y=S−x to form quadratic.",
        distractors, difficulty
    )

    solve = solve_row(question, f"S={S}, P={P}", steps, correct, difficulty)
    return [mcq, solve]


# --------------------------------------------------
# 3) Age problem (father–son)
# --------------------------------------------------

def gen_age_problem():
    difficulty = 3
    father = random.randint(28, 45)
    son = random.randint(10, 18)
    years = random.randint(2, 6)

    product = (father - years) * (son - years)

    question = (
        f"The present ages of a father and his son are {father} years and {son} years respectively. "
        f"How many years ago was the product of their ages {product}?"
    )

    correct = f"{years} years ago"
    wrong1 = f"{years+1} years ago"
    wrong2 = f"{years-1} years ago" if years > 2 else f"{years+2} years ago"
    wrong3 = f"{product} years ago"

    options, correct_key = make_mcq_options(correct, [wrong1, wrong2, wrong3])

    steps = [
        "Let x years ago be the required time",
        f"( {father} − x )( {son} − x ) = {product}",
        "Expand: father·son − (father+son)x + x² = product",
        "Form quadratic equation: x² − (father+son)x + (father·son − product) = 0",
        f"Valid solution is x = {years} (reject negative/invalid)",
        f"Answer: {years} years ago"
    ]

    distractors = {
        [k for k, v in options.items() if v == wrong1][0]: {"tag": "off_by_one", "why": "Solved but shifted by 1 year."},
        [k for k, v in options.items() if v == wrong2][0]: {"tag": "off_by_one", "why": "Solved but shifted by 1 year."},
        [k for k, v in options.items() if v == wrong3][0]: {"tag": "unit_error", "why": "Used product value as time."}
    }

    mcq = mcq_row(
        question, options, correct_key,
        "Let x years ago. Form quadratic from product of past ages and solve.",
        distractors, difficulty
    )

    solve = solve_row(question, f"Father={father}, Son={son}, Product={product}", steps, correct, difficulty)
    return [mcq, solve]


# --------------------------------------------------
# 4) Reciprocal problem (number and its reciprocal / sum of reciprocals)
# --------------------------------------------------

def gen_reciprocal():
    difficulty = 3
    x = random.randint(2, 8)

    # Using: 1/x + 1/(x+1) = (2x+1)/x(x+1)
    num = 2*x + 1
    den = x*(x+1)

    question = f"The sum of the reciprocals of two consecutive natural numbers is {num}/{den}. Find the numbers."

    correct = f"{x} and {x+1}"
    wrong1 = f"{x-1} and {x}"
    wrong2 = f"{x+1} and {x+2}"
    wrong3 = f"{x} and {x+2}"

    options, correct_key = make_mcq_options(correct, [wrong1, wrong2, wrong3])

    steps = [
        "Let the consecutive numbers be x and x+1",
        f"1/x + 1/(x+1) = {num}/{den}",
        "Take LCM: (2x+1)/(x(x+1)) = given fraction",
        "Cross multiply and solve quadratic",
        f"x = {x}",
        f"Numbers: {x} and {x+1}"
    ]

    distractors = {
        [k for k, v in options.items() if v == wrong1][0]: {"tag": "shift_error", "why": "Picked previous consecutive pair."},
        [k for k, v in options.items() if v == wrong2][0]: {"tag": "shift_error", "why": "Picked next consecutive pair."},
        [k for k, v in options.items() if v == wrong3][0]: {"tag": "gap_error", "why": "Used non-consecutive numbers."}
    }

    mcq = mcq_row(
        question, options, correct_key,
        "Let numbers be x and x+1, form equation using reciprocals and solve.",
        distractors, difficulty
    )

    solve = solve_row(question, "Reciprocal (consecutive)", steps, correct, difficulty)
    return [mcq, solve]


# --------------------------------------------------
# 5) Two-digit number (digit reversal) with +27
# --------------------------------------------------

def gen_two_digit():
    difficulty = 4

    # Ensure solvable: x - y = -3  => y = x+3 (so reversed by adding 27)
    tens = random.randint(2, 6)
    ones = tens + 3
    number = 10*tens + ones
    product_digits = tens * ones
    reversed_number = 10*ones + tens

    question = (
        f"The product of the digits of a two-digit number is {product_digits}. "
        f"If 27 is added to the number, the digits are reversed. Find the number."
    )

    correct = f"{number}"
    wrong1 = f"{reversed_number}"
    wrong2 = f"{number + 27}"
    wrong3 = f"{product_digits}"

    options, correct_key = make_mcq_options(correct, [wrong1, wrong2, wrong3])

    steps = [
        "Let tens digit = x and ones digit = y",
        "Original number = 10x + y",
        "Reversed number = 10y + x",
        f"Given: (10x + y) + 27 = 10y + x",
        "So, 9x − 9y = −27  ⇒  x − y = −3  ⇒  y = x + 3",
        f"Also xy = {product_digits}",
        "Substitute y = x+3 into xy",
        "x(x+3) = product",
        f"x = {tens}, y = {ones}",
        f"Number = {number}"
    ]

    distractors = {
        [k for k, v in options.items() if v == wrong1][0]: {"tag": "reversal_only", "why": "Chose reversed number instead of original."},
        [k for k, v in options.items() if v == wrong2][0]: {"tag": "misread", "why": "Returned number after adding 27."},
        [k for k, v in options.items() if v == wrong3][0]: {"tag": "data_confusion", "why": "Returned product of digits as number."}
    }

    mcq = mcq_row(
        question, options, correct_key,
        "Use digit variables and reversal condition to form quadratic and solve.",
        distractors, difficulty
    )

    solve = solve_row(question, f"Digit product={product_digits}", steps, f"The number is {number}", difficulty)
    return [mcq, solve]


# --------------------------------------------------
# 6) Right-angled triangle (Pythagoras -> quadratic)
# --------------------------------------------------

def gen_triangle():
    difficulty = 4

    # Use reliable triples (a,b,c) and ask with difference
    triples = [
        (3, 4, 5),
        (5, 12, 13),
        (8, 15, 17),
        (7, 24, 25),
        (9, 40, 41)
    ]
    a, b, c = random.choice(triples)
    diff = abs(b - a)

    question = (
        f"The hypotenuse of a right-angled triangle is {c} cm. "
        f"If the difference of the other two sides is {diff} cm, find their lengths."
    )

    correct = f"{min(a,b)} cm and {max(a,b)} cm"
    wrong1 = f"{min(a,b)} cm and {max(a,b)+diff} cm"
    wrong2 = f"{min(a,b)+1} cm and {max(a,b)+1} cm"
    wrong3 = f"{c} cm and {diff} cm"

    options, correct_key = make_mcq_options(correct, [wrong1, wrong2, wrong3])

    steps = [
        "Let one side = x cm, other side = x + d cm",
        "Using Pythagoras theorem:",
        "x² + (x+d)² = hypotenuse²",
        "Form quadratic equation and solve for x",
        f"Here the sides are {a} cm and {b} cm"
    ]

    distractors = {
        [k for k, v in options.items() if v == wrong1][0]: {"tag": "difference_misuse", "why": "Added difference incorrectly."},
        [k for k, v in options.items() if v == wrong2][0]: {"tag": "arithmetic_error", "why": "Shifted both sides wrongly."},
        [k for k, v in options.items() if v == wrong3][0]: {"tag": "concept_error", "why": "Used hypotenuse and difference as legs."}
    }

    mcq = mcq_row(
        question, options, correct_key,
        "Let legs be x and x+d, apply Pythagoras theorem and solve quadratic.",
        distractors, difficulty
    )

    solve = solve_row(question, f"Hypotenuse={c}, Difference={diff}", steps, correct, difficulty)
    return [mcq, solve]


# --------------------------------------------------
# 7) Rectangular land -> square (percentage reduction)
# --------------------------------------------------

def gen_rectangle_square():
    difficulty = 4

    # Pick nice integer dimensions
    L, B = random.choice([(30, 20), (25, 15), (28, 21), (40, 25)])
    area = L * B
    perimeter = 2 * (L + B)
    percent = int(round(((L - B) / L) * 100))

    question = (
        f"The area of a rectangular land is {area} m² and its perimeter is {perimeter} m. "
        f"If the land is to be made square, by what percentage should the length be reduced?"
    )

    correct = f"{percent}%"
    wrong1 = f"{int(round(((L - B) / B) * 100))}%"
    wrong2 = f"{int(round(((L - B) / (L + B)) * 100))}%"
    wrong3 = f"{L - B}%"

    options, correct_key = make_mcq_options(correct, [wrong1, wrong2, wrong3])

    steps = [
        "Let length = x and breadth = y",
        f"xy = {area}",
        f"2(x+y) = {perimeter} ⇒ x+y = {perimeter//2}",
        "From y = (perimeter/2) − x, substitute in xy equation",
        "Form quadratic equation to find x and y",
        f"Length = {L}, Breadth = {B}",
        "To make it square, length must become equal to breadth",
        f"Reduction = {L} − {B} = {L-B}",
        f"Percentage reduction = (({L-B})/{L})×100 = {percent}%"
    ]

    distractors = {
        [k for k, v in options.items() if v == wrong1][0]: {"tag": "wrong_base", "why": "Divided by breadth instead of length."},
        [k for k, v in options.items() if v == wrong2][0]: {"tag": "wrong_denominator", "why": "Divided by (L+B) instead of L."},
        [k for k, v in options.items() if v == wrong3][0]: {"tag": "missing_percent_formula", "why": "Used reduction value directly as percent."}
    }

    mcq = mcq_row(
        question, options, correct_key,
        "First find length and breadth using area & perimeter, then compute percentage reduction of length.",
        distractors, difficulty
    )

    solve = solve_row(question, f"Area={area}, Perimeter={perimeter}", steps, correct, difficulty)
    return [mcq, solve]


# --------------------------------------------------
# 8) Picnic / money sharing
# --------------------------------------------------

def gen_picnic():
    difficulty = 4

    # Construct consistent values:
    # Total budget T = x * per
    # After 5 absent: T/(x-5) = per + inc
    while True:
        x = random.randint(15, 30)
        per = random.choice([800, 1000, 1200, 1500, 2000])
        T = x * per
        inc = T / (x - 5) - per
        if inc.is_integer() and inc > 100:
            inc = int(inc)
            break

    question = (
        f"Some students planned a picnic with a budget of Rs {T}. "
        f"Five students were absent, so each student had to pay Rs {inc} more. "
        f"How many students attended the picnic?"
    )

    attended = x - 5
    correct = f"{attended} students"
    wrong1 = f"{x} students"
    wrong2 = f"{attended + 1} students"
    wrong3 = f"{attended - 1} students"

    options, correct_key = make_mcq_options(correct, [wrong1, wrong2, wrong3])

    steps = [
        "Let total students planned = x",
        f"Total budget T = {T}",
        "Original share = T/x",
        "After 5 absent, students = x−5",
        "New share = T/(x−5)",
        f"Given: T/(x−5) = T/x + {inc}",
        "Form quadratic equation and solve for x",
        f"x = {x}",
        f"Students attended = x−5 = {attended}"
    ]

    distractors = {
        [k for k, v in options.items() if v == wrong1][0]: {"tag": "asked_attended_but_gave_planned", "why": "Gave planned students instead of attended."},
        [k for k, v in options.items() if v == wrong2][0]: {"tag": "off_by_one", "why": "Miscounted attendance by 1."},
        [k for k, v in options.items() if v == wrong3][0]: {"tag": "off_by_one", "why": "Miscounted attendance by 1."}
    }

    mcq = mcq_row(
        question, options, correct_key,
        "Let planned students be x. Use share increase condition to form quadratic and solve.",
        distractors, difficulty
    )

    solve = solve_row(question, f"T={T}, Increase={inc}, Absent=5", steps, correct, difficulty)
    return [mcq, solve]


# --------------------------------------------------
# 9) Product becomes given after years
# --------------------------------------------------

def gen_future_product():
    difficulty = 3
    a, b = random.sample(range(10, 20), 2)
    years = random.randint(2, 5)
    product = (a + years) * (b + years)

    question = (
        f"The present ages of two sisters are {a} years and {b} years. "
        f"After how many years will the product of their ages be {product}?"
    )

    correct = f"{years} years"
    wrong1 = f"{years+1} years"
    wrong2 = f"{years-1} years" if years > 2 else f"{years+2} years"
    wrong3 = f"{product} years"

    options, correct_key = make_mcq_options(correct, [wrong1, wrong2, wrong3])

    steps = [
        "Let x years be required time",
        f"( {a} + x )( {b} + x ) = {product}",
        "Expand to form quadratic equation",
        "Solve for x (reject negative)",
        f"x = {years}"
    ]

    distractors = {
        [k for k, v in options.items() if v == wrong1][0]: {"tag": "off_by_one", "why": "Shifted years by 1."},
        [k for k, v in options.items() if v == wrong2][0]: {"tag": "off_by_one", "why": "Shifted years by 1."},
        [k for k, v in options.items() if v == wrong3][0]: {"tag": "unit_error", "why": "Used product value as time."}
    }

    mcq = mcq_row(
        question, options, correct_key,
        "Let x years later. Form quadratic from future product and solve.",
        distractors, difficulty
    )

    solve = solve_row(question, f"Ages={a},{b}, TargetProduct={product}", steps, correct, difficulty)
    return [mcq, solve]


# --------------------------------------------------
# 10) Difference of squares (identity-based)
# --------------------------------------------------

def gen_difference_squares():
    difficulty = 3
    x = random.randint(6, 15)

    # Use identity: (x+2)^2 - x^2 = 4x + 4
    diff = (x + 2)**2 - x**2
    question = f"The difference of the squares of two numbers which differ by 2 is {diff}. Find the numbers."

    correct = f"{x} and {x+2}"
    wrong1 = f"{x-2} and {x}"
    wrong2 = f"{x} and {x+1}"
    wrong3 = f"{diff} and {x}"

    options, correct_key = make_mcq_options(correct, [wrong1, wrong2, wrong3])

    steps = [
        "Let the numbers be x and x+2",
        "(x+2)² − x² = diff",
        "Use identity: a² − b² = (a−b)(a+b)",
        "So (2)(2x+2) = diff",
        "Solve for x",
        f"x = {x}",
        f"Numbers: {x} and {x+2}"
    ]

    distractors = {
        [k for k, v in options.items() if v == wrong1][0]: {"tag": "shift_error", "why": "Selected wrong pair of numbers."},
        [k for k, v in options.items() if v == wrong2][0]: {"tag": "difference_misread", "why": "Used difference 1 instead of 2."},
        [k for k, v in options.items() if v == wrong3][0]: {"tag": "data_confusion", "why": "Used diff value as one number."}
    }

    mcq = mcq_row(
        question, options, correct_key,
        "Use difference of squares identity and solve for x.",
        distractors, difficulty
    )

    solve = solve_row(question, f"Difference={diff}", steps, correct, difficulty)
    return [mcq, solve]


def main():
    parser = argparse.ArgumentParser(description="Quadratic Word Problems Generator (MCQ+Solve)")
    parser.add_argument("--samples", type=int, default=100, help="Number of QUESTIONS (each gives 2 rows)")
    parser.add_argument("--fresh", action="store_true", help="Overwrite file instead of appending")
    args = parser.parse_args()

    generators = [
        gen_consecutive_numbers,
        gen_sum_product,
        gen_age_problem,
        gen_reciprocal,
        gen_two_digit,
        gen_triangle,
        gen_rectangle_square,
        gen_picnic,
        gen_future_product,
        gen_difference_squares
    ]

    rows = []
    for _ in range(args.samples):
        rows.extend(random.choice(generators)()) 

    write_jsonl(rows, fresh=args.fresh)
    print(f"Generated {len(rows)} rows ({args.samples} questions) → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
