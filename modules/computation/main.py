"""计算模块 Demo。"""


def run(task: str, context: dict) -> dict:
    previous_count = len(context.get("previous_results", []))
    return {
        "status": "success",
        "summary": "已形成数值计算方案骨架",
        "data": {
            "steps": [
                "定义控制方程与边界条件",
                "选择离散方法与收敛准则",
                "设计参数扫描和敏感性分析",
                "输出可复现实验与误差评估",
            ],
            "previous_results_seen": previous_count,
        },
        "files": [],
        "logs": [f"computation: received {previous_count} previous results"],
    }
