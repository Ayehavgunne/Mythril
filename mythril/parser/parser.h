#ifndef MYTHRIL_PARSER_H
#define MYTHRIL_PARSER_H

#include <vector>
#include "../lexer/lexer.h"
#include "node.h"

class Parser {
private:
	vector<Token> _tokens;
public:
	int pos = -1; // So that calling next_token the first time we will start at the zeroth index of _tokens
	Token current_token;
	int indent_level = 0;

	void next_token();
	int line_num();
	ProgramNode parse();
	bool match_type(TokenType token_type);
	bool match_value(const string&);
	static bool match_value(const string&, const Token&);
	static bool match_value(const string&, const Token&);
	BlockNode block();
	ExpressionNode expression();
	Token preview(int);
	NameNode get_name_node();

	map<string, int> precedence_map = {
		{"<", 10},
		{"+", 20},
		{"-", 20},
		{"*", 40},
	};

	explicit Parser(vector<Token>&);
};

#endif //MYTHRIL_PARSER_H
