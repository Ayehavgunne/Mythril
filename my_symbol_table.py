from collections import OrderedDict
from decimal import Decimal
from enum import Enum
from my_ast import Type
from my_grammar import *


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
LIST_BUILTIN = BuiltinTypeSymbol(LIST)
TUPLE_BUILTIN = BuiltinTypeSymbol(TUPLE)
DICT_BUILTIN = BuiltinTypeSymbol(DICT)
ENUM_BUILTIN = BuiltinTypeSymbol(ENUM)
FUNC_BUILTIN = BuiltinTypeSymbol(FUNC)
NULLTYPE_BUILTIN = BuiltinTypeSymbol(NULLTYPE)


class VarSymbol(Symbol):
	def __init__(self, name, var_type):
		super().__init__(name, var_type)
		self.accessed = False
		self.val_assigned = False

	def __str__(self):
		return '<{name}:{type}>'.format(name=self.name, type=self.type)

	__repr__ = __str__


class FuncSymbol(Symbol):
	def __init__(self, name, return_type, parameters, body, symtable_builder):
		super().__init__(name, return_type)
		self.parameters = parameters
		self.body = body
		self.symtab_builder = symtable_builder
		self.symtab_builder.visit(self.body)
		self.accessed = False

	def __str__(self):
		return '<{name}:{type} ({params})>'.format(name=self.name, type=self.type, params=', '.join('{}:{}'.format(key, value.value) for key, value in self.parameters.items()))

	__repr__ = __str__


class SymbolTable(object):
	def __init__(self):
		self._symbols = OrderedDict()
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
		self.define(LIST_BUILTIN)
		self.define(TUPLE_BUILTIN)
		self.define(DICT_BUILTIN)
		self.define(ENUM_BUILTIN)
		self.define(FUNC_BUILTIN)
		self.define(NULLTYPE_BUILTIN)

	def __str__(self):
		s = 'Symbols: {symbols}'.format(
			symbols=[value for value in self._symbols.values()]
		)
		return s

	__repr__ = __str__

	@property
	def unvisited_symbols(self):
		return [sym_name for sym_name, sym_val in self._symbols.items() if not isinstance(sym_val, BuiltinTypeSymbol) and not sym_val.accessed]

	def define(self, symbol):
		self._symbols[symbol.name] = symbol

	def lookup(self, name):
		symbol = self._symbols.get(name)
		return symbol

	def infer_type(self, value):
		if isinstance(value, BuiltinTypeSymbol):
			return value
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