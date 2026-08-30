from typing import IO


class Preamble:
    def __init__(self, my_prog: IO[str]):
        self.my_prog = my_prog
        self.list = False
        self.range = False
        self.print = False

    def write(self) -> None:
        self.my_prog.write(
            '#pragma clang diagnostic ignored "-Wparentheses-equality"\n'
        )
        self.my_prog.write('#include "bigint.h"\n')
        if self.list:
            self.my_prog.write("#include <vector>\n")
        if self.range:
            self.my_prog.write("#include <ranges>\n")
        if self.print:
            self.my_prog.write("#include <iostream>\n")
        self.my_prog.write("using namespace std;\n\n")
