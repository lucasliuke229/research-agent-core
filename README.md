# Research Agent Core

模块化的科研 AI 智能体框架。调度器按流水线依次执行文献调研 → 理论分析 → 数值计算 → 实验设计 → 报告生成，每个模块独立开发、统一对接，最终汇总为结构化研究结果。

## 项目愿景

不是比赛 demo，不是半成品。目标是做一个**长期维护、可分享给其他科研人员使用的生产级研究 Agent 平台**。

## 快速开始

**首次使用请先看 [`docs/SETUP.md`](docs/SETUP.md)**，里面有从零开始配置环境的完整步骤。

```bash
# 1. 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 命令行运行
python demo.py

# 4. 运行测试
python -m unittest discover -s tests -v

# 5. Web 界面
python web/server.py
# 浏览器打开 http://localhost:8000
```

## 项目结构

```
research_agent_core_demo/
├── core/                   ← 核心框架（不要随便动）
│   ├── state.py            → 数据格式：TaskStatus、ModuleResult、TaskState
│   ├── registry.py         → 模块注册中心（电话簿）
│   ├── orchestrator.py     → 调度器（大脑）
│   ├── utils.py            → 工具箱：校验、规范化、生成 ID
│   └── __init__.py         → 对外统一入口
│
├── modules/                ← 可插拔的研究能力模块
│   ├── literature/         → 文献检索
│   ├── theory/             → 理论分析
│   ├── computation/        → 数值计算
│   ├── experiment/         → 实验设计
│   └── report/             → 报告汇总
│
├── web/                    ← 前端界面
│   ├── server.py           → FastAPI 后端
│   ├── index.html          → 现代前端页面
│   └── app.py              → [已废弃] Streamlit 旧版
│
├── tests/                  ← 测试
│   └── test_core.py
│
├── docs/                   ← 文档
│   ├── ARCHITECTURE.md     → 架构设计文档
│   └── SETUP.md            → 环境配置指南
│
├── 对接文件/                ← 模块开发规范（给模块开发者看的）
│   ├── MODULE_FORMAT_SPEC_v0.1.md
│   ├── module_main.py
│   └── module_service.py
│
├── lessons/                ← 教学代码（给初学者看的）
│   ├── lesson1_variables.py
│   ├── lesson2_functions.py
│   └── lesson3_classes_v2.py
│
├── skills/                 ← 自定义 AI 技能（个人配置，不提交 git）
│
├── demo.py                 ← 命令行入口
├── requirements.txt        ← 依赖列表
├── CLAUDE.md               ← AI 助手行为约束
├── .gitignore              ← Git 忽略规则
├── LICENSE                 ← MIT 许可证
└── README.md               ← 你在这里
```

## 架构

详细架构文档见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。

核心思想：**state.py 定义格式 → registry.py 登记模块 → orchestrator.py 调度执行 → utils.py 保证格式统一。**

调度器不直接 import 任何模块，通过注册中心按名字查找。加新模块只改注册中心，调度器代码一行不动。

## 如何开发新模块

1. 在 `modules/` 下新建文件夹
2. 写一个 `main.py`，里面定义 `def run(task: str, context: dict) -> dict`
3. 在 `core/registry.py` 的 `_BUILTIN_MODULES` 里加一行
4. 跑测试确认注册成功

详细规范见 `对接文件/MODULE_FORMAT_SPEC_v0.1.md`。

## 技术栈

- 核心：Python 标准库（零依赖）
- Web：FastAPI + 原生 HTML/CSS/JS（前后端分离架构）
- 数据库：SQLite（计划中）

## 许可证

MIT License — 详见 [LICENSE](LICENSE)
