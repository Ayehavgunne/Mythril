import sys
from io import StringIO

from lexer import Lexer
from parser import Parser
from preprocessor import Preprocessor
from src.my_ast import Program


def emit(tree: Program):
    my_str = StringIO()


def main():
    f = "test.my"
    with open(f) as my_file:
        code = my_file.read()
        lexer = Lexer(code, f)
        parser = Parser(lexer)
        tree = parser.parse()
        symtab_builder = Preprocessor(parser.file_name)
        symtab_builder.check(tree)
        if symtab_builder.warnings:
            sys.exit(1)
        emit(tree)
        

if __name__ == "__main__":
    main()