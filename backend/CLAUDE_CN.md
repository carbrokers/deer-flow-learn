# CLAUDE.md

本文档用于指导 Claude Code（claude.ai/code）在本仓库中进行后端开发。

## 项目概览

DeerFlow 是一个基于 LangGraph 的全栈 AI super agent 系统。后端提供“超级智能体”能力，包括沙箱执行、持久化 memory、subagent 委托以及可扩展 tool 集成；这些能力都运行在线程级隔离环境中。

**整体架构**：

- **LangGraph Server**（端口 2024）：Agent runtime 和 workflow 执行服务。
- **Gateway API**（端口 8001）：提供模型、MCP、skills、memory、artifacts、uploads、本地 thread 清理等 REST API。
- **Frontend**（端口 3000）：Next.js Web 界面。
- **Nginx**（端口 2026）：统一反向代理入口。
- **Provisioner**（端口 8002，Docker 开发模式下可选）：仅当 sandbox 配置为 provisioner/Kubernetes 模式时启动。

**运行模式**：

- **Standard mode**（`make dev`）：LangGraph Server 作为独立进程负责 agent 执行。总共约 4 个进程。
- **Gateway mode**（`make dev-pro`，实验性）：Agent runtime 通过 `RunManager` + `run_agent()` + `StreamBridge` 嵌入 Gateway（`packages/harness/deerflow/runtime/`）。服务通过 async task 自行管理并发。总共约 3 个进程，不启动 LangGraph Server。

**项目结构**：

```text
deer-flow/
├── Makefile                    # 仓库根目录命令（check、install、dev、stop）
├── config.yaml                 # 主应用配置
├── extensions_config.json      # MCP server 和 skill 配置
├── backend/                    # 后端应用（当前目录）
│   ├── Makefile                # 后端专用命令（dev、gateway、lint）
│   ├── langgraph.json          # LangGraph server 配置
│   ├── packages/
│   │   └── harness/            # deerflow-harness 包（import 前缀：deerflow.*）
│   │       ├── pyproject.toml
│   │       └── deerflow/
│   │           ├── agents/             # LangGraph agent 系统
│   │           │   ├── lead_agent/     # 主 agent（factory + system prompt）
│   │           │   ├── middlewares/    # middleware 组件
│   │           │   ├── memory/         # memory 抽取、队列、prompt
│   │           │   └── thread_state.py # ThreadState schema
│   │           ├── sandbox/            # sandbox 执行系统
│   │           │   ├── local/          # 本地文件系统 provider
│   │           │   ├── sandbox.py      # 抽象 Sandbox 接口
│   │           │   ├── tools.py        # bash、ls、read/write/str_replace
│   │           │   └── middleware.py   # sandbox 生命周期管理
│   │           ├── subagents/          # subagent 委托系统
│   │           │   ├── builtins/       # general-purpose、bash agents
│   │           │   ├── executor.py     # 后台执行引擎
│   │           │   └── registry.py     # agent 注册表
│   │           ├── tools/builtins/     # 内建 tools（present_files、ask_clarification、view_image）
│   │           ├── mcp/                # MCP 集成（tools、cache、client）
│   │           ├── models/             # 模型 factory，支持 thinking/vision
│   │           ├── skills/             # skill 发现、加载、解析
│   │           ├── config/             # 配置系统（app、model、sandbox、tool 等）
│   │           ├── community/          # 社区 tools（tavily、jina_ai、firecrawl、image_search、aio_sandbox）
│   │           ├── reflection/         # 动态模块加载（resolve_variable、resolve_class）
│   │           ├── utils/              # 工具函数（network、readability）
│   │           └── client.py           # 嵌入式 Python client（DeerFlowClient）
│   ├── app/                    # 应用层（import 前缀：app.*）
│   │   ├── gateway/            # FastAPI Gateway API
│   │   │   ├── app.py          # FastAPI 应用
│   │   │   └── routers/        # FastAPI 路由模块（models、mcp、memory、skills、uploads、threads、artifacts、agents、suggestions、channels）
│   │   └── channels/           # IM 平台集成
│   ├── tests/                  # 测试套件
│   └── docs/                   # 文档
├── frontend/                   # Next.js 前端应用
└── skills/                     # Agent skills 目录
    ├── public/                 # 公共 skills（提交到仓库）
    └── custom/                 # 自定义 skills（gitignored）
```

## 重要开发约定

### 文档同步策略

**重要：每次代码变更后都要同步更新 README.md 和 CLAUDE.md。**

修改代码时，必须同步更新相关文档：

- 面向用户的变化（功能、安装、使用方式）更新 `README.md`。
- 面向开发者的变化（架构、命令、workflow、内部系统）更新 `CLAUDE.md`。
- 文档必须与代码保持同步。
- 保证文档内容准确且及时。

## 常用命令

**仓库根目录**（完整应用）：

```bash
make check      # 检查系统要求
make install    # 安装所有依赖（frontend + backend）
make dev        # 启动所有服务（LangGraph + Gateway + Frontend + Nginx），启动前检查 config.yaml
make dev-pro    # Gateway mode（实验性）：跳过 LangGraph，把 agent runtime 嵌入 Gateway
make start-pro  # 生产模式 + Gateway mode（实验性）
make stop       # 停止所有服务
```

