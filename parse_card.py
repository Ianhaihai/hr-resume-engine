# 第四个程序：把简历解析成一张"结构化档案卡"

# 复用字段提取函数，但这次只返回"值"（去掉"关键词："前缀）
def find_field(keyword):
    with open("resume.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        if keyword in line:
            # .replace(旧, 新) 把"关键词："替换成空，只留下内容
            return line.strip().replace(keyword + "：", "")
    return "未找到"

# 用字典（dict）把多个字段组织成一张"档案卡"
resume_card = {
    "姓名": find_field("姓名"),
    "学历": find_field("学历"),
    "技能": find_field("技能"),
    "求职意向": find_field("求职意向"),
    "实习经历": find_field("实习经历"),
}

for key, value in resume_card.items():
    print(f"{key}：{value}")

# 打印整张卡片
# print(resume_card)