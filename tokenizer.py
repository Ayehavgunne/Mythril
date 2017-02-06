single_operators = ('(', ')', ',', ':', '[', ']', '{', '}')
multi_operators = (
    '+', '-', '*', '/', '//', '%', '**', '<', '>', '<=', '>=',
    '==', '!=','=','+=', '-=', '*=', '/=', '//=', '%=', '**='
)

class Token(object):
    def __init__(self, type_name, value=''):
        self.type = type_name
        self.value = value

    def __str__(self):
        if "'" in self.value:
            return '{}(type={}, value="{}")'.format(self.__class__.__name__, self.type, self.value)
        else:
            return "{}(type={}, value='{}')".format(self.__class__.__name__, self.type, self.value)

    def __repr__(self):
        return self.__str__()

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def name_or_num_or_op(string):
    if string.isdecimal() or string.isnumeric() or is_float(string):
        return Token('NUMBER', string)
    elif string in multi_operators:
        return Token('OP', string)
    else:
        return Token('NAME', string)

def tokenize(string):
    word = ''
    in_str = False
    single_quote = False
    for char in string:
        if not in_str:
            if char == '\n':
                if word:
                    yield name_or_num_or_op(word)
                yield Token('NEWLINE', '\\n')
                word = ''
            elif char == '\t':
                yield Token('INDENT', '\\t')
                word = ''
            elif char in single_operators:
                if word:
                    yield name_or_num_or_op(word)
                yield Token('OP', char)
                word = ''
            elif char.isspace():
                if word:
                    yield name_or_num_or_op(word)
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
                yield Token('STRING', word)
                word = ''
            elif char == '"' and not single_quote:
                in_str = False
                yield Token('STRING', word)
                word = ''
            else:
                word += char
    yield Token('END')

if __name__ == '__main__':
    for t in tokenize(open('example.dm').read()):
        print(t)