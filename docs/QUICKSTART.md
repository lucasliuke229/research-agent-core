# 队友快速上手指南

## 1. 下载项目

```bash
git clone https://github.com/lucasliuke229/research-agent-core.git
cd research-agent-core
```

## 2. 搭建环境

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. 配置 AI 模型

```bash
cp .env.example .env
nano .env
```

把 `sk-your-api-key-here` 换成你自己的 DeepSeek API Key（或任何兼容 OpenAI 格式的 Key）。

## 4. 定制你的 AI 助手

打开 `CLAUDE.md`，找到"用户信息"区域，把那几行改成你自己的情况。这样你的 AI 才知道怎么配合你。

## 5. 跑一下确认环境正确

```bash
python demo.py
# 能跑通就说明环境对了

python web/server.py
# 浏览器打开 http://localhost:8000，能看到工作台界面
```

## 6. 开始开发你的模块

1. 读 `对接文件/MODULE_FORMAT_SPEC_v0.1.md`（15 节，5 分钟看完）
2. 看示例代码 `modules/literature/main.py`（已接入真实 AI 调用）
3. 在 `modules/<你的模块>/main.py` 里实现 `run(task, context) -> dict`
4. 调用 LLM 的方式：`from core.llm import chat`，然后 `chat("你的问题", system="你是XX专家")`
5. 返回格式固定 6 个字段：`status`、`summary`、`data`、`files`、`logs`、`error`

## 规则

- **只能改** `modules/<你的模块>/` 目录下的文件
- **不能动** `core/`、`web/`、`对接文件/`、根目录文件
- 如果需要在 `core/registry.py` 注册新模块，先跟我说

## 遇到问题

- 先看 `docs/TEAM.md` 和 `docs/SETUP.md`
- 找我：队长 lucas，直接在群里问

---

项目仓库：https://github.com/lucasliuke229/research-agent-core
