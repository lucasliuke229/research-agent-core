# ============================================================
# 第 1 课：变量、print、if/else、for 循环
# ============================================================

# --- 概念 1：变量 —— 贴了标签的盒子 ---

name = "小明"          # 字符串 —— 一段文字，用引号包起来
age = 18               # 整数
height = 1.75          # 小数（也叫浮点数）
is_student = True      # 布尔值 —— 只有 True（真）和 False（假）两种

# print() 就是把括号里的东西显示到屏幕上
print("我叫", name)
print("我今年", age, "岁")
print("身高", height, "米")
print("是学生吗？", is_student)

# 变量可以随时改
name = "小红"
print("现在改名叫", name, "了")
print("")


# --- 概念 2：if / elif / else —— 条件判断 ---

score = 85

# Python 靠缩进（空格）来判断哪行代码属于哪个 if
if score >= 90:              # 如果分数 >= 90
    print("优秀")
elif score >= 60:            # 否则如果分数 >= 60
    print("及格")
else:                        # 否则
    print("不及格")
print("")


# --- 概念 3：for 循环 —— 重复做一件事 ---

print("数到 5：")
for i in [1, 2, 3, 4, 5]:    # i 依次变成列表里的每个值
    print("  第", i, "次")

print("")

friends = ["小明", "小红", "小刚"]
for friend in friends:        # friend 依次变成列表里的每个人
    print("你好，", friend)
print("")


# --- 概念 4：列表（list）和字典（dict）---

# 列表：用方括号，按顺序放东西
colors = ["红", "绿", "蓝"]
print("第一个颜色：", colors[0])   # 列表从 0 开始数！
print("第三个颜色：", colors[2])
print("列表长度：", len(colors))    # len() 告诉你列表里有几个东西

print("")

# 字典：用花括号，是"钥匙 → 值"的对应关系
person = {
    "名字": "小明",
    "年龄": 22,
    "城市": "北京"
}
print("这个人叫：", person["名字"])
print("这个人年龄：", person["年龄"])

# 往字典里加东西
person["爱好"] = "编程"
print("整个字典：", person)
print("")


# --- 课后小练习 ---
# 把 x 改名，跑跑看输出有什么变化
x = 10
y = 20
if x > y:
    print("x 比 y 大")
elif x < y:
    print("x 比 y 小")
else:
    print("x 和 y 一样大")
