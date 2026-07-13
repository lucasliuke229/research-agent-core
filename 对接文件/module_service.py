from __future__ import annotations

from typing import Any


def execute_module(
    task: str,
    context: dict[str, Any],
) -> dict[str, Any]:
    """在这里实现模块自己的真实功能。"""

    language = context.get("language", "zh-CN")

    return {
        "summary": "模块真实功能执行完成",
        "data": {
            "task": task,
            "language": language,
        },
        "files": [],
        "logs": [
            "business logic completed",
        ],
    }
