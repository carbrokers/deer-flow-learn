"""Markdown reporting for the Tech Decision Copilot demo."""

from __future__ import annotations

from .models import DecisionReport


def render_markdown_report(report: DecisionReport) -> str:
    lines = [
        "# Tech Decision Copilot Report",
        "",
        "## Problem",
        report.problem_statement,
        "",
    ]

    if report.needs_clarification:
        lines.extend(
            [
                "## Clarification Needed",
                "当前信息不足，先补齐这些前提：",
                *[f"- {item}" for item in report.missing_information],
                "",
            ]
        )

    lines.extend(
        [
            "## Evaluation Dimensions",
            *[f"- {item}" for item in report.evaluation_dimensions],
            "",
            "## Candidate Comparison",
            "| 方案 | 优势 | 代价 | 适用场景 |",
            "| --- | --- | --- | --- |",
        ]
    )
    for candidate in report.candidates:
        lines.append(
            f"| {candidate.option} | {'；'.join(candidate.pros[:2])} | {'；'.join(candidate.cons[:2])} | {candidate.best_for} |"
        )

    lines.extend(
        [
            "",
            "## Recommendation",
            f"- 推荐方案：{report.recommendation.option}",
            f"- 结论理由：{report.recommendation.rationale}",
            f"- 置信度：{report.recommendation.confidence}",
            "",
            "## Evidence",
            *[f"- `{item.source}` {item.summary} 支持：**{item.supports}**" for item in report.evidence],
            "",
            "## Risks",
            *[f"- {item}" for item in report.risks],
            "",
            "## Next Steps",
            *[f"- {item}" for item in report.follow_ups],
            "",
        ]
    )
    return "\n".join(lines)
