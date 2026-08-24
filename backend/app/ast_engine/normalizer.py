"""
AST Normalizer

Reduces the influence of superficial differences (variable names, function
names, formatting, comments, whitespace) while preserving the information
that matters for structural comparison: operators, control flow, function
structure, expressions, loops, conditions, calls.

Strategy: walk the AST and rewrite it into a normalized token sequence /
skeleton tree where identifiers are replaced by role-based placeholders
(VAR1, VAR2, FUNC1, ...) assigned in order of first appearance. This keeps
the *shape* of the program (how many distinct variables, in what order they
interact) without keying on their literal names — comments and formatting
never enter the AST in the first place, so nothing extra needs to be done
for those.
"""
import ast
from typing import Dict


class IdentifierNormalizer(ast.NodeTransformer):
    """Replaces variable/function identifiers with positional placeholders."""

    def __init__(self):
        self.var_map: Dict[str, str] = {}
        self.func_map: Dict[str, str] = {}
        self._var_counter = 0
        self._func_counter = 0

    def _norm_var(self, name: str) -> str:
        if name in ("self", "cls"):
            return name
        if name not in self.var_map:
            self._var_counter += 1
            self.var_map[name] = f"VAR{self._var_counter}"
        return self.var_map[name]

    def _norm_func(self, name: str) -> str:
        if name not in self.func_map:
            self._func_counter += 1
            self.func_map[name] = f"FUNC{self._func_counter}"
        return self.func_map[name]

    def visit_FunctionDef(self, node: ast.FunctionDef):
        node.name = self._norm_func(node.name)
        for arg in node.args.args:
            arg.arg = self._norm_var(arg.arg)
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)

    def visit_Name(self, node: ast.Name):
        node.id = self._norm_var(node.id)
        return node

    def visit_Call(self, node: ast.Call):
        # Normalize call target names when they refer to user-defined funcs
        if isinstance(node.func, ast.Name) and node.func.id in self.func_map:
            node.func.id = self.func_map[node.func.id]
        self.generic_visit(node)
        return node

    def visit_arg(self, node: ast.arg):
        node.arg = self._norm_var(node.arg)
        return node


def normalize(tree: ast.AST) -> ast.AST:
    """Return a structurally-normalized copy of the AST."""
    import copy

    tree_copy = copy.deepcopy(tree)
    normalizer = IdentifierNormalizer()
    return normalizer.visit(tree_copy)


def to_structure_string(tree: ast.AST) -> str:
    """
    Serialize a normalized AST into a compact string capturing only node
    types and structure (no line numbers, no literal values except types),
    suitable for token-level and tree-edit-distance comparison.
    """
    parts = []

    def walk(node, depth):
        node_name = type(node).__name__
        parts.append("  " * depth + node_name)
        for child in ast.iter_child_nodes(node):
            walk(child, depth + 1)

    walk(tree, 0)
    return "\n".join(parts)
