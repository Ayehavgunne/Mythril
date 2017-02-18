NUMBER = 'NUMBER'
STRING = 'STRING'
PLUS = '+'
MINUS = '-'
MUL = '*'
DIV = '/'
FLOORDIV = '//'
MOD = '%'
POWER = '**'
LPAREN = '('
RPAREN = ')'
CAST = '::'
EOF = 'END'
NEWLINE = 'NEWLINE'
NAME = 'NAME'
ASSIGN = '='
PLUS_ASSIGN = '+='
MINUS_ASSIGN = '-='
MUL_ASSIGN = '*='
DIV_ASSIGN = '/='
FLOORDIV_ASSIGN = '//='
MOD_ASSIGN = '%='
POWER_ASSIGN = '**='
EQUALS = '=='
NOT_EQUALS = '!='
LESS_THAN = '<'
GREATER_THAN = '>'
LESS_THAN_OR_EQUAL_TO = '>='
GREATER_THAN_OR_EQUAL_TO = '<='
BEGIN = 'BEGIN'
TYPE = 'TYPE'
INDENT = 'INDENT'
KEYWORD = 'KEYWORD'
COMP_OP = ('<', '>', '<=', '>=', '==', '!=')
IF = 'if'
WHILE = 'while'


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


class Assign(AST):
	def __init__(self, left, op, right):
		self.left = left
		self.token = self.op = op
		self.right = right


class OpAssign(AST):
	def __init__(self, left, op, right):
		self.left = left
		self.token = self.op = op
		self.right = right


class Comparison(AST):
	def __init__(self, op, comp, block):
		self.token = self.op = op
		self.comp = comp
		self.block = block


class BinOp(AST):
	def __init__(self, left, op, right):
		self.left = left
		self.token = self.op = op
		self.right = right


class UnaryOp(AST):
	def __init__(self, op, expr):
		self.token = self.op = op
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