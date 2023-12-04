from parser import parse_code

code_str = """
def loop1(n) -> "n":
    if n <= 0:
        pass
    else:
        loop1(n-1)


def loop2(n, m) -> "n * m":
    if n <= 0:
        pass
    else:
        loop2(n-1, m)
        loop1(m)


def loop3(n, m, w) -> "n * m * w":
    if n <= 0:
        pass
    else:
        loop3(n-1, m, w)
        loop2(m, w)
"""

print(parse_code(code_str))
