# 环境配置指南

这份文档告诉你如何从零开始把这个项目跑起来。

---

## 你需要什么

| 要求 | 说明 |
|---|---|
| Python 3.10 或更高 | `python3 --version` 查看版本 |
| macOS / Linux / Windows | 三个平台都可以 |
| 终端（命令行） | macOS 用"终端"，Windows 用 PowerShell |
| 约 50MB 磁盘空间 | 虚拟环境 + 依赖包的大小 |

---

## 第一步：下载项目

```bash
# 如果项目在 Git 仓库里
git clone <仓库地址>
cd research_agent_core_demo

# 如果是本地文件夹，直接 cd 进去
cd /path/to/research_agent_core_demo
```

`cd` 之后你就在项目根目录了。**以下所有命令都在项目根目录下运行。**

---

## 第二步：确认 Python 版本

```bash
python3 --version
```

如果版本低于 3.10，需要先升级 Python。macOS 用户推荐用 Homebrew：

```bash
brew install python@3.12
```

---

## 第三步：创建虚拟环境

**什么是虚拟环境？** 一个只属于这个项目的独立 Python 运行环境。所有包都装在这里面，不污染你的系统 Python，不跟其他项目打架。

```bash
python3 -m venv venv
```

运行后项目文件夹里会出现一个 `venv/` 目录。这个目录：
- 删掉就相当于完全卸载环境，不影响任何别的东西
- 不会提交到 Git（`.gitignore` 里已忽略）
- 如果哪天环境坏了，删掉重新跑这一行就行

---

## 第四步：激活虚拟环境

**macOS / Linux：**

```bash
source venv/bin/activate
```

**Windows：**

```powershell
venv\Scripts\activate
```

激活成功后，终端提示符前会出现 `(venv)` 标记。这说明当前终端里的 `python` 和 `pip` 都是用的虚拟环境里的版本。

**验证：**

```bash
which python
# 应该显示 .../research_agent_core_demo/venv/bin/python
```

---

## 第五步：安装依赖

```bash
pip install -r requirements.txt
```

这会安装列表里列出的所有包。核心框架本身是纯 Python 标准库，不需要装任何东西。目前需要额外安装的是 FastAPI（Web 后端）和 Uvicorn（Web 服务器）。

---

## 第六步：跑起来

**命令行模式：**

```bash
python demo.py
```

**Web 界面模式：**

```bash
python web/server.py
```

浏览器打开 `http://localhost:8000`，在网页里输入任务、选类型、点运行。

---

## 日常使用

每次打开终端要跑这个项目时：

```bash
cd /path/to/research_agent_core_demo   # 进入项目
source venv/bin/activate               # 激活环境
python demo.py                         # 命令行跑
python web/server.py                   # Web 界面跑
```

用完退出环境：

```bash
deactivate
```

---

## 常见问题

### Q: 提示 `No module named 'xxx'`

激活了虚拟环境（`(venv)` 标记出现了）却报这个错，说明包没装全：

```bash
pip install -r requirements.txt
```

### Q: 虚拟环境坏了怎么办

删掉重建：

```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Q: 想加新的包

```bash
# 先激活环境
source venv/bin/activate
# 安装
pip install 包名
# 记下来，方便别人复现
pip freeze | grep 包名 >> requirements.txt
```

### Q: macOS 上 python3 命令找不到

macOS 自带的是 `python3`，如果你的系统上叫 `python`，把上面所有 `python3` 替换成 `python` 就行。

---

## 本项目作者的本地环境（仅供参考）

这不是要求，只是记录作者开发时用的环境。如果你的配置不一样，按上面步骤走就行，不需要跟这里一模一样。

| 项目 | 作者环境 |
|---|---|
| 操作系统 | macOS |
| Python 路径 | `/opt/homebrew/bin/python3` |
| Python 版本 | 3.10+ |
| 虚拟环境路径 | `项目根目录/venv/` |
| 包管理器 | pip |
