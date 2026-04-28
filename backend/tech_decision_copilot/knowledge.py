"""Curated knowledge cards used by the demo workflow.

This is intentionally local and deterministic so the demo can run without
external search. It acts like a lightweight replacement for a research tool.
"""

from __future__ import annotations

from .models import CandidateAnalysis, EvidenceItem


def frontend_candidates() -> list[CandidateAnalysis]:
    return [
        CandidateAnalysis(
            option="Next.js",
            pros=[
                "SSR、RSC 和路由约定完整，适合从原型直接过渡到长期产品。",
                "SEO、首屏性能和服务端集成方案更成熟。",
                "适合需要内容营销、登录态和后端聚合的产品。",
            ],
            cons=[
                "框架约束更强，原型期会背上更多目录结构和部署心智负担。",
                "如果只是快速验证交互，服务端能力可能暂时用不上。",
            ],
            best_for="重视 SEO、SSR、长期运营和全栈一致性的团队。",
        ),
        CandidateAnalysis(
            option="Vite + React",
            pros=[
                "启动快、脚手架轻，适合快速做交互原型和试验新想法。",
                "前端边界清晰，团队可先把精力放在 AI 工作流和产品验证上。",
                "可按需补充路由、状态管理和部署策略，不必一次决定全部框架约束。",
            ],
            cons=[
                "SSR、SEO 和全栈整合需要额外拼装。",
                "随着产品复杂度提升，工程规范需要自己补齐。",
            ],
            best_for="原型验证、强前端团队、对 SEO 暂无硬要求的项目。",
        ),
    ]


def frontend_evidence() -> list[EvidenceItem]:
    return [
        EvidenceItem("heuristic:prototype-speed", "轻量构建链在原型期能更快验证 AI 交互假设。", "Vite + React"),
        EvidenceItem("heuristic:ssr-seo", "当需求包含 SSR 和 SEO 时，内建服务端能力会显著降低整合成本。", "Next.js"),
        EvidenceItem("heuristic:long-term-ops", "长期运营通常更看重统一的路由、数据获取和部署约束。", "Next.js"),
    ]


def sdk_candidates() -> list[CandidateAnalysis]:
    return [
        CandidateAnalysis(
            option="OpenAI SDK",
            pros=[
                "贴近底层 API，能力暴露完整。",
                "对模型参数、响应结构和错误处理的控制粒度更高。",
                "适合需要自行设计抽象层或服务端编排的团队。",
            ],
            cons=[
                "流式 UI、消息状态和多模型适配需要自己补更多胶水代码。",
                "前后端协同时，工程样板和可复用层要自己维护。",
            ],
            best_for="后端主导、想保留底层控制权、接受自己封装抽象的团队。",
        ),
        CandidateAnalysis(
            option="Vercel AI SDK",
            pros=[
                "流式输出、UI 状态和多提供商适配做得更开箱即用。",
                "适合快速把聊天、工具调用和多模型切换接进产品原型。",
                "前端和全栈场景里的开发体验更顺手。",
            ],
            cons=[
                "会引入一层抽象，边缘能力和 provider 特性可能需要绕开 SDK。",
                "后续如果完全脱离其抽象，需要承担迁移成本。",
            ],
            best_for="需要快速交付 AI 应用体验、强调流式交互和多模型切换的团队。",
        ),
    ]


def sdk_evidence() -> list[EvidenceItem]:
    return [
        EvidenceItem("heuristic:streaming-ui", "流式消息和前端状态管理是 AI SDK 的强项。", "Vercel AI SDK"),
        EvidenceItem("heuristic:provider-agnostic", "当系统需要多模型切换时，统一 provider 抽象能降低接线成本。", "Vercel AI SDK"),
        EvidenceItem("heuristic:low-level-control", "直接使用官方 SDK 时，底层能力暴露更完整，但抽象工作转移到业务侧。", "OpenAI SDK"),
    ]
