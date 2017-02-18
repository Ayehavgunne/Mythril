from collections import OrderedDict
from decimal import Decimal
from enum import Enum
from ast import Type
from ast import Null
from grammar import *


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


class VarSymbol(Symbol):
	def __init__(self, name, var_type):
		super().__init__(name, var_type)

	def __str__(self):
		return '<{name}:{type}>'.format(name=self.name, type=self.type)

	__repr__ = __str__


class SymbolTable(object):
	def __init__(self):
		self._symbols = OrderedDict()
		self._init_builtins()

	def _init_builtins(self):
		self.define(BuiltinTypeSymbol(ANY))
		self.define(BuiltinTypeSymbol(INT))
		self.define(BuiltinTypeSymbol(DEC))
		self.define(BuiltinTypeSymbol(COMPLEX))
		self.define(BuiltinTypeSymbol(BOOL))
		self.define(BuiltinTypeSymbol(BYTES))
		self.define(BuiltinTypeSymbol(STR))
		self.define(BuiltinTypeSymbol(LIST))
		self.define(BuiltinTypeSymbol(TUPLE))
		self.define(BuiltinTypeSymbol(DICT))
		self.define(BuiltinTypeSymbol(ENUM))
		self.define(BuiltinTypeSymbol(FUNC))
		self.define(BuiltinTypeSymbol(NULLTYPE))

	def __str__(self):
		s = 'Symbols: {symbols}'.format(
			symbols=[value for value in self._symbols.values()]
		)
		return s

	__repr__ = __str__

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
				return self.lookup('int')
			elif isinstance(value, Decimal):
				return self.lookup('dec')
			elif isinstance(value, complex):
				return self.lookup('complex')
			elif isinstance(value, str):
				return self.lookup('str')
			elif isinstance(value, bool):
				return self.lookup('bool')
			elif isinstance(value, bytes):
				return self.lookup('byte')
			elif isinstance(value, list):
				return self.lookup('list')
			elif isinstance(value, tuple):
				return self.lookup('tuple')
			elif isinstance(value, dict):
				return self.lookup('dict')
			elif isinstance(value, Enum):
				return self.lookup('enum')
			elif callable(value):
				return self.lookup('func')
			elif value is None:
				return self.lookup('nulltype')
			else:
				raise TypeError('Type not recognized: {}'.format(value))


class NodeVisitor(object):
	def visit(self, node):
		method_name = 'visit_' + type(node).__name__.lower()
		visitor = getattr(self, method_name, self.generic_visit)
		return visitor(node)

	@staticmethod
	def generic_visit(node):
		raise Exception('No visit_{} method'.format(type(node).__name__))


class SymbolTableBuilder(NodeVisitor):
	def __init__(self):
		self.symtab = SymbolTable()

	def visit_block(self, node):
		for declaration in node.declarations:
			self.visit(declaration)
		self.visit(node.compound_statement)

	def visit_program(self, node):
		self.visit(node.block)

	def visit_binop(self, node):
		if node.op.value == '::':
			return self.symtab.infer_type(node.right)
		else:
			left = self.visit(node.left)
			right = self.visit(node.right)
			left_type = self.symtab.infer_type(left)
			right_type = self.symtab.infer_type(right)
			if right_type is left_type or left_type is self.symtab.lookup('any') or right_type is self.symtab.lookup('any'):
				return left_type
			else:
				raise TypeError

	def visit_comparison(self, node):
		self.visit(node.comp)

	def visit_num(self, node):
		return self.symtab.infer_type(node.value)

	def visit_str(self, node):
		return self.symtab.infer_type(node.value)

	@staticmethod
	def visit_type(node):
		return node.value

	def visit_assign(self, node):
		var_name = node.left.value
		value = self.visit(node.right)
		if not self.symtab.lookup(var_name):
			self.symtab.define(VarSymbol(var_name, value))

	def visit_opassign(self, node):
		left = self.visit(node.left)
		right = self.visit(node.right)
		left_type = self.symtab.infer_type(left)
		right_type = self.symtab.infer_type(right)
		if right_type is left_type or left_type is self.symtab.lookup('any') or right_type is self.symtab.lookup('any'):
			return left_type
		else:
			raise TypeError

	def visit_var(self, node):
		var_name = node.value
		val = self.symtab.lookup(var_name)
		if val is None:
			raise NameError(repr(var_name))
		else:
			return val

	def visit_unaryop(self, node):
		self.visit(node.expr)

	def visit_compound(self, node):
		for child in node.children:
			self.visit(child)

	def visit_noop(self, node):
		pass

	def visit_vardecl(self, node):
		type_name = node.type_node.value
		type_symbol = self.symtab.lookup(type_name)
		var_name = node.var_node.value
		var_symbol = VarSymbol(var_name, type_symbol)
		self.symtab.define(var_symbol)


