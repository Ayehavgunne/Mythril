#include "lexer.h"
#include "../exceptions.h"
#include "my_grammar.h"
#include "../util.h"
#include <bits/stdc++.h>
#include <iostream>
#include <string>

using namespace std;

ostream &operator<<(ostream &out_stream, const Token &token) {
	map<TokenType, string> token_type_map = {
		{TokenType::TYPE, "TYPE"},
		{TokenType::NUMBER, "NUMBER"},
		{TokenType::STRING, "STRING"},
		{TokenType::OP, "OP"},
		{TokenType::CONSTANT, "CONSTANT"},
		{TokenType::NEWLINE, "NEWLINE"},
		{TokenType::INDENT, "INDENT"},
		{TokenType::KEYWORD, "KEYWORD"},
		{TokenType::ANON, "ANON"},
		{TokenType::NAME, "NAME"},
		{TokenType::END_OF_FILE, "EOF"},
	};

	map<char, string> whitespace_map = {
		{' ', " "},
		{'\t', "\\t"},
		{'\n', "\\n"},
		{'\v', "\\v"},
		{'\f', "\\f"},
		{'\r', "\\r"},
	};

	string value = token.value;

	if (isspace((int) value[0])) {
		value = '\'' + whitespace_map[value[0]] + '\'';
	}
	else if (token.type != TokenType::NUMBER) {
		if (value.find('\'') != string::npos) {
			value = '"' + value + '"';
		}
		else {
			value = '\'' + value + '\'';
		}
	}
	out_stream
		<< "Token(type="
		<< token_type_map[token.type]
		<< ", value="
		<< value
		<< ", line_num="
		<< token.line_num
		<< ", indent_level="
		<< token.indent_level
		<< ")";
	return out_stream;
}

Lexer::Lexer(string &text) {
	_text = text;
	current_char = _text[pos];
	char_type = CharType::NONE;
	word_type = CharType::NONE;
}

void Lexer::word_to_char() {
	strcpy(char_word, word.c_str());
}

Token Lexer::eof() {
	return Token {
		.indent_level=_indent_level,
		.line_num=_line_num,
		.type=TokenType::END_OF_FILE,
		.value="EOF",
		.char_value={'E', 'O', 'F'},
	};
}

Token Lexer::make_token(TokenType type) {
	string old_word = reset_word();
	Token token = {
		.type=type,
		.value=old_word,
		.line_num=_line_num,
		.indent_level=_indent_level,
	};
	strcpy(token.char_value, old_word.c_str());
	return token;
}

void Lexer::next_char() {
	pos += 1;
	if (pos > _text.length() - 1) {
		current_char = '\0';
		char_type = CharType::NONE;
	}
	else {
		current_char = _text[pos];
		char_type = get_type(current_char);
	}
	word_to_char();
}

string Lexer::reset_word() {
	string old_word = word;
	word = "";
	word_type = CharType::NONE;
	return old_word;
}

string Lexer::peek(int num) {
	int peek_pos = pos + num;
	if (peek_pos > _text.length() - 1 && peek_pos < 0) {
		string peek_char(1, '\0');
		return peek_char;
	}
	else {
		string peek_char(1, _text[peek_pos]);
		return peek_char;
	}
}

void Lexer::skip_whitespace() {
	if (peek(-1)[0] == '\n') {
		throw SyntaxError(
			"Only tab characters can indent",
			_line_num,
			current_char
		);
	}
	while (current_char[0] != EOF && current_char == " ") {
		next_char();
		reset_word();
	}
}

CharType Lexer::get_type(string a_char) {
	if (a_char == " ") {
		return CharType::WHITEPSACE;
	}
	if (a_char == "\n") {
		return CharType::NEW_LINE;
	}
	if (a_char == "#") {
		return CharType::COMMENT;
	}
	if (a_char == "\\") {
		return CharType::ESCAPE;
	}
	if (in(grammar::OPERATORS, a_char)) {
		return CharType::OPERATIC;
	}
	if (isdigit(a_char[0])) {
		return CharType::NUMERIC;
	}
	return CharType::ALPHANUMERIC;
}

Token Lexer::eat_newline() {
	reset_word();
	Token token = {
		.type=TokenType::NEWLINE,
		.value="\n",
		.line_num=_line_num,
		.indent_level=_indent_level,
		.char_value={'\n'},
	};
	_indent_level = 0;
	_line_num += 1;
	next_char();
	return token;
}

Token Lexer::eat_string() {
	string quote_char = current_char;
	next_char();
	while (current_char != quote_char) {
		if (current_char == "\\" && peek(1) == quote_char) {
			next_char();
		}
		word += current_char;
		next_char();
	}
	next_char();
	return make_token(TokenType::STRING);
}

