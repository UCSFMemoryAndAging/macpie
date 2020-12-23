from typing import Callable, ClassVar

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from macpie import util
from macpie.core import DataObject, Datasheet


class Query:
    """
    A data structure representing a query using a directed graph structure.

    The query is composed of nodes and directed edges (i.e. the edges
    are an ordered pair of nodes). Nodes and edges can have operations attached
    to them. A node can attach a unary operation (i.e. the operation takes a single input).
    An edge can attach a binary operation (i.e. the operation requires two inputs)
    with the left and right node of the edge representing the left and right operand of
    the operation, respectively.

    When the query is executed, all operations are executed, and the operation results are
    attached to the node and edges themselves.
    """

    SHEETNAME_QUERY_DATAOBJECTS : ClassVar[str] = '_query_dataobjects'
    SHEETNAME_QUERY_OPERATIONS : ClassVar[str] = '_query_operations'

    def __init__(self, g: nx.DiGraph = None):
        if g is None:
            #: Directed graph data structure representing the query.
            self.g = nx.DiGraph()
        else:
            self.g = g

        #: Whether :meth:`execute` has been called
        self.executed = False

        self.log_dataobjects = []
        self.log_operations = []

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'num_nodes={self.g.number_of_nodes()!r}, '
            f'num_edges={self.g.number_of_edges()!r})'
        )

    def add_node(
        self,
        do: DataObject,
        name=None,
        operation: Callable = None
    ):
        """
        Add a single DataObject node to the query.

        :param operation: A callable to be called on the DataObject. Typically
                          a data transformation function that expects a single
                          pandas.DataFrame object and arbitrary keyword arguments.
                          See :meth:`execute_nodes`
        """
        self.g.add_node(do)
        self.g.nodes[do]['name'] = name if name is not None else do.name
        if operation is not None:
            self.g.nodes[do]['operation'] = operation

    def add_edge(
        self,
        do1: DataObject,
        do2: DataObject,
        name=None,
        operation=None
    ):
        """
        Add an edge between do1 and do2.

        :param operation: A callable to be called on the two DataObjects. Typically
                          a data transformation function that expects two pandas.DataFrame
                          objects and arbitrary keyword arguments.
                          See :meth:`execute_edges`
        """
        self.g.add_edge(do1, do2)

        if name is None:
            if operation is not None:
                name = operation.func.__name__
            else:
                name = util.string.add_suffix(do1.name + "->", do2.name)
        self.g[do1][do2]['name'] = name

        if operation is not None:
            self.g[do1][do2]['operation'] = operation

    def execute(self):
        """
        Execute query by calling all ``operation`` functions on each node and edge.
        """
        self.execute_nodes()
        self.execute_edges()
        self.executed = True

    def execute_nodes(self):
        """
        Execute all the nodes, calling the ``operation`` on each node if it exists.
        """
        for n, d in self.g.nodes.items():
            self.log_node(n)
            if 'operation' in d:
                node_operation = d['operation']
                self.g.nodes[n]['operation_result'] = node_operation(n.df)
                # log the node operation
                self.log_node_operation(n, node_operation)

    def execute_edges(self):
        """
        Execute all the edges, calling the ``operation`` on each edge if it exists.
        """
        for u, v, edge_operation in self.g.edges.data('operation'):
            if edge_operation is not None:
                left_df = (self.g.nodes[u]['operation_result']
                           if 'operation_result' in self.g.nodes[u]
                           else u.df)
                right_df = (self.g.nodes[v]['operation_result']
                            if 'operation_result' in self.g.nodes[v]
                            else v.df)
                operation_result = edge_operation(left_df, right_df)
                self.g.edges[u, v]['operation_result'] = operation_result
                # log the edge operation
                self.log_edge_operation(u, v, edge_operation)

    def get_root_node(self):
        """
        If the query is a rooted tree, get the root node.
        """
        return list(nx.topological_sort(self.g))[0]

    def get_node(self, n, attr: str = None):
        """
        Get the node attribute if specified, otherwise get the node.
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
        if attr is not None:
            results = []
            for n, d in self.g.nodes.items():
                if attr in d:
                    results.append(d)
            return results
        else:
            return [d for n, d in self.g.nodes.items()]

    def get_all_edge_data(self, attr: str = None):
        """Get the data dict of all edges. If ``attr`` is specified, get the
        data dict of all edges that have that ``attr`` in its data dict.
        """
        if attr is not None:
            results = []
            for e, d in self.g.edges.items():
                if attr in d:
                    results.append(d)
            return results
        else:
            return [d for e, d in self.g.edges.items()]

    def log_node(self, a):
        self.log_dataobjects.append(a.to_dict())

    def log_node_operation(self, a, node_operation):
        self.log_operations.append({
            'left_operand': a.name,
            'right_operand': 'N/A',
            'operation': node_operation.func.__name__,
            'operation_params': node_operation.keywords,
            'operation_results_shape': f'({a.df.mac.num_rows()}, {a.df.mac.num_cols()})'}
        )

    def log_edge_operation(self, a, b, edge_operation):
        results = self.g.edges[a, b]['operation_result']
        self.log_operations.append({
            'left_operand': a.name,
            'right_operand': b.name,
            'operation': edge_operation.func.__name__,
            'operation_params': edge_operation.keywords,
            'operation_results_shape': (f'({results.mac.num_rows()}, {results.mac.num_cols()})'
                                        if results is not None else "")})

    def get_log_dataobjects(self):
        return Datasheet(self.SHEETNAME_QUERY_DATAOBJECTS, pd.DataFrame(self.log_dataobjects))

    def get_log_operations(self):
        return Datasheet(self.SHEETNAME_QUERY_OPERATIONS, pd.DataFrame(self.log_operations))

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
        """
        Print a text representation of the query.
        """
        self.print_nodes()
        self.print_edges()

    def draw_graph(self):
        """
        Print a graph representation of the query using matplotlib.
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
