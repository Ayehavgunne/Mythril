#pragma clang diagnostic ignored "-Wparentheses-equality"
#pragma clang diagnostic ignored "-Wunqualified-std-cast-call"
// #include "bigint.h"
// #include "my_std_lib.h"
#include <iostream>
#include <vector>
#include <memory>
#include <unordered_map>
using namespace std;

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

int main(int argc, char *argv[]) {
    shared_ptr<Dict<string, int>> dict(new Dict<string, int>({{"one", 1}, {"two", 2}, {"three", 3}, {"four", 4}, {"five", 5}}));
    cout << dict->get("six", 6) << "\n";

    for (auto value : dict->values()) {
        cout << value << "\n";
    }
    for (auto key : dict->keys()) {
        cout << key << "\n";
    }
    for (auto [key, value] : dict->items()) {
        cout << key << " " << value << "\n";
    }

    return 0;
}
