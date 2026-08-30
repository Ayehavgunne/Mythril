if __name__ == "__main__":
    from enum import StrEnum
    from argparse import ArgumentParser

    from build import build_prog

    class OptimizationLevel(StrEnum):
        O0 = "base"
        O1 = "1"
        O2 = "2"
        O3 = "3"
        OFAST = "fast"
        OZ = "z"

    opt_map = {
        None: "-O0",
        OptimizationLevel.O0: "-O0",
        OptimizationLevel.O1: "-O1",
        OptimizationLevel.O2: "-O2",
        OptimizationLevel.O3: "-O3",
        OptimizationLevel.OFAST: "-O3 -ffast-math",
        OptimizationLevel.OZ: "-Oz",
    }

    parser = ArgumentParser(
        prog="mythril",
        description="Compiler for the mythril programming language",
    )
    parser.add_argument("filename")
    parser.add_argument("-o", "--output")
    parser.add_argument("-p", "--print", action="store_true")
    parser.add_argument("-r", "--run", action="store_true")
    parser.add_argument("--optimization", type=OptimizationLevel)
    parser.add_argument("--ignore_warnings", action="store_true")
    args = parser.parse_args()
    build_prog(
        args.filename, args.output, args.run, args.print, opt_map[args.optimization], args.ignore_warnings
    )
