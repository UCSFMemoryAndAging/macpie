import matplotlib.pyplot as plt
import networkx as nx

from macpie.util import add_suffix


class Query:

    def __init__(self, g=None):
        if g is None:
            self.g = nx.DiGraph()
        else:
            self.g = g

        self.executed = False

        self.log_dataobjects = []
        self.log_operations = []

    def add_node(
        self,
        do,
        name=None,
        operation=None
    ):
        self.g.add_node(do)
        self.g.nodes[do]['name'] = name if name is not None else do.name
        if operation is not None:
            self.g.nodes[do]['operation'] = operation

    def add_edge(
        self,
        do1,
        do2,
        name=None,
        operation=None
    ):
        self.g.add_edge(do1, do2)

        if name is None:
            if operation is not None:
                name = operation.func.__name__
            else:
                name = add_suffix(do1.name + "->", do2.name)
        self.g[do1][do2]['name'] = name

        if operation is not None:
            self.g[do1][do2]['operation'] = operation

    def execute(self):
        self.execute_nodes()
        self.execute_edges()
        self.executed = True

    def execute_nodes(self):
        for n, d in self.g.nodes.items():
            self.log_node(n)
            if 'operation' in d:
                node_operation = d['operation']
                self.g.nodes[n]['operation_result'] = node_operation(n.df)
                # log the node operation
                self.log_node_operation(n, node_operation)

    def execute_edges(self):
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
                self.g.edges[u, v]['duplicates'] = operation_result.mac.any_duplicates('_duplicates')
                # log the edge operation
                self.log_edge_operation(u, v, edge_operation)

    def get_root_node(self):
        return list(nx.topological_sort(self.g))[0]

    def get_node(self, n, attr: str = None):
        node = self.g.nodes[n]
        if attr is not None:
            if attr in node:
                return node[attr]
            else:
                return None
        else:
            return node

    def get_all_node_data(self, attr: str = None):
        """Get the data dict of all nodes. If attr is specified, get the
        data dict of all nodes that have that attr in its data dict.
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
        """Get the data dict of all edges. If attr is specified, get the
        data dict of all edges that have that attr in its data dict.
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
        entry = {
            'left_operand': a.name,
            'right_operand': 'N/A',
            'operation': node_operation.func.__name__,
            'operation_params': str(node_operation.keywords),
            'operation_results_shape': f'({a.df.mac.num_rows()}, {a.df.mac.num_cols()})'
        }

        self.log_operations.append(entry)

    def log_edge_operation(self, a, b, edge_operation):
        results = self.g.edges[a, b]['operation_result']

        entry = {
            'left_operand': a.name,
            'right_operand': b.name,
            'operation': edge_operation.func.__name__,
            'operation_params': str(edge_operation.keywords),
            'operation_results_shape': (f'({results.mac.num_rows()}, {results.mac.num_cols()})'
                                        if results is not None else "")
        }

        self.log_operations.append(entry)

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
        self.print_nodes()
        self.print_edges()

    def draw_graph(self):
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
