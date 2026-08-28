def fib_rec(n: int) -> int:
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fib_rec(n - 1) + fib_rec(n - 2)


print(fib_rec(40))
