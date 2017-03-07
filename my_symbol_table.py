from collections import OrderedDict
from decimal import Decimal
from enum import Enum
from my_ast import Type
from my_types import *


class Symbol(object):
	def __init__(self, name, symbol_type=None):
		self.name = name
		self.type = symbol_type


class BuiltinTypeSymbol(Symbol):
	def __init__(self, name):
		super().__init__(name)

	def __str__(self):
		return self.name

	__repr__ = __str__


ANY_BUILTIN = BuiltinTypeSymbol(ANY)
INT_BUILTIN = BuiltinTypeSymbol(INT)
DEC_BUILTIN = BuiltinTypeSymbol(DEC)
FLOAT_BUILTIN = BuiltinTypeSymbol(FLOAT)
COMPLEX_BUILTIN = BuiltinTypeSymbol(COMPLEX)
BOOL_BUILTIN = BuiltinTypeSymbol(BOOL)
BYTES_BUILTIN = BuiltinTypeSymbol(BYTES)
STR_BUILTIN = BuiltinTypeSymbol(STR)
ARRAY_BUILTIN = BuiltinTypeSymbol(ARRAY)
LIST_BUILTIN = BuiltinTypeSymbol(LIST)
TUPLE_BUILTIN = BuiltinTypeSymbol(TUPLE)
DICT_BUILTIN = BuiltinTypeSymbol(DICT)
ENUM_BUILTIN = BuiltinTypeSymbol(ENUM)
FUNC_BUILTIN = BuiltinTypeSymbol(FUNC)
NULLTYPE_BUILTIN = BuiltinTypeSymbol(NULLTYPE)


class VarSymbol(Symbol):
	def __init__(self, name, var_type, read_only=False):
		super().__init__(name, var_type)
		self.accessed = False
		self.val_assigned = False
		self.read_only = read_only

	def __str__(self):
		return '<{name}:{type}>'.format(name=self.name, type=self.type)

	__repr__ = __str__


class CollectionSymbol(Symbol):
	def __init__(self, name, var_type, item_types):
		super().__init__(name, var_type)
		self.item_types = item_types
		self.accessed = False
		self.val_assigned = False


class FuncSymbol(Symbol):
	def __init__(self, name, return_type, parameters, body):
		super().__init__(name, return_type)
		self.parameters = parameters
		self.body = body
		self.accessed = False
		self.val_assigned = True

	def __str__(self):
		return '<{name}:{type} ({params})>'.format(name=self.name, type=self.type, params=', '.join('{}:{}'.format(key, value.value) for key, value in self.parameters.items()))

	__repr__ = __str__


class TypeSymbol(Symbol):
	def __init__(self, name, types):
		super().__init__(name, types)
		self.accessed = False

	def __str__(self):
		return '<{name}:{type}>'.format(name=self.name, type=self.type)

	__repr__ = __str__


class BuiltinFuncSymbol(Symbol):
	def __init__(self, name, return_type, parameters, body):
		super().__init__(name, return_type)
		self.parameters = parameters
		self.body = body
		self.accessed = False
		self.val_assigned = True

	def __str__(self):
		return '<{name}:{type} ({params})>'.format(name=self.name, type=self.type, params=', '.join('{}:{}'.format(key, value.value) for key, value in self.parameters.items()))

	__repr__ = __str__


print_parameters = OrderedDict()
print_parameters['objects'] = []
PRINT_BUILTIN = BuiltinFuncSymbol('print', NULLTYPE_BUILTIN, print_parameters, print)


class SymbolTable(object):
	def __init__(self):
		self._scope = [OrderedDict()]
		self._init_builtins()

	def _init_builtins(self):
		self.define(ANY_BUILTIN)
		self.define(INT_BUILTIN)
		self.define(DEC_BUILTIN)
		self.define(FLOAT_BUILTIN)
		self.define(COMPLEX_BUILTIN)
		self.define(BOOL_BUILTIN)
		self.define(BYTES_BUILTIN)
		self.define(STR_BUILTIN)
		self.define(ARRAY_BUILTIN)
		self.define(LIST_BUILTIN)
		self.define(TUPLE_BUILTIN)
		self.define(DICT_BUILTIN)
		self.define(ENUM_BUILTIN)
		self.define(FUNC_BUILTIN)
		self.define(NULLTYPE_BUILTIN)
		self.define(PRINT_BUILTIN)

	def __str__(self):
		s = 'Symbols: {symbols}'.format(
			symbols=self.symbols
		)
		return s

	__repr__ = __str__

	@property
	def symbols(self):
		return [value for scope in self._scope for value in scope.values()]

	@property
	def keys(self):
		return [key for scope in self._scope for key in scope.keys()]

	@property
	def items(self):
		return [(key, value) for scope in self._scope for key, value in scope.items()]

	@property
	def top_scope(self):
		return self._scope[-1] if len(self._scope) >= 1 else None

	@property
	def second_scope(self):
		return self._scope[-2] if len(self._scope) >= 2 else None

	def search_scopes(self, name):
		for scope in reversed(self._scope):
			if name in scope:
				return scope[name]

	def new_scope(self):
		self._scope.append(OrderedDict())

	def drop_top_scope(self):
		self._scope.pop()

	@property
	def unvisited_symbols(self):
		return [sym_name for sym_name, sym_val in self.items if not isinstance(sym_val, (BuiltinTypeSymbol, BuiltinFuncSymbol)) and not sym_val.accessed]

	def define(self, symbol, level=0):
		level = (len(self._scope) - level) - 1
		self._scope[level][symbol.name] = symbol

	def lookup(self, name):
		return self.search_scopes(name)

	def infer_type(self, value):
		if isinstance(value, BuiltinTypeSymbol):
			return value
		if isinstance(value, FuncSymbol):
			return self.lookup(FUNC)
		elif isinstance(value, VarSymbol):
			return value.type
		elif isinstance(value, Type):
			return self.lookup(value.value)
		else:
			if isinstance(value, int):
				return self.lookup(INT)
			elif isinstance(value, Decimal):
				return self.lookup(DEC)
			elif isinstance(value, float):
				return self.lookup(FLOAT)
			elif isinstance(value, complex):
				return self.lookup(COMPLEX)
			elif isinstance(value, str):
				return self.lookup(STR)
			elif isinstance(value, bool):
				return self.lookup(BOOL)
			elif isinstance(value, bytes):
				return self.lookup(BYTES)
			elif isinstance(value, list):
				return self.lookup(LIST)
			elif isinstance(value, tuple):
				return self.lookup(TUPLE)
			elif isinstance(value, dict):
				return self.lookup(DICT)
			elif isinstance(value, Enum):
				return self.lookup(ENUM)
			elif callable(value):
				return self.lookup(FUNC)
			elif value is None:
				return self.lookup(NULLTYPE)
			else:
				raise TypeError('Type not recognized: {}'.format(value))