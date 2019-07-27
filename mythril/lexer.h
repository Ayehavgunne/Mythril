#pragma once
#include <iosfwd>
#include <string>
#include <vector>
#include "my_types.h"
using namespace std;

enum CharType {
    CHAR_START,
    CHAR_WHITEPSACE,
    CHAR_COMMENT,
    CHAR_ESCAPE,
    CHAR_OPERATIC,
    CHAR_NUMERIC,
    CHAR_ALPHANUMERIC,
};

enum TokenType {
    TOKEN_TYPE,
    TOKEN_NUMBER,
    TOKEN_STRING,
    TOKEN_OP,
    TOKEN_CONSTANT,
    TOKEN_NEWLINE,
    TOKEN_INDENT,
    TOKEN_KEYWORD,
    TOKEN_ANON,
    TOKEN_NAME,
    TOKEN_EOF,
};

struct Token {
    TokenType type;
    string value;
    string value_type;
    int line_num;
    int indent_level;
};

class Lexer {
private:
    string _text;
    int _line_num = 1;
    int _indent_level = 0;
public:
    int pos = 0;
    char current_char = _text[pos];
    CharType char_type;
    string word;
    CharType word_type;
    Token current_token;
    explicit Lexer(string &text);
    Token get_next_token();
    Token eof();
    vector<Token> tokens;
};
