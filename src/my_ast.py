from dataclasses import dataclass, field

import grammar

# import my_types


@dataclass
class Node:
    pass


@dataclass
class NotDoneYet(Node):
    pass


@dataclass
class Statement(Node):
    pass


@dataclass
class Expression(Statement):
    pass


@dataclass
class Program(Statement):
    block: Compound


@dataclass
class Eof(Statement):
    pass


@dataclass
class Compound(Statement):
    children: list[Statement] = field(default_factory=list)


@dataclass
class VarDecl(Expression):
    value: Var
    type: Type
    line_num: int
    read_only: bool = False


@dataclass
class Var(Expression):
    value: str
    # type: str
    line_num: int
    read_only: bool = False


@dataclass
class FuncDecl(Expression):
    name: str
    return_type: Type
    parameters: dict[str, Var | Type]
    body: Compound
    line_num: int
    parameter_defaults: dict[str, Node] = field(default_factory=dict)
    varargs: list[str | Var | Type] = field(default_factory=list)


@dataclass
class AnonymousFunc(Expression):
    return_type: Type
    parameters: Var | Type
    body: Compound
    line_num: int
    parameter_defaults: dict[str, Node] = field(default_factory=dict)
    varargs: list[str | Var | Type] = field(default_factory=list)


@dataclass
class FuncCall(Expression):
    name: str
    arguments: list[Node]
    line_num: int
    named_arguments: dict[str, Node] = field(default_factory=dict)


@dataclass
class MethodCall(Expression):
    obj: str
    name: str
    arguments: list
    line_num: int
    named_arguments: dict[str, Node] = field(default_factory=dict)


@dataclass
class Return(Expression):
    value: Node
    line_num: int


@dataclass
class StructDeclaration(Statement):
    name: str
    fields: dict[str, Type]
    line_num: int


@dataclass
class StructLiteral(Expression):
    fields: dict[str, Type]
    line_num: int


@dataclass
class ClassDeclaration(Statement):
    name: str
    base: NotDoneYet
    constructor: FuncDecl | None
    methods: NotDoneYet
    class_fields: NotDoneYet
    instance_fields: NotDoneYet


@dataclass
class Assign(Expression):
    left: Expression
    op: str
    right: Expression
    line_num: int


@dataclass
class OpAssign(Expression):
    left: Expression
    op: str
    right: Expression
    line_num: int


@dataclass
class If(Statement):
    op: str
    comps: list[Node]
    blocks: list[Compound]
    indent_level: int
    line_num: int


@dataclass
class Else(Statement):
    pass


@dataclass
class While(Statement):
    op: str
    comp: list[Node]
    block: LoopBlock
    line_num: int


@dataclass
class For(Statement):
    iterator: Node | list[Node]
    block: LoopBlock
    elements: list[Node]
    line_num: int


@dataclass
class LoopBlock(Statement):
    children: list[Statement] = field(default_factory=list)


@dataclass
class Break(Statement):
    line_num: int


@dataclass
class Continue(Statement):
    line_num: int


@dataclass
class Pass(Statement):
    line_num: int


@dataclass
class BinOp(Expression):
    left: Expression
    op: str
    right: Expression
    line_num: int


@dataclass
class UnaryOp(Expression):
    op: str
    expr: Expression
    line_num: int


@dataclass
class Range(Expression):
    left: Expression
    right: Expression
    line_num: int
    value = grammar.RANGE


@dataclass
class CollectionAccess(Expression):
    collection: grammar.Token
    key: Node
    line_num: int


@dataclass
class DotAccess(Expression):
    obj: str
    field: str
    line_num: int


@dataclass
class Type(Expression):
    value: str
    line_num: int
    func_ret_type: Type | None = None


@dataclass
class AliasDeclaration(Statement):
    name: str
    collection: tuple[Type]
    line_num: int


@dataclass
class Void(Statement):
    value: str = "void"


@dataclass
class Constant(Expression):
    value: str
    line_num: int


@dataclass
class Num(Expression):
    value: str
    val_type: str | None
    line_num: int


@dataclass
class Str(Expression):
    value: str
    line_num: int


@dataclass
class Collection(Expression):
    type: str
    line_num: int
    read_only: bool
    items: list[Expression]


@dataclass
class Dict(Expression):
    items: dict[Expression, Expression]
    line_num: int


@dataclass
class Print(Expression):
    value: Node
    line_num: int


@dataclass
class Input(Expression):
    value: Node
    line_num: int
