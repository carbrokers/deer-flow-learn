# DeerFlow 7 天学习与实战计划

## 目标

用 7 天时间，以 DeerFlow 为主线，建立一套完整的 AI Agent 工程认知，并亲手做出一个 CLI 版“技术选型决策助手”。

这份计划的落地物包含两部分：

1. 学习路线：从 DeerFlow 的执行链路、prompt、中间件、skills、sandbox、MCP、memory 一路拆开。
2. 可运行 demo：`backend/tech_decision_copilot/`，用于把这些抽象映射成一个简化但完整的决策型 agent 原型。

## 学习安排

### Day 1：建立全局心智模型

- 阅读：`README.md`、`backend/CLAUDE.md`、`backend/packages/harness/deerflow/agents/lead_agent/agent.py`
- 重点：
  - 请求如何流入 Gateway、Runtime、Model、Tool、Response
  - Standard mode 与 Gateway mode 的差异
  - Agent、Tool、Skill、MCP、Memory、Sandbox 的边界
- 产出：
  - 自己的架构图
  - 核心抽象解释表

### Day 2：Lead Agent 与 Prompt 设计

- 阅读：`backend/packages/harness/deerflow/agents/lead_agent/prompt.py`、`backend/tests/test_lead_agent_prompt.py`
- 重点：
  - Prompt 不是单点设计，而是和 middleware、tool schema 一起构成约束系统
  - 澄清、loop detection、todo、summarization 的作用
- 产出：
  - 一个“通用决策 agent prompt 模板”

### Day 3：Skill、Tool、Sandbox 能力模型

- 阅读：`backend/packages/harness/deerflow/skills/loader.py`、`backend/packages/harness/deerflow/skills/parser.py`、`backend/packages/harness/deerflow/sandbox/tools.py`
- 重点：
  - Tool 是执行接口，Skill 是任务工作方式
  - Sandbox 决定真实行动边界
- 产出：
  - Prompt / Tool / Skill / Sandbox 分层判断表

### Day 4：MCP、Memory 与设计分层

- 阅读：`backend/packages/harness/deerflow/mcp/client.py`、`backend/packages/harness/deerflow/config/extensions_config.py`、`backend/packages/harness/deerflow/agents/memory/`
- 重点：
  - 外部能力为什么不总是直接变成 tool
  - Memory 该存什么，不该存什么
- 产出：
  - demo 的 Prompt / Tool / MCP / Memory 职责图

### Day 5：完成 Demo 核心骨架

Demo 名称：`Tech Decision Copilot`

- 输入：自然语言技术选型问题
- 输出：
  - 问题重述
  - 评估维度
  - 候选方案
  - 证据摘要
  - 推荐结论
  - 风险和下一步

最小模块：

- `workflow.py`：规划 -> 调研 -> 分析 -> 决策
- `knowledge.py`：本地研究卡片，模拟工具层
- `memory.py`：会话级约束缓存
- `reporting.py`：Markdown 报告输出
- `cli.py`：终端入口

### Day 6：增强 demo 的真实价值

- 固定评估维度模板
- 输出来源标记
- 信息不足时主动要求补充条件
- 报告不是总结，而是“建议 + 理由 + 风险 + 下一步”

### Day 7：回到 DeerFlow 做映射复盘

复盘以下问题：

- Agent 为什么需要 middleware
- Skill 与 Tool 的边界
- MCP 什么时候比内建 tool 更合适
- 决策型 agent 如何约束输出质量
- 这个 demo 下一步如何升级为更像 DeerFlow 的系统

## Demo 设计映射

### 与 DeerFlow 对齐的点

- `workflow.py` 对应 DeerFlow 中 Lead Agent 的主任务编排思路
- `knowledge.py` 对应“工具层”，只是这里先用本地知识卡片替代真实 web / MCP
- `memory.py` 只保存会影响后续判断的约束，呼应 DeerFlow memory 的最小化原则
- `reporting.py` 明确输出结构，而不是把结果藏在自由文本里

### 刻意简化的点

- 不接真实模型，不接真实 web 搜索
- 不做多 agent，只保留 planner / researcher / analyzer / decision 的工作流分层
- 不引入 MCP，只在文档中预留升级位

### 下一步演进

如果继续往 DeerFlow 靠拢，建议这样升级：

1. 用真实 tool 替换 `knowledge.py`，接入 web search 或 MCP 搜索源。
2. 把不同问题类型的分析模板抽成 skill。
3. 用会话 memory 存“团队偏好、预算、部署环境、合规要求”等稳定约束。
4. 当研究任务变长时，再拆成 researcher / analyzer 子代理。

## 运行方式

在 `backend/` 目录执行：

```bash
uv run python -m tech_decision_copilot.cli --question "前端 AI 产品原型阶段，使用 Next.js 还是 Vite + React？"
```

## 验证清单

- 能比较两个前端技术栈并输出结构化建议
- 能比较两个模型接入方案并输出理由与风险
- 信息不足时不会强行拍板
- 更换约束条件后，建议会发生合理变化
