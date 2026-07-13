# ============================================================
# 第 2 课：函数（def）
# ============================================================

# --- 概念 1：最简单的函数 ---

def say_hello():
    """打个招呼。def 后面是函数名，括号里是参数（目前空的），冒号后面是函数体"""
    print("你好！我是函数，你调用我，我就执行这行代码。")


# 调用函数 —— 写函数名加括号就运行了
say_hello()
say_hello()  # 可以调用很多次
say_hello()


# --- 概念 2：带参数的函数 ---

def greet(name):
    """参数 name 是调用时传进来的，函数里直接用"""
    print("你好，", name, "！")


greet("小明")    # 输出：你好， 小明 ！
greet("小红")    # 输出：你好， 小红 ！
greet("小刚")    # 每次传不同的参数，输出就不同


# --- 概念 3：带返回值的函数 ---

def add(a, b):
    """return 就是函数的'答案'，外面可以拿到这个答案"""
    result = a + b
    return result


sum1 = add(3, 5)      # sum1 拿到 return 的值：8
sum2 = add(10, 20)    # sum2 拿到 return 的值：30
print("3 + 5 =", sum1)
print("10 + 20 =", sum2)


# --- 概念 4：函数可以返回不同类型的东西 ---

def check_age(age):
    """根据年龄返回不同的文字"""
    if age >= 18:
        return "成年人"
    else:
        return "未成年人"


print("小明 22 岁是：", check_age(22))   # 成年人
print("小红 15 岁是：", check_age(15))   # 未成年人
print("小刚 30 岁是：", check_age(30))   # 成年人


# --- 概念 5：函数 === 你的项目里的 run(task, context) ---
# 这就是你项目里每个模块最核心的东西：

def my_module_run(task, context):
    """
    你的项目里每个模块都有一个叫 run 的函数。
    它接收两个参数：
        task  —— 用户的问题（字符串）
        context —— 额外的信息（字典，后面会讲）
    返回：
        result —— 执行结果（字典）
    """
    # 假装做了一些工作
    print("正在处理任务：", task)
    print("上下文信息：", context)

    # 返回一个结果
    return {
        "status": "success",
        "summary": "处理完成，结果是..." + task[:10] + "...",
    }


# 调用一下试试
result = my_module_run("帮我查一下剪切增稠流体的文献", {"language": "中文"})
print("函数返回的结果：", result)


# --- 概念 6：关键规则 ---
print("")
print("========== 函数的三个铁规则 ==========")
print("规则 1：函数不调用就不执行")
print("   def say_hello(): 写在文件里没用，必须写 say_hello() 才会跑")
print("")
print("规则 2：参数是函数的'输入口'，return 是函数的'输出口'")
print("   def add(a, b):  a 和 b 是输入，return 是输出")
print("")
print("规则 3：return 后面的代码永远不会执行")
print("   比如 def foo():")
print("       return '结束'")
print("       print('这行永远不会打印')  ← 没用")
