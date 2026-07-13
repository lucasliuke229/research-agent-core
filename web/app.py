# DEPRECATED: 这是旧版 Streamlit 前端，已被 web/server.py + web/index.html 替代。
# 此文件保留仅作参考，不再维护。运行 Web 界面请用：python web/server.py

"""最小 Streamlit 前端（已废弃）。

运行：
    pip install streamlit
    streamlit run web/app.py
"""

import streamlit as st

from core import run_task

st.set_page_config(page_title="Research Agent", layout="wide")
st.title("Research Agent Core Demo")

task = st.text_area("请输入科研任务")
task_type = st.selectbox(
    "任务类型",
    ["theory", "computation", "experiment", "literature", "full"],
)

if st.button("运行", type="primary"):
    if not task.strip():
        st.warning("请输入任务")
    else:
        result = run_task(
            task,
            task_type,
            context={"domain": "mechanics"},
        )

        st.metric("状态", result["status"])
        st.subheader("摘要")
        st.text(result["summary"])

        if result["error"]:
            st.error(result["error"])

        st.subheader("结构化结果")
        st.json(result["results"])

        st.subheader("日志")
        st.code("\n".join(result["logs"]))
