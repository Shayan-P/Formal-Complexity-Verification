from datatypes import Program, BaseFunc
from expressions import ConstantExpr, VariableExpr, add, mul, sub, leq
from commands import FunctionCallCommand, BlockCommand, IfCommand, PassCommand
from utils import fresh_var


def orderify(expr):
    c0 = VariableExpr(fresh_var("c0_"))
    c1 = VariableExpr(fresh_var("c1_"))
    return add(mul(c0, expr), c1)


single_loop_func = BaseFunc(
    name="loop1",
    input_names=["n"],
    T=orderify(VariableExpr("n")),
    body=IfCommand(
        condition=leq(VariableExpr("n"), ConstantExpr(0)),
        true=PassCommand(),
        false=FunctionCallCommand(func_name="loop1", args=[sub(VariableExpr("n"), ConstantExpr(1))])
    )
)

double_loop_func = BaseFunc(
    name="loop2",
    input_names=["n", "m"],
    T=orderify(mul(VariableExpr("n"), VariableExpr("m"))),
    body=IfCommand(
        condition=leq(VariableExpr("n"), ConstantExpr(0)),
        true=PassCommand(),
        false=BlockCommand(
           FunctionCallCommand(func_name="loop2",
                               args=[sub(VariableExpr("n"), ConstantExpr(1)), VariableExpr("m")]),
           FunctionCallCommand(func_name="loop1", args=[VariableExpr("m")])
        )
    )
)

triple_loop_func = BaseFunc(
    name="loop3",
    input_names=["n", "m", "w"],
    T=orderify(mul(mul(VariableExpr("n"), VariableExpr("m")), VariableExpr("w"))),
    body=IfCommand(
        condition=leq(VariableExpr("n"), ConstantExpr(0)),
        true=PassCommand(),
        false=BlockCommand(
           FunctionCallCommand(func_name="loop3",
                               args=[sub(VariableExpr("n"), ConstantExpr(1)), VariableExpr("m"), VariableExpr("w")]),
           FunctionCallCommand(func_name="loop2", args=[VariableExpr("m"), VariableExpr("w")])
        )
    )
)

program = Program(funcs=[
    single_loop_func, double_loop_func, triple_loop_func
])

print(program.validate_complexities())
