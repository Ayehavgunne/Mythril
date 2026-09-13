#pragma clang diagnostic ignored "-Wparentheses-equality"
#pragma clang diagnostic ignored "-Wunqualified-std-cast-call"
#include "bigint.h"
#include "my_std_lib.h"
#include <iostream>
#include <memory>
using namespace std;

struct ContextFile {
  string path;
  File file;
  ContextFile(string path) {
    this->path = path;
    cout << "Opening file" << "\n";
    this->file = open(path);
    ;
    cout << "File opened" << "\n";
    ;
  }

  File& enter__() {
    cout << "Enter" << "\n";
    return this->file;
  }

  void exit__() {
    ;
    cout << "Closing file" << "\n";
    this->file.close();
  }
};
int main(int argc, char *argv[]) {
  {
    shared_ptr<ContextFile> tmp__(new ContextFile{"./todo.md"});
    auto my_file = &tmp__->enter__();

    cout << my_file->read() << "\n";

    tmp__->exit__();
  };
  return 0;
}