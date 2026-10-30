# 第三个程序：用函数提取简历字段（简历解析器的雏形）

# 定义函数：根据关键词，从简历里找出那一行
def find_field(keyword):
    with open("resume.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        if keyword in line:
            return line.strip()
    return "未找到"

# 调用函数，提取三个字段
print(find_field("姓名"))
print(find_field("学历"))
print(find_field("技能"))
