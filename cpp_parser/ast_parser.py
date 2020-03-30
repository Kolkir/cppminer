from clang.cindex import Index
from .sample import Sample
from .context import Context
from .path import Path
from .ast_utils import ast_to_graph, is_function, is_class, is_operator_token, is_namespace
from networkx.algorithms import shortest_path
from networkx.drawing.nx_agraph import to_agraph
from itertools import combinations
import uuid
import os
import re
import random


def debug_save_graph(func_node, g):
    file_name = func_node.spelling + ".png"
    num = 0
    while os.path.exists(file_name):
        file_name = func_node.spelling + str(num) + ".png"
        num += 1
    a = to_agraph(g)
    a.draw(file_name, prog='dot')
    a.clear()


def tokenize(name, max_subtokens_num):
    if is_operator_token(name):
        return [name]
    first_tokens = name.split('_')
    str_tokens = []
    for token in first_tokens:
        internal_tokens = re.findall('[a-z]+|[A-Z]+[a-z]*|[0-9.]+|[-*/&|%=()]+', token)
        str_tokens += [t for t in internal_tokens if len(t) > 0]
    assert len(str_tokens) > 0, "Can't tokenize expr: {0}".format(name)
    if max_subtokens_num != 0:
        str_tokens = str_tokens[:max_subtokens_num]
    return str_tokens


class AstParser:
    def __init__(self, max_contexts_num, max_path_len, max_subtokens_num, max_ast_depth, out_path):
        self.validate = False
        self.save_buffer_size = 1000
        self.out_path = out_path
        self.max_subtokens_num = max_subtokens_num
        self.max_contexts_num = max_contexts_num
        self.max_path_len = max_path_len
        self.max_ast_depth = max_ast_depth
        self.index = Index.create()
        self.samples = set()
        self.header_only_functions = set()

    def __del__(self):
        self.save()

    def __parse_node(self, node):
        namespaces = [x for x in node.get_children() if is_namespace(x)]
        for n in namespaces:
            # ignore standard library functions
            if n.displayname != 'std' and not n.displayname.startswith('__'):
                self.__parse_node(n)

        functions = [x for x in node.get_children() if is_function(x)]
        for f in functions:
            self.__parse_function(f)

        classes = [x for x in node.get_children() if is_class(x)]
        for c in classes:
            methods = [x for x in c.get_children() if is_function(x)]
            for m in methods:
                self.__parse_function(m)

        self.__dump_samples()

    def parse(self, compiler_args, file_path=None):
        ast = self.index.parse(file_path, compiler_args)
        self.__parse_node(ast.cursor)

    def __dump_samples(self):
        if len(self.samples) >= self.save_buffer_size:
            self.save()

    def save(self):
        if not self.out_path:
            return
        if not os.path.exists(self.out_path):
            os.makedirs(self.out_path)
        if len(self.samples) > 0:
            file_name = os.path.join(self.out_path, str(uuid.uuid4().hex) + ".c2s")
            # print(file_name)
            with open(file_name, "w") as file:
                for sample in self.samples:
                    file.write(str(sample.source_mark) + str(sample) + "\n")
            self.samples.clear()

    def __parse_function(self, func_node):
        try:
            # ignore standard library functions
            if func_node.displayname.startswith('__'):
                return

            # detect header only function duplicates
            file_name = func_node.location.file.name
            source_mark = (file_name, func_node.extent.start.line)
            if file_name.endswith('.h') and func_node.is_definition:
                # print('Header only function: {0}'.format(func_node.displayname))
                if source_mark in self.header_only_functions:
                    # print('Duplicate')
                    return
                else:
                    self.header_only_functions.add(source_mark)

            key = tokenize(func_node.spelling, self.max_subtokens_num)
            g = ast_to_graph(func_node, self.max_ast_depth)

            # debug_save_graph(func_node, g)

            terminal_nodes = [node for (node, degree) in g.degree() if degree == 1]
            random.shuffle(terminal_nodes)

            contexts = set()
            ends = combinations(terminal_nodes, 2)

            for start, end in ends:
                path = shortest_path(g, start, end)
                if path:
                    if self.max_path_len != 0 and len(path) > self.max_path_len:
                        continue  # skip too long paths
                    path = path[1:-1]
                    start_node = g.nodes[start]['label']
                    end_node = g.nodes[end]['label']

                    path_tokens = []
                    for path_item in path:
                        path_node = g.nodes[path_item]['label']
                        path_tokens.append(path_node)

                    context = Context(tokenize(start_node, self.max_subtokens_num),
                                      tokenize(end_node, self.max_subtokens_num),
                                      Path(path_tokens, self.validate), self.validate)
                    contexts.add(context)
                if len(contexts) > self.max_contexts_num:
                    break

            if len(contexts) > 0:
                sample = Sample(key, contexts, source_mark, self.validate)
                self.samples.add(sample)
        except Exception as e:
            # skip unknown cursor exceptions
            if 'Unknown template argument kind' not in str(e):
                print('Failed to parse function : ')
                print('Filename : ' + func_node.location.file.name)
                print('Start {0}:{1}'.format(func_node.extent.start.line, func_node.extent.start.column))
                print('End {0}:{1}'.format(func_node.extent.end.line, func_node.extent.end.column))
                print(e)
