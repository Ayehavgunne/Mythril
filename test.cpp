#pragma clang diagnostic ignored "-Wparentheses-equality"
#pragma clang diagnostic ignored "-Wunqualified-std-cast-call"
#include "bigint.h"
#include "my_std_lib.h"
#include <format>
#include <iostream>
#include <memory>
#include <ranges>
#include <tuple>
#include <vector>
#include <coroutine>

#ifdef __APPLE__
#include "TargetConditionals.h"
#ifdef TARGET_OS_MAC
#include "generator.h"
#endif
#else
#include <generator>
#endif

using namespace std;

BigInt::bigint my_gen();
shared_ptr<BigInt::bigint> plus_five(BigInt::bigint num);
shared_ptr<BigInt::bigint> fib(BigInt::bigint n);
BigInt::bigint my_gen() {
  ;
  for (auto &x : range(BigInt::bigint("0"), BigInt::bigint("10"), BigInt::bigint("1"))) {
    co_yield (x * BigInt::bigint("2"));
  };
}

shared_ptr<BigInt::bigint> plus_five(BigInt::bigint num) {
  return make_shared<BigInt::bigint>((num + BigInt::bigint("5")));
  ;
}

shared_ptr<BigInt::bigint> fib(BigInt::bigint n) {
  auto a(make_shared<BigInt::bigint>(BigInt::bigint("0")));
  auto b(make_shared<BigInt::bigint>(BigInt::bigint("1")));
  ;
  for (auto &_ : range(BigInt::bigint("0"), n, BigInt::bigint("1"))) {
    auto prev_a(*a);
    *a = *b;
    *b = (prev_a + *b);
  }
  return make_shared<BigInt::bigint>(*a);
  ;
}