**backend 目录**（仅后端开发）：

```bash
make install    # 安装后端依赖
make dev        # 仅运行 LangGraph server（端口 2024）
make gateway    # 仅运行 Gateway API（端口 8001）
make test       # 运行全部后端测试
make lint       # 使用 ruff 做 lint
make format     # 使用 ruff 格式化代码
```

Docker/provisioner 相关回归测试：

- `tests/test_docker_sandbox_mode_detection.py`：验证从 `config.yaml` 识别 sandbox mode。
- `tests/test_provisioner_kubeconfig.py`：验证 kubeconfig 文件/目录处理。

边界检查（harness → app import 防火墙）：

- `tests/test_harness_boundary.py`：确保 `packages/harness/deerflow/` 永远不会 import `app.*`。

CI 会通过 [.github/workflows/backend-unit-tests.yml](../.github/workflows/backend-unit-tests.yml) 在每个 PR 上运行这些回归测试。

## 架构

### Harness / App 分层

后端拆成两层，并且依赖方向是严格单向的：

- **Harness**（`packages/harness/deerflow/`）：可发布的 agent 框架包（`deerflow-harness`）。Import 前缀为 `deerflow.*`。它包含 agent 编排、tools、sandbox、models、MCP、skills、config，也就是构建和运行 agent 所需的核心能力。
- **App**（`app/`）：不单独发布的应用代码。Import 前缀为 `app.*`。它包含 FastAPI Gateway API，以及飞书、Slack、Telegram 等 IM channel 集成。

**依赖规则**：App 可以 import deerflow，但 deerflow 绝不能 import app。这个边界由 CI 中的 `tests/test_harness_boundary.py` 强制检查。

**Import 约定**：

```python
# Harness 内部
from deerflow.agents import make_lead_agent
from deerflow.models import create_chat_model

# App 内部
from app.gateway.app import app
from app.channels.service import start_channel_service

# App → Harness（允许）
from deerflow.config import get_app_config

# Harness → App（禁止，由 test_harness_boundary.py 强制检查）
# from app.gateway.routers.uploads import ...  # ← 会导致 CI 失败
```

### Agent 系统

**Lead Agent**（`packages/harness/deerflow/agents/lead_agent/agent.py`）：

- 入口函数：`make_lead_agent(config: RunnableConfig)`，在 `langgraph.json` 中注册。
- 通过 `create_chat_model()` 动态选择模型，支持 thinking 和 vision。
- 通过 `get_available_tools()` 加载 tools，组合 sandbox、内建 tools、MCP、community tools 和 subagent tools。
- 通过 `apply_prompt_template()` 生成 system prompt，并注入 skills、memory、subagent instructions。

**ThreadState**（`packages/harness/deerflow/agents/thread_state.py`）：

- 在 `AgentState` 基础上扩展：`sandbox`、`thread_data`、`title`、`artifacts`、`todos`、`uploaded_files`、`viewed_images`。
- 使用自定义 reducer：`merge_artifacts`（去重）和 `merge_viewed_images`（合并/清空）。

**运行时配置**（通过 `config.configurable` 传入）：

- `thinking_enabled`：启用模型的 extended thinking。
- `model_name`：选择指定 LLM 模型。
- `is_plan_mode`：启用 TodoList middleware。
- `subagent_enabled`：启用任务委托工具。

### Middleware 链

Lead agent 的 middleware 会按照严格的 append 顺序组装，涉及 `packages/harness/deerflow/agents/middlewares/tool_error_handling_middleware.py` 中的 `build_lead_runtime_middlewares`，以及 `packages/harness/deerflow/agents/lead_agent/agent.py` 中的 `_build_middlewares`：

