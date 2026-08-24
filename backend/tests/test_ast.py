"""Tests for the AST engine: normalization, features, similarity."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ast_engine.parser import parse_source, CodeParseError
from app.ast_engine.features import extract_features
from app.ast_engine.similarity import (
    ast_structural_similarity,
    token_similarity,
    structural_similarity,
    tree_edit_distance_similarity,
)

CODE_A = """
a = 10
b = 20
c = a + b
print(c)
"""

CODE_B = """
x = 10
y = 20
total = x + y
print(total)
"""

CODE_DIFFERENT = """
def greet(name):
    print("Hello, " + name)

greet("World")
"""


def test_parse_valid_code():
    parsed = parse_source(CODE_A)
    assert parsed.language == "python"


def test_parse_invalid_code_raises():
    try:
        parse_source("def broken(:\n    pass")
        assert False, "Expected CodeParseError"
    except CodeParseError:
        pass


def test_renamed_variables_are_highly_similar():
    tree_a = parse_source(CODE_A).tree
    tree_b = parse_source(CODE_B).tree
    ast_sim = ast_structural_similarity(tree_a, tree_b)
    tok_sim = token_similarity(tree_a, tree_b)
    assert ast_sim > 90, f"expected high AST similarity, got {ast_sim}"
    assert tok_sim > 90, f"expected high token similarity, got {tok_sim}"


def test_different_programs_are_less_similar():
    tree_a = parse_source(CODE_A).tree
    tree_c = parse_source(CODE_DIFFERENT).tree
    ast_sim = ast_structural_similarity(tree_a, tree_c)
    assert ast_sim < 90


def test_feature_extraction_counts():
    tree_a = parse_source(CODE_A).tree
    features = extract_features(tree_a)
    assert features.num_assignments == 3
    assert features.num_calls == 1


def test_tree_edit_distance_similarity_bounds():
    tree_a = parse_source(CODE_A).tree
    tree_b = parse_source(CODE_B).tree
    sim = tree_edit_distance_similarity(tree_a, tree_b)
    assert 0 <= sim <= 100
