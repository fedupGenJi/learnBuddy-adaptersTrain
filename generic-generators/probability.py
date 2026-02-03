import json
import random
import argparse
from pathlib import Path
from fractions import Fraction

OUTPUT_PATH = Path("data/probability/raw/probability_train.jsonl")

SYSTEM_GEN = "You are an NEB Grade 10 Mathematics question generator. Output MUST be STRICT JSON only. No extra text."
SYSTEM_SOLVE = "You are an NEB Grade 10 Mathematics tutor. Output MUST be STRICT JSON only. No extra text."

# ------------------ Utilities ------------------

def write_jsonl(rows, fresh=False):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if fresh else "a"
    with open(OUTPUT_PATH, mode, encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def frac_str(x):
    return f"{x.numerator}/{x.denominator}"

def mcq_row(question, options, correct, explanation, distractors, difficulty):
    return {
        "chapter": "probability",
        "task": "generate_mcq",
        "difficulty": difficulty,
        "messages": [
            {"role": "system", "content": SYSTEM_GEN},
            {"role": "user", "content":
                "Task: generate_mcq\n"
                "Chapter: Probability\n"
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
            "meta": {"chapter": "probability", "difficulty": difficulty}
        }
    }

def solve_row(question, given, steps, final_answer, difficulty):
    return {
        "chapter": "probability",
        "task": "solve",
        "difficulty": difficulty,
        "messages": [
            {"role": "system", "content": SYSTEM_SOLVE},
            {"role": "user", "content": f"Solve with full steps:\n{question}"}
        ],
        "response": {
            "given": given,
            "to_find": "Required probability",
            "steps": steps,
            "final_answer": final_answer
        }
    }

# ------------------ Type 1: Mutually Exclusive ------------------

def gen_mutually_exclusive():
    total = random.choice([20, 30, 40])
    a = random.randint(5, total//2)
    b = random.randint(5, total//2)
    difficulty = 1

    p = Fraction(a + b, total)

    question = f"In a class of {total} students, {a} play football and {b} play volleyball. No student plays both games. Find the probability that a randomly chosen student plays football or volleyball."

    correct = p
    wrong1 = Fraction(a, total)      # only A
    wrong2 = Fraction(b, total)      # only B
    wrong3 = Fraction(a*b, total*total)

    options = {
        "A": frac_str(wrong1),
        "B": frac_str(wrong2),
        "C": frac_str(correct),
        "D": frac_str(wrong3)
    }

    distractors = {
        "A": {"tag": "only_A", "why": "Calculated P(A) instead of P(A ∪ B)."},
        "B": {"tag": "only_B", "why": "Calculated P(B) instead of P(A ∪ B)."},
        "D": {"tag": "multiplication_error", "why": "Used multiplication instead of addition."}
    }

    steps = [
        "Since events are mutually exclusive:",
        "P(A ∪ B) = P(A) + P(B)",
        f"= {a}/{total} + {b}/{total} = {(a+b)}/{total}"
    ]

    return [
        mcq_row(question, options, "C", "Add probabilities of mutually exclusive events.", distractors, difficulty),
        solve_row(question, f"n(S)={total}, n(A)={a}, n(B)={b}", steps, frac_str(correct), difficulty)
    ]

# ------------------ Type 2: Addition Law (Not exclusive) ------------------

def gen_addition_law():
    total = 50
    a = random.randint(15, 25)
    b = random.randint(15, 25)
    both = random.randint(5, min(a,b)-1)
    difficulty = 2

    p = Fraction(a + b - both, total)

    question = f"In a group of {total} students, {a} like tea, {b} like coffee and {both} like both. Find the probability that a student likes tea or coffee."

    wrong1 = Fraction(a+b, total)
    wrong2 = Fraction(a+b+both, total)
    wrong3 = Fraction(both, total)

    options = {
        "A": frac_str(wrong1),
        "B": frac_str(wrong2),
        "C": frac_str(p),
        "D": frac_str(wrong3)
    }

    distractors = {
        "A": {"tag": "ignored_intersection", "why": "Did not subtract common students."},
        "B": {"tag": "double_added", "why": "Added intersection again."},
        "D": {"tag": "only_intersection", "why": "Used only common part."}
    }

    steps = [
        "P(A ∪ B) = P(A) + P(B) − P(A ∩ B)",
        f"= {a}/{total} + {b}/{total} − {both}/{total}",
        f"= {(a+b-both)}/{total}"
    ]

    return [
        mcq_row(question, options, "C", "Use addition law of probability.", distractors, difficulty),
        solve_row(question, f"A={a}, B={b}, A∩B={both}, S={total}", steps, frac_str(p), difficulty)
    ]

# ------------------ Type 3: Independent (With Replacement) ------------------

def gen_independent():
    red = random.randint(3,6)
    blue = random.randint(3,6)
    total = red + blue
    difficulty = 2

    p = Fraction(red, total) * Fraction(red, total)

    question = f"A bag contains {red} red and {blue} blue balls. Two balls are drawn one after another with replacement. Find the probability that both are red."

    wrong1 = Fraction(red, total)
    wrong2 = Fraction(red*(red-1), total*(total-1))
    wrong3 = Fraction(1, total)

    options = {
        "A": frac_str(wrong1),
        "B": frac_str(p),
        "C": frac_str(wrong2),
        "D": frac_str(wrong3)
    }

    distractors = {
        "A": {"tag": "single_event", "why": "Calculated probability for one draw only."},
        "C": {"tag": "without_replacement", "why": "Used dependent probability formula."},
        "D": {"tag": "random_guess", "why": "Random incorrect fraction."}
    }

    steps = [
        "With replacement → Independent events",
        "P(A ∩ B) = P(A) × P(B)",
        f"= {red}/{total} × {red}/{total}"
    ]

    return [
        mcq_row(question, options, "B", "Multiply probabilities for independent events.", distractors, difficulty),
        solve_row(question, f"Red={red}, Total={total}", steps, frac_str(p), difficulty)
    ]

# ------------------ Type 4: Dependent (Without Replacement) ------------------

def gen_dependent():
    red = random.randint(4,7)
    blue = random.randint(3,6)
    total = red + blue
    difficulty = 2

    p = Fraction(red, total) * Fraction(red-1, total-1)

    question = f"A bag contains {red} red and {blue} blue balls. Two balls are drawn without replacement. Find the probability that both are red."

    wrong1 = Fraction(red, total)**2
    wrong2 = Fraction(red, total)
    wrong3 = Fraction(1, total)

    options = {
        "A": frac_str(wrong1),
        "B": frac_str(wrong2),
        "C": frac_str(p),
        "D": frac_str(wrong3)
    }

    distractors = {
        "A": {"tag": "assumed_independent", "why": "Used replacement formula."},
        "B": {"tag": "single_event", "why": "Used probability of first draw only."},
        "D": {"tag": "random_error", "why": "Random incorrect value."}
    }

    steps = [
        "Without replacement → Dependent events",
        f"P = {red}/{total} × {red-1}/{total-1}"
    ]

    return [
        mcq_row(question, options, "C", "Multiply conditional probabilities.", distractors, difficulty),
        solve_row(question, f"Red={red}, Blue={blue}", steps, frac_str(p), difficulty)
    ]

# ------------------ Type 5: Tree Diagram ------------------

def gen_tree():
    boys = random.randint(3,6)
    girls = random.randint(3,6)
    total = boys + girls
    difficulty = 3

    p = Fraction(boys, total) * Fraction(girls, total-1)

    question = f"A box contains {boys} boys' cards and {girls} girls' cards. Two cards are drawn without replacement. Find the probability that first is a boy and second is a girl (using tree diagram)."

    wrong1 = Fraction(boys, total) * Fraction(girls, total)
    wrong2 = Fraction(girls, total) * Fraction(boys, total-1)
    wrong3 = Fraction(boys+girls, total)

    options = {
        "A": frac_str(wrong1),
        "B": frac_str(p),
        "C": frac_str(wrong2),
        "D": frac_str(wrong3)
    }

    distractors = {
        "A": {"tag": "replacement_error", "why": "Used same denominator twice."},
        "C": {"tag": "order_error", "why": "Reversed order."},
        "D": {"tag": "invalid_probability", "why": "Probability cannot be 1."}
    }

    steps = [
        "Using tree diagram:",
        f"P(Boy first) = {boys}/{total}",
        f"P(Girl second) = {girls}/{total-1}",
        "Multiply both probabilities."
    ]

    return [
        mcq_row(question, options, "B", "Multiply branch probabilities from tree diagram.", distractors, difficulty),
        solve_row(question, f"Boys={boys}, Girls={girls}", steps, frac_str(p), difficulty)
    ]

# ------------------ Main ------------------

def main():
    parser = argparse.ArgumentParser(description="Probability dataset generator")
    parser.add_argument("--samples", type=int, default=50)
    parser.add_argument("--fresh", action="store_true")
    args = parser.parse_args()

    generators = [
        gen_mutually_exclusive,
        gen_addition_law,
        gen_independent,
        gen_dependent,
        gen_tree
    ]

    rows = []

    for _ in range(args.samples):
        gen = random.choice(generators)
        rows.extend(gen())

    write_jsonl(rows, fresh=args.fresh)

    print(f"Generated {len(rows)} rows ({args.samples} questions) at {OUTPUT_PATH}")

if __name__ == "__main__":
    main()