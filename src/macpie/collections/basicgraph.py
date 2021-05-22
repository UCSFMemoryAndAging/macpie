import matplotlib.pyplot as plt
import networkx as nx

from macpie.core.dataset import Dataset
from macpie.tools import string as strtools

from .base import BaseCollection


class BasicGraph(BaseCollection):
    """A collection of Datasets using a directed graph structure,
    composed of Dataset nodes and directed edges (i.e. the edges
    are an ordered pair of Dataset nodes).

    :param g: an existing :class:`networkx.DiGraph`. Defaults to None.
    """

    def __init__(self, g: nx.DiGraph = None):
        if g is None:
            #: Directed graph data structure holding the collection.
            self.g = nx.DiGraph()
        else:
            self.g = g

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'num_nodes={self.g.number_of_nodes()!r}, '
            f'num_edges={self.g.number_of_edges()!r})'
        )

    def __iter__(self):
        return self.g.__iter__()

    def to_dict(self):
        return nx.convert.to_dict_of_dicts(self.g)

    def add_node(
        self,
        dset: Dataset,
        name=None
    ):
        """Add a single Dataset node to the graph.
        """
        self.g.add_node(dset)
        self.g.nodes[dset]['name'] = name if name is not None else dset.name

    def add_edge(
        self,
        u: Dataset,
        v: Dataset,
        name=None
    ):
        """Add an edge between u and v.
        """
        self.g.add_edge(u, v)

        name = strtools.add_suffix(u.name + "->", v.name) if name is None else name
        self.g[u][v]['name'] = name

    def get_root_node(self):
        """If the graph is a rooted tree, get the root node.
        """
        return list(nx.topological_sort(self.g))[0]

    def get_node(self, n, attr: str = None):
        """Get the node attribute if specified, otherwise get the node.
        """
        node = self.g.nodes[n]
        if attr is not None:
            if attr in node:
                return node[attr]
            else:
                return None
        else:
            return node

    def get_all_node_data(self, attr: str = None):
        """Get the data dict of all nodes. If ``attr`` is specified, get the
        data dict of all nodes that have that ``attr`` in its data dict.
        """
        if attr is None:
            return [d for n, d in self.g.nodes.items()]
        else:
            results = []
            for n, d in self.g.nodes.items():
                if attr in d:
                    results.append(d)
            return results

    def get_all_edge_data(self, attr: str = None):
        """Get the data dict of all edges. If ``attr`` is specified, get the
        data dict of all edges that have that ``attr`` in its data dict.
        """
        if attr is None:
            return [d for e, d in self.g.edges.items()]
        else:
            results = []
            for e, d in self.g.edges.items():
                if attr in d:
                    results.append(d)
            return results

    def print_nodes(self):
        counter = 1
        for n, d in self.g.nodes.items():
            print('\nNODE ' + str(counter))
            print(n)
            print(d)
            counter += 1

    def print_edges(self):
        counter = 1
        for e, d in self.g.edges.items():
            print('\nEDGE ' + str(counter))
            print(e)
            print(d)
            counter += 1

    def print_graph(self):
        """Print a text representation of the graph.
        """
        self.print_nodes()
        self.print_edges()

    def draw_graph(self):
        """Print a graph representation of the graph using the
        ``matplotlib`` library.
        """
        pos = nx.shell_layout(self.g)
        # pos = nx.spring_layout(self.g)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.axis('equal')

        nx.draw_networkx_nodes(self.g, pos, node_size=500)
        nx.draw_networkx_edges(self.g, pos, arrowsize=30)
        nx.draw_networkx_edge_labels(
            self.g,
            pos,
            edge_labels=nx.get_edge_attributes(self.g, 'name'),
            verticalalignment='center',
            horizontalalignment='center'
        )
        nx.draw_networkx_labels(
            self.g,
            pos,
            labels={n: d['name'] for n, d in self.g.nodes.items() if n in pos},
            font_size=10,
            horizontalalignment="left"
        )

        # plt.tight_layout()
        plt.axis("off")
        plt.show()