1. **ThreadDataMiddleware**：创建每个 thread 对应的目录（`backend/.deer-flow/threads/{thread_id}/user-data/{workspace,uploads,outputs}`）。Web UI 删除 thread 时，先删除 LangGraph thread，再由 Gateway 清理本地 `.deer-flow/threads/{thread_id}` 目录。
2. **UploadsMiddleware**：跟踪新上传文件，并将上传文件信息注入对话。
3. **SandboxMiddleware**：获取 sandbox，并将 `sandbox_id` 写入 state。
4. **DanglingToolCallMiddleware**：为缺少响应的 `AIMessage.tool_calls` 注入占位 `ToolMessage`，例如用户中断导致 tool response 缺失时。原始 provider tool-call payload 只保留在 `additional_kwargs["tool_calls"]` 中。
5. **LLMErrorHandlingMiddleware**：在后续 middleware/tool 阶段运行前，将 provider/model 调用错误规范化为 assistant 可恢复处理的错误。
6. **GuardrailMiddleware**：tool 调用前授权检查。通过可插拔的 `GuardrailProvider` 协议实现；当 `config` 中 `guardrails.enabled` 启用时生效。它会评估每个 tool call，拒绝时返回错误 `ToolMessage`。Provider 有三类：内建 `AllowlistProvider`（零依赖）、OAP policy provider（如 `aport-agent-guardrails`）、自定义 provider。配置和实现方式见 [docs/GUARDRAILS.md](docs/GUARDRAILS.md)。
7. **SandboxAuditMiddleware**：在 tool 执行前审计 sandbox 中的 shell/file 操作，用于安全日志。
8. **ToolErrorHandlingMiddleware**：将 tool 异常转换为错误 `ToolMessage`，让当前 run 可以继续，而不是直接中止。
9. **SummarizationMiddleware**：接近 token 上限时压缩上下文；可选，启用后生效。
10. **TodoListMiddleware**：通过 `write_todos` tool 跟踪任务；可选，在 plan mode 下生效。
11. **TokenUsageMiddleware**：启用 token tracking 时记录 token 使用指标；可选。
12. **TitleMiddleware**：首轮完整交互后自动生成 thread title，并在调用 title model 前规范化结构化消息内容。
13. **MemoryMiddleware**：将对话加入异步 memory 更新队列，只保留用户消息和最终 AI 响应。
14. **ViewImageMiddleware**：在 LLM 调用前注入 base64 图片数据；仅当模型支持 vision 时启用。
15. **DeferredToolFilterMiddleware**：在 tool search 启用前，从绑定到模型的 tool schema 中隐藏 deferred tools；可选。
16. **SubagentLimitMiddleware**：当 `subagent_enabled` 启用时，截断模型响应中过多的 `task` tool calls，以满足 `MAX_CONCURRENT_SUBAGENTS` 并发限制。
17. **LoopDetectionMiddleware**：检测重复 tool-call loop。触发 hard stop 时，会清空结构化 `tool_calls` 和原始 provider tool-call metadata，强制生成最终文本回答。
18. **ClarificationMiddleware**：拦截 `ask_clarification` tool call，并通过 `Command(goto=END)` 中断当前执行；必须位于最后。

### 配置系统

**主配置**（`config.yaml`）：

初始化方式：将 `config.example.yaml` 复制为项目根目录下的 `config.yaml`。

**配置版本管理**：`config.example.yaml` 包含 `config_version` 字段。启动时，`AppConfig.from_file()` 会比较用户配置版本和 example 版本，若用户配置过旧则发出 warning。缺失 `config_version` 会被视为版本 0。运行 `make config-upgrade` 可自动合并缺失字段。变更配置 schema 时，需要同步提升 `config.example.yaml` 中的 `config_version`。

**配置缓存**：`get_app_config()` 会缓存解析后的配置，但当配置路径变化或文件 mtime 更新时会自动重载。这保证 Gateway 和 LangGraph 对 `config.yaml` 的读取保持一致，无需手动重启进程。

配置优先级：

1. 显式传入的 `config_path` 参数。
2. `DEER_FLOW_CONFIG_PATH` 环境变量。
3. 当前目录（backend/）下的 `config.yaml`。
4. 父目录（项目根目录）下的 `config.yaml`，这是推荐位置。

以 `$` 开头的配置值会解析为环境变量，例如 `$OPENAI_API_KEY`。
`ModelConfig` 还声明了 `use_responses_api` 和 `output_version`，因此可以显式启用 OpenAI `/v1/responses`，同时继续使用 `langchain_openai:ChatOpenAI`。

**扩展配置**（`extensions_config.json`）：

MCP servers 和 skills 在项目根目录的 `extensions_config.json` 中统一配置。

配置优先级：

1. 显式传入的 `config_path` 参数。
2. `DEER_FLOW_EXTENSIONS_CONFIG_PATH` 环境变量。
3. 当前目录（backend/）下的 `extensions_config.json`。
4. 父目录（项目根目录）下的 `extensions_config.json`，这是推荐位置。

### Gateway API（`app/gateway/`）

FastAPI 应用运行在端口 8001，健康检查路径为 `GET /health`。

**Routers**：

| Router | Endpoints |
|--------|-----------|
| **Models**（`/api/models`） | `GET /`：列出模型；`GET /{name}`：获取模型详情 |
| **MCP**（`/api/mcp`） | `GET /config`：读取配置；`PUT /config`：更新配置（写入 extensions_config.json） |
| **Skills**（`/api/skills`） | `GET /`：列出 skills；`GET /{name}`：获取详情；`PUT /{name}`：更新 enabled 状态；`POST /install`：从 .skill archive 安装（支持标准可选 frontmatter，如 `version`、`author`、`compatibility`） |
| **Memory**（`/api/memory`） | `GET /`：读取 memory 数据；`POST /reload`：强制重载；`GET /config`：读取配置；`GET /status`：读取配置和数据状态 |
| **Uploads**（`/api/threads/{id}/uploads`） | `POST /`：上传文件（自动转换 PDF/PPT/Excel/Word）；`GET /list`：列出文件；`DELETE /{filename}`：删除文件 |
| **Threads**（`/api/threads/{id}`） | `DELETE /`：在 LangGraph thread 删除后，移除 DeerFlow 管理的本地 thread 数据；非预期失败会在服务端记录日志，并向客户端返回通用 500 detail |
| **Artifacts**（`/api/threads/{id}/artifacts`） | `GET /{path}`：提供 artifact 文件；对 active content types（`text/html`、`application/xhtml+xml`、`image/svg+xml`）始终强制作为附件下载，以降低 XSS 风险；其他文件类型仍可通过 `?download=true` 强制下载 |
| **Suggestions**（`/api/threads/{id}/suggestions`） | `POST /`：生成后续问题；在 JSON 解析前规范化 rich list/block 模型内容 |

