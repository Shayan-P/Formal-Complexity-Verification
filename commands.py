from abc import ABC, abstractmethod
from typing import Any, Dict, List, FrozenSet, Union
from dataclasses import dataclass
from cvc5 import Kind
from expressions import Expr, IfExpr, add, ConstantExpr
from functools import reduce


class Command(ABC):
    @abstractmethod
    def variables(self):
        pass

    @abstractmethod
    def eval_complexity(self, functions: List["BaseFunc"]):
        pass


@dataclass
class IfCommand(Command):
    condition: Expr
    true: Command
    false: Command

    def variables(self):
        return self.condition.variables() | self.true.variables() | self.false.variables()

    def eval_complexity(self, functions: List["BaseFunc"]):
        return IfExpr(self.condition, self.true.eval_complexity(functions), self.false.eval_complexity(functions))

    def __repr__(self):
        return f"if({self.condition}) then {self.true} else {self.false}"


@dataclass
class FunctionCallCommand(Command):
    func_name: str
    args: List[Expr]

    def variables(self):
        res = set()
        for arg in self.args:
            res |= arg.variables()
        return res

    def eval_complexity(self, functions: List["BaseFunc"]):
        funcs = [func for func in functions if func.name == self.func_name]
        if len(funcs) == 0:
            raise Exception(f"no function named {self.func_name} to call")
        if len(funcs) > 1:
            raise Exception(f"multiple functions named {self.func_name} it is ambiguous")
        func = funcs[0]
        return func.T.substitute_evaluate({
            name: value for name, value in zip(func.input_names, self.args)
        })

    def __repr__(self):
        return f"{self.func_name}({','.join([f'{x}' for x in self.args])})"


@dataclass
class BlockCommand(Command):
    first: Command
    second: Command

    def variables(self):
        return self.first.variables() | self.second.variables()

    def eval_complexity(self, functions: List["BaseFunc"]):
        return add(self.first.eval_complexity(functions), self.second.eval_complexity(functions))

    def __repr__(self):
        return f"{self.first}; {self.second}"


@dataclass
class PassCommand(Command):
    def variables(self):
        return set()

    def eval_complexity(self, functions: List["BaseFunc"]):
        return ConstantExpr(0)

    def __repr__(self):
        return 'pass'


def make_block(commands):
    if len(commands) == 0:
        return PassCommand()
    return reduce(lambda a, b: BlockCommand(a, b), commands)
