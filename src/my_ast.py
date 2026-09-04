from dataclasses import dataclass, field

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
class Eof(Statement):
    pass


@dataclass(kw_only=True, eq=True, frozen=True)
class Compound(Statement):
    children: list[Statement] = field(default_factory=list)


@dataclass(kw_only=True, eq=True, frozen=True)
class VarDecl(Statement):
    value: Var
    type: Type
    line_num: int
    read_only: bool = False


@dataclass(kw_only=True, eq=True, frozen=True)
class Var(Expression):
    value: str
    type: Type | None = None
    line_num: int
    read_only: bool = False


@dataclass(kw_only=True, eq=True, frozen=True)
class FuncDecl(Statement):
    name: str
    return_type: Type
    parameters: dict[str, Var | Type]
    body: Compound
    line_num: int
    parameter_defaults: dict[str, Node] = field(default_factory=dict)
    varargs: list[str | Var | Type] = field(default_factory=list)
    constructor: bool = False
    destructor: bool = False


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
class Return(Statement):
    value: Node
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class StructDeclaration(Statement):
    name: str
    instance_fields: dict[str, Type]
    static_fields: dict[str, Type]
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class StructLiteral(Expression):
    intsance_fields: dict[str, Type]
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class StructCreation(Statement):
    name: str
    arguments: list[Expression]
    line_num: int
    named_arguments: dict[str, Expression] = field(default_factory=dict)


@dataclass(kw_only=True, eq=True, frozen=True)
class ClassDeclaration(StructDeclaration):
    base: NotDoneYet
    constructor: FuncDecl | None
    methods: list[FuncDecl]


@dataclass(kw_only=True, eq=True, frozen=True)
class Self(Statement):
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
    block: LoopBlock
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class For(Statement):
    iterator: Expression | list[Expression]
    block: LoopBlock
    elements: list[Expression]
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class LoopBlock(Statement):
    children: list[Statement] = field(default_factory=list)


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
    value: str
    line_num: int
    val_type: str | None = None
    func_ret_type: Type | None = None


@dataclass(kw_only=True, eq=True, frozen=True)
class AliasDeclaration(Statement):
    name: str
    collection: tuple[Type]
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class Void(Type):
    value: str = "void"


@dataclass(kw_only=True, eq=True, frozen=True)
class Constant(Expression):
    value: str
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class Num(Type):
    value: str
    val_type: str | None
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class Str(Type):
    value: str
    val_type: str = grammar.STR
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class Collection(Expression):
    type: str
    line_num: int
    read_only: bool
    items: list[Expression]


@dataclass(kw_only=True, eq=True, frozen=True)
class Dict(Expression):
    items: dict[Expression, Expression]
    line_num: int


@dataclass(kw_only=True, eq=True, frozen=True)
class Print(FuncCall):
    pass


@dataclass(kw_only=True, eq=True, frozen=True)
class Input(FuncCall):
    pass


@dataclass(kw_only=True, eq=True, frozen=True)
class Open(FuncCall):
    pass


@dataclass(kw_only=True, eq=True, frozen=True)
class Import(Statement):
    name: str
    path: str
