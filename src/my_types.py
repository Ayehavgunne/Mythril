from dataclasses import dataclass, field

import grammar


@dataclass
class MyAny:
    name: str = grammar.ANY

    @property
    def destination_type(self) -> str:
        return "void"


@dataclass
class Void(MyAny):
    name: str = "void"


@dataclass
class AnyVal(MyAny):
    pass


@dataclass
class Int(AnyVal):
    name: str = grammar.INT

    @property
    def destination_type(self) -> str:
        return "int"


@dataclass
class Int8(AnyVal):
    name: str = grammar.INT8

    @property
    def destination_type(self) -> str:
        return "char"


@dataclass
class Int32(AnyVal):
    name: str = grammar.INT32

    @property
    def destination_type(self) -> str:
        return "long"


@dataclass
class Int64(AnyVal):
    name: str = grammar.INT64

    @property
    def destination_type(self) -> str:
        return "long long"


@dataclass
class Int128(AnyVal):
    name: str = grammar.INT128

    @property
    def destination_type(self) -> str:
        raise NotImplementedError


@dataclass
class Dec(AnyVal):
    name: str = grammar.DEC

    @property
    def destination_type(self) -> str:
        raise NotImplementedError


@dataclass
class Float(AnyVal):
    name: str = grammar.FLOAT

    @property
    def destination_type(self) -> str:
        return "float"


@dataclass
class Complex(AnyVal):
    name: str = grammar.COMPLEX

    @property
    def destination_type(self) -> str:
        raise NotImplementedError


@dataclass
class Str(AnyVal):
    name: str = grammar.STR

    @property
    def destination_type(self) -> str:
        return "string"


@dataclass
class Bool(AnyVal):
    name: str = grammar.BOOL

    @property
    def destination_type(self) -> str:
        return "bool"


@dataclass
class Bytes(AnyVal):
    name: str = grammar.BYTES

    @property
    def destination_type(self) -> str:
        raise NotImplementedError


@dataclass
class Collection(MyAny):
    name: str = "Collection"
    subtype: MyAny = field(default_factory=MyAny)


@dataclass
class List(Collection):
    name: str = grammar.LIST
    subtype: MyAny = field(default_factory=MyAny)

    @property
    def destination_type(self) -> str:
        return f"vector<{self.subtype.destination_type}>"


@dataclass
class Set(Collection):
    name: str = grammar.SET

    @property
    def destination_type(self) -> str:
        raise NotImplementedError


@dataclass
class Dict(Collection):
    name: str = grammar.DICT

    @property
    def destination_type(self) -> str:
        raise NotImplementedError


@dataclass
class Enum(AnyVal):
    name: str

    @property
    def destination_type(self) -> str:
        return self.name


@dataclass
class Struct(AnyVal):
    name: str

    @property
    def destination_type(self) -> str:
        return self.name


@dataclass
class Class(AnyVal):
    name: str

    @property
    def destination_type(self) -> str:
        return self.name

@dataclass
class AnyRef(MyAny):
    pass


@dataclass
class Func(AnyRef):
    name: str = grammar.FUNC

    @property
    def destination_type(self) -> str:
        raise NotImplementedError


type_map = {
    grammar.ANY: MyAny,
    grammar.INT: Int,
    grammar.STR: Str,
    grammar.LIST: List,
    grammar.STRUCT: Struct,
    grammar.CLASS: Class,
}
