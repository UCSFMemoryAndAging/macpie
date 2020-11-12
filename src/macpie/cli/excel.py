import numpy as np
import openpyxl as pyxl
import pandas as pd
from pathlib import Path

from macpie.io import create_output_dir
from macpie.io import get_row_by_col_val, ws_autoadjust_colwidth, ws_get_col, ws_highlight_row
from macpie.util import add_suffix


def write_link_results_with_merge(Q, output_dir: Path = None):
    if Q.executed is False:
        raise RuntimeError("should not write results file without first calling 'execute()'")

    final_dir = create_output_dir(output_dir, "results")
    final_file = final_dir / (final_dir.stem + '.xlsx')

    writer = pd.ExcelWriter(final_file, engine='openpyxl')

    fields_list = []
    fields_list_dups = []

    primary_node = Q.get_root_node()
    primary_result = Q.get_node(primary_node, 'operation_result')
    primary_result.columns = pd.MultiIndex.from_product([[primary_node.name], primary_result.columns])

    final_result = primary_result

    for left_node, right_node, operation_result in Q.g.edges.data('operation_result'):
        if operation_result is not None:
            if Q.g.edges[left_node, right_node]['duplicates']:
                # put secondary results that have duplicates as separate worksheets after the results worksheet
                sheet_name = Q.g.edges[left_node, right_node]['name']
                sheet_name = add_suffix(sheet_name, "(DUPS)", 31)
                operation_result.to_excel(excel_writer=writer, sheet_name=sheet_name, index=False)
                fields_list_dups.extend([(sheet_name, col) for col in operation_result.columns])
            else:
                # merge all secondary results that do not have any duplicates
                final_result = final_result.mac.merge(
                    operation_result,
                    left_on=[
                        (primary_node.name, primary_node.id2_col),
                        (primary_node.name, primary_node.date_col),
                        (primary_node.name, primary_node.id_col)
                    ],
                    right_on=[col + '_link' for col in [primary_node.id2_col,
                                                        primary_node.date_col,
                                                        primary_node.id_col]],
                    add_indexes=(None, right_node.name)
                )
                fields_list.extend(list(final_result.columns))

    final_result_sheet_name = 'MERGED_RESULTS'
    final_result.index = np.arange(1, len(final_result) + 1)
    final_result.to_excel(excel_writer=writer, sheet_name=final_result_sheet_name, index=True)

    fields_list_df = pd.DataFrame(data=fields_list, columns=['Worksheet', 'Column'])
    fields_list_df.to_excel(excel_writer=writer, sheet_name='_fields_available', index=False)

    log_dataobjects = pd.DataFrame(Q.log_dataobjects)
    log_operations = pd.DataFrame(Q.log_operations)
    log_dataobjects.to_excel(excel_writer=writer, sheet_name='_log_dataobjects', index=False)
    log_operations.to_excel(excel_writer=writer, sheet_name='_log_operations', index=False)

    writer.save()

    format_link_results_with_merge(final_file, final_result_sheet_name)

    return final_file


def write_results_basic(Q, output_dir: Path = None):
    if Q.executed is False:
        raise RuntimeError("should not write results file without first calling 'execute()'")

    final_dir = create_output_dir(output_dir, "results")
    final_file = final_dir / (final_dir.stem + '.xlsx')

    writer = pd.ExcelWriter(final_file, engine='openpyxl')

    nodes_with_operations = Q.get_all_node_data('operation')
    for node in nodes_with_operations:
        result = node['operation_result']
        result.to_excel(excel_writer=writer, sheet_name=node['name'], index=False)

    edges_with_operation_results = Q.get_all_edge_data('operation_result')
    for edge in edges_with_operation_results:
        sheet_name = edge['name']
        if edge['duplicates']:
            sheet_name = add_suffix(sheet_name, "(DUPS)", 31)
        edge['operation_result'].to_excel(excel_writer=writer, sheet_name=sheet_name, index=False)

    log_dataobjects = pd.DataFrame(Q.log_dataobjects)
    log_operations = pd.DataFrame(Q.log_operations)

    log_dataobjects.to_excel(excel_writer=writer, sheet_name='_log_dataobjects', index=False)
    log_operations.to_excel(excel_writer=writer, sheet_name='_log_operations', index=False)

    writer.save()

    format_results_basic(final_file)

    return final_file


def format_results_basic(f):
    filename = str(f)
    wb = pyxl.load_workbook(filename)

    for ws in wb.worksheets:
        if ws.title.startswith('_log_'):
            ws_autoadjust_colwidth(ws)
        else:
            ws_highlight_dupes(ws, '_duplicates')

    wb.save(filename)


def format_link_results_with_merge(f, results_sheet=None):
    filename = str(f)
    wb = pyxl.load_workbook(filename)

    if results_sheet is not None and results_sheet in wb.sheetnames:
        ws = wb

    for ws in wb.worksheets:
        if ws.title.endswith('(DUPS)'):
            ws_highlight_dupes(ws, '_duplicates')
        elif ws.title == results_sheet:
            ws_index = wb.index(ws)
            wb.move_sheet(ws, -ws_index)
            format_multiindex(ws)
        elif ws.title.startswith('_log_'):
            ws_autoadjust_colwidth(ws)

    wb.save(filename)


def format_multiindex(ws):
    # get row index where column A has value of 1 (index of the dataframe)
    row_index = get_row_by_col_val(ws, 0, 1)
    row_index = row_index - 1
    ws.delete_rows(row_index)

    # forced to keep the index column due to bug, so might as well give it a good name
    ws['A2'].value = "Original_Order"
    # https://stackoverflow.com/questions/54682506/openpyxl-in-python-delete-rows-function-breaks-the-merged-cell
    # ws.delete_cols(1,1)

    data_range = "A2:" + pyxl.utils.get_column_letter(ws.max_column) + str(ws.max_row)

    ws.auto_filter.ref = data_range


def read_multiindex(f):
    filename = str(f)
    wb = pyxl.load_workbook(filename)
    ws = wb.active

    if ws['A2'].value == "Original_Order":
        return pd.read_excel(filename, index_col=0, header=[0, 1], engine='openpyxl')
    else:
        return pd.read_excel(filename, index_col=None, header=[0, 1], engine='openpyxl')


def ws_highlight_dupes(ws, dupes_col):
    dupes_col = ws_get_col(ws, dupes_col)
    if dupes_col > -1:
        rows_iter = ws.iter_rows(min_col=dupes_col, min_row=1, max_col=dupes_col, max_row=ws.max_row)
        for row in rows_iter:
            cell = row[0]
            if cell.value is True:
                ws_highlight_row(ws, cell.row)
