#pragma clang diagnostic ignored "-Wparentheses-equality"
#pragma clang diagnostic ignored "-Wunqualified-std-cast-call"
#include "bigint.hpp"
#include "boost_include.hpp"
#include "my_std_lib.hpp"
#include <iostream>
#include <memory>
#include <tuple>
using namespace std;

struct ContextFile {
  string path;
  File file;
  ContextFile(string path) {
    this->path = path;
    ;
    cout << "Opening file" << "\n";
    this->file = open(path);
    ;
  }

  File &enter__() {
    return this->file;
    ;
  }

  void exit__() {
    ;
    cout << "Closing file" << "\n";
    this->file.close();
  }
};
ostream &operator<<(ostream &outs, const ContextFile &contextfile) {
  return outs << "ContextFile {\n"
              << "    path: " << contextfile.path << "\n"
              << "    file: " << contextfile.file << "\n}";
}
int main(int argc, char *argv[]) {
  {
    bool tmp_caught__ = false;
    shared_ptr<ContextFile> tmp__(new ContextFile{"./.python-version"});
    try {
      auto my_file = &tmp__->enter__();

      ;
      cout << my_file->read() << "\n";
      ;
      cout << *my_file << "\n";

    } catch (exception &e) {
      tmp_caught__ = true;
      cerr << "Error: " << e.what() << "\n";
      tmp__->exit__();
      throw;
    }
    if (!tmp_caught__) {
      tmp__->exit__();
    }
  }
  return 0;
}
