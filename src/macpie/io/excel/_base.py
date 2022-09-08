import abc
import re

import pandas as pd

import tablib as tl

from macpie._config import get_option
from macpie.core.dataset import Dataset
from macpie.core.datasetfields import DatasetFields
from macpie.tools import lltools, tablibtools


DATASETS_SHEET_NAME = "_mp_datasets"
COLLECTION_SHEET_NAME = "_mp_collection"

INVALID_TITLE_REGEX = re.compile(r"[\\*?:/\[\]]")


def safe_xlsx_sheet_title(s, replace="-"):
    return re.sub(INVALID_TITLE_REGEX, replace, s)[:31]


def read_excel(io, as_collection=False, storage_options=None, engine=None, **kwargs):
    """
    Read an Excel file into a macpie Dataset.

    This is the analog of :func:`pandas.read_excel`, so read
    the documentation for that function for descriptions of available
    parameters, notes, and examples.


    Parameters
    ----------
    as_collection : bool, default False
        Whether to parse the Excel file as a :class:`macpie.BaseCollection` and
        return the appropriate collection type.
    **kwargs
        All remaining keyword arguments are passed through to the underlying
        :meth:`pandas.ExcelFile.parse` method.

    See Also
    --------
    Dataset.to_excel : Write Dataset to an Excel file.
    pandas.read_excel : Pandas analog
    """

    should_close = False
    if not isinstance(io, MACPieExcelFile):
        should_close = True
        io = MACPieExcelFile(io, storage_options=storage_options)
    elif engine and engine != io.engine:
        raise ValueError(
            "Engine should not be specified when passing "
            "an ExcelFile - ExcelFile already has the engine set"
        )

    try:
        if as_collection:
            data = io.parse_collection()
        else:
            data = io.parse(**kwargs)
    finally:
        # make sure to close opened file handles
        if should_close:
            io.close()

    return data


class MACPieExcelFile(pd.ExcelFile):
    """
    Class for parsing tabular Excel sheets into Dataset objects.

    This is the analog of :class:`pandas.ExcelFile`, so read
    the documentation for more information.

    See :func:`read_excel` also for more documentation.

    Parameters
    ----------
    path_or_buffer : str, bytes, path object (pathlib.Path or
        py._path.local.LocalPath), a file-like object, or openpyxl workbook.
        If a string or path object, expected to be a path to a
        .xls, .xlsx, .xlsb, .xlsm, .odf, .ods, or .odt file.
    engine : str, default "mp_openpyxl"
        If io is not a buffer or path, this must be set to identify io.
        Supported engines: ``mp_openpyxl``
        Engine compatibility :

        - ``mp_openpyxl`` supports newer Excel file formats.
    """

    def __init__(self, path_or_buffer, storage_options=None):
        from ._openpyxl import MACPieOpenpyxlReader

        self._engines["mp_openpyxl"] = MACPieOpenpyxlReader

        super().__init__(path_or_buffer, engine="mp_openpyxl", storage_options=storage_options)

        self._dataset_dicts = self.get_dataset_dicts()
        self._collection_dict = self.get_collection_dict()

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"io={self._io!r}, "
            f"datasets={self.dataset_sheetnames!r}, "
            f"collection_class={self.collection_classname!r})"
        )

    @property
    def dataset_sheetnames(self):
        if self._dataset_dicts:
            return list(self._dataset_dicts.keys())
        return []

    @property
    def collection_classname(self):
        if self._collection_dict is None:
            return None
        return self._collection_dict["class_name"]

    def get_dataset_dicts(self):
        if DATASETS_SHEET_NAME not in self.sys_sheet_names:
            return {}
            # raise ValueError(f"Cannot read Excel file without a '{DATASETS_SHEET_NAME}' sheet")

        dataset_dicts = self._reader.parse_excel_dict_sheet(DATASETS_SHEET_NAME)

        for excel_dict in dataset_dicts.values():
            excel_dict["id_col_name"] = lltools.make_tuple_if_list_like(
                excel_dict.get("id_col_name")
            )
            excel_dict["date_col_name"] = lltools.make_tuple_if_list_like(
                excel_dict.get("date_col_name")
            )
            excel_dict["id2_col_name"] = lltools.make_tuple_if_list_like(
                excel_dict.get("id2_col_name")
            )

        return dataset_dicts

    def get_collection_dict(self):
        if COLLECTION_SHEET_NAME not in self.sys_sheet_names:
            return {}

        collection_dict = self._reader.parse_excel_dict_sheet(COLLECTION_SHEET_NAME)
        return collection_dict

    def parse_tablib_dataset(
        self, sheet_name=None, headers=True, tablib_class=tablibtools.MacpieTablibDataset
    ):
        return self._reader.parse_tablib_dataset(
            sheet_name=sheet_name, headers=headers, tablib_class=tablib_class
        )

    def parse_tablib_datasets(
        self, sheet_name=None, headers=True, tablib_class=tablibtools.MacpieTablibDataset
    ):
        ret_dict = False

        if isinstance(sheet_name, list):
            sheets = sheet_name
            ret_dict = True
        elif sheet_name is None:
            sheets = self.sheet_names
            ret_dict = True
        else:
            sheets = [sheet_name]

        output = {}

        for asheetname in sheets:
            if isinstance(asheetname, str):
                sheetname = asheetname
            else:
                sheetname = self._reader.get_sheetname_by_index(asheetname)

            tlset = self.parse_tablib_dataset(
                sheet_name=sheetname, headers=headers, tablib_class=tablib_class
            )
            output[asheetname] = tlset

        if ret_dict:
            return output
        else:
            return output[asheetname]

    def parse_dataset_fields(self, sheet_name):
        tldset = self.parse_tablib_dataset(sheet_name)
        dataset_fields = DatasetFields()
        tldset.df.apply(
            lambda x: dataset_fields.append_series(x, with_tags=True, tag_value="x"),
            axis="columns",
        )
        return dataset_fields

    def parse_collection(self):
        if not self._collection_dict:
            raise ValueError(
                f"Cannot parse as collection without '{self.collection_sheet_name}' sheet."
            )

        import macpie.core.collections

        collection_class_name = self._collection_dict["class_name"]
        collection_class = getattr(macpie.core.collections, collection_class_name)
        return collection_class.from_excel_dict(self, self._collection_dict)

    def parse(self, sheet_name=0, **kwargs):
        """
        Parse specified sheet(s) into a macpie Dataset.
        Equivalent to read_excel(MACPieExcelFile, ...) See the :func:`read_excel`
        docstring for more info on accepted parameters.

        Returns
        -------
        Dataset or dict of Datasets
            Dataset from the passed in Excel file.
        """

        ret_dict = False

        if isinstance(sheet_name, list):
            sheets = sheet_name
            ret_dict = True
        elif sheet_name is None:
            sheets = self.sheet_names
            ret_dict = True
        else:
            sheets = [sheet_name]

        output = {}

        for asheetname in sheets:
            if isinstance(asheetname, str):
                sheetname = asheetname
            else:
                sheetname = self._reader.get_sheetname_by_index(asheetname)

            excel_dict = self._dataset_dicts.get(sheetname)
            if excel_dict is not None:
                read_excel_kwargs = excel_dict.get("read_excel_kwargs")
            else:
                read_excel_kwargs = {}

            kwargs.update(read_excel_kwargs)
            df = self._reader.parse(sheet_name=sheetname, **kwargs)

            if excel_dict is not None:
                output[asheetname] = Dataset.from_excel_dict(excel_dict, df)
            else:
                output[asheetname] = Dataset(df)

        if ret_dict:
            return output
        else:
            return output[asheetname]

    @property
    def sheet_names(self):
        return [
            sheet_name for sheet_name in self._reader.sheet_names if not sheet_name.startswith("_")
        ]

    @property
    def sys_sheet_names(self):
        return [
            sheet_name for sheet_name in self._reader.sheet_names if sheet_name.startswith("_")
        ]


