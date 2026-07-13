"""Research Agent Core — FastAPI 后端

启动方式：
    source venv/bin/activate
    python web/server.py

然后浏览器打开 http://localhost:8000
"""

import sys
from pathlib import Path

# 把项目根目录加到 Python 搜索路径里。
# 因为 server.py 在 web/ 子目录下，python web/server.py 运行时
# Python 默认从 web/ 开始找模块，找不到上一层的 core/。
# 这两行告诉 Python："往上走一层，那里还有模块要导入。"
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from core import run_task

# ────────────────────────── 创建 FastAPI 应用 ──────────────────────────

app = FastAPI(
    title="Research Agent Core",
    description="模块化科研 AI 智能体框架",
    version="0.1.0",
)


# ────────────────────────── API 接口 ──────────────────────────


@app.post("/api/run")
async def api_run_task(request: Request):
    """
    接收前端发来的任务，调用 core 跑流水线，返回结果。

    前端需要发送 JSON：
    {
        "task": "研究剪切增稠流体...",
        "task_type": "full" 或 "literature" / "theory" / "computation" / "experiment"
    }
    """
    body = await request.json()

    task = body.get("task", "")
    task_type = body.get("task_type", "full")

    # 调用你的 core，跟 demo.py 一模一样的逻辑
    result = run_task(
        task=task,
        task_type=task_type,
        context={
            "domain": "mechanics",
            "language": "zh-CN",
        },
    )

    return JSONResponse(content=result)


# ────────────────────────── 前端页面 ──────────────────────────

# 读取同目录下的 index.html
WEB_DIR = Path(__file__).parent


@app.get("/", response_class=HTMLResponse)
async def index():
    """返回前端页面。"""
    html_path = WEB_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


# ────────────────────────── 启动入口 ──────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "web.server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # 代码改了自动重启，开发时很方便
    )
