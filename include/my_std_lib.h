#include <algorithm>
#include <vector>
#include <string>
#include <iostream>
#include <fstream>
#include <sstream>

inline const char * const bool_to_str(bool b) {
  return b ? "true" : "false";
}

template<typename T, typename V>
bool contains(std::vector<T, V> const & v, T x) {
    return find(v.begin(), v.end(), x) != v.end();
}

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

File open(std::string name) {
    return {name};
}
