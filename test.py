# import sys

# sys.set_int_max_str_digits(100000)


def fib(n: int) -> int:
    a = 0
    b = 1
    for _ in range(0, n):
        prev_a = a
        a = b
        b = prev_a + b
    return a


print(fib(200))
