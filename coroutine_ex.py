import asyncio
import inspect
import types

from functools import wraps
from asyncio.futures import Future


def coroutine(func):
    """Simple prototype of coroutine"""
    print(inspect.isgeneratorfunction(func))
    if inspect.isgeneratorfunction(func):
        return types.coroutine(func)

    @wraps(func)
    def coro(*a, **k):
        res = func(*a, **k)
        print(res)
        if isinstance(res, Future) or inspect.isgenerator(res):
            res = yield from res
        return res

    return types.coroutine(coro)


@coroutine
def foo():
    yield from asyncio.sleep(1)
    print("Hello Foo")


loop = asyncio.get_event_loop()
print(loop)
loop.run_until_complete(loop.create_task(foo()))
loop.close()
