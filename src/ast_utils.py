import networkx as nx
import uuid
from clang.cindex import CursorKind, TypeKind, TokenKind


def is_function(node):
    if node.kind in [CursorKind.FUNCTION_DECL,
                     CursorKind.FUNCTION_TEMPLATE,
                     CursorKind.CXX_METHOD,
                     CursorKind.DESTRUCTOR,
                     CursorKind.CONSTRUCTOR]:
        if node.is_definition():
            not_empty = False
            for _ in node.get_children():
                not_empty = True
                break
            return not_empty
    return False


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


def is_template_parameter(node):
    return node.kind in [CursorKind.TEMPLATE_TYPE_PARAMETER,
                         CursorKind.TEMPLATE_TEMPLATE_PARAMETER]


def is_reference(node):
    return node.kind in [CursorKind.DECL_REF_EXPR, CursorKind.MEMBER_REF_EXPR]


def is_operator(node):
    return node.kind in [CursorKind.BINARY_OPERATOR,
                         CursorKind.UNARY_OPERATOR,
                         CursorKind.COMPOUND_ASSIGNMENT_OPERATOR]


def is_call_expr(node):
    return node.kind == CursorKind.CALL_EXPR


binary_operators = ['+', '-', '*', '/', '%', '&', '|']
unary_operators = ['++', '--']
comparison_operators = ['==', '<=', '>=', '<', '>', '!=', '&&', '||']
unary_assignment_operators = [op + '=' for op in binary_operators]
assignment_operators = ['='] + unary_assignment_operators


def is_operator_token(token):
    if token in binary_operators:
        return True
    if token in unary_operators:
        return True
    if token in comparison_operators:
        return True
    if token in unary_assignment_operators:
        return True
    if token in assignment_operators:
        return True


def get_id():
    node_id = uuid.uuid1()
    return node_id.int


def add_node(ast_node, graph):
    try:
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
    except Exception as e:
        msg = 'Error: {0} in:\n'.format(str(e))
        msg += 'Filename : {0}\n'.format(ast_node.location.file.name)
        msg += 'Start {0}:{1}'.format(ast_node.extent.start.line, ast_node.extent.start.column)
        msg += 'End {0}:{1}'.format(ast_node.extent.end.line, ast_node.extent.end.column)
        raise Exception(msg)


def add_child(graph, parent_id, name):
    child_id = get_id()
    assert len(name) > 0, "Missing node name"
    graph.add_node(child_id, label=name)
    graph.add_edge(parent_id, child_id)


def add_call_expr(parent_id, ast_node, graph):
    expr_type = ast_node.type.spelling
    add_child(graph, parent_id, expr_type)


def add_operator(parent_id, ast_node, graph):
    name_token = None
    for token in ast_node.get_tokens():
        if is_operator_token(token.spelling):
            name_token = token
            break

    if not name_token:
        filename = ast_node.location.file.name
        with open(filename, 'r') as fh:
            contents = fh.read()
        code_str = contents[ast_node.extent.start.offset: ast_node.extent.end.offset]
        for ch in code_str:
            if ch in binary_operators:
                add_child(graph, parent_id, ch)
    else:
        name = name_token.spelling
        add_child(graph, parent_id, name)
        # print("\tName : {0}".format(name))


def add_reference(parent_id, ast_node, graph):
    if ast_node.kind in [CursorKind.DECL_REF_EXPR, CursorKind.MEMBER_REF_EXPR]:
        name = "unknown"
        for token in ast_node.get_tokens():
            if token.kind == TokenKind.IDENTIFIER:
                name = token.spelling
                break
    else:
        name = ast_node.spelling
    add_child(graph, parent_id, name)
    # print("\tName : {0}".format(name))


def add_literal(parent_id, ast_node, graph):
    if ast_node.kind in [CursorKind.STRING_LITERAL,
                         CursorKind.CHARACTER_LITERAL]:
        add_child(graph, parent_id, 'STRING_VALUE')
    else:
        token = next(ast_node.get_tokens(), None)
        if token:
            value = token.spelling
            add_child(graph, parent_id, value)
            # print("\tValue : {0}".format(value))


def add_declaration(parent_id, ast_node, graph):
    if is_function(ast_node):
        return_type = ast_node.type.get_result().spelling
        if len(return_type) > 0:
            add_child(graph, parent_id, return_type)
    else:
        declaration_type = ast_node.type.spelling
        if len(declaration_type) > 0:
            add_child(graph, parent_id, declaration_type)
            # print("\tDecl type : {0}".format(declaration_type))

    if not is_template_parameter(ast_node):
        name = ast_node.spelling
        # handle unnamed declarations
        if len(name) == 0:
            name = ast_node.kind.name + "_UNNAMED"
        add_child(graph, parent_id, name)
        # print("\tName : {0}".format(name))


def ast_to_graph(ast_start_node, max_depth):
    g = nx.Graph()
    stack = [(ast_start_node, 0)]
    parent_map = {ast_start_node.hash: None}
    while stack:
        ast_node, depth = stack.pop()
        node_id = ast_node.hash
        if not g.has_node(node_id):
            add_node(ast_node, g)
            parent_id = parent_map[node_id]
            if parent_id is not None:
                g.add_edge(parent_id, node_id)

            # Ignore too deep trees
            if max_depth == 0 or depth <= max_depth:
                for child_node in ast_node.get_children():
                    stack.append((child_node, depth + 1))
                    parent_map[child_node.hash] = node_id
    return g
