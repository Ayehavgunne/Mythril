# Mythril <img src="https://github.com/Ayehavgunne/Mythril/blob/gh-pages/mythril_light.png" width=40 />
A new multi-paradigm programming language. Right now it is being coded in Python by transpiling to C++.

This project is super early in development.

Some examples of the code for Mythril can be seen in the [example.my file](https://github.com/Ayehavgunne/Mythril/blob/master/example.my).
That is where I have been placing bits of test code as I work on various features.

The main inspiration is Python with some ideas from a couple other languages thrown in.

## Priorities in order of importance:
* Principal of least astonishment (surprise) - POLA
* Sane defaults
* Correctness
* Ease of use
* Flexibility
* Be more performant than Python (not a hard bar to clear)
* Make higher performance possible through more specificity/explicitnes (make the risky operations OPT INT / make the default safety OPT OUT)
* (Append) Zen of Python

## Planned Features:
* Type Infrence
* Pattern Matching
* First Class Functions
* Closures
* Classes
* Protocols (Structural typing)
* Default to BigInt and offer sized Ints as an option
* Default to an infinitely precise Decimal type and offer normal Floating Point as an opt in option
* Default parameter values to functions
* Keyword arguments
* Design by Contract
* Builtin Testing
* Builtin Documentation
* Generators
* Comprehensions
* Context Managers
* Anonymous (multi-statement) Functions
* Decorators
* Slicing
* Type Aliasing

## Influences
* Python
* Javascript
* C++
* Cobra
* V
