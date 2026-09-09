from collections.abc import Generator
from contextlib import contextmanager, suppress
import re
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any

import grammar
import my_ast
import my_types
import import_manager

type Scope = dict[str, Symbol]


def to_snake(s: str) -> str:
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    s = s.lower()
    return s


class VisitorError(Exception):
    pass


@dataclass
class Symbol:
    name: str
    node: my_ast.Node
    type: my_types.MyAny
    accessed: bool = False


ANY_BUILTIN = Symbol(name=grammar.ANY, node=my_ast.Node(), type=my_types.MyAny())
TRUE_BUILTIN = Symbol(name=grammar.TRUE, node=my_ast.Node(), type=my_types.Bool())
FALSE_BUILTIN = Symbol(name=grammar.FALSE, node=my_ast.Node(), type=my_types.Bool())
INT_BUILTIN = Symbol(name=grammar.INT, node=my_ast.Node(), type=my_types.Int())
# INT8_BUILTIN = Symbol(name=grammar.INT8, node=my_ast.Node(), type="Int8")
INT32_BUILTIN = Symbol(name=grammar.INT32, node=my_ast.Node(), type=my_types.Int32())
INT64_BUILTIN = Symbol(name=grammar.INT64, node=my_ast.Node(), type=my_types.Int64())
DEC_BUILTIN = Symbol(name=grammar.DEC, node=my_ast.Node(), type=my_types.Dec())
FLOAT_BUILTIN = Symbol(name=grammar.FLOAT, node=my_ast.Node(), type=my_types.Float())
# COMPLEX_BUILTIN = Symbol(name=grammar.COMPLEX, type="Complex")
BOOL_BUILTIN = Symbol(name=grammar.BOOL, node=my_ast.Node(), type=my_types.Bool())
# BYTES_BUILTIN = Symbol(name=grammar.BYTES, type="Bytes")
STR_BUILTIN = Symbol(name=grammar.STR, node=my_ast.Node(), type=my_types.Str())
STRUCT_BUILTIN = Symbol(name=grammar.STRUCT, node=my_ast.Node(), type=my_types.Struct())
LIST_BUILTIN = Symbol(name=grammar.LIST, node=my_ast.Node(), type=my_types.List())
DICT_BUILTIN = Symbol(name=grammar.DICT, node=my_ast.Node(), type=my_types.Dict())
ENUM_BUILTIN = Symbol(name=grammar.ENUM, node=my_ast.Node(), type=my_types.MyEnum())
FUNC_BUILTIN = Symbol(name=grammar.FUNC, node=my_ast.Node(), type=my_types.Func())


PRINT_BUILTIN = Symbol(
    name=grammar.PRINT,
    node=my_ast.Print(
        name=grammar.PRINT,
        arguments=[
            my_ast.Var(
                value="output",
                line_num=1,
                type=my_ast.Type(name=grammar.STR, line_num=1, val_type=grammar.STR),
            )
        ],
        line_num=1,
    ),
    type=my_types.Void(),
)
INPUT_BUILTIN = Symbol(
    name=grammar.INPUT,
    node=my_ast.Input(
        name=grammar.INPUT,
        arguments=[
            my_ast.Var(
                value="prompt",
                type=my_ast.Type(name=grammar.STR, line_num=1),
                line_num=1,
            )
        ],
        line_num=1,
    ),
    type=my_types.Str(),
)
OPEN_BUILTIN = Symbol(
    name=grammar.OPEN,
    node=my_ast.Open(
        name=grammar.OPEN,
        arguments=[
            my_ast.Var(
                value="path", type=my_ast.Type(name=grammar.STR, line_num=1), line_num=1
            )
        ],
        line_num=1,
    ),
    type=my_types.Class("File"),
)


FILE_BUILTIN = Symbol(
    name="File",
    node=my_ast.ClassDeclaration(
        name="File",
        instance_fields={
            "my_file": my_ast.Type(name="my_file", line_num=1),
            "path": my_ast.Type(name=grammar.STR, line_num=1),
        },
        static_fields={},
        parameter_defaults={},
        constructor=my_ast.FuncDecl(
            name=grammar.NEW,
            return_type=my_ast.Void(line_num=1),
            parameters={
                "path": my_ast.Var(
                    value="path",
                    type=my_ast.Type(name=grammar.STR, line_num=1),
                    line_num=1,
                ),
            },
            type=my_ast.FuncType.CONSTRUCTOR,
            body=my_ast.Compound(children=[]),
            line_num=1,
        ),
        methods={
            "read": my_ast.FuncDecl(
                name="read",
                return_type=my_ast.Str(name=grammar.STR, line_num=1),
                parameters={},
                body=my_ast.Compound(children=[]),
                line_num=1,
            ),
            "write": my_ast.FuncDecl(
                name="write",
                return_type=my_ast.Void(line_num=1),
                parameters={"data": my_ast.Str(name=grammar.STR, line_num=1)},
                body=my_ast.Compound(children=[]),
                line_num=1,
            ),
            "close": my_ast.FuncDecl(
                name="close",
                return_type=my_ast.Void(line_num=1),
                parameters={},
                body=my_ast.Compound(children=[]),
                line_num=1,
            ),
        },
        base=my_ast.NotDoneYet(),
        line_num=1,
    ),
    type=my_types.Class(name="File"),
)


