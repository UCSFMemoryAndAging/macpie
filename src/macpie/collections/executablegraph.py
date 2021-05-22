from typing import Callable

import networkx as nx

from macpie.core.dataset import Dataset
from macpie.tools import string as strtools

from .basicgraph import BasicGraph


class ExecutableGraph(BasicGraph):
    """A collection of Datasets using a directed graph structure.

    The collection is composed of nodes and directed edges (i.e. the edges
    are an ordered pair of nodes). Nodes and edges can have operations attached
    to them. A node can attach a unary operation (i.e. the operation takes a single input).
    An edge can attach a binary operation (i.e. the operation requires two inputs)
    with the left and right node of the edge representing the left and right operand of
    the operation, respectively.

    When the collection is executed, all operations are executed, and the operation results are
    attached to the node and edges themselves.
    """

    def __init__(self, g: nx.DiGraph = None):
        super().__init__(g)

        #: Whether :meth:`execute` has been called
        self.executed = False

        self.log_operations = []

    def add_node(
        self,
        dset: Dataset,
        name=None,
        operation: Callable = None
    ):
        """Add a single Dataset node to the graph.

        :param operation: A callable to be called on the Dataset. Typically
                          a data transformation function that expects a single
                          pandas.DataFrame object and arbitrary keyword arguments.
                          See :meth:`execute_nodes`
        """
        super().add_node(dset, name)
        if operation is not None:
            self.g.nodes[dset]['operation'] = operation

    def add_edge(
        self,
        u: Dataset,
        v: Dataset,
        name=None,
        operation: Callable = None
    ):
        """Add an edge between u and v.

        :param operation: A callable to be called on the two Datasets. Typically
                          a data transformation function that expects two pandas.DataFrame
                          objects and arbitrary keyword arguments.
                          See :meth:`execute_edges`
        """

        if name is None:
            if operation is not None:
                name = operation.func.__name__
            else:
                name = strtools.add_suffix(u.name + "->", v.name)

        super().add_edge(u, v, name)

        if operation is not None:
            self.g[u][v]['operation'] = operation

    def execute(self):
        """Execute by calling all ``operation`` functions on each node and edge.
        """
        self.execute_nodes()
        self.execute_edges()
        self.executed = True

    def execute_nodes(self):
        """Execute all the nodes, calling the ``operation`` on each node if it exists.
        """
        for n, d in self.g.nodes.items():
            if 'operation' in d:
                node_operation = d['operation']
                self.g.nodes[n]['operation_result'] = node_operation(n.df)
                # log the node operation
                self.log_node_operation(n, node_operation)

    def execute_edges(self):
        """Execute all the edges, calling the ``operation`` on each edge if it exists.
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

    def get_log_operations(self):
        return self.log_operations
