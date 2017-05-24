# Mythril
A new multi-paradigm programming language

This is super early in development so please don't expect much yet.

## Goals:
  * Learn about compilers, LLVM, language design
  * Create a Python like syntax and mix in a whole lot of new language features and ideas
  * Use LLVM to make it more performant than Python but just as easy to use

## TODO
- [x] Keyword arguments
- [x] Argument default values
- [ ] Variable number of arguments (varargs) {Partialy done}
- [ ] Variable number of keyword arguments
- [ ] Signed Integers
- [x] Structs
- [ ] Classes
- [ ] Multiple Inheritance (for both classes and structs! Still considering alternatives however) 
- [ ] A Type system would most likely be good to have
- [ ] Enums
- [ ] Actors
- [ ] Tests built in ('test')
- [ ] Contracts built in ('require' and 'ensure')
- [ ] Exceptions
- [ ] Yielding
- [ ] Context Manager ('with' and 'as')
- [ ] Modules (importing with 'import' and 'from')
- [ ] Object literals
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
- [ ] Automatic integer(or number) casting on overflow
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
  * Pony
  * F#