"""
AST Feature Extractor

Extracts numeric structural features from a parsed AST, used both for
cosine-similarity comparison and as the ML model's input vector.
"""
import ast
from dataclasses import dataclass, asdict


FEATURE_NAMES = [
    "node_count",
    "max_depth",
    "num_functions",
    "num_loops",
    "num_if",
    "num_variables",
    "num_assignments",
    "num_operators",
    "num_calls",
    "num_returns",
    "num_classes",
    "num_imports",
]


@dataclass
class CodeFeatures:
    node_count: int = 0
    max_depth: int = 0
    num_functions: int = 0
    num_loops: int = 0
    num_if: int = 0
    num_variables: int = 0
    num_assignments: int = 0
    num_operators: int = 0
    num_calls: int = 0
    num_returns: int = 0
    num_classes: int = 0
    num_imports: int = 0

    def as_dict(self):
        return asdict(self)

    def as_vector(self):
        return [getattr(self, name) for name in FEATURE_NAMES]


_LOOP_TYPES = (ast.For, ast.While, ast.AsyncFor)
_OPERATOR_TYPES = (ast.BinOp, ast.BoolOp, ast.UnaryOp, ast.Compare, ast.AugAssign)


def extract_features(tree: ast.AST) -> CodeFeatures:
    features = CodeFeatures()
    seen_vars = set()
    max_depth = 0

    def walk(node, depth):
        nonlocal max_depth
        max_depth = max(max_depth, depth)
        features.node_count += 1

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            features.num_functions += 1
        elif isinstance(node, _LOOP_TYPES):
            features.num_loops += 1
        elif isinstance(node, ast.If):
            features.num_if += 1
        elif isinstance(node, ast.Assign):
            features.num_assignments += 1
        elif isinstance(node, ast.Call):
            features.num_calls += 1
        elif isinstance(node, ast.Return):
            features.num_returns += 1
        elif isinstance(node, ast.ClassDef):
            features.num_classes += 1
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            features.num_imports += 1
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store,)):
            seen_vars.add(node.id)

        if isinstance(node, _OPERATOR_TYPES):
            features.num_operators += 1

        for child in ast.iter_child_nodes(node):
            walk(child, depth + 1)

    walk(tree, 0)
    features.max_depth = max_depth
    features.num_variables = len(seen_vars)
    return features
