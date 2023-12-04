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

    def __repr__(self):
        return f"{self.name}"


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

    def __repr__(self):
        return f"{self.value}"


@dataclass
class Op:
    name: str

    def cvc5_kind(self):
        return getattr(Kind, self.name.upper())

    def __repr__(self):
        return f"{self.name.upper()}"


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

    def __repr__(self):
        return f"({self.op} {self.operand})"


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

    def __repr__(self):
        if self.op.cvc5_kind() == Kind.ADD:
            return f"({self.left}+{self.right})"
        if self.op.cvc5_kind() == Kind.SUB:
            return f"({self.left}-{self.right})"
        if self.op.cvc5_kind() == Kind.MULT:
            return f"({self.left}*{self.right})"
        if self.op.cvc5_kind() == Kind.INTS_MODULUS:
            return f"({self.left}%{self.right})"
        if self.op.cvc5_kind() == Kind.LEQ:
            return f"({self.left}<={self.right})"
        if self.op.cvc5_kind() == Kind.LT:
            return f"({self.left}<{self.right})"
        if self.op.cvc5_kind() == Kind.GEQ:
            return f"({self.left}>={self.right})"
        if self.op.cvc5_kind() == Kind.GT:
            return f"({self.left}>{self.right})"
        if self.op.cvc5_kind() == Kind.EQUAL:
            return f"({self.left}=={self.right})"
        return f"({self.op} {self.left} {self.right})"


@dataclass
class IfExpr(Expr):
    condition: Expr
    true: Expr
    false: Expr

    def to_cvc5(self, slv, variables):
        return slv.mkTerm(Kind.ITE,
                          self.condition.to_cvc5(slv, variables),
                          self.true.to_cvc5(slv, variables),
                          self.false.to_cvc5(slv, variables))

    def variables(self):
        return self.condition.variables() | self.true.variables() | self.false.variables()

    def substitute_evaluate(self, subs: Dict[str, "Expr"]) -> "Expr":
        return IfExpr(self.condition.substitute_evaluate(subs),
                      self.true.substitute_evaluate(subs),
                      self.false.substitute_evaluate(subs))

    def __repr__(self):
        return f"(if {self.condition} then {self.true} else {self.false})"


def add(a, b):
    return BinOpExpr(Op("add"), a, b)


def mul(a, b):
    return BinOpExpr(Op("mult"), a, b)


def sub(a, b):
    return BinOpExpr(Op("sub"), a, b)


def leq(a, b):
    return BinOpExpr(Op("leq"), a, b)


def forall_cvc5(slv, variables, quant_var_names, expression: Expr):
    quant_var_list = slv.mkTerm(Kind.VARIABLE_LIST,
                                *[variables[name] for name in quant_var_names])
    return slv.mkTerm(Kind.FORALL,
                      quant_var_list,
                      expression.to_cvc5(slv, variables))
