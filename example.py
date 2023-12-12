from datatypes import Program
from expressions import VariableExpr, mul, add
from parser import parse_code
from utils import fresh_var


def orderify(expr):
    c0 = VariableExpr(fresh_var("c0_"))
    c1 = VariableExpr(fresh_var("c1_"))
    return add(mul(c0, expr), c1)


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

program: Program = parse_code(code_str)

for fun in program.funcs:
    T = fun.T
    fun.set_T(orderify(T))

print(program.validate_complexities())
