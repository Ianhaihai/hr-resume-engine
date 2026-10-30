# app.py —— 简历工作台网页界面（Streamlit）
#
# 这是把项目从「demo」变成「工具」的关键入口：
#   1. 左侧贴岗位 JD（或直接上传 JD 文件），支持切换多个岗位
#   2. 右侧批量上传 PDF / TXT 简历
#   3. 点一下，AI 自动解析 + 按匹配度排序，输出初筛名单
#
# 运行方式（终端里，项目根目录）：
#   streamlit run app.py
#
# 依赖：pip install streamlit pymupdf

import io
import csv
import streamlit as st

import llm                 # 统一 AI 调用入口（真实/演示模式自动切换）
from pdf_utils import extract_text
from ai_parse import ai_parse
from screen import score_resume


st.set_page_config(page_title="AI 简历初筛工作台", page_icon="📋", layout="wide")

# 顶部：模式提示（有 key 走真实通义千问，没有走演示模式）
mode = "真实 AI 模式（通义千问）" if llm.has_key() else "演示模式（未配置 API Key，先看流程）"
st.title("📋 AI 简历初筛工作台")
st.caption(f"当前模式：**{mode}** ｜ 解析 / 匹配 / 排序全部由 AI 完成")


# ---------- 侧边栏：岗位 JD ----------
st.sidebar.header("① 设置岗位 JD")
jd_text = st.sidebar.text_area(
    "粘贴岗位描述（JD）",
    height=220,
    placeholder="例如：HRBP 实习生，要求人力资源/心理学相关本科，有校招或招聘实习经验优先……",
)

jd_files = st.sidebar.file_uploader(
    "或上传 JD 文件（.txt，可多个岗位）",
    type=["txt"],
    accept_multiple_files=True,
)

# 把「手动输入」和「上传的 JD 文件」汇总成一个可选列表
jd_sources = [("✍️ 手动输入", jd_text)]
for f in (jd_files or []):
    try:
        jd_sources.append((f.name, f.read().decode("utf-8", "ignore")))
    except Exception:
        pass

if len(jd_sources) > 1:
    choice = st.sidebar.selectbox("选择当前匹配的岗位", [n for n, _ in jd_sources])
    active_jd = dict(jd_sources)[choice]
else:
    active_jd = jd_text


# ---------- 主区：上传简历 ----------
st.header("② 上传简历（PDF / TXT，可多选）")
resume_files = st.file_uploader(
    "拖入或点击上传",
    type=["pdf", "txt"],
    accept_multiple_files=True,
)

start = st.button("🚀 开始匹配初筛", type="primary", disabled=not active_jd.strip())


# ---------- 执行匹配 ----------
if start and resume_files:
    with st.spinner("AI 正在解析并匹配简历……"):
        results = []
        for f in resume_files:
            text = extract_text(f.name, f.read())
            if text.startswith("[PDF 解析失败") or text.startswith("[PDF 未提取"):
                st.warning(f"{f.name}：{text}")
                continue
            name = ai_parse(text).get("姓名", f.name)   # 解析不到姓名就用文件名
            sc = score_resume(text, active_jd)
            try:
                score = int(sc.get("score", 0))
            except (ValueError, TypeError):
                score = 0
            results.append({
                "姓名": name,
                "来源文件": f.name,
                "匹配度": score,
                "推荐理由": sc.get("summary", ""),
                "优势": "；".join(sc.get("advantages", [])),
                "差距": "；".join(sc.get("gaps", [])),
            })

    if not results:
        st.error("没有可用的简历，请检查上传的文件。")
    else:
        results.sort(key=lambda r: r["匹配度"], reverse=True)

        st.success(f"初筛完成：共 {len(results)} 份，已按匹配度降序排列")
        st.dataframe(
            [{"排名": i + 1, **r} for i, r in enumerate(results)],
            use_container_width=True,
            hide_index=True,
        )

        # 明细展开
        for i, r in enumerate(results, 1):
            with st.expander(f"#{i}  {r['姓名']}  ·  匹配度 {r['匹配度']}/100"):
                st.write(f"**推荐理由**：{r['推荐理由']}")
                if r["优势"]:
                    st.write(f"**优势**：{r['优势']}")
                if r["差距"]:
                    st.write(f"**差距**：{r['差距']}")

        # 导出 CSV
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["姓名", "来源文件", "匹配度", "推荐理由", "优势", "差距"])
        writer.writeheader()
        writer.writerows(results)
        st.download_button(
            "⬇️ 导出初筛结果 CSV",
            data=buf.getvalue().encode("utf-8-sig"),
            file_name="初筛结果.csv",
            mime="text/csv",
        )

elif start and not resume_files:
    st.warning("请先上传至少一份简历。")
elif not active_jd.strip():
    st.info("请先在左侧设置岗位 JD，再上传简历开始匹配。")
