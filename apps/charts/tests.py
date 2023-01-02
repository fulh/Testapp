from django.test import TestCase

# Create your tests here.

# lis = [11, 22, 33, 44, 55]
# list = []
# print(lis)
#
# for num in range(len(lis)-1,-1,-1):
#
# 	if num % 2 != 0:
#
# 		lis.pop(num)
#
# 	else:
#
# 		print(lis)

# a = 234
# ac= a.as_integer_ratio()
# print(ac)
x = {"a", "b", "c"}
y = {"f", "e", "d", "c", "b", "a"}

# z = x.issubset(y)
# h = x.issuperset(y)
# print(z,h)
#
#
# tlp = "I am is {},age {,},is {:.2%}".format("fulihua",18,0.24)
# print(tlp)

x = 123456789.87654321

# 保留两位小数
# r2 = format(x,",")
# print(r2)



# def weihou():
#     name = "chenzhuo"
#     def weiweihou():
#         global name
#         name  = "lengjing"
#     weiweihou()
#     print(name)
# print(name)
# weihou()
# print(name)

# a = list(map(lambda x: len(x) % 2 == 1, ["a", 'b', 'cd', 'efg', 'hig', 'klmn', 'opqr']))
# print(a)
# print(hash("name"))

# fil = open("urls.py")
# fil.readlines()


# f = open("urls.py", 'r+',encoding="utf-8") # 文件句柄
f  = open("urls.py", 'r+',encoding="utf-8")
fw = open("urls.py1", 'w+',encoding="utf-8")
isrede = False
for line in f:
    # line_new = line.strip()
    if line.startswith("#"):
        # fw.write(line)
        print("============")
        print(line,end="")
        isrede = True
        continue
    if isrede:
        # fw.write(line)
        print(line,end="")

    if line.startswith("  "):
        # isrede = False
        break


f.close()
fw.close()

# for letter in 'Python':     # 第一个实例
#    if letter == 'h':
#       print("++++++++")
#       continue
#    print('当前字母 :', letter)


# import random
# print(random.random())
# print(random.randint(1,5))
# print(random.randrange(1,2))
# print(random.sample(["22","33","44"],2))


import json

#
# name_emb = {'a':'1111','b':'2222','c':'3333','d':'4444'}
#
# emb_filename = ('./emb_json.json')
#
# # solution 1
# jsObj = json.dumps(name_emb)
# with open(emb_filename, "w") as f:
#     f.write(jsObj)
#     f.close()
#
# # solution 2
# json.dump(name_emb, open(emb_filename, "w"))

# i  =  8
# json_data = json.dumps(1)
# json_str = json.loads(json_data)
#
# print(type(json_data))
# print(type(json_str))


class A:
    name = "fulihua"
    def __getitem__(self, item):
        print('getitem',item)
        return self.__dict__[item]

    def __setitem__(self, key, value):
        print('setitem')
        self.__dict__[key]=value

    def __delitem__(self, key):
        print('delitem')
        self.__dict__.pop(key)



# class B(A):
#     pass
#
# class C(A):
#     pass
#
# class D(B):
#     pass
#
# class E(C):
#     pass
#
# class F(D,E):
#     pass

# print(F.mro())

new_b=A()
new_b["aaa"] = "fulihua"