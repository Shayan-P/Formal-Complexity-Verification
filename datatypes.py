import dataclasses
from abc import abstractmethod

import cvc5

from expressions import Expr, VariableExpr, ConstantExpr, leq, forall_cvc5, BinOpExpr, Op
from commands import BlockCommand, Command
from typing import List
from cvc5 import Solver, Kind
from functools import reduce
from dataclasses import dataclass

"""
    essentially finding time complexity is finding the fix point of eval_complexity in all BaseFuncs
"""


@dataclass
class BaseFunc:
    name: str
    input_names: List[str]
    body: Command
    T: Expr

    def __init__(self, name: str, input_names, body: Command, T=ConstantExpr(1)):
        self.name = name
        self.body = body
        self.input_names = input_names
        self.T: Expr = None
        self.set_T(T)
        for variable in body.variables():
            if variable not in self.input_names:
                raise Exception(f"used variable {variable} in function {self.name} "
                                f"which is not among the inputs: {self.input_names}")

    def set_T(self, T: Expr):
        # todo how to make sure that initially variables belong to the input?
        self.T = T
        # for variable in T.variables():
        #     if variable not in self.input_names:
        #         raise Exception(f"time complexity of function {self.name} is expressed as {T} "
        #                         f"used variable {variable} which is not among the inputs: {self.input_names}")

    def eval_complexity(self, functions: List["BaseFunc"]) -> Expr:
        """
        param args: inputs to the function
        :return: returns the complexity of the function assuming complexity of all calls are current .T of the functions
        """
        return self.body.eval_complexity(functions)


@dataclass
class Program:
    funcs: List[BaseFunc]

    def __init__(self, funcs: List[BaseFunc]):
        self.funcs = funcs

    def validate_complexities(self) -> bool:
        slv = Solver()
        slv.setOption('produce-models', 'true')

        funcs_T = [func.T for func in self.funcs]
        exp_funcs_T = [func.eval_complexity(self.funcs) for func in self.funcs]
        variables = reduce(lambda a, b: a | b, [func.body.variables() for func in self.funcs], set())
        variables = reduce(lambda a, b: a | b, [exp.variables() for exp in exp_funcs_T], variables)
        intSort = slv.getIntegerSort()
        variables = {name: slv.mkVar(intSort, name) for name in variables}
        constant_cs = []
        # todo this is hacky. remove this later
        for name in list(variables.keys()):
            if name.startswith("c1__"):
                variables[name] = slv.mkConst(intSort, name)
                slv.assertFormula(BinOpExpr(Op("geq"), VariableExpr(name), ConstantExpr(0)).to_cvc5(slv, variables))
                constant_cs.append(variables[name])
            if name.startswith("c0__"):
                variables[name] = slv.mkConst(intSort, name)
                slv.assertFormula(BinOpExpr(Op("geq"), VariableExpr(name), ConstantExpr(1)).to_cvc5(slv, variables))
                constant_cs.append(variables[name])

        for exp_T, T, func in zip(exp_funcs_T, funcs_T, self.funcs):
            expression = leq(exp_T, T)
            # todo this is hacky. how to write this correctly?
            expression = reduce(lambda a, b: BinOpExpr(Op("or"), a, b),
                                [BinOpExpr(Op("leq"), VariableExpr(name), ConstantExpr(0)) for name in
                                 func.input_names],
                                expression)
            formula = forall_cvc5(
                slv, variables,
                quant_var_names=func.input_names,
                expression=expression)
            slv.assertFormula(formula)
            print("asserting formula", formula)

        if slv.checkSat().isSat():
            for c in constant_cs:
                print(c, '=', slv.getValue(c))
            return True
        else:
            return False
