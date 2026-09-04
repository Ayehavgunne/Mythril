from typing import IO


class Preamble:
    def __init__(self, my_prog: IO[str]):
        self.my_prog = my_prog
        self.list = False
        self.range = False
        self.print = False
        self.format = False
        self.files = False
        self.map = False
        self.set = False

    def write(self) -> None:
        self.my_prog.write(
            '#pragma clang diagnostic ignored "-Wparentheses-equality"\n'
        )
        self.my_prog.write('#include "my_std_lib.h"\n')
        self.my_prog.write('#include "bigint.h"\n')
        # self.my_prog.write("#include <iostream>\n")
        # self.my_prog.write("#include <iterator>\n")
        if self.list:
            self.my_prog.write("#include <vector>\n")
        if self.map:
            self.my_prog.write("#include <unordered_map>\n")
        if self.set:
            self.my_prog.write("#include <set>\n")
        if self.files:
            self.my_prog.write("#include <fstream>\n")
        if self.range:
            self.my_prog.write("#include <ranges>\n")
        if self.format:
            self.my_prog.write("#include <format>\n")
        if self.print:
            self.my_prog.write("#include <iostream>\n")
        self.my_prog.write("using namespace std;\n\n")
