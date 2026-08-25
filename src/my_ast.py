from dataclasses import dataclass, field

import grammar

# import my_types


@dataclass(kw_only=True)
class Node:
    pass


@dataclass(kw_only=True)
class NotDoneYet(Node):
    pass


@dataclass(kw_only=True)
class Statement(Node):
    pass


@dataclass(kw_only=True)
class Expression(Statement):
    pass


@dataclass(kw_only=True)
class Program(Statement):
    block: Compound


@dataclass(kw_only=True)
class Eof(Statement):
    pass


@dataclass(kw_only=True)
class Compound(Statement):
    children: list[Statement] = field(default_factory=list)


@dataclass(kw_only=True)
class VarDecl(Expression):
    value: Var
    type: Type
    line_num: int
    read_only: bool = False


@dataclass(kw_only=True)
class Var(Expression):
    value: str
    # type: str
    line_num: int
    read_only: bool = False


@dataclass(kw_only=True)
class FuncDecl(Expression):
    name: str
    return_type: Type
    parameters: dict[str, Var | Type]
    body: Compound
    line_num: int
    parameter_defaults: dict[str, Node] = field(default_factory=dict)
    varargs: list[str | Var | Type] = field(default_factory=list)


@dataclass(kw_only=True)
class AnonymousFunc(Expression):
    return_type: Type
    parameters: dict[str, Var | Type]
    body: Compound
    line_num: int
    parameter_defaults: dict[str, Node] = field(default_factory=dict)
    varargs: list[str | Var | Type] = field(default_factory=list)


@dataclass(kw_only=True)
class FuncCall(Expression):
    name: str
    arguments: list[Expression]
    line_num: int
    named_arguments: dict[str, Expression] = field(default_factory=dict)


@dataclass(kw_only=True)
class MethodCall(Expression):
    obj: str
    name: str
    arguments: list[Expression]
    line_num: int
    named_arguments: dict[str, Expression] = field(default_factory=dict)


@dataclass(kw_only=True)
class Return(Expression):
    value: Node
    line_num: int


@dataclass(kw_only=True)
class StructDeclaration(Statement):
    name: str
    fields: dict[str, Type]
    line_num: int


@dataclass(kw_only=True)
class StructLiteral(Expression):
    fields: dict[str, Type]
    line_num: int


@dataclass(kw_only=True)
class ClassDeclaration(Statement):
    name: str
    base: NotDoneYet
    constructor: FuncDecl | None
    methods: NotDoneYet
    class_fields: NotDoneYet
    instance_fields: NotDoneYet
    line_num: int


@dataclass(kw_only=True)
class Assign(Expression):
    left: Expression
    op: str
    right: Expression
    line_num: int


@dataclass(kw_only=True)
class OpAssign(Expression):
    left: Expression
    op: str
    right: Expression
    line_num: int


@dataclass(kw_only=True)
class If(Statement):
    comps: list[Expression]
    block: Compound
    indent_level: int
    line_num: int


@dataclass(kw_only=True)
class ElseIf(If):
    pass


@dataclass(kw_only=True)
class Else(Statement):
    block: Compound
    indent_level: int
    line_num: int


@dataclass(kw_only=True)
class While(Statement):
    op: str
    comp: list[Node]
    block: LoopBlock
    line_num: int


@dataclass(kw_only=True)
class For(Statement):
    iterator: Node | list[Node]
    block: LoopBlock
    elements: list[Node]
    line_num: int


@dataclass(kw_only=True)
class LoopBlock(Statement):
    children: list[Statement] = field(default_factory=list)


@dataclass(kw_only=True)
class Break(Statement):
    line_num: int


@dataclass(kw_only=True)
class Continue(Statement):
    line_num: int


@dataclass(kw_only=True)
class Pass(Statement):
    line_num: int


@dataclass(kw_only=True)
class BinOp(Expression):
    left: Expression
    op: str
    right: Expression
    line_num: int


@dataclass(kw_only=True)
class UnaryOp(Expression):
    op: str
    expr: Expression
    line_num: int


@dataclass(kw_only=True)
class Operator(Expression):
    value: str
    line_num: int


@dataclass(kw_only=True)
class Range(Expression):
    left: Expression
    right: Expression
    line_num: int
    value: str = grammar.RANGE


@dataclass(kw_only=True)
class CollectionAccess(Expression):
    key: Node
    line_num: int


@dataclass(kw_only=True)
class DotAccess(Expression):
    obj: str
    field: str
    line_num: int


@dataclass(kw_only=True)
class Type(Expression):
    value: str
    line_num: int
    func_ret_type: Type | None = None


@dataclass(kw_only=True)
class AliasDeclaration(Statement):
    name: str
    collection: tuple[Type]
    line_num: int


@dataclass(kw_only=True)
class Void(Type):
    value: str = "void"


@dataclass(kw_only=True)
class Constant(Expression):
    value: str
    line_num: int


@dataclass(kw_only=True)
class Num(Expression):
    value: str
    val_type: str | None
    line_num: int


@dataclass(kw_only=True)
class Str(Expression):
    value: str
    line_num: int


@dataclass(kw_only=True)
class Collection(Expression):
    type: str
    line_num: int
    read_only: bool
    items: list[Expression]


@dataclass(kw_only=True)
class Dict(Expression):
    items: dict[Expression, Expression]
    line_num: int


@dataclass(kw_only=True)
class Print(FuncCall):
    pass


@dataclass(kw_only=True)
class Input(FuncCall):
    pass
