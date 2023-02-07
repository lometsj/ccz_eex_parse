import struct


def u32(data):
    return struct.unpack("<I", data)[0]


def u16(data):
    return struct.unpack("<H", data)[0]


def u8(data):
    return struct.unpack("<B", data)[0]


def p32(data):
    return struct.pack("<I", data)


def p16(data):
    return struct.pack("<H", data)


def p8(data):
    return struct.pack("<B", data)

import json


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        """
        判断是否为bytes类型的数据是的话转换成str
        :param obj:
        :return:
        """
        if isinstance(obj, bytes):
            obj = obj.replace(b'\xa1\x40',b' ')
            return obj.decode('gbk', errors='backslashreplace')
        if isinstance(obj, set):
            print(obj)
            print(type(obj))
            return None
        return json.JSONEncoder.default(self, obj)

def json_format(data):
    return json.dumps(data, sort_keys=True, indent=4, separators=(',', ':'), cls=MyEncoder, ensure_ascii=False)

class Stack(object):
    # 初始化栈为空列表
    def __init__(self):
        self.items = []

    # 判断栈是否为空，返回布尔值
    def is_empty(self):
        return self.items == []

    # 返回栈顶元素
    def peek(self):
        return self.items[len(self.items) - 1]

    # 返回栈的大小
    def size(self):
        return len(self.items)

    # 把新的元素堆进栈里面（程序员喜欢把这个过程叫做压栈，入栈，进栈……）
    def push(self, item):
        self.items.append(item)

    # 把栈顶元素丢出去（程序员喜欢把这个过程叫做出栈……）
    def pop(self):
        return self.items.pop()