Token Lexer::eat_operator() {
	if (
		in(grammar::MULTI_WORD_OPERATORS, word)
		&& in(grammar::MULTI_WORD_OPERATORS, preview_token(1).value)
	) {
		next_char();
		word += ' ';
		while (
			char_type == CharType::ALPHANUMERIC
			|| char_type == CharType::NUMERIC
		) {
			word += current_char;
			next_char();
		}
		return make_token(TokenType::OP);
	}

	while (char_type == CharType::OPERATIC) {
		word += current_char;
		next_char();

		if (
			in(grammar::SINGLE_OPERATORS, current_char)
			|| in(grammar::SINGLE_OPERATORS, word)
		) {
			word_type = CharType::NONE;
			break;
		}
	}
	return make_token(TokenType::OP);
}

Token Lexer::eat_keyword() {
	if (
		in(grammar::MULTI_WORD_KEYWORDS, word)
		&& in(grammar::MULTI_WORD_KEYWORDS, preview_token(1).value)
	) {
		next_char();
		word += ' ';
		while (
			char_type == CharType::ALPHANUMERIC
			|| char_type == CharType::NUMERIC
		) {
			word += current_char;
			next_char();
		}
	}
	return make_token(TokenType::KEYWORD);
}

Token Lexer::eat_alphanumeric() {
	while (char_type == CharType::ALPHANUMERIC || char_type == CharType::NUMERIC) {
		word += current_char;
		next_char();
	}

	if (in(grammar::OPERATORS, word)) {
		return eat_operator();
	}
	else if (in(grammar::KEYWORDS, word)) {
		return eat_keyword();
	}
	else if (in(grammar::TYPES, word)) {
		return make_token(TokenType::TYPE);
	}
	else if (in(grammar::CONSTANTS, word)) {
		return make_token(TokenType::CONSTANT);
	}
	else {
		return make_token(TokenType::NAME);
	}
}

Token Lexer::eat_number() {
	while (
		char_type == CharType::NUMERIC || (current_char == "." && peek(1) != ".")
		) {
		word += current_char;
		next_char();
		if (char_type == CharType::ALPHANUMERIC) {
			throw SyntaxError(
				"Variables cannot start with numbers",
				_line_num,
				current_char
			);
		}
	}
	string value = reset_word();
	MythrilType value_type;
	if (value.find('.') != string::npos) {
		value_type = MythrilType::DEC;
	}
	else {
		value_type = MythrilType::INT;
	}
	Token token = Token {
		.type=TokenType::NUMBER,
		.value=value,
		.line_num=_line_num,
		.indent_level=_indent_level,
		.value_type=value_type,
	};
	strcpy(token.char_value, value.c_str());
	return token;
}

void Lexer::skip_indent() {
	while (current_char[0] != EOF && current_char == "\t") {
		reset_word();
		_indent_level += 1;
		next_char();
	}
}

void Lexer::skip_comment() {
	while (current_char != "\n") {
		next_char();
		if (current_char[0] == EOF) {
			return;
		}
	}
	eat_newline();
	if (current_char == "#") {
		skip_comment();
	}
}

Token Lexer::preview_token(int num) {
	if (num < 1) {
		throw invalid_argument("num argument must be 1 or greater");
	}

	Token next_token = {};
	int _pos = pos;
	string _current_char = current_char;
	CharType _char_type = char_type;
	string _word = word;
	CharType _word_type = word_type;
	int __line_num = _line_num;
	int __indent_level = _indent_level;

	while (num > 0) {
		next_token = get_next_token();
		num -= 1;
	}

	pos = _pos;
	current_char = _current_char;
	char_type = _char_type;
	word = _word;
	word_type = _word_type;
	_line_num = __line_num;
	_indent_level = __indent_level;

	return next_token;
}

Token Lexer::get_next_token() {
	if (current_char[0] == EOF || current_char[0] == '\0') {
		return eof();
	}

	if (current_char == "\n") {
		return eat_newline();
	}

	if (current_char == "\t") {
		skip_indent();
	}

	if (current_char == " ") {
		skip_whitespace();
	}

	if (current_char == "#") {
		skip_comment();
		return get_next_token();
	}

	if (in(grammar::QUOTES, current_char)) {
		return eat_string();
	}

	if (char_type == CharType::NONE) {
		char_type = get_type(current_char);
	}
	if (word_type == CharType::NONE) {
		word_type = char_type;
	}

	if (word_type == CharType::OPERATIC) {
		return eat_operator();
	}

	if (word_type == CharType::ALPHANUMERIC) {
		return eat_alphanumeric();
	}

	if (word_type == CharType::NUMERIC) {
		return eat_number();
	}

	throw SyntaxError("Unknown Character", _line_num, current_char);
}

vector<Token> Lexer::analyze() {
	Token token = get_next_token();
	tokens.push_back(token);
	while (token.type != TokenType::END_OF_FILE) {
		token = get_next_token();
		tokens.push_back(token);
	}
	return tokens;
}
