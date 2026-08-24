"""Generates a professional PDF plagiarism report using ReportLab."""
import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.config import settings

RISK_COLORS = {
    "Low": colors.HexColor("#16a34a"),
    "Medium": colors.HexColor("#ca8a04"),
    "High": colors.HexColor("#ea580c"),
    "Very High": colors.HexColor("#dc2626"),
}


def generate_report_pdf(
    comparison_id: int,
    user_name: str,
    file_a_name: str,
    file_b_name: str,
    scores: dict,
    explanation: list,
) -> str:
    """Builds the PDF and returns the file path."""
    os.makedirs(settings.REPORT_DIRECTORY, exist_ok=True)
    filename = f"report_comparison_{comparison_id}_{int(datetime.utcnow().timestamp())}.pdf"
    path = os.path.join(settings.REPORT_DIRECTORY, filename)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"], fontSize=18, spaceAfter=6
    )
    heading_style = ParagraphStyle(
        "Heading", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6
    )
    body_style = styles["BodyText"]

    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    story = []

    story.append(Paragraph("AI-Based Source Code Plagiarism Detection Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", body_style))
    story.append(Spacer(1, 0.4 * cm))

    meta_table = Table(
        [
            ["User", user_name],
            ["Source File A", file_a_name],
            ["Source File B", file_b_name],
            ["Comparison ID", str(comparison_id)],
        ],
        colWidths=[5 * cm, 10 * cm],
    )
    meta_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(meta_table)

    story.append(Paragraph("Similarity Scores", heading_style))
    score_rows = [
        ["Metric", "Score"],
        ["AST Similarity", f"{scores['ast_similarity']:.2f}%"],
        ["Token Similarity", f"{scores['token_similarity']:.2f}%"],
        ["Structural Similarity", f"{scores['structural_similarity']:.2f}%"],
        ["ML Score", f"{scores['ml_score']:.2f}%"],
        ["Final Plagiarism Score", f"{scores['final_score']:.2f}%"],
        ["Risk Level", scores["risk_level"]],
    ]
    score_table = Table(score_rows, colWidths=[8 * cm, 7 * cm])
    risk_color = RISK_COLORS.get(scores["risk_level"], colors.black)
    score_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (1, -1), (1, -1), risk_color),
                ("FONTNAME", (1, -1), (1, -1), "Helvetica-Bold"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(score_table)

    story.append(Paragraph("Detected Similar Structures", heading_style))
    for point in explanation:
        story.append(Paragraph(f"&bull; {point}", body_style))

    story.append(Paragraph("Analysis Method", heading_style))
    story.append(
        Paragraph(
            "Source files were parsed into Abstract Syntax Trees (AST), normalized to "
            "reduce the influence of variable naming and formatting, and compared using "
            "AST structural similarity, token similarity, cosine similarity over "
            "structural feature vectors, tree edit distance, and a Random Forest "
            "classifier trained on labeled code-pair examples. Scores were combined "
            "using a configurable weighted formula.",
            body_style,
        )
    )

    story.append(Spacer(1, 0.6 * cm))
    story.append(
        Paragraph(
            "<i>Note: this score indicates structural similarity between the submitted "
            "programs. It is an indicator to support human review, not definitive proof "
            "of academic misconduct.</i>",
            body_style,
        )
    )

    doc.build(story)
    return path
