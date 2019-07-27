cmake_minimum_required(VERSION 3.14)
project(Mythril)

set(CMAKE_CXX_STANDARD 14)

add_executable(mythril mythril/main.cpp mythril/lexer.cpp mythril/lexer.h mythril/my_types.cpp mythril/my_types.h)