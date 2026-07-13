# 科研 Agent 模块格式规范 v0.1

本规范用于统一各功能模块的目录、入口函数、输入参数和返回结果。

模块开发者只需要遵守本文档，不需要了解 Core 内部实现。

---

## 1. 模块目录格式

每个模块放在 `modules/` 下，目录名使用英文小写和下划线。

例如：

```text
modules/
├── theory/
│   ├── __init__.py
│   ├── main.py
│   ├── service.py
│   └── README.md
│
├── computation/
│   ├── __init__.py
│   ├── main.py
│   ├── service.py
│   └── README.md
│
└── experiment/
    ├── __init__.py
    ├── main.py
    ├── service.py
    └── README.md
```

最低要求：

```text
modules/<模块名>/
├── __init__.py
└── main.py
```

推荐增加：

```text
service.py
README.md
```

说明：

- `main.py`：Core 调用入口，格式必须统一；
- `service.py`：模块自己的真实功能；
- `README.md`：说明模块输入、输出和依赖；
- 其他文件可由模块开发者自由增加。

---

## 2. 唯一对外入口

每个模块的 `main.py` 中必须存在：

```python
def run(task: str, context: dict) -> dict:
    ...
```

Core 只调用这个函数。

不能自行改成：

```python
execute(...)
start(...)
invoke(...)
process(...)
```

也不能增加必须的位置参数，例如：

```python
def run(task, context, model, output_dir):
    ...
```

额外参数统一从 `context` 中读取。

---

## 3. 输入参数

### 3.1 task

类型：

```python
str
```

含义：用户提交的任务描述。

示例：

```python
task = "分析剪切增稠流体在冲击载荷下的阻塞机制"
```

### 3.2 context

类型：

```python
dict
```

含义：模块运行时需要的附加参数。

示例：

```python
context = {
    "language": "zh-CN",
    "input_file": "data/test.csv",
    "output_dir": "outputs/computation",
}
```

读取可选参数时必须使用：

```python
language = context.get("language", "zh-CN")
```

不要直接假设字段一定存在：

```python
language = context["language"]
```

除非该字段已经在本模块的 `README.md` 中明确标记为必填。

模块不要修改传入的 `context`。

---

## 4. 标准返回格式

所有模块统一返回：

```python
{
    "status": "success",
    "summary": "模块执行结果摘要",
    "data": {},
    "files": [],
    "logs": [],
    "error": None,
}
```

字段要求：

| 字段 | 类型 | 含义 |
|---|---|---|
| `status` | `str` | 模块执行状态 |
| `summary` | `str` | 给用户看的简短结果 |
| `data` | `dict` | 给 Core 或后续模块使用的结构化结果 |
| `files` | `list[str]` | 模块生成的文件路径 |
| `logs` | `list[str]` | 模块运行日志 |
| `error` | `str \| None` | 错误信息 |

合法状态只能使用：

```text
success
failed
partial
```

不要使用：

```text
ok
done
finish
completed
error
```

---

## 5. 成功返回示例

```python
return {
    "status": "success",
    "summary": "理论分析完成",
    "data": {
        "hypotheses": [
            "冲击速度影响阻塞前沿传播速度",
            "固相体积分数影响临界状态",
        ],
        "variables": [
            "impact_velocity",
            "solid_fraction",
        ],
    },
    "files": [],
    "logs": [
        "theory analysis started",
        "theory analysis completed",
    ],
    "error": None,
}
```

---

## 6. 失败返回示例

```python
return {
    "status": "failed",
    "summary": "缺少输入文件",
    "data": {},
    "files": [],
    "logs": [
        "input file is missing",
    ],
    "error": "context.input_file is required",
}
```

---

## 7. main.py 推荐写法

```python
from __future__ import annotations

from typing import Any

from .service import execute_module


def run(task: str, context: dict[str, Any]) -> dict[str, Any]:
    """Core 调用本模块的唯一入口。"""

    try:
        result = execute_module(
            task=task,
            context=context,
        )

        return {
            "status": "success",
            "summary": result["summary"],
            "data": result.get("data", {}),
            "files": result.get("files", []),
            "logs": result.get("logs", []),
            "error": None,
        }

    except Exception as exc:
        return {
            "status": "failed",
            "summary": "模块执行失败",
            "data": {},
            "files": [],
            "logs": [
                "module execution failed",
            ],
            "error": f"{type(exc).__name__}: {exc}",
        }
```

---

