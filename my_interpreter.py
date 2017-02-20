from decimal import Decimal
from enum import Enum
from my_visitor import NodeVisitor
from my_ast import Null
from my_ast import Return
from my_ast import VarDecl
from my_ast import Var
from my_grammar import *


class Interpreter(NodeVisitor):
	def __init__(self):
		self._scope = [{}]

	@property
	def top_scope(self):
		return self._scope[-1]

	@property
	def second_scope(self):
		return self._scope[-2]

	def new_scope(self):
		self._scope.append({})

	def drop_top_scope(self):
		self._scope.pop()

	def visit_program(self, node):
		self.visit(node.block)

	def visit_compound(self, node):
		for child in node.children:
			self.visit(child)

	def visit_vardecl(self, node):
		self.top_scope[node.var_node.value] = Null()

	def visit_type(self, node):
		pass

	def visit_noop(self, node):
		pass

	def visit_comparison(self, node):
		comp = node.comp
		if isinstance(comp, Var):
			result = self.top_scope[comp.value]
		elif comp.op.value == EQUALS:
			result = self.visit(comp.left) == self.visit(comp.right)
		elif comp.op.value == NOT_EQUALS:
			result = self.visit(comp.left) != self.visit(comp.right)
		elif comp.op.value == LESS_THAN:
			result = self.visit(comp.left) < self.visit(comp.right)
		elif comp.op.value == LESS_THAN_OR_EQUAL_TO:
			result = self.visit(comp.left) <= self.visit(comp.right)
		elif comp.op.value == GREATER_THAN:
			result = self.visit(comp.left) > self.visit(comp.right)
		elif comp.op.value == GREATER_THAN_OR_EQUAL_TO:
			result = self.visit(comp.left) >= self.visit(comp.right)
		else:
			raise SyntaxError('Unknown comparison operator: {}'.format(comp.op.value))
		if result is True:
			if node.op.value == WHILE:
				self.visit(node.block)
				self.visit_comparison(node)
			elif node.op.value == IF:
				self.visit(node.block)
		elif node.alt_block:
			self.visit(node.alt_block)

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
			elif cast_type == FLOAT:
				return float(self.visit(node.left))
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
		if op == PLUS_ASSIGN:
			self.top_scope[var_name] += self.visit(node.right)
		elif op == MINUS_ASSIGN:
			self.top_scope[var_name] -= self.visit(node.right)
		elif op == MUL_ASSIGN:
			self.top_scope[var_name] *= self.visit(node.right)
		elif op == FLOORDIV_ASSIGN:
			self.top_scope[var_name] //= self.visit(node.right)
		elif op == DIV_ASSIGN:
			self.top_scope[var_name] /= self.visit(node.right)
		elif op == MOD_ASSIGN:
			self.top_scope[var_name] %= self.visit(node.right)
		elif op == POWER_ASSIGN:
			self.top_scope[var_name] **= self.visit(node.right)

	def visit_var(self, node):
		var_name = node.value
		return self.top_scope[var_name]

	def visit_funcdecl(self, node):
		self.top_scope[node.name.value] = node

	def visit_funccall(self, node):
		func = self.top_scope[node.name.value]
		func.args = node.arguments
		self.new_scope()
		for x, key in enumerate(func.parameters.keys()):
			self.top_scope[key] = self.second_scope[node.arguments[x].value]
		self.visit(func.body)
		for key in func.parameters.keys():
			del self.top_scope[key]
		return_var = None
		for child in reversed(func.body.children):
			if isinstance(child, Return):
				if child.value.token.type == NAME:
					return_var = self.top_scope.pop(child.value.value)
				else:
					return_var = child.value.value
				break
		if not return_var and func.return_type.value != VOID:
			raise TypeError
		self.drop_top_scope()
		return return_var

	def visit_return(self, node): # TODO: What if function is returning a type???
		if node.value.token.type != NAME:
			return node.value.value
		return self.top_scope[node.value.value]

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
			return NotImplementedError

	@staticmethod
	def visit_num(node):
		return node.value

	@staticmethod
	def visit_str(node):
		return node.value

	def interpret(self, tree):
		return self.visit(tree)


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
	for variable_name in sorted(interpreter.top_scope.keys()):
		string += '{}: {}, '.format(repr(variable_name), repr(interpreter.top_scope[variable_name]))
	print('{' + string[:-2] + '}')