Nginx 代理规则：`/api/langgraph/*` → LangGraph，其他 `/api/*` → Gateway。

### Sandbox 系统（`packages/harness/deerflow/sandbox/`）

**接口**：抽象 `Sandbox`，提供 `execute_command`、`read_file`、`write_file`、`list_dir`。

**Provider 模式**：`SandboxProvider` 负责 `acquire`、`get`、`release` 生命周期。

**实现**：

- `LocalSandboxProvider`：单例本地文件系统执行，带路径映射。
- `AioSandboxProvider`（`packages/harness/deerflow/community/`）：基于 Docker 的隔离执行。

**虚拟路径系统**：

- Agent 看到的路径：`/mnt/user-data/{workspace,uploads,outputs}`、`/mnt/skills`。
- 物理路径：`backend/.deer-flow/threads/{thread_id}/user-data/...`、`deer-flow/skills/`。
- 路径转换：`replace_virtual_path()` / `replace_virtual_paths_in_command()`。
- 本地 sandbox 判断：`is_local_sandbox()` 检查 `sandbox_id == "local"`。

**Sandbox Tools**（位于 `packages/harness/deerflow/sandbox/tools.py`）：

- `bash`：执行命令，包含路径转换和错误处理。
- `ls`：列目录，tree 格式，最多 2 层。
- `read_file`：读取文件内容，支持可选行范围。
- `write_file`：写入/追加文件，必要时创建目录。
- `str_replace`：字符串替换，支持单次或全部替换；同路径串行化粒度为 `(sandbox.id, path)`，因此不同隔离 sandbox 中相同虚拟路径不会在同一进程内互相阻塞。

### Subagent 系统（`packages/harness/deerflow/subagents/`）

**内建 Agents**：`general-purpose`（除 `task` 外的所有 tools）和 `bash`（命令执行专家）。

**执行模型**：双线程池：`_scheduler_pool`（3 workers）+ `_execution_pool`（3 workers）。

**并发限制**：`MAX_CONCURRENT_SUBAGENTS = 3`，由 `SubagentLimitMiddleware` 强制执行。它会在 `after_model` 阶段截断多余 tool calls。单个任务超时时间为 15 分钟。

**流程**：`task()` tool → `SubagentExecutor` → 后台线程 → 每 5 秒轮询 → SSE events → result。

**事件**：`task_started`、`task_running`、`task_completed` / `task_failed` / `task_timed_out`。

### Tool 系统（`packages/harness/deerflow/tools/`）

`get_available_tools(groups, include_mcp, model_name, subagent_enabled)` 会组装：

1. **配置定义的 tools**：通过 `resolve_variable()` 从 `config.yaml` 解析。
2. **MCP tools**：来自启用的 MCP servers，按需懒加载，并通过 mtime 失效缓存。
3. **内建 tools**：
   - `present_files`：将输出文件展示给用户，仅允许 `/mnt/user-data/outputs`。
   - `ask_clarification`：请求用户澄清，由 ClarificationMiddleware 拦截并中断。
   - `view_image`：以 base64 读取图片，仅当模型支持 vision 时加入。
4. **Subagent tool**（启用时）：
   - `task`：委托给 subagent，参数包括 description、prompt、subagent_type、max_turns。

**Community tools**（`packages/harness/deerflow/community/`）：

- `tavily/`：Web search（默认 5 条结果）和 web fetch（4KB 限制）。
- `jina_ai/`：通过 Jina reader API 获取网页，并做 readability 提取。
- `firecrawl/`：通过 Firecrawl API 做网页抓取。

**ACP agent tools**：

- `invoke_acp_agent`：调用 `config.yaml` 中配置的外部 ACP-compatible agents。
- ACP launcher 必须是真正的 ACP adapter。标准 `codex` CLI 本身不是 ACP-compatible；请配置类似 `npx -y @zed-industries/codex-acp` 的 wrapper，或已安装的 `codex-acp` 二进制文件。
- ACP 可执行文件缺失时会返回可操作的错误信息，而不是原始 `[Errno 2]`。
- 每个 ACP agent 使用 thread 级 workspace：`{base_dir}/threads/{thread_id}/acp-workspace/`。Lead agent 可通过虚拟路径 `/mnt/acp-workspace/` 只读访问该 workspace。在 docker sandbox mode 下，该目录会以只读 volume 挂载到容器的 `/mnt/acp-workspace`；在 local sandbox mode 下，由 `tools.py` 负责路径转换。
- `image_search/`：通过 DuckDuckGo 做图片搜索。

