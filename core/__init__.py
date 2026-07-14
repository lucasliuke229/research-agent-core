"""Research Agent 核心层公共入口。

业务代码只需要依赖这里导出的接口，避免直接耦合内部实现。
"""

from .orchestrator import Orchestrator, run_task
from .registry import ModuleRegistry, default_registry, load_builtin_modules
from .state import ModuleResult, TaskState, TaskStatus
from .llm import chat, get_config_info

__all__ = [
    "Orchestrator",
    "run_task",
    "ModuleRegistry",
    "default_registry",
    "load_builtin_modules",
    "ModuleResult",
    "TaskState",
    "TaskStatus",
    "chat",
    "get_config_info",
]
