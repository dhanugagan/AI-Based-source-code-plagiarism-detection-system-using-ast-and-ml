"""
Dataset Generator

Builds a labeled dataset of code-pair feature vectors for training the
plagiarism classifier, using the five categories described in the spec:
  1. Original code            (two genuinely different implementations)
  2. Renamed-variable code     (same logic, different names)          -> similar
  3. Reformatted code          (same code, different formatting)      -> similar
  4. Modified code             (same logic, small changes)            -> similar
  5. Different algorithm       (same problem, different approach)     -> NOT similar

Programs are generated from a small library of "base problems" so that
transformed variants can be produced programmatically instead of hand-typed,
while keeping the dataset small enough to ship as a reference example.

IMPORTANT: transformed variants of the same base program are kept together
on the same side of the train/test split (see ml/train.py) to avoid data
leakage.
"""
import random
import textwrap
from dataclasses import dataclass
from typing import List, Tuple

random.seed(42)

# ---------------------------------------------------------------------------
# Base problems: each has a canonical implementation and a genuinely
# different alternative implementation that solves the same problem.
# ---------------------------------------------------------------------------
BASE_PROBLEMS = {
    "sum_two": {
        "canonical": """
            a = 10
            b = 20
            c = a + b
            print(c)
        """,
        "alternative": """
            def add(x, y):
                return x + y

            result = add(10, 20)
            print(result)
        """,
    },
    "factorial": {
        "canonical": """
            def factorial(n):
                result = 1
                for i in range(1, n + 1):
                    result = result * i
                return result

            print(factorial(5))
        """,
        "alternative": """
            def factorial(n):
                if n <= 1:
                    return 1
                return n * factorial(n - 1)

            print(factorial(5))
        """,
    },
    "max_in_list": {
        "canonical": """
            numbers = [4, 2, 9, 1, 7]
            largest = numbers[0]
            for num in numbers:
                if num > largest:
                    largest = num
            print(largest)
        """,
        "alternative": """
            numbers = [4, 2, 9, 1, 7]
            print(max(numbers))
        """,
    },
    "fibonacci": {
        "canonical": """
            def fib(n):
                a, b = 0, 1
                for _ in range(n):
                    a, b = b, a + b
                return a

            print(fib(10))
        """,
        "alternative": """
            def fib(n):
                if n <= 1:
                    return n
                return fib(n - 1) + fib(n - 2)

            print(fib(10))
        """,
    },
    "is_prime": {
        "canonical": """
            def is_prime(n):
                if n < 2:
                    return False
                for i in range(2, n):
                    if n % i == 0:
                        return False
                return True

            print(is_prime(17))
        """,
        "alternative": """
            def is_prime(n):
                if n < 2:
                    return False
                i = 2
                while i * i <= n:
                    if n % i == 0:
                        return False
                    i += 1
                return True

            print(is_prime(17))
        """,
    },
    "reverse_string": {
        "canonical": """
            text = "hello world"
            reversed_text = text[::-1]
            print(reversed_text)
        """,
        "alternative": """
            text = "hello world"
            chars = list(text)
            chars.reverse()
            print("".join(chars))
        """,
    },
    "sum_list": {
        "canonical": """
            values = [1, 2, 3, 4, 5]
            total = 0
            for v in values:
                total += v
            print(total)
        """,
        "alternative": """
            values = [1, 2, 3, 4, 5]
            print(sum(values))
        """,
    },
    "count_vowels": {
        "canonical": """
            word = "engineering"
            vowels = "aeiou"
            count = 0
            for ch in word:
                if ch in vowels:
                    count += 1
            print(count)
        """,
        "alternative": """
            word = "engineering"
            vowels = set("aeiou")
            count = sum(1 for ch in word if ch in vowels)
            print(count)
        """,
    },
}

VAR_NAME_POOLS = [
    ["a", "b", "c"],
    ["x", "y", "total"],
    ["p", "q", "r"],
    ["val1", "val2", "outcome"],
    ["m", "n", "res"],
]


def _dedent(code: str) -> str:
    return textwrap.dedent(code).strip() + "\n"


def rename_variables(code: str) -> str:
    """Naive but effective variable-renaming transform for short snippets."""
    import re

    tokens = sorted(set(re.findall(r"\b[a-zA-Z_]\w*\b", code)), key=len, reverse=True)
    keywords = {
        "def", "return", "for", "in", "range", "if", "else", "elif", "while",
        "print", "True", "False", "None", "import", "from", "and", "or",
        "not", "break", "continue", "len", "max", "min", "sum", "list",
        "set", "str", "int",
    }
    identifiers = [t for t in tokens if t not in keywords and not t.isdigit()]
    renamed = code
    for i, ident in enumerate(identifiers):
        placeholder = f"__ID{i}__"
        renamed = re.sub(rf"\b{re.escape(ident)}\b", placeholder, renamed)
    pool = random.choice(VAR_NAME_POOLS) + [f"var{i}" for i in range(20)]
    for i, ident in enumerate(identifiers):
        placeholder = f"__ID{i}__"
        renamed = renamed.replace(placeholder, pool[i % len(pool)] + str(i))
    return renamed


def reformat(code: str) -> str:
    """Change whitespace/formatting without touching logic."""
    lines = code.strip("\n").split("\n")
    out = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        indent = len(line) - len(line.lstrip())
        out.append(" " * indent + stripped + "  ")
    out.append("")
    return "\n".join(out)


def modify_slightly(code: str) -> str:
    """Add a harmless extra statement (small change, same logic)."""
    lines = _dedent(code).split("\n")
    insert_at = min(2, len(lines) - 1)
    lines.insert(insert_at, "    _unused = 0" if lines[0].startswith("def") else "_unused = 0")
    return "\n".join(lines)


@dataclass
class CodePair:
    code_a: str
    code_b: str
    label: int  # 1 = similar/plagiarized-structure, 0 = not similar
    category: str
    base_problem: str


def generate_dataset() -> List[CodePair]:
    pairs: List[CodePair] = []

    for name, problem in BASE_PROBLEMS.items():
        canonical = _dedent(problem["canonical"])
        alternative = _dedent(problem["alternative"])

        # 1. Renamed-variable pair -> similar
        pairs.append(CodePair(canonical, rename_variables(canonical), 1, "renamed_variable", name))

        # 2. Reformatted pair -> similar
        pairs.append(CodePair(canonical, reformat(canonical), 1, "reformatted", name))

        # 3. Modified (small change) pair -> similar
        pairs.append(CodePair(canonical, modify_slightly(canonical), 1, "modified", name))

        # 4. Renamed + reformatted combined -> similar (harder case)
        combined = reformat(rename_variables(canonical))
        pairs.append(CodePair(canonical, combined, 1, "renamed_and_reformatted", name))

        # 5. Different algorithm, same problem -> NOT similar (structurally)
        pairs.append(CodePair(canonical, alternative, 0, "different_algorithm", name))

    # 6. Cross-problem pairs (totally unrelated programs) -> NOT similar
    names = list(BASE_PROBLEMS.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            code_a = _dedent(BASE_PROBLEMS[names[i]]["canonical"])
            code_b = _dedent(BASE_PROBLEMS[names[j]]["canonical"])
            pairs.append(CodePair(code_a, code_b, 0, "unrelated", f"{names[i]}_vs_{names[j]}"))

    random.shuffle(pairs)
    return pairs
