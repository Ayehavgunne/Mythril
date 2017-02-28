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


class Dec(AnyVal):
	def __init__(self):
		super().__init__()
		self.name = DEC


class Float(AnyVal):
	def __init__(self):
		super().__init__()
		self.name = FLOAT


class Complex(AnyVal):
	def __init__(self):
		super().__init__()
		self.name = COMPLEX


class Str(AnyVal):
	def __init__(self):
		super().__init__()
		self.name = STR


class Bool(AnyVal):
	def __init__(self):
		super().__init__()
		self.name = BOOL


class Bytes(AnyVal):
	def __init__(self):
		super().__init__()
		self.name = BYTES


class Collection(Any):
	def __init__(self):
		super().__init__()
		self.name = None


class Array(Collection):
	def __init__(self):
		super().__init__()
		self.name = ARRAY


class List(Collection):
	def __init__(self):
		super().__init__()
		self.name = LIST


class Tuple(Collection):
	def __init__(self):
		super().__init__()
		self.name = TUPLE


class Set(Collection):
	def __init__(self):
		super().__init__()
		self.name = SET


class Dict(Collection):
	def __init__(self):
		super().__init__()
		self.name = DICT


class Enum(Collection):
	def __init__(self):
		super().__init__()
		self.name = ENUM


class AnyRef(Any):
	def __init__(self):
		super().__init__()
		self.name = None


class Func(AnyRef):
	def __init__(self):
		super().__init__()
		self.name = FUNC


class NullType(Any):
	def __init__(self):
		super().__init__()
		self.name = NULLTYPE


def get_type_cls(cls):
	import sys
	import inspect
	for name, obj in inspect.getmembers(sys.modules[__name__]):
		if inspect.isclass(obj) and obj.__name__ == cls:
			return obj()