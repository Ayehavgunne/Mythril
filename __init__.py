if __name__ == '__main__':
	from my_lexer import Lexer
	from my_parser import Parser
	from my_symbol_table_builder import SymbolTableBuilder
	from compiler.my_compiler import CodeGenerator
	file = 'test.my'
	code = open(file).read()
	lexer = Lexer(code, file)
	parser = Parser(lexer)
	t = parser.parse()
	symtab_builder = SymbolTableBuilder(parser.file_name)
	symtab_builder.check(t)
	if not symtab_builder.warnings:
		generator = CodeGenerator(parser.file_name)
		generator.generate_code(t)
		# generator.evaluate(True, True)
		# generator.evaluate(True, False)
		generator.evaluate(False, True)
		# generator.evaluate(False, False)
		#
		# generator.compile(file[:-3], True, True)
	else:
		print('Did not run')
