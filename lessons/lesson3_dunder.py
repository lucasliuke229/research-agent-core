# ============================================================
# 快速补充：__init__ 到底是什么
# ============================================================

# 前后各两个下划线包起来的名字，是 Python 预留的"暗号"
# 英文叫 dunder（double underscore 的缩写）


# ===== __init__：创建对象时自动触发 =====

class Dog:
    def __init__(self, name):
        print(">>> __init__ 被自动调用了！")    # 证明它是自动的
        self.name = name


print("创建第一只狗：")
dog1 = Dog("大黄")    # 你写 Dog(...)，Python 自动触发 __init__
print("")

print("创建第二只狗：")
dog2 = Dog("小白")
# 你不用自己调用 __init__，Python 帮你调了


print("")
print("=" * 50)
print("")


# ===== 其他 __xxx__ 暗号的例子 =====

class Book:
    def __init__(self, title, pages):
        self.title = title
        self.pages = pages

    def __str__(self):
        # print(book对象) 时，Python 自动调用这个，决定打印内容
        return "《" + self.title + "》共 " + str(self.pages) + " 页"

    def __len__(self):
        # len(book对象) 时，Python 自动调用这个
        return self.pages


book = Book("Python入门", 300)

print(book)                # 自动调用 __str__，输出：《Python入门》共 300 页
print("书的页数：", len(book))   # 自动调用 __len__，输出：300


print("")
print("=" * 50)
print("")


# ===== 结论 =====
print("结论：")
print("  __init__ 就是 Python 规定的「初始化暗号」")
print("  你写 Phone(...) 时，Python 自动去找 __init__ 并运行它")
print("  你不需要自己调用 dog.__init__()，Python 帮你做了")
print("")
print("  如果你的函数名叫 init（少了下划线），Python 不认识它，不会自动调用")
print("  所以前后各两个下划线不是装饰，是必须的语法")
