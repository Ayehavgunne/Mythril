from contextlib import suppress
from dataclasses import dataclass, field
from enum import StrEnum

import grammar


@dataclass(kw_only=True, eq=True, frozen=True)
class Node:
    pass


@dataclass(kw_only=True, eq=True, frozen=True)
class NotDoneYet(Node):
    pass


@dataclass(kw_only=True, eq=True, frozen=True)
class Statement(Node):
    pass


@dataclass(kw_only=True, eq=True, frozen=True)
class Expression(Node):
    pass


@dataclass(kw_only=True, eq=True, frozen=True)
class Program(Statement):
    block: Compound


@dataclass(kw_only=True, eq=True, frozen=True)
class Eof(Expression):
    pass


@dataclass(kw_only=True, eq=True, frozen=True)
class Compound(Statement):
    children: list[Statement | Expression] = field(default_factory=list)


@dataclass(kw_only=True, eq=True, frozen=True)
class VarDecl(Statement):
    value: Var
    type: Type
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class Var(Expression):
    value: str
    type: Type | None = None
    line_num: int


class FuncType(StrEnum):
    DEF = "def"
    CONSTRUCTOR = "new"
    DESTRUCTOR = "del"
    GETTER = "get"
    SETTER = "set"
    ENTER = "enter"
    EXIT = "exit"

    @classmethod
    def get(cls, name: str) -> "FuncType":
        with suppress(KeyError):
            return cls(name)
        return FuncType.DEF


@dataclass(kw_only=True, eq=True, frozen=True)
class FuncDecl(Statement):
    name: str
    return_type: Type
    parameters: dict[str, Var | Type]
    body: Compound
    line_num: int
    parameter_defaults: dict[str, Node] = field(default_factory=dict)
    varargs: list[str | Var | Type] = field(default_factory=list)
    type: FuncType = FuncType.DEF
    static: bool = False


@dataclass(kw_only=True, eq=True, frozen=True)
class AnonymousFunc(Expression):
    return_type: Type
    parameters: dict[str, Var | Type]
    body: Compound
    line_num: int
    parameter_defaults: dict[str, Node] = field(default_factory=dict)
    varargs: list[str | Var | Type] = field(default_factory=list)


@dataclass(kw_only=True, eq=True, frozen=True)
class FuncCall(Expression):
    name: str
    arguments: list[Expression]
    line_num: int
    named_arguments: dict[str, Expression] = field(default_factory=dict)


@dataclass(kw_only=True, eq=True, frozen=True)
class MethodCall(Expression):
    obj: Expression
    name: str
    arguments: list[Expression]
    line_num: int
    named_arguments: dict[str, Expression] = field(default_factory=dict)


@dataclass(kw_only=True, eq=True, frozen=True)
class Return(Expression):
    value: Node
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class StructDeclaration(Statement):
    name: str
    instance_fields: dict[str, Type]
    static_fields: dict[str, Type]
    parameter_defaults: dict[str, Node] = field(default_factory=dict)
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class StructLiteral(Expression):
    instance_fields: dict[str, Type]
    parameter_defaults: dict[str, Node] = field(default_factory=dict)
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class StructCreation(Statement):
    name: str
    arguments: list[Expression]
    line_num: int
    named_arguments: dict[str, Expression] = field(default_factory=dict)


@dataclass(kw_only=True, eq=True, frozen=True)
class Enum(Statement):
    name: str
    fields: list[Expression]
    subtype: Type
    methods: dict[str, FuncDecl]
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class ClassDeclaration(StructDeclaration):
    base: NotDoneYet
    constructor: FuncDecl | None
    methods: dict[str, FuncDecl]


@dataclass(kw_only=True, eq=True, frozen=True)
class Self(Expression):
    value: str = grammar.SELF
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class Assign(Statement):
    left: Expression
    op: str
    right: Expression
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class OpAssign(Assign):
    pass


@dataclass(kw_only=True, eq=True, frozen=True)
class If(Statement):
    comps: list[Expression]
    block: Compound
    indent_level: int
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class ElseIf(If):
    pass


@dataclass(kw_only=True, eq=True, frozen=True)
class Else(Statement):
    block: Compound
    indent_level: int
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class While(Statement):
    op: str
    comp: list[Expression]
    block: Compound
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class For(Statement):
    iterator: Expression  # | list[Expression]
    block: Compound
    elements: list[Expression]
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class Break(Statement):
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class Continue(Statement):
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class Pass(Statement):
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class With(Statement):
    expr: Expression
    var: Expression | None = None
    body: Compound
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class BinOp(Expression):
    left: Expression
    op: Operator
    right: Expression
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class UnaryOp(Expression):
    op: Operator
    expr: Expression
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class Operator(Expression):
    value: str
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class Cast(BinOp):
    pass


@dataclass(kw_only=True, eq=True, frozen=True)
class Range(Expression):
    left: Expression
    right: Expression
    line_num: int
    value: str = grammar.RANGE


@dataclass(kw_only=True, eq=True, frozen=True)
class Slice(Expression):
    item: str
    left: Expression
    right: Expression
    line_num: int
    value: str = grammar.SLICE


@dataclass(kw_only=True, eq=True, frozen=True)
class CollectionAccess(Expression):
    name: str
    key: Node
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class DotAccess(Expression):
    obj: Expression
    field: str
    line_num: int
    method_call: bool = False


@dataclass(kw_only=True, eq=True, frozen=True)
class Type(Expression):
    name: str
    line_num: int
    val_type: str = ""
    # func_ret_type: Type | None = None


@dataclass(kw_only=True, eq=True, frozen=True)
class AliasDeclaration(Statement):
    name: str
    collection: tuple[Type]
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class Void(Type):
    name: str = "void"


@dataclass(kw_only=True, eq=True, frozen=True)
class Constant(Expression):
    value: str
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class Num(Type):
    name: str
    val_type: str = grammar.INT
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class Str(Type):
    name: str
    val_type: str = grammar.STR
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class Collection(Expression):
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class List(Collection):
    items: list[Expression]


@dataclass(kw_only=True, eq=True, frozen=True)
class Tuple(Collection):
    items: list[Expression]


@dataclass(kw_only=True, eq=True, frozen=True)
class Set(Collection):
    items: list[Expression]


@dataclass(kw_only=True, eq=True, frozen=True)
class Dict(Collection):
    items: dict[Expression, Expression]


COLLECTION_MAP = {
    List: grammar.LIST,
    Tuple: grammar.TUPLE,
    Set: grammar.SET,
    Dict: grammar.DICT,
}


def get_collection_type(collection: Collection) -> str:
    return COLLECTION_MAP[type(collection)]


@dataclass(kw_only=True, eq=True, frozen=True)
class Print(FuncCall):
    named_arguments: dict[str, Expression] = field(
        default_factory=lambda: {
            "end": Str(name="\\n", line_num=1),
            "sep": Str(name=" ", line_num=1),
        }
    )


@dataclass(kw_only=True, eq=True, frozen=True)
class Input(FuncCall):
    pass


@dataclass(kw_only=True, eq=True, frozen=True)
class Open(FuncCall):
    pass


@dataclass(kw_only=True, eq=True, frozen=True)
class Import(Expression):
    name: str
    path: str
