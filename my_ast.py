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


class ControlStructure(AST):
	def __init__(self, op, comp, block, alt_block=None):
		self.op = op
		self.comp = comp
		self.block = block
		self.alt_block = alt_block


class BinOp(AST):
	def __init__(self, left, op, right):
		self.left = left
		self.op = op
		self.right = right


class UnaryOp(AST):
	def __init__(self, op, expr):
		self.op = op
		self.expr = expr


class Type(AST):
	def __init__(self, token):
		self.token = token
		self.value = token.value


class Null(AST):
	def __str__(self):
		return 'NULL'

	__repr__ = __str__


class Var(AST):
	def __init__(self, token):
		self.token = token
		self.value = token.value


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


class NoOp(AST):
	pass