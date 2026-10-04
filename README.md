# Mythril <img src="https://github.com/Ayehavgunne/Mythril/blob/gh-pages/mythril.png" width=40 />
A new multi-paradigm programming language. Right now it is being coded in Python by transpiling to C++.

This project is super early in development.

Some examples of the code for Mythril can be seen in the [example.my file](https://github.com/Ayehavgunne/Mythril/blob/master/example.my).
That is where I have been placing bits of test code as I work on various features.

## Goals:
* Learn about compilers, language design
* Create a Python like syntax and mix in some new language features and ideas. Basically Python with enforced types
* Make it more performant than Python but make sure it is just as easy to use
* Focus on designs that will reduce possible errors
* Choose defaults that are simple, easy and work despite possible performance overhead but make optimization easy. Example: use dynamic lists by default but allow creation of fixed size lists with a bit more notation

## Planned Features:
* Type Infrencing
* Pattern Matching
* First Class Functions
* Closures
* Classes
* Default to an accurate Decimal type and offer Floating Point as an option
* Default parameter values to functions
* Keyword arguments
* Design by Contract
* Builtin Testing
* Builtin Documentation
* Generators
* Comprehensions
* Context Managers
* Anonymous (multi statement) Functions
* Decorators
* Type Aliasing
* Slicing

## Influences
* Python
* Javascript
* C++
* Cobra
* V
