import networkx as nx


def ast_to_graph(ast_start_node):
    g = nx.Graph()
    stack = [ast_start_node]
    parent_map = {ast_start_node.hash: None}
    while stack:
        ast_node = stack.pop()
        node_id = ast_node.hash
        if not g.has_node(node_id):
            g.add_node(node_id, node=ast_node)
            parent_id = parent_map[node_id]
            if parent_id is not None:
                g.add_edge(parent_id, node_id)
            for child_node in ast_node.get_children():
                stack.append(child_node)
                parent_map[child_node.hash] = node_id
    return g
