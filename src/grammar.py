# Operators
from enum import StrEnum

PLUS = "+"
MINUS = "-"
MUL = "*"
DIV = "/"
FLOORDIV = "//"
MOD = "%"
POWER = "**"
ARITHMATIC_LEFT_SHIFT = "<<<"
ARITHMATIC_RIGHT_SHIFT = ">>>"
XOR = "xor"
BINARY_ONES_COMPLIMENT = "~"
BINARY_LEFT_SHIFT = "<<"
BINARY_RIGHT_SHIFT = ">>"
AND = "and"
OR = "or"
NOT = "not"
IN = "in"
NOT_IN = "not in"
IS = "is"
IS_NOT = "is not"
AMPERSAND = "&"
PIPE = "|"
LPAREN = "("
RPAREN = ")"
LSQUAREBRACKET = "["
RSQUAREBRACKET = "]"
LCURLYBRACKET = "{"
RCURLYBRACKET = "}"
COMMA = ","
COLON = ":"
DOT = "."
RANGE = ".."
ELLIPSIS = "..."
ARROW = ">"
CAST = "::"
ASSIGN = "="
PLUS_ASSIGN = "+="
MINUS_ASSIGN = "-="
MUL_ASSIGN = "*="
DIV_ASSIGN = "/="
FLOORDIV_ASSIGN = "//="
MOD_ASSIGN = "%="
POWER_ASSIGN = "**="
EQUALS = "=="
NOT_BANG = "!"
NOT_EQUALS = "!="
LESS_THAN = "<"
GREATER_THAN = ">"
LESS_THAN_OR_EQUAL_TO = "<="
GREATER_THAN_OR_EQUAL_TO = ">="
DECORATOR = "@"

# Syntax
OPEN_BLOCK = LCURLYBRACKET
CLOSE_BLOCK = RCURLYBRACKET
ESCAPE = "\\"
COMMENT = "#"
NEWLINE = "\n"
TAB = "\t"
SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'

LBRACKETS = (LPAREN, LSQUAREBRACKET, LCURLYBRACKET)

# Types
ANY = "Any"
INT = "Int"
INT8 = "Int8"
INT32 = "Int32"
INT64 = "Int64"  # same as int but doesn't automatically promote to larger integer type upon overflow
INT128 = "Int128"
DEC = "Dec"
FLOAT = "Float"
COMPLEX = "Complex"
STR = "Str"
BOOL = "Bool"
BYTES = "Bytes"
LIST = "List"
TUPLE = "TUPLE"
SET = "Set"
DICT = "Dict"
ENUM_TYPE = "Enum"
FUNC = "Func"
STRUCT_TYPE = "Struct"

# Contstants
TRUE = "true"
FALSE = "false"
NAN = "nan"
INF = "inf"
NEGATIVE_INF = "-inf"

# Keywords
IF = "if"
ELSE_IF = "elif"
ELSE = "else"
FOR = "for"
WHILE = "while"
FUNC_DEFINITION = "def"
ENUM = "enum"
STRUCT = "struct"
CLASS = "class"
CONST = "const"
NEW = "new"
SUPER = "super"
SELF = "self"
RETURN = "return"
TEST = "test"
YIELD = "yield"
BREAK = "break"
CONTINUE = "continue"
MATCH = "match"
DEL = "del"
FROM = "from"
IMPORT = "import"
WILDCARD = "*"
WITH = "with"
AS = "as"
PASS = "pass"
ALIAS = "alias"
REQUIRE = "require"
ENSURE = "ensure"
OVERRIDE = "override"
DOC = "doc"  # allow unquoted text in doc block
ABSTRACT = "abstract"
GETTER = "getter"
SETTER = "setter"
ASSERT = "assert"

ARITHMETIC_OP = (
    PLUS,
    MINUS,
    MUL,
    DIV,
    MOD,
    FLOORDIV,
    POWER,
    ARITHMATIC_LEFT_SHIFT,
    ARITHMATIC_RIGHT_SHIFT,
)

ASSIGNMENT_OP = (
    ASSIGN,
    PLUS_ASSIGN,
    MINUS_ASSIGN,
    MUL_ASSIGN,
    DIV_ASSIGN,
    FLOORDIV_ASSIGN,
    MOD_ASSIGN,
    POWER_ASSIGN,
)

ARITHMETIC_ASSIGNMENT_OP = (
    PLUS_ASSIGN,
    MINUS_ASSIGN,
    MUL_ASSIGN,
    DIV_ASSIGN,
    FLOORDIV_ASSIGN,
    MOD_ASSIGN,
    POWER_ASSIGN,
)

