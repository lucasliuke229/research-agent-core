"""科研 Agent 总调度器。"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable

from .registry import ModuleRegistry, default_registry, load_builtin_modules
from .state import ModuleResult, TaskState, TaskStatus, utc_now_iso
from .utils import new_task_id, normalize_result, validate_task

DEFAULT_FULL_PIPELINE = (
    "literature",
    "theory",
    "computation",
    "experiment",
    "report",
)


class Orchestrator:
    """负责任务校验、模块执行、状态更新和异常隔离。"""

    def __init__(
        self,
        registry: ModuleRegistry | None = None,
        *,
        auto_load_builtin: bool = True,
    ) -> None:
        self.registry = registry or default_registry
        if auto_load_builtin:
            load_builtin_modules(self.registry)

    def run_task(
        self,
        task: str,
        task_type: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """运行单模块任务；task_type='full' 时运行默认流水线。"""
        context = deepcopy(context or {})
        task_type = task_type.strip().lower()

        state = TaskState(
            task_id=new_task_id(),
            task=task,
            task_type=task_type,
            context=context,
        )

        try:
            validate_task(task, context)
            state.status = TaskStatus.RUNNING
            state.add_log(f"任务开始，类型={task_type}")

            if task_type == "full":
                self._run_pipeline(
                    state,
                    DEFAULT_FULL_PIPELINE,
                    stop_on_error=False,
                )
            else:
                self._run_one(state, task_type)

        except Exception as exc:
            state.add_result(
                ModuleResult.failed(
                    "核心调度失败",
                    error=f"{type(exc).__name__}: {exc}",
                    module="core",
                )
            )
            state.add_log("任务在核心调度阶段失败")
        finally:
            state.finish()
            state.add_log(f"任务结束，状态={state.status.value}")

        return state.to_response()

    def run_pipeline(
        self,
        task: str,
        modules: Iterable[str],
        context: dict[str, Any] | None = None,
        *,
        stop_on_error: bool = True,
    ) -> dict[str, Any]:
        """运行用户指定的多模块流水线。"""
        context = deepcopy(context or {})
        state = TaskState(
            task_id=new_task_id(),
            task=task,
            task_type="pipeline",
            context=context,
            status=TaskStatus.RUNNING,
        )

        try:
            validate_task(task, context)
            self._run_pipeline(state, modules, stop_on_error=stop_on_error)
        except Exception as exc:
            state.add_result(
                ModuleResult.failed(
                    "流水线调度失败",
                    error=f"{type(exc).__name__}: {exc}",
                    module="core",
                )
            )
        finally:
            state.finish()

        return state.to_response()

    def _run_pipeline(
        self,
        state: TaskState,
        modules: Iterable[str],
        *,
        stop_on_error: bool,
    ) -> None:
        module_names = [name.strip().lower() for name in modules]
        if not module_names:
            raise ValueError("流水线至少需要一个模块")

        state.add_log(f"流水线开始：{' -> '.join(module_names)}")

        for module_name in module_names:
            result = self._run_one(state, module_name)

            # 后续模块可读取前序模块的结构化结果。
            state.context.setdefault("previous_results", []).append(
                result.to_dict()
            )

            if result.status == TaskStatus.FAILED and stop_on_error:
                state.add_log(f"模块 {module_name} 失败，流水线终止")
                break

    def _run_one(
        self,
        state: TaskState,
        module_name: str,
    ) -> ModuleResult:
        state.current_module = module_name
        state.add_log(f"准备运行模块：{module_name}")
        started_at = utc_now_iso()

        try:
            spec = self.registry.get(module_name)
            raw_result = spec.runner(state.task, deepcopy(state.context))
            result = normalize_result(
                raw_result,
                module_name=module_name,
                started_at=started_at,
            )
        except Exception as exc:
            result = ModuleResult.failed(
                f"模块 {module_name} 执行失败",
                error=f"{type(exc).__name__}: {exc}",
                logs=[f"{module_name}: exception captured by orchestrator"],
                module=module_name,
            )

        state.add_result(result)
        state.add_log(
            f"模块 {module_name} 完成，状态={result.status.value}"
        )
        return result


_default_orchestrator: Orchestrator | None = None


def run_task(
    task: str,
    task_type: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """函数式门面，供 Web 层直接调用。"""
    global _default_orchestrator

    if _default_orchestrator is None:
        _default_orchestrator = Orchestrator()

    return _default_orchestrator.run_task(task, task_type, context)
