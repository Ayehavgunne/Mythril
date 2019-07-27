#include "lexer.h"
using namespace std;

Lexer::Lexer(string &text) {
    _text = text;
    char_type = CHAR_START;
    word_type = CHAR_START;
}

Token Lexer::get_next_token() {
    if (current_char == EOF) {
        return eof();
    }


};

Token Lexer::eof() {
    Token token = {
        .indent_level = _indent_level,
        .line_num = _line_num,
        .type = TOKEN_EOF,
        .value = word,
    };
    return token;
}