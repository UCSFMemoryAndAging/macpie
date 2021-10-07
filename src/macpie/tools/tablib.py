from openpyxl import load_workbook
import pandas as pd
import tablib as tl


def append_with_tags(dset: tl.Dataset, ser: pd.Series):
    """Adds ``ser`` as a row to ``dset`` with tags derived
    from the labels in ``ser`` that are not headers in ``dset``,
    and whose value is ``'x'`` or ``'X'``.

        >>> dset = tl.Dataset()
        >>> dset.headers = ('Dataset', 'Field')
        >>> dset.append(('CDR', 'Col1'))
        >>> dset.export("df")
          Dataset Field
        0     CDR  Col1
        >>> ser_data = {'Dataset':'CDR', 'Field':'Col2', 'Merge?': 'x'}
        >>> ser = pd.Series(data=ser_data, index=['Dataset','Field','Merge?'])
        >>> ser
        Dataset     CDR
        Field      Col2
        Merge?        x
        >>> mp.tablibtools.append_with_tags(dset, ser)
        >>> dset.export("df")
          Dataset Field
        0     CDR  Col1
        1     CDR  Col2
        >>> dset2 = dset.filter('Merge?')
          Dataset Field
        0     CDR  Col2

    :param dset: The :class:`tablib.Dataset` that gets ``ser`` appended to
    :param ser: A row of data to append to ``dset``
    """
    ser = ser.copy()
    headers = dset.headers
    data_row = [ser.pop(item=header) for header in headers]
    tags = ser[ser.str.lower() == "x"].index.tolist()
    dset.append(data_row, tags)


def read_excel(filepath, sheet_name: str = None, headers=True):
    """Returns a Tablib Dataset from an Excel file."""

    wb = load_workbook(filepath, read_only=True, data_only=True)
    sheet = wb.active if sheet_name is None else wb[sheet_name]

    dset = tl.Dataset()
    dset.title = sheet.title

    for i, row in enumerate(sheet.rows):
        row_vals = [c.value for c in row]
        if (i == 0) and (headers):
            dset.headers = row_vals
        else:
            dset.append(row_vals)

    return dset
