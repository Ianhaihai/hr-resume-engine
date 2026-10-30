# enrich.py —— 简历丰富（项目核心卖点之一）
# 输入一份简历，AI 按 STAR 法则把单薄经历扩写成有数据、有成果的专业表述。
# 这正是 HRBP「帮候选人 / 员工改简历」这个 B 端高频场景的 AI 化。

import llm

MODE = "真实 AI 模式" if llm.has_key() else "演示模式（未配置 API Key）"


def enrich_resume(resume_text):
    """调用 AI，对简历做 STAR 法则的优化扩写，返回『优化前 / 优化后』对比。"""
    system = (
        "你是资深 HR 顾问。请基于候选人简历，按照 STAR 法则（情境-任务-行动-结果）"
        "把单薄的经历扩写成有数据、有成果的专业表述。要求：\n"
        "① 必须包含量化数据；\n"
        "② 只能基于真实信息合理展开，不得编造虚假经历；\n"
        "③ 输出『优化前 / 优化后』两段对比。"
    )
    return llm.chat(system, resume_text)


if __name__ == "__main__":
    try:
        with open("resume.txt", "r", encoding="utf-8") as f:
            text = f.read()
        print(f"【模式】{MODE}\n")
        print("===== 原始简历 =====")
        print(text)
        print("\n===== AI 简历丰富建议 =====")
        print(enrich_resume(text))
    except RuntimeError as e:
        print(f"调用出错：{e}")
        print("排查建议：检查 LLM_API_KEY 是否正确、阿里云是否已实名认证、qwen-plus 是否还有免费额度。")
