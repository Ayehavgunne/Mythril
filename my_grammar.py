# Operators
PLUS = '+'
MINUS = '-'
MUL = '*'
DIV = '/'
FLOORDIV = '//'
MOD = '%'
POWER = '**'
ARITHMATIC_LEFT_SHIFT = '<<<'  # TODO
ARITHMATIC_RIGHT_SHIFT = '>>>'  # TODO
XOR = 'xor'
BINARY_ONES_COMPLIMENT = '~'  # TODO
BINARY_LEFT_SHIFT = '<<'  # TODO
BINARY_RIGHT_SHIFT = '>>'  # TODO
AND = 'and'
OR = 'or'
NOT = 'not'
IN = 'in'  # TODO
NOT_IN = 'not in'  # TODO
IS = 'is'  # TODO
IS_NOT = 'is not'  # TODO
TYPE_AND = '&'
TYPE_OR = '|'
TYPE_THEN = ','
LPAREN = '('
RPAREN = ')'
LSQUAREBRACKET = '['
RSQUAREBRACKET = ']'
LCURLYBRACKET = '{'
RCURLYBRACKET = '}'
COMMA = ','
COLON = ':'
DOT = '.'  # TODO
RANGE = '..'
ELLIPSIS = '...'  # TODO
ARROW = '->'
CAST = '::'
ASSIGN = '='
PLUS_ASSIGN = '+='
MINUS_ASSIGN = '-='
MUL_ASSIGN = '*='
DIV_ASSIGN = '/='
FLOORDIV_ASSIGN = '//='
MOD_ASSIGN = '%='
POWER_ASSIGN = '**='
EQUALS = '=='
NOT_BANG = '!'
NOT_EQUALS = '!='
LESS_THAN = '<'
GREATER_THAN = '>'
LESS_THAN_OR_EQUAL_TO = '<='
GREATER_THAN_OR_EQUAL_TO = '>='
DECORATOR = '@'  # TODO

# Types
ANY = 'Any'
INT = 'Int'
INT8 = 'Int8'
INT32 = 'Int32'
INT128 = 'Int128'
DEC = 'Dec'
FLOAT = 'Float'
COMPLEX = 'Complex'  # TODO
STR = 'Str'
BOOL = 'Bool'
BYTES = 'Bytes'  # TODO
ARRAY = 'Array'
LIST = 'List'
TUPLE = 'Tuple'  # TODO
SET = 'Set'  # TODO
DICT = 'Dict'
ENUM = 'Enum'  # TODO
FUNC = 'Func'
STRUCT = 'Struct'  # TODO
NULLTYPE = 'NullType'

# Contstants
TRUE = 'true'
FALSE = 'false'
NULL = 'null'
NAN = 'nan'
INF = 'inf'
NEGATIVE_INF = '-inf'

# Keywords
IF = 'if'
ELSE_IF = 'else if'
ELSE = 'else'
FOR = 'for'
WHILE = 'while'
SWITCH = 'switch'
CASE = 'case'
DEFAULT = 'default'
DEF = 'def'
CLASS = 'class'  # TODO
ACTOR = 'actor'  # TODO
CONST = 'const'
NEW = 'new'  # TODO
SUPER = 'super'  # TODO
THIS = 'this'  # TODO
RETURN = 'return'
TEST = 'test'  # TODO
TRY = 'try'  # TODO
CATCH = 'catch'  # TODO
FINALLY = 'finally'  # TODO
THEN = 'then'  # TODO
YIELD = 'yield'  # TODO
BREAK = 'break'
CONTINUE = 'continue'
MATCH = 'match'  # TODO
DEL = 'del'  # TODO
FROM = 'from'  # TODO
IMPORT = 'import'  # TODO
WILDCARD = '*'  # TODO
WITH = 'with'  # TODO
AS = 'as'  # TODO
PASS = 'pass'
VOID = 'void'
RAISE = 'raise'  # TODO
ALIAS = 'alias'
REQUIRE = 'require'  # TODO
ENSURE = 'ensure'  # TODO
OVERRIDE = 'override'  # TODO
DOC = 'doc'  # TODO allow unquoted text in doc block
ABSTRACT = 'abstract'  # TODO
GETTER = 'getter'  # TODO
SETTER = 'setter'  # TODO
ASSERT = 'assert'  # TODO

ARITHMETIC_OP = (PLUS, MINUS, MUL, DIV, MOD, FLOORDIV, POWER, ARITHMATIC_LEFT_SHIFT, ARITHMATIC_RIGHT_SHIFT)

ASSIGNMENT_OP = (ASSIGN, PLUS_ASSIGN, MINUS_ASSIGN, MUL_ASSIGN, DIV_ASSIGN, FLOORDIV_ASSIGN, MOD_ASSIGN, POWER_ASSIGN)

