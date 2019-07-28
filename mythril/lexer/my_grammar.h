#ifndef MYTHRIL_MY_GRAMMAR_H
#define MYTHRIL_MY_GRAMMAR_H

#include <string>
using namespace std;

// Operators
const string PLUS = "+";
const string MINUS = "-";
const string MUL = "*";
const string DIV = "/";
const string FLOORDIV = "//";
const string MOD = "%";
const string POWER = "**";
const string ARITHMATIC_LEFT_SHIFT = "<<<";
const string ARITHMATIC_RIGHT_SHIFT = ">>>";
const string XOR = "xor";
const string BINARY_ONES_COMPLIMENT = "~";
const string BINARY_LEFT_SHIFT = "<<";
const string BINARY_RIGHT_SHIFT = ">>";
const string AND = "and";
const string OR = "or";
const string NOT = "not";
const string IN = "in";
const string NOT_IN = "not in";
const string IS = "is";
const string IS_NOT = "is not";
const string AMPERSAND = "&";
const string PIPE = "|";
const string LPAREN = "(";
const string RPAREN = ")";
const string LSQUAREBRACKET = "[";
const string RSQUAREBRACKET = "]";
const string LCURLYBRACKET = "{";
const string RCURLYBRACKET = "}";
const string COMMA = ",";
const string COLON = ":";
const string DOT = ".";
const string RANGE = "..";
const string ELLIPSIS = "...";
const string ARROW = "->";
const string CAST = "::";
const string ASSIGN = "=";
const string PLUS_ASSIGN = "+=";
const string MINUS_ASSIGN = "-=";
const string MUL_ASSIGN = "*=";
const string DIV_ASSIGN = "/=";
const string FLOORDIV_ASSIGN = "//=";
const string MOD_ASSIGN = "%=";
const string POWER_ASSIGN = "**=";
const string EQUALS = "==";
const string NOT_BANG = "!";
const string NOT_EQUALS = "!=";
const string LESS_THAN = "<";
const string GREATER_THAN = ">";
const string LESS_THAN_OR_EQUAL_TO = "<=";
const string GREATER_THAN_OR_EQUAL_TO = ">=";
const string DECORATOR = "@";

const string OPERATORS[51] = {
	PLUS, MINUS, MUL, DIV, FLOORDIV, MOD, POWER, ARITHMATIC_LEFT_SHIFT, ARITHMATIC_RIGHT_SHIFT, XOR,
	BINARY_ONES_COMPLIMENT, BINARY_LEFT_SHIFT, BINARY_RIGHT_SHIFT, AND, OR, NOT, IN, NOT_IN, IS, IS_NOT,
	AMPERSAND, PIPE, LPAREN, RPAREN, LSQUAREBRACKET, RSQUAREBRACKET, LCURLYBRACKET, RCURLYBRACKET, COMMA,
	COLON, DOT, RANGE, ELLIPSIS, ARROW, CAST, ASSIGN, PLUS_ASSIGN, MINUS_ASSIGN, MUL_ASSIGN, DIV_ASSIGN,
	FLOORDIV_ASSIGN, MOD_ASSIGN, POWER_ASSIGN, EQUALS, NOT_BANG, NOT_EQUALS, LESS_THAN, GREATER_THAN,
	LESS_THAN_OR_EQUAL_TO, GREATER_THAN_OR_EQUAL_TO, DECORATOR,
};

const string SINGLE_OPERATORS[11] = {
	LPAREN, RPAREN, LSQUAREBRACKET, RSQUAREBRACKET, LCURLYBRACKET, RCURLYBRACKET, BINARY_ONES_COMPLIMENT,
	COMMA, DECORATOR, AMPERSAND, PIPE,
};

const string MULTI_WORD_OPERATORS[5] = {
	IS, IS_NOT, IN, NOT_IN, NOT,
};

const string ARITHMATIC_OP[9] = {
	PLUS, MINUS, MUL, DIV, MOD, FLOORDIV, POWER, ARITHMATIC_LEFT_SHIFT, ARITHMATIC_RIGHT_SHIFT,
};

const string ASSIGNMENT_OP[8] = {
	ASSIGN, PLUS_ASSIGN, MINUS_ASSIGN, MUL_ASSIGN, DIV_ASSIGN, FLOORDIV_ASSIGN, MOD_ASSIGN, POWER_ASSIGN,
};

