from clang.cindex import Index
from clang.cindex import CursorKind
from sample import Sample
from ast_utils import ast_to_graph
from networkx.algorithms import shortest_path
from itertools import permutations
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
        g = ast_to_graph(func_node)

        terminal_nodes = [node for (node, degree) in g.degree() if degree == 1]

        contexts = []
        ends = permutations(terminal_nodes, 2)
        for start, end in ends:
            path = shortest_path(g, start, end)
            if path:
                path = path[1:-1]
                start_node = g.nodes[start]['node']
                end_node = g.nodes[end]['node']
                for path_item in path:
                    path_node = g.nodes[path_item]['node']

        sample = Sample(key, contexts)
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
