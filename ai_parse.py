# ai_parse.py —— 简历解析（把一份简历文本变成结构化字典）
# 这是 Loop 7 的功能，现在统一走 llm.py 调用 AI。

import llm

MODE = "真实 AI 模式" if llm.has_key() else "演示模式（未配置 API Key）"


def ai_parse(resume_text):
    """调用 AI，把简历文本解析成结构化字典。"""
    system = (
        "你是一个简历解析助手。请把简历文本解析成 JSON，"
        "字段包括：姓名、求职意向、学历、实习经历、技能。"
    )
    return llm.chat_json(system, resume_text)


if __name__ == "__main__":
    try:
        with open("resume.txt", "r", encoding="utf-8") as f:
            text = f.read()
        print(f"【模式】{MODE}")
        card = ai_parse(text)
        print("【解析结果】")
        print(card)
    except RuntimeError as e:
        print(f"调用出错：{e}")
        print("排查建议：检查 LLM_API_KEY 是否正确、阿里云是否已实名认证、qwen-plus 是否还有免费额度。")
