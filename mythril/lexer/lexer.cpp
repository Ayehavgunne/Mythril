#include "lexer.h"
#include "../exceptions.h"
#include "my_grammar.h"
#include <algorithm>
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
		{'\t', "\\t"},
		{'\n', "\\n"},
		{'\v', "\\v"},
		{'\f', "\\f"},
		{'\r', "\\r"},
	};

	string value = token.value;

	if (isspace((int) value[0])) {
		value = '\'' + whitespace_map[(int) value[0]] + '\'';
	}
	else if (token.type == TokenType::END_OF_FILE) {
		value = "'EOF'";
	}
	else if (token.type != TokenType::NUMBER) {
		bool in_str = value.find('\'') != string::npos;
		if (in_str) {
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

Token Lexer::eof() {
	return Token{
		.indent_level=_indent_level,
		.line_num=_line_num,
		.type=TokenType::END_OF_FILE,
		.value=word,
	};
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
}

string Lexer::reset_word() {
	string old_word = word;
	word = "";
	word_type = CharType::NONE;
	return old_word;
}

char Lexer::peek(int num) {
	int peek_pos = pos + num;
	if (peek_pos > _text.length() - 1 && peek_pos < 0) {
		return '\0';
	}
	else {
		return _text[peek_pos];
	}
}

void Lexer::skip_whitespace() {
	if (peek(-1) == '\n') {
		throw SyntaxError(
			"Only tab characters can indent",
			_line_num,
			current_char
		);
	}
	while (current_char != EOF && current_char == ' ') {
		next_char();
		reset_word();
	}
}

CharType Lexer::get_type(char a_char) {
	string a_str(1, a_char);
	if (a_char == ' ') {
		return CharType::WHITEPSACE;
	}
	if (a_char == '\n') {
		return CharType::NEW_LINE;
	}
	if (a_char == '#') {
		return CharType::COMMENT;
	}
	if (a_char == '\\') {
		return CharType::ESCAPE;
	}
	bool in_ops = find(begin(OPERATORS), end(OPERATORS), a_str) != end(OPERATORS);
	if (in_ops) {
		return CharType::OPERATIC;
	}
	if (isdigit(a_char)) {
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
		.indent_level=_indent_level
	};
	_indent_level = 0;
	_line_num += 1;
	next_char();
	return token;
}

Token Lexer::eat_string() {
	char quote_char = current_char;
	next_char();
	while (current_char != quote_char) {
		if (current_char == '\\' && peek(1) == quote_char) {
			next_char();
		}
		word += current_char;
		next_char();
	}
	next_char();
	return make_token(TokenType::STRING);
}

void Lexer::skip_indent() {
	while (current_char != EOF && current_char == '\t') {
		reset_word();
		_indent_level += 1;
		next_char();
	}
}

void Lexer::skip_comment() {
	while (current_char != '\n') {
		next_char();
		if (current_char == EOF) {
			return;
		}
	}
	eat_newline();
	if (current_char == '#') {
		skip_comment();
	}
}

Token Lexer::preview_token(int num) {
	if (num < 1) {
		throw invalid_argument("num argument must be 1 or greater");
	}

	Token next_token = {};
	int _pos = pos;
	char _current_char = current_char;
	CharType _char_type = char_type;
	string _word = word;
	CharType _word_type = word_type;
	int __line_num = _line_num;
	int __indent_level = _indent_level;

	while (num >= 0) {
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

Token Lexer::make_token(TokenType type) {
	return Token{
		.type = type,
		.value = reset_word(),
		.line_num = _line_num,
		.indent_level = _indent_level,
	};
}

Token Lexer::get_next_token() {
	if (current_char == EOF || current_char == '\0') {
		return eof();
	}

	if (current_char == '\n') {
		return eat_newline();
	}

	if (current_char == '\t') {
		skip_indent();
	}

	if (current_char == ' ') {
		skip_whitespace();
	}

	if (current_char == '#') {
		skip_comment();
		return get_next_token();
	}

	string current_char_str(1, current_char);
	bool is_quote_char = find(
		begin(QUOTES),
		end(QUOTES),
		current_char_str
	) != end(QUOTES);

	if (is_quote_char) {
		return eat_string();
	}

	if (char_type == CharType::NONE) {
		char_type = get_type(current_char);
	}
	if (word_type == CharType::NONE) {
		word_type = char_type;
	}

	if (word_type == CharType::OPERATIC) {
		while (char_type == CharType::OPERATIC) {
			word += current_char;
			next_char();

			string current_char_str(1, current_char);
			bool cc_in_single_op = find(
				begin(SINGLE_OPERATORS),
				end(SINGLE_OPERATORS),
				current_char_str
			) != end(SINGLE_OPERATORS);
			bool word_in_single_op = find(
				begin(SINGLE_OPERATORS),
				end(SINGLE_OPERATORS),
				word
			) != end(SINGLE_OPERATORS);

			if (cc_in_single_op || word_in_single_op) {
				word_type = CharType::NONE;
				break;
			}
		}
		return make_token(TokenType::OP);
	}

	if (word_type == CharType::ALPHANUMERIC) {
		while (char_type == CharType::ALPHANUMERIC || char_type == CharType::NUMERIC) {
			word += current_char;
			next_char();
		}

		bool in_op = find(begin(OPERATORS), end(OPERATORS), word) != end(OPERATORS);

		if (in_op) {
			string pt = preview_token(1).value;
			bool word_in_mw_op = find(
				begin(MULTI_WORD_OPERATORS),
				end(MULTI_WORD_OPERATORS),
				word
			) != end(MULTI_WORD_OPERATORS);
			bool pt_in_mw_op = find(
				begin(MULTI_WORD_OPERATORS),
				end(MULTI_WORD_OPERATORS),
				pt
			) != end(MULTI_WORD_OPERATORS);

			if (word_in_mw_op && pt_in_mw_op) {
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
			return make_token(TokenType::OP);
		}

		bool in_keywords = find(begin(KEYWORDS), end(KEYWORDS), word) != end(KEYWORDS);
		bool in_types = find(begin(TYPES), end(TYPES), word) != end(TYPES);
		bool in_constants = find(
			begin(CONSTANTS),
			end(CONSTANTS),
			word
		) != end(CONSTANTS);

		if (in_keywords) {
			string pt = preview_token(1).value;
			bool word_in_mw_keywords = find(
				begin(MULTI_WORD_KEYWORDS),
				end(MULTI_WORD_KEYWORDS),
				word
			) != end(MULTI_WORD_KEYWORDS);
			bool pt_in_mw_keywords = find(
				begin(MULTI_WORD_KEYWORDS),
				end(MULTI_WORD_KEYWORDS),
				pt
			) != end(MULTI_WORD_KEYWORDS);

			if (word_in_mw_keywords && pt_in_mw_keywords) {
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
		else if (in_types) {
			return make_token(TokenType::TYPE);
		}
		else if (in_constants) {
			return make_token(TokenType::CONSTANT);
		}
		else {
			return make_token(TokenType::NAME);
		}
	}

	if (word_type == CharType::NUMERIC) {
		while (
			char_type == CharType::NUMERIC || (current_char == '.' && peek(1) != '.')
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
		bool in_str = value.find('.') != string::npos;
		if (in_str) {
			value_type = MythrilType::DEC;
		}
		else {
			value_type = MythrilType::INT;
		}
		Token token = make_token(TokenType::NUMBER);
		token.value_type = value_type;
		return token;
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
