# Research Agent Core — 架构文档

## 项目定位

一个模块化的科研 AI 智能体框架。调度器（Orchestrator）按流水线依次执行各研究模块，模块间通过统一的数据格式传递结果。目标是做成长期维护、可分享给其他科研人员使用的生产级工具。

## 架构总览

```
用户（CLI / Web / API）
        │
        ▼
  core/__init__.py          ← 对外的统一入口
        │
        ▼
  core/orchestrator.py      ← 大脑：创建任务、调度模块、汇总结果
        │
        ├─ core/state.py    ← 数据格式：TaskStatus、ModuleResult、TaskState
        ├─ core/registry.py ← 模块电话簿：登记和查找模块
        └─ core/utils.py    ← 工具箱：校验输入、规范化结果、生成 ID
        │
        ▼
  modules/                  ← 5 个可插拔的研究能力模块
    ├─ literature/          → 文献检索
    ├─ theory/              → 理论分析
    ├─ computation/         → 数值计算
    ├─ experiment/          → 实验设计
    └─ report/              → 报告汇总
```

## 数据流

```
用户输入 → TaskState（任务档案）
              │
              ├─→ 模块 1 执行 → 返回 dict 或 ModuleResult
              │                      │
              │                      ├─→ normalize_result() 统一格式
              │                      │
              │                      └─→ 塞进 context["previous_results"]
              │                               │
              ├─→ 模块 2 执行 ←───────────────┘
              ├─→ ...
              ├─→ 模块 5 执行
              │
              └─→ state.finish() → state.to_response() → 输出 JSON
```

## 核心模块详解

### core/state.py — 数据格式

定义了三样东西，全项目共用：

- **TaskStatus**：5 种合法状态枚举（PENDING / RUNNING / SUCCESS / FAILED / PARTIAL）
- **ModuleResult**：每个模块执行完交的"答卷"，9 个字段（status、summary、files、logs、data、error、module、started_at、finished_at）
- **TaskState**：一个任务从生到死的完整档案，里面装多个 ModuleResult

### core/registry.py — 模块注册中心

一个字典，存"模块名 → 执行函数"的映射。调度器按名字查找函数，不直接 import 模块。

好处：加新模块只改 `_BUILTIN_MODULES` 字典，不用改调度器。

### core/orchestrator.py — 调度器

负责：
1. 创建 TaskState 档案
2. 按顺序调用模块（`_run_pipeline`）
3. 每个模块抛异常不崩整个流程（异常隔离）
4. 收 ModuleResult、填档案、结算总状态
5. 输出 `state.to_response()` 给用户

### core/utils.py — 工具箱

- `new_task_id()`：生成 12 位短 ID
- `validate_task()`：检查输入是否合法
- `normalize_result()`：把模块返回的 dict 或 ModuleResult 统一转成 ModuleResult。这是模块和调度器之间的**翻译官**

### core/__init__.py — 对外入口

把内部地址翻译成对外简称。外面写 `from core import run_task` 就够了，不需要知道 `run_task` 在 `orchestrator.py` 里。

## 模块开发规范

参见 `对接文件/MODULE_FORMAT_SPEC_v0.1.md`。

每个模块必须暴露一个 `run(task: str, context: dict) -> dict` 函数。返回值必须是标准字典格式，包含 `status`、`summary`、`data` 等字段。

## 技术决策记录

| 决策 | 原因 |
|---|---|
| 核心只用标准库 | 零依赖，任何 Python 环境都能跑 |
| dataclass 而不是手写类 | 减少样板代码，自动生成 `__init__` |
| 枚举而不是字符串 | 拼写错误当场报错，不埋雷 |
| 注册中心而不是硬编码 import | 模块和调度器解耦，加模块不改核心 |

## 当前技术架构

- **后端**：FastAPI（`web/server.py`）— 接收前端请求，调用 core 运行任务，返回 JSON 结果
- **前端**：原生 HTML/CSS/JS（`web/index.html`）— 现代单页应用，流水线可视化，零前端依赖
- **通信**：HTTP POST `/api/run` → JSON 响应。前端和后端完全分离，后端不关心界面长什么样

## 未来规划

- 数据库持久化：SQLite 保存历史任务
- WebSocket 实时推送：模块完成立刻通知前端
- 对接真实 AI API：替换模块中的 stub 数据为真实 LLM 调用
