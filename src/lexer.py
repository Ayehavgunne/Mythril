from dataclasses import dataclass

import grammar
from grammar import LexerType, TokenType


@dataclass
class Token:
    token_type: grammar.TokenType
    value: str
    line_num: int
    indent_level: int
    value_type: str | None = None


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
        self._indent_level = 0
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

    def make_token(
        self,
        token_type: grammar.TokenType,
        value: str,
        value_type: str | None = None,
        line_num: int | None = None,
    ):
        return Token(
            token_type=token_type,
            value=value,
            line_num=line_num or self.line_num,
            indent_level=self.indent_level,
            value_type=value_type,
        )

    def preview_token(self, num=1) -> Token | None:
        if num < 1:
            raise ValueError("num argument must be 1 or greater")
        next_token = None
        current_pos = self.pos
        current_char = self.current_char
        current_char_type = self.char_type
        current_word = self.word
        current_word_type = self.word_type
        current_line_num = self.line_num
        current_indent_level = self.indent_level
        for _ in range(num):
            next_token = self.get_next_token()
        self.pos = current_pos
        self.current_char = current_char
        self.char_type = current_char_type
        self.word = current_word
        self.word_type = current_word_type
        self._line_num = current_line_num
        self._indent_level = current_indent_level
        return next_token

    def skip_whitespace(self):
        # if self.peek(-1) == '\n':
        #     print(f'({self.current_char})')
        #     raise SyntaxError('Only tab characters can indent')
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

    @property
    def indent_level(self):
        return self._indent_level

    def reset_indent_level(self):
        self._indent_level = 0
        return self._indent_level

    def decriment_indent_level(self):
        self._indent_level -= 1
        return self._indent_level

    def increment_indent_level(self):
        self._indent_level += 1
        return self._indent_level

    def eat_newline(self):
        self.reset_word()
        token = self.make_token(TokenType.NEWLINE, grammar.NEWLINE)
        self.reset_indent_level()
        self.increment_line_num()
        self.next_char()
        return token

    def skip_indent(self):
        while self.current_char is not None and self.current_char == "\t":
            self.reset_word()
            self.increment_indent_level()
            self.next_char()

    # def eat_indent(self):
    #     self.next_char()
    #     self.reset_word()
    #     self.increment_indent_level()
    #     return self.make_token(TokenType.INDENT, grammar.INDENT)

    def eof(self):
        return self.make_token(TokenType.EOF, LexerType.EOF)

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

    def get_next_token(self) -> Token:
        if self.current_char is None:
            return self.eof()

        if self.current_char == grammar.NEWLINE:
            return self.eat_newline()

        if self.current_char == "\t":
            self.skip_indent()

        if self.current_char.isspace() and self.current_char != "\t":
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
            return self.make_token(TokenType.STRING, self.reset_word())

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
            return self.make_token(TokenType.STRING, self.reset_word())

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
            return self.make_token(TokenType.OP, self.reset_word())

        if self.word_type == LexerType.ALPHANUMERIC:
            while (
                self.char_type == LexerType.ALPHANUMERIC
                or self.char_type == LexerType.NUMERIC
            ):
                self.word += self.current_char
                self.next_char()

            if self.word in grammar.OPERATORS:
                next_token = self.preview_token(1)
                if (
                    self.word in grammar.MULTI_WORD_OPERATORS
                    and (next_token.value if next_token else "")
                    in grammar.MULTI_WORD_OPERATORS
                ):
                    self.next_char()
                    self.word += " "
                    while (
                        self.char_type == LexerType.ALPHANUMERIC
                        or self.char_type == LexerType.NUMERIC
                    ):
                        self.word += self.current_char
                        self.next_char()
                    return self.make_token(TokenType.OP, self.reset_word())
                else:
                    return self.make_token(TokenType.OP, self.reset_word())

            if self.word in grammar.KEYWORDS:
                next_token = self.preview_token(1)
                if (
                    self.word in grammar.MULTI_WORD_KEYWORDS
                    and (next_token.value if next_token else "")
                    in grammar.MULTI_WORD_KEYWORDS
                ):
                    self.next_char()
                    self.word += " "
                    while (
                        self.char_type == LexerType.ALPHANUMERIC
                        or self.char_type == LexerType.NUMERIC
                    ):
                        self.word += self.current_char
                        self.next_char()
                    return self.make_token(TokenType.KEYWORD, self.reset_word())
                else:
                    return self.make_token(TokenType.KEYWORD, self.reset_word())
            elif self.word in grammar.TYPES:
                return self.make_token(TokenType.TYPE, self.reset_word())
            elif self.word in grammar.CONSTANTS:
                return self.make_token(TokenType.CONSTANT, self.reset_word())
            else:
                return self.make_token(TokenType.NAME, self.reset_word())

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
                # value = Decimal(value)
                value_type = grammar.DEC
            else:
                # value = int(value)
                value_type = grammar.INT
            return self.make_token(TokenType.NUMBER, value, value_type=value_type)

        if self.char_type == LexerType.ESCAPE:
            self.reset_word()
            self.next_char()
            line_num = self.line_num
            if self.current_char == grammar.NEWLINE:
                self.increment_line_num()
            self.next_char()
            return self.make_token(TokenType.ESCAPE, grammar.ESCAPE, line_num=line_num)

        raise SyntaxError("Unknown character")

    def analyze(self):
        token = self.get_next_token()
        while token.token_type != LexerType.EOF:
            yield token
            token = self.get_next_token()
        yield token


if __name__ == "__main__":
    file = "test.my"
    with open(file) as my_file:
        lexer = Lexer(my_file.read(), file)
        for t in lexer.analyze():
            if t.token_type == LexerType.NEWLINE:
                print(t, end="\n\n")
            else:
                print(t, end=" ")
