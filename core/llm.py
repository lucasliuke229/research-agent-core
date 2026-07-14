"""LLM 抽象层 —— 所有模块通过这个文件调用 AI，不直接依赖任何特定服务商。

设计原则：
- 模块不关心后端是谁（DeepSeek / OpenAI / Claude / 本地模型）
- 换模型只改 .env 文件，代码一行不动（也可以前端设置面板运行时切换）
- 使用 OpenAI 兼容格式（绝大多数国产模型都支持）

配置方式（在项目根目录创建 .env 文件）：
    LLM_API_KEY=sk-xxxxxxxx
    LLM_BASE_URL=https://api.deepseek.com
    LLM_MODEL=deepseek-chat

从前端传入 llm_config 可以覆盖 .env 的默认值，支持运行时切换模型。
"""

from __future__ import annotations

import os
from pathlib import Path

# ────────────────────────── 加载 .env 文件 ──────────────────────────

try:
    from dotenv import load_dotenv

    _env_path = Path(__file__).resolve().parent.parent / ".env"
    if _env_path.exists():
        load_dotenv(_env_path)
except ImportError:
    pass

# ────────────────────────── 配置读取 ──────────────────────────

API_KEY = os.getenv("LLM_API_KEY", "")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

# ────────────────────────── 预设模型列表 ──────────────────────────
# 前端设置面板也会有一份，这里提供给后端 /api/presets 使用

PRESETS = [
    {
        "id": "deepseek",
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "description": "国产高性价比模型，适合科研分析",
    },
    {
        "id": "openai",
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o", "gpt-4o-mini", "o3-mini"],
        "description": "综合能力最强的闭源模型",
    },
    {
        "id": "claude",
        "name": "Anthropic Claude",
        "base_url": "https://api.anthropic.com/v1",
        "models": ["claude-sonnet-4-20250514", "claude-haiku-3-5-20250613"],
        "description": "长文本分析与科研写作能力突出",
    },
    {
        "id": "groq",
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "models": ["llama-3.1-70b-versatile", "mixtral-8x7b-32768"],
        "description": "开源模型高速推理（需单独注册）",
    },
    {
        "id": "qwen",
        "name": "通义千问",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": ["qwen-max", "qwen-plus", "qwen-turbo"],
        "description": "阿里云出品，中文能力优秀",
    },
    {
        "id": "zhipu",
        "name": "智谱 GLM",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "models": ["glm-4-plus", "glm-4-flash"],
        "description": "清华系，中文理解出色",
    },
    {
        "id": "kimi",
        "name": "Moonshot (Kimi)",
        "base_url": "https://api.moonshot.cn/v1",
        "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        "description": "超长上下文，适合处理长论文",
    },
    {
        "id": "ollama",
        "name": "Ollama（本地）",
        "base_url": "http://localhost:11434/v1",
        "models": ["qwen2.5", "llama3.1", "deepseek-r1", "mistral"],
        "description": "本地运行，无需联网，完全免费",
    },
]

# ────────────────────────── 核心接口 ──────────────────────────


def chat(
    prompt: str,
    *,
    system: str = "",
    temperature: float = 0.7,
    max_tokens: int = 4096,
    model: str = "",
    base_url: str = "",
    api_key: str = "",
) -> str:
    """
    发送 prompt 给 LLM，返回模型回复的文本。

    参数：
        prompt  - 用户消息（必填）
        system  - 系统提示词（可选）
        temperature - 随机程度，0=确定，1=创意（默认 0.7）
        max_tokens  - 回复最大长度（默认 4096）
        model    - 覆盖 .env 的模型名（可选，从前端传）
        base_url - 覆盖 .env 的 API 地址（可选）
        api_key  - 覆盖 .env 的密钥（可选）

    返回：
        AI 回复的纯文本字符串
    """
    # 运行时覆盖优先，否则用 .env 默认值
    _api_key = api_key or API_KEY
    _base_url = base_url or BASE_URL
    _model = model or MODEL

    if not _api_key:
        raise RuntimeError(
            "LLM_API_KEY 未设置。请在项目根目录创建 .env 文件，"
            "或在网页的设置面板中填写 API Key。"
        )

    from openai import OpenAI

    client = OpenAI(api_key=_api_key, base_url=_base_url)

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    content = response.choices[0].message.content
    return content.strip() if content else ""


def get_config_info() -> dict:
    """
    返回当前配置信息（隐藏密钥），供前端设置面板显示。

    返回：
        {
            "model": "deepseek-chat",
            "base_url": "https://api.deepseek.com",
            "has_api_key": true,    # 密钥是否已配置（不暴露真实值）
            "presets": [...],       # 全部预设模型列表
        }
    """
    return {
        "model": MODEL,
        "base_url": BASE_URL,
        "has_api_key": bool(API_KEY),
        "presets": PRESETS,
    }
