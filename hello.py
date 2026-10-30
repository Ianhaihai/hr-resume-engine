# 第一个程序：读取简历文件，打印到屏幕

# 1. 打开文件，"r" 是 read（读取）的意思，utf-8 是中文编码
with open("resume.txt", "r", encoding="utf-8") as f:
    # 2. 把文件全部内容读出来，存到 content 这个变量里
    content = f.read()

# 3. 把内容打印到屏幕上
print(content)
