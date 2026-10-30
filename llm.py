# llm.py —— 项目统一的 AI 调用入口
#
# 设计目标：
#   1. 有 API Key 时，调用真实大模型（阿里云百炼 / 通义千问 OpenAI 兼容模式）
#   2. 没有 Key 时，进入「演示模式」返回示例结果，保证整个流程不崩溃、能看效果
#   3. 出错时给出清晰的中文报错，方便排查（而不是一堆看不懂的英文堆栈）
#
# 配置方式（推荐）：在项目根目录建一个 .env 文件，写一行：
#   LLM_API_KEY=你的sk-key
# 程序会自动读取，key 永远不会写进代码，也不会被传到 GitHub（.gitignore 已挡住）
# 备选方式：终端临时设环境变量 export LLM_API_KEY="你的sk-key"

import os
import json
import requests


def _load_env(path=".env"):
    """读取 .env 文件，把里面的 KEY=值 放进环境变量（已有环境变量时不覆盖）。"""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


_load_env()

# 从环境变量读取配置；没设就用默认值（已按阿里云百炼填好）
API_KEY = os.environ.get("LLM_API_KEY")
BASE_URL = os.environ.get("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
MODEL = os.environ.get("LLM_MODEL", "qwen-plus")


def has_key():
    """是否配置了 API Key。"""
    return bool(API_KEY)


def _headers():
    """构造请求头，Bearer 后面跟的就是你的 Key。"""
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


def _clean_json(text):
    """有些模型会把 JSON 包在 ```json ... ``` 里，去掉外壳再解析。"""
    t = text.strip()
    if t.startswith("```"):
        parts = t.split("```", 2)
        if len(parts) >= 2:
            t = parts[1]
        if t.lower().startswith("json"):
            t = t[4:]
    return t.strip()


def _post(payload):
    """真正发请求给百炼，并做统一的错误处理。"""
    url = f"{BASE_URL}/chat/completions"
    try:
        resp = requests.post(url, headers=_headers(), json=payload, timeout=60)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"网络请求失败：{e}（检查网络或 BASE_URL 是否正确）")
    if resp.status_code != 200:
        raise RuntimeError(f"百炼返回错误 {resp.status_code}：{resp.text}")
    return resp.json()


def chat(system_prompt, user_prompt):
    """普通对话：返回模型生成的纯文本。"""
    if not has_key():
        return _mock(system_prompt, user_prompt)
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    data = _post(payload)
    return data["choices"][0]["message"]["content"]


def chat_json(system_prompt, user_prompt):
    """强制模型返回 JSON，并把结果转成 Python 字典。"""
    if not has_key():
        return json.loads(_mock(system_prompt, user_prompt))
    system_prompt += "\n请只输出 JSON，不要任何多余文字。"
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
    }
    data = _post(payload)
    content = data["choices"][0]["message"]["content"]
    return json.loads(_clean_json(content))


def _mock(system, user):
    """演示模式：没有 Key 时，返回一份示例结果，方便先看流程。
    注意：这是写死的示例，配置了 Key 后会被真实 AI 输出替换。"""
    if "解析" in system or "结构化" in system:
        return json.dumps({
            "姓名": "叶一",
            "求职意向": "人力资源 HRBP（实习）",
            "学历": "某大学 人力资源管理 本科 2027届",
            "实习经历": "某互联网公司 HR 实习生，深度参与秋季校招，累计筛选技术类简历 500+ 份并协助安排面试 60+ 场。",
            "技能": "精通 Excel、熟练使用飞书、普通话一级乙等",
        }, ensure_ascii=False)
    if "丰富" in system or "扩写" in system or "STAR" in system:
        return ("【简历丰富建议（演示示例）】\n"
                "原经历：在一家公司做过招聘助理，帮忙收简历、安排面试。\n"
                "优化后：作为招聘助理支持秋季校招，独立处理 300+ 份简历初筛，"
                "协调 20+ 场面试排期，到面准时率达 95%，并用 Excel 搭建候选人跟踪表，"
                "使团队协同效率提升约 30%。")
    # 需要 JSON 的评分请求（chat_json 调用，system 里含 "JSON" 或 "score"）：
    # 必须放在「匹配/诊断」纯文本分支之前，否则会被提前拦截返回非 JSON 导致解析失败
    if "JSON" in system or "score" in system:
        return json.dumps({
            "score": 85,
            "advantages": ["人力资源相关本科对口", "有校招实习经历", "Excel/飞书技能达标"],
            "gaps": ["缺少薪酬/员工关系项目经历"],
            "summary": "综合匹配度高，建议补充员工关系相关项目后优先约面。",
        }, ensure_ascii=False)
    if "匹配" in system or "诊断" in system:
        return ("【匹配诊断（演示示例）】\n"
                "综合匹配度：78 / 100\n"
                "优势：人力资源相关本科对口、有校招实习经历、Excel/飞书技能达标。\n"
                "差距：缺少薪酬 / 员工关系项目经历（JD 中的加分项）。\n"
                "建议：补充一个员工关系或薪酬相关的课程 / 项目，匹配度可提升至 88。")
    return "（演示模式）未识别到的指令类型，配置 API Key 后可得真实 AI 输出。"
