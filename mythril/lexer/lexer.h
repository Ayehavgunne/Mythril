#ifndef MYTHRIL_LEXER_H
#define MYTHRIL_LEXER_H

#include "../my_types.h"
#include <iosfwd>
#include <iostream>
#include <map>
#include <string>
#include <vector>

using namespace std;

enum class CharType {
	NONE,
	NEW_LINE,
	WHITEPSACE,
	COMMENT,
	ESCAPE,
	OPERATIC,
	NUMERIC,
	ALPHANUMERIC,
};

enum class TokenType {
	TYPE,
	NUMBER,
	STRING,
	OP,
	CONSTANT,
	NEWLINE,
	INDENT,
	KEYWORD,
	ANON,
	NAME,
	ESCAPE,
	END_OF_FILE,
};

struct Token {
	TokenType type;
	string value;
	int line_num;
	int indent_level;
	MythrilType value_type;
	char char_value[50];
};

ostream &operator<<(ostream &out_stream, const Token &token);

class Lexer {
private:
	string _text;
	int _line_num = 1;
	int _indent_level = 0;

public:
	int pos = 0;
	string current_char;
	CharType char_type;
	string word;
	CharType word_type;
	vector<Token> tokens;
	char char_word[50] = {};

	explicit Lexer(string &);
	vector<Token> analyze();
	Token get_next_token();
	void next_char();
	string reset_word();
	Token eof();
	string peek(int);
	void skip_whitespace();
	static CharType get_type(string);
	Token eat_newline();
	Token eat_string();
	Token eat_operator();
	Token eat_keyword();
	Token eat_alphanumeric();
	Token eat_number();
	Token eat_escape();
	void skip_indent();
	void skip_comment();
	Token preview_token(int);
	Token make_token(TokenType);
	void word_to_char();
};

#endif