### MCP 系统（`packages/harness/deerflow/mcp/`）

- 使用 `langchain-mcp-adapters` 的 `MultiServerMCPClient` 管理多个 MCP server。
- **懒初始化**：通过 `get_cached_mcp_tools()` 在首次使用时加载 tools。
- **缓存失效**：通过比较配置文件 mtime 检测变更。
- **Transports**：支持 stdio（基于命令）、SSE、HTTP。
- **OAuth（HTTP/SSE）**：支持 token endpoint flows（`client_credentials`、`refresh_token`），自动刷新 token 并注入 Authorization header。
- **运行时更新**：Gateway API 会保存到 extensions_config.json；LangGraph 通过 mtime 检测更新。

### Skills 系统（`packages/harness/deerflow/skills/`）

- **位置**：`deer-flow/skills/{public,custom}/`。
- **格式**：包含 `SKILL.md` 的目录；`SKILL.md` 使用 YAML frontmatter（`name`、`description`、`license`、`allowed-tools`）。
- **加载**：`load_skills()` 递归扫描 `skills/{public,custom}` 中的 `SKILL.md`，解析 metadata，并从 extensions_config.json 读取 enabled 状态。
- **注入**：启用的 skills 会以 container path 的形式列入 agent system prompt。
- **安装**：`POST /api/skills/install` 会将 .skill ZIP archive 解压到 custom/ 目录。

### Model Factory（`packages/harness/deerflow/models/factory.py`）

- `create_chat_model(name, thinking_enabled)` 根据配置通过 reflection 实例化 LLM。
- 支持 `thinking_enabled` 标志，并可通过每个模型的 `when_thinking_enabled` 覆盖配置。
- 支持 vLLM 风格的 thinking 开关：为 Qwen reasoning models 使用 `when_thinking_enabled.extra_body.chat_template_kwargs.enable_thinking`，同时兼容旧版 `thinking` 配置。
- 支持 `supports_vision` 标志，用于图片理解模型。
- 以 `$` 开头的配置值会解析为环境变量。
- Provider 模块缺失时，reflection resolver 会给出可执行的安装提示，例如 `uv add langchain-google-genai`。

### vLLM Provider（`packages/harness/deerflow/models/vllm_provider.py`）

- `VllmChatModel` 继承自 `langchain_openai:ChatOpenAI`，用于 vLLM 0.19.0 的 OpenAI-compatible endpoint。
- 保留 vLLM 非标准 assistant `reasoning` 字段，覆盖完整响应、streaming deltas 和后续 tool-call turns。
- 面向 vLLM 0.19.0 Qwen reasoning models 的配置设计，通过 `extra_body.chat_template_kwargs.enable_thinking` 启用 thinking，同时接受旧版 `thinking` alias。

### IM Channels 系统（`app/channels/`）

将外部消息平台（飞书、Slack、Telegram）桥接到 DeerFlow agent，并通过 LangGraph Server 执行。

**架构**：Channels 使用 `langgraph-sdk` HTTP client 和 LangGraph Server 通信，方式与前端一致，从而保证 thread 在服务端创建和管理。

**组件**：

- `message_bus.py`：异步 pub/sub hub（`InboundMessage` → queue → dispatcher；`OutboundMessage` → callbacks → channels）。
- `store.py`：基于 JSON 文件的持久化映射，`channel_name:chat_id[:topic_id]` → `thread_id`。根会话 key 为 `channel:chat`，threaded conversation key 为 `channel:chat:topic`。
- `manager.py`：核心 dispatcher。通过 `client.threads.create()` 创建 thread，路由命令；Slack/Telegram 使用 `client.runs.wait()`；飞书使用 `client.runs.stream(["messages-tuple", "values"])` 做增量出站更新。
- `base.py`：抽象 `Channel` 基类（start/stop/send 生命周期）。
- `service.py`：根据 `config.yaml` 管理所有已配置 channels 的生命周期。
- `slack.py` / `feishu.py` / `telegram.py`：平台特定实现。`feishu.py` 在内存中跟踪运行中的 card `message_id`，并原地 patch 同一张 card。

**消息流程**：

1. 外部平台 → Channel 实现 → `MessageBus.publish_inbound()`。
2. `ChannelManager._dispatch_loop()` 从 queue 消费消息。
3. 对 chat 消息：查找或在 LangGraph Server 上创建 thread。
4. 飞书 chat：`runs.stream()` → 累积 AI 文本 → 发布多次 outbound update（`is_final=False`）→ 发布最终 outbound（`is_final=True`）。
5. Slack/Telegram chat：`runs.wait()` → 提取最终响应 → 发布 outbound。
6. 飞书 channel 会先发送一张 running reply card，然后对每次 outbound update patch 同一张 card。Card JSON 设置 `config.update_multi=true`，满足飞书 patch API 要求。
7. 对命令（`/new`、`/status`、`/models`、`/memory`、`/help`）：本地处理或查询 Gateway API。
8. Outbound → channel callbacks → 平台回复。

**配置**（`config.yaml` → `channels`）：