const string ARITHMETIC_ASSIGNMENT_OP[7] = {
	PLUS_ASSIGN, MINUS_ASSIGN, MUL_ASSIGN, DIV_ASSIGN, FLOORDIV_ASSIGN, MOD_ASSIGN, POWER_ASSIGN,
};

const string COMPARISON_OP[7] = {
	EQUALS, NOT_BANG, NOT_EQUALS, LESS_THAN, GREATER_THAN, GREATER_THAN_OR_EQUAL_TO, LESS_THAN_OR_EQUAL_TO,
};

const string LOGICAL_OP[3] = {
	AND, OR, NOT,
};

const string BINARY_OP[4] = {
	XOR, BINARY_ONES_COMPLIMENT, BINARY_LEFT_SHIFT, BINARY_RIGHT_SHIFT,
};

const string MEMBERSHIP_OP[2] = {
	IN, NOT_IN,
};

const string IDENTITY_OP[2] = {
	IS, IS_NOT,
};

const string TYPE_OP[3] = {
	AMPERSAND, PIPE, COMMA
};

// Keywords
const string IF = "if";
const string ELSE_IF = "else if";
const string ELSE = "else";
const string FOR = "for";
const string WHILE = "while";
const string SWITCH = "switch";
const string CASE = "case";
const string DEFAULT = "default";
const string DEF = "def";
const string CLASS = "class";
const string ACTOR = "actor";
const string CONST = "const";
const string NEW = "new";
const string SUPER = "super";
const string THIS = "this";
const string RETURN = "return";
const string TEST = "test";
const string TRY = "try";
const string CATCH = "catch";
const string FINALLY = "finally";
const string THEN = "then";
const string YIELD = "yield";
const string BREAK = "break";
const string CONTINUE = "continue";
const string MATCH = "match";
const string DEL = "del";
const string FROM = "from";
const string IMPORT = "import";
const string WILDCARD = "*";
const string WITH = "with";
const string AS = "as";
const string PASS = "pass";
const string VOID = "void";
const string RAISE = "raise";
const string ALIAS = "alias";
const string REQUIRE = "require";
const string ENSURE = "ensure";
const string OVERRIDE = "override";
const string DOC = "doc"; // TODO allow unquoted text in doc block
const string ABSTRACT = "abstract";
const string GETTER = "getter";
const string SETTER = "setter";
const string ASSERT = "assert";

const string KEYWORDS[42] = {
	IF, ELSE, WHILE, FOR, SWITCH, CASE, DEF, CLASS, SUPER, THIS, RETURN, TEST, TRY, CATCH, FINALLY, THEN,
	YIELD, BREAK, CONTINUE, DEL, MATCH, IMPORT, WILDCARD, FROM, WITH, AS, PASS, VOID, RAISE, ACTOR, CONST, REQUIRE, ENSURE,
	OVERRIDE, DOC, ABSTRACT, GETTER, SETTER, ASSERT, DEFAULT, NEW, ALIAS,
};

const string MULTI_WORD_KEYWORDS[3] = {
	IF, ELSE, ELSE_IF,
};

// Contstants
const string TRUE = "true";
const string FALSE = "false";
const string NAN = "nan";
const string INF = "inf";
const string NEGATIVE_INF = "-inf";

const string CONSTANTS[18] = {
	TRUE, FALSE, NAN, INF, NEGATIVE_INF
};

// Types
const string ANY = "Any";
const string INT = "Int";
const string INT8 = "Int8";
const string INT32 = "Int32";
const string INT64 = "Int64";  // same as int but doesn't automatically promote to larger integer type upon overflow
const string INT128 = "Int128";
const string DEC = "Dec";
const string FLOAT = "Float";
const string COMPLEX = "Complex";
const string STR = "Str";
const string BOOL = "Bool";
const string BYTES = "Bytes";
const string ARRAY = "Array";
const string LIST = "List";
const string SET = "Set";
const string DICT = "Dict";
const string ENUM = "Enum";
const string FUNC = "Func";
const string STRUCT = "Struct";

const string TYPES[19] = {
	ANY, INT, INT8, INT32, INT64, INT128, DEC, FLOAT, COMPLEX, STR, BOOL, BYTES, ARRAY, LIST, SET, DICT, ENUM,
	FUNC, STRUCT
};

#endif