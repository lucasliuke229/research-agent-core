"""报告汇总模块 Demo。"""


def run(task: str, context: dict) -> dict:
    previous = context.get("previous_results", [])
    successful = [
        item for item in previous if item.get("status") == "success"
    ]
    return {
        "status": "success",
        "summary": f"已汇总 {len(successful)} 个成功模块的结果",
        "data": {
            "report_title": f"科研任务报告：{task[:40]}",
            "source_modules": [
                item.get("module") for item in successful
            ],
        },
        "files": [],
        "logs": ["report: previous module results summarized"],
    }
