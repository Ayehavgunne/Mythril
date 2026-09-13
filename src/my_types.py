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
    NONE = auto()
    RAW = auto()
    REFERENCE = auto()
    UNIQUE = auto()
    SHARED = auto()
    WEAK = auto()


@dataclass(kw_only=True)
class Pointer:
    type: PointerType = PointerType.SHARED
    subtype: MyAny = field(default_factory=MyAny)

    @property
    def destination_type(self) -> str:
        dest_type = self.subtype.destination_type
        match self.type:
            case PointerType.NONE:
                return dest_type
            case PointerType.RAW:
                return f"*{dest_type}"
            case PointerType.REFERENCE:
                return f"{dest_type}&"
            case PointerType.UNIQUE:
                return f"unique_ptr<{dest_type}>"
            case PointerType.SHARED:
                return f"shared_ptr<{dest_type}>"
            case PointerType.WEAK:
                return f"weak_ptr<{dest_type}>"

    def make(self, value: str) -> str:
        match self.type:
            case PointerType.NONE:
                return value
            case PointerType.RAW:
                return value
            case PointerType.REFERENCE:
                return value
            case PointerType.UNIQUE:
                return f"make_unique<{self.subtype.destination_type}>({value})"
            case PointerType.SHARED:
                return f"make_shared<{self.subtype.destination_type}>({value})"
            case PointerType.WEAK:
                return f"make_weak<{self.subtype.destination_type}>({value})"

    @property
    def dereference(self) -> str:
        match self.type:
            case PointerType.NONE:
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
        return "byte"


@dataclass
class Collection(MyAny):
    pass


@dataclass
class List(Collection):
    name: str = grammar.LIST
    subtype: MyAny = field(default_factory=MyAny)

    @property
    def destination_type(self) -> str:
        if self.name == grammar.LIST:
            return f"vector<{self.subtype.destination_type}>"
        else:
            return f"{self.name}<{self.subtype.destination_type}>"


@dataclass
class Tuple(Collection):
    name: str = grammar.TUPLE
    subtypes: list[MyAny] = field(default_factory=list)
    _current: int = 0

    @property
    def destination_type(self) -> str:
        return f"tuple<{', '.join([subtype.destination_type for subtype in self.subtypes])}>"

    def __iter__(self):
        return self

    def __next__(self):
        if self._current < len(self.subtypes) - 1:
            value = self.subtypes[self._current]
            self._current += 1
            return value
        else:
            raise StopIteration


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
