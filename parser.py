import ast

from cvc5 import Kind

from datatypes import Program, BaseFunc
from expressions import IfExpr, BinOpExpr, Expr, Op, VariableExpr, ConstantExpr
from commands import IfCommand, make_block, FunctionCallCommand, PassCommand


def parse_code(code_string):
    ast_module = ast.parse(code_string)
    if not isinstance(ast_module, ast.Module):
        raise Exception("expected the code string to parse into module")
    return parse_ast(ast_module)


def parse_ast(node):
    if isinstance(node, ast.Module):
        funcs = []
        for child in node.body:
            if not isinstance(child, ast.FunctionDef):
                raise Exception("expected the code consist of the definition of some functions")
            funcs.append(parse_ast(child))
        return Program(funcs)

    elif isinstance(node, ast.FunctionDef):
        return BaseFunc(
            name=node.name,
            input_names=parse_ast(node.args),
            body=make_block(parse_ast(node.body))
        )

    elif isinstance(node, ast.If):
        return IfCommand(
            condition=parse_ast(node.test),
            true=make_block(parse_ast(node.body)),
            false=make_block(parse_ast(node.orelse))
        )

    elif isinstance(node, ast.Call):
        name = node.func.id
        args = parse_ast(node.args)
        for arg in args:
            if not isinstance(arg, Expr):
                raise Exception(f"calling {name} with {arg} is invalid. It should be expression")
        return FunctionCallCommand(
            func_name=name,
            args=args
        )

    elif isinstance(node, ast.Expr):
        return parse_ast(node.value)

    elif isinstance(node, ast.Pass):
        return PassCommand()

    elif isinstance(node, ast.Compare):
        if len(node.ops) > 1:
            raise Exception("currently only one comparison is supported")
        op = op_to_kind_name(node.ops[0].__class__.__name__.upper())
        left = check_expr(parse_ast(node.left))
        right = check_expr(parse_ast(node.comparators[0]))
        return BinOpExpr(Op(op), left, right)

    elif isinstance(node, ast.BinOp):
        op = op_to_kind_name(node.op.__class__.__name__.upper())
        left = check_expr(parse_ast(node.left))
        right = check_expr(parse_ast(node.right))
        return BinOpExpr(Op(op), left, right)

    elif isinstance(node, ast.Name):
        return VariableExpr(node.id)

    elif isinstance(node, ast.Num):
        val: int|bool = node.value
        if (type(val) is not bool) and (type(val) is not int):
            raise Exception(f"value {val} is not acceptable. should be int or bool")
        return ConstantExpr(val)

    elif isinstance(node, ast.arguments):
        return [parse_ast(arg) for arg in node.args]

    elif isinstance(node, ast.arg):
        return node.arg

    elif isinstance(node, list):
        return [parse_ast(item) for item in node]

    raise Exception(f"{type(node)} not supported")


def check_expr(expr):
    if not isinstance(expr, Expr):
        raise Exception(f"{expr} is not an expression")
    return expr


def op_to_kind_name(op):
    op = op.upper()
    if op == "LTE":
        return "LEQ"
    if op == "GTE":
        return "GEQ"
    if op == "MOD":
        return "INTS_MODULUS"
    if not hasattr(Kind, op):
        raise Exception(f"operation {op} not found")
    return op
