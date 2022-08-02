from faker import Faker
# （1）数据的唯一性【生成多个数据，保证数据不重复】
# fk = Faker("zh-CN")
# result = [fk.unique.boolean() for i in range(10090)]
# print(f"列表总数{len(result)},去重后总数{len(set(result))}")
# result的结果是生成10个不同的名字，存在一个列表中['聂玉梅', '崔旭', '高桂珍', '张桂花', '颜建平', '黄辉', '梁柳', '宋红梅', '张平', '卜建军']
# （2）数据共享【通过Faker.seed(234)实现】



class TestDemo:
    def __init__(self):
        self.fk = Faker(locale="zh-CN").unique


    def create_data(self):
        # Faker.seed(234)
        # phones = self.fk.name()
        phones = [[self.fk.phone_number(),self.fk.name(),self.fk.ssn(),self.fk.address(),self.fk.job(),self.fk.text(),False ] for _ in range(5)]
        for i in range(5):
            print(self.fk.phone_number())
            # print(self.fk.profile(fields=None, sex=None))
        print(phones)


    def updata_data(self):
        # Faker.seed(234)
        print(self.fk.name())


if __name__ == '__main__':
    cl = TestDemo()
    cl.create_data()
    cl.updata_data()
