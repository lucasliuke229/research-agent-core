# ============================================================
# 第 3 课 重讲：class 到底是什么
# 核心思想：class = 变量 + 函数，捆在一起
# ============================================================

# 先忘掉 class 这个词。
# 我们从一个真实场景出发。


# ===== 第一步：没有 class，我们怎么管两部手机？ =====

# 手机 1 的数据
phone1_brand = "iPhone"
phone1_price = 6999
phone1_battery = 80

# 手机 2 的数据
phone2_brand = "华为"
phone2_price = 4999
phone2_battery = 95

# 操作手机的"函数"（散落在外面）
def show_info(brand, price, battery):
    print("品牌：", brand, "，价格：", price, "，电量：", battery, "%")

def charge(battery):
    battery = battery + 10
    if battery > 100:
        battery = 100
    print("充电完成，电量：", battery, "%")
    return battery

# 使用
print("--- 不用 class，数据和方法是分离的 ---")
show_info(phone1_brand, phone1_price, phone1_battery)
phone1_battery = charge(phone1_battery)

show_info(phone2_brand, phone2_price, phone2_battery)
phone2_battery = charge(phone2_battery)

# 问题：
# 1. 变量散落一地（phone1_brand, phone1_price, phone1_battery... 如果是 10 部手机？）
# 2. 函数和数据没有绑定（charge 函数不知道 phone1_battery 是谁的电池）
# 3. 每次都要手动把变量传来传去


print("")
print("=" * 60)
print("")


# ===== 第二步：用 class 改写 =====

class Phone:
    """
    Phone 类 —— 一部手机的蓝图。
    类定义了两样东西：
        属性（变量）：这部手机有什么数据（品牌、价格、电量）
        方法（函数）：这部手机能做什么操作（展示信息、充电）
    """

    def __init__(self, brand, price, battery):
        """
        这个函数叫初始化，创建手机时自动运行。
        作用：把传进来的数据贴到这部手机上。
        """
        self.brand = brand        # self.brand = 这部手机的品牌
        self.price = price        # self.price = 这部手机的价格
        self.battery = battery    # self.battery = 这部手机的电量

    def show_info(self):
        """
        展示信息。注意：不需要传参数！
        因为数据已经在 self 里了。
        """
        print("品牌：", self.brand, "，价格：", self.price, "，电量：", self.battery, "%")

    def charge(self):
        """
        充电。注意：不需要传参数！
        直接改 self.battery。
        """
        self.battery = self.battery + 10
        if self.battery > 100:
            self.battery = 100
        print("充电完成，电量：", self.battery, "%")


# ===== 第三步：用这个 class 创建手机 =====

print("--- 用 class，数据和方法捆在一起 ---")

# 拆解 phone1 = Phone("iPhone", 6999, 80)  这句话做了什么：
#   1. Python 看到 Phone(...)，知道要用 Phone 这个蓝图造一个实物
#   2. 自动调用 __init__，把 "iPhone" 贴到 self.brand，6999 贴到 self.price...
#   3. 返回这个实物，存到 phone1 变量里

phone1 = Phone("iPhone", 6999, 80)
phone2 = Phone("华为", 4999, 95)

# 现在用 . 来访问
# phone1.brand 就是 "iPhone"
# phone1.battery 就是 80
# phone1.show_info() 就是调用 phone1 的方法

phone1.show_info()       # 展示手机 1 的信息
phone1.charge()          # 手机 1 充电
phone1.charge()          # 再充一次

print("")

phone2.show_info()       # 展示手机 2 的信息
phone2.charge()          # 手机 2 充电

# 注意：phone1.charge() 只影响 phone1 的 battery，
#      phone2 的 battery 完全不受影响！
#      这就是 self 的作用 —— 精确地知道改的是谁的 battery


print("")
print("=" * 60)
print("")


# ===== 最关键的问题：self 到底是什么？ =====

print("--- 理解 self ---")

# 当你写 phone1.show_info() 时，Python 实际做的是：
#   Phone.show_info(phone1)
#   把 phone1 偷偷塞进 self 的位置！

# 证据：下面两种写法效果完全一样
print("写法 1（正常用法）：")
phone1.show_info()

print("写法 2（背后的真相）：")
Phone.show_info(phone1)    # 手动把 phone1 传给 self

# 所以 self 没有魔法，它就是「调用这个方法的那个对象」。
# phone1.show_info() → self = phone1
# phone2.show_info() → self = phone2


print("")
print("=" * 60)
print("")


# ===== 总结：class 就三句话 =====

print("========== class 的三句话 ==========")
print("")
print("第 1 句：class 是蓝图，对象是实物")
print('  class Phone = 手机的「设计图纸」')
print('  phone1 = Phone(...) = 按图纸造出来的「一部真手机」')
print("  一张图纸可以造无数部手机")
print("")
print("第 2 句：self = 哪个对象调用的，self 就是谁")
print("  phone1.show_info() -> self 就是 phone1")
print("  phone2.show_info() -> self 就是 phone2")
print('  所以 self.brand 在 phone1 里是 iPhone，在 phone2 里是华为')
print("")
print("第 3 句：class 里存放两样东西")
print("  属性 = 变量 = 数据（brand, price, battery）")
print("  方法 = 函数 = 操作（show_info, charge）")
print("  它们通过 self 连在一起，就再也不分开了")


print("")
print("=" * 60)
print("")


# ===== 动手练习：你自己写一个 =====

# 照着上面的 Phone 类，写一个 Dog 类：
#   属性：name（名字）, age（年龄）
#   方法：bark()，打印 "xxx 在叫：汪汪！"
#   方法：birthday()，年龄 +1，打印 "xxx 长大了一岁，现在 y 岁"

class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def bark(self):
        print(self.name, "在叫：汪汪！")

    def birthday(self):
        self.age = self.age + 1
        print(self.name, "长大了一岁，现在", self.age, "岁")


print("--- 练习：Dog 类 ---")
dog1 = Dog("大黄", 3)
dog2 = Dog("小白", 1)

dog1.bark()
dog1.birthday()
dog1.birthday()

dog2.bark()
dog2.birthday()

# 试试自己改：
# 1. 再加一个方法 sit()，打印 "xxx 坐下来了"
# 2. 创建第三只狗 dog3，看看行不行
