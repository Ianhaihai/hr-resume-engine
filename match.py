# match.py —— 岗位匹配诊断（项目核心卖点之二）
# 对比「简历」与「JD」，输出匹配度分数、优势项、差距项、提升建议。
# 这是 HRBP 向业务部门解释「为什么推这个人」的现成材料，也是防歧视设计的落点。

import llm

MODE = "真实 AI 模式" if llm.has_key() else "演示模式（未配置 API Key）"


def match_resume_jd(resume_text, jd_text):
    """调用 AI，对简历与 JD 做匹配诊断。"""
    system = (
        "你是 HRBP 岗位的匹配评估专家。请对比简历与 JD，输出：\n"
        "① 综合匹配度（0-100 分数）；\n"
        "② 优势项；③ 差距项；④ 提升建议。\n"
        "要求：结论可解释、可审计；严禁基于性别、年龄、地域、婚育等受保护特征做判断。"
    )
    user = f"【简历】\n{resume_text}\n\n【JD】\n{jd_text}"
    return llm.chat(system, user)


if __name__ == "__main__":
    try:
        with open("resume.txt", "r", encoding="utf-8") as f:
            resume = f.read()
        with open("Data/samples/jd_hrbp.txt", "r", encoding="utf-8") as f:
            jd = f.read()
        print(f"【模式】{MODE}\n")
        print("===== 匹配诊断报告 =====")
        print(match_resume_jd(resume, jd))
    except RuntimeError as e:
        print(f"调用出错：{e}")
        print("排查建议：检查 LLM_API_KEY 是否正确、阿里云是否已实名认证、qwen-plus 是否还有免费额度。")
