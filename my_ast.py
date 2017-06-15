from my_grammar import *


class AST(object):
	def __str__(self):
		return '(' + ' '.join(str(value) for key, value in self.__dict__.items() if not key.startswith("__")) + ')'

	__repr__ = __str__


class Program(AST):
	def __init__(self, block):
		self.block = block


class VarDecl(AST):
	def __init__(self, var_node, type_node, line_num):
		self.var_node = var_node
		self.type_node = type_node
		self.read_only = False
		self.line_num = line_num


class Compound(AST):
	def __init__(self):
		self.children = []

	def __str__(self):
		return '\n'.join(str(child) for child in self.children)

	__repr__ = __str__


class FuncDecl(AST):
	def __init__(self, name, return_type, parameters, body, line_num, parameter_defaults=None, varargs=None):
		self.name = name
		self.return_type = return_type
		self.parameters = parameters
		self.parameter_defaults = parameter_defaults or {}
		self.varargs = varargs
		self.body = body
		self.line_num = line_num

	def __str__(self):
		return '<{name}:{type} ({params})>'.format(name=self.name.value, type=self.return_type.value, params=', '.join('{}:{}'.format(key, value.value) for key, value in self.parameters.items()))

	__repr__ = __str__


class AnonymousFunc(AST):
	def __init__(self, return_type, parameters, body, line_num, parameter_defaults=None, varargs=None):
		self.return_type = return_type
		self.parameters = parameters
		self.parameter_defaults = parameter_defaults or {}
		self.varargs = varargs
		self.body = body
		self.line_num = line_num

	def __str__(self):
		return '<Anonymous:{type} ({params})>'.format(type=self.return_type.value, params=', '.join('{}:{}'.format(key, value.value) for key, value in self.parameters.items()))

	__repr__ = __str__


class FuncCall(AST):
	def __init__(self, name, arguments, line_num, named_arguments=None):
		self.name = name
		self.arguments = arguments
		self.named_arguments = named_arguments or {}
		self.line_num = line_num


class MethodCall(AST):
	def __init__(self, obj, name, arguments, line_num, named_arguments=None):
		self.obj = obj
		self.name = name
		self.arguments = arguments
		self.named_arguments = named_arguments or {}
		self.line_num = line_num


class Return(AST):
	def __init__(self, value, line_num):
		self.value = value
		self.line_num = line_num


class StructDeclaration(AST):
	def __init__(self, name, fields, line_num):
		self.name = name
		self.fields = fields
		self.line_num = line_num


class StructLiteral(AST):
	def __init__(self, fields, line_num):
		self.fields = fields
		self.line_num = line_num


class ClassDeclaration(AST):
	def __init__(self, name, base=None, constructor=None, methods=None, class_fields=None, instance_fields=None):
		self.name = name
		self.constructor = constructor
		self.base = base
		self.methods = methods
		self.class_fields = class_fields
		self.instance_fields = instance_fields


class Assign(AST):
	def __init__(self, left, op, right, line_num):
		self.left = left
		self.op = op
		self.right = right
		self.line_num = line_num


class OpAssign(AST):
	def __init__(self, left, op, right, line_num):
		self.left = left
		self.op = op
		self.right = right
		self.line_num = line_num


class If(AST):
	def __init__(self, op, comps, blocks, line_num):
		self.op = op
		self.comps = comps
		self.blocks = blocks
		self.line_num = line_num


class Else(AST):
	pass


class While(AST):
	def __init__(self, op, comp, block, line_num):
		self.op = op
		self.comp = comp
		self.block = block
		self.line_num = line_num


class For(AST):
	def __init__(self, iterator, block, elements, line_num):
		self.iterator = iterator
		self.block = block
		self.elements = elements
		self.line_num = line_num


class LoopBlock(AST):
	def __init__(self):
		self.children = []

	def __str__(self):
		return '\n'.join(str(child) for child in self.children)

	__repr__ = __str__


class Switch(AST):
	def __init__(self, value, cases, line_num):
		self.value = value
		self.cases = cases
		self.line_num = line_num


class Case(AST):
	def __init__(self, value, block, line_num):
		self.value = value
		self.block = block
		self.line_num = line_num


class Break(AST):
	def __init__(self, line_num):
		self.line_num = line_num

	def __str__(self):
		return BREAK

	__repr__ = __str__


class Continue(AST):
	def __init__(self, line_num):
		self.line_num = line_num

	def __str__(self):
		return CONTINUE

	__repr__ = __str__


class Pass(AST):
	def __init__(self, line_num):
		self.line_num = line_num

	def __str__(self):
		return CONTINUE

	__repr__ = __str__


class BinOp(AST):
	def __init__(self, left, op, right, line_num):
		self.left = left
		self.op = op
		self.right = right
		self.line_num = line_num


class UnaryOp(AST):
	def __init__(self, op, expr, line_num):
		self.op = op
		self.expr = expr
		self.line_num = line_num


class Range(AST):
	def __init__(self, left, op, right, line_num):
		self.left = left
		self.op = op
		self.right = right
		self.value = 'range_temp'
		self.line_num = line_num


class CollectionAccess(AST):
	def __init__(self, collection, key, line_num):
		self.collection = collection
		self.key = key
		self.line_num = line_num


class DotAccess(AST):
	def __init__(self, obj, field, line_num):
		self.obj = obj
		self.field = field
		self.line_num = line_num


class Type(AST):
	def __init__(self, token, line_num, func_ret_type=None):
		self.token = token
		self.value = token.value
		self.func_ret_type = func_ret_type or []
		self.line_num = line_num


class AliasDeclaration(AST):
	def __init__(self, name, collection, line_num):
		self.name = name
		self.collection = collection
		self.line_num = line_num


class Void(AST):
	value = VOID


class Var(AST):
	def __init__(self, token, line_num, read_only=False):
		self.token = token
		self.value = token.value
		self.read_only = read_only
		self.line_num = line_num


class Constant(AST):
	def __init__(self, token, line_num):
		self.token = token
		self.value = token.value
		self.line_num = line_num


class Num(AST):
	def __init__(self, token, line_num):
		self.token = token
		self.value = token.value
		self.line_num = line_num


class Str(AST):
	def __init__(self, token, line_num):
		self.token = token
		self.value = token.value
		self.line_num = line_num


class Collection(AST):
	def __init__(self, token, collection_type, line_num, read_only, *items):
		self.token = token
		self.type = collection_type
		self.read_only = read_only
		self.read_only = read_only
		self.items = items
		self.line_num = line_num


class HashMap(AST):
	def __init__(self, items, line_num):
		self.items = items
		self.line_num = line_num


class Print(AST):
	def __init__(self, token, value, line_num):
		self.token = token
		self.value = value
		self.line_num = line_num


class Input(AST):
	def __init__(self, token, value, line_num):
		self.token = token
		self.value = value
		self.line_num = line_num


class NoOp(AST):
	def __str__(self):
		return 'noop'

	__repr__ = __str__
