# screen.py —— 批量初筛：一堆简历按岗位 JD 打分排序（HRBP 秋招提效核心）
#
# 这个脚本把前面学的所有东西串起来：
#   读文件 → 解析每张简历卡片 → 调 AI 按 JD 打分 → 排序 → 输出初筛名单
# 没有 Key 时走演示模式也能看流程；有 Key 时调用真实通义千问。

import os
import glob
from ai_parse import ai_parse   # 复用简历解析（循环 7）
import llm                      # 统一 AI 调用入口

SAMPLES = "Data/samples"
JD_PATH = os.path.join(SAMPLES, "jd_hrbp.txt")


def load_jd():
    with open(JD_PATH, "r", encoding="utf-8") as f:
        return f.read()


def find_resume_files():
    # glob 一次性找到所有 resume*.txt，比如 resume1.txt、resume2.txt
    files = glob.glob(os.path.join(SAMPLES, "resume*.txt"))
    return sorted(files)


def score_resume(resume_text, jd_text):
    """调用 AI 给一份简历打 0-100 分，并返回优势/差距/一句话推荐理由。"""
    system = (
        "你是资深 HRBP，负责校招简历初筛。请对比【候选人简历】与【岗位 JD】，给出综合匹配度评分与简析。\n"
        "【合规要求】评分只能依据学历、专业、实习/项目经历、技能、成果等岗位相关要素，"
        "严禁依据性别、年龄、籍贯、婚育状况、照片、民族等任何受保护特征，否则视为违规。\n"
        "请只输出 JSON："
        '{"score": 0-100的整数, "advantages": ["优势1","优势2"], '
        '"gaps": ["差距1"], "summary": "一句话推荐理由"}'
    )
    user = f"【岗位 JD】\n{jd_text}\n\n【候选人简历】\n{resume_text}"
    try:
        return llm.chat_json(system, user)
    except Exception as e:
        # 万一 AI 返回格式异常，兜底返回，保证整批不中断
        return {"score": 0, "advantages": [], "gaps": ["评估异常"], "summary": f"评估出错：{e}"}


def main():
    jd = load_jd()
    files = find_resume_files()
    mode = "真实 AI 模式" if llm.has_key() else "演示模式"
    print(f"【模式】{mode}")
    print(f"岗位 JD：{JD_PATH}")
    print(f"待初筛简历：{len(files)} 份\n")

    results = []
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        card = ai_parse(text)                       # 先解析成结构化卡片
        name = card.get("姓名", os.path.basename(path))
        sc = score_resume(text, jd)                # 再按 JD 打分
        try:
            score = int(sc.get("score", 0))
        except (ValueError, TypeError):
            score = 0
        results.append({
            "name": name,
            "file": os.path.basename(path),
            "score": score,
            "advantages": sc.get("advantages", []),
            "gaps": sc.get("gaps", []),
            "summary": sc.get("summary", ""),
        })

    # 按分数从高到低排序——HRBP 只需重点看前几名
    results.sort(key=lambda r: r["score"], reverse=True)

    print("===== 初筛排序结果（按匹配度降序）=====")
    for i, r in enumerate(results, 1):
        print(f"\n#{i}  {r['name']}  |  匹配度 {r['score']}/100  |  来源 {r['file']}")
        print(f"    推荐理由：{r['summary']}")
        if r["advantages"]:
            print(f"    优势：{'；'.join(r['advantages'])}")
        if r["gaps"]:
            print(f"    差距：{'；'.join(r['gaps'])}")


if __name__ == "__main__":
    main()