COMPARISON_OP = (EQUALS, NOT_BANG, NOT_EQUALS, LESS_THAN, GREATER_THAN, GREATER_THAN_OR_EQUAL_TO, LESS_THAN_OR_EQUAL_TO)

LOGICAL_OP = (AND, OR, NOT)

BINARY_OP = (XOR, BINARY_ONES_COMPLIMENT, BINARY_LEFT_SHIFT, BINARY_RIGHT_SHIFT)

MEMBERSHIP_OP = (IN, NOT_IN)

IDENTITY_OP = (IS, IS_NOT)

TYPE_OP = (TYPE_AND, TYPE_OR, TYPE_THEN)

MULTI_WORD_OPERATORS = (IS, IS_NOT, IN, NOT_IN, NOT)

OPERATORS = (
	LPAREN, RPAREN, LSQUAREBRACKET, RSQUAREBRACKET, LCURLYBRACKET, RCURLYBRACKET,
	ARROW, COMMA, COLON, DOT, DECORATOR, CAST, RANGE, ELLIPSIS,
) + ARITHMETIC_OP + ASSIGNMENT_OP + COMPARISON_OP + LOGICAL_OP + BINARY_OP + MEMBERSHIP_OP + IDENTITY_OP + TYPE_OP

SINGLE_OPERATORS = (
	LPAREN, RPAREN, LSQUAREBRACKET, RSQUAREBRACKET, LCURLYBRACKET, RCURLYBRACKET,
	BINARY_ONES_COMPLIMENT, COMMA, DECORATOR, TYPE_AND, TYPE_OR, TYPE_THEN
)

KEYWORDS = (
	IF, ELSE, WHILE, FOR, SWITCH, CASE, DEF, CLASS, SUPER, THIS, RETURN, TEST, TRY, CATCH,
	FINALLY, THEN, YIELD, BREAK, CONTINUE, DEL, IMPORT, FROM, WITH, AS, PASS, VOID, RAISE, ACTOR,
	CONST, REQUIRE, ENSURE, OVERRIDE, DOC, ABSTRACT, GETTER, SETTER, ASSERT, DEFAULT, NEW, ALIAS
)

MULTI_WORD_KEYWORDS = (IF, ELSE, ELSE_IF)

TYPES = (ANY, INT, INT8, INT32, INT128, DEC, FLOAT, COMPLEX, STR, BOOL, BYTES, ARRAY, LIST, TUPLE, DICT, ENUM, FUNC, STRUCT, NULLTYPE)

CONSTANTS = (TRUE, FALSE, NULL, NAN, INF, NEGATIVE_INF)

BUILTIN_FUNCTIONS = ('print',)

PRINT = 'print'
TYPE = 'TYPE'
NUMBER = 'NUMBER'
STRING = 'STRING'
OP = 'OP'
CONSTANT = 'CONSTANT'
NEWLINE = 'NEWLINE'
INDENT = 'INDENT'
KEYWORD = 'KEYWORD'
ANON = 'ANON'
NAME = 'NAME'
EOF = 'EOF'

ALPHANUMERIC = 'alphanumeric'
NUMERIC = 'numeric'
OPERATIC = 'operatic'
WHITESPACE = 'whitespace'
COMMENT = 'comment'
ESCAPE = 'escape'

# TODO Features to add
# Keyword arguments {Done in Compiler}
# Argument default values {Done in Compiler}
# Variable number of arguments (varargs) {Partialy done in Compiler}
# Variable number of keyword arguments
# Signed Integers {Not an issue in interpreter}
# Structs
# Classes
# Multiple Inheritance (for both classes and structs!)
# Enums
# Actors
# Tests built into the language
# Contracts built into the language ('require' and 'ensure')
# Exceptions
# Yielding
# Context Manager ('with' and 'as' keywords)
# Modules (importing with 'from' and/or 'import')
# Object literals
# Closures {Done in Interpreter}
# Anonymous (multi statement) functions {Done in Interpreter}
# assigning functions to variables {Done in Interpreter}
# Properties ('getter' and 'setter')
# Decorators
# Delete things ('del' keyword)
# Type Aliasing
# Bytes type
# Binary operators
# Complex number type
# Slices
# More Collection types (set, hashmap, tuple)
# Pattern matching
# Throw away variable using '_' single underscore character
# Call C or Python functions from within Mythril http://eli.thegreenplace.net/2015/calling-back-into-python-from-llvmlite-jited-code/
# Automatic integer(or number) casting on overflow
# Support Unicode (UTF-8) by default
# Multiple dispatch or only allow single function with given name and force heavy use of type aliasing?
# Ignore underscores in numbers (as separators to increase readability)
# Add hexidecimal, octal, and binary literal representations of numbers
# Javadocs like documentation built in