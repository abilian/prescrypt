"""Golden test for Bellman-Ford shortest paths."""
from __future__ import annotations


# --- Bellman-Ford function (simplified from bellman_ford.py) ---

INF = float('inf')


def bellman_ford(graph, weight, source):
    """Single source shortest paths by Bellman-Ford

    :param graph: directed graph in listlist format
    :param weight: weight matrix (can be negative)
    :param source: source vertex
    :returns: distance table, precedence table, bool (True if negative cycle)
    :complexity: O(|V|*|E|)
    """
    n = len(graph)
    dist = [INF] * n
    prec = [-1] * n
    dist[source] = 0
    for nb_iterations in range(n):
        changed = False
        for node in range(n):
            for neighbor in graph[node]:
                alt = dist[node] + weight[node][neighbor]
                if alt < dist[neighbor]:
                    dist[neighbor] = alt
                    prec[neighbor] = node
                    changed = True
        if not changed:
            return dist, prec, False
    return dist, prec, True


# --- Tests ---

# Test 1: Simple graph with positive weights
#   0 --5--> 1 --3--> 2
#   |                 ^
#   +-------7---------+
graph1 = [
    [1, 2],  # 0 -> 1, 2
    [2],     # 1 -> 2
    []       # 2
]
weight1 = [
    [0, 5, 7],
    [INF, 0, 3],
    [INF, INF, 0]
]
dist1, prec1, neg_cycle1 = bellman_ford(graph1, weight1, 0)
print(f"dist1: {' '.join(str(d) for d in dist1)}")  # 0 5 7 (via 0->2 not 0->1->2)
print(f"neg_cycle1: {str(neg_cycle1)}")  # False

# Test 2: Graph where going through intermediate is shorter
graph2 = [
    [1],     # 0 -> 1
    [2],     # 1 -> 2
    [3],     # 2 -> 3
    []       # 3
]
weight2 = [
    [0, 1, INF, INF],
    [INF, 0, 1, INF],
    [INF, INF, 0, 1],
    [INF, INF, INF, 0]
]
dist2, prec2, neg_cycle2 = bellman_ford(graph2, weight2, 0)
print(f"dist2: {' '.join(str(d) for d in dist2)}")  # 0 1 2 3
print(f"neg_cycle2: {str(neg_cycle2)}")  # False

# Test 3: Graph with negative edge (but no negative cycle)
graph3 = [
    [1, 2],  # 0 -> 1, 2
    [2],     # 1 -> 2
    []       # 2
]
weight3 = [
    [0, 4, 5],
    [INF, 0, -3],
    [INF, INF, 0]
]
dist3, prec3, neg_cycle3 = bellman_ford(graph3, weight3, 0)
print(f"dist3: {' '.join(str(d) for d in dist3)}")  # 0 4 1 (0->1->2 is shorter)
print(f"neg_cycle3: {str(neg_cycle3)}")  # False

# Test 4: Single vertex
graph4 = [[]]
weight4 = [[0]]
dist4, prec4, neg_cycle4 = bellman_ford(graph4, weight4, 0)
print(f"dist4: {dist4[0]}")  # 0
print(f"neg_cycle4: {str(neg_cycle4)}")  # False

# Test 5: Unreachable vertex
graph5 = [
    [1],  # 0 -> 1
    [],   # 1
    []    # 2 (unreachable)
]
weight5 = [
    [0, 2, INF],
    [INF, 0, INF],
    [INF, INF, 0]
]
dist5, prec5, neg_cycle5 = bellman_ford(graph5, weight5, 0)
print(f"dist5_0: {dist5[0]}")  # 0
print(f"dist5_1: {dist5[1]}")  # 2
print(f"dist5_2_unreachable: {str(dist5[2] == INF)}")  # True

print("bellman_ford tests passed")
