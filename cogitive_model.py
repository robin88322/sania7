import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from typing import Any, Dict, List, NoReturn, Optional
from pylab import rcParams


class CognitiveModel:
    def __init__(self, adjacency_matrix, nodes_names=None):
        #self.graph = nx.DiGraph(data=adjacency_matrix)
        self.graph = nx.from_numpy_matrix(adjacency_matrix, create_using=nx.DiGraph(), parallel_edges=False)
        if True:
            nx.set_node_attributes(self.graph, nodes_names, "name")

    @property
    def adjacency_matrix(self):
        """Матриця суміжності"""
        return nx.adjacency_matrix(self.graph).todense()

    @property
    def graph_weights(self):
        return nx.get_edge_attributes(self.graph, "weight")

    def check_perturbation_stability(self):
        """Перевірка стійкості за збуренням"""
        if self.get_spectral_radius(self.adjacency_matrix) <= 1:
            return True
        else:
            return False

    def check_numerical_stability(self):
        """Перевірка сітйкості за значеннями"""
        if self.get_spectral_radius(self.adjacency_matrix) < 1:
            return True
        else:
            return False

    def check_structural_stability(self):
        """Перевірка структурної стійкості

        Returns:
            list of even cycles. If result is an empty list then the model is stable otherwise the model is unstable"""

        def is_even(cycle):
            """Check if contains even number of edges with negative weight"""
            negative_count = np.count_nonzero(
                np.less([self.graph_weights[edge] for edge in nx.find_cycle(self.graph, cycle)], 0))
            return not negative_count & 0x1

        return [cycle for cycle in nx.simple_cycles(self.graph) if is_even(cycle)]

    def calculate_eigenvalues(self):
        """Знаходження власних чисел"""
        return np.linalg.eigvals(self.adjacency_matrix)

    @staticmethod
    def get_spectral_radius(matrix):
        return np.max(np.absolute(np.linalg.eigvals(matrix)))

    def draw_graph(self):
        colors = ['y' if self.graph_weights[edge] > 0 else 'r' for edge in self.graph.in_edges]
        labels  = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx(self.graph, pos=nx.circular_layout(self.graph), arrows=True, arrowstyle='-|>',arrowsize=12, with_labels=True, edge_color=colors, font_size=12, font_color="#ffffff", node_color="b" )
        nx.draw_networkx_edge_labels(self.graph,pos=nx.circular_layout(self.graph), edge_labels=labels, label_pos=0.2, font_size=8, clip_on=False)
        plt.show()

    def impulse_model(self, t: int = 5, q: Optional[np.ndarray] = None) -> NoReturn:
        rcParams["figure.figsize"] = 7, 5
        x_0 = np.zeros((self.adjacency_matrix.shape[0], 1))
        init_q = x_0.copy()
        x_list = [x_0, x_0]
        if q is None:
            q = init_q.copy()
            q[1] = 1
        else:
            q = np.array(q).reshape(-1, 1)
        save_q = q.copy()

        for _ in range(t):
            x_next = x_list[-1] + np.dot(self.adjacency_matrix, (x_list[-1] - x_list[-2])) + q
            x_list.append(x_next)
            q = init_q.copy()
        x_plot = np.array(x_list[1:])
        x_plot = x_plot.reshape(x_plot.shape[:2])

        for index in range(x_plot.shape[1]):
            plt.plot(range(t + 1), x_plot[:, index], label=f"V{index + 1}")
        plt.title(f"Графік імпульсних процесів у вершинах внаслідок \n внесення збурення q = {save_q.reshape(-1, )}")
        plt.xlabel("Час, t")
        plt.ylabel("x(t)")
        plt.legend()
        plt.show()
