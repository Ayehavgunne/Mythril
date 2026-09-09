#include <algorithm>
#include <fstream>
#include <iostream>
#include <memory>
#include <set>
#include <span>
#include <sstream>
#include <string>
#include <vector>
using namespace std;

#ifdef __APPLE__
#include "TargetConditionals.h"
#ifdef TARGET_OS_MAC
#include "generator.h"
#endif
#else
#include <generator>
#endif

inline const char *const bool_to_str(bool b) {
    return b ? "true" : "false";
}

template <typename T, typename V>
bool contains(vector<T, V> const &v, T x) {
    return find(v.begin(), v.end(), x) != v.end();
}

bool contains(string my_str, string substring) {
    return my_str.contains(substring);
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

        while (getline(this->my_file, line)) {
            contents << line << '\n';
        }

        return contents.str();
    }

    void close() {
        this->my_file.close();
    }
};

File open(string name) {
    return {name};
}

template <typename T>
generator<T> range(T start, T end, T step) {
    T i = start;
    while (i <= end) {
        co_yield i;
        i = i + step;
    }
}

template <int left = 0, int right = 0, typename T>
constexpr auto slice(T &&container)
{
    if constexpr (right > 0) {
        return span(begin(forward<T>(container)) + left,
                    begin(forward<T>(container)) + right);
    } else {
        return span(begin(forward<T>(container)) + left,
                    end(forward<T>(container)) + right);
    }
}
