"""任务状态与模块结果的数据模型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def utc_now_iso() -> str:
    """返回带时区的 UTC ISO 时间。"""
    return datetime.now(timezone.utc).isoformat()


class TaskStatus(str, Enum):
    """任务和模块统一使用的状态枚举。"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass(slots=True)
class ModuleResult:
    """一个能力模块的标准返回值。"""

    status: TaskStatus
    summary: str
    files: list[str] = field(default_factory=list)
    logs: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    module: str | None = None
    started_at: str = field(default_factory=utc_now_iso)
    finished_at: str | None = None

    @classmethod
    def success(
        cls,
        summary: str,
        *,
        files: list[str] | None = None,
        logs: list[str] | None = None,
        data: dict[str, Any] | None = None,
        module: str | None = None,
    ) -> "ModuleResult":
        now = utc_now_iso()
        return cls(
            status=TaskStatus.SUCCESS,
            summary=summary,
            files=files or [],
            logs=logs or [],
            data=data or {},
            module=module,
            started_at=now,
            finished_at=now,
        )

    @classmethod
    def failed(
        cls,
        summary: str,
        *,
        error: str,
        logs: list[str] | None = None,
        module: str | None = None,
    ) -> "ModuleResult":
        now = utc_now_iso()
        return cls(
            status=TaskStatus.FAILED,
            summary=summary,
            logs=logs or [],
            error=error,
            module=module,
            started_at=now,
            finished_at=now,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "summary": self.summary,
            "files": list(self.files),
            "logs": list(self.logs),
            "data": dict(self.data),
            "error": self.error,
            "module": self.module,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }


@dataclass(slots=True)
class TaskState:
    """一次用户任务从开始到结束的完整状态。"""

    task_id: str
    task: str
    task_type: str
    context: dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    current_module: str | None = None
    results: list[ModuleResult] = field(default_factory=list)
    logs: list[str] = field(default_factory=list)
    started_at: str = field(default_factory=utc_now_iso)
    finished_at: str | None = None

    def add_log(self, message: str) -> None:
        self.logs.append(f"[{utc_now_iso()}] {message}")

    def add_result(self, result: ModuleResult) -> None:
        self.results.append(result)
        self.logs.extend(result.logs)

    def finish(self) -> None:
        """根据所有模块结果计算任务总状态。"""
        self.finished_at = utc_now_iso()
        self.current_module = None

        if not self.results:
            self.status = TaskStatus.FAILED
            return

        statuses = {result.status for result in self.results}
        if statuses == {TaskStatus.SUCCESS}:
            self.status = TaskStatus.SUCCESS
        elif TaskStatus.SUCCESS in statuses:
            self.status = TaskStatus.PARTIAL
        else:
            self.status = TaskStatus.FAILED

    def to_response(self) -> dict[str, Any]:
        """转换为 Web/CLI 可以直接消费的统一响应。"""
        files = [path for result in self.results for path in result.files]
        summaries = [
            f"{result.module}: {result.summary}" if result.module else result.summary
            for result in self.results
        ]
        errors = [result.error for result in self.results if result.error]

        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status.value,
            "summary": "\n".join(summaries) if summaries else "任务未产生结果",
            "files": files,
            "logs": list(self.logs),
            "error": "\n".join(errors) if errors else None,
            "results": [result.to_dict() for result in self.results],
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }
