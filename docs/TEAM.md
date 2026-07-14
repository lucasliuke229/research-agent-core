# 团队成员协作指南

## 加入项目后第一件事

```bash
# 1. 克隆项目
git clone <仓库地址>
cd research_agent_core_demo

# 2. 配置环境（详细步骤见 docs/SETUP.md）
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 配置 LLM（复制模板，填入自己的 API Key）
cp .env.example .env
nano .env    # 把 sk-your-api-key-here 换成你的真实密钥

# 4. 跑一下确认环境正确
python demo.py

# 5. 启动 Web 工作台
python web/server.py
# 浏览器打开 http://localhost:8000
```

## 定制你的 AI 助手

项目根目录的 `CLAUDE.md` 是所有 AI 助手的行为指南。**clone 后第一件事：打开 CLAUDE.md，把"用户信息"部分改成你自己的情况。** 这样你的 AI 才能按你的风格配合你。

至少改这几行：
- 你的背景（物理 / CS / 数学？什么水平？）
- 你的目标（想学什么？想要什么输出风格？）
- 你的工作偏好（需要详细注释还是简洁代码？）

## 项目架构（5 分钟看懂）

```
core/         ← 队长维护的核心框架（不要随便动）
modules/      ← 你负责开发的模块（每个人分一个）
web/          ← Web 前端和后端
对接文件/      ← 模块开发规范（必读！！）
docs/         ← 项目文档
```

核心流程：用户输入科研问题 → 调度器依次调 5 个模块 → 返回结构化结果。

**你只需要关心你负责的那个模块** —— 在 `modules/<模块名>/main.py` 里写一个 `run(task, context) -> dict` 函数。

## 你的任务：开发一个模块

当前项目状态：
- ✅ **文献调研** — 已接入 LLM，真正在做文献检索分析
- ❌ **理论分析** — 还是假数据，需要开发
- ❌ **数值计算** — 还是假数据，需要开发
- ❌ **实验设计** — 还是假数据，需要开发
- ❌ **报告汇总** — 还是假数据，需要开发

### 模块开发流程

1. **读规范** — `对接文件/MODULE_FORMAT_SPEC_v0.1.md`（必须读！15 节，20 条检查清单）
2. **看示例** — `modules/literature/main.py` 是参考实现（真实 LLM 调用）
3. **开发你的模块** — 在 `modules/<模块名>/main.py` 里实现 `run(task, context) -> dict`
4. **在 `core/registry.py` 里注册** — 如果模块名跟现有的 5 个不同，加一行
5. **测试** — `python -m unittest discover -s tests -v`

### 调用 LLM 的方式

项目里已经有 LLM 抽象层，你的模块直接调就行：

```python
from core.llm import chat

def run(task, context):
    reply = chat("你的问题", system="你是一个XX专家", temperature=0.3)
    return {"status": "success", "summary": reply[:200], "data": {"full_report": reply}, "files": [], "logs": [], "error": None}
```

`chat()` 自动读 `.env` 里的配置（模型、API Key、地址），也接受前端设置面板的实时覆盖。你不用关心 API 细节。

### 返回格式（固定 6 个字段）

```python
{
    "status": "success",     # 或 "failed"、"partial"
    "summary": "一句话摘要",
    "data": {"key": "value"}, # 结构化数据，必须是字典
    "files": [],
    "logs": ["步骤1", "步骤2"],
    "error": None             # 成功时为 None
}
```

### 模块间传数据

如果上游模块（比如文献调研）提供了结果，你可以从 `context["previous_results"]` 读到它。示例：

```python
previous = context.get("previous_results", [])
lit_result = next((r for r in previous if r.get("module") == "literature"), None)
if lit_result:
    papers = lit_result.get("data", {}).get("full_report", "")
```

## 提交代码

```bash
git add modules/<你的模块>/
git commit -m "模块名：实现真 AI 调用"
git push
```

不要碰 `core/`、别人的模块、`对接文件/`，除非你在跟队长讨论后的架构变更。

## 问题

遇到任何问题：在 GitHub 开 Issue，或者直接在群里问队长。

队长：lucas — 负责 core 框架、LLM 抽象层、Web 前后端
