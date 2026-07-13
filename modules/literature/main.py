"""文献模块 Demo。

真实项目中应在这里接 Crossref、Semantic Scholar、OpenAlex、
本地向量库或机构数据库，而不是把检索逻辑写进 core。
"""


def run(task: str, context: dict) -> dict:
    return {
        "status": "success",
        "summary": "已生成文献检索策略",
        "data": {
            "query_plan": [
                f'核心主题："${task}"'.replace("$", ""),
                "补充机制词、材料词和测试方法词",
                "按综述、奠基论文、近五年研究分层检索",
                "记录 DOI、研究对象、方法、结论和局限",
            ]
        },
        "files": [],
        "logs": ["literature: query plan generated"],
    }