struct Circle {
  BigInt::bigint radius;
  BigInt::bigint x;
  BigInt::bigint y;
};
ostream &operator<<(ostream &outs, const Circle &circle) {
  return outs << "Circle {\n"
              << "    radius: " << circle.radius << "\n"
              << "    x: " << circle.x << "\n"
              << "    y: " << circle.y << "\n}";
}
struct ContextFile {
  string path;
  File file;
  ContextFile(string path) {
    this->path = path;
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
int main(int argc, char *argv[]) {
  ;
  for (auto &x : *my_gen()) {
    ;
    cout << x << "\n";
  }
  shared_ptr<vector<BigInt::bigint>> my_list(new vector<BigInt::bigint>(
      {BigInt::bigint("1"), BigInt::bigint("2"), BigInt::bigint("3"),
       BigInt::bigint("4"), BigInt::bigint("5"), BigInt::bigint("6"),
       BigInt::bigint("7"), BigInt::bigint("8"), BigInt::bigint("9"),
       BigInt::bigint("10")}));
  ;
  shared_ptr<span<BigInt::bigint>> sublist(
      new span<BigInt::bigint>(slice(*my_list, 2, 6)));
  ;
  ;
  for (auto &item : *sublist) {
    ;
    cout << item << "\n";
  };
  cout << "\n";
  auto num(make_shared<BigInt::bigint>(BigInt::bigint("1")));
  ;
  ;
  cout << *num << "\n";
  ;
  cout << "\n";
  ;
  cout << "\n";
  {
    bool tmp_caught__ = false;
    shared_ptr<ContextFile> tmp__(new ContextFile{"./todo.md"});
    try {
      auto my_file = &tmp__->enter__();

      ;
      cout << my_file->read() << "\n";

    } catch (exception &e) {
      tmp_caught__ = true;
      cerr << "Error: " << e.what() << "\n";
      tmp__->exit__();
      throw;
    }
    if (!tmp_caught__) {
      tmp__->exit__();
    }
  };
  cout << "\n";
  shared_ptr<vector<BigInt::bigint>> things(new vector<BigInt::bigint>(
      {BigInt::bigint("1"), BigInt::bigint("2"), BigInt::bigint("3")}));
  ;
  ;
  for (auto &item : *things) {
    ;
    cout << item << "\n";
  };
  cout << "\n";
  shared_ptr<tuple<BigInt::bigint, string>> other_things(
      new tuple<BigInt::bigint, string>(
          make_tuple(BigInt::bigint("1"), "Hello")));
  ;
  shared_ptr<Dict<string, string>> stuff(new Dict<string, string>(
      {{"first_name", "Samus"}, {"last_name", "Aran"}}));
  ;
  ;
  cout << (*things)[1] << "\n";
  ;
  cout << "\n";
  ;
  cout << get<0>((*other_things)) << "\n";
  ;
  cout << "\n";
  ;
  cout << (*stuff)["first_name"] << "\n";
  ;
  cout << "\n";
  ;
  if (contains(*things, BigInt::bigint("2"))) {
    ;
    cout << "yes" << "\n";
  };
  if (!contains(*things, BigInt::bigint("2"))) {
    ;
    cout << "no" << "\n";
  };
  cout << "\n";
  auto name(make_shared<string>("anthony"));
  ;
  ;
  if (contains(*name, "an")) {
    ;
    cout << format("Name '{}' has 'an' in it", string(*name)) << "\n";
  };
  cout << "\n";
  shared_ptr<string> short_name(new string(slice(*name, 0, -3)));
  ;
  ;
  cout << *short_name << "\n";
  ;
  cout << "\n";
  auto number(make_shared<BigInt::bigint>(BigInt::bigint("10")));
  ;
  ;
  while ((*number > BigInt::bigint("1"))) {
    ;
    *number -= BigInt::bigint("1");
    ;
    if ((*number == BigInt::bigint("5"))) {
      ;
      continue;
    };
    if ((*number == BigInt::bigint("2"))) {
      ;
      break;
    };
    cout << *number << "\n";
  };
  cout << "\n";
  ;
  for (auto &x :
       range(BigInt::bigint("0"), BigInt::bigint("40"), BigInt::bigint("1"))) {
    ;
    cout << x << "\n";
  };
  cout << "\n";
  *number = BigInt::bigint("22");
  ;
  if ((*number > BigInt::bigint("23"))) {
    ;
    cout << "greater than 23" << "\n";
  } else if ((*number == BigInt::bigint("23"))) {
    ;
    cout << "equals 23" << "\n";
  } else {
    ;
    cout << "less than 23" << "\n";
  };
  cout << "\n";
  ;
  cout << *plus_five(BigInt::bigint("2")) << "\n";
  ;
  cout << "\n";
  ;
  cout << *fib(BigInt::bigint("10")) << "\n";
  ;
  cout << "\n";
  ;
  cout << "🍌" << "\n";
  ;
  cout << "\n";
  shared_ptr<Circle> cir(new Circle(
      {BigInt::bigint("5"), BigInt::bigint("2"), BigInt::bigint("4")}));
  ;
  ;
  cout << cir->radius << "\n";
  ;
  cout << "\n";
  ;
  cout << *cir << "\n";
  ;
  cout << "\n";
  auto y(make_shared<BigInt::bigint>(BigInt::bigint("10")));
  ;
  ;
  for (auto &x : range(BigInt::bigint("0"), (*y + BigInt::bigint("1")),
                       BigInt::bigint("1"))) {
    ;
    cout << (((string)x + " ") + (string)*fib(x)) << "\n";
  };
  cout << "\n";
  ;
  cout << (*things)[(1 + 1)] << "\n";
  ;
  cout << "\n";
  auto yes(true);
  ;
  auto no(false);
  ;
  auto h(make_shared<BigInt::bigint>(BigInt::bigint("5")));
  ;
  auto g(make_shared<float>(0.1));
  ;
  ;
  if (no) {
    *g = 2.6;

    ;
    if ((yes && no)) {
      ;
      *h += *h;
    }
  } else if (yes) {
    *g = 3.6;
  } else {
    *g = 7.6;
  };
  cout << *h << "\n";
  ;
  cout << "\n";
  ;
  cout << *g << "\n";
  ;
  cout << "\n";
  ;
  shared_ptr<string> prompt(new string());
  cout << "enter your fav color" << '\n';
  cin >> *prompt;
  ;
  cout << format("Wow, your fav color is {}?!", string(*prompt)) << "\n";
  return 0;
}
