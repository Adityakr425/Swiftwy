import heapq
from simulator import segment_status


def build_graphs():
    """
    Build two adjacency graphs from simulator segments:
      - graph: distance-based weights
      - graph_low: distance penalized by congestion (for alternate routes)
    Returns (graph, graph_low)
    """
    graph = {}
    graph_low = {}
    segments = segment_status()

    for s in segments:
        u = s["start"]
        v = s["end"]
        dist = s.get("distance_km", 30.0)
        eta = s.get("eta_min", max(1, int(dist / 40 * 60)))
        congestion = s.get("congestion", 0)

        graph.setdefault(u, {})[v] = {"distance": dist, "eta": eta}
        graph.setdefault(v, {})[u] = {"distance": dist, "eta": eta}

        penalty = dist * (1 + congestion / 100.0)
        graph_low.setdefault(u, {})[v] = {"distance": penalty, "eta": eta}
        graph_low.setdefault(v, {})[u] = {"distance": penalty, "eta": eta}

    return graph, graph_low


def shortest_path(graph, start, end):
    """
    Dijkstra's algorithm returning list of node names from start to end.
    Returns [] if no path found or nodes missing.
    """
    if start not in graph or end not in graph:
        return []

    pq = [(0, start, [])]  # (cost, node, path)
    visited = set()

    while pq:
        cost, node, path = heapq.heappop(pq)
        if node in visited:
            continue

        visited.add(node)
        path = path + [node]

        if node == end:
            return path

        for nbr, meta in graph.get(node, {}).items():
            weight = meta["distance"]
            heapq.heappush(pq, (cost + weight, nbr, path))
    return []


def calculate_best_route(start, end):
    """
    Returns: best_route (congestion-aware), best_eta,
             main_route (distance-based), main_eta.
    If nodes missing or unreachable, returns empty lists and zeros.
    """
    graph, graph_low = build_graphs()

    main_route = shortest_path(graph, start, end)
    main_eta = 0
    if main_route and len(main_route) > 1:
        for i in range(len(main_route) - 1):
            a = main_route[i]
            b = main_route[i + 1]
            main_eta += graph[a][b]["eta"]

    best_route = shortest_path(graph_low, start, end)
    best_eta = 0
    if best_route and len(best_route) > 1:
        for i in range(len(best_route) - 1):
            a = best_route[i]
            b = best_route[i + 1]
            best_eta += graph_low[a][b]["eta"]

    return best_route, best_eta, main_route, main_eta