- `langgraph_url`：LangGraph Server URL，默认 `http://localhost:2024`。
- `gateway_url`：Gateway API URL，用于辅助命令，默认 `http://localhost:8001`。
- 在 Docker Compose 中，IM channels 运行在 `gateway` 容器内，因此 `localhost` 指向该容器自身。应使用 `http://langgraph:2024` / `http://gateway:8001`，或设置 `DEER_FLOW_CHANNELS_LANGGRAPH_URL` / `DEER_FLOW_CHANNELS_GATEWAY_URL`。
- 每个 channel 的配置：`feishu`（app_id、app_secret）、`slack`（bot_token、app_token）、`telegram`（bot_token）。

### Memory 系统（`packages/harness/deerflow/agents/memory/`）

**组件**：

- `updater.py`：基于 LLM 更新 memory，包含 fact 抽取、空白归一化后的 fact 去重（比较前会 trim 首尾空白）和原子文件 I/O。
- `queue.py`：debounced update queue（按 thread 去重，可配置等待时间）。
- `prompt.py`：memory update prompt templates。

**数据结构**（存储在 `backend/.deer-flow/memory.json`）：

- **User Context**：`workContext`、`personalContext`、`topOfMind`，均为 1-3 句摘要。
- **History**：`recentMonths`、`earlierContext`、`longTermBackground`。
- **Facts**：离散事实，字段包括 `id`、`content`、`category`（preference/knowledge/context/behavior/goal）、`confidence`（0-1）、`createdAt`、`source`。

**工作流**：

1. `MemoryMiddleware` 过滤消息，只保留用户输入和最终 AI 响应，并将 conversation 加入队列。
2. Queue 做 debounce（默认 30 秒）、批处理更新、按 thread 去重。
3. 后台线程调用 LLM 抽取 context updates 和 facts。
4. 使用临时文件 + rename 原子化写入更新，并做 cache invalidation；append 前跳过重复 fact content。
5. 下一轮交互将 top 15 facts + context 注入 system prompt 的 `<memory>` tags。

针对 updater 的重点回归测试位于 `backend/tests/test_memory_updater.py`。

**配置**（`config.yaml` → `memory`）：

- `enabled` / `injection_enabled`：总开关。
- `storage_path`：memory.json 路径。
- `debounce_seconds`：处理前等待时间，默认 30 秒。
- `model_name`：用于更新 memory 的 LLM，null 表示使用默认模型。
- `max_facts` / `fact_confidence_threshold`：fact 存储限制，默认 100 / 0.7。
- `max_injection_tokens`：prompt 注入 token 限制，默认 2000。

### Reflection 系统（`packages/harness/deerflow/reflection/`）

- `resolve_variable(path)`：import 模块并返回变量，例如 `module.path:variable_name`。
- `resolve_class(path, base_class)`：import 并校验 class 是否符合指定 base class。

### 配置 Schema

**`config.yaml`** 主要部分：

- `models[]`：LLM 配置，包括 `use` class path、`supports_thinking`、`supports_vision` 和 provider-specific fields。
- vLLM reasoning models 应使用 `deerflow.models.vllm_provider:VllmChatModel`；Qwen 风格 parser 优先使用 `when_thinking_enabled.extra_body.chat_template_kwargs.enable_thinking`，DeerFlow 也会兼容旧版 `thinking` alias。
- `tools[]`：tool 配置，包括 `use` variable path 和 `group`。
- `tool_groups[]`：tools 的逻辑分组。
- `sandbox.use`：Sandbox provider class path。
- `skills.path` / `skills.container_path`：skills 目录的 host path 和 container path。
- `title`：自动标题生成（enabled、max_words、max_chars、prompt_template）。
- `summarization`：上下文摘要（enabled、触发条件、保留策略）。
- `subagents.enabled`：subagent 委托总开关。
- `memory`：memory 系统（enabled、storage_path、debounce_seconds、model_name、max_facts、fact_confidence_threshold、injection_enabled、max_injection_tokens）。

**`extensions_config.json`**：

- `mcpServers`：server name → config 的映射（enabled、type、command、args、env、url、headers、oauth、description）。
- `skills`：skill name → state 的映射（enabled）。

两者都可以在运行时通过 Gateway API endpoints 或 `DeerFlowClient` 方法修改。

### Embedded Client（`packages/harness/deerflow/client.py`）

`DeerFlowClient` 提供不经过 HTTP 服务、直接在进程内访问所有 DeerFlow 能力的方式。所有返回类型都与 Gateway API response schemas 对齐，因此消费方代码在 HTTP mode 和 embedded mode 下可以保持一致。

**架构**：它 import 的是 LangGraph Server 和 Gateway API 同样使用的 `deerflow` 模块。共享同一套配置文件和数据目录，不依赖 FastAPI。

**Agent Conversation**（替代 LangGraph Server）：

