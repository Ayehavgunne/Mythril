from llvmlite import ir
from mythril.grammar import *


class Any:
	def __init__(self):
		self.name = ANY

	def __str__(self):
		return '<{}>'.format(self.name)

	__repr__ = __str__


class Number(Any):
	def __init__(self):
		super().__init__()
		self.name = None


class Bool(Number):
	def __init__(self):
		super().__init__()
		self.name = BOOL

	@staticmethod
	def type():
		return ir.IntType(1)


class Int(Number):
	def __init__(self):
		super().__init__()
		self.name = INT

	@staticmethod
	def type():
		return ir.IntType(64)


class Int8(Number):
	def __init__(self):
		super().__init__()
		self.name = INT8

	@staticmethod
	def type():
		return ir.IntType(8)


class Int16(Number):
	def __init__(self):
		super().__init__()
		self.name = INT16

	@staticmethod
	def type():
		return ir.IntType(16)


class Int32(Number):
	def __init__(self):
		super().__init__()
		self.name = INT32

	@staticmethod
	def type():
		return ir.IntType(32)


class Int64(Number):
	def __init__(self):
		super().__init__()
		self.name = INT64

	@staticmethod
	def type():
		return ir.IntType(64)


class Int128(Number):
	def __init__(self):
		super().__init__()
		self.name = INT128

	@staticmethod
	def type():
		return ir.IntType(128)


class Dec(Number):
	def __init__(self):
		super().__init__()
		self.name = DEC

	@staticmethod
	def type():
		return ir.DoubleType()  # TODO: temorarily making Decimal a DoubleType till find (or make) a better representation


class Float(Number):
	def __init__(self):
		super().__init__()
		self.name = FLOAT

	@staticmethod
	def type():
		return ir.FloatType()


class Complex(Number):
	def __init__(self):
		super().__init__()
		self.name = COMPLEX

	@staticmethod
	def type():
		raise NotImplementedError


class Bytes(Any):
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


class Str(Array):
	def __init__(self):
		super().__init__()
		self.name = STR


class List(Collection):
	def __init__(self):
		super().__init__()
		self.name = LIST

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


class Func(Any):
	def __init__(self):
		super().__init__()
		self.name = FUNC

	@staticmethod
	def type():
		return ir.FunctionType


class Class(Struct):
	def __init__(self):
		super().__init__()
		self.name = CLASS

	@staticmethod
	def type():
		raise NotImplementedError

# def get_type_cls(cls):
# 	import sys
# 	import inspect
# 	for name, obj in inspect.getmembers(sys.modules[__name__]):
# 		if inspect.isclass(obj) and obj.__name__ == cls:
# 			return obj()
