if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser
    from preprocessor import Preprocessor

    file = "test.my"
    with open(file) as my_file:
        code = my_file.read()
        lexer = Lexer(code, file)
        parser = Parser(lexer)
        t = parser.parse()
        symtab_builder = Preprocessor(parser.file_name)
        symtab_builder.check(t)
