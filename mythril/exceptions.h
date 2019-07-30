#ifndef MYTHRIL_EXCEPTIONS_H
#define MYTHRIL_EXCEPTIONS_H

#include <exception>
#include <string>

using namespace std;

struct SyntaxError : public exception {
private:
	string _message;
	int _line_num;
	char _character;
public:
	explicit SyntaxError(const string &message, int line_num, char character) {
		_message = message;
		_line_num = line_num;
		_character = character;
	}

	string what() {
		return "Syntax Error: " + _message + " Line: " + to_string(_line_num) + " -> " + _character;
	}
};

#endif
