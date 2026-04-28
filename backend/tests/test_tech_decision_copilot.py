"""Tests for the Tech Decision Copilot learning demo."""

from __future__ import annotations

from tech_decision_copilot.cli import main
from tech_decision_copilot.memory import SessionMemory
from tech_decision_copilot.workflow import run_decision_workflow


def test_frontend_stack_comparison_returns_structured_recommendation():
    report = run_decision_workflow(
        "前端 AI 产品原型阶段，使用 Next.js 还是 Vite + React？",
    )

    assert report.problem_statement.startswith("前端 AI 产品原型阶段")
    assert report.recommendation.option in {"Next.js", "Vite + React"}
    assert report.evaluation_dimensions
    assert len(report.candidates) == 2
    assert report.recommendation.rationale
    assert report.risks
    assert report.evidence


def test_model_integration_comparison_includes_reasons_and_risks():
    report = run_decision_workflow(
        "做一个需要流式输出和多模型切换的 AI 应用，接入 OpenAI 官方 SDK 还是 Vercel AI SDK？",
    )

    assert {candidate.option for candidate in report.candidates} == {
        "OpenAI SDK",
        "Vercel AI SDK",
    }
    assert "流式输出" in " ".join(report.evaluation_dimensions)
    assert report.recommendation.option == "Vercel AI SDK"
    assert any(risk for risk in report.risks if "抽象" in risk or "迁移" in risk)


def test_insufficient_information_returns_missing_prerequisites():
    report = run_decision_workflow("数据库选型应该怎么选？")

    assert report.needs_clarification is True
    assert report.missing_information
    assert report.recommendation.option == "暂不建议直接拍板"


def test_constraint_change_can_flip_recommendation():
    prototype_report = run_decision_workflow(
        "前端 AI 产品原型阶段，使用 Next.js 还是 Vite + React？",
    )
    production_report = run_decision_workflow(
        "团队已经熟悉 SSR，计划长期运营并且重视 SEO 的 AI 产品，使用 Next.js 还是 Vite + React？",
    )

    assert prototype_report.recommendation.option == "Vite + React"
    assert production_report.recommendation.option == "Next.js"


def test_session_memory_tracks_recent_constraints():
    memory = SessionMemory()

    run_decision_workflow(
        "团队已经熟悉 SSR，计划长期运营并且重视 SEO 的 AI 产品，使用 Next.js 还是 Vite + React？",
        memory=memory,
    )

    snapshot = memory.snapshot()
    assert snapshot["questions"]
    assert snapshot["constraints"]
    assert "SSR" in " ".join(snapshot["constraints"])


def test_cli_prints_markdown_report(capsys):
    exit_code = main(
        [
            "--question",
            "前端 AI 产品原型阶段，使用 Next.js 还是 Vite + React？",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "# Tech Decision Copilot Report" in captured.out
    assert "## Recommendation" in captured.out
    assert "| 方案 |" in captured.out
