"""
Comparison Service

Orchestrates the full detection pipeline for a pair of code submissions:
parse -> normalize -> extract features -> compute similarity scores ->
ML prediction -> weighted final score -> risk classification -> explanation.
"""
from app.config import settings
from app.ast_engine.parser import parse_source, CodeParseError
from app.ast_engine.features import extract_features
from app.ast_engine.similarity import (
    ast_structural_similarity,
    token_similarity,
    structural_similarity,
    tree_edit_distance_similarity,
)
from app.ml.predict import predict_ml_score, MLPredictionError


class ComparisonError(Exception):
    pass


def classify_risk(score: float) -> str:
    if score <= settings.RISK_LOW_MAX:
        return "Low"
    if score <= settings.RISK_MEDIUM_MAX:
        return "Medium"
    if score <= settings.RISK_HIGH_MAX:
        return "High"
    return "Very High"


def build_explanation(ast_sim, tok_sim, struct_sim, ted_sim, features_a, features_b) -> list:
    points = []
    if ast_sim >= 70:
        points.append(f"AST structural similarity is high ({ast_sim:.1f}%), suggesting closely matching control flow and program structure.")
    if tok_sim >= 70:
        points.append(f"Normalized token sequences are highly similar ({tok_sim:.1f}%), even after removing variable-name differences.")
    if abs(features_a.num_functions - features_b.num_functions) == 0 and features_a.num_functions > 0:
        points.append(f"Both programs define the same number of functions ({features_a.num_functions}).")
    if abs(features_a.num_loops - features_b.num_loops) == 0 and features_a.num_loops > 0:
        points.append(f"Both programs use the same number of loop constructs ({features_a.num_loops}).")
    if ted_sim >= 70:
        points.append(f"Tree edit distance similarity is high ({ted_sim:.1f}%), indicating few structural edits would transform one program into the other.")
    if struct_sim >= 70:
        points.append(f"Structural feature vectors (node counts, depth, operators) are closely aligned ({struct_sim:.1f}%).")
    if not points:
        points.append("No strong structural overlap was detected between the two submissions.")
    return points


def compare_code(code_a: str, code_b: str, language: str = "python") -> dict:
    try:
        parsed_a = parse_source(code_a, language)
        parsed_b = parse_source(code_b, language)
    except CodeParseError as exc:
        raise ComparisonError(str(exc)) from exc

    features_a = extract_features(parsed_a.tree)
    features_b = extract_features(parsed_b.tree)

    ast_sim = ast_structural_similarity(parsed_a.tree, parsed_b.tree)
    tok_sim = token_similarity(parsed_a.tree, parsed_b.tree)
    struct_sim = structural_similarity(features_a, features_b)
    ted_sim = tree_edit_distance_similarity(parsed_a.tree, parsed_b.tree)

    try:
        ml_score = predict_ml_score(code_a, language, code_b)
    except MLPredictionError:
        # Fall back gracefully so the rest of the pipeline still returns a result.
        ml_score = round((ast_sim + tok_sim + struct_sim) / 3, 2)

    final_score = round(
        ast_sim * settings.WEIGHT_AST
        + tok_sim * settings.WEIGHT_TOKEN
        + struct_sim * settings.WEIGHT_STRUCTURAL
        + ml_score * settings.WEIGHT_ML,
        2,
    )
    risk_level = classify_risk(final_score)
    explanation = build_explanation(ast_sim, tok_sim, struct_sim, ted_sim, features_a, features_b)

    return {
        "ast_similarity": ast_sim,
        "token_similarity": tok_sim,
        "structural_similarity": struct_sim,
        "tree_edit_distance_similarity": ted_sim,
        "ml_score": ml_score,
        "final_score": final_score,
        "risk_level": risk_level,
        "explanation": explanation,
        "features_a": features_a.as_dict(),
        "features_b": features_b.as_dict(),
    }
