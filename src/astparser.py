from clang.cindex import Index
from clang.cindex import CursorKind
from sample import Sample
import re


def is_function(node):
    return node.kind in [CursorKind.FUNCTION_DECL,
                         CursorKind.FUNCTION_TEMPLATE]


def is_method(node):
    return node.kind in [CursorKind.CXX_METHOD]


def is_class(node):
    return node.kind in [CursorKind.CLASS_TEMPLATE,
                         CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION,
                         CursorKind.CLASS_DECL]


class AstParser:
    def __init__(self):
        self.index = Index.create()
        self.samples = []
        self.tokens = dict()
        self.token_id = 0

    def parse(self, file_name, compiler_args):
        ast = self.index.parse(None, [file_name] + compiler_args)

        functions = [x for x in ast.cursor.get_children() if is_function(x)]
        for f in functions:
            self.__parse_function(f)

        classes = [x for x in ast.cursor.get_children() if is_class(x)]
        for c in classes:
            methods = [x for x in c.get_children() if is_method(x)]
            for m in methods:
                self.__parse_function(m)

    def __parse_function(self, func_node):
        key = self.__tokenize(func_node.spelling)
        print("Function " + str(key) + " " + func_node.spelling)
        terminal_nodes = self.__get_terminal_nodes(func_node)
        paths = self.__get_paths(func_node, terminal_nodes)
        sample = Sample(key, paths)
        self.samples.append(sample)

    def encode_token(self, token):
        if token in self.tokens.keys():
            return self.tokens[token]
        else:
            self.token_id += 1
            self.tokens[token] = self.token_id
            return self.token_id

    def __tokenize(self, name):
        first_tokens = name.split('_')
        str_tokens = []
        for token in first_tokens:
            internal_tokens = re.findall('^[a-z]+|[A-Z][^A-Z]*', token)
            str_tokens += internal_tokens
        tokens = []
        for token in str_tokens:
            tokens.append(self.encode_token(token))
        return tokens

    def __get_terminal_nodes(self, func_node):
        terminal_nodes = []

        def get_trem_nodes(nodes, out_nodes):
            for n in nodes:
                children = list(n.get_children())
                if len(children) == 0:
                    out_nodes.append(n)                    
                else:
                    get_trem_nodes(children, out_nodes)

        get_trem_nodes(list(func_node.get_children()), terminal_nodes)
        return terminal_nodes

    def __get_paths(self, func_node, terminal_nodes):
        # TODO: Implement
        paths = []
        return paths
