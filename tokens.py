from abc import ABCMeta

op_map = {}

class Token(object, metaclass=ABCMeta):
	def __init__(self, line_num):
		self.line_num = line_num
		self.type = str(self.__class__.__name__).lower()

	def __str__(self):
		return '({})'.format(self.type)

	def __repr__(self):
		return self.__str__()


class Literal(Token):
	def __init__(self, value, line_num):
		super().__init__(line_num)
		self.value = value

	def nud(self, _=None):
		return self

	def __str__(self):
		return '({} {})'.format(self.type, self.value)

	def __repr__(self):
		return self.__str__()


class Name(Literal):
	def __init__(self, value, line_num):
		super().__init__(value, line_num)


class Keyword(Literal):
	def __init__(self, value, line_num):
		super().__init__(value, line_num)


class PrimitiveType(Literal):
	def __init__(self, value, line_num):
		super().__init__(value, line_num)


class Escape(Literal):
	def __init__(self, line_num):
		super().__init__('\\', line_num)


class NewLine(Literal):
	def __init__(self, line_num):
		super().__init__('\\n', line_num)


class Indent(Literal):
	def __init__(self, line_num):
		super().__init__('\\t', line_num)


class Number(Literal):
	def __init__(self, value, line_num):
		super().__init__(value, line_num)


class String(Literal):
	def __init__(self, value, line_num):
		super().__init__(value, line_num)


class Operator(Token):
	value = None

	def __init__(self, line_num):
		super().__init__(line_num)
		self.first = None
		self.second = None
		self.third = None

	def __str__(self):
		name = self.__class__.__name__
		if name == 'Name' or name == 'Number' or name == 'String':
			return '({} {})'.format(name.lower(), self.value)
		out = [name.lower(), self.first, self.second, self.third]
		out = map(str, filter(None, out))
		return '(' + ' '.join(out) + ')'

	def __repr__(self):
		return self.__str__()


class Add(Operator):
	lbp = 110
	value = '+'

	def __init__(self, line_num):
		super().__init__(line_num)

	def nud(self, parser):
		self.first = parser.expression(130)
		self.second = None
		return self

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class Sub(Operator):
	lbp = 110
	value = '-'

	def __init__(self, line_num):
		super().__init__(line_num)

	def nud(self, parser):
		self.first = parser.expression(130)
		self.second = None
		return self

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class Mul(Operator):
	lbp = 120
	value = '*'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class Div(Operator):
	lbp = 120
	value = '/'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class FloorDiv(Operator):
	lbp = 120
	value = '//'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class Mod(Operator):
	lbp = 130
	value = '%'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class PowerOf(Operator):
	lbp = 140
	value = '**'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp - 1)
		return self


class Equal(Operator):
	lbp = 60
	value = '=='

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class NotEqual(Operator):
	lbp = 60
	value = '!='

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class Or(Operator):
	lbp = 30
	value = 'or'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp - 1)
		return self


class And(Operator):
	lbp = 40
	value = 'and'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp - 1)
		return self


class Not(Operator):
	lbp = 50
	value = 'not'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self

	def nud(self, parser):
		self.first = parser.expression(self.lbp)
		self.second = None
		return self


class Is(Operator):
	lbp = 60
	value = 'is'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class IsNot(Operator):
	lbp = 60
	value = 'is not'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class In(Operator):
	lbp = 60
	value = 'in'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class NotIn(Operator):
	lbp = 60
	value = 'not in'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class Greater(Operator):
	lbp = 60
	value = '>'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class GreaterEqual(Operator):
	lbp = 60
	value = '>='

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class Less(Operator):
	lbp = 60
	value = '<'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class LessEqual(Operator):
	lbp = 60
	value = '<='

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class LParen(Operator):
	lbp = 150
	value = '('

	def __init__(self, line_num):
		super().__init__(line_num)

	def nud(self, parser):
		self.first = []
		comma = False
		if parser.current_token.value != ')':
			while 1:
				if parser.current_token.value == ')':
					break
				self.first.append(parser.expression())
				if parser.current_token.value != ',':
					break
				comma = True
				parser.advance(',')
		parser.advance(')')
		if not self.first or comma:
			return self
		else:
			return self.first[0]

	def led(self, left, parser):
		self.first = left
		self.second = []
		if parser.current_token.value != ')':
			while 1:
				self.second.append(parser.expression())
				if parser.current_token.value != ',':
					break
				parser.advance(',')
		parser.advance(')')
		return self


