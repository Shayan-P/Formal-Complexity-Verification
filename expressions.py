from abc import ABC, abstractmethod
from typing import Any, Dict, List, FrozenSet, Union
from dataclasses import dataclass
from cvc5 import Kind


class Expr(ABC):
    @abstractmethod
    def to_cvc5(self, slv, variables):
        pass

    @abstractmethod
    def variables(self):
        pass

    @abstractmethod
    def substitute_evaluate(self, subs: Dict[str, "Expr"]) -> "Expr":
        pass


@dataclass
class VariableExpr(Expr):
    name: str

    def to_cvc5(self, slv, variables):
        return variables[self.name]

    def variables(self):
        return {self.name}

    def substitute_evaluate(self, subs: Dict[str, "Expr"]) -> "Expr":
        return subs.get(self.name, self)


@dataclass
class ConstantExpr(Expr):
    value: Union[int, bool]

    def to_cvc5(self, slv, variables):
        if type(self.value) is int:
            return slv.mkInteger(self.value)
        else:
            return slv.mkBoolean(self.value)

    def variables(self):
        return set()

    def substitute_evaluate(self, subs: Dict[str, "Expr"]) -> "Expr":
        return self


@dataclass
class Op:
    name: str

    def cvc5_kind(self):
        return getattr(Kind, self.name.upper())


@dataclass
class UnOpExpr(Expr):
    op: Op
    operand: Expr

    def to_cvc5(self, slv, variables):
        return slv.mkTerm(self.op.cvc5_kind(),
                          self.operand.to_cvc5(slv, variables))

    def variables(self):
        return self.operand.variables()

    def substitute_evaluate(self, subs: Dict[str, "Expr"]) -> "Expr":
        return UnOpExpr(self.op, self.operand.substitute_evaluate(subs))


@dataclass
class BinOpExpr(Expr):
    op: Op
    left: Expr
    right: Expr

    def to_cvc5(self, slv, variables):
        return slv.mkTerm(self.op.cvc5_kind(),
                          self.left.to_cvc5(slv, variables),
                          self.right.to_cvc5(slv, variables))

    def variables(self):
        return self.left.variables() | self.right.variables()

    def substitute_evaluate(self, subs: Dict[str, "Expr"]) -> "Expr":
        return BinOpExpr(self.op,
                         self.left.substitute_evaluate(subs),
                         self.right.substitute_evaluate(subs))


def ite(condition, true_exp, false_exp):
    return BinOpExpr(
        Op("or"),
        BinOpExpr(Op("and"), condition, true_exp),
        BinOpExpr(Op("and"), UnOpExpr(Op("not"), condition), false_exp)
    )


def add(a, b):
    return BinOpExpr(Op("add"), a, b)


def mul(a, b):
    return BinOpExpr(Op("mult"), a, b)


def sub(a, b):
    return BinOpExpr(Op("sub"), a, b)


def leq(a, b):
    return BinOpExpr(Op("leq"), a, b)
