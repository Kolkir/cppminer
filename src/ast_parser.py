from clang.cindex import Index
from sample import Sample
from context import Context
from path import Path
from ast_utils import ast_to_graph, is_function, is_class, is_operator_token
from networkx.algorithms import shortest_path
from networkx.drawing.nx_agraph import write_dot
from itertools import permutations
import os
import re


def debug_save_graph(func_node, g):
    file_name = func_node.spelling + ".dot"
    num = 0
    while os.path.exists(file_name):
        file_name = func_node.spelling + str(num) + ".dot"
        num += 1
    write_dot(g, file_name)


class AstParser:
    def __init__(self):
        self.index = Index.create()
        self.samples = []
        self.token_id = 0
        self.tokens = dict()
        self.path_id = 0
        self.paths = dict()

    def parse(self, file_name, compiler_args):
        ast = self.index.parse(None, [file_name] + compiler_args)

        functions = [x for x in ast.cursor.get_children() if is_function(x)]
        for f in functions:
            self.__parse_function(f)

        classes = [x for x in ast.cursor.get_children() if is_class(x)]
        for c in classes:
            methods = [x for x in c.get_children() if is_function(x)]
            for m in methods:
                self.__parse_function(m)

    def save(self, out_path):
        with open(os.path.join(out_path, "tokens.c2s"), "w") as file:
            for token, key in self.tokens.items():
                file.write(str(key) + ":" + token + "\n")

        with open(os.path.join(out_path, "paths.c2s"), "w") as file:
            for path, key in self.paths.items():
                file.write(str(key) + ":" + str(path.tokens) + "\n")

        with open(os.path.join(out_path, "samples.c2s"), "w") as file:
            for sample in self.samples:
                file.write(str(sample) + "\n")

    def __parse_function(self, func_node):
        key = self.__tokenize(func_node.spelling)
        g = ast_to_graph(func_node)

        # debug_save_graph(func_node, g)

        terminal_nodes = [node for (node, degree) in g.degree() if degree == 1]

        contexts = []
        ends = permutations(terminal_nodes, 2)
        for start, end in ends:
            path = shortest_path(g, start, end)
            if path:
                path = path[1:-1]
                start_node = g.nodes[start]['label']
                end_node = g.nodes[end]['label']

                path_tokens = []
                for path_item in path:
                    path_node = g.nodes[path_item]['label']
                    path_tokens.append(self.__encode_token(path_node))

                context = Context(self.__tokenize(start_node), self.__tokenize(end_node),
                                  self.__encode_path(Path(path_tokens)))
                contexts.append(context)

        sample = Sample(key, contexts)
        self.samples.append(sample)

    def __encode_token(self, token):
        if token in self.tokens.keys():
            return self.tokens[token]
        else:
            self.token_id += 1
            self.tokens[token] = self.token_id
            return self.token_id

    def __encode_path(self, path):
        if path in self.paths.keys():
            return self.paths[path]
        else:
            self.path_id += 1
            self.paths[path] = self.path_id
            return self.path_id

    def __tokenize(self, name):
        if is_operator_token(name):
            return [self.__encode_token(name)]
        first_tokens = name.split('_')
        str_tokens = []
        for token in first_tokens:
            internal_tokens = re.findall('[a-z]+|[A-Z]+|[0-9]+', token)
            str_tokens += [t for t in internal_tokens if len(t) > 0]
        ret_tokens = []
        for token in str_tokens:
            ret_tokens.append(self.__encode_token(token))
        if len(ret_tokens) < 1:
            print("tokenize error")
        return ret_tokens
