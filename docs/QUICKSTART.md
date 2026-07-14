# 队友操作手册

项目仓库：https://github.com/lucasliuke229/research-agent-core

---

## 零、这是什么项目

一个模块化的科研 AI 智能体框架。用户输入研究问题 → 调度器自动依次执行文献调研 → 理论分析 → 数值计算 → 实验设计 → 报告生成 → 输出结构化结果。

**核心层（core/）我已经写好了，你们只需要负责 modules/ 下的模块开发。** 每个模块就是一个文件夹，里面写一个 `run(task, context) -> dict` 函数，调 AI 完成该模块的研究任务。模块之间不需要互相引用，数据通过 core 调度器自动传递。

---

## 一、下载项目

打开终端（Mac 叫"终端"，Windows 叫 PowerShell），运行：

```bash
git clone https://github.com/lucasliuke229/research-agent-core.git
cd research-agent-core
```

如果你没装 git：Mac 用户 `brew install git`，Windows 用户去 https://git-scm.com 下载。

---

## 二、搭建 Python 环境

### 2.1 确认 Python 版本 >= 3.10

```bash
python3 --version
```

如果不是 3.10+，先去 https://python.org 下载安装。Mac 用户推荐 `brew install python@3.12`。

### 2.2 创建虚拟环境

虚拟环境 = 只属于这个项目的独立 Python 运行环境。所有包装在这里面，不污染你的系统 Python，不跟其他项目打架。

```bash
python3 -m venv venv
```

运行后项目文件夹里会出现一个 `venv/` 子目录。这个目录不会提交到 Git（.gitignore 已配置），如果环境坏了，删掉重建就行。

### 2.3 激活虚拟环境

**macOS / Linux：**

```bash
source venv/bin/activate
```

**Windows PowerShell：**

```powershell
venv\Scripts\activate
```

激活成功后，终端提示符前面会出现蓝色的 `(venv)` 标记。这表示你接下来的 `python` 和 `pip` 都是用的虚拟环境版本。

**验证一下：**

```bash
which python
```

输出应该包含 `.../research-agent-core/venv/bin/python`，而不是 `/usr/bin/python` 之类的系统路径。

### 2.4 安装依赖

```bash
pip install -r requirements.txt
```

自动安装 fastapi、uvicorn、openai、websockets、python-dotenv 等所有需要的包。

---

## 三、配置 AI 模型

### 3.1 获取 API Key

去你用的 AI 服务商后台申请一个 API Key：

- **DeepSeek**：https://platform.deepseek.com → API Keys → 创建密钥
- **OpenAI**：https://platform.openai.com → API Keys
- **通义千问**：https://dashscope.console.aliyun.com → 创建 API Key
- **智谱 GLM**：https://open.bigmodel.cn → API Keys
- **Ollama 本地**：不需要 Key，但需要先装 Ollama

### 3.2 创建配置文件

```bash
cp .env.example .env
```

打开 `.env` 文件（任何文本编辑器都行），把里面的配置改成你的：

```env
# 把 sk-your-api-key-here 换成你的真实密钥
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 如果用的是 DeepSeek，地址不用改。其他服务商换下面的地址
LLM_BASE_URL=https://api.deepseek.com

# 换成你想用的模型名
LLM_MODEL=deepseek-v4-pro
```

**其他服务商的 base_url 和 model 参考：**

| 服务商 | base_url | 模型名示例 |
|---|---|---|
| DeepSeek | `https://api.deepseek.com` | `deepseek-v4-pro`, `deepseek-v4-flash` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o`, `gpt-4o-mini` |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-max`, `qwen-plus` |
| 智谱 GLM | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-plus`, `glm-4-flash` |
| Kimi | `https://api.moonshot.cn/v1` | `moonshot-v1-128k` |
| Ollama 本地 | `http://localhost:11434/v1` | `qwen2.5`, `llama3.1` |

**Windows 用户注意：** 不要用"记事本"编辑 `.env`，它会偷偷加后缀 `.txt`。推荐用 VS Code、Sublime Text，或者直接终端里 `notepad .env`。

---

## 四、定制你的 AI 助手（重要！）

项目里有个 `CLAUDE.md` 文件，这是给 AI 助手看的项目指南。每个 AI 打开项目都会先读它。

**你必须把"用户信息"区域改成你自己的情况。** 打开 `CLAUDE.md`：

```markdown
## 用户信息（<-- 每位队友必须改成自己）

> ⚠️ 此区域为个人配置区……
```

把下面几行改成：
- 你的名字
- 你的背景（物理 / CS / 数学 / 什么水平）
- 你的偏好（喜欢详细注释还是简洁代码）
- 你的目标

你用什么 AI 工具？**如果你用 Claude Code（终端版）**，CLAUDE.md 自动生效。**如果你用 ChatGPT/其他 AI**，每次把 CLAUDE.md 的内容复制给你的 AI 让它了解项目规则。

---

## 五、验证环境

跑一下确认一切正常：

```bash
# 命令行模式
python demo.py
```

输出一堆 JSON 且最后没有 error 就对了。

```bash
# Web 工作台模式
python web/server.py
```

