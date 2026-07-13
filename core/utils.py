"""核心层公共工具。"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any
from uuid import uuid4

from .state import ModuleResult, TaskStatus, utc_now_iso


def new_task_id() -> str:
    """生成便于日志追踪的短任务 ID。"""
    return uuid4().hex[:12]


def validate_task(task: str, context: dict[str, Any]) -> None:
    if not isinstance(task, str):
        raise TypeError("task 必须是字符串")
    if not task.strip():
        raise ValueError("task 不能为空")
    if not isinstance(context, dict):
        raise TypeError("context 必须是 dict")


def normalize_result(
    raw_result: ModuleResult | Mapping[str, Any],
    *,
    module_name: str,
    started_at: str,
) -> ModuleResult:
    """将模块返回的 dataclass 或 dict 统一转换为 ModuleResult。"""
    if isinstance(raw_result, ModuleResult):
        raw_result.module = raw_result.module or module_name
        # 任务执行起点以调度器记录为准，模块只负责业务结果。
        raw_result.started_at = started_at
        raw_result.finished_at = utc_now_iso()
        return raw_result

    if not isinstance(raw_result, Mapping):
        raise TypeError(
            f"模块 {module_name!r} 必须返回 ModuleResult 或 Mapping，"
            f"实际返回 {type(raw_result).__name__}"
        )

    status_value = raw_result.get("status", "success")
    try:
        status = (
            status_value
            if isinstance(status_value, TaskStatus)
            else TaskStatus(str(status_value))
        )
    except ValueError as exc:
        raise ValueError(
            f"模块 {module_name!r} 返回了非法状态 {status_value!r}"
        ) from exc

    summary = raw_result.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError(f"模块 {module_name!r} 的 summary 必须是非空字符串")

    files = raw_result.get("files", [])
    logs = raw_result.get("logs", [])
    data = raw_result.get("data", {})

    if not isinstance(files, list) or not all(isinstance(x, str) for x in files):
        raise TypeError(f"模块 {module_name!r} 的 files 必须是字符串列表")
    if not isinstance(logs, list) or not all(isinstance(x, str) for x in logs):
        raise TypeError(f"模块 {module_name!r} 的 logs 必须是字符串列表")
    if not isinstance(data, dict):
        raise TypeError(f"模块 {module_name!r} 的 data 必须是 dict")

    return ModuleResult(
        status=status,
        summary=summary,
        files=files,
        logs=logs,
        data=data,
        error=raw_result.get("error"),
        module=module_name,
        started_at=started_at,
        finished_at=utc_now_iso(),
    )


def ensure_output_dir(path: str | Path) -> Path:
    output_dir = Path(path)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir
