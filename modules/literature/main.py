"""文献调研模块 —— 调用 LLM 进行真实的文献检索与分析。

通过 core.llm.chat() 调用 AI，不依赖特定服务商。
换 DeepSeek / OpenAI / Claude 只改 .env 文件。
"""

from core.llm import chat


# 系统提示词 —— 告诉 AI 它要扮演的角色
SYSTEM_PROMPT = (
    "你是一个专业的科研文献调研助手。你的任务是根据用户的研究课题，"
    "进行系统的文献检索和分析。请用中文回复。\n\n"
    "请按以下结构组织你的回答：\n"
    "1. 核心关键词与检索策略\n"
    "2. 该领域的发展脉络（奠基性工作 → 关键进展 → 当前前沿）\n"
    "3. 5-8 篇最相关的研究工作（标题、第一作者、年份、核心贡献、方法、局限性）\n"
    "4. 现有研究的共同局限和未解决的问题\n"
    "5. 对用户研究方向的建议切入点"
)


def run(task: str, context: dict) -> dict:
    """
    文献调研模块的入口函数。

    task    —— 用户的研究问题
    context —— 调度器传入的上下文（含语言、领域等）
    """
    prompt = _build_prompt(task, context)

    # 从前端传来的 llm_config 中提取运行时模型覆盖参数
    llm_config = context.get("llm_config", {})

    try:
        reply = chat(prompt,
                     system=SYSTEM_PROMPT,
                     temperature=0.3,
                     model=llm_config.get("model", ""),
                     base_url=llm_config.get("base_url", ""),
                     api_key=llm_config.get("api_key", ""))
        return {
            "status": "success",
            "summary": _extract_summary(reply),
            "data": {
                "full_report": reply,
                "word_count": len(reply),
            },
            "files": [],
            "logs": ["literature: AI 文献调研完成"],
            "error": None,
        }
    except Exception as exc:
        return {
            "status": "failed",
            "summary": "文献调研失败",
            "data": {},
            "files": [],
            "logs": [f"literature: {exc}"],
            "error": str(exc),
        }


def _build_prompt(task: str, context: dict) -> str:
    """根据任务和上下文，拼出完整的 prompt。"""
    language = context.get("language", "zh-CN")
    domain = context.get("domain", "")
    if domain:
        return f"研究领域：{domain}\n研究课题：{task}\n请用{'中文' if 'zh' in language else '英文'}回复。"
    return f"研究课题：{task}\n请用{'中文' if 'zh' in language else '英文'}回复。"


def _extract_summary(reply: str) -> str:
    """从 AI 的完整回复中，提取一行简短的摘要。"""
    first_line = reply.strip().split("\n")[0]
    if len(first_line) > 120:
        return first_line[:120] + "..."
    return first_line
