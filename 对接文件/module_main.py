from __future__ import annotations

from typing import Any

from .service import execute_module


def run(task: str, context: dict[str, Any]) -> dict[str, Any]:
    """Core 调用本模块的唯一入口。"""

    try:
        result = execute_module(
            task=task,
            context=context,
        )

        return {
            "status": "success",
            "summary": result["summary"],
            "data": result.get("data", {}),
            "files": result.get("files", []),
            "logs": result.get("logs", []),
            "error": None,
        }

    except Exception as exc:
        return {
            "status": "failed",
            "summary": "模块执行失败",
            "data": {},
            "files": [],
            "logs": [
                "module execution failed",
            ],
            "error": f"{type(exc).__name__}: {exc}",
        }
