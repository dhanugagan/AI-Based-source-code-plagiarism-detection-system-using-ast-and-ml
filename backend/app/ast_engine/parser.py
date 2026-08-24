"""
AST Parser

Wraps Python's built-in `ast` module. Source code is only ever parsed for
static analysis — it is never executed. Architecture allows a
language-specific parser to be plugged in later (see PARSERS registry) for
Java/C/C++/JavaScript without pretending Python's `ast` module can parse them.
"""
import ast
from dataclasses import dataclass


class CodeParseError(Exception):
    """Raised when source code cannot be parsed into a valid AST."""


@dataclass
class ParsedProgram:
    source: str
    tree: ast.AST
    language: str


def parse_python(source: str) -> ParsedProgram:
    if source is None or source.strip() == "":
        raise CodeParseError("Source code is empty.")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise CodeParseError(f"Syntax error while parsing source: {exc}") from exc
    return ParsedProgram(source=source, tree=tree, language="python")


# Registry so additional languages can be added without touching call sites.
PARSERS = {
    "python": parse_python,
}


def parse_source(source: str, language: str = "python") -> ParsedProgram:
    language = (language or "python").lower()
    if language not in PARSERS:
        raise CodeParseError(
            f"Unsupported language '{language}'. Supported languages: {list(PARSERS.keys())}"
        )
    return PARSERS[language](source)
