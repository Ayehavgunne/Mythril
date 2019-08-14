#include "parser.h"
#include "../exceptions.h"
#include "../my_grammar.h"
#include "../util.h"

using namespace std;

Parser::Parser(vector<Token> &tokens) {
	_tokens = tokens;
	pos = 0;
	next_token();
}

void Parser::next_token() {
	pos += 1;
	current_token = _tokens[pos];
}

int Parser::line_num() {
	return current_token.line_num;
}

ProgramNode Parser::parse() {
	ProgramNode program_node = {};
	BlockNode top_block = block();
	while (current_token.type != TokenType::END_OF_FILE) {
		BlockNode current_block = block();
		top_block.children.reserve(
			top_block.children.size() + current_block.children.size()
		);
		top_block.children.insert(
			top_block.children.end(),
			current_block.children.begin(),
			current_block.children.end()
		);
	}
	if (current_token.type != TokenType::END_OF_FILE) {
		throw SyntaxError(
			"Unexpected end of program",
			current_token.line_num,
			current_token.value
		);
	}
	return program_node;
}

BlockNode Parser::block() {
	vector<Node> children;
	Node exp = expression();
	children.push_back(exp);

	if (current_token.type == TokenType::NEWLINE) {
		next_token();
	}

	while (current_token.indent_level == indent_level) {
		exp = expression();
		children.push_back(exp);
		if (current_token.type == TokenType::NEWLINE) {
			next_token();
		}
		else if (current_token.type == TokenType::END_OF_FILE) {
			break;
		}
	}

	BlockNode block_node = {};
	block_node.children=children,
	block_node.line_num=current_token.line_num;
	return block_node;
}

bool Parser::match_type(TokenType token_type) {
	return current_token.type == token_type;
}

bool Parser::match_value(const string &value) {
	return current_token.value == value;
}

bool Parser::match_value(const string &value, const Token &token) {
	return token.value == value;
}

ExpressionNode Parser::expression() {
	if (match_type(TokenType::NAME)) {
		NameNode name = get_name_node();
	}
}

Token Parser::preview(int num) {
	return _tokens[pos + num];
}

NameNode Parser::get_name_node() {
	if (in(grammar::KEYWORDS, current_token.value)) {
		// keyword
	}

	Token next_token = preview(1);
	if (match_value(grammar::LPAREN, next_token)) {
		// callable
	}
	else if (in(grammar::ASSIGNMENT_OP, next_token.value)) {
		// assignment
	}
	else if () {

	}
}
