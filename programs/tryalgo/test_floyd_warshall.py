"""Golden test for Floyd-Warshall all pairs shortest paths."""
from __future__ import annotations


# --- Floyd-Warshall function (from floyd_warshall.py) ---

def floyd_warshall(weight):
    """All pairs shortest paths by Floyd-Warshall

    :param weight: edge weight matrix
    :modifies: weight matrix to contain distances in graph
    :returns: True if there are negative cycles
    :complexity: O(|V|^3)
    """
    V = range(len(weight))
    for k in V:
        for u in V:
            for v in V:
                weight[u][v] = min(weight[u][v],
                                   weight[u][k] + weight[k][v])
    for v in V:
        if weight[v][v] < 0:      # negative cycle found
            return True
    return False


# --- Tests ---

# Use large number instead of float('inf') for JS compatibility
INF = 999999999

# Test 1: Simple graph with 4 vertices
# Graph:
#   0 --5-- 1
#   |       |
#   2       3
#   |       |
#   3 --1-- 2
weight1 = [
    [0,   5,   INF, 2  ],
    [INF, 0,   3,   INF],
    [INF, INF, 0,   1  ],
    [INF, INF, INF, 0  ]
]
has_neg_cycle1 = floyd_warshall(weight1)
print(f"neg_cycle1: {str(has_neg_cycle1)}")
print(f"dist(0,0): {weight1[0][0]}")  # 0
print(f"dist(0,1): {weight1[0][1]}")  # 5
print(f"dist(0,2): {weight1[0][2]}")  # 8 (0->1->2)
print(f"dist(0,3): {weight1[0][3]}")  # 2

# Test 2: Graph with shorter paths through intermediate nodes
weight2 = [
    [0,   1,   INF, INF],
    [INF, 0,   1,   INF],
    [INF, INF, 0,   1  ],
    [INF, INF, INF, 0  ]
]
has_neg_cycle2 = floyd_warshall(weight2)
print(f"neg_cycle2: {str(has_neg_cycle2)}")
print(f"dist(0,3): {weight2[0][3]}")  # 3 (0->1->2->3)

# Test 3: Complete graph
weight3 = [
    [0, 1, 4],
    [1, 0, 2],
    [4, 2, 0]
]
has_neg_cycle3 = floyd_warshall(weight3)
print(f"neg_cycle3: {str(has_neg_cycle3)}")
print(f"dist(0,2): {weight3[0][2]}")  # 3 (0->1->2)

# Test 4: Single vertex
weight4 = [[0]]
has_neg_cycle4 = floyd_warshall(weight4)
print(f"neg_cycle4: {str(has_neg_cycle4)}")

print("floyd_warshall tests passed")
