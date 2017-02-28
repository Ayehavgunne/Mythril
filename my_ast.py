from my_grammar import *


class AST(object):
	def __str__(self):
		return '(' + ' '.join(str(value) for key, value in self.__dict__.items() if not key.startswith("__")) + ')'

	__repr__ = __str__


class Program(AST):
	def __init__(self, block):
		self.block = block


class VarDecl(AST):
	def __init__(self, var_node, type_node):
		self.var_node = var_node
		self.type_node = type_node
		self.read_only = False


class Compound(AST):
	def __init__(self):
		self.children = []

	def __str__(self):
		return '\n'.join(str(child) for child in self.children)

	__repr__ = __str__


class FuncDecl(AST):
	def __init__(self, name, return_type, parameters, body):
		self.name = name
		self.return_type = return_type
		self.parameters = parameters
		self.body = body

	def __str__(self):
		return '<{name}:{type} ({params})>'.format(name=self.name.value, type=self.return_type.value, params=', '.join('{}:{}'.format(key, value.value) for key, value in self.parameters.items()))

	__repr__ = __str__


class AnonymousFunc(AST):
	def __init__(self, return_type, parameters, body):
		self.return_type = return_type
		self.parameters = parameters
		self.body = body

	def __str__(self):
		return '<Anonymous:{type} ({params})>'.format(type=self.return_type.value, params=', '.join('{}:{}'.format(key, value.value) for key, value in self.parameters.items()))

	__repr__ = __str__


class FuncCall(AST):
	def __init__(self, name, arguments):
		self.name = name
		self.arguments = arguments


class Return(AST):
	def __init__(self, value, parent=None):
		self.value = value
		self.parent = parent


class Assign(AST):
	def __init__(self, left, op, right):
		self.left = left
		self.op = op
		self.right = right


class OpAssign(AST):
	def __init__(self, left, op, right):
		self.left = left
		self.op = op
		self.right = right


class If(AST):
	def __init__(self, op, comps, blocks):
		self.op = op
		self.comps = comps
		self.blocks = blocks


class Else(AST):
	pass


class While(AST):
	def __init__(self, op, comp, block):
		self.op = op
		self.comp = comp
		self.block = block


class For(AST):
	def __init__(self, iterator, block, elements):
		self.iterator = iterator
		self.block = block
		self.elements = elements


class LoopBlock(AST):
	def __init__(self):
		self.children = []

	def __str__(self):
		return '\n'.join(str(child) for child in self.children)

	__repr__ = __str__


class Switch(AST):
	def __init__(self, value, cases):
		self.value = value
		self.cases = cases


class Case(AST):
	def __init__(self, value, block):
		self.value = value
		self.block = block


class Break(AST):
	def __str__(self):
		return BREAK

	__repr__ = __str__


class Continue(AST):
	def __str__(self):
		return CONTINUE

	__repr__ = __str__


class Pass(AST):
	def __str__(self):
		return CONTINUE

	__repr__ = __str__


class BinOp(AST):
	def __init__(self, left, op, right):
		self.left = left
		self.op = op
		self.right = right


class UnaryOp(AST):
	def __init__(self, op, expr):
		self.op = op
		self.expr = expr


class Range(AST):
	def __init__(self, left, op, right):
		self.left = left
		self.op = op
		self.right = right


class CollectionAccess(AST):
	def __init__(self, collection, key):
		self.collection = collection
		self.key = key


class Type(AST):
	def __init__(self, token, func_ret_type=None):
		self.token = token
		self.value = token.value
		self.func_ret_type = func_ret_type


class Void(AST):
	value = VOID


class Null(AST):
	def __str__(self):
		return 'NULL'

	__repr__ = __str__


class Var(AST):
	def __init__(self, token, read_only=False):
		self.token = token
		self.value = token.value
		self.read_only = read_only


class Constant(AST):
	def __init__(self, token):
		self.token = token
		self.value = token.value


class Num(AST):
	def __init__(self, token):
		self.token = token
		self.value = token.value


class Str(AST):
	def __init__(self, token):
		self.token = token
		self.value = token.value


class Collection(AST):
	def __init__(self, token, read_only, *items):
		self.token = token
		self.read_only = read_only
		self.items = items


class HashMap(AST):
	def __init__(self, token, items):
		self.token = token
		self.items = items


class NoOp(AST):
	def __str__(self):
		return 'noop'

	__repr__ = __str__