import argparse
from pathlib import Path
from ast_parser import AstParser


def main():
    args_parser = argparse.ArgumentParser(description='cpp miner')

    args_parser.add_argument('Path',
                             metavar='path',
                             type=str,
                             help='the path to file')

    args_parser.add_argument('OutPath',
                             metavar='out',
                             type=str,
                             help='the output path')

    args = args_parser.parse_args()

    input_path = Path(args.Path).resolve().as_posix()
    print("File: " + input_path)

    output_path = Path(args.OutPath).resolve().as_posix()
    print("Output path: " + output_path)

    parser = AstParser()
    parser.parse(input_path, ["-x c++", "-std=c++17"])

    parser.save(output_path)


if __name__ == "__main__":
    main()
