# DeerFlow Learning Progress

## Goal

- 主目标：系统学习 DeerFlow 的 Agent 工程设计
- 实战目标：完成并持续迭代 `Tech Decision Copilot` CLI demo

## Navigation

- 学习计划：[2026-04-28-deerflow-learning-and-tech-decision-copilot.md](./2026-04-28-deerflow-learning-and-tech-decision-copilot.md)
- Demo 代码：[`backend/tech_decision_copilot/`](/Users/bytedance/workspace/ai/deer-flow/backend/tech_decision_copilot)
- Demo 测试：[`backend/tests/test_tech_decision_copilot.py`](/Users/bytedance/workspace/ai/deer-flow/backend/tests/test_tech_decision_copilot.py)

## Current Status

- 当前阶段：Day 1，建立全局心智模型
- 已完成：
  - 创建 7 天学习与实战计划文档
  - 实现 `Tech Decision Copilot` CLI demo
  - 为 demo 添加基础测试并验证通过
- 当前建议阅读：
  - [`README.md`](/Users/bytedance/workspace/ai/deer-flow/README.md)
  - [`backend/CLAUDE.md`](/Users/bytedance/workspace/ai/deer-flow/backend/CLAUDE.md)
  - [`backend/packages/harness/deerflow/agents/lead_agent/agent.py`](/Users/bytedance/workspace/ai/deer-flow/backend/packages/harness/deerflow/agents/lead_agent/agent.py)
- 下一步：
  - 用自己的话总结 DeerFlow 主执行链路
  - 画出 Gateway / Runtime / Agent / Tool / Memory / Sandbox 的关系图

## Today Notes

- 当前先不追求把所有代码细节读完，重点是建立主链路认知。
- 学习顺序采用“先全局，后局部，再回到 demo 映射”的方式。

## Open Questions

- 为什么 DeerFlow 要把很多约束放进 middleware，而不是只靠 prompt？
- skill 和 tool 的边界在实际工程里如何判断？
- memory 在什么情况下值得引入，什么情况下只是额外复杂度？

## Validation

- Demo 测试：`cd backend && uv run pytest tests/test_tech_decision_copilot.py -v`
- Demo 运行：`cd backend && uv run python -m tech_decision_copilot.cli --question "前端 AI 产品原型阶段，使用 Next.js 还是 Vite + React？"`

## Update Template

每次学习结束后，追加或修改以下内容：

### Date

- 学到了什么：
- 还没搞懂什么：
- 今天看了哪些文件：
- 做了什么实验：
- 下一步准备看什么：

## Resume Prompt

新开一个 Codex 窗口时，可以直接使用这段话：

```text
请先阅读 docs/plans/2026-04-28-learning-progress.md 和 docs/plans/2026-04-28-deerflow-learning-and-tech-decision-copilot.md，再结合 backend/tech_decision_copilot 和 backend/tests/test_tech_decision_copilot.py，继续协助我学习 DeerFlow。
```
