import re
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any

import grammar
import my_ast

type Scope = dict[str, Symbol]


def to_snake(s: str) -> str:
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', s)
    s = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s)
    s = s.lower()
    return s


class VisitorException(Exception):
    pass


@dataclass(kw_only=True)
class Symbol:
    name: str
    type: Symbol | None = None


@dataclass
class BuiltinTypeSymbol(Symbol):
    pass


ANY_BUILTIN = BuiltinTypeSymbol(grammar.ANY)
INT_BUILTIN = BuiltinTypeSymbol(grammar.INT, "Int")
# INT8_BUILTIN = BuiltinTypeSymbol(grammar.INT8, "Int8")
# INT32_BUILTIN = BuiltinTypeSymbol(grammar.INT32, "Int32")
# INT128_BUILTIN = BuiltinTypeSymbol(grammar.INT128, "Int128")
DEC_BUILTIN = BuiltinTypeSymbol(grammar.DEC, "Dec")
FLOAT_BUILTIN = BuiltinTypeSymbol(grammar.FLOAT, "Float")
# COMPLEX_BUILTIN = BuiltinTypeSymbol(grammar.COMPLEX, "Complex")
BOOL_BUILTIN = BuiltinTypeSymbol(grammar.BOOL, "Bool")
# BYTES_BUILTIN = BuiltinTypeSymbol(grammar.BYTES, "Bytes")
STR_BUILTIN = BuiltinTypeSymbol(grammar.STR, "Str")
STRUCT_BUILTIN = BuiltinTypeSymbol(grammar.STRUCT, "Str")
LIST_BUILTIN = BuiltinTypeSymbol(grammar.LIST, "List")
DICT_BUILTIN = BuiltinTypeSymbol(grammar.DICT, "Dict")
ENUM_BUILTIN = BuiltinTypeSymbol(grammar.ENUM, "Enum")
FUNC_BUILTIN = BuiltinTypeSymbol(grammar.FUNC, "Func")


@dataclass
class VarSymbol(Symbol):
    accessed: bool = False
    val_assigned: bool = False
    read_only: bool = False


@dataclass
class StructSymbol(Symbol):
    fields: dict[str, my_ast.Type]
    accessed: bool = False
    val_assigned: bool = False


@dataclass
class CollectionSymbol(Symbol):
    item_types: Symbol
    accessed: bool = False
    val_assigned: bool = False


@dataclass
class FuncSymbol(Symbol):
    # def __init__(self, name, return_type, parameters, body, parameter_defaults=None):
    parameters = parameters
    parameter_defaults = parameter_defaults or {}
    body = body
    accessed: bool = False
    val_assigned: bool = False


@dataclass
class AliasSymbol(Symbol):
    accessed: bool = False


@dataclass
class BuiltinFuncSymbol(Symbol):
    # def __init__(self, name, return_type, parameters, body):
    parameters = parameters
    body = body
    accessed: bool = False
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

    def visit(self, node: my_ast.AST) -> Any:
        method_name = "visit_" + to_snake(type(node).__name__)
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    @staticmethod
    def generic_visit(node: my_ast.AST) -> None:
        raise VisitorException(f"No visit_{to_snake(type(node).__name__)} method")

    @property
    def top_scope(self) -> Scope | None:
        return self._scope[-1] if len(self._scope) >= 1 else None

    @property
    def second_scope(self) -> Scope | None:
        return self._scope[-2] if len(self._scope) >= 2 else None

    def search_scopes(self, name: str, level: int | None = None) -> Symbol:
        if level:
            if name in self._scope[level]:
                return self._scope[level][name]
        else:
            for scope in reversed(self._scope):
                if name in scope:
                    return scope[name]

    def define(self, key: str, value: Symbol, level: int = 0) -> None:
        level = (len(self._scope) - level) - 1
        self._scope[level][key] = value

    def new_scope(self) -> None:
        self._scope.append({})

    def drop_top_scope(self) -> None:
        self._scope.pop()

    @property
    def symbols(self) -> list[Symbol]:
        return [value for scope in self._scope for value in scope.values()]

    @property
    def keys(self) -> list[str]:
        return [key for scope in self._scope for key in scope]

    @property
    def items(self) -> list[tuple[str, Symbol]]:
        return [(key, value) for scope in self._scope for key, value in scope.items()]

    @property
    def unvisited_symbols(self) -> list[str]:
        return [
            sym_name
            for sym_name, sym_val in self.items
            if not isinstance(sym_val, (BuiltinTypeSymbol, BuiltinFuncSymbol))
            and not sym_val.accessed
        ]

    def infer_type(self, value: Symbol) -> Symbol:
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
