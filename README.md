# Mythril <img src="https://github.com/Ayehavgunne/Mythril/blob/gh-pages/Mythril.png" width=40 />
A new multi-paradigm programming language. This branch is an attempt to restart the project with C++.

This project is super early in development.

Some examples of the code for Mythril can be seen in the [example.my file](https://github.com/Ayehavgunne/Mythril/blob/c_plus_plus_restart/example.my).
That is where I have been placing bits of test code as I work on various features.

## Goals:
* Learn about compilers, LLVM, language design
* Create a Python like syntax and mix in a whole lot of new language features and ideas
* Use LLVM to make it more performant than Python but make sure it is just as easy to use
* Focus on designs that will reduce possible errors
* Choose defaults that are simple, easy and work despite possible performance overhead but make optimization easy. Example: use dynamic arrays by default but allow creation of fixed size arrays with a bit more notation

## Planned Features:
* Type Infrencing
* Strict Typing
* Pattern Matching
* First Class Functions
* Closures
* Classes
* Default to an accurate Decimal type and offer Float as an option
* Default parameter values to functions
* Keyword arguments
* Design by Contract
* Builtin Testing
* Builtin Documentation
* Array programming
* Generators
* Comprehensions
* Context Managers
* Anonymous (multi statement) Functions
* Decorators
* Type Aliasing
* Slicing

## TODO:
- [ ] Refactor, refactor, refactor
- [ ] Make a super cool logo
- [ ] Keyword arguments
- [ ] Parameter default values
- [ ] Variable number of arguments
- [ ] Variable number of keyword arguments
- [ ] Nested Functions
- [ ] Structs
- [ ] Classes
- [ ] Multiple inheritance or composition? Both? Favor composition somehow?
- [ ] A robust type system
- [ ] Enums
- [ ] A `nobreak` statement just like the `for else` loop in Python except it is called `nobreak` so it is clearer
- [ ] Tests built in (`test`)
- [ ] Contracts built in (`require` and `ensure`)
- [ ] Exceptions
- [ ] Yielding
- [ ] Context Manager (`with` and `as`)
- [ ] Modules (importing with `import` and `from`)
- [ ] Closures
- [ ] Anonymous (multi statement) functions
- [ ] Assigning functions to variables
- [ ] Properties (`getter` and `setter`)
- [ ] Decorators
- [ ] Delete things (`del`)
- [ ] Type Aliasing
- [ ] Bytes type
- [ ] Binary operators
- [ ] Complex number type
- [ ] Arrays
- [ ] Lists
- [ ] Slices
- [ ] Iterator unpacking
- [ ] Allow for double calling as in immediatly calling a function returned by a function ex: returns_function()()
- [ ] More Collection types (set, hashmap, linked list, trees, etc.)
- [ ] Pattern matching (`match`)
- [ ] Throw away variable using a single underscore character (be able to use it multiple times)
- [ ] Call C and/or Python functions from within Mythril, [example](http://eli.thegreenplace.net/2015/calling-back-into-python-from-llvmlite-jited-code/)
- [ ] Automatic integer(or number) promotion on overflow
- [ ] Support Unicode (UTF-8) by default
- [ ] Ignore underscores in numbers (as separators to increase readability)
- [ ] Add hexidecimal, octal, and binary literal representations of numbers
- [ ] Javadocs like documentation built in
- [x] DO NOT add a Null type
- [ ] Use an Option type instead of Null for sentinal values
- [ ] Implement Exhaustive Pattern Matching to help reduce potential errors

## Influences
* Python
* Javascript
* C/C++
* Julia
* Go
* Pony
* F#
* Cobra
* SQL
