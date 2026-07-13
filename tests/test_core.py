"""仅依赖标准库的核心层测试。"""

import unittest

from core.orchestrator import Orchestrator
from core.registry import ModuleRegistry


class CoreTests(unittest.TestCase):
    def test_successful_module(self):
        registry = ModuleRegistry()

        def demo(task, context):
            return {
                "status": "success",
                "summary": f"done: {task}",
                "files": [],
                "logs": ["ok"],
            }

        registry.register("demo", demo)
        result = Orchestrator(
            registry,
            auto_load_builtin=False,
        ).run_task("test task", "demo")

        self.assertEqual(result["status"], "success")
        self.assertIn("done: test task", result["summary"])

    def test_unknown_module_is_captured(self):
        registry = ModuleRegistry()
        result = Orchestrator(
            registry,
            auto_load_builtin=False,
        ).run_task("test task", "missing")

        self.assertEqual(result["status"], "failed")
        self.assertIn("未知模块", result["error"])

    def test_module_exception_is_isolated(self):
        registry = ModuleRegistry()

        def broken(task, context):
            raise RuntimeError("simulated failure")

        registry.register("broken", broken)
        result = Orchestrator(
            registry,
            auto_load_builtin=False,
        ).run_task("test task", "broken")

        self.assertEqual(result["status"], "failed")
        self.assertIn("simulated failure", result["error"])


if __name__ == "__main__":
    unittest.main()
