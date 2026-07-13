"""能力模块注册中心。

注册中心只负责“模块叫什么、入口函数在哪里”，不负责执行模块。
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any, Callable, Mapping

from .state import ModuleResult

Runner = Callable[[str, dict[str, Any]], ModuleResult | Mapping[str, Any]]


@dataclass(frozen=True, slots=True)
class ModuleSpec:
    name: str
    runner: Runner
    description: str = ""


class ModuleRegistry:
    """可测试、可扩展的模块注册表。"""

    def __init__(self) -> None:
        self._modules: dict[str, ModuleSpec] = {}

    def register(
        self,
        name: str,
        runner: Runner,
        *,
        description: str = "",
        overwrite: bool = False,
    ) -> None:
        normalized_name = name.strip().lower()
        if not normalized_name:
            raise ValueError("模块名称不能为空")
        if not callable(runner):
            raise TypeError(f"模块 {normalized_name!r} 的 runner 必须可调用")
        if normalized_name in self._modules and not overwrite:
            raise ValueError(f"模块 {normalized_name!r} 已注册")

        self._modules[normalized_name] = ModuleSpec(
            name=normalized_name,
            runner=runner,
            description=description,
        )

    def module(
        self,
        name: str,
        *,
        description: str = "",
        overwrite: bool = False,
    ):
        """装饰器注册方式，适合插件模块。"""

        def decorator(runner: Runner) -> Runner:
            self.register(
                name,
                runner,
                description=description,
                overwrite=overwrite,
            )
            return runner

        return decorator

    def get(self, name: str) -> ModuleSpec:
        normalized_name = name.strip().lower()
        try:
            return self._modules[normalized_name]
        except KeyError as exc:
            available = ", ".join(self.names()) or "无"
            raise KeyError(
                f"未知模块 {normalized_name!r}；当前可用模块：{available}"
            ) from exc

    def has(self, name: str) -> bool:
        return name.strip().lower() in self._modules

    def names(self) -> list[str]:
        return sorted(self._modules)

    def describe(self) -> dict[str, str]:
        return {
            name: spec.description
            for name, spec in sorted(self._modules.items())
        }


default_registry = ModuleRegistry()

_BUILTIN_MODULES = {
    "theory": (
        "modules.theory.main",
        "理论分析、公式推导与机制解释",
    ),
    "computation": (
        "modules.computation.main",
        "数值计算、仿真方案与代码生成",
    ),
    "experiment": (
        "modules.experiment.main",
        "实验方案、参数表与操作流程",
    ),
    "literature": (
        "modules.literature.main",
        "论文检索、阅读与证据整理",
    ),
    "report": (
        "modules.report.main",
        "汇总各模块结果并生成报告",
    ),
}


def load_builtin_modules(
    registry: ModuleRegistry = default_registry,
) -> ModuleRegistry:
    """按路径延迟导入内置模块，避免 core 与 modules 强耦合。"""
    for name, (module_path, description) in _BUILTIN_MODULES.items():
        if registry.has(name):
            continue

        module = import_module(module_path)
        runner = getattr(module, "run", None)
        if runner is None:
            raise AttributeError(f"{module_path} 缺少 run(task, context) 入口")

        registry.register(name, runner, description=description)

    return registry
