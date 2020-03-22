import time
from functools import wraps
from mylab.info import send_wechat
import concurrent.futures

def timeit(func):
    def inner(*args,**kwargs):
        print('"timeit decorator is used"')
        start = time.time()
        result = func(*args,**kwargs)
        stop = time.time()
        print(f'function "{func.__name__}" has runned for {stop-start}s' )
        return result
    return inner


def wechat(func):
    print("%s are dcecorated with wechat notification"%func.__name__)
    def inner(*args,**kwargs):
        result = func(*args,**kwargs)
        send_wechat(func.__name__,"函数%s 执行完成%d"%(func.__name__,time.time()))
        return result
    return inner

#可以添加参数'text'的装饰器
def timeit_param(func,text):
    def inner1(func):
        def inner2(*args,**kwargs):
            start = time.time()
            func(*args,**kwargs)
            stop = time.time()
            print(f'function "{func.__name__}" has runned for {stop-start}s,{text}' )
        return inner2
    return inner1


# @wechat
# @timeit
# def example_func():
#     print('this is a test')


if __name__ =='__main__':
    example_func()

'''
在其他模块上使用，首先将decorator文件夹的位置添加到sys.path 中去
    import sys
    sys.path.append(r'C:/Users/Sabri/OneDrive/Document/python/decorator')
    import BasicDecorators as bd
    @bd.timeit
    def example2():
        print('this is a test')

    example2()
'''
