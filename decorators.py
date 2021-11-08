def inc(x):
    return x + 1


def dec(x):
    return x - 1


def operate(func,x):
    result = func(x)
    return result


# print(operate(inc, 3))
# print(operate(dec, 2))


def is_called():
    def is_returned():
        print("Hello")
    return is_returned()


new = is_called
# new()


def upper_decorator(func):
    def inner():
        print("in upper_decorator")
        return func()
    return inner


def second_dec(func):
    def inner2():
        print("Printing some length...")
        return len(func()), func()
    return inner2


@second_dec
@upper_decorator
def say_hi():
    print("in say_hi")
    return "Hello There!"


# print(say_hi())
assert 1 == 1
print("this is not crazy")