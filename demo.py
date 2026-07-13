"""命令行运行示例。"""

import json

from core import run_task


if __name__ == "__main__":
    result = run_task(
        "研究剪切增稠流体在复杂冲击加载下的阻塞相变",
        "full",
        context={
            "domain": "mechanics",
            "language": "zh-CN",
        },
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
