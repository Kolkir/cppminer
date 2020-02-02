from clang.cindex import Index
from sample import Sample
from ast_utils import ast_to_graph, is_function, is_class, is_method
from networkx.algorithms import shortest_path
from networkx.drawing.nx_agraph import write_dot
from itertools import permutations
import re


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
        write_dot(g, func_node.spelling + ".dot")

        terminal_nodes = [node for (node, degree) in g.degree() if degree == 1]

        contexts = []
        ends = permutations(terminal_nodes, 2)
        for start, end in ends:
            path = shortest_path(g, start, end)
            if path:
                path = path[1:-1]
                start_node = g.nodes[start]['label']
                end_node = g.nodes[end]['label']
                for path_item in path:
                    path_node = g.nodes[path_item]['label']

        sample = Sample(key, contexts)
        self.samples.append(sample)

    def __encode_token(self, token):
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
            tokens.append(self.__encode_token(token))
        return tokens
