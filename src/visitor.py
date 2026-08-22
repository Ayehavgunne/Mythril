import re
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any

import grammar
import my_ast

type Scope = dict[str, AccessibleSymbol]


def to_snake(s: str) -> str:
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    s = s.lower()
    return s


class VisitorException(Exception):
    pass


@dataclass(kw_only=True)
class Symbol:
    name: str
    type: Symbol | None = None


@dataclass(kw_only=True)
class BuiltinTypeSymbol(Symbol):
    pass


ANY_BUILTIN = BuiltinTypeSymbol(name=grammar.ANY)
INT_BUILTIN = BuiltinTypeSymbol(name=grammar.INT, type="Int")
# INT8_BUILTIN = BuiltinTypeSymbol(name=grammar.INT8, type="Int8")
# INT32_BUILTIN = BuiltinTypeSymbol(name=grammar.INT32, type="Int32")
# INT128_BUILTIN = BuiltinTypeSymbol(name=grammar.INT128, type="Int128")
DEC_BUILTIN = BuiltinTypeSymbol(name=grammar.DEC, type="Dec")
FLOAT_BUILTIN = BuiltinTypeSymbol(name=grammar.FLOAT, type="Float")
# COMPLEX_BUILTIN = BuiltinTypeSymbol(name=grammar.COMPLEX, type="Complex")
BOOL_BUILTIN = BuiltinTypeSymbol(name=grammar.BOOL, type="Bool")
# BYTES_BUILTIN = BuiltinTypeSymbol(name=grammar.BYTES, type="Bytes")
STR_BUILTIN = BuiltinTypeSymbol(name=grammar.STR, type="Str")
STRUCT_BUILTIN = BuiltinTypeSymbol(name=grammar.STRUCT, type="Str")
LIST_BUILTIN = BuiltinTypeSymbol(name=grammar.LIST, type="List")
DICT_BUILTIN = BuiltinTypeSymbol(name=grammar.DICT, type="Dict")
ENUM_BUILTIN = BuiltinTypeSymbol(name=grammar.ENUM, type="Enum")
FUNC_BUILTIN = BuiltinTypeSymbol(name=grammar.FUNC, type="Func")


@dataclass(kw_only=True)
class AccessibleSymbol(Symbol):
    accessed: bool = False


@dataclass(kw_only=True)
class VarSymbol(AccessibleSymbol):
    val_assigned: bool = False
    read_only: bool = False


@dataclass(kw_only=True)
class StructSymbol(AccessibleSymbol):
    fields: dict[str, my_ast.Type]
    val_assigned: bool = False


@dataclass(kw_only=True)
class CollectionSymbol(AccessibleSymbol):
    item_types: Symbol
    val_assigned: bool = False


@dataclass(kw_only=True)
class FuncSymbol(AccessibleSymbol):
    parameters: dict[str, my_ast.Var | my_ast.Type] | None
    parameter_defaults: dict[str, my_ast.Node] = field(default_factory=dict)
    body: my_ast.Compound | None
    val_assigned: bool = False


@dataclass(kw_only=True)
class AliasSymbol(AccessibleSymbol):
    type: list[my_ast.Type]


@dataclass(kw_only=True)
class BuiltinFuncSymbol(AccessibleSymbol):
    parameters: my_ast.Var | my_ast.Type
    body: my_ast.Compound
    val_assigned: bool = False


class NodeVisitor:
    def __init__(self) -> None:
        self._scope: list[Scope] = [{}]
        self._init_builtins()

    def _init_builtins(self):
        self.define(grammar.ANY, ANY_BUILTIN)
        self.define(grammar.INT, INT_BUILTIN)
        # self.define(grammar.INT8, INT8_BUILTIN)
        # self.define(grammar.INT32, INT32_BUILTIN)
        # self.define(grammar.INT128, INT128_BUILTIN)
        self.define(grammar.DEC, DEC_BUILTIN)
        self.define(grammar.FLOAT, FLOAT_BUILTIN)
        # self.define(grammar.COMPLEX, COMPLEX_BUILTIN)
        self.define(grammar.BOOL, BOOL_BUILTIN)
        # self.define(grammar.BYTES, BYTES_BUILTIN)
        self.define(grammar.STR, STR_BUILTIN)
        self.define(grammar.STRUCT, STRUCT_BUILTIN)
        self.define(grammar.LIST, LIST_BUILTIN)
        self.define(grammar.DICT, DICT_BUILTIN)
        self.define(grammar.ENUM, ENUM_BUILTIN)
        self.define(grammar.FUNC, FUNC_BUILTIN)

    def visit(self, node: my_ast.Node) -> Any:
        method_name = "visit_" + to_snake(type(node).__name__)
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    @staticmethod
    def generic_visit(node: my_ast.Node) -> None:
        raise VisitorException(f"No visit_{to_snake(type(node).__name__)} method")

    @property
    def top_scope(self) -> Scope | None:
        return self._scope[-1] if len(self._scope) >= 1 else None

    @property
    def second_scope(self) -> Scope | None:
        return self._scope[-2] if len(self._scope) >= 2 else None

    def search_scopes(self, name: str, level: int | None = None) -> Symbol | None:
        if level:
            if name in self._scope[level]:
                return self._scope[level][name]
        else:
            for scope in reversed(self._scope):
                if name in scope:
                    return scope[name]
        return None

    def define(self, key: str, value: Symbol, level: int = 0) -> None:
        level = (len(self._scope) - level) - 1
        self._scope[level][key] = value

    def new_scope(self) -> None:
        self._scope.append({})

    def drop_top_scope(self) -> None:
        self._scope.pop()

    @property
    def symbols(self) -> list[AccessibleSymbol]:
        return [value for scope in self._scope for value in scope.values()]

    @property
    def keys(self) -> list[str]:
        return [key for scope in self._scope for key in scope]

    @property
    def items(self) -> list[tuple[str, AccessibleSymbol]]:
        return [(key, value) for scope in self._scope for key, value in scope.items()]

    @property
    def unvisited_symbols(self) -> list[str]:
        return [
            sym_name
            for sym_name, sym_val in self.items
            if not isinstance(sym_val, (BuiltinTypeSymbol, BuiltinFuncSymbol))
            and not sym_val.accessed
        ]

    def infer_type(self, value: Symbol) -> Symbol | None:
        if isinstance(value, BuiltinTypeSymbol):
            return value
        if isinstance(value, FuncSymbol):
            return self.search_scopes(grammar.FUNC)
        elif isinstance(value, VarSymbol):
            return value.type
        elif isinstance(value, my_ast.Type):
            return self.search_scopes(value.value)
        else:
            if isinstance(value, int):
                return self.search_scopes(grammar.INT)
            elif isinstance(value, Decimal):
                return self.search_scopes(grammar.DEC)
            elif isinstance(value, float):
                return self.search_scopes(grammar.FLOAT)
            elif isinstance(value, complex):
                return self.search_scopes(grammar.COMPLEX)
            elif isinstance(value, str):
                return self.search_scopes(grammar.STR)
            elif isinstance(value, bool):
                return self.search_scopes(grammar.BOOL)
            elif isinstance(value, bytes):
                return self.search_scopes(grammar.BYTES)
            elif isinstance(value, list):
                return self.search_scopes(grammar.LIST)
            elif isinstance(value, dict):
                return self.search_scopes(grammar.DICT)
            elif isinstance(value, Enum):
                return self.search_scopes(grammar.ENUM)
            elif callable(value):
                return self.search_scopes(grammar.FUNC)
            else:
                raise TypeError(f"Type not recognized: {value}")