class NodeVisitor:
    import_manager = import_manager.ImportManager()

    def __init__(self) -> None:
        self._scope: list[Scope] = [{}]
        self._init_builtins()
        self.import_names = []

    def _init_builtins(self):
        self.define(grammar.ANY, ANY_BUILTIN)
        self.define(grammar.TRUE, TRUE_BUILTIN)
        self.define(grammar.FALSE, FALSE_BUILTIN)
        self.define(grammar.INT, INT_BUILTIN)
        # self.define(grammar.INT8, INT8_BUILTIN)
        self.define(grammar.INT32, INT32_BUILTIN)
        self.define(grammar.INT64, INT64_BUILTIN)
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
        self.define(grammar.OPEN, OPEN_BUILTIN)
        self.define("File", FILE_BUILTIN)

    def visit(self, node: my_ast.Node) -> Any:
        method_name = "visit_" + to_snake(type(node).__name__)
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    @staticmethod
    def generic_visit(node: my_ast.Node) -> None:
        raise VisitorError(f"No visit_{to_snake(type(node).__name__)} method")

    @property
    def top_scope(self) -> Scope:
        return self._scope[-1] if len(self._scope) >= 1 else {}

    @property
    def second_scope(self) -> Scope:
        return self._scope[-2] if len(self._scope) >= 2 else {}

    def search_scopes(self, name: str, level: int | None = None) -> Symbol | None:
        if level:
            if name in self._scope[level]:
                return self._scope[level][name]
        else:
            for scope in reversed(self._scope):
                if name in scope:
                    return scope[name]
        for scope in reversed(self._scope):
            for import_name in self.import_names:
                if f"{import_name}.{name}" in scope:
                    return scope[f"{import_name}.{name}"]
        return None

    def define(self, key: str, value: Symbol, level: int = 0) -> None:
        level = (len(self._scope) - level) - 1
        self._scope[level][key] = value

    @contextmanager
    def temp_define(
        self, key: str, value: Symbol, level: int = 0
    ) -> Generator[None, None, None]:
        level = (len(self._scope) - level) - 1
        self._scope[level][key] = value
        yield
        del self._scope[level][key]

    @contextmanager
    def create_scope(self) -> Generator[None, None, None]:
        self.new_scope()
        yield
        self.pop_scope()

    def new_scope(self) -> None:
        self._scope.append({})

    def pop_scope(self) -> None:
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

    def infer_type(self, value: Any) -> my_types.MyAny | None:
        with suppress(TypeError):
            if isinstance(value, my_types.MyAny):
                return value
        if isinstance(value, Symbol):
            return value.type
        elif isinstance(value, my_ast.Type):
            scoped_var = self.search_scopes(value.name)
            if scoped_var is None:
                return None
            return scoped_var.type
        elif value == grammar.VOID:
            return my_types.Void()
        else:
            scoped_var = None
            if value == grammar.INT64:
                scoped_var = self.search_scopes(grammar.INT64)
            elif value == grammar.INT32:
                scoped_var = self.search_scopes(grammar.INT32)
            elif isinstance(value, int) or value == grammar.INT:
                scoped_var = self.search_scopes(grammar.INT)
            elif isinstance(value, Decimal) or value == grammar.DEC:
                scoped_var = self.search_scopes(grammar.DEC)
            elif isinstance(value, float) or value == grammar.FLOAT:
                scoped_var = self.search_scopes(grammar.FLOAT)
            elif isinstance(value, complex) or value == grammar.COMPLEX:
                scoped_var = self.search_scopes(grammar.COMPLEX)
            elif isinstance(value, str) or value == grammar.STR:
                scoped_var = self.search_scopes(grammar.STR)
            elif isinstance(value, bool) or value == grammar.BOOL:
                scoped_var = self.search_scopes(grammar.BOOL)
            elif isinstance(value, bytes) or value == grammar.BYTES:
                scoped_var = self.search_scopes(grammar.BYTES)
            elif isinstance(value, list) or value == grammar.LIST:
                scoped_var = self.search_scopes(grammar.LIST)
            elif isinstance(value, dict) or value == grammar.DICT:
                scoped_var = self.search_scopes(grammar.DICT)
            elif isinstance(value, Enum) or value == grammar.ENUM:
                scoped_var = self.search_scopes(grammar.ENUM)
            elif callable(value) or value == grammar.FUNC:
                scoped_var = self.search_scopes(grammar.FUNC)
            if scoped_var is None:
                return None
            return scoped_var.type
        raise VisitorError(f"Type not recognized: {value}")
