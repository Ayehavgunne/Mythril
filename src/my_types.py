from dataclasses import dataclass, field
from enum import Enum, auto

import grammar


@dataclass
class MyAny:
    name: str = grammar.ANY

    @property
    def destination_type(self) -> str:
        return "void"


class PointerType(Enum):
    none = auto()
    raw = auto()
    reference = auto()
    unique = auto()
    shared = auto()
    weak = auto()


@dataclass(kw_only=True)
class Pointer:
    type: PointerType = PointerType.shared
    subtype: MyAny = field(default_factory=MyAny)

    @property
    def destination_type(self) -> str:
        dest_type = self.subtype.destination_type
        match self.type:
            case PointerType.none:
                return dest_type
            case PointerType.raw:
                return f"*{dest_type}"
            case PointerType.reference:
                return f"&{dest_type}"
            case PointerType.unique:
                return f"unique_ptr<{dest_type}>"
            case PointerType.shared:
                return f"shared_ptr<{dest_type}>"
            case PointerType.weak:
                return f"weak_ptr<{dest_type}>"

    def make(self, value: str) -> str:
        match self.type:
            case PointerType.none:
                return value
            case PointerType.raw:
                return value
            case PointerType.reference:
                return value
            case PointerType.unique:
                return f"make_unique<{self.subtype.destination_type}>({value})"
            case PointerType.shared:
                return f"make_shared<{self.subtype.destination_type}>({value})"
            case PointerType.weak:
                return f"make_weak<{self.subtype.destination_type}>({value})"

    @property
    def dereference(self) -> str:
        match self.type:
            case PointerType.none:
                return ""
            case _:
                return "*"


@dataclass
class Void(MyAny):
    name: str = "void"


@dataclass
class Auto(MyAny):
    name: str = "auto"

    @property
    def destination_type(self) -> str:
        return self.name


@dataclass
class AnyVal(MyAny):
    pass


@dataclass
class Int(AnyVal):
    name: str = grammar.INT

    @property
    def destination_type(self) -> str:
        return "BigInt::bigint"


@dataclass
class Int8(AnyVal):
    name: str = grammar.INT8

    @property
    def destination_type(self) -> str:
        return "char"


@dataclass
class Int16(AnyVal):
    name: str = grammar.INT16

    @property
    def destination_type(self) -> str:
        return "short"


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
class Dec(AnyVal):
    name: str = grammar.DEC

    @property
    def destination_type(self) -> str:
        return "float"  # TODO: find a decimal type library


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
        raise "byte"


@dataclass
class Collection(MyAny):
    pass


@dataclass
class List(Collection):
    name: str = grammar.LIST
    subtype: MyAny = field(default_factory=MyAny)

    @property
    def destination_type(self) -> str:
        return f"vector<{self.subtype.destination_type}>"


@dataclass
class Tuple(Collection):
    name: str = grammar.TUPLE
    subtypes: list[MyAny] = field(default_factory=list)

    @property
    def destination_type(self) -> str:
        return f"tuple<{', '.join([subtype.destination_type for subtype in self.subtypes])}>"


@dataclass
class Set(Collection):
    name: str = grammar.SET
    subtype: MyAny = field(default_factory=MyAny)

    @property
    def destination_type(self) -> str:
        return f"set<{self.subtype.destination_type}>"


@dataclass
class Dict(Collection):
    name: str = grammar.DICT
    key: MyAny = field(default_factory=MyAny)
    value: MyAny = field(default_factory=MyAny)

    @property
    def destination_type(self) -> str:
        return f"Dict<{self.key.destination_type}, {self.value.destination_type}>"


@dataclass
class MyEnum(AnyVal):
    name: str = grammar.ENUM

    @property
    def destination_type(self) -> str:
        return self.name


@dataclass
class Struct(AnyVal):
    name: str = grammar.STRUCT

    @property
    def destination_type(self) -> str:
        return self.name


@dataclass
class Class(AnyVal):
    name: str = grammar.CLASS

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


INTS = (Int, Int32, Int64)

TYPE_MAP = {
    grammar.ANY: MyAny,
    grammar.BOOL: Bool,
    grammar.INT: Int,
    grammar.INT16: Int16,
    grammar.INT32: Int32,
    grammar.INT64: Int64,
    grammar.DEC: Dec,
    grammar.FLOAT: Float,
    grammar.STR: Str,
    grammar.LIST: List,
    grammar.TUPLE: Tuple,
    grammar.SET: Set,
    grammar.DICT: Dict,
    grammar.ENUM: MyEnum,
    grammar.STRUCT: Struct,
    grammar.CLASS: Class,
}
