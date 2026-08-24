"""
Similarity Engine

Implements the multiple similarity techniques described in the spec:
  - AST structural similarity (sequence matching over normalized structure)
  - Token similarity (over normalized token stream)
  - Cosine similarity (over numeric structural feature vectors)
  - A simplified Tree Edit Distance (Zhang-Shasha style, capped for
    performance on typical academic-project-sized submissions)

All individual scores are normalized to a common 0-100 scale.
"""
import ast
import math
from difflib import SequenceMatcher
from typing import List

from app.ast_engine.normalizer import normalize, to_structure_string
from app.ast_engine.features import CodeFeatures

MAX_TED_NODES = 400  # safety cap so tree edit distance stays tractable


def _clamp_pct(value: float) -> float:
    return max(0.0, min(100.0, round(value, 2)))


def ast_structural_similarity(tree_a: ast.AST, tree_b: ast.AST) -> float:
    """Sequence-matcher ratio over the normalized structure strings."""
    norm_a = normalize(tree_a)
    norm_b = normalize(tree_b)
    struct_a = to_structure_string(norm_a)
    struct_b = to_structure_string(norm_b)
    ratio = SequenceMatcher(None, struct_a, struct_b).ratio()
    return _clamp_pct(ratio * 100)


def _tokenize_normalized(tree: ast.AST) -> List[str]:
    norm = normalize(tree)
    tokens = []

    def walk(node):
        tokens.append(type(node).__name__)
        # Include normalized identifiers/constant *types* (not raw literal
        # values) so token similarity still reflects structure, not text.
        if isinstance(node, ast.Name):
            tokens.append(node.id)
        if isinstance(node, ast.Constant):
            tokens.append(f"CONST_{type(node.value).__name__}")
        for child in ast.iter_child_nodes(node):
            walk(child)

    walk(norm)
    return tokens


def token_similarity(tree_a: ast.AST, tree_b: ast.AST) -> float:
    tokens_a = _tokenize_normalized(tree_a)
    tokens_b = _tokenize_normalized(tree_b)
    ratio = SequenceMatcher(None, tokens_a, tokens_b).ratio()
    return _clamp_pct(ratio * 100)


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def structural_similarity(features_a: CodeFeatures, features_b: CodeFeatures) -> float:
    cos = cosine_similarity(features_a.as_vector(), features_b.as_vector())
    return _clamp_pct(cos * 100)


def _tree_to_list(tree: ast.AST, limit: int) -> List[str]:
    """Flatten a tree into a bounded pre-order node-type list for TED."""
    out = []

    def walk(node):
        if len(out) >= limit:
            return
        out.append(type(node).__name__)
        for child in ast.iter_child_nodes(node):
            if len(out) >= limit:
                return
            walk(child)

    walk(tree)
    return out


def tree_edit_distance_similarity(tree_a: ast.AST, tree_b: ast.AST) -> float:
    """
    Simplified tree edit distance: compares bounded, normalized pre-order
    node-type sequences using classic Levenshtein edit distance as a
    tractable proxy for full Zhang-Shasha tree edit distance. This captures
    insertions/deletions/substitutions of structural nodes, which is what
    matters for plagiarism-style comparisons, while staying fast enough to
    run interactively on typical student-sized submissions.
    """
    norm_a = normalize(tree_a)
    norm_b = normalize(tree_b)
    seq_a = _tree_to_list(norm_a, MAX_TED_NODES)
    seq_b = _tree_to_list(norm_b, MAX_TED_NODES)

    n, m = len(seq_a), len(seq_b)
    if n == 0 and m == 0:
        return 100.0
    if n == 0 or m == 0:
        return 0.0

    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if seq_a[i - 1] == seq_b[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # deletion
                dp[i][j - 1] + 1,      # insertion
                dp[i - 1][j - 1] + cost,  # substitution
            )

    edit_distance = dp[n][m]
    max_len = max(n, m)
    similarity = 1 - (edit_distance / max_len)
    return _clamp_pct(similarity * 100)
