import argparse
from pathlib import Path
from ast_parser import AstParser


def main():
    args_parser = argparse.ArgumentParser(description='cpp miner')

    args_parser.add_argument('Path',
                             metavar='path',
                             type=str,
                             help='the path to file')

    args = args_parser.parse_args()

    input_path = Path(args.Path).resolve().as_posix()
    print("File: " + input_path)

    parser = AstParser()
    parser.parse(input_path, ["-x c++", "-std=c++17"])


if __name__ == "__main__":
    main()
