types = ('any', 'int', 'dec', 'float', 'complex', 'str', 'bool', 'byte', 'list', 'tuple', 'dict', 'enum', 'func')
single_operators = ('(', ')', ',', ':', '[', ']', '{', '}', '.', '&', '|', '^', '~')
multi_operators = (
	'+', '-', '*', '/', '//', '%', '**', '<', '>', '<=', '>=', '==',
	'!=','=','+=', '-=', '*=', '/=', '//=', '%=', '**=', '<<', '>>'
	'is not', 'not in', 'is', 'in', 'not', 'and', 'or'
)
keywords = (
	'if', 'else', 'for', 'switch', 'case', 'def', 'false', 'true', 'null', 'class', 'this', 'return', 'try',
	'catch', 'finally', 'while', 'yield', 'break', 'continue', 'del', 'from', 'import', 'as', 'pass', 'raise',
	'with', 'union', 'struct', 'require', 'ensure', 'override', 'doc', 'abstract', 'property', 'get', 'set'
)


class Token(object):
	def __init__(self, type_name, line_num, value=''):
		self.type = type_name
		self.line_num = line_num
		self.value = value

	def __str__(self):
		if "'" in self.value:
			quote_char = '"'
		else:
			quote_char = "'"
		return "{}(type={}, value={}{}{}, line_num={})".format(
			self.__class__.__name__,
			self.type,
			quote_char,
			self.value,
			quote_char,
			self.line_num
		)

	def __repr__(self):
		return self.__str__()

def is_float(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def name_or_num_or_op(string, line_num):
	if string.isdecimal() or string.isnumeric() or is_float(string):
		return Token('NUMBER', line_num, string)
	elif string in multi_operators:
		return Token('OP', line_num, string)
	else:
		return Token('NAME', line_num, string)

def tokenize(string):
	word = ''
	in_str = False
	single_quote = False
	line_num = 1
	for char in string:
		if not in_str:
			if char == '\n':
				if word:
					yield name_or_num_or_op(word, line_num)
				yield Token('NEWLINE', line_num, '\\n')
				line_num += 1
				word = ''
			elif char == '\t':
				yield Token('INDENT', line_num, '\\t')
				word = ''
			elif char in single_operators:
				if word:
					yield name_or_num_or_op(word, line_num)
				yield Token('OP', line_num, char)
				word = ''
			elif char.isspace():
				if word:
					yield name_or_num_or_op(word, line_num)
				word = ''
			elif char == "'" or char == '"':
				in_str = True
				if char == "'":
					single_quote = True
			else:
				word += char
		else:
			if char == "'" and single_quote:
				in_str = False
				yield Token('STRING', line_num, word)
				word = ''
			elif char == '"' and not single_quote:
				in_str = False
				yield Token('STRING', line_num, word)
				word = ''
			else:
				word += char
	yield Token('END', line_num)

if __name__ == '__main__':
	for t in tokenize(open('example.dm').read()):
		print(t)