"""Golden test for topological ordering."""
from __future__ import annotations


# --- Topological order functions (from topological_order.py) ---

def topological_order_dfs(graph):
    """Topological sorting by depth first search

    :param graph: directed graph in listlist format
    :returns: list of vertices in order
    :complexity: O(|V|+|E|)
    """
    n = len(graph)
    order = []
    times_seen = [-1] * n
    for start in range(n):
        if times_seen[start] == -1:
            times_seen[start] = 0
            to_visit = [start]
            while len(to_visit) > 0:
                node = to_visit[-1]
                children = graph[node]
                if times_seen[node] == len(children):
                    to_visit.pop()
                    order.append(node)
                else:
                    child = children[times_seen[node]]
                    times_seen[node] += 1
                    if times_seen[child] == -1:
                        times_seen[child] = 0
                        to_visit.append(child)
    return order[::-1]


def topological_order(graph):
    """Topological sorting by maintaining indegree

    :param graph: directed graph in listlist format
    :returns: list of vertices in order
    :complexity: O(|V|+|E|)
    """
    V = range(len(graph))
    indeg = [0 for _ in V]
    for node in V:            # compute indegree
        for neighbor in graph[node]:
            indeg[neighbor] += 1
    Q = [node for node in V if indeg[node] == 0]
    order = []
    while len(Q) > 0:
        node = Q.pop()        # node without incoming arrows
        order.append(node)
        for neighbor in graph[node]:
            indeg[neighbor] -= 1
            if indeg[neighbor] == 0:
                Q.append(neighbor)
    return order


def is_valid_topological_order(graph, order):
    """Check if order is a valid topological order for graph."""
    n = len(graph)
    if len(order) != n:
        return False
    position = {v: i for i, v in enumerate(order)}
    for u in range(n):
        for v in graph[u]:
            if position[u] >= position[v]:
                return False
    return True


# --- Tests ---

# Test 1: Simple DAG
#   0 -> 1 -> 2
#   |         ^
#   +----3----+
graph1 = [
    [1, 3],  # 0 -> 1, 3
    [2],     # 1 -> 2
    [],      # 2
    [2]      # 3 -> 2
]
order1_dfs = topological_order_dfs(graph1)
order1_ind = topological_order(graph1)
print(f"valid_dfs1: {str(is_valid_topological_order(graph1, order1_dfs))}")
print(f"valid_ind1: {str(is_valid_topological_order(graph1, order1_ind))}")

# Test 2: Linear chain
# 0 -> 1 -> 2 -> 3
graph2 = [
    [1],  # 0 -> 1
    [2],  # 1 -> 2
    [3],  # 2 -> 3
    []    # 3
]
order2_dfs = topological_order_dfs(graph2)
order2_ind = topological_order(graph2)
print(f"valid_dfs2: {str(is_valid_topological_order(graph2, order2_dfs))}")
print(f"valid_ind2: {str(is_valid_topological_order(graph2, order2_ind))}")

# Test 3: Diamond shape
#     1
#    / \
#   0   3
#    \ /
#     2
graph3 = [
    [1, 2],  # 0 -> 1, 2
    [3],     # 1 -> 3
    [3],     # 2 -> 3
    []       # 3
]
order3_dfs = topological_order_dfs(graph3)
order3_ind = topological_order(graph3)
print(f"valid_dfs3: {str(is_valid_topological_order(graph3, order3_dfs))}")
print(f"valid_ind3: {str(is_valid_topological_order(graph3, order3_ind))}")

# Test 4: Disconnected components
graph4 = [
    [1],  # 0 -> 1
    [],   # 1
    [3],  # 2 -> 3
    []    # 3
]
order4_dfs = topological_order_dfs(graph4)
order4_ind = topological_order(graph4)
print(f"valid_dfs4: {str(is_valid_topological_order(graph4, order4_dfs))}")
print(f"valid_ind4: {str(is_valid_topological_order(graph4, order4_ind))}")

# Test 5: Single vertex
graph5 = [[]]
order5 = topological_order(graph5)
print(f"single_vertex: {repr(order5)}")

print("topological_order tests passed")
