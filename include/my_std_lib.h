#include <algorithm>
#include <fstream>
#include <iostream>
#include <memory>
#include <set>
#include <span>
#include <sstream>
#include <string>
#include <vector>
#include <unordered_map>
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
    shared_ptr<fstream> my_file;
    string path;

    File() {}
    File(string path) {
        this->path = path;
        this->my_file->open(path);
    }

    void write(string data) {
        *this->my_file << data;
    }

    string read() {
        stringstream contents;
        string line;

        while (getline(*this->my_file, line)) {
            contents << line << '\n';
        }

        return contents.str();
    }

    shared_ptr<fstream> __enter(string path) {
        this->path = path;
        this->my_file->open(path);
        return this->my_file;
    }

    void __exit() {
        this->close();
    }

    void close() {
        this->my_file->close();
    }
};

File open(string name) {
    return {name};
}

template <typename T>
generator<T> range(T start, T end, T step) {
    T i = start;
    while (i < end) {
        co_yield i;
        i = i + step;
    }
}

string slice(string str, int left, int right) {
    if (right < 0) {
        right = str.length() + right;
    }
    return str.substr(left, right - left);
}

template <typename T>
constexpr auto slice(T &&container, int left, int right) {
    if (right > 0) {
        return span(begin(forward<T>(container)) + left,
                    begin(forward<T>(container)) + right);
    } else {
        return span(begin(forward<T>(container)) + left,
                    end(forward<T>(container)) + right);
    }
}

template <typename K, typename V>
struct Dict {
private:
    unordered_map<K, V> map_;
    vector<K> keys_;

public:
    Dict(vector<tuple<K, V>> data) {
        for (auto [key, value] : data) {
            this->keys_.push_back(key);
            this->map_[key] = value;
        }
    }

    V operator [](K key) {
        return this->map_[key];
    }

    vector<K>::iterator begin() {
        return this->keys_.begin();
    }

    vector<K>::iterator end() {
        return this->keys_.end();
    }

    vector<K> keys() {
        return this->keys_;
    }

    vector<V> values() {
        vector<V> values;
        for (auto key : this->keys_) {
            values.push_back(this->map_[key]);
        }
        return values;
    }

    vector<tuple<K, V>> items() {
        vector<tuple<K, V>> items;
        for (auto key : this->keys_) {
            items.push_back({key, this->map_[key]});
        }
        return items;
    }

    V get(K key, V fallback) {
        try {
            return this->map_.at(key);
        } catch (out_of_range _) {
            return fallback;
        }
    }

    V get(K key) {
        return this->map_.at(key);
    }
};
