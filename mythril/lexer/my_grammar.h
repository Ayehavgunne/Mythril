#ifndef MYTHRIL_MY_GRAMMAR_H
#define MYTHRIL_MY_GRAMMAR_H

#include <vector>
#include <string>

using namespace std;

namespace grammar {
	// Quote characters
	const string SINGLE_QUOTE = "'";
	const string DOUBLE_QUOTE = "\"";
	const string BACKTICK = "`";

	const vector<string> QUOTES = {SINGLE_QUOTE, DOUBLE_QUOTE};

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

	const vector<string> OPERATORS = {
		PLUS, MINUS, MUL, DIV, FLOORDIV, MOD, POWER, ARITHMATIC_LEFT_SHIFT,
		ARITHMATIC_RIGHT_SHIFT, XOR, BINARY_ONES_COMPLIMENT, BINARY_LEFT_SHIFT,
		BINARY_RIGHT_SHIFT, AND, OR, NOT, IN, NOT_IN, IS, IS_NOT, AMPERSAND, PIPE,
		LPAREN, RPAREN, LSQUAREBRACKET, RSQUAREBRACKET, LCURLYBRACKET, RCURLYBRACKET,
		COMMA, COLON, DOT, RANGE, ELLIPSIS, ARROW, CAST, ASSIGN, PLUS_ASSIGN,
		MINUS_ASSIGN, MUL_ASSIGN, DIV_ASSIGN, FLOORDIV_ASSIGN, MOD_ASSIGN, POWER_ASSIGN,
		EQUALS, NOT_BANG, NOT_EQUALS, LESS_THAN, GREATER_THAN, LESS_THAN_OR_EQUAL_TO,
		GREATER_THAN_OR_EQUAL_TO, DECORATOR,
	};

	const vector<string> SINGLE_OPERATORS = {
		LPAREN, RPAREN, LSQUAREBRACKET, RSQUAREBRACKET, LCURLYBRACKET, RCURLYBRACKET,
		BINARY_ONES_COMPLIMENT, COMMA, DECORATOR, AMPERSAND, PIPE,
	};

	const vector<string> MULTI_WORD_OPERATORS = {
		IS, IS_NOT, IN, NOT_IN, NOT,
	};

	const vector<string> ARITHMATIC_OP = {
		PLUS, MINUS, MUL, DIV, MOD, FLOORDIV, POWER, ARITHMATIC_LEFT_SHIFT,
		ARITHMATIC_RIGHT_SHIFT,
	};

	const vector<string> ASSIGNMENT_OP = {
		ASSIGN, PLUS_ASSIGN, MINUS_ASSIGN, MUL_ASSIGN, DIV_ASSIGN, FLOORDIV_ASSIGN,
		MOD_ASSIGN, POWER_ASSIGN,
	};

	const vector<string> ARITHMETIC_ASSIGNMENT_OP = {
		PLUS_ASSIGN, MINUS_ASSIGN, MUL_ASSIGN, DIV_ASSIGN, FLOORDIV_ASSIGN, MOD_ASSIGN,
		POWER_ASSIGN,
	};

	const vector<string> COMPARISON_OP = {
		EQUALS, NOT_BANG, NOT_EQUALS, LESS_THAN, GREATER_THAN, GREATER_THAN_OR_EQUAL_TO,
		LESS_THAN_OR_EQUAL_TO,
	};

	const vector<string> LOGICAL_OP = {
		AND, OR, NOT,
	};

	const vector<string> BINARY_OP = {
		XOR, BINARY_ONES_COMPLIMENT, BINARY_LEFT_SHIFT, BINARY_RIGHT_SHIFT,
	};

	const vector<string> MEMBERSHIP_OP = {
		IN, NOT_IN,
	};

	const vector<string> IDENTITY_OP = {
		IS, IS_NOT,
	};

	const vector<string> TYPE_OP = {
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
	const string DOC = "doc";  // TODO allow unquoted text in doc block
	const string ABSTRACT = "abstract";
	const string GETTER = "getter";
	const string SETTER = "setter";
	const string ASSERT = "assert";

	const vector<string> KEYWORDS = {
		IF, ELSE_IF, ELSE, WHILE, FOR, SWITCH, CASE, DEF, CLASS, SUPER, THIS, RETURN,
		TEST, TRY, CATCH, FINALLY, THEN, YIELD, BREAK, CONTINUE, DEL, MATCH, IMPORT,
		WILDCARD, FROM, WITH, AS, PASS, VOID, RAISE, ACTOR, CONST, REQUIRE, ENSURE,
		OVERRIDE, DOC, ABSTRACT, GETTER, SETTER, ASSERT, DEFAULT, NEW, ALIAS,
	};

	const vector<string> MULTI_WORD_KEYWORDS = {
		IF, ELSE_IF, ELSE,
	};

	// Contstants
	const string TRUE = "true";
	const string FALSE = "false";
	const string NAN = "nan";
	const string INF = "inf";
	const string NEGATIVE_INF = "-inf";

	const vector<string> CONSTANTS = {
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

	const vector<string> TYPES = {
		ANY, INT, INT8, INT32, INT64, INT128, DEC, FLOAT, COMPLEX, STR, BOOL, BYTES,
		ARRAY, LIST, SET, DICT, ENUM, FUNC, STRUCT
	};
}
#endif
