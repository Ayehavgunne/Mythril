#include <iostream>
#include <fstream>
#include <string>
#include "lexer.h"
using namespace std;

int main(int arg_count, char **args) {
    string file_name = args[1];
    cout << "Reading File " << file_name << endl;
    ifstream in_file;
    in_file.open(file_name);

    string file_contents;

    if (!in_file) {
        cerr << "Unable to open file " << file_name;
        exit(1);
    }

    char character;

    while (in_file >> character) {
        file_contents += character;
    }

    Lexer lexer(file_contents);
    lexer.get_next_token();

    return 0;
}