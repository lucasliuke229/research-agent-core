"""实验模块 Demo。"""


def run(task: str, context: dict) -> dict:
    """返回实验设计方案骨架。"""
    return {
        "status": "success",
        "summary": "已生成实验流程骨架",
        "data": {
            "sections": [
                "研究目的与假设",
                "材料与仪器",
                "自变量、因变量和控制变量",
                "实验步骤",
                "数据记录与不确定度",
                "安全与失效处理",
            ],
        },
        "files": [],
        "logs": ["experiment: protocol skeleton generated"],
        "error": None,
    }
