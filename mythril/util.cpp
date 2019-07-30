#include <string>
#include <vector>
#include "util.h"

using namespace std;

bool in(const vector<string> &container, const string &element) {
	return find(container.begin(), container.end(), element) != container.end();
}