- `chat(message, thread_id)`：同步接口，按 message-id 累积 streaming deltas，并返回最终 AI 文本。
- `stream(message, thread_id)`：订阅 LangGraph `stream_mode=["values", "messages", "custom"]`，并 yield `StreamEvent`：
  - `"values"`：完整 state 快照（title、messages、artifacts）。通过 `messages` mode 已经投递过的 AI 文本不会在这里重复合成，以避免重复投递。
  - `"messages-tuple"`：按 chunk 更新。对 AI 文本而言这是 **delta**，需要按 `id` 拼接还原完整消息；tool calls 和 tool results 各自只发一次。
  - `"custom"`：从 `StreamWriter` 转发。
  - `"end"`：stream 结束，携带累计 `usage`，每个 message id 只统计一次。
- Agent 通过 `create_agent()` + `_build_middlewares()` 懒创建，与 `make_lead_agent` 保持一致。
- 支持通过 `checkpointer` 参数跨轮持久化 state。
- `reset_agent()` 可强制重建 agent，例如 memory 或 skill 发生变化后。
- 完整设计见 [docs/STREAMING.md](docs/STREAMING.md)：说明 Gateway 和 DeerFlowClient 为什么是并行路径、LangGraph `stream_mode` 语义、按 id 去重的不变量，以及回归测试策略。

**Gateway 等价方法**（替代 Gateway API）：

| Category | Methods | Return format |
|----------|---------|---------------|
| Models | `list_models()`、`get_model(name)` | `{"models": [...]}`、`{name, display_name, ...}` |
| MCP | `get_mcp_config()`、`update_mcp_config(servers)` | `{"mcp_servers": {...}}` |
| Skills | `list_skills()`、`get_skill(name)`、`update_skill(name, enabled)`、`install_skill(path)` | `{"skills": [...]}` |
| Memory | `get_memory()`、`reload_memory()`、`get_memory_config()`、`get_memory_status()` | dict |
| Uploads | `upload_files(thread_id, files)`、`list_uploads(thread_id)`、`delete_upload(thread_id, filename)` | `{"success": true, "files": [...]}`、`{"files": [...], "count": N}` |
| Artifacts | `get_artifact(thread_id, path)` → `(bytes, mime_type)` | tuple |

**与 Gateway 的关键差异**：Upload 接收本地 `Path` 对象，而不是 HTTP `UploadFile`；复制前会拒绝目录路径；当文档转换必须在已有 event loop 内运行时复用单个 worker。Artifact 返回 `(bytes, mime_type)`，而不是 HTTP Response。新的 Gateway-only thread cleanup route 会在 LangGraph thread 删除后清理 `.deer-flow/threads/{thread_id}`；目前还没有对应的 `DeerFlowClient` 方法。`update_mcp_config()` 和 `update_skill()` 会自动使缓存的 agent 失效。

**测试**：`tests/test_client.py`（77 个单元测试，包括 `TestGatewayConformance`）、`tests/test_client_live.py`（live integration tests，需要 config.yaml）。

**Gateway Conformance Tests**（`TestGatewayConformance`）：验证每个返回 dict 的 client method 都符合对应的 Gateway Pydantic response model。每个测试都会用 Gateway model 解析 client output；如果 Gateway 新增了 required field 而 client 没有提供，Pydantic 会抛出 `ValidationError`，CI 会捕获这种 drift。覆盖：`ModelsListResponse`、`ModelResponse`、`SkillsListResponse`、`SkillResponse`、`SkillInstallResponse`、`McpConfigResponse`、`UploadResponse`、`MemoryConfigResponse`、`MemoryStatusResponse`。

## 开发流程

### 测试驱动开发（TDD）——强制要求

**每个新功能或 bug fix 都必须配套单元测试，没有例外。**

- 测试放在 `backend/tests/`，按现有命名约定使用 `test_<feature>.py`。
- 修改前后都运行完整测试：`make test`。
- 测试通过后，功能才算完成。
- 对轻量 config/utility 模块，优先写无外部依赖的纯单元测试。
- 如果某个模块在测试中引发循环 import，可以在 `tests/conftest.py` 中添加 `sys.modules` mock；参考已有的 `deerflow.subagents.executor` 示例。

```bash
# 运行全部测试
make test

# 运行指定测试文件
PYTHONPATH=. uv run pytest tests/test_<feature>.py -v
```

### 运行完整应用

从**项目根目录**执行：

```bash
make dev
```

这会启动所有服务，并通过 `http://localhost:2026` 提供应用访问。

**所有启动模式**：

| | **Local Foreground** | **Local Daemon** | **Docker Dev** | **Docker Prod** |
|---|---|---|---|---|
| **Dev** | `./scripts/serve.sh --dev`<br/>`make dev` | `./scripts/serve.sh --dev --daemon`<br/>`make dev-daemon` | `./scripts/docker.sh start`<br/>`make docker-start` | — |
| **Dev + Gateway** | `./scripts/serve.sh --dev --gateway`<br/>`make dev-pro` | `./scripts/serve.sh --dev --gateway --daemon`<br/>`make dev-daemon-pro` | `./scripts/docker.sh start --gateway`<br/>`make docker-start-pro` | — |
| **Prod** | `./scripts/serve.sh --prod`<br/>`make start` | `./scripts/serve.sh --prod --daemon`<br/>`make start-daemon` | — | `./scripts/deploy.sh`<br/>`make up` |
| **Prod + Gateway** | `./scripts/serve.sh --prod --gateway`<br/>`make start-pro` | `./scripts/serve.sh --prod --gateway --daemon`<br/>`make start-daemon-pro` | — | `./scripts/deploy.sh --gateway`<br/>`make up-pro` |

