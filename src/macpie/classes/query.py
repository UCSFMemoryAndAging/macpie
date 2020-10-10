import networkx as nx
import pandas as pd
from pathlib import Path

from macpie.io import create_output_dir, format_excel
from macpie.util import add_suffix


SHEET_CHARS_LIMIT = 31


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
        self.g.add_node(
            do,
            name=name if name is not None else do.name,
            operation=operation
        )

    def add_edge(
        self,
        do1,
        do2,
        name=None,
        operation=None
    ):
        if name is None:
            if operation is not None:
                name = operation.func.__name__
            else:
                name = add_suffix(do1.name + "->", do2.name)

        self.g.add_edge(
            do1,
            do2,
            name=name,
            operation=operation
        )

    def execute(self):
        self.execute_nodes()
        self.execute_edges()
        self.executed = True

    def execute_nodes(self):
        # iterate through all nodes
        for node, node_operation in self.g.nodes.data('operation'):
            self.log_node(node)
            if node_operation is not None:
                self.g.nodes[node]['operation_result'] = node_operation(node.df)

                # log the node operation
                self.log_node_operation(node, node_operation)

    def execute_edges(self):
        # iterate through all edges
        for left_node, right_node, edge_operation in self.g.edges.data('operation'):
            if edge_operation is not None:
                left_df = (self.g.nodes[left_node]['operation_result']
                           if self.g.nodes[left_node]['operation']
                           else left_node.df)
                right_df = (self.g.nodes[right_node]['operation_result']
                            if self.g.nodes[right_node]['operation']
                            else right_node.df)

                operation_result = edge_operation(left_df, right_df)

                self.g.edges[left_node, right_node]['operation_result'] = operation_result
                self.g.edges[left_node, right_node]['duplicates'] = operation_result.mac.any_duplicates()

                # log the edge operation
                self.log_edge_operation(left_node, right_node, edge_operation)

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

    def write_excel(self, output_dir: Path = None):
        if self.executed is False:
            raise RuntimeError("should not write results file without first calling 'execute()'")

        final_dir = create_output_dir(output_dir)
        final_file = final_dir / (final_dir.stem + '.xlsx')

        writer = pd.ExcelWriter(final_file, engine='openpyxl')

        # nodes
        for node, node_operation in self.g.nodes.data('operation'):
            # only output nodes that have been operated on to reduce bloated files
            if node_operation is not None:
                result = self.g.nodes[node]['operation_result']
                result.to_excel(excel_writer=writer, sheet_name=node.name, index=False)

        # edges with operations like linking
        for left_node, right_node, operation_result in self.g.edges.data('operation_result'):
            if operation_result is not None:
                sheet_name = self.g.edges[left_node, right_node]['name']
                if self.g.edges[left_node, right_node]['duplicates']:
                    sheet_name = add_suffix(sheet_name, "(DUPS)", 31)
                operation_result.to_excel(excel_writer=writer, sheet_name=sheet_name, index=False)

        log_dataobjects = pd.DataFrame(self.log_dataobjects)
        log_operations = pd.DataFrame(self.log_operations)

        log_dataobjects.to_excel(excel_writer=writer, sheet_name='_log_dataobjects', index=False)
        log_operations.to_excel(excel_writer=writer, sheet_name='_log_operations', index=False)

        writer.save()
        format_excel(final_file)

        return final_file