class RParen(Operator):
	lbp = 0
	value = ')'

	def __init__(self, line_num):
		super().__init__(line_num)


class LSquareBracket(Operator):
	lbp = 150
	value = '['

	def __init__(self, line_num):
		super().__init__(line_num)

	def nud(self, parser):
		self.first = []
		if parser.current_token.value != ']':
			while 1:
				if parser.current_token.value == ']':
					break
				self.first.append(parser.expression())
				if parser.current_token.value != ',':
					break
				parser.advance(',')
		parser.advance(']')
		return self


class RSquareBracket(Operator):
	lbp = 0
	value = ']'

	def __init__(self, line_num):
		super().__init__(line_num)


class LSquiglyBracket(Operator):
	lbp = 150
	value = '{'

	def __init__(self, line_num):
		super().__init__(line_num)

	def nud(self, parser):
		self.first = []
		if parser.current_token.value != '}':
			while 1:
				if parser.current_token.value == '}':
					break
				self.first.append(parser.expression())
				parser.advance(':')
				self.first.append(parser.expression())
				if parser.current_token.value != ',':
					break
				parser.advance(',')
		parser.advance('}')
		return self


class RSquiglyBracket(Operator):
	lbp = 0
	value = '}'

	def __init__(self, line_num):
		super().__init__(line_num)


class Dot(Operator):
	lbp = 150
	value = '.'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		if parser.current_token.__class__.__name__ != 'Name':
			raise SyntaxError('Expected an attribute Name, not {}.'.format(parser.current_token.__class__.__name__))
		self.first = left
		self.second = parser.current_token
		parser.advance()
		return self


class Comma(Operator):
	lbp = 0
	value = ','

	def __init__(self, line_num):
		super().__init__(line_num)


class Colon(Operator):
	lbp = 0
	value = ':'

	def __init__(self, line_num):
		super().__init__(line_num)


class Assign(Operator):
	lbp = 10
	value = '='

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self

class TernIf(Operator):
	lbp = 20
	value = 'if'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression()
		parser.advance('else')
		self.third = parser.expression()
		return self


class TernElse(Operator):
	lbp = 0
	value = 'else'

	def __init__(self, line_num):
		super().__init__(line_num)


class BinAnd(Operator):
	lbp = 90
	value = '&'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class BinOr(Operator):
	lbp = 70
	value = '|'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class BinXOr(Operator):
	lbp = 80
	value = '^'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class BinOnesComp(Operator):
	lbp = 130
	value = '~'

	def __init__(self, line_num):
		super().__init__(line_num)

	def nud(self, parser):
		self.first = parser.expression(self.lbp)
		self.second = None
		return self


class BinLeftShift(Operator):
	lbp = 100
	value = '<<'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class BinRightShift(Operator):
	lbp = 100
	value = '>>'

	def __init__(self, line_num):
		super().__init__(line_num)

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class End(Token):
	lbp = 0
	value = ''

	def __init__(self, line_num):
		super().__init__(line_num)


from sys import modules
from inspect import getmembers
from inspect import isclass

for name, obj in getmembers(modules[__name__]):
	if isclass(obj):
		if issubclass(obj, Operator):
			op_map[obj.value] = obj

operators_left = ('@', '+=', '-=', '*=', '/=', '//=', '%=', '**=')
