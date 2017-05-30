# Mythril <img src="https://github.com/Ayehavgunne/Mythril/blob/gh-pages/Mythril.png" width=40 />
A new multi-paradigm programming language. Right now it is being coded in Python using llvmlite.

This project is super early in development.

Some examples of the code for Mythril can be seen in the [example.my file](https://github.com/Ayehavgunne/Mythril/blob/master/example.my).
That is where I have been placing bits of test code as I work on various features.

## Goals:
* Learn about compilers, LLVM, language design
* Create a Python like syntax and mix in a whole lot of new language features and ideas
* Use LLVM to make it more performant than Python but just as easy to use
* Focus on designs that will reduce possible errors

## Planned Features:
* Type Infrencing
* Pattern Matching
* First Class Functions
* Classes
* Actors
* Default to an accurate Decimal type and offer Floating Point as an option
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
* Multiple Dispatch

## TODO:
- [ ] Make a super cool logo
- [x] Keyword arguments
- [x] Parameter default values
- [ ] Variable number of arguments (varargs) {Partialy done}
- [ ] Variable number of keyword arguments
- [ ] Signed Integers
- [x] Structs
- [ ] Classes
- [ ] Multiple Inheritance (for both classes and structs! Considering alternatives) 
- [ ] A more robust Type System would most likely be good to have
- [ ] Enums
- [ ] Actors
- [ ] Single quote strings for Interpolation and Double quote strings for literals
- [ ] Tests built in ('test')
- [ ] Contracts built in ('require' and 'ensure')
- [ ] Exceptions (Looking at alternatives)
- [ ] Yielding
- [ ] Context Manager ('with' and 'as')
- [ ] Modules (importing with 'import' and 'from')
- [ ] Closures
- [ ] Anonymous (multi statement) functions
- [x] Assigning functions to variables
- [ ] Properties ('getter' and 'setter')
- [ ] Decorators
- [ ] Delete things ('del')
- [ ] Type Aliasing
- [ ] Bytes type
- [ ] Binary operators
- [ ] Complex number type
- [ ] Slices
- [ ] Tuple unpacking
- [ ] Allow for double calling as in immediatly calling a function returned by a function ex: returns_function()()
- [ ] More Collection types (set, hashmap, tuple, linked list, trees, etc.)
- [ ] Pattern matching ('match')
- [ ] Throw away variable using a single underscore character (be able to use it multiple times)
- [ ] Call C and/or Python functions from within Mythril [Example](http://eli.thegreenplace.net/2015/calling-back-into-python-from-llvmlite-jited-code/)
- [ ] Automatic integer(or number) promotion on overflow
- [ ] Support Unicode (UTF-8) by default
- [ ] Multiple dispatch
- [ ] Ignore underscores in numbers (as separators to increase readability)
- [ ] Add hexidecimal, octal, and binary literal representations of numbers
- [ ] Javadocs like documentation built in
- [x] DO NOT add a Null type
- [ ] Use an Option type instead of Null for sentinal values
- [ ] Do Exhaustive Pattern Matching to help reduce errors

## Influences
* Python
* Javascript
* Java
* Julia
* Go
* Pony
* F#
* Cobra
