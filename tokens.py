from abc import ABCMeta


class Token(object, metaclass=ABCMeta):
	def __init__(self, line_num):
		self.line_num = line_num
		self.value = None
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

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = '+'

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

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = '-'

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

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = '*'

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class Div(Operator):
	lbp = 120

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = '/'

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class FloorDiv(Operator):
	lbp = 120

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = '//'

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class Equal(Operator):
	lbp = 60

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = '=='

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class NotEqual(Operator):
	lbp = 60

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = '!='

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class Or(Operator):
	lbp = 30

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = 'or'

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp - 1)
		return self


class And(Operator):
	lbp = 40

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = 'and'

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp - 1)
		return self


class Not(Operator):
	lbp = 50

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = 'not'

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

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = 'is'

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class IsNot(Operator):
	lbp = 60

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = 'is not'

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class In(Operator):
	lbp = 60

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = 'in'

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class NotIn(Operator):
	lbp = 60

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = 'not in'

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class Greater(Operator):
	lbp = 60

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = '>'

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class GreaterEqual(Operator):
	lbp = 60

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = '>='

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class Less(Operator):
	lbp = 60

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = '<'

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class LessEqual(Operator):
	lbp = 60

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = '<='

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression(self.lbp)
		return self


class LParen(Operator):
	lbp = 150

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = '('

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


class RParen(Token):
	lbp = 0

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = ')'


class LSquareBracket(Operator):
	lbp = 150

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = '['

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


class RSquareBracket(Token):
	lbp = 0

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = ']'


class LSquiglyBracket(Operator):
	lbp = 150

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = '{'

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


class RSquiglyBracket(Token):
	lbp = 0

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = '}'


class Dot(Operator):
	lbp = 150

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = '.'

	def led(self, left, parser):
		if parser.current_token.__class__.__name__ != 'Name':
			raise SyntaxError('Expected an attribute Name, not {}.'.format(parser.current_token.__class__.__name__))
		self.first = left
		self.second = parser.current_token
		parser.advance()
		return self


class Comma(Operator):
	lbp = 0

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = ','


class Colon(Operator):
	lbp = 0

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = ':'


class Assign(Operator):
	lbp = 10

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = '='


class TernIf(Operator):
	lbp = 20

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = 'if'

	def led(self, left, parser):
		self.first = left
		self.second = parser.expression()
		parser.advance('else')
		self.third = parser.expression()
		return self


class TernElse(Token):
	lbp = 0

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = 'else'


class End(Token):
	lbp = 0

	def __init__(self, line_num):
		super().__init__(line_num)
		self.value = ''


# infix('|', 70); infix('^', 80); infix('&', 90)
#
# infix('<<', 100); infix('>>', 100)
#
# infix('%', 120)
#
# prefix('~', 130)
#
# infix_r('**', 140)

op_map = {
	'+': Add, '-': Sub, '*': Mul, '/': Div, '//': FloorDiv, '(': LParen, ')': RParen, 'if': TernIf, 'else': TernElse,
	'.': Dot, ',': Comma, ':': Colon, 'is': Is, 'is not': IsNot, 'in': In, '[': LSquareBracket, ']': RSquareBracket,
	'{': LSquiglyBracket, '}': RSquiglyBracket, '=': Assign, '==': Equal, '!=': NotEqual
}
operators = (
	',', ':', '.', '&', '|', '@', '^', '~', '+', '-', '*', '/', '<', '>', '%', '=', '//', '**', '<=', '>=', '==', '!=',
	'+=', '-=', '*=', '/=', '//=', '%=', '**=', '<<', '>>', 'is not', 'not in', 'is', 'in', 'not', 'and', 'or')
