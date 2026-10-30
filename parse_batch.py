import os

# 把之前的函数升级：多接收一个参数 filename（要解析哪个文件）
def find_field(filename, keyword):
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        if keyword in line:
            return line.strip().replace(keyword + "：", "")
    return "未找到"

# 1. 用 os 工具箱，列出文件夹里所有"简历"文件
all_files = os.listdir(".")
resume_files = []
for f in all_files:
    if f.startswith("resume") and f.endswith(".txt"):
        resume_files.append(f)

# 2. 批量解析：每份简历生成一张卡片，塞进一个大列表
all_cards = []
for filename in resume_files:
    card = {
        "文件": filename,
        "姓名": find_field(filename, "姓名"),
        "学历": find_field(filename, "学历"),
        "技能": find_field(filename, "技能"),
    }
    all_cards.append(card)

# 3. 打印所有卡片
for card in all_cards:
    print(card)
