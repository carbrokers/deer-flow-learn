"""Workflow for the Tech Decision Copilot demo."""

from __future__ import annotations

from .knowledge import frontend_candidates, frontend_evidence, sdk_candidates, sdk_evidence
from .memory import SessionMemory
from .models import DecisionReport, Recommendation


def _extract_constraints(question: str) -> list[str]:
    mapping = {
        "原型": "优先原型速度",
        "原型阶段": "优先原型速度",
        "SEO": "重视 SEO",
        "ssr": "团队具备 SSR 场景",
        "SSR": "团队具备 SSR 场景",
        "长期": "计划长期运营",
        "流式": "需要流式输出",
        "多模型": "需要多模型切换",
        "熟悉": "团队已有相关经验",
    }
    constraints: list[str] = []
    for key, value in mapping.items():
        if key in question and value not in constraints:
            constraints.append(value)
    return constraints


def _clarification_report(question: str) -> DecisionReport:
    return DecisionReport(
        problem_statement=question,
        evaluation_dimensions=["业务目标", "团队能力", "性能与稳定性", "运维约束", "数据规模"],
        candidates=[],
        evidence=[],
        recommendation=Recommendation(
            option="暂不建议直接拍板",
            rationale="缺少业务形态、数据规模、团队经验和部署约束，任何数据库建议都会过早收敛。",
            confidence="low",
        ),
        risks=[
            "在目标不明确时先选型，后续迁移成本通常比早期多问几个问题更高。",
        ],
        follow_ups=[
            "先明确读写比例、事务要求、部署环境和团队运维能力。",
            "补充是否需要强一致事务、搜索能力、向量检索或多租户隔离。",
        ],
        needs_clarification=True,
        missing_information=[
            "核心业务场景是什么，OLTP、分析型还是混合场景？",
            "数据规模、读写比例和一致性要求是什么？",
            "团队更熟悉托管服务还是自运维数据库？",
        ],
    )


def _frontend_report(question: str, constraints: list[str]) -> DecisionReport:
    recommend_next = any(token in question for token in ["SEO", "SSR", "长期"])
    recommendation = Recommendation(
        option="Next.js" if recommend_next else "Vite + React",
        rationale=(
            "题目已经明确包含 SSR、SEO 或长期运营，框架内建的服务端与路由能力更能减少后续重构。"
            if recommend_next
            else "当前重点是 AI 产品原型验证，先降低框架负担、尽快验证交互和价值假设更合适。"
        ),
        confidence="medium",
    )
    return DecisionReport(
        problem_statement=question,
        evaluation_dimensions=["原型速度", "SEO / SSR 需求", "工程复杂度", "长期演进成本", "团队心智负担"],
        candidates=frontend_candidates(),
        evidence=frontend_evidence(),
        recommendation=recommendation,
        risks=[
            "如果先选 Vite + React，后续补 SSR 与内容营销链路时会增加迁移成本。",
            "如果过早选 Next.js，原型期可能把时间花在框架约束和部署细节上。",
        ],
        follow_ups=[
            "用一个真实页面验证首屏、登录态、流式回答和部署流程。",
            "把 SEO、SSR、内容营销和后台管理是否在第一阶段上线说清楚。",
        ],
    )


def _sdk_report(question: str, constraints: list[str]) -> DecisionReport:
    return DecisionReport(
        problem_statement=question,
        evaluation_dimensions=["流式输出体验", "多模型适配", "底层控制力", "前端集成成本", "后续迁移风险"],
        candidates=sdk_candidates(),
        evidence=sdk_evidence(),
        recommendation=Recommendation(
            option="Vercel AI SDK",
            rationale="题目明确要求流式输出和多模型切换，先用更高层抽象换取交付速度更划算。",
            confidence="medium",
        ),
        risks=[
            "抽象层会掩盖部分 provider 特性，遇到底层能力差异时需要补 escape hatch。",
            "如果未来完全迁移离开该抽象层，需要评估消息协议和流式适配成本。",
        ],
        follow_ups=[
            "先做一个最小聊天链路，验证流式更新、工具调用和 provider fallback。",
            "列出你真正需要的底层能力，判断是否会被 SDK 抽象卡住。",
        ],
    )


def run_decision_workflow(question: str, memory: SessionMemory | None = None) -> DecisionReport:
    normalized = question.strip()
    constraints = _extract_constraints(normalized)

    if "Next.js" in normalized and "Vite" in normalized:
        report = _frontend_report(normalized, constraints)
    elif "OpenAI" in normalized and "Vercel AI SDK" in normalized:
        report = _sdk_report(normalized, constraints)
    else:
        report = _clarification_report(normalized)

    if memory is not None:
        memory.record(normalized, constraints, report.recommendation.option)

    return report
