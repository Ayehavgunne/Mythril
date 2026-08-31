#include <algorithm>
#include <vector>
#include <string>
#include <iostream>

inline const char * const bool_to_str(bool b) {
  return b ? "true" : "false";
}

template<typename T, typename V>
bool contains(std::vector<T, V> const & v, T x) {
    return find(v.begin(), v.end(), x) != v.end();
}
