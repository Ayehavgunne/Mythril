#include <algorithm>
#include <vector>
#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <set>
#include <memory>
using namespace std;

#ifdef __APPLE__
    #include "TargetConditionals.h"
    #ifdef TARGET_OS_MAC
        #include "generator.h"
    #endif
#else
    #include <generator>
#endif

inline const char * const bool_to_str(bool b) {
  return b ? "true" : "false";
}

template<typename T, typename V>
bool contains(vector<T, V> const & v, T x) {
    return find(v.begin(), v.end(), x) != v.end();
}

struct File {
    fstream my_file;
    string path;

    File() {}
    
    File(string path) {
        this->path = path;
        this->my_file.open(path);
    }

    void write(string data) {
        this->my_file << data;
    }

    string read() {
        stringstream contents;
        string line;
        
        while ( getline (this->my_file, line) ) {
            contents << line << '\n';
        }

        return contents.str();
    }

    void close() {
        this->my_file.close();
    }
};

shared_ptr<File> open(string name) {
    return make_shared<File>(name);
}

template<typename T>
generator<T> range(T start, T end, T step) {
    T i = start;
    while (i < end) {
        co_yield i;
        i = i + step;
    }
}

// template<typename T>
// struct Set {
//     vector<T> _items;

//     void add(T item) {
//         if (this->contains(item)) {
//             return;
//         }
//         this->_items.push_back(item);
//     }

//     bool contains(T item) {
//         return find(this->_items.begin(), this->_items.end(), item) != this->_items.end();
//     }

//     void remove(T item) {
//         if (this->contains(item)) {
//             return;
//         }
//         this->_items.erase(remove(this->_items.begin(), this->_items.end(), item), this->_items.end());
//     }
// };

// template<typename T>
// Set<T> make_set() {
//     return {}
// }
