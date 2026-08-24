"""
Preprocessing: converts a pair of source-code strings into the numeric
feature vector consumed by the ML model. Combines each program's own
structural feature vector with the AST/token/structural similarity scores
between them, so the model sees both "what each program looks like" and
"how similar they are".
"""
from typing import List, Tuple

from app.ast_engine.parser import parse_source, CodeParseError
from app.ast_engine.features import extract_features, FEATURE_NAMES
from app.ast_engine.similarity import (
    ast_structural_similarity,
    token_similarity,
    structural_similarity,
    tree_edit_distance_similarity,
)

VECTOR_FEATURE_NAMES = (
    [f"a_{n}" for n in FEATURE_NAMES]
    + [f"b_{n}" for n in FEATURE_NAMES]
    + ["ast_sim", "token_sim", "struct_sim", "ted_sim"]
)


def build_feature_vector(code_a: str, code_b: str, language: str = "python") -> List[float]:
    parsed_a = parse_source(code_a, language)
    parsed_b = parse_source(code_b, language)

    features_a = extract_features(parsed_a.tree)
    features_b = extract_features(parsed_b.tree)

    ast_sim = ast_structural_similarity(parsed_a.tree, parsed_b.tree)
    tok_sim = token_similarity(parsed_a.tree, parsed_b.tree)
    struct_sim = structural_similarity(features_a, features_b)
    ted_sim = tree_edit_distance_similarity(parsed_a.tree, parsed_b.tree)

    vector = (
        features_a.as_vector()
        + features_b.as_vector()
        + [ast_sim, tok_sim, struct_sim, ted_sim]
    )
    return vector


def build_dataset_matrix(pairs) -> Tuple[List[List[float]], List[int], List[str]]:
    """pairs: iterable of CodePair. Returns (X, y, base_problem_ids)."""
    X, y, groups = [], [], []
    for pair in pairs:
        try:
            vec = build_feature_vector(pair.code_a, pair.code_b)
        except CodeParseError:
            continue
        X.append(vec)
        y.append(pair.label)
        groups.append(pair.base_problem)
    return X, y, groups
