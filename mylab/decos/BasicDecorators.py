import time
from functools import wraps


def timeit(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        print('"timeit decorator is used"')
        start = time.time()
        func(*args,**kwargs)
        stop = time.time()
        print(f'function "{func.__name__}" has runned for {stop-start}s' )
    return wrapper

#可以添加参数'text'的装饰器
def param_timeit(text):
    def timeit(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            start = time.time()
            func(*args,**kwargs)
            stop = time.time()
            print(f'function "{func.__name__}" has runned for {stop-start}s,{text}' )
        return wrapper
    return timeit


@timeit
def example():
    print('this is a test')


if __name__ =='__main__':
    example()

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
