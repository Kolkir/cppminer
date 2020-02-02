import networkx as nx
import uuid
from clang.cindex import CursorKind


def is_function(node):
    return node.kind in [CursorKind.FUNCTION_DECL,
                         CursorKind.FUNCTION_TEMPLATE]


def is_method(node):
    return node.kind in [CursorKind.CXX_METHOD]


def is_class(node):
    return node.kind in [CursorKind.CLASS_TEMPLATE,
                         CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION,
                         CursorKind.CLASS_DECL]


def is_literal(node):
    return node.kind in [CursorKind.INTEGER_LITERAL,
                         CursorKind.FLOATING_LITERAL,
                         CursorKind.IMAGINARY_LITERAL,
                         CursorKind.STRING_LITERAL,
                         CursorKind.CHARACTER_LITERAL]


def is_reference(node):
    return node.kind in [CursorKind.DECL_REF_EXPR, CursorKind.MEMBER_REF_EXPR]


def is_operator(node):
    return node.kind in [CursorKind.BINARY_OPERATOR,
                         CursorKind.UNARY_OPERATOR,
                         CursorKind.COMPOUND_ASSIGNMENT_OPERATOR]


def is_call_expr(node):
    return node.kind == CursorKind.CALL_EXPR


def get_id():
    node_id = uuid.uuid1()
    return node_id.int


def add_node(ast_node, graph):
    node_id = ast_node.hash
    kind = ast_node.kind.name
    graph.add_node(node_id, label=kind)
    # print("Cursor kind : {0}".format(kind))
    if ast_node.kind.is_declaration():
        add_declaration(node_id, ast_node, graph)
    elif is_literal(ast_node):
        add_literal(node_id, ast_node, graph)
    elif is_reference(ast_node):
        add_reference(node_id, ast_node, graph)
    elif is_operator(ast_node):
        add_operator(node_id, ast_node, graph)
    elif is_call_expr(ast_node):
        add_call_expr(node_id, ast_node, graph)


def add_child(graph, parent_id, name):
    child_id = get_id()
    graph.add_node(child_id, label=name)
    graph.add_edge(parent_id, child_id)


def add_call_expr(parent_id, ast_node, graph):
    # [kolodiazhnyi] seems that it is redundant info
    # name = ast_node.spelling
    # add_child(graph, parent_id, name)

    expr_type = ast_node.type.spelling
    add_child(graph, parent_id, expr_type)

    # print("\tReturn type : {0}".format(expr_type))
    # print("\tName : {0}".format(name))


def add_operator(parent_id, ast_node, graph):
    children = list(ast_node.get_children())
    start = (children[0].location.line,
             children[0].location.column)
    end = (children[1].location.line,
           children[1].location.column)
    name_token = ""
    for token in ast_node.get_tokens():
        if (start < (token.extent.start.line,
                     token.extent.start.column) and
                end >= (token.extent.end.line,
                        token.extent.end.column)):
            name_token = token
    name = name_token.spelling
    add_child(graph, parent_id, name)

    # print("\tName : {0}".format(name))


def add_reference(parent_id, ast_node, graph):
    name = ast_node.spelling
    add_child(graph, parent_id, name)

    # print("\tName : {0}".format(name))


def add_literal(parent_id, ast_node, graph):
    tokens = list(ast_node.get_tokens())
    if tokens:
        value = tokens[0].spelling
        add_child(graph, parent_id, value)

        # print("\tValue : {0}".format(value))


def add_declaration(parent_id, ast_node, graph):
    if is_function(ast_node) or is_method(ast_node):
        return_type = ast_node.type.get_result().spelling
        add_child(graph, parent_id, return_type)
        # print("\tReturn type : {0}".format(return_type))
    else:
        declaration_type = ast_node.type.spelling
        add_child(graph, parent_id, declaration_type)
        # print("\tDecl type : {0}".format(declaration_type))

    name = ast_node.spelling
    add_child(graph, parent_id, name)

    # print("\tName : {0}".format(name))


def ast_to_graph(ast_start_node):
    g = nx.Graph()
    stack = [ast_start_node]
    parent_map = {ast_start_node.hash: None}
    while stack:
        ast_node = stack.pop()
        node_id = ast_node.hash
        if not g.has_node(node_id):
            add_node(ast_node, g)
            parent_id = parent_map[node_id]
            if parent_id is not None:
                g.add_edge(parent_id, node_id)
            for child_node in ast_node.get_children():
                stack.append(child_node)
                parent_map[child_node.hash] = node_id
    return g
