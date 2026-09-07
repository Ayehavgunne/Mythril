#include <sstream>
#include <iostream>
#include <string>
#include <fstream>
#include <memory>
using namespace std;

struct File {
    std::fstream my_file;
    std::string path;
    
    File(std::string path) {
        this->path = path;
        this->my_file.open(path);
    }

    void write(std::string data) {
        this->my_file << data;
    }

    std::string read() {
        std::stringstream contents;
        std::string line;
        
        while ( getline (this->my_file, line) ) {
            contents << line << '\n';
        }

        return contents.str();
    }

    void close() {
        this->my_file.close();
    }
};

shared_ptr<File> open(std::string name) {
    return make_shared<File>(name);
}

struct ContextFile {
  shared_ptr<File> file;

  ContextFile() {}
  ContextFile(string path) {
    this->file = open(path);
  }

  shared_ptr<File> enter(string path) {
    cout << "opening file" << "\n";
    this->file = open(path);
    return this->file;
  }

  void exit() {
    cout << "closing file" << "\n";
    this->file->close();
  }
};

int main(int argc, char *argv[]) {
  {
    shared_ptr<ContextFile> __tmp = make_shared<ContextFile>();
    shared_ptr<File> todo_file = __tmp->enter("./todo.md");
    cout << todo_file->read() << "\n";

    __tmp->exit();
  }

  cout << "done" << "\n";

  return 0;
}