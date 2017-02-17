NUMBER = 'NUMBER'
PLUS = '+'
MINUS = '-'
MUL = '*'
DIV = '/'
FLOORDIV = '//'
LPAREN = '('
RPAREN = ')'
CAST = '::'
EOF = 'END'
NEWLINE = 'NEWLINE'
NAME = 'NAME'
ASSIGN = '='
BEGIN = 'BEGIN'
TYPE = 'TYPE'
KEYWORD = 'KEYWORD'


class AST(object):
	def __init__(self):
		self.left = None
		self.token = self.op = None
		self.right = None
		self.value = None
		self.expr = None
		self.block = None
		self.var_node = None
		self.type_node = None

	def __str__(self):
		out = [
			self.left,
			self.right,
			self.expr,
			self.block,
			self.type_node,
			self.var_node,
		]
		if self.token:
			out.insert(0, self.token.type)
			out.insert(1, self.token.value)
		else:
			out.insert(0, self.value)
		out = map(str, filter(None, out))
		return '(' + ' '.join(out) + ')'

	__repr__ = __str__


class Program(AST):
	def __init__(self, block):
		super().__init__()
		self.block = block


class VarDecl(AST):
	def __init__(self, var_node, type_node):
		super().__init__()
		self.var_node = var_node
		self.type_node = type_node


class Compound(AST):
	def __init__(self):
		super().__init__()
		self.children = []

	def __str__(self):
		return '\n'.join(str(child) for child in self.children)

	__repr__ = __str__


class Assign(AST):
	def __init__(self, left, op, right):
		super().__init__()
		self.left = left
		self.token = self.op = op
		self.right = right


class BinOp(AST):
	def __init__(self, left, op, right):
		super().__init__()
		self.left = left
		self.token = self.op = op
		self.right = right


class UnaryOp(AST):
	def __init__(self, op, expr):
		super().__init__()
		self.token = self.op = op
		self.expr = expr


class Type(AST):
	def __init__(self, token):
		super().__init__()
		self.token = token
		self.value = token.value


class Null(AST):
	def __str__(self):
		return 'NULL'

	__repr__ = __str__


class Var(AST):
	def __init__(self, token):
		super().__init__()
		self.token = token
		self.value = token.value


class Num(AST):
	def __init__(self, token):
		super().__init__()
		self.token = token
		self.value = token.value


class Str(AST):
	def __init__(self, token):
		super().__init__()
		self.token = token
		self.value = token.value


class NoOp(AST):
	def __init__(self):
		super().__init__()