if __name__ == "__main__":
    from argparse import ArgumentParser

    from build import build_prog

    parser = ArgumentParser(
        prog="mythril",
        description="Compiler for the mythril programming language",
    )
    parser.add_argument("filename")
    parser.add_argument("-o", "--output")
    parser.add_argument("-p", "--print", action="store_true")
    parser.add_argument("-r", "--run", action="store_true")
    args = parser.parse_args()
    build_prog(args.filename, args.output, args.run, args.print)
