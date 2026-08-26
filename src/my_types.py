from dataclasses import dataclass, field

import grammar


@dataclass
class Any:
    name: str = grammar.ANY

    @property
    def type(self):
        return 'void'

@dataclass
class AnyVal(Any):
    pass


@dataclass
class Int(AnyVal):
    name: str = grammar.INT

    @property
    def type(self):
        return "int"


@dataclass
class Int8(AnyVal):
    name: str = grammar.INT8

    @property
    def type(self):
        raise 'char'


@dataclass
class Int32(AnyVal):
    name: str = grammar.INT32

    @property
    def type(self):
        return "long"


@dataclass
class Int64(AnyVal):
    name: str = grammar.INT64

    @property
    def type(self):
        return "long long"


@dataclass
class Int128(AnyVal):
    name: str = grammar.INT128

    @property
    def type(self):
        raise NotImplementedError


@dataclass
class Dec(AnyVal):
    name: str = grammar.DEC

    @property
    def type(self):
        raise NotImplementedError


@dataclass
class Float(AnyVal):
    name: str = grammar.FLOAT

    @property
    def type(self):
        return "float"


@dataclass
class Complex(AnyVal):
    name: str = grammar.COMPLEX

    @property
    def type(self):
        raise NotImplementedError


@dataclass
class Str(AnyVal):
    name: str = grammar.STR

    @property
    def type(self):
        raise 'string'


@dataclass
class Bool(AnyVal):
    name: str = grammar.BOOL

    @property
    def type(self):
        return "bool"


@dataclass
class Bytes(AnyVal):
    name: str = grammar.BYTES

    @property
    def type(self):
        raise NotImplementedError


@dataclass
class Collection(Any):
    name: str = 'Collection'
    subtype: Any = field(default_factory=Any)


@dataclass
class List(Collection):
    name: str = grammar.LIST
    subtype: Any = field(default_factory=Any)

    @property
    def type(self):
        return f'vector<{self.subtype.type}>'


@dataclass
class Set(Collection):
    name: str = grammar.SET

    @property
    def type(self):
        raise NotImplementedError


@dataclass
class Dict(Collection):
    name: str = grammar.DICT

    @property
    def type(self):
        raise NotImplementedError


@dataclass
class Enum(Collection):
    name: str = grammar.ENUM

    @property
    def type(self):
        raise NotImplementedError


@dataclass
class Struct(Collection):
    name: str = grammar.STRUCT

    @property
    def type(self):
        raise NotImplementedError


@dataclass
class AnyRef(Any):
    pass


@dataclass
class Func(AnyRef):
    name: str = grammar.FUNC

    @property
    def type(self):
        raise NotImplementedError


type_map = {
    grammar.ANY: Any,
    grammar.INT: Int,
    grammar.STR: Str,
}
