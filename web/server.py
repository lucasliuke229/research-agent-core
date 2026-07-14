"""Research Agent Core — FastAPI 后端

启动方式：
    source venv/bin/activate
    python web/server.py

然后浏览器打开 http://localhost:8000
"""

import sys
import os
import json
import pty
import struct
import fcntl
import termios
import asyncio
import subprocess
from pathlib import Path

# 把项目根目录加到 Python 搜索路径里 — server.py 在 web/ 子目录下
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from core import run_task, get_config_info

# ────────────────────────── 创建 FastAPI 应用 ──────────────────────────

app = FastAPI(
    title="Research Agent Core",
    description="模块化科研 AI 智能体框架",
    version="0.1.0",
)

WEB_DIR = Path(__file__).parent

# 挂载静态文件 — CSS / JS 从 web/ 子目录提供
app.mount("/css", StaticFiles(directory=str(WEB_DIR / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(WEB_DIR / "js")), name="js")


# ────────────────────────── API：运行科研任务 ──────────────────────────

@app.post("/api/run")
async def api_run_task(request: Request):
    """
    接收前端 JSON { task, task_type, llm_config? }，调用 core 执行流水线，返回结果。

    llm_config 可选字段：model, base_url, api_key
    用于运行时切换 AI 模型，覆盖 .env 默认值。
    """
    body = await request.json()
    task = body.get("task", "")
    task_type = body.get("task_type", "full")
    llm_config = body.get("llm_config", {})

    result = run_task(
        task=task,
        task_type=task_type,
        context={
            "domain": "mechanics",
            "language": "zh-CN",
            "llm_config": llm_config,   # 传给模块，模块读 context["llm_config"]
        },
    )
    return JSONResponse(content=result)


# ────────────────────────── API：获取配置信息 ──────────────────────────

@app.get("/api/config")
async def api_get_config():
    """返回当前 LLM 配置信息（密钥已隐藏）和预设模型列表。"""
    info = get_config_info()
    return JSONResponse(content=info)


# ────────────────────────── 前端页面 ──────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    """返回前端页面。"""
    return HTMLResponse(
        content=(WEB_DIR / "index.html").read_text(encoding="utf-8")
    )


# ────────────────────────── WebSocket：网页终端 ──────────────────────────
# 核心思路：创建一个 PTY（伪终端），一头接网页的 xterm.js，
# 另一头接一个真实的 bash 进程。你在网页里敲什么，bash 就收到什么；
# bash 输出什么，网页就显示什么。


class TerminalSession:
    """管理一个 PTY 终端会话。"""

    def __init__(self):
        self.master_fd: int | None = None
        self.proc: subprocess.Popen | None = None

    def start(self, rows: int = 24, cols: int = 80) -> None:
        """
        创建一个 PTY 对：
          - master_fd：我们读写的这一端
          - slave_fd：bash 进程读写的另一端

        PTY 的作用是让 bash 以为自己连着一个真正的终端
        （而不是一个程序），这样 claude、vim、top 等需要
        终端能力的命令才能正常工作。
        """
        master_fd, slave_fd = pty.openpty()

        # 设置终端窗口大小（行数 x 列数）
        winsize = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)

        # 启动 bash，让它的输入/输出都走 PTY 的 slave 端
        self.proc = subprocess.Popen(
            ["bash", "--login"],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            start_new_session=True,
            env={
                **os.environ,
                "TERM": "xterm-256color",
                "COLORTERM": "truecolor",
            },
        )

        # 关闭 slave 端 — 我们只需要 master 端跟它通信
        os.close(slave_fd)
        self.master_fd = master_fd

    def resize(self, rows: int, cols: int) -> None:
        """当用户拖拽网页终端的大小时，同步改 PTY 的窗口大小。"""
        if self.master_fd is None:
            return
        winsize = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)

    def read(self) -> bytes | None:
        """从 PTY 读数据（bash 的输出）。返回 None 表示终端已关闭。"""
        if self.master_fd is None:
            return None
        try:
            data = os.read(self.master_fd, 4096)
            if not data:
                return None
            return data
        except OSError:
            return None

    def write(self, data: bytes) -> None:
        """向 PTY 写数据（发送给 bash）。"""
        if self.master_fd is not None:
            os.write(self.master_fd, data)

    def close(self) -> None:
        """清理：关 PTY，杀进程。"""
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
            self.master_fd = None
        if self.proc is not None:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=2)
            except Exception:
                self.proc.kill()
            self.proc = None


@app.websocket("/ws/terminal")
async def terminal_ws(websocket: WebSocket):
    """
    网页终端 WebSocket 端点。

    通信协议（双向）：
      - 客户端 → 服务端：
          * 文本消息 = 用户在终端里敲的字符（UTF-8）
          * JSON 文本消息 {"type":"resize","rows":24,"cols":80} = 窗口大小变了
      - 服务端 → 客户端：
          * 二进制消息 = bash 的输出（终端屏幕内容）
    """
    await websocket.accept()

    session = TerminalSession()
    session.start()

    # asyncio.Queue 用于在两个异步任务之间传递 PTY 的输出数据
    read_queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def on_pty_readable():
        """当 PTY master fd 上有数据可读时，扔进队列。"""
        data = session.read()
        if data:
            read_queue.put_nowait(data)

    loop.add_reader(session.master_fd, on_pty_readable)

    async def pty_to_ws():
        """任务 1：持续从 PTY 读数据，发给网页。"""
        try:
            while True:
                data = await read_queue.get()
                await websocket.send_bytes(data)
        except Exception:
            pass

    async def ws_to_pty():
        """任务 2：持续从网页收数据，发往 PTY。"""
        try:
            while True:
                msg = await websocket.receive()
                if "text" in msg:
                    text = msg["text"]
                    # 尝试解析为 JSON（resize 命令）
                    try:
                        ctrl = json.loads(text)
                        if ctrl.get("type") == "resize":
                            session.resize(ctrl["rows"], ctrl["cols"])
                            continue
                    except (json.JSONDecodeError, KeyError, TypeError):
                        pass
                    # 普通终端输入
                    session.write(text.encode())
                elif "bytes" in msg:
                    session.write(msg["bytes"])
        except WebSocketDisconnect:
            pass
        except Exception:
            pass

    try:
        await asyncio.gather(pty_to_ws(), ws_to_pty())
    finally:
        loop.remove_reader(session.master_fd)
        session.close()


# ────────────────────────── 启动入口 ──────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "web.server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
