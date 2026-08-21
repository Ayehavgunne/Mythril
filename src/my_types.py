from dataclasses import dataclass

import grammar


@dataclass
class Any:
    name: str = grammar.ANY


@dataclass
class AnyVal(Any):
    name: None


@dataclass
class Int(AnyVal):
    name: str = grammar.INT

    @staticmethod
    def type():
        return "int"


@dataclass
class Int8(AnyVal):
    name: str = grammar.INT8

    @staticmethod
    def type():
        raise NotImplementedError


@dataclass
class Int32(AnyVal):
    name: str = grammar.INT32

    @staticmethod
    def type():
        return "long"


@dataclass
class Int64(AnyVal):
    name: str = grammar.INT64

    @staticmethod
    def type():
        return "long long"


@dataclass
class Int128(AnyVal):
    name: str = grammar.INT128

    @staticmethod
    def type():
        raise NotImplementedError


@dataclass
class Dec(AnyVal):
    name: str = grammar.DEC

    @staticmethod
    def type():
        raise NotImplementedError


@dataclass
class Float(AnyVal):
    name: str = grammar.FLOAT

    @staticmethod
    def type():
        return "float"


@dataclass
class Complex(AnyVal):
    name: str = grammar.COMPLEX

    @staticmethod
    def type():
        raise NotImplementedError


@dataclass
class Str(AnyVal):
    name: str = grammar.STR

    @staticmethod
    def type():
        raise NotImplementedError


@dataclass
class Bool(AnyVal):
    name: str = grammar.BOOL

    @staticmethod
    def type():
        return "bool"


@dataclass
class Bytes(AnyVal):
    name: str = grammar.BYTES

    @staticmethod
    def type():
        raise NotImplementedError


@dataclass
class Collection(Any):
    name: None


@dataclass
class List(Collection):
    name: str = grammar.LIST

    @staticmethod
    def type():
        raise NotImplementedError


@dataclass
class Set(Collection):
    name: str = grammar.SET

    @staticmethod
    def type():
        raise NotImplementedError


@dataclass
class Dict(Collection):
    name: str = grammar.DICT

    @staticmethod
    def type():
        raise NotImplementedError


@dataclass
class Enum(Collection):
    name: str = grammar.ENUM

    @staticmethod
    def type():
        raise NotImplementedError


@dataclass
class Struct(Collection):
    name: str = grammar.STRUCT

    @staticmethod
    def type():
        raise NotImplementedError


@dataclass
class AnyRef(Any):
    name: None


@dataclass
class Func(AnyRef):
    name: str = grammar.FUNC

    @staticmethod
    def type():
        return "ir.FunctionType"


# def get_type_cls(cls):
# 	import sys
# 	import inspect
# 	for name, obj in inspect.getmembers(sys.modules[__name__]):
# 		if inspect.isclass(obj) and obj.__name__ == cls:
# 			return obj()