class MACPieExcelReader(pd.io.excel._base.BaseExcelReader):
    @abc.abstractmethod
    def get_sheetname_by_index(self, index):
        pass

    @abc.abstractmethod
    def parse_excel_dict_sheet(self, sheet_name):
        pass

    @abc.abstractmethod
    def parse_tablib_dataset(
        self, sheet_name, headers=True, tablib_class=tablibtools.MacpieTablibDataset
    ):
        pass


class MACPieExcelWriter(pd.ExcelWriter):
    """
    Class for writing Dataset objects into Excel sheets.

    Default is to use the ``mp_xlsxwriter`` engine, which is the macpie version
    of panda's ``xlsxwriter`` engine. It has the best writing performance. The
    other engine option is ``mp_openpyxl`` (the macpie version of the ``openpyxl``
    engine).

    ``mp_xlsxwriter`` engine-specific options:

    * ``autofit_columns`` - True/False. Whether to autofit columns.
    * ``strip_carriage_returns`` - True/False. Whether to strip carriage
      returns (i.e. "\\\\r"). Otherwise Excel will encode it as "_x000D_".
      See https://github.com/jmcnamara/XlsxWriter/issues/680.

    Examples
    --------
    .. code-block:: python

        writer = mp.MACPieExcelWriter(
            file_path,
            engine="mp_xlsxwriter",
            engine_kwargs={
                "options": {"autofit_columns": True, "strip_carriage_returns": True}
            },
        )


    Notes
    -----
    This is the analog of :class:`pandas.ExcelWriter`, so read
    the documentation for that class for descriptions of available
    parameters, notes, and examples.
    """

    def __new__(cls, *args, **kwargs):
        # only switch class if generic(MACPieExcelWriter)
        if cls is MACPieExcelWriter:
            engine = kwargs.pop("engine", None)
            if engine is None:
                engine = get_option("excel.writer.engine")
            if engine not in ("mp_xlsxwriter", "mp_openpyxl"):
                raise ValueError(
                    f"Invalid engine: '{engine}''. Only 'mp_xlsxwriter' or 'mp_openpyxl' supported."
                )

            cls = pd.io.excel._util.get_writer(engine)

        return object.__new__(cls)

    @abc.abstractmethod
    def write_excel_dict(self, excel_dict: dict):
        pass

    @abc.abstractmethod
    def write_tablib_dataset(self, tlset: tl.Dataset, freeze_panes=True):
        pass

    @abc.abstractmethod
    def highlight_duplicates(self, sheet_name, column_name):
        pass

    @abc.abstractmethod
    def finalize_sheet_order(self):
        pass

    @abc.abstractmethod
    def sheet_names(self):
        pass

    def finalized_sheet_order(self, sheetnames):
        try:
            dset_sheet_index = sheetnames.index(DATASETS_SHEET_NAME) + 1
            sheetname_to_move_to = next(
                sheetname
                for sheetname in sheetnames[dset_sheet_index:]
                if sheetname.startswith("_mp")
            )
            lltools.move_item_to(sheetnames, DATASETS_SHEET_NAME, sheetname_to_move_to)
        except (ValueError, StopIteration) as e:
            pass

        return sheetnames

    def _get_sheet_name(self, sheet_name):
        if not sheet_name:
            sheet_name = get_option("excel.sheet_name.default")
        return super()._get_sheet_name(sheet_name)
