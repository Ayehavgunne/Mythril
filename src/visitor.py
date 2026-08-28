from contextlib import suppress
import re
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any

import grammar
import my_ast
import my_types

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
    type: my_types.MyAny


@dataclass(kw_only=True)
class AccessibleSymbol(Symbol):
    accessed: bool = False
    read_only: bool = False


@dataclass(kw_only=True)
class BuiltinTypeSymbol(AccessibleSymbol):
    pass


ANY_BUILTIN = BuiltinTypeSymbol(name=grammar.ANY, type=my_types.MyAny)
INT_BUILTIN = BuiltinTypeSymbol(name=grammar.INT, type=my_types.Int)
# INT8_BUILTIN = BuiltinTypeSymbol(name=grammar.INT8, type="Int8")
# INT32_BUILTIN = BuiltinTypeSymbol(name=grammar.INT32, type="Int32")
# INT128_BUILTIN = BuiltinTypeSymbol(name=grammar.INT128, type="Int128")
DEC_BUILTIN = BuiltinTypeSymbol(name=grammar.DEC, type=my_types.Dec)
FLOAT_BUILTIN = BuiltinTypeSymbol(name=grammar.FLOAT, type=my_types.Float)
# COMPLEX_BUILTIN = BuiltinTypeSymbol(name=grammar.COMPLEX, type="Complex")
BOOL_BUILTIN = BuiltinTypeSymbol(name=grammar.BOOL, type=my_types.Bool)
# BYTES_BUILTIN = BuiltinTypeSymbol(name=grammar.BYTES, type="Bytes")
STR_BUILTIN = BuiltinTypeSymbol(name=grammar.STR, type=my_types.Str)
STRUCT_BUILTIN = BuiltinTypeSymbol(name=grammar.STRUCT, type=my_types.Struct)
LIST_BUILTIN = BuiltinTypeSymbol(name=grammar.LIST, type=my_types.List)
DICT_BUILTIN = BuiltinTypeSymbol(name=grammar.DICT, type=my_types.Dict)
ENUM_BUILTIN = BuiltinTypeSymbol(name=grammar.ENUM, type=my_types.Enum)
FUNC_BUILTIN = BuiltinTypeSymbol(name=grammar.FUNC, type=my_types.Func)


@dataclass(kw_only=True)
class VarSymbol(AccessibleSymbol):
    val_assigned: bool = False


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
    # body: my_ast.Compound | None
    val_assigned: bool = False


@dataclass(kw_only=True)
class AliasSymbol(AccessibleSymbol):
    pass


@dataclass(kw_only=True)
class BuiltinFuncSymbol(FuncSymbol):
    pass


PRINT_BUILTIN = BuiltinFuncSymbol(
    name=grammar.PRINT,
    type=my_types.Void(),
    parameters={"output": my_ast.Type(value=grammar.ANY, line_num=1)},
    # body=None,
)
INPUT_BUILTIN = BuiltinFuncSymbol(
    name=grammar.INPUT,
    type=my_types.Str(),
    parameters={"output": my_ast.Type(value=grammar.ANY, line_num=1)},
    # body=None,
)


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
        self.define(grammar.PRINT, PRINT_BUILTIN)
        self.define(grammar.INPUT, INPUT_BUILTIN)

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

    def search_scopes(
        self, name: str, level: int | None = None
    ) -> AccessibleSymbol | None:
        if level:
            if name in self._scope[level]:
                return self._scope[level][name]
        else:
            for scope in reversed(self._scope):
                if name in scope:
                    return scope[name]
        return None

    def define(self, key: str, value: AccessibleSymbol, level: int = 0) -> None:
        level = (len(self._scope) - level) - 1
        self._scope[level][key] = value

    def new_scope(self) -> None:
        self._scope.append({})

    def pop_scope(self) -> None:
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

    def infer_type(self, value: Any) -> my_types.MyAny | None:
        with suppress(TypeError):
            if issubclass(value, my_types.MyAny):
                return value
        if isinstance(value, BuiltinTypeSymbol):
            return value.type
        if isinstance(value, FuncSymbol):
            return self.search_scopes(grammar.FUNC).type
        elif isinstance(value, VarSymbol):
            with suppress(TypeError):
                if issubclass(value.type, my_types.MyAny):
                    return value.type
            return self.infer_type(self.search_scopes(value.type.value))
        elif isinstance(value, my_ast.Type):
            return self.search_scopes(value.value).type
        else:
            if isinstance(value, int) or value == grammar.INT:
                return self.search_scopes(grammar.INT).type
            elif isinstance(value, Decimal) or value == grammar.DEC:
                return self.search_scopes(grammar.DEC).type
            elif isinstance(value, float) or value == grammar.FLOAT:
                return self.search_scopes(grammar.FLOAT).type
            elif isinstance(value, complex) or value == grammar.COMPLEX:
                return self.search_scopes(grammar.COMPLEX).type
            elif isinstance(value, str) or value == grammar.STR:
                return self.search_scopes(grammar.STR).type
            elif isinstance(value, bool) or value == grammar.BOOL:
                return self.search_scopes(grammar.BOOL).type
            elif isinstance(value, bytes) or value == grammar.BYTES:
                return self.search_scopes(grammar.BYTES).type
            elif isinstance(value, list) or value == grammar.LIST:
                return self.search_scopes(grammar.LIST).type
            elif isinstance(value, dict) or value == grammar.DICT:
                return self.search_scopes(grammar.DICT).type
            elif isinstance(value, Enum) or value == grammar.ENUM:
                return self.search_scopes(grammar.ENUM).type
            elif callable(value) or value == grammar.FUNC:
                return self.search_scopes(grammar.FUNC).type
        raise TypeError(f"Type not recognized: {value}")
