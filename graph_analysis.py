import networkx as nx
import matplotlib.pyplot as plt
import io
import pulp
import heapq


class GraphAnalysis:
    def __init__(self, adj_matrix):
        self.adj_matrix = adj_matrix
        self.graph = nx.Graph()
        self._create_graph()


    def _create_graph(self):
        n = len(self.adj_matrix)
        for i in range(n):
            for j in range(i + 1, n):
                if self.adj_matrix[i][j] == 1:
                    self.graph.add_edge(i + 1, j + 1)


    def draw_graph(self):
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_color='skyblue', node_size=300, edge_color='gray')
        buffer = io.BytesIO()
        plt.savefig(buffer, format='PNG')
        buffer.seek(0)
        plt.close()
        return buffer


    def maximum_independent_set(self):
        return nx.approximation.maximum_independent_set(self.graph)


    def largest_matching(self):
        return nx.maximal_matching(self.graph)
    

    def minimum_vertex_cover(self):
        nodes = list(self.graph.nodes)
        edges = list(self.graph.edges)
        
        prob = pulp.LpProblem("MinimumVertexCover", pulp.LpMinimize)
        
        x = pulp.LpVariable.dicts('x', nodes, 0, 1, pulp.LpBinary)
        
        prob += pulp.lpSum([x[i] for i in nodes])
        
        for u, v in edges:
            prob += x[u] + x[v] >= 1
        
        prob.solve()
        
        min_vertex_cover = [i for i in nodes if x[i].varValue == 1]
        
        return min_vertex_cover


    def min_edge_cover(self):
        return nx.min_edge_cover(self.graph)


    def edges_to_remove_for_eulerian_path(self):
        graph = self.graph.copy()
        odd_degree_nodes = [node for node in graph.nodes if graph.degree(node) % 2 != 0]
        
        if len(odd_degree_nodes) <= 2:
            return []

        # Precompute all shortest paths between odd-degree nodes
        shortest_paths = dict(nx.all_pairs_dijkstra_path_length(graph))
        odd_pairs = [(u, v) for i, u in enumerate(odd_degree_nodes) for v in odd_degree_nodes[i + 1:]]
        
        # Min-heap to efficiently fetch the shortest odd pair
        min_heap = [(shortest_paths[u][v], u, v) for u, v in odd_pairs if v in shortest_paths[u]]
        heapq.heapify(min_heap)

        min_edges_to_remove = []
        while len(odd_degree_nodes) > 2:
            if not min_heap:
                break

            _, u, v = heapq.heappop(min_heap)
            if not nx.has_path(graph, u, v):
                continue

            path = nx.shortest_path(graph, source=u, target=v)
            
            for i in range(len(path) - 1):
                if graph.has_edge(path[i], path[i + 1]):
                    min_edges_to_remove.append((path[i], path[i + 1]))
                    graph.remove_edge(path[i], path[i + 1])

            odd_degree_nodes = [node for node in graph.nodes if graph.degree(node) % 2 != 0]
            if len(odd_degree_nodes) <= 2:
                break
            
            min_heap = [(shortest_paths[u][v], u, v) for u in odd_degree_nodes for v in odd_degree_nodes if u < v and v in shortest_paths[u]]
            heapq.heapify(min_heap)

        return min_edges_to_remove
