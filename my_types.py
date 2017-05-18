from llvmlite import ir
from my_grammar import *


class Any:
	def __init__(self):
		self.name = ANY

	def __str__(self):
		return '<{}>'.format(self.name)

	__repr__ = __str__


class AnyVal(Any):
	def __init__(self):
		super().__init__()
		self.name = None


class Int(AnyVal):
	def __init__(self):
		super().__init__()
		self.name = INT

	@staticmethod
	def type():
		return lambda: ir.IntType(64)


class Int8(AnyVal):
	def __init__(self):
		super().__init__()
		self.name = INT8

	@staticmethod
	def type():
		return lambda: ir.IntType(8)


class Int32(AnyVal):
	def __init__(self):
		super().__init__()
		self.name = INT32

	@staticmethod
	def type():
		return lambda: ir.IntType(32)


class Int64(AnyVal):
	def __init__(self):
		super().__init__()
		self.name = INT64

	@staticmethod
	def type():
		return lambda: ir.IntType(64)


class Int128(AnyVal):
	def __init__(self):
		super().__init__()
		self.name = INT128

	@staticmethod
	def type():
		return lambda: ir.IntType(128)


class Dec(AnyVal):
	def __init__(self):
		super().__init__()
		self.name = DEC

	@staticmethod
	def type():
		return ir.DoubleType  # TODO: temorarily making Decimal a DoubleType till find (or make) a better representation


class Float(AnyVal):
	def __init__(self):
		super().__init__()
		self.name = FLOAT

	@staticmethod
	def type():
		return lambda: ir.FloatType


class Complex(AnyVal):
	def __init__(self):
		super().__init__()
		self.name = COMPLEX

	@staticmethod
	def type():
		raise NotImplementedError


class Str(AnyVal):
	def __init__(self):
		super().__init__()
		self.name = STR

	@staticmethod
	def type():
		raise NotImplementedError


class Bool(AnyVal):
	def __init__(self):
		super().__init__()
		self.name = BOOL

	@staticmethod
	def type():
		return lambda: ir.IntType(1)


class Bytes(AnyVal):
	def __init__(self):
		super().__init__()
		self.name = BYTES

	@staticmethod
	def type():
		raise NotImplementedError


class Collection(Any):
	def __init__(self):
		super().__init__()
		self.name = None


class Array(Collection):
	def __init__(self):
		super().__init__()
		self.name = ARRAY

	@staticmethod
	def type(element_type, count):
		return ir.ArrayType(element_type, count)


class List(Collection):
	def __init__(self):
		super().__init__()
		self.name = LIST

	@staticmethod
	def type():
		raise NotImplementedError


class Tuple(Collection):
	def __init__(self):
		super().__init__()
		self.name = TUPLE

	@staticmethod
	def type():
		raise NotImplementedError


class Set(Collection):
	def __init__(self):
		super().__init__()
		self.name = SET

	@staticmethod
	def type():
		raise NotImplementedError


class Dict(Collection):
	def __init__(self):
		super().__init__()
		self.name = DICT

	@staticmethod
	def type():
		raise NotImplementedError


class Enum(Collection):
	def __init__(self):
		super().__init__()
		self.name = ENUM

	@staticmethod
	def type():
		raise NotImplementedError


class Struct(Collection):
	def __init__(self):
		super().__init__()
		self.name = STRUCT

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
		self.name = FUNC

	@staticmethod
	def type():
		return ir.FunctionType


def get_type_cls(cls):
	import sys
	import inspect
	for name, obj in inspect.getmembers(sys.modules[__name__]):
		if inspect.isclass(obj) and obj.__name__ == cls:
			return obj()
