from collections import OrderedDict
from ast import PLUS, MINUS, MUL, DIV, FLOORDIV, Null, Type


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
		self.define(BuiltinTypeSymbol('any'))
		self.define(BuiltinTypeSymbol('int'))
		self.define(BuiltinTypeSymbol('dec'))
		self.define(BuiltinTypeSymbol('complex'))
		self.define(BuiltinTypeSymbol('bool'))
		self.define(BuiltinTypeSymbol('byte'))
		self.define(BuiltinTypeSymbol('str'))
		self.define(BuiltinTypeSymbol('list'))
		self.define(BuiltinTypeSymbol('tuple'))
		self.define(BuiltinTypeSymbol('dict'))
		self.define(BuiltinTypeSymbol('enum'))
		self.define(BuiltinTypeSymbol('func'))
		self.define(BuiltinTypeSymbol('null'))

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

	# def assign_val(self, symbol, value):
	# 	self._symbols[symbol] = value

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
			elif isinstance(value, float):
				return self.lookup('dec')
			else:
				return self.lookup('any')


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
			if right_type is left_type:
				return left_type
			else:
				raise TypeError

	def visit_num(self, node):
		return self.symtab.infer_type(node.value)

	@staticmethod
	def visit_type(node):
		return node.value

	def visit_assign(self, node):
		var_name = node.left.value
		value = self.visit(node.right)
		if not self.symtab.lookup(var_name):
			var_type = self.symtab.infer_type(value)
			self.symtab.define(VarSymbol(var_name, var_type))
		# self.symtab.assign_val(var_name, value)

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
	def __init__(self, par):
		self.parser = par
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

	def visit_binop(self, node):
		op = node.op.value
		if op == PLUS:
			return self.visit(node.left) + self.visit(node.right)
		elif op == MINUS:
			return self.visit(node.left) - self.visit(node.right)
		elif op == MUL:
			return self.visit(node.left) * self.visit(node.right)
		elif node.op.type == FLOORDIV:
			return self.visit(node.left) // self.visit(node.right)
		elif op == DIV:
			return self.visit(node.left) / self.visit(node.right)

	def visit_unaryop(self, node):
		op = node.op.value
		if op == PLUS:
			return +self.visit(node.expr)
		elif op == MINUS:
			return -self.visit(node.expr)

	def visit_assign(self, node):
		var_name = node.left.value
		self.GLOBAL_SCOPE[var_name] = self.visit(node.right)

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

	def interpret(self):
		return self.visit(self.parser.parse())

if __name__ == '__main__':
	from lexer import Lexer
	from parser import Parser
	lexer = Lexer(open('math.my').read())
	parser = Parser(lexer)
	tree = parser.parse()
	symtab_builder = SymbolTableBuilder()
	symtab_builder.visit(tree)
	# interpreter = Interpreter(parser)
	# result = interpreter.interpret()
	# print(interpreter.GLOBAL_SCOPE)
