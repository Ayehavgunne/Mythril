from dataclasses import dataclass
from decimal import Decimal

import grammar
from grammar import LexerType


@dataclass
class Token:
    def __init__(
        self,
        token_type: grammar.TokenType,
        value: str,
        line_num: int,
        value_type: str | None = None,
    ):
        self.type = token_type
        self.value = value
        self.value_type = value_type
        self.line_num = line_num

    def __str__(self):
        return (
            f"Token(type={self.type}, value={self.value!r}, line_num={self.line_num})"
        )

    __repr__ = __str__


class Lexer:
    def __init__(self, text: str, file_name: str | None = None):
        self.text = text
        self.file_name = file_name
        self.pos = 0
        self.current_char = self.text[self.pos]
        self.char_type = None
        self.word = ""
        self.word_type = None
        self._line_num = 1
        self.current_token = None

    def next_char(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
            self.char_type = None
        else:
            self.current_char = self.text[self.pos]
            self.char_type = self.get_type(self.current_char)

    def reset_word(self):
        old_word = self.word
        self.word = ""
        self.word_type = None
        return old_word

    def peek(self, num: int):
        peek_pos = self.pos + num
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def preview_token(self, num=1):
        if num < 1:
            raise ValueError("num argument must be 1 or greater")
        next_token = None
        current_pos = self.pos
        current_char = self.current_char
        current_char_type = self.char_type
        current_word = self.word
        current_word_type = self.word_type
        current_line_num = self.line_num
        for _ in range(num):
            next_token = self.get_next_token()
        self.pos = current_pos
        self.current_char = current_char
        self.char_type = current_char_type
        self.word = current_word
        self.word_type = current_word_type
        self._line_num = current_line_num
        return next_token

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.next_char()
            self.reset_word()

    def skip_comment(self):
        while self.current_char != grammar.NEWLINE:
            self.next_char()
            if self.current_char is None:
                return self.eof()
        self.eat_newline()
        if self.current_char == grammar.COMMENT:
            self.skip_comment()

    def increment_line_num(self):
        self._line_num += 1

    @property
    def line_num(self):
        return self._line_num

    def eat_newline(self):
        self.reset_word()
        token = Token(LexerType.NEWLINE, grammar.NEWLINE, self.line_num)
        self.increment_line_num()
        self.next_char()
        return token

    def eof(self):
        return Token(LexerType.EOF, LexerType.EOF, self.line_num)

    @staticmethod
    def get_type(char: str):
        if char.isspace():
            return LexerType.WHITESPACE
        if char == grammar.COMMENT:
            return LexerType.COMMENT
        if char == grammar.ESCAPE:
            return LexerType.ESCAPE
        if char in grammar.OPERATORS:
            return LexerType.OPERATIC
        if char.isdigit():
            return LexerType.NUMERIC
        else:
            return LexerType.ALPHANUMERIC

    def get_next_token(self):
        if self.current_char is None:
            return self.eof()

        if self.current_char == grammar.NEWLINE:
            return self.eat_newline()

        if self.current_char.isspace():
            self.skip_whitespace()

        if self.current_char == grammar.COMMENT:
            self.skip_comment()
            return self.get_next_token()

        if self.current_char == grammar.DOUBLE_QUOTE:
            self.next_char()
            while self.current_char != grammar.DOUBLE_QUOTE:
                if (
                    self.current_char == grammar.ESCAPE
                    and self.peek(1) == grammar.DOUBLE_QUOTE
                ):
                    self.next_char()
                self.word += self.current_char
                self.next_char()
            self.next_char()
            return Token(LexerType.STRING, self.reset_word(), self.line_num)

        if self.current_char == grammar.SINGLE_QUOTE:
            self.next_char()
            while self.current_char != grammar.SINGLE_QUOTE:
                if (
                    self.current_char == grammar.ESCAPE
                    and self.peek(1) == grammar.SINGLE_QUOTE
                ):
                    self.next_char()
                self.word += self.current_char
                self.next_char()
            self.next_char()
            return Token(LexerType.STRING, self.reset_word(), self.line_num)

        if not self.char_type:
            self.char_type = self.get_type(self.current_char)
        if not self.word_type:
            self.word_type = self.char_type

        if self.word_type == LexerType.OPERATIC:
            while self.char_type == LexerType.OPERATIC:
                self.word += self.current_char
                self.next_char()
                if (
                    self.current_char in grammar.SINGLE_OPERATORS
                    or self.word in grammar.SINGLE_OPERATORS
                ):
                    break
            return Token(LexerType.OP, self.reset_word(), self.line_num)

        if self.word_type == LexerType.ALPHANUMERIC:
            while (
                self.char_type == LexerType.ALPHANUMERIC
                or self.char_type == LexerType.NUMERIC
            ):
                self.word += self.current_char
                self.next_char()

            if self.word in grammar.OPERATORS:
                if (
                    self.word in grammar.MULTI_WORD_OPERATORS
                    and self.preview_token(1).value in grammar.MULTI_WORD_OPERATORS
                ):
                    self.next_char()
                    self.word += " "
                    while (
                        self.char_type == LexerType.ALPHANUMERIC
                        or self.char_type == LexerType.NUMERIC
                    ):
                        self.word += self.current_char
                        self.next_char()
                    return Token(LexerType.OP, self.reset_word(), self.line_num)
                else:
                    return Token(LexerType.OP, self.reset_word(), self.line_num)

            if self.word in grammar.KEYWORDS:
                if (
                    self.word in grammar.MULTI_WORD_KEYWORDS
                    and self.preview_token(1).value in grammar.MULTI_WORD_KEYWORDS
                ):
                    self.next_char()
                    self.word += " "
                    while (
                        self.char_type == LexerType.ALPHANUMERIC
                        or self.char_type == LexerType.NUMERIC
                    ):
                        self.word += self.current_char
                        self.next_char()
                    return Token(LexerType.KEYWORD, self.reset_word(), self.line_num)
                else:
                    return Token(LexerType.KEYWORD, self.reset_word(), self.line_num)
            elif self.word in grammar.TYPES:
                return Token(LexerType.TYPE, self.reset_word(), self.line_num)
            elif self.word in grammar.CONSTANTS:
                return Token(LexerType.CONSTANT, self.reset_word(), self.line_num)
            else:
                return Token(LexerType.NAME, self.reset_word(), self.line_num)

        if self.word_type == LexerType.NUMERIC:
            while (
                self.char_type == LexerType.NUMERIC
                or self.current_char == grammar.DOT
                and self.peek(1) != grammar.DOT
            ):
                self.word += self.current_char
                self.next_char()
                if self.char_type == LexerType.ALPHANUMERIC:
                    raise SyntaxError("Variables cannot start with numbers")
            value = self.reset_word()
            if grammar.DOT in value:
                value = Decimal(value)
                value_type = grammar.DEC
            else:
                value = int(value)
                value_type = grammar.INT
            return Token(LexerType.NUMBER, value, self.line_num, value_type=value_type)

        if self.char_type == LexerType.ESCAPE:
            self.reset_word()
            self.next_char()
            line_num = self.line_num
            if self.current_char == grammar.NEWLINE:
                self.increment_line_num()
            self.next_char()
            return Token(LexerType.ESCAPE, grammar.ESCAPE, line_num)

        raise SyntaxError("Unknown character")

    def analyze(self):
        token = self.get_next_token()
        while token.type != LexerType.EOF:
            yield token
            token = self.get_next_token()
        yield token


if __name__ == "__main__":
    file = "test.my"
    with open(file) as my_file:
        lexer = Lexer(my_file.read(), file)
        for t in lexer.analyze():
            if t.type == LexerType.NEWLINE:
                print(t)
            else:
                print(t, end=" ")
