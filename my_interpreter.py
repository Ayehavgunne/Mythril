from decimal import Decimal
from enum import Enum
from my_visitor import NodeVisitor
from my_ast import Null
from my_ast import VarDecl
from my_ast import NoOp
from my_grammar import *


class Interpreter(NodeVisitor):
	def __init__(self):
		self._scope = [{}]
		self.create_builtin_funcs()

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

	def define(self, key, value, level=0):
		level = (len(self._scope) - level) - 1
		self._scope[level][key] = value

	def new_scope(self):
		self._scope.append({})

	def drop_top_scope(self):
		self._scope.pop()

	def visit_program(self, node):
		self.visit(node.block)

	def visit_compound(self, node):
		res = None
		for child in node.children:
			temp = self.visit(child)
			if temp is not None:
				res = temp
		return res

	def visit_vardecl(self, node):
		self.top_scope[node.var_node.value] = Null()

	def visit_type(self, node):
		return self.search_scopes(node.value)

	def visit_noop(self, node):
		pass

	def visit_controlstructure(self, node):
		for x, comp in enumerate(node.comps):
			if self.visit(comp) is True:
				if node.op.value == WHILE:
					self.visit(node.blocks[x])
					self.visit_controlstructure(node)
				elif node.op.value == IF:
					return self.visit(node.blocks[x])
			elif isinstance(comp, NoOp):
				return self.visit(node.blocks[x])

	def visit_binop(self, node):
		op = node.op.value
		left = self.visit(node.left)
		right = self.visit(node.right)
		if op == PLUS:
			return left + right
		elif op == MINUS:
			return left - right
		elif op == MUL:
			return left * right
		elif op == FLOORDIV:
			return left // right
		elif op == DIV:
			return left / right
		elif op == MOD:
			return left % right
		elif op == POWER:
			return left ** right
		elif op == AND:
			return left and right
		elif op == OR:
			return left or right
		elif op == EQUALS:
			return left == right
		elif op == NOT_EQUALS:
			return left != right
		elif op == LESS_THAN:
			return left < right
		elif op == LESS_THAN_OR_EQUAL_TO:
			return left <= right
		elif op == GREATER_THAN:
			return left > right
		elif op == GREATER_THAN_OR_EQUAL_TO:
			return left >= right
		elif op == CAST:
			cast_type = node.right.value
			if cast_type == INT:
				return int(left)
			elif cast_type == DEC:
				return Decimal(left)
			elif cast_type == FLOAT:
				return float(left)
			elif cast_type == COMPLEX:
				return complex(left)
			elif cast_type == STR:
				return str(left)
			elif cast_type == BOOL:
				return bool(left)
			elif cast_type == BYTES:
				return bytes(left)
			elif cast_type == LIST:
				return list(left)
			elif cast_type == TUPLE:
				return tuple(left)
			elif cast_type == DICT:
				return dict(left)
			elif cast_type == ENUM:
				return Enum(left.value, left)
			elif cast_type in (ANY, FUNC, NULL):
				raise TypeError('Cannot cast to type {}'.format(cast_type))

	def visit_unaryop(self, node):
		op = node.op.value
		if op == PLUS:
			return +self.visit(node.expr)
		elif op == MINUS:
			return -self.visit(node.expr)
		elif op == NOT:
			return not self.visit(node.expr)

	def visit_assign(self, node):
		if isinstance(node.left, VarDecl):
			var_name = node.left.var_node.value
			if node.left.type_node.value == FLOAT:
				node.right.value = float(node.right.value)
		else:
			var_name = node.left.value
			var_value = self.top_scope.get(var_name)
			if var_value and isinstance(var_value, float):
				node.right.value = float(node.right.value)
		self.top_scope[var_name] = self.visit(node.right)

	def visit_opassign(self, node):
		var_name = node.left.value
		op = node.op.value
		right = self.visit(node.right)
		if op == PLUS_ASSIGN:
			self.top_scope[var_name] += right
		elif op == MINUS_ASSIGN:
			self.top_scope[var_name] -= right
		elif op == MUL_ASSIGN:
			self.top_scope[var_name] *= right
		elif op == FLOORDIV_ASSIGN:
			self.top_scope[var_name] //= right
		elif op == DIV_ASSIGN:
			self.top_scope[var_name] /= right
		elif op == MOD_ASSIGN:
			self.top_scope[var_name] %= right
		elif op == POWER_ASSIGN:
			self.top_scope[var_name] **= right

	def visit_var(self, node):
		return self.search_scopes(node.value)

	def visit_funcdecl(self, node):
		self.top_scope[node.name.value] = node

	def visit_funccall(self, node):
		if node.name.value in BUILTIN_FUNCTIONS:
			args = []
			for arg in node.arguments:
				args.append(self.visit(arg))
			self.search_scopes(node.name.value)(*args)
		else:
			func = self.search_scopes(node.name.value)
			func.args = node.arguments
			self.new_scope()
			for x, key in enumerate(func.parameters.keys()):
				self.top_scope[key] = self.visit(node.arguments[x])
			return_var = self.visit(func.body)
			if return_var is None and func.return_type.value != VOID:
				raise TypeError
			self.drop_top_scope()
			return return_var

	def visit_return(self, node):
		return self.visit(node.value)

	@staticmethod
	def visit_constant(node):
		if node.value == TRUE:
			return True
		elif node.value == FALSE:
			return False
		elif node.value == NAN:
			return Decimal(NAN)
		elif node.value == INF:
			return Decimal(INF)
		elif node.value == NEGATIVE_INF:
			return Decimal(NEGATIVE_INF)
		else:
			raise NotImplementedError

	@staticmethod
	def visit_num(node):
		return node.value

	@staticmethod
	def visit_str(node):
		return node.value

	def visit_collection(self, node):
		items = []
		for item in node.items:
			items.append(self.visit(item))
		if node.read_only:
			return tuple(items)
		return items

	def visit_hashmap(self, node):
		types = {}
		for key, val in node.items.items():
			types[key] = self.visit(val)
		return types

	def interpret(self, tree):
		return self.visit(tree)

	def create_builtin_funcs(self):
		for func in BUILTIN_FUNCTIONS:
			if func == 'print':
				self.top_scope[func] = print

if __name__ == '__main__':
	from my_lexer import Lexer
	from my_parser import Parser
	from my_symbol_table_builder import SymbolTableBuilder
	code = open('math.my').read()
	lexer = Lexer(code)
	parser = Parser(lexer)
	t = parser.parse()
	symtab_builder = SymbolTableBuilder()
	symtab_builder.build(t)
	interpreter = Interpreter()
	interpreter.interpret(t)
	string = ''
	# for variable_name in sorted(interpreter.top_scope.keys()):
	# 	string += '{}: {}, '.format(repr(variable_name), repr(interpreter.top_scope[variable_name]))
	# print('{' + string[:-2] + '}')