class Interpreter(NodeVisitor):
	def __init__(self):
		self.GLOBAL_SCOPE = {}

	def visit_program(self, node):
		self.visit(node.block)

	def visit_compound(self, node):
		for child in node.children:
			self.visit(child)

	def visit_vardecl(self, node):
		self.GLOBAL_SCOPE[node.var_node.value] = Null()

	def visit_type(self, node):
		pass

	def visit_noop(self, node):
		pass

	def visit_comparison(self, node):
		comp = node.comp
		op = comp.op.value
		if op == EQUALS:
			result = self.visit(comp.left) == self.visit(comp.right)
		elif op == NOT_EQUALS:
			result = self.visit(comp.left) != self.visit(comp.right)
		elif op == LESS_THAN:
			result = self.visit(comp.left) < self.visit(comp.right)
		elif op == LESS_THAN_OR_EQUAL_TO:
			result = self.visit(comp.left) <= self.visit(comp.right)
		elif op == GREATER_THAN:
			result = self.visit(comp.left) > self.visit(comp.right)
		elif op == GREATER_THAN_OR_EQUAL_TO:
			result = self.visit(comp.left) >= self.visit(comp.right)
		else:
			raise SyntaxError('Unknown comparison operator: {}'.format(op))
		if result:
			if node.op.value == WHILE:
				self.visit(node.block)
				self.visit_comparison(node)
			elif node.op.value == IF:
				self.visit(node.block)

	def visit_binop(self, node):
		op = node.op.value
		if op == PLUS:
			return self.visit(node.left) + self.visit(node.right)
		elif op == MINUS:
			return self.visit(node.left) - self.visit(node.right)
		elif op == MUL:
			return self.visit(node.left) * self.visit(node.right)
		elif op == FLOORDIV:
			return self.visit(node.left) // self.visit(node.right)
		elif op == DIV:
			return self.visit(node.left) / self.visit(node.right)
		elif op == MOD:
			return self.visit(node.left) % self.visit(node.right)
		elif op == POWER:
			return self.visit(node.left) ** self.visit(node.right)
		elif op == CAST:
			cast_type = node.right.value
			if cast_type == INT:
				return int(self.visit(node.left))
			elif cast_type == DEC:
				return Decimal(self.visit(node.left))
			elif cast_type == COMPLEX:
				return complex(self.visit(node.left))
			elif cast_type == STR:
				return str(self.visit(node.left))
			elif cast_type == BOOL:
				return bool(self.visit(node.left))
			elif cast_type == BYTES:
				return bytes(self.visit(node.left))
			elif cast_type == LIST:
				return list(self.visit(node.left))
			elif cast_type == TUPLE:
				return tuple(self.visit(node.left))
			elif cast_type == DICT:
				return dict(self.visit(node.left))
			elif cast_type == ENUM:
				return Enum(node.left.value, self.visit(node.left))
			elif cast_type in (ANY, FUNC, NULL):
				raise TypeError('Cannot cast to type {}'.format(cast_type))

	def visit_unaryop(self, node):
		op = node.op.value
		if op == PLUS:
			return +self.visit(node.expr)
		elif op == MINUS:
			return -self.visit(node.expr)

	def visit_assign(self, node):
		var_name = node.left.value
		self.GLOBAL_SCOPE[var_name] = self.visit(node.right)

	def visit_opassign(self, node):
		var_name = node.left.value
		op = node.op.value
		if op == PLUS_ASSIGN:
			self.GLOBAL_SCOPE[var_name] += self.visit(node.right)
		elif op == MINUS_ASSIGN:
			self.GLOBAL_SCOPE[var_name] -= self.visit(node.right)
		elif op == MUL_ASSIGN:
			self.GLOBAL_SCOPE[var_name] *= self.visit(node.right)
		elif op == FLOORDIV_ASSIGN:
			self.GLOBAL_SCOPE[var_name] //= self.visit(node.right)
		elif op == DIV_ASSIGN:
			self.GLOBAL_SCOPE[var_name] /= self.visit(node.right)
		elif op == MOD_ASSIGN:
			self.GLOBAL_SCOPE[var_name] %= self.visit(node.right)
		elif op == POWER_ASSIGN:
			self.GLOBAL_SCOPE[var_name] **= self.visit(node.right)

	def visit_var(self, node):
		var_name = node.value
		val = self.GLOBAL_SCOPE.get(var_name)
		if val is None:
			raise NameError(repr(var_name))
		else:
			return val

	@staticmethod
	def visit_num(node):
		return node.value

	@staticmethod
	def visit_str(node):
		return node.value

	def interpret(self, tree):
		return self.visit(tree)

if __name__ == '__main__':
	from lexer import Lexer
	from parser import Parser
	code = open('math.my').read()
	lexer = Lexer(code)
	parser = Parser(lexer)
	t = parser.parse()
	symtab_builder = SymbolTableBuilder()
	symtab_builder.visit(t)
	interpreter = Interpreter()
	interpreter.interpret(t)
	print(interpreter.GLOBAL_SCOPE)