终端打印 `Uvicorn running on http://127.0.0.1:8000` 后，浏览器打开这个地址。你会看到一个三栏工作台界面——能输入科研问题、选运行模式、看流水线进度和结果。然后你可以换个模型——在网页里点设置，选你配置的任意模型，随时随地测模块输出。

**停止服务器：** 按 `Ctrl+C`。

---

## 六、开发你的模块

### 6.1 理解你要做什么

你要写的代码只在一个地方：`modules/<你的模块>/main.py`。里面有一个函数：

```python
def run(task: str, context: dict) -> dict:
    """
    task   — 用户输入的研究问题（字符串）
    context — 额外信息（字典），包含 language、domain、previous_results 等

    返回值必须是字典，包含 6 个固定字段：
        status:   "success" / "failed" / "partial"
        summary:  一句话摘要
        data:     结构化输出（字典，必须能转 JSON）
        files:    生成的文件路径列表
        logs:     运行日志列表
        error:    错误信息，没有就写 None
    """
```

### 6.2 调用 AI

项目里已经封装好了 LLM 调用。你只需要：

```python
from core.llm import chat

def run(task, context):
    try:
        reply = chat(
            "这里写你的 prompt，比如：请分析以下研究问题的理论基础：" + task,
            system="你是一个XX领域的专家。请用中文回答。",
            temperature=0.3,    # 0=精确，1=创意。科研分析建议 0.1-0.4
        )

        return {
            "status": "success",
            "summary": reply[:200] + "...",
            "data": {"full_report": reply},
            "files": [],
            "logs": ["模块执行完成"],
            "error": None,
        }
    except Exception as e:
        return {
            "status": "failed",
            "summary": "执行失败",
            "data": {},
            "files": [],
            "logs": [str(e)],
            "error": str(e),
        }
```

### 6.3 读取上游模块的结果

如果你的模块排在 literature 后面，你可以从 `context["previous_results"]` 读到文献模块的输出：

```python
previous = context.get("previous_results", [])

# 找到文献调研的结果
lit = next((r for r in previous if r.get("module") == "literature"), None)
if lit:
    papers = lit.get("data", {}).get("full_report", "")
    # 现在 papers 里是文献模块返回的完整报告，你可以用它做进一步分析
```

### 6.4 完整示例

打开 `modules/literature/main.py` 看参考实现。这个文件已经接入了真实 LLM 调用，是其他模块的标准模板。

### 6.5 规范文档

**必须读：** `对接文件/MODULE_FORMAT_SPEC_v0.1.md`。15 节，包含完整的返回格式规范、提交前检查清单、推荐代码写法。

---

## 七、当前模块分配

| 模块 | 文件路径 | 状态 | 谁负责 |
|---|---|---|---|
| 文献调研 | `modules/literature/main.py` | ✅ 已完成 | lucas |
| 理论分析 | `modules/theory/main.py` | ❌ 假数据待开发 | 待分配 |
| 数值计算 | `modules/computation/main.py` | ❌ 假数据待开发 | 待分配 |
| 实验设计 | `modules/experiment/main.py` | ❌ 假数据待开发 | 待分配 |
| 报告汇总 | `modules/report/main.py` | ❌ 假数据待开发 | 待分配 |

---

## 八、规则（重要）

**你可以做：**
- ✅ 在 `modules/<你的模块>/` 里随便写代码
- ✅ 新建文件、改 main.py、加 service.py、加 README.md
- ✅ 装新的 Python 包（用 `pip install 包名`，然后告诉我，我加到 requirements.txt 里）

**你不能做：**
- ❌ 改 `core/` 下的任何文件
- ❌ 改 `web/` 下的文件
- ❌ 改别人的模块
- ❌ 改 `对接文件/`、`docs/`、根目录文件（CLAUDE.md、README.md、requirements.txt 等）
- ❌ 从你的模块里直接 import 别人的模块（不允许 `from modules.theory.main import run`）

**如果你需要改公共文件，先跟队长说。** 比如你写了一个新模块需要注册到 registry，告诉我，我来加。

---

## 九、提交代码

```bash
# 确保在 venv 里
git add modules/<你的模块名>/
git commit -m "模块名：功能描述"
git push origin main
```

如果你删了或改了文件，也用 `git add` 提交改动。

---

## 十、常见问题

**Q: `ModuleNotFoundError: No module named 'xxx'`**

说明虚拟环境没激活。确认终端前面有 `(venv)` 标记，然后 `pip install -r requirements.txt`。

**Q: `LLM_API_KEY 未设置`**

说明 `.env` 文件没配好。确认执行过 `cp .env.example .env` 并且编辑了里面的 API Key。

**Q: `.env` 改了但没生效**

重启 `python web/server.py`。.env 在启动时加载一次，改了之后要重启。

**Q: 我的模块被 git 忽略了**

检查你的模块文件名是不是在 `.gitignore` 里。`outputs/` 目录里生成的文件会被忽略——这是故意的，生成结果不提交。

**Q: 怎么单独测试我的模块**

```python
# 在项目根目录跑
from modules.理论分析.main import run
result = run("研究问题", {"language": "zh-CN"})
print(result["summary"])
```

或者在网页工作台里选"单模块运行"，只跑你的模块看效果。

---

项目仓库：https://github.com/lucasliuke229/research-agent-core

有问题群里直接找我 —— 队长 lucas
