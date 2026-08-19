import grammar


class Any:
    def __init__(self):
        self.name = grammar.ANY

    def __str__(self):
        return f"<{self.name}>"

    __repr__ = __str__


class AnyVal(Any):
    def __init__(self):
        super().__init__()
        self.name = None


class Int(AnyVal):
    def __init__(self):
        super().__init__()
        self.name = grammar.INT

    @staticmethod
    def type():
        return "ir.IntType(64)"


class Int8(AnyVal):
    def __init__(self):
        super().__init__()
        self.name = grammar.INT8

    @staticmethod
    def type():
        return "ir.IntType(8)"


class Int32(AnyVal):
    def __init__(self):
        super().__init__()
        self.name = grammar.INT32

    @staticmethod
    def type():
        return "ir.IntType(32)"


class Int64(AnyVal):
    def __init__(self):
        super().__init__()
        self.name = grammar.INT64

    @staticmethod
    def type():
        return "ir.IntType(64)"


class Int128(AnyVal):
    def __init__(self):
        super().__init__()
        self.name = grammar.INT128

    @staticmethod
    def type():
        return "ir.IntType(128)"


class Dec(AnyVal):
    def __init__(self):
        super().__init__()
        self.name = grammar.DEC

    @staticmethod
    def type():
        return "ir.DoubleType()"  # TODO: temorarily making Decimal a DoubleType till find (or make) a better representation


class Float(AnyVal):
    def __init__(self):
        super().__init__()
        self.name = grammar.FLOAT

    @staticmethod
    def type():
        return "ir.FloatType()"


class Complex(AnyVal):
    def __init__(self):
        super().__init__()
        self.name = grammar.COMPLEX

    @staticmethod
    def type():
        raise NotImplementedError


class Str(AnyVal):
    def __init__(self):
        super().__init__()
        self.name = grammar.STR

    @staticmethod
    def type():
        raise NotImplementedError


class Bool(AnyVal):
    def __init__(self):
        super().__init__()
        self.name = grammar.BOOL

    @staticmethod
    def type():
        return "ir.IntType(1)"


class Bytes(AnyVal):
    def __init__(self):
        super().__init__()
        self.name = grammar.BYTES

    @staticmethod
    def type():
        raise NotImplementedError


class Collection(Any):
    def __init__(self):
        super().__init__()
        self.name = None


class List(Collection):
    def __init__(self):
        super().__init__()
        self.name = grammar.LIST

    @staticmethod
    def type():
        raise NotImplementedError


class Set(Collection):
    def __init__(self):
        super().__init__()
        self.name = grammar.SET

    @staticmethod
    def type():
        raise NotImplementedError


class Dict(Collection):
    def __init__(self):
        super().__init__()
        self.name = grammar.DICT

    @staticmethod
    def type():
        raise NotImplementedError


class Enum(Collection):
    def __init__(self):
        super().__init__()
        self.name = grammar.ENUM

    @staticmethod
    def type():
        raise NotImplementedError


class Struct(Collection):
    def __init__(self):
        super().__init__()
        self.name = grammar.STRUCT

    @staticmethod
    def type():
        raise NotImplementedError


class AnyRef(Any):
    def __init__(self):
        super().__init__()
        self.name = None


class Func(AnyRef):
    def __init__(self):
        super().__init__()
        self.name = grammar.FUNC

    @staticmethod
    def type():
        return "ir.FunctionType"


# def get_type_cls(cls):
# 	import sys
# 	import inspect
# 	for name, obj in inspect.getmembers(sys.modules[__name__]):
# 		if inspect.isclass(obj) and obj.__name__ == cls:
# 			return obj()
