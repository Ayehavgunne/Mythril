from tokens import Keyword
from tokens import PrimitiveType
from tokens import Escape
from tokens import NewLine
from tokens import Indent
from tokens import Name
from tokens import Number
from tokens import String
from tokens import op_map
from tokens import End

primitive_types = ('any', 'int', 'dec', 'float', 'complex', 'str', 'bool', 'byte', 'list', 'tuple', 'dict', 'enum', 'func')
operators = (
	'(', ')', '[', ']', '{', '}', ',', ':', '.', '&', '|', '@',	'^', '~', '+', '-', '*', '/', '<', '>', '%',
	'=', '//', '**', '<=', '>=', '==', '!=', '+=', '-=', '*=', '/=', '//=', '%=', '**=', '<<', '>>', 'is not',
	'not in', 'is', 'in', 'not', 'and', 'or'
)
single_operators = (')', ']', '}', ',', ':', '.', '&', '|', '@', '^', '~',)
keywords = (
	'if', 'else', 'for', 'switch', 'case', 'def', 'false', 'true', 'null', 'class', 'super', 'this', 'return', 'test',
	'try', 'catch', 'finally', 'while', 'yield', 'break', 'continue', 'del', 'from', 'import', 'as', 'pass', 'void',
	'raise', 'with', 'union', 'struct', 'require', 'ensure', 'override', 'doc', 'abst', 'prop', 'get', 'set', 'assert'
)

def is_float(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def get_type(char):
	if char in operators:
		return 'operatic'
	try:
		int(char)
		return 'numeric'
	except ValueError:
		return 'alphanumeric'

def get_token_of_type(string, line_num):
	if string.isdecimal() or string.isnumeric() or is_float(string):
		return Number(string, line_num)
	elif string in operators:
		return op_map[string](line_num)
	elif string in keywords:
		return Keyword(string, line_num)
	elif string in primitive_types:
		return PrimitiveType(string, line_num)
	else:
		return Name(string, line_num)

def analyze(string):
	word = ''
	in_str = False
	comment = False
	single_quote = False
	line_num = 1
	word_type = None
	escape = False
	for x, char in enumerate(string):
		if not escape:
			if char == '\\':
				escape = True
			elif not in_str:
				if char == '\n':
					if word:
						yield get_token_of_type(word, line_num)
					yield NewLine(line_num)
					line_num += 1
					comment = False
					word = ''
					word_type = None
				elif char == '#':
					comment = True
				elif not comment:
					if char == '\t':
						yield Indent(line_num)
						word = ''
						word_type = None
					elif char.isspace():
						if word == 'is':
							if x + 4 < len(string) - 1 and string[x + 1] == 'n' and string[x + 2] == 'o' and string[x + 3] == 't' and string[x + 4] == ' ':
								word += char
								continue
						elif word == 'not':
							if x + 3 < len(string) - 1 and string[x + 1] == 'i' and string[x + 2] == 'n' and string[x + 3] == ' ':
								word += char
								continue
						if word:
							yield get_token_of_type(word, line_num)
						word = ''
						word_type = None
					elif char == "'" or char == '"':
						in_str = True
						if char == "'":
							single_quote = True
						if word:
							yield get_token_of_type(word, line_num)
						word = ''
						word_type = None
					else:
						char_type = get_type(char)
						if word == '':
							word_type = get_type(char)
						if word_type == 'alphanumeric' and char_type != 'operatic':
							word += char
						if word_type == 'alphanumeric' and char_type == 'operatic':
							yield get_token_of_type(word, line_num)
							word = char
							word_type = char_type
						elif word_type == 'numeric' and char_type == 'alphanumeric':
							raise ValueError('Variables cannot start with numbers')
						elif word_type == 'numeric' and (char == '.' or char_type == 'numeric'):
							word += char
						elif char_type == 'operatic' and (word_type == 'alphanumeric' or word_type == 'numeric'):
							yield get_token_of_type(word, line_num)
							word = char
							word_type = char_type
						elif char_type == 'operatic' and word_type == 'operatic':
							if char not in single_operators:
								word += char
							else:
								yield get_token_of_type(char, line_num)
								word = ''
						elif word_type == 'operatic' and char_type != 'operatic':
							yield get_token_of_type(word, line_num)
							word = char
							word_type = char_type
			else:
				if char == "'" and single_quote:
					in_str = False
					single_quote = False
					yield String(word, line_num)
					word = ''
					word_type = None
				elif char == '"' and not single_quote:
					in_str = False
					yield String(word, line_num)
					word = ''
					word_type = None
				else:
					if word == '':
						word_type = get_type(char)
					word += char
		else:
			if not in_str:
				yield Escape(line_num)
			word += '\\' + char
			escape = False
	if word:
		yield get_token_of_type(word, line_num)
	yield End(line_num)

if __name__ == '__main__':
	for t in analyze(open('math.dm').read()):
		if t.type != 'newline':
			print(t, end=' ')
		else:
			print(t)