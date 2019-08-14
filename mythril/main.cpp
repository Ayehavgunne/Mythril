#include "exceptions.h"
#include "lexer/lexer.h"
#include "parser/parser.h"
#include <fstream>
#include <iostream>
#include <string>

using namespace std;

int main(int arg_count, char **args) {
	string file_name = args[1];
	ifstream in_file;
	in_file.open(file_name);

	string file_contents;

	if (!in_file) {
		cerr << "Unable to open file " << file_name;
		exit(1);
	}

	char character;

	while ((character = in_file.get()) != EOF) {
		file_contents += character;
	}

	Lexer lexer(file_contents);
	try {
		lexer.analyze();
	}
	catch (SyntaxError &err) {
		cerr << err.what() << "\n";
		return 1;
	}

//	for (Token &token : lexer.tokens) {
//		if (token.type == TokenType::NEWLINE) {
//			cout << token << '\n';
//		}
//		else {
//			cout << token << ' ';
//		}
//	}

	Parser parser(lexer.tokens);
	ProgramNode root = parser.parse();

	return 0;
}