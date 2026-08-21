from dataclasses import dataclass, field

import grammar
# import my_types


@dataclass
class AST:
    pass


@dataclass
class NotDoneYet(AST):
    pass


@dataclass
class Program(AST):
    block: Compound


@dataclass
class VarDecl(AST):
    value: Var
    type: Type
    line_num: int
    read_only: bool = False


@dataclass
class Var(AST):
    value: str
    type: str
    line_num: int
    read_only: bool = False


@dataclass
class Compound(AST):
    children: list[AST] = field(default_factory=list)


@dataclass
class FuncDecl(AST):
    name: str
    return_type: Type
    parameters: Var | Type
    body: Compound
    line_num: int
    parameter_defaults: dict[str, AST] = field(default_factory=dict)
    varargs: list[str | Var | Type] = field(default_factory=list)


@dataclass
class AnonymousFunc(AST):
    return_type: Type
    parameters: Var | Type
    body: Compound
    line_num: int
    parameter_defaults: dict[str, AST] = field(default_factory=dict)
    varargs: list[str | Var | Type] = field(default_factory=list)


@dataclass
class FuncCall(AST):
    name: str
    arguments: list[AST]
    line_num: int
    named_arguments: dict[str, AST] = field(default_factory=dict)


@dataclass
class MethodCall(AST):
    obj: str
    name: str
    arguments: list
    line_num: int
    named_arguments: dict[str, AST] = field(default_factory=dict)


@dataclass
class Return(AST):
    value: AST
    line_num: int


@dataclass
class StructDeclaration(AST):
    name: str
    fields: dict[str, Type]
    line_num: int


@dataclass
class StructLiteral(AST):
    fields: dict[str, Type]
    line_num: int


@dataclass
class ClassDeclaration(AST):
    name: str
    base: NotDoneYet
    constructor: FuncDecl | None
    methods: NotDoneYet
    class_fields: NotDoneYet
    instance_fields: NotDoneYet


@dataclass
class Assign(AST):
    left: AST | list[AST]
    op: str
    right: AST | list[AST]
    line_num: int


@dataclass
class OpAssign(AST):
    left: AST | list[AST]
    op: str
    right: AST | list[AST]
    line_num: int


@dataclass
class If(AST):
    op: str
    comps: list[AST]
    blocks: list[Compound]
    indent_level: int
    line_num: int


@dataclass
class Else(AST):
    pass


@dataclass
class While(AST):
    op: str
    comp: list[AST]
    block: LoopBlock
    line_num: int


@dataclass
class For(AST):
    iterator: AST | list[AST]
    block: LoopBlock
    elements: list[AST]
    line_num: int


@dataclass
class LoopBlock(AST):
    children: list[AST] = field(default_factory=list)


@dataclass
class Break(AST):
    line_num: int


@dataclass
class Continue(AST):
    line_num: int


@dataclass
class Pass(AST):
    line_num: int


@dataclass
class BinOp(AST):
    left: AST | list[AST]
    op: str
    right: AST | list[AST]
    line_num: int


@dataclass
class UnaryOp(AST):
    op: str
    expr: AST | list[AST]
    line_num: int


@dataclass
class Range(AST):
    left: AST | list[AST]
    right: AST | list[AST]
    line_num: int
    value = grammar.RANGE


@dataclass
class CollectionAccess(AST):
    collection: grammar.Token
    key: AST
    line_num: int


@dataclass
class DotAccess(AST):
    obj: str
    field: str
    line_num: int


@dataclass
class Type(AST):
    value: str
    line_num: int
    func_ret_type: Type | None = None


@dataclass
class AliasDeclaration(AST):
    name: str
    collection: tuple[Type]
    line_num: int


@dataclass
class Void(AST):
    value: str = "void"


@dataclass
class Constant(AST):
    value: str
    line_num: int


@dataclass
class Num(AST):
    value: str
    val_type: str | None
    line_num: int


@dataclass
class Str(AST):
    value: str
    line_num: int


@dataclass
class Collection(AST):
    type: str
    line_num: int
    read_only: bool
    items: list[AST]


@dataclass
class Dict(AST):
    items: dict[str, AST]
    line_num: int


@dataclass
class Print(AST):
    value: AST
    line_num: int


@dataclass
class Input(AST):
    value: AST
    line_num: int