| Action | Local | Docker Dev | Docker Prod |
|---|---|---|---|
| **Stop** | `./scripts/serve.sh --stop`<br/>`make stop` | `./scripts/docker.sh stop`<br/>`make docker-stop` | `./scripts/deploy.sh down`<br/>`make down` |
| **Restart** | `./scripts/serve.sh --restart [flags]` | `./scripts/docker.sh restart` | — |

Gateway mode 会把 agent runtime 嵌入 Gateway，不启动 LangGraph server。

**Nginx 路由**：

- Standard mode：`/api/langgraph/*` → LangGraph Server（2024）。
- Gateway mode：`/api/langgraph/*` → Gateway embedded runtime（8001，通过 envsubst 配置）。
- `/api/*`（其他 API）→ Gateway API（8001）。
- `/`（非 API）→ Frontend（3000）。

### 分别运行后端服务

从 **backend** 目录运行：

```bash
# Terminal 1: LangGraph server
make dev

# Terminal 2: Gateway API
make gateway
```

不经过 nginx 时的直接访问地址：

- LangGraph：`http://localhost:2024`
- Gateway：`http://localhost:8001`

### 前端配置

前端通过环境变量连接后端服务：

- `NEXT_PUBLIC_LANGGRAPH_BASE_URL`：默认 `/api/langgraph`，通过 nginx 访问。
- `NEXT_PUBLIC_BACKEND_BASE_URL`：默认空字符串，通过 nginx 访问。

从根目录运行 `make dev` 时，前端会自动通过 nginx 连接后端。

## 关键功能

### 文件上传

支持多文件上传和自动文档转换：

- Endpoint：`POST /api/threads/{thread_id}/uploads`
- 支持：PDF、PPT、Excel、Word 文档，通过 `markitdown` 转换。
- 复制前拒绝目录输入，保证上传要么全部成功，要么全部失败。
- 当从已有 event loop 调用时，每个请求复用一个 conversion worker。
- 文件存储在线程隔离目录中。
- Agent 通过 `UploadsMiddleware` 接收上传文件列表。

详情见 [docs/FILE_UPLOAD.md](docs/FILE_UPLOAD.md)。

### Plan Mode

TodoList middleware 用于复杂多步骤任务：

- 通过运行时配置控制：`config.configurable.is_plan_mode = True`。
- 提供 `write_todos` tool 跟踪任务。
- 同一时间保持一个 `in_progress` 任务，并实时更新。

详情见 [docs/plan_mode_usage.md](docs/plan_mode_usage.md)。

### Context Summarization

当上下文接近 token 上限时自动做摘要：

- 在 `config.yaml` 的 `summarization` key 下配置。
- 触发类型：tokens、messages，或 max input 的比例。
- 摘要旧消息，同时保留最近消息。

详情见 [docs/summarization.md](docs/summarization.md)。

### Vision Support

对 `supports_vision: true` 的模型：

- `ViewImageMiddleware` 处理对话中的图片。
- `view_image_tool` 会加入 agent toolset。
- 图片会自动转为 base64 并注入 state。

## 代码风格

- 使用 `ruff` 进行 lint 和格式化。
- 行宽：240 字符。
- Python 3.12+，使用类型标注。
- 使用双引号和空格缩进。

## 文档

详细文档见 `docs/` 目录：

- [CONFIGURATION.md](docs/CONFIGURATION.md)：配置选项。
- [ARCHITECTURE.md](docs/ARCHITECTURE.md)：架构细节。
- [API.md](docs/API.md)：API 参考。
- [SETUP.md](docs/SETUP.md)：安装配置指南。
- [FILE_UPLOAD.md](docs/FILE_UPLOAD.md)：文件上传功能。
- [PATH_EXAMPLES.md](docs/PATH_EXAMPLES.md)：路径类型与用法。
- [summarization.md](docs/summarization.md)：上下文摘要。
- [plan_mode_usage.md](docs/plan_mode_usage.md)：使用 TodoList 的 plan mode。

## Learning Demo

一个小型 CLI 学习 demo 位于 `backend/tech_decision_copilot/`。它有意与生产级 DeerFlow runtime 分离，用来把 DeerFlow 的核心概念映射成一个最小 workflow：

- `workflow.py` 表示 planner → researcher → analyzer → decision 的编排。
- `knowledge.py` 作为本地知识源，模拟 tool-backed research。
- `memory.py` 只保存和技术决策相关的会话约束。
- `reporting.py` 渲染结构化 Markdown 报告。
- `cli.py` 通过 `uv run python -m tech_decision_copilot.cli --question "..."` 暴露 demo。

对应学习计划见 `../docs/plans/2026-04-28-deerflow-learning-and-tech-decision-copilot.md`。
