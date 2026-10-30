# 第二个程序：从简历里找出"姓名"那一行

# 1. 打开文件，按行读取
with open("resume.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

# 2. 一行一行检查，找到包含"姓名"的那一行
for line in lines:
    if "姓名" in line:
        print(line.strip())