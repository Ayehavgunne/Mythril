#ifndef MYTHRIL_NODE_H
#define MYTHRIL_NODE_H

#include <vector>
#include <string>

using namespace std;

struct Node {
	int line_num;
};

struct BlockNode : Node {
	vector<Node> children;
};

struct ProgramNode : Node {
	BlockNode body;
};

struct OperatorNode : Node {};

struct ExpressionNode : Node {};

struct NameNode : Node {};

struct UnaryOpNode : Node {
	OperatorNode op;
	ExpressionNode expr;
};

struct BinaryOpNode : Node {
	Node left;
	OperatorNode op;
	Node right;
};

struct ArgumentNode : Node {};
struct PositionalArgumentNode : ArgumentNode {};
struct KeywordArgumentNode : ArgumentNode {};

struct ClassNode : Node {};

struct FuncCallNode : Node {
	string name;
	vector<PositionalArgumentNode> positional_arguments;
	vector<KeywordArgumentNode> keyword_arguments;
};

struct MethodCallNode : FuncCallNode {
	ClassNode parent;
};

#endif //MYTHRIL_NODE_H
