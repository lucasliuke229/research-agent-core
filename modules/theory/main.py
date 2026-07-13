"""理论分析模块 Demo。"""


def run(task: str, context: dict) -> dict:
    domain = context.get("domain", "general science")
    return {
        "status": "success",
        "summary": "已生成理论分析框架",
        "data": {
            "domain": domain,
            "questions": [
                "研究对象的控制变量是什么？",
                "核心机理及其可证伪假设是什么？",
                "哪些无量纲参数可能支配状态转变？",
            ],
        },
        "files": [],
        "logs": [f"theory: domain={domain}", f"theory: task={task}"],
    }
