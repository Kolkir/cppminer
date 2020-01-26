from clang.cindex import Index
from clang.cindex import CursorKind
from clang.cindex import TypeKind
import argparse
from pathlib import Path


def is_function(node):
    return node.kind in [CursorKind.FUNCTION_DECL,
                         CursorKind.FUNCTION_TEMPLATE]


def is_method(node):
    return node.kind in [CursorKind.CXX_METHOD]


def is_class(node):
    return node.kind in [CursorKind.CLASS_TEMPLATE,
                         CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION,
                         CursorKind.CLASS_DECL]


def main():
    print(CursorKind.get_all_kinds())
    args_parser = argparse.ArgumentParser(description='libclang test')

    args_parser.add_argument('Path',
                             metavar='path',
                             type=str,
                             help='the path to file')

    args = args_parser.parse_args()

    input_path = Path(args.Path).resolve().as_posix()

    index = Index.create()
    ast = index.parse(None, [input_path, '-x c++', '-std=c++17'])
    if not ast:
        args_parser.error('unable to load input')

    functions = [x for x in ast.cursor.get_children() if is_function(x)]
    classes = [x for x in ast.cursor.get_children() if is_class(x)]

    print('Functions:')
    for f in functions:
        print(f.spelling)

    print('')

    print('Classes:')
    for c in classes:
        print(c.spelling)
        methods = [x for x in c.get_children() if is_method(x)]
        for m in methods:
            print('\t' + m.spelling)


if __name__ == "__main__":
    main()