## 8. service.py 推荐写法

```python
from __future__ import annotations

from typing import Any


def execute_module(
    task: str,
    context: dict[str, Any],
) -> dict[str, Any]:
    """模块自己的真实业务逻辑。"""

    language = context.get("language", "zh-CN")

    # 在这里实现本模块的真实功能。
    # 可以调用大模型、数据库、Python、Matlab 或其他工具。

    return {
        "summary": "模块真实功能执行完成",
        "data": {
            "task": task,
            "language": language,
        },
        "files": [],
        "logs": [
            "business logic completed",
        ],
    }
```

`service.py` 的内部格式不受 Core 限制。

模块开发者可以自由改动内部实现，只要 `main.py` 的 `run()` 接口不变。

---

## 9. data 字段规范

`data` 用于保存结构化结果。

正确：

```python
"data": {
    "variables": ["velocity", "pressure"],
    "equations": ["p = F / A"],
    "parameters": {
        "density": 1000,
        "temperature": 298,
    },
}
```

不推荐：

```python
"data": "分析完成"
```

`data` 必须是字典。

建议只放可以转换成 JSON 的数据：

```text
字符串
数字
布尔值
列表
字典
None
```

不要直接放：

```text
数据库连接
文件对象
线程
模型客户端
Matlab Engine
复杂 Python 类实例
```

---

## 10. files 字段规范

模块生成的文件统一放到：

```text
outputs/<模块名>/
```

例如：

```text
outputs/theory/result.json
outputs/computation/simulation.py
outputs/experiment/protocol.md
```

返回格式：

```python
"files": [
    "outputs/experiment/protocol.md",
]
```

错误格式：

```python
"files": "outputs/experiment/protocol.md"
```

只有文件真实生成后，才能写入 `files`。

---

## 11. logs 字段规范

日志必须是字符串列表：

```python
"logs": [
    "input loaded",
    "analysis completed",
    "result saved",
]
```

日志中不要写：

```text
API Key
密码
Token
个人隐私
数据库账号
```

---

## 12. 前序模块结果

当多个模块按顺序运行时，Core 可能在 `context` 中加入：

```python
context["previous_results"]
```

读取方式：

```python
previous_results = context.get(
    "previous_results",
    [],
)
```

查找指定模块：

```python
def find_previous_result(
    context: dict,
    module_name: str,
) -> dict | None:
    results = context.get("previous_results", [])

    for result in reversed(results):
        if result.get("module") == module_name:
            return result

    return None
```

模块必须能够在没有 `previous_results` 时独立运行。

模块之间不要直接相互调用。

禁止：

```python
from modules.theory.main import run
```

模块协作统一通过 Core 传入的 `context` 完成。

---

## 13. 每个模块的 README.md

每个模块建议写一个简短的 `README.md`。

格式：

```markdown
# 模块名称

## 模块注册名

theory

## 功能

说明模块主要完成什么任务。

## 必填 context 字段

无

## 可选 context 字段

- language: 输出语言
- input_file: 输入文件路径

## data 输出字段

- hypotheses: 假设列表
- variables: 变量列表

## 生成文件

- outputs/theory/result.json

## 外部依赖

- openai
- pandas

## 运行说明

说明模块如何单独测试。
```

---

## 14. 模块完成后的检查清单

模块开发者提交给 Core 负责人前，确认：

- [ ] 模块目录名称为英文小写
- [ ] 存在 `__init__.py`
- [ ] 存在 `main.py`
- [ ] 存在 `run(task, context)`
- [ ] 返回值是字典
- [ ] 包含 `status`
- [ ] 包含 `summary`
- [ ] 包含 `data`
- [ ] 包含 `files`
- [ ] 包含 `logs`
- [ ] 包含 `error`
- [ ] `data` 是字典
- [ ] `files` 是字符串列表
- [ ] `logs` 是字符串列表
- [ ] 状态只使用 `success`、`failed`、`partial`
- [ ] 模块不会调用 `exit()` 或 `quit()`
- [ ] 模块不直接调用其他模块
- [ ] 模块可以单独运行
- [ ] 已写清楚需要的 `context` 字段
- [ ] 已写清楚输出的 `data` 字段

---

## 15. 最小边界总结

模块开发者只需要记住：

```text
固定入口：
modules/<模块名>/main.py

固定函数：
run(task, context)

固定返回：
status
summary
data
files
logs
error
```

模块内部如何实现，由各模块开发者自行决定。