COMPARISON_OP = (
    EQUALS,
    NOT_BANG,
    NOT_EQUALS,
    LESS_THAN,
    GREATER_THAN,
    GREATER_THAN_OR_EQUAL_TO,
    LESS_THAN_OR_EQUAL_TO,
)

LOGICAL_OP = (AND, OR, NOT)

BINARY_OP = (XOR, BINARY_ONES_COMPLIMENT, BINARY_LEFT_SHIFT, BINARY_RIGHT_SHIFT)

MEMBERSHIP_OP = (IN, NOT_IN)

IDENTITY_OP = (IS, IS_NOT)

TYPE_OP = (AMPERSAND, PIPE, COMMA)

MULTI_WORD_OPERATORS = (IS, IS_NOT, IN, NOT_IN, NOT)

TERM_OPS = (
    (MUL, DIV, FLOORDIV, MOD, POWER, CAST, RANGE)
    + COMPARISON_OP
    + LOGICAL_OP
    + BINARY_OP
)

OPERATORS = (
    (
        LPAREN,
        RPAREN,
        LSQUAREBRACKET,
        RSQUAREBRACKET,
        LCURLYBRACKET,
        RCURLYBRACKET,
        ARROW,
        COMMA,
        COLON,
        DOT,
        DECORATOR,
        CAST,
        RANGE,
        ELLIPSIS,
    )
    + ARITHMETIC_OP
    + ASSIGNMENT_OP
    + COMPARISON_OP
    + LOGICAL_OP
    + BINARY_OP
    + MEMBERSHIP_OP
    + IDENTITY_OP
    + TYPE_OP
)

SINGLE_OPERATORS = (
    LPAREN,
    RPAREN,
    LSQUAREBRACKET,
    RSQUAREBRACKET,
    LCURLYBRACKET,
    RCURLYBRACKET,
    BINARY_ONES_COMPLIMENT,
    COMMA,
    DECORATOR,
    AMPERSAND,
    PIPE,
)

KEYWORDS = (
    IF,
    ELSE,
    WHILE,
    FOR,
    FUNC_DEFINITION,
    ENUM,
    STRUCT,
    CLASS,
    SUPER,
    SELF,
    RETURN,
    TEST,
    YIELD,
    BREAK,
    CONTINUE,
    DEL,
    IMPORT,
    FROM,
    WITH,
    AS,
    PASS,
    CONST,
    REQUIRE,
    ENSURE,
    OVERRIDE,
    DOC,
    ABSTRACT,
    GETTER,
    SETTER,
    ASSERT,
    NEW,
    ALIAS,
)

MULTI_WORD_KEYWORDS = (IF, ELSE, ELSE_IF)

TYPES = (
    ANY,
    INT,
    INT8,
    INT32,
    INT64,
    INT128,
    DEC,
    FLOAT,
    COMPLEX,
    STR,
    BOOL,
    BYTES,
    LIST,
    DICT,
    ENUM,
    FUNC,
    STRUCT,
)

CONSTANTS = (TRUE, FALSE, NAN, INF, NEGATIVE_INF)

PRINT = "print"
INPUT = "input"

BUILTIN_FUNCTIONS = (PRINT, INPUT)


# For Lexer
class LexerType(StrEnum):
    TYPE = "TYPE"
    NUMBER = "NUMBER"
    STRING = "STRING"
    OP = "OP"
    CONSTANT = "CONSTANT"
    NEWLINE = "NEWLINE"
    KEYWORD = "KEYWORD"
    ANON = "ANON"
    NAME = "NAME"
    EOF = "EOF"
    VOID = "VOID"
    ALPHANUMERIC = "alphanumeric"
    NUMERIC = "numeric"
    OPERATIC = "operatic"
    WHITESPACE = "whitespace"
    COMMENT = "comment"
    ESCAPE = "escape"


class TokenType(StrEnum):
    PROGRAM_START = "PROGRAM_START"
    NUMBER = "NUMBER"
    STRING = "STRING"
    OP = "OP"
    CONSTANT = "CONSTANT"
    NEWLINE = "NEWLINE"
    KEYWORD = "KEYWORD"
    ANON = "ANON"
    NAME = "NAME"
    EOF = "EOF"
    VOID = "VOID"
    ALPHANUMERIC = "ALPHANUMERIC"
    NUMERIC = "NUMERIC"
    OPERATIC = "OPERATIC"
    WHITESPACE = "WHITESPACE"
    COMMENT = "COMMENT"
    ESCAPE = "ESCAPE"
    TYPE = "TYPE